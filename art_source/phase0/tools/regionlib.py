"""Shape / shading helpers for the procedural region backdrops and draft monsters (all output snaps to the 48-colour pack palette)."""
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
from pal import C

# ---------------- shapes (return bool masks on an HxW grid) ----------------
def grid(W, H):
    ys, xs = np.mgrid[0:H, 0:W]; return xs + 0.5, ys + 0.5
def E(W, H, cx, cy, rx, ry, rot=0.0):
    x, y = grid(W, H); x = x - cx; y = y - cy
    if rot:
        c, s = np.cos(rot), np.sin(rot); x, y = c * x + s * y, -s * x + c * y
    return (x / rx) ** 2 + (y / ry) ** 2 <= 1.0
def P(W, H, pts):
    from PIL import ImageDraw
    im = Image.new('1', (W, H), 0); ImageDraw.Draw(im).polygon([(float(a), float(b)) for a, b in pts], fill=1)
    return np.array(im, bool)
def R(W, H, x0, y0, x1, y1):
    m = np.zeros((H, W), bool); m[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = True; return m
def LN(W, H, p0, p1, w):
    x, y = grid(W, H); (ax, ay), (bx, by) = p0, p1
    dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy or 1
    t = np.clip(((x - ax) * dx + (y - ay) * dy) / L2, 0, 1)
    return (x - ax - t * dx) ** 2 + (y - ay - t * dy) ** 2 <= (w / 2.0) ** 2

# ---------------- pseudo-3D shading ----------------
LIGHT = np.array([-0.55, -0.75, 0.9]); LIGHT = LIGHT / np.linalg.norm(LIGHT)
def shade_rim(mask, n_tones):
    """small-icon shading: mid fill, light rim where the top/left neighbour is outside, dark rim bottom/right."""
    def out(dx, dy):
        m = np.pad(mask, 1)[1 + dy:1 + dy + mask.shape[0], 1 + dx:1 + dx + mask.shape[1]]; return ~m
    mid = 1 if n_tones >= 3 else 0
    idx = np.full(mask.shape, mid)
    if n_tones >= 2: idx[out(1, 0) | out(0, 1) | out(1, 1)] = 0
    if n_tones >= 3: idx[(out(-1, 0) | out(0, -1)) & ~(out(1, 0) | out(0, 1))] = 2
    if n_tones >= 4: idx[out(-1, -1) & ~out(-1, 0) & ~out(0, -1) & ~(out(1, 0) | out(0, 1))] = 3
    if n_tones == 2: idx[~(out(1, 0) | out(0, 1) | out(1, 1))] = 1
    return np.where(mask, idx, -1)

def shade_idx(mask, n_tones, bulge=1.0, flat=False, th=None, rim=False):
    """0=darkest .. n_tones-1=lightest; dome profile from the distance transform, lambert-lit from the top-left."""
    if flat: return np.where(mask, n_tones // 2, -1)
    if rim: return shade_rim(mask, n_tones)
    d = ndi.distance_transform_edt(np.pad(mask, 1))[1:-1, 1:-1]
    dm = max(d.max(), 1.0); t = np.clip(d / dm, 0, 1)
    h = np.sqrt(1 - (1 - t) ** 2) * dm * bulge
    gy, gx = np.gradient(ndi.gaussian_filter(h, 0.8))
    n = np.stack([-gx, -gy, np.ones_like(h)], -1); n /= np.linalg.norm(n, axis=-1, keepdims=True)
    I = np.clip(n @ LIGHT, 0, 1)
    th = th or {2: [0.62], 3: [0.55, 0.85], 4: [0.5, 0.78, 0.95]}[n_tones]
    idx = np.digitize(I, th)
    return np.where(mask, idx, -1)

class Sprite:
    """Parts painted back to front; outer 1px outline + internal separator lines."""
    def __init__(s, W, H):
        s.W, s.H = W, H; s.rgb = np.zeros((H, W, 3), np.uint8); s.pid = np.zeros((H, W), np.int32); s.n = 0; s.meta = {}
    def add(s, mask, ramp, sep=True, line=None, flat=False, bulge=1.0, th=None, clip=None, rim=False):
        if clip is not None: mask = mask & clip
        if not mask.any(): return mask
        s.n += 1; k = s.n
        idx = shade_idx(mask, len(ramp), bulge, flat, th, rim)
        for i, nm in enumerate(ramp): s.rgb[idx == i] = C[nm]
        if sep:
            behind = (s.pid > 0) & ~mask
            nb = np.zeros_like(mask)
            nb[1:] |= behind[:-1]; nb[:-1] |= behind[1:]; nb[:, 1:] |= behind[:, :-1]; nb[:, :-1] |= behind[:, 1:]
            edge = mask & nb
            s.rgb[edge] = C[line or 'outline']
        s.pid[mask] = k
        return mask
    def px(s, pts, col):
        for x, y in pts:
            if 0 <= x < s.W and 0 <= y < s.H: s.rgb[y, x] = C[col]; s.pid[y, x] = max(s.pid[y, x], 1)
    def fill(s, mask, col):
        s.rgb[mask] = C[col]; s.pid[mask & (s.pid == 0)] = 1
    def image(s, outline=True, trim=True):
        op = s.pid > 0
        a = np.zeros((s.H, s.W, 4), np.uint8); a[op, :3] = s.rgb[op]; a[op, 3] = 255
        if outline:
            n = np.zeros_like(op); n[1:] |= op[:-1]; n[:-1] |= op[1:]; n[:, 1:] |= op[:, :-1]; n[:, :-1] |= op[:, 1:]
            ring = n & ~op; a[ring, :3] = C['outline']; a[ring, 3] = 255
        if not trim: return a
        ys, xs = np.nonzero(a[..., 3]); s.bbox = (xs.min(), ys.min()); return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

def eye(s, x, y, r=1, pupil='outline', white='white', look=(0, 0), glow=None):
    """small cartoon eye: (2r+1) square white with 1px pupil; glow=colour draws a solid glowing eye instead."""
    if glow:
        s.px([(x + i, y + j) for i in range(-r, r + 1) for j in range(-r, r + 1) if abs(i) + abs(j) <= r + (r > 1)], glow); return
    s.px([(x + i, y + j) for i in range(-r, r + 1) for j in range(-r, r + 1)], white)
    s.px([(x + look[0], y + look[1])], pupil)

# ---------------- backdrop helpers ----------------
def _h(x, y, sd):
    v = (np.asarray(x, np.int64) * 374761393 + np.asarray(y, np.int64) * 668265263 + sd * 2246822519) & 0xffffffff
    v = ((v ^ (v >> 13)) * 1274126177) & 0xffffffff
    return ((v ^ (v >> 16)) & 0xffffffff) / 0xffffffff
def vnoise(Wn, Hn, cw, ch, sd):
    ys_, xs_ = np.mgrid[0:Hn, 0:Wn].astype(float)
    gx, gy = xs_ / cw, ys_ / ch; x0, y0 = np.floor(gx).astype(int), np.floor(gy).astype(int); fx, fy = gx - x0, gy - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a_, b_, c_, d_ = _h(x0, y0, sd), _h(x0 + 1, y0, sd), _h(x0, y0 + 1, sd), _h(x0 + 1, y0 + 1, sd)
    return (a_ * (1 - fx) + b_ * fx) * (1 - fy) + (c_ * (1 - fx) + d_ * fx) * fy
def noise1(n, cell, sd):
    x = np.arange(n) / cell; i = np.floor(x).astype(int); f = x - i; f = f * f * (3 - 2 * f)
    return _h(i, 0, sd) * (1 - f) + _h(i + 1, 0, sd) * f

class Canvas:
    def __init__(s, W=270, H=480): s.W, s.H = W, H; s.a = np.zeros((H, W, 3), np.uint8)
    def fill(s, mask, col): s.a[mask] = C[col]
    def rect(s, x0, y0, x1, y1, col): s.a[max(0, y0):y1, max(0, x0):x1] = C[col]
    def px(s, x, y, col):
        if 0 <= x < s.W and 0 <= y < s.H: s.a[y, x] = C[col]
    def paint_sprite(s, spr, x, y):
        a = spr if isinstance(spr, np.ndarray) else np.array(spr)
        h, w = a.shape[:2]
        for yy in range(h):
            Y = y + yy
            if not 0 <= Y < s.H: continue
            m = a[yy, :, 3] > 0; xs = np.arange(w) + x; ok = m & (xs >= 0) & (xs < s.W)
            s.a[Y, xs[ok]] = a[yy, ok, :3]
    def sky(s, bands, y0=0):
        """bands: [(colour, rows)], 2-row checker dither at each boundary"""
        y = y0; prev = None
        for col, rows in bands:
            s.a[y:y + rows] = C[col]
            if prev is not None:
                for dy in (-1, 0):
                    Y = y + dy
                    if 0 <= Y < s.H:
                        xs = np.arange(s.W); m = (xs + Y) % 2 == 0
                        s.a[Y, m] = C[col if dy == -1 else prev]
            prev = col; y += rows
        return y
    def cloud(s, cx, cy, w, sd, cols=('white', 'sky_lt'), shadow=None):
        m = np.zeros((s.H, s.W), bool)
        n = max(3, w // 7)
        for i in range(n):
            t = i / (n - 1); r = (0.45 + 0.55 * np.sin(np.pi * t)) * w / 4.2 * (0.8 + 0.4 * _h(i, sd, 7))
            m |= E(s.W, s.H, cx - w / 2 + t * w, cy - r * 0.35, r * 1.25, r)
        m &= grid(s.W, s.H)[1] <= cy + 2
        low = m & ~np.roll(m, -3, 0)
        s.fill(m, cols[0]); s.fill(low, cols[1])
        if shadow: s.fill(m & ~np.roll(m, -1, 0), shadow)
        return m
    def ridge(s, y_base, amp, cell, sd, cols, top=None, rough=0.0):
        """filled silhouette from x-noise: y(x) = y_base - amp*noise; cols=(fill, rim)"""
        hgt = noise1(s.W, cell, sd) * amp + (noise1(s.W, max(2, cell // 4), sd + 9) - 0.5) * amp * rough
        ytop = (y_base - hgt).astype(int)
        ys = np.arange(s.H)[:, None]; m = ys >= ytop[None, :]
        s.fill(m, cols[0])
        if len(cols) > 1:
            rim = m & ~np.roll(m, 1, 0); s.fill(rim, cols[1])
        return m, ytop
    def image(s):
        a = np.zeros((s.H, s.W, 4), np.uint8); a[..., :3] = s.a; a[..., 3] = 255; return Image.fromarray(a, 'RGBA')

def ground(W, H, y0, cols, sd, calm_y=300, cw=10, ch=3, q=(0.12, 0.5), tufts=None, n_tufts=200, speck=None):
    """3-tone value-noise ground (like the forest meadow). cols=(dark, mid, light). Contrast (dark share) drops below calm_y."""
    n = 0.6 * vnoise(W, H, cw, ch, sd) + 0.4 * vnoise(W, H, max(2, cw // 2.5), max(1, ch // 1.5), sd + 6)
    ys = np.mgrid[0:H, 0:W][0]
    calm = np.clip((ys - calm_y) / 80.0, 0, 1)
    q1 = np.quantile(n, q[0]) * (1 - calm) + np.quantile(n, q[0] * 0.35) * calm
    q2 = np.quantile(n, q[1])
    a = np.zeros((H, W, 3), np.uint8)
    a[n < q1] = C[cols[0]]; a[(n >= q1) & (n < q2)] = C[cols[1]]; a[n >= q2] = C[cols[2]]
    if speck:
        sp = _h(*np.mgrid[0:H, 0:W][::-1], sd + 3)
        for col, thr in speck: a[(sp < thr) & (ys < calm_y + 40)] = C[col]
    if tufts:
        for i in range(n_tufts):
            tx, ty = int(_h(i, 1, sd) * W), int(y0 + _h(i, 2, sd) * (H - y0))
            if ty > calm_y + 30 and _h(i, 3, sd) < 0.6: continue
            for dx, dy, k in ((0, 0, 0), (-1, -1, 0), (1, -1, 0), (0, -1, 0), (-2, -2, 1), (2, -2, 1)):
                if 0 <= tx + dx < W and 0 <= ty + dy < H: a[ty + dy, tx + dx] = C[tufts[k]]
    a[:y0] = 0
    return a

def patches(canvas, y_from, y_to, sd, cols, density=0.55, size=(11, 4), step=(72, 26), calm_y=300, edge_col=None):
    """scattered flat ellipse patches (dirt / puddles / flagstones), bigger toward the bottom; sparse below calm_y."""
    W, H = canvas.W, canvas.H; ys_, xs_ = np.mgrid[0:H, 0:W]
    row = 0
    for gy in range(y_from, y_to, step[1]):
        row += 1
        for gx in range(-20, W + 20, step[0]):
            k = gx * 7 + gy + sd * 1000
            cx = gx + (row % 3) * step[0] / 3 + (_h(k, 3, 51) - 0.5) * 44; cy = gy + (_h(k, 4, 51) - 0.5) * 12
            dens = density * (0.35 if gy > calm_y else 1.0)
            if _h(k, 5, 51) > dens: continue
            sc = 1 + (gy - 150) / 400
            rx, ry = (size[0] + _h(k, 6, 51) * 7) * sc, (size[1] + _h(k, 7, 51) * 2) * sc
            jit = (_h(xs_ // 2, ys_ // 2, k) - 0.5) * 0.35
            d = ((xs_ - cx) / rx) ** 2 + ((ys_ - cy) / ry) ** 2 + np.abs(xs_ - cx) / rx * 0.35 + jit
            pm = d < 1.0
            if not pm.any(): continue
            canvas.fill(pm, cols[0]); canvas.fill(pm & (_h(xs_, ys_, k + 1) < 0.18), cols[1])
            canvas.fill(pm & ~np.roll(pm, -1, 0), edge_col or cols[1])
            e2 = pm & ~np.roll(pm, 1, 0); canvas.fill(e2 & (_h(xs_, ys_, k + 2) < 0.5), edge_col or cols[1])
