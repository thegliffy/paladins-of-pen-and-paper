"""REFINE PASS backdrops (270x480): meadow (Millpond), cave (Howling Cleft), town (Candlewick) + new town Brinewick.
Same framing as before: horizon y141, monster feet band y222-266, calm zone below y300. Rules: refine_style.STYLE."""
import numpy as np
from scipy import ndimage as ndi
from regionlib import Canvas, Sprite, E, P, R, LN, _h, noise1, vnoise, shade_idx
from pal import C
W, H = 270, 480; HOR = 141
YS, XS = np.mgrid[0:H, 0:W]
def e(*a, **k): return E(W, H, *a, **k)
def p(pts): return P(W, H, pts)
def r(*a): return R(W, H, *a)
def ln(*a): return LN(W, H, *a)
def spr(cv, s): cv.paint_sprite(s.image(trim=False), 0, 0)

# ---------------- perspective ground helpers ----------------
def vn(u, v, sd):
    """value noise at arbitrary float coords (smoothstep), 0..1"""
    x0, y0 = np.floor(u).astype(np.int64), np.floor(v).astype(np.int64); fx, fy = u - x0, v - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b, c, d = _h(x0, y0, sd), _h(x0 + 1, y0, sd), _h(x0, y0 + 1, sd), _h(x0 + 1, y0 + 1, sd)
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy
YV = 112                                                    # vanishing row (a bit above the horizon)
SC = np.clip((YS - YV) / (H - YV), 0.02, 1.0)                # perspective scale: 1 at the bottom row
GU = (XS - 135) / SC; GV = 340.0 / SC                         # ground-plane coords (px at the bottom)
def gnoise(cw, ch, sd, oct2=0.35):
    n = (1 - oct2) * vn(GU / cw, GV / ch, sd) + oct2 * vn(GU / (cw * 0.42), GV / (ch * 0.42), sd + 17)
    fade = np.clip((SC - 0.1) / 0.22, 0, 1)                   # flatten toward the horizon (no far speckle)
    return 0.5 + (n - 0.5) * fade
def bands(cv, mask, n, cols, th):
    """paint <=3 adjacent tones by thresholds th (dark < th0 <= mid < th1 <= light)"""
    cv.fill(mask, cols[1]); cv.fill(mask & (n < th[0]), cols[0]); cv.fill(mask & (n >= th[1]), cols[2])
def soften(mask, it=1):
    return ndi.binary_opening(mask, iterations=it)
CALM = np.clip((YS - 300) / 70.0, 0, 1)                      # 0 above y300 .. 1 at y370+

def tuft(cv, x, y, size, cols, k):
    """grass tuft: 3-5 blades, base dark, tips light; size grows with depth"""
    hgt = 2 + size; blades = (-1, 0, 1) if size < 2 else (-2, -1, 0, 1, 2)
    for i, b in enumerate(blades):
        hh = hgt - abs(b) // 2 - (k + i) % 2
        for j in range(hh):
            xx = x + b + (b * j) // max(3, hgt + 1)
            cv.px(xx, y - j, cols[0] if j == 0 else (cols[2] if j == hh - 1 else cols[1]))
def flower(cv, x, y, col):
    cv.px(x, y - 1, col); cv.px(x - 1, y, col); cv.px(x + 1, y, col); cv.px(x, y, 'gold' if col != 'gold' else 'cream'); cv.px(x, y + 1, 'leaf')

def tree_line(cv, y_base, cols, sd, crown=(9, 15), step=(7, 12), rim=None):
    """row of rounded tree crowns (silhouette terrain: no outline), lit from the top-left"""
    m = np.zeros((H, W), bool); x = -6; k = 0
    while x < W + 8:
        rr = crown[0] + _h(k, 1, sd) * (crown[1] - crown[0]); yy = y_base - rr * 0.55 - _h(k, 2, sd) * 6
        m |= e(x, yy, rr * 0.8, rr * 0.75); x += step[0] + _h(k, 3, sd) * (step[1] - step[0]); k += 1
    m |= (YS >= y_base - 4) & (YS < y_base + 3)
    m &= YS < y_base + 3
    cv.fill(m, cols[0])
    lit = m & ~np.roll(np.roll(m, 2, 0), 2, 1)                # top-left facing edge
    cv.fill(lit & (YS < y_base - 2), cols[1])
    if rim: cv.fill(m & ~np.roll(m, 1, 0) & (XS % 3 != 0), rim)
    return m

# ================================================================ Millpond (meadow)
def millpond():
    cv = Canvas()
    cv.sky([('blue', 30), ('sky', 52), ('sky_lt', 62)])
    for i, (x, y, w) in enumerate(((44, 50, 46), (182, 38, 58), (240, 78, 30), (112, 86, 24))): cv.cloud(x, y, w, i + 3)
    tree_line(cv, HOR - 9, ('haze', 'grass'), 7, crown=(6, 10), step=(5, 9))                     # far wood, aerial blue-green
    tree_line(cv, HOR - 2, ('pine', 'leaf_dk'), 11, crown=(7, 13), step=(6, 11), rim='leaf')        # near wood line
    # ground: soft perspective value bands, lighter toward the horizon (haze)
    g = YS >= HOR
    n = gnoise(70, 26, 21)
    bands(cv, g, n, ('leaf', 'grass', 'lime'), (0.31 - 0.12 * CALM, 0.74 + 0.14 * CALM))
    cv.fill(g & (YS < HOR + 5), 'grass'); cv.fill(g & (YS < HOR + 2), 'lime')
    # worn footpath from the bottom-left toward the pond bank (natural, not blotches)
    t = np.clip((YS - 152) / (H - 152), 0, 1); cxp = 112 - 70 * t + 26 * np.sin(t * 3.4) + (noise1(H, 30, 4)[YS] - 0.5) * 5
    half = 2.6 + t * 17; path = (np.abs(XS - cxp) < half) & (YS > 153)             # refine-2: >=5px at the far end, edged
    path = soften(path)
    cv.fill(path, 'wood_lt'); pn = gnoise(14, 6, 33)
    cv.fill(path & (pn > 0.58), 'tan'); cv.fill(path & (pn < 0.22) & (YS > 260), 'wood')
    ped = path & ~ndi.binary_erosion(path)
    cv.fill(ped & (XS < cxp), 'leaf'); cv.fill(ped & (XS >= cxp), 'leaf_dk')                                   # lit left verge / shaded right verge
    cv.fill(np.roll(ped & (XS < cxp), 1, 1) & path & ~ped, 'tan'); cv.fill(np.roll(ped & (XS >= cxp), -1, 1) & path & ~ped, 'wood')   # inner lip
    # windmill on the left knoll (prop: outlined)
    bx, by = 40, HOR - 1
    kn = e(bx + 4, by + 5, 36, 10) & (YS < HOR + 1); cv.fill(kn, 'grass'); cv.fill(kn & ~np.roll(kn, 1, 0), 'lime'); cv.fill(kn & (XS > bx + 14) & (YS > by), 'leaf')   # knoll (terrain)
    s = Sprite(W, H)
    s.add(p([(bx - 11, by), (bx - 7, by - 42), (bx + 7, by - 42), (bx + 11, by)]), ['tan', 'sand', 'parchment'])
    for yy in range(by - 36, by, 6): s.px([(xx, yy) for xx in range(bx - 9, bx + 10) if s.pid[yy, xx] and (xx + yy // 6) % 4 == 0], 'tan')
    s.add(p([(bx - 10, by - 42), (bx, by - 53), (bx + 10, by - 42)]), ['red_dk', 'red', 'coral'])
    s.add(r(bx - 3, by - 11, bx + 3, by), ['bark', 'wood_dk'], flat=True)
    s.add(r(bx - 2, by - 31, bx + 2, by - 26), ['navy', 'blue_dk'], flat=True)
    hub = (bx, by - 38)
    for a in (0.35, 0.35 + np.pi / 2, 0.35 + np.pi, 0.35 + 1.5 * np.pi):
        tip = (hub[0] + np.cos(a) * 26, hub[1] + np.sin(a) * 26)
        s.add(ln(hub, tip, 2), ['bark', 'wood_dk'], sep=False)
        nx, ny = -np.sin(a), np.cos(a); b0 = (hub[0] + np.cos(a) * 8, hub[1] + np.sin(a) * 8)
        s.add(p([b0, tip, (tip[0] + nx * 6, tip[1] + ny * 6), (b0[0] + nx * 5, b0[1] + ny * 5)]), ['wood_lt', 'tan', 'parchment'], sep=False)
    s.add(e(hub[0], hub[1], 2, 2), ['bark', 'wood'])
    spr(cv, s)
    # the pond, back right: dark far bank, sky reflection, lily pads, reeds (terrain: no black outline)
    pond = soften(e(190, 163, 76, 14) | e(238, 157, 46, 11))
    cv.fill(pond, 'blue'); cv.fill(pond & (YS > 166), 'blue_dk')
    cv.fill(pond & ~np.roll(pond, 2, 0), 'pine'); cv.fill(pond & ~np.roll(pond, 1, 0), 'leaf_dk')     # far bank shade
    cv.fill(pond & ~np.roll(pond, -1, 0), 'wood_dk'); cv.fill(np.roll(pond, -1, 0) & ~pond & (YS > 160), 'wood_lt')   # near bank mud lip
    for i in range(26):
        x, y = int(122 + _h(i, 1, 5) * 146), int(156 + _h(i, 2, 5) * 16)
        L_ = 3 + int(_h(i, 3, 5) * 7)
        if pond[y, x] and pond[y, min(W - 1, x + L_)]: cv.a[y, x:x + L_] = C['sky' if y < 166 else 'blue']
    for i in range(8):
        x, y = int(132 + _h(i, 4, 6) * 126), int(156 + _h(i, 5, 6) * 14)
        lp = e(x, y, 3.6, 1.5)
        if (lp & pond).sum() == lp.sum(): cv.fill(lp, 'leaf'); cv.px(x - 1, y - 1, 'grass'); cv.px(x + 2, y, 'leaf_dk'); cv.px(x + 2, y - 1, 'blue')
    cv.px(171, 158, 'cream'); cv.px(172, 158, 'gold'); cv.px(170, 158, 'cream')
    for i in range(64):
        x = int(112 + _h(i, 7, 8) * 158); col = pond[:, min(W - 1, x)]
        if not col.any(): continue
        ed = np.nonzero(col)[0]; y0 = ed.min() + 1 if _h(i, 9, 8) < 0.55 else ed.max()
        hgt = 5 + int(_h(i, 8, 8) * 8)
        for k in range(hgt): cv.px(x + (k > hgt * 0.65 and i % 2), y0 - k, 'pine' if k < 2 else ('leaf_dk' if k < hgt - 2 else 'leaf'))
        if i % 4 == 0:
            for k in range(3): cv.px(x, y0 - hgt + k, 'wood_dk'); cv.px(x + 1, y0 - hgt + k, 'bark')
    # tufts + flowers (perspective sized, sparse in the calm zone, none on the path)
    for i in range(330):
        x, y = int(_h(i, 1, 61) * W), int(HOR + 6 + _h(i, 2, 61) ** 0.9 * (H - HOR - 8))
        if path[min(H - 1, y + 1), x] or pond[min(H - 1, y + 2), x] or (y > 300 and _h(i, 3, 61) < 0.7): continue
        depth = (y - HOR) / (H - HOR); size = 0 if depth < 0.12 else (1 if depth < 0.45 else 2)
        tuft(cv, x, y, size, ('leaf', 'leaf_dk', 'lime') if n[y, x] > 0.5 else ('leaf_dk', 'leaf', 'grass'), i)
    for i in range(46):
        x, y = int(_h(i, 4, 62) * W), int(178 + _h(i, 5, 62) * 120)
        if path[y, x] or pond[min(H - 1, y + 3), x]: continue
        for j in range(1 + i % 3):
            flower(cv, x + j * 4 - (j % 2) * 2, y + (j % 2) * 2, ('cream', 'gold', 'white', 'coral')[i % 4])
    return cv

# ---------------- rock helpers ----------------
from scipy.spatial import cKDTree
def cells(u, v, n, sd, box, aniso=(1.0, 1.0)):
    """Voronoi rock facets: label per pixel from n seeds in box (u0,v0,u1,v1) of the (u,v) coordinate field"""
    u0, v0, u1, v1 = box; k = np.arange(n)
    seeds = np.stack([u0 + _h(k, 1, sd) * (u1 - u0), v0 + _h(k, 2, sd) * (v1 - v0)], -1)
    t = cKDTree(seeds * np.array(aniso)); d, lab = t.query(np.stack([u.ravel() * aniso[0], v.ravel() * aniso[1]], -1), k=2)
    lab = lab[:, 0].reshape(u.shape); gap = (d[:, 1] - d[:, 0]).reshape(u.shape)
    return lab, gap
def rock_facets(cv, mask, lab, ramp, crack, sd, bulge=0.7, crack_w=1.2, gap=None):
    """shade each facet as a low dome lit from the top-left; crevices between facets in `crack`"""
    for k in np.unique(lab[mask]):
        m = mask & (lab == k)
        if m.sum() < 3: continue
        ys_, xs_ = np.nonzero(m); y0, y1, x0, x1 = ys_.min(), ys_.max() + 1, xs_.min(), xs_.max() + 1
        sub = m[y0:y1, x0:x1]; idx = shade_idx(sub, len(ramp), bulge=bulge)
        tone = int(_h(k, 7, sd) * 2.99) - 1                                    # per-facet value shift -1..+1
        for i in range(len(ramp)):
            j = int(np.clip(i + (tone if abs(tone) == 1 and _h(k, 8, sd) < 0.5 else 0), 0, len(ramp) - 1))
            reg = np.zeros_like(m); reg[y0:y1, x0:x1] = sub & (idx == i); cv.fill(reg, ramp[j])
    if gap is not None: cv.fill(mask & (gap < crack_w), crack)
def pebble(s, x, y, rx, ry, ramp=('ink', 'slate', 'gray', 'silver')):
    s.add(e(x, y, rx, ry), list(ramp))

def edge_of(m):
    return m & ~ndi.binary_erosion(m)
def rock_poly(cx, cy, rx, ry, sd, flat_bottom=True, nv=9):
    k = np.arange(nv); ang = np.linspace(np.pi, 2 * np.pi, nv) if flat_bottom else np.linspace(0, 2 * np.pi, nv, endpoint=False)
    rr = 0.78 + 0.32 * _h(k, 1, sd)
    pts = [(cx + np.cos(t) * rx * q, cy + np.sin(t) * ry * q * (1.25 if flat_bottom else 1)) for t, q in zip(ang, rr)]
    if flat_bottom: pts += [(cx + rx * 0.95, cy + ry * 0.25), (cx - rx * 0.95, cy + ry * 0.25)]
    return p(pts)
def rock_prop(s, cx, cy, rx, ry, sd, ramp=('ink', 'slate', 'gray', 'silver')):
    """natural boulder prop (outlined): irregular faceted outline, lit top-left facet, one crack"""
    m = rock_poly(cx, cy, rx, ry, sd); s.add(m, list(ramp), bulge=0.5)
    lit = m & rock_poly(cx - rx * 0.32, cy - ry * 0.42, rx * 0.42, ry * 0.32, sd + 1) & ~edge_of(m)
    s.add(lit, [ramp[-1]], sep=False, flat=True)
    if rx > 6:
        x0 = cx + rx * (0.1 + 0.3 * _h(sd, 2, 3)); s.add(ln((x0, cy - ry * 0.7), (x0 + rx * 0.2, cy + ry * 0.1), 1.0) & m, [ramp[0]], sep=False, flat=True)

# ================================================================ Howling Cleft (cave)
def howling_cleft():
    cv = Canvas()
    cv.sky([('slate', 10), ('gray', 18), ('silver', 14), ('mist', 10)])                                # overcast slot of sky
    top = (24 + noise1(W, 22, 5) * 26 + (noise1(W, 6, 9) - 0.5) * 8).astype(int)
    top[95:180] = np.minimum(top[95:180], 18 + (noise1(85, 10, 3) * 8).astype(int))
    cliff = (YS >= top[None, :]) & (YS < HOR + 9)
    # facets: big in the middle-distance, flattened (strata), lit top-left
    u = XS.astype(float); v = YS.astype(float)
    lab, gap = cells(u, v, 70, 41, (-10, 0, W + 10, HOR + 10), aniso=(0.75, 1.35))
    rock_facets(cv, cliff, lab, ['slate', 'gray', 'silver', 'mist'], 'ink', 41, bulge=0.55, gap=gap, crack_w=1.15)
    cv.fill(cliff & (gap < 0.55) & (YS > 60), 'outline')                                             # deepest crevices only
    cv.fill(cliff & ~np.roll(cliff, 1, 0), 'mist'); cv.fill(cliff & ~np.roll(cliff, 2, 0) & np.roll(cliff, 1, 0), 'silver')   # lit cliff top
    for i in range(12):                                                                         # moss tufts on a few ledges
        x = int(_h(i, 1, 77) * W); col = np.nonzero(cliff[:, x] & (gap[:, x] < 1.1) & (YS[:, x] > top[x] + 6) & (YS[:, x] < HOR - 6))[0]
        if not len(col): continue
        y = int(col[int(_h(i, 2, 77) * len(col))])
        for k in range(4 + i % 3): cv.px(x + k, y - 1, 'haze' if k in (1, 2) else 'pine'); cv.px(x + k, y, 'pine'); cv.px(x + k, y + 1 + (k % 3 == 0), 'pine_dk')
    # the mouth of the cleft
    mp_ = [(70, HOR + 9), (73, 126), (78, 112), (88, 96), (97, 88), (110, 76), (124, 71), (136, 64), (149, 69), (163, 73), (175, 85), (186, 94), (192, 109), (199, 122), (204, HOR + 9)]
    mouth = soften(p([(x + (_h(i, 1, 3) - 0.5) * 6, y + (_h(i, 2, 3) - 0.5) * 5) for i, (x, y) in enumerate(mp_)]), 1)
    ring = ndi.binary_dilation(mouth, iterations=3) & ~mouth & cliff
    cv.fill(ring, 'slate'); cv.fill(ring & ~ndi.binary_dilation(mouth, iterations=1) & (XS > 136), 'ink')
    cv.fill(mouth, 'outline')
    inner = ndi.binary_erosion(mouth, iterations=5); cv.fill(mouth & ~inner & (XS < 120) & (YS < 120), 'ink')
    pas = mouth & (YS > 128) & (vn(XS / 9.0, YS / 3.0, 5) > 0.45 - (YS - 128) / 40.0); cv.fill(pas, 'ink')   # passage floor fading in
    s = Sprite(W, H)
    for i, x in enumerate(range(86, 194, 11)):                                                  # stalactite teeth (rock props)
        col = np.nonzero(mouth[:, x])[0]
        if not len(col): continue
        yt = int(col.min()); Lt = 7 + int(_h(i, 1, 13) * 13)
        s.add(p([(x - 4, yt - 3), (x + 4, yt - 3), (x + 0.5, yt + Lt)]), ['slate', 'gray', 'silver'])
    for i, (x, h_) in enumerate(((84, 13), (103, 8), (172, 10), (191, 15))):                     # stalagmites at the lip
        s.add(p([(x - 5, HOR + 10), (x + 5, HOR + 10), (x + 0.5, HOR + 10 - h_)]), ['slate', 'gray', 'silver'])
    spr(cv, s)
    for (x, y) in ((129, 110), (133, 110), (149, 102), (152, 102)): cv.px(x, y, 'gold')        # something answers
    cv.px(129, 111, 'amber'); cv.px(133, 111, 'amber')
    # ---- floor: grey grit over bedrock; value falls off toward the viewer (light comes from the open cleft above)
    fl = YS >= HOR + 9
    n = gnoise(80, 30, 77); dep = (YS - HOR) / (H - HOR)
    v = (1 - dep) + (n - 0.5) * (0.42 - 0.3 * CALM)
    cv.fill(fl, 'gray'); cv.fill(fl & (v > 0.9), 'silver'); cv.fill(fl & (v < 0.42), 'slate')
    cv.fill(fl & (v > 0.9) & (v < 0.93) & (n < 0.5), 'gray')
    foot = (noise1(W, 9, 13) * 5).astype(int)
    cv.fill(fl & (YS < HOR + 11 + foot[None, :]), 'slate'); cv.fill(fl & (YS < HOR + 10 + foot[None, :] // 2), 'ink')   # shadow at the cliff foot
    lab2, gap2 = cells(GU, GV, 150, 88, (-500, 340, 500, 340 / 0.16))
    crk = fl & (gap2 < 1.3 * SC + 0.2) & (YS > HOR + 20) & (_h(lab2, 3, 5) < 0.55) & (CALM < 0.5)
    cv.fill(crk, 'slate'); cv.fill(np.roll(crk, 1, 0) & fl & ~crk & (YS > 200) & (v > 0.7), 'silver')     # crack + lit lower lip
    pud = soften(e(56, 292, 30, 6) | e(80, 296, 18, 4)); cv.fill(ndi.binary_dilation(pud, iterations=2) & fl, 'slate')
    cv.fill(pud, 'navy'); cv.fill(pud & (YS < 291), 'blue_dk'); cv.a[293, 46:60] = C['gray']; cv.a[290, 66:72] = C['silver']
    # grit + pebbles (tiny ones are 2-tone, bigger ones are outlined props)
    for i in range(260):
        x, y = int(_h(i, 1, 91) * W), int(HOR + 14 + _h(i, 2, 91) ** 1.1 * (H - HOR - 20))
        if (y > 300 and _h(i, 3, 91) < 0.8) or pud[min(H - 1, y + 1), x]: continue
        cv.px(x, y, 'silver'); cv.px(x, y + 1, 'slate')
        if (y - HOR) / (H - HOR) > 0.35 and i % 3 == 0: cv.px(x + 1, y, 'silver'); cv.px(x + 1, y + 1, 'slate')
    s = Sprite(W, H)
    for i in range(18):
        x, y = int(_h(i, 1, 93) * W), int(170 + _h(i, 2, 93) * 140)
        if 30 < x < 240 and 200 < y < 275: continue
        sc = (y - YV) / (H - YV); rock_prop(s, x, y, 2.2 + sc * 4 * (0.6 + _h(i, 3, 93)), 1.6 + sc * 2.4, 100 + i)
    for k, (x, y, rx, ry) in enumerate(((10, 176, 20, 15), (36, 182, 9, 7), (260, 178, 22, 17), (236, 186, 8, 6), (4, 322, 14, 10), (268, 330, 16, 11), (24, 334, 7, 5))):
        rock_prop(s, x, y, rx, ry, 300 + k)
    spr(cv, s)
    return cv

# ---------------- town helpers ----------------
def cobbles(cv, mask, cols, sd, y0, y1):
    """perspective cobble rows (row height grows toward the viewer); fill, lit top lip, dark joints"""
    y = y0; row = 0
    while y < y1:
        hh = 2 + int((y - y0) / max(1, (y1 - y0)) * 3.2); wv = int(hh * 2.3) + 1; off = (row * 5 + int(_h(row, 1, sd) * wv)) % wv
        for x in range(-off, W, wv):
            ww = wv - 1 + (1 if _h(x, row, sd) < 0.3 else 0)
            st = mask & (YS >= y) & (YS < y + hh - 1) & (XS >= x) & (XS < x + ww - 1)
            tone = _h(x, row, sd + 1); c = cols[1] if tone < 0.6 else (cols[0] if tone < 0.8 else cols[2])
            cv.fill(st, c); cv.fill(st & (YS == y), cols[2] if c != cols[2] else 'mist')
            cv.fill(mask & (YS >= y) & (YS < y + hh) & ((XS == x + ww - 1) | (XS == x + ww - 2) & (YS == y + hh - 2)), cols[0])
        cv.fill(mask & (YS == y + hh - 1), cols[0] if len(cols) < 4 else cols[3])
        y += hh; row += 1
def barrel(s, x, y, w=8, h=10, ramp=('bark', 'wood_dk', 'wood', 'wood_lt')):
    s.add(e(x, y - h / 2, w / 2, h / 2) | r(int(x - w / 2), int(y - h + 2), int(x + w / 2), int(y - 1)), list(ramp))
    for yy in (int(y - h + 3), int(y - 3)): s.px([(xx, yy) for xx in range(int(x - w / 2) + 1, int(x + w / 2))], 'slate')
def crate(s, x0, y0, w, h, ramp=('wood_dk', 'wood', 'wood_lt')):
    s.add(r(x0, y0, x0 + w, y0 + h), list(ramp))
    s.add(ln((x0 + 1, y0 + h - 1), (x0 + w - 1, y0 + 1), 1.0), [ramp[0]], sep=False, flat=True)
def house(s, x, w, ytop, roof, yb, chimney=True, door=None, wall=('tan', 'sand', 'parchment'), beams=('bark', 'wood_dk')):
    s.add(r(x, ytop + 16, x + w, yb), list(wall))
    s.add(p([(x - 4, ytop + 18), (x + w / 2, ytop - 8), (x + w + 4, ytop + 18)]), list(roof))
    for k in range(3):                                                                        # roof courses
        yy = ytop - 2 + k * 6; half = (yy - (ytop - 8)) / 26 * (w / 2 + 4)
        s.px([(xx, yy) for xx in range(int(x + w / 2 - half) + 2, int(x + w / 2 + half) - 1) if (xx + k) % 2 == 0], roof[0])
    if chimney: s.add(r(x + w - 12, ytop - 8, x + w - 6, ytop + 6), ['slate', 'gray', 'silver'])
    for bx in (x, x + w // 2, x + w - 2): s.add(r(bx, ytop + 16, bx + 2, yb), list(beams), flat=True, sep=False)
    s.add(r(x, ytop + 30, x + w, ytop + 32), list(beams), flat=True, sep=False)
    s.add(r(x + 6, ytop + 20, x + 13, ytop + 27) | r(x + w - 16, ytop + 36, x + w - 9, ytop + 43), ['amber', 'gold'], flat=True)
    s.px([(x + 9, yy) for yy in range(ytop + 20, ytop + 27)] + [(xx, ytop + 23) for xx in range(x + 6, x + 13)], 'wood_dk')    # window cross
    if door: s.add(r(x + door, yb - 13, x + door + 9, yb), ['bark', 'wood_dk'], flat=True)
def steam(cv, x, y, n, sd, cols=('mist', 'silver')):
    for k in range(n): cv.cloud(x + int((_h(k, 1, sd) - 0.3) * 6) + k * 3, y - k * 8, 12 + k * 5, sd + k, cols=cols)

# ================================================================ Candlewick (town)
def candlewick():
    cv = Canvas(); cv.sky([('sky', 34), ('sky_lt', 56), ('cream', 44)])
    for i, (x, y, w) in enumerate(((40, 50, 40), (200, 40, 50), (126, 80, 22))): cv.cloud(x, y, w, i + 9)
    tree_line(cv, HOR - 30, ('haze', 'grass'), 21, crown=(5, 9), step=(5, 9))                   # far trees behind the roofs
    s = Sprite(W, H); yb = HOR + 2
    houses = [(-6, 44, 96, 'red'), (38, 40, 88, 'thatch'), (80, 52, 80, 'red'), (132, 46, 90, 'thatch'), (178, 44, 84, 'red'), (222, 54, 94, 'thatch')]
    ROOF = {'red': ('red_dk', 'red', 'coral'), 'thatch': ('wood', 'wood_lt', 'tan')}
    for i, (x, w, yt, rf) in enumerate(houses):
        house(s, x, w, yt, ROOF[rf], yb, door=(18 if i == 3 else (w // 2 + 4 if i % 2 == 0 else None)))
        if i == 3:                                                                              # the inn: kettle sign
            s.add(r(x + 34, yt + 34, x + 36, yt + 40), ['bark'], flat=True, sep=False)
            s.add(e(x + 35, yt + 44, 5, 4), ['ink', 'slate', 'gray']); s.add(ln((x + 40, yt + 43), (x + 43, yt + 40), 1.6), ['slate', 'gray'], sep=False)
    spr(cv, s)
    for i, (x, w, yt, rf) in enumerate(houses):
        if i % 2 == 0: steam(cv, x + w - 9, yt - 12, 3, 30 + i * 5)
    # ground: cobbled lane along the houses, packed earth square in front
    gnd = YS >= HOR + 3
    n = gnoise(70, 26, 101)
    bands(cv, gnd, n, ('wood_lt', 'tan', 'sand'), (0.2 - 0.12 * CALM, 0.8 + 0.1 * CALM))
    lane = (YS >= HOR + 3) & (YS < HOR + 24 + (noise1(W, 30, 2) * 4).astype(int)[None, :])
    cobbles(cv, lane, ('slate', 'gray', 'silver', 'slate'), 7, HOR + 4, HOR + 30)
    cv.fill(lane & (YS == HOR + 3), 'ink')
    kerb = lane & ~np.roll(lane, -1, 0); cv.fill(kerb, 'wood_lt'); cv.fill(np.roll(kerb, 1, 0) & gnd & ~lane, 'wood')
    for dx in (-26, 26):                                                                        # cart ruts toward the viewer
        t = np.clip((YS - 170) / (H - 170), 0, 1); rx_ = 135 + dx * (0.5 + t * 1.8)
        rut = (np.abs(XS - rx_) < 0.9 + t * 2.2) & (YS > 168) & (YS < 310) & (vn(XS / 3.0, YS / 9.0, 4) > 0.22); cv.fill(rut, 'wood_lt')
        cv.fill(rut & (np.abs(XS - rx_) < 0.5 + t * 0.8) & (YS > 200), 'tan')
    for i in range(70):                                                                         # straw + pebbles, sparse
        x, y = int(_h(i, 1, 55) * W), int(175 + _h(i, 2, 55) * 140)
        if y > 300 and i % 3: continue
        if i % 2: cv.px(x, y, 'gold'); cv.px(x + 1, y - (i % 4 == 1), 'amber')
        else: cv.px(x, y, 'parchment'); cv.px(x, y + 1, 'wood_lt')
    s = Sprite(W, H)                                                                            # well, barrels, crates, lamp post at the edges
    s.add(e(20, 186, 14, 5) | r(6, 172, 35, 186), ['slate', 'gray', 'silver'])
    for yy in (176, 181): s.px([(xx, yy + (xx // 5) % 2) for xx in range(7, 35) if xx % 5], 'slate')
    s.add(e(20, 172, 12, 3), ['outline'], flat=True, sep=False)
    s.add(r(8, 148, 10, 174) | r(30, 148, 32, 174), ['bark', 'wood_dk'], flat=True)
    s.add(p([(4, 150), (20, 140), (36, 150)]), ['red_dk', 'red', 'coral'])
    s.add(ln((10, 156), (30, 156), 1.4), ['bark'], flat=True, sep=False); s.add(ln((22, 157), (22, 166), 1.0), ['bark'], flat=True, sep=False)
    s.add(r(19, 166, 26, 171), ['wood_dk', 'wood'], flat=True)
    barrel(s, 44, 183); barrel(s, 52, 186, 7, 9)
    crate(s, 228, 172, 11, 9); crate(s, 236, 178, 10, 9); crate(s, 230, 164, 8, 8)
    s.add(r(255, 128, 258, 188), ['ink', 'slate'], flat=True)
    s.add(r(251, 120, 262, 130), ['ink', 'slate', 'gray'])
    s.add(r(253, 122, 260, 128), ['amber', 'gold', 'cream'], sep=False)
    spr(cv, s)
    # refine-2: fill the square's EDGES (centre x50-220 below y195 stays clean for the seats/table/hub UI)
    edge_zone = ((XS < 46) | (XS > 224)) & (YS > 190)
    for i in range(16):                                                                         # a few worn flagstones poking through the earth
        x = int(4 + _h(i, 1, 141) * 38) if i % 2 else int(228 + _h(i, 1, 141) * 38); y = int(196 + _h(i, 2, 141) * 120)
        fs = e(x, y, 4 + (y - 190) / 60, 1.6 + (y - 190) / 120) & edge_zone
        cv.fill(fs, 'tan'); cv.fill(fs & ~np.roll(fs, 1, 0), 'sand'); cv.fill(fs & ~np.roll(fs, -1, 0), 'wood_lt')
    for i in range(150):                                                                        # grass tufts hugging the edges + the house fronts
        x = int(_h(i, 1, 142) * 46) if i % 2 else 224 + int(_h(i, 1, 142) * 46); y = int(166 + _h(i, 2, 142) * 300)
        if y > 330 and i % 3: continue
        tuft(cv, x, y, 0 if y < 200 else 1, ('leaf_dk', 'leaf', 'grass'), i)
    for i in range(40):
        x, y = int(60 + _h(i, 3, 143) * 150), int(165 + _h(i, 4, 143) * 14); tuft(cv, x, y, 0, ('leaf', 'grass', 'lime'), i)
    s = Sprite(W, H)
    s.add(r(4, 214, 40, 220), ['wood_dk', 'wood', 'wood_lt']); s.add(r(4, 208, 40, 214), ['bark', 'wood_dk', 'wood'])        # flower trough
    for k, x in enumerate(range(7, 39, 4)): s.add(e(x, 207, 2.2, 2), [('red_dk', 'red', 'coral'), ('orange', 'amber', 'gold'), ('plum', 'violet', 'haze')][k % 3], sep=False); s.px([(x, 209)], 'leaf')
    s.add(r(232, 222, 266, 226), ['wood_dk', 'wood', 'wood_lt']); s.add(r(234, 226, 237, 232) | r(261, 226, 264, 232), ['bark', 'wood_dk'], flat=True)   # bench
    s.add(e(250, 214, 10, 6), ['wood', 'wood_lt', 'tan', 'sand']); s.add(e(250, 212, 7, 3), ['wood_lt', 'tan'], sep=False)      # hay bale
    s.add(e(16, 262, 9, 9) & ~e(16, 262, 6, 6), ['bark', 'wood_dk', 'wood']); s.add(e(16, 262, 2, 2), ['bark', 'wood_dk'])         # leaning cart wheel
    for a in range(0, 360, 60): s.add(ln((16, 262), (16 + 6 * np.cos(np.radians(a)), 262 + 6 * np.sin(np.radians(a))), 1.0), ['wood_dk'], flat=True, sep=False)
    for x in range(228, 270, 8): s.add(r(x, 252, x + 3, 268), ['bark', 'wood_dk', 'wood'])                                       # fence
    s.add(r(228, 255, 270, 257), ['wood_dk', 'wood', 'wood_lt'])
    crate(s, 6, 300, 12, 10); barrel(s, 262, 312, 9, 12)
    spr(cv, s)
    return cv

# ================================================================ Brinewick (coast fishing town; NEW)
def brinewick():
    cv = Canvas(); cv.sky([('sky', 30), ('sky_lt', 52), ('ice', 26)])
    for i, (x, y, w) in enumerate(((52, 44, 44), (196, 30, 54), (130, 70, 22))): cv.cloud(x, y, w, i + 21)
    SEA = 104
    cv.rect(0, SEA, W, SEA + 3, 'blue_dk'); cv.rect(0, SEA + 3, W, SEA + 14, 'blue'); cv.rect(0, SEA + 14, W, HOR + 4, 'sky')
    for i in range(40):
        x, y = int(_h(i, 1, 12) * W), int(SEA + 2 + _h(i, 2, 12) * 34); L_ = 3 + int(_h(i, 3, 12) * 7 + (y - SEA) / 6)
        cv.a[y, max(0, x):min(W, x + L_)] = C['sky_lt' if y > SEA + 14 else 'sky']
    s = Sprite(W, H)                                                                            # a far sail
    s.add(p([(214, SEA + 1), (220, SEA - 13), (221, SEA + 1)]), ['mist', 'white'], sep=False); s.add(r(208, SEA + 1, 226, SEA + 4), ['bark', 'wood_dk'], flat=True)
    spr(cv, s)
    yb = HOR + 1; s = Sprite(W, H)
    SHINGLE = ('navy', 'blue_dk', 'sky'); STONE = ('slate', 'gray', 'silver')
    # left: net shed + drying rack with a hanging net
    house(s, -4, 46, 92, SHINGLE, yb, chimney=False, door=18, wall=('wood_dk', 'wood', 'wood_lt'), beams=('bark', 'wood_dk'))
    for x0 in (48, 92): s.add(r(x0, 96, x0 + 3, yb), ['bark', 'wood_dk', 'wood'])
    s.add(r(46, 95, 97, 98), ['bark', 'wood_dk', 'wood'])
    spr(cv, s); s = Sprite(W, H)
    net = p([(51, 98), (92, 98), (88, 124), (70, 130), (55, 122)])
    for y in range(98, 131):
        for x in range(50, 93):
            if net[y, x] and ((x + y) % 4 == 0 or (x - y) % 4 == 0): cv.px(x, y, 'ink')
    for (x, y) in ((60, 110), (78, 116), (70, 104)): cv.px(x, y, 'amber'); cv.px(x + 1, y, 'orange')   # cork floats
    # centre: the salt-bread bakery, striped awning, loaf sign, bread rack
    house(s, 104, 58, 86, ('red_dk', 'red', 'coral'), yb, chimney=True, door=None, wall=STONE + ('mist',), beams=('slate', 'ink'))
    aw = p([(100, 118), (166, 118), (170, 128), (96, 128)]); s.add(aw, ['red_dk', 'red', 'coral'])
    for x in range(98, 170, 8): s.add(p([(x, 118), (x + 4, 118), (x + 4.5, 128), (x - 0.5, 128)]) & aw, ['silver', 'mist', 'white'], sep=False)
    s.add(r(108, 128, 158, yb), ['bark', 'wood_dk'], flat=True)                                     # shop opening
    s.add(r(106, 134, 160, 138), ['wood_dk', 'wood', 'wood_lt'])                                     # counter
    for k, x in enumerate(range(110, 156, 9)): s.add(e(x + 3, 132, 3.6, 2.2), ['wood', 'wood_lt', 'tan', 'sand'])   # salt loaves
    s.px([(x + 2, 131) for x in range(110, 156, 9)], 'white')                                         # salt crust
    s.add(r(122, 104, 144, 112), ['wood_dk', 'wood', 'wood_lt']); s.add(e(133, 108, 6, 2.4), ['wood_lt', 'tan', 'sand']); s.px([(131, 107), (134, 107)], 'white')
    # right: the damp forge, glowing mouth, anvil, quench barrel, steam
    s.add(r(178, 94, 268, yb), list(STONE))
    for yy in range(99, yb, 6):
        s.px([(xx, yy) for xx in range(179, 268)], 'slate'); s.px([(xx, yy + 1) for xx in range(179, 268) if xx % 3], 'silver')
        s.px([(xx, yy + k) for xx in range(179 + (yy // 6 % 2) * 6, 268, 12) for k in range(1, 6)], 'slate')
    s.add(p([(174, 96), (223, 78), (272, 96)]), ['ink', 'slate', 'gray'])
    s.add(r(238, 62, 250, 90), ['ink', 'slate', 'gray'])
    arch = (e(208, 122, 14, 8) | r(194, 122, 223, yb)) & (YS <= yb); s.add(arch, ['outline'], flat=True)
    s.add(r(197, 130, 220, yb) & (YS <= yb), ['blood', 'red_dk', 'orange'], sep=False, flat=True)
    s.add(p([(199, yb), (204, 128), (208, 134), (212, 126), (218, yb)]), ['orange', 'amber', 'gold'], sep=False)
    s.add(p([(203, yb), (208, 133), (213, yb)]), ['gold', 'cream'], sep=False, flat=True)
    s.add(r(192, 120, 225, 123), ['ink', 'slate', 'gray'])
    s.add(r(232, 128, 246, 132) | r(236, 132, 242, 138) | r(233, 138, 245, yb), ['ink', 'slate', 'gray'])      # anvil
    barrel(s, 258, yb, 9, 12, ramp=('wood_dk', 'wood', 'wood_lt', 'tan'))
    s.add(e(258, yb - 11, 4, 1.2), ['blue_dk', 'sky'], sep=False)
    spr(cv, s)
    steam(cv, 244, 56, 4, 71); steam(cv, 257, 122, 2, 73, cols=('white', 'mist'))
    for (x, y) in ((196, 134), (220, 128), (204, 124)): cv.px(x, y, 'gold')                         # sparks
    # ground: plank boardwalk along the fronts, wet sand toward the viewer, tide line puddles
    gnd = YS >= HOR + 2
    n = gnoise(70, 26, 131)
    bands(cv, gnd, n, ('tan', 'sand', 'parchment'), (0.18 - 0.12 * CALM, 0.8 + 0.1 * CALM))
    walk = (YS >= HOR + 2) & (YS < HOR + 20)
    cv.fill(walk, 'wood'); cv.fill(walk & (YS % 5 == (HOR + 2) % 5), 'wood_dk'); cv.fill(walk & (YS % 5 == (HOR + 3) % 5), 'wood_lt')
    sx = (XS + (YS - HOR) // 5 * 13) % 31 == 0; cv.fill(walk & sx, 'wood_dk')
    cv.fill(walk & (YS == HOR + 2), 'bark'); cv.fill((YS == HOR + 20), 'wood_dk'); cv.fill((YS == HOR + 21), 'tan')
    for x in range(6, W, 38): cv.rect(x, HOR + 20, x + 3, HOR + 26, 'wood_dk'); cv.rect(x, HOR + 26, x + 3, HOR + 27, 'tan')   # pilings
    for (cx, cy, rx_, ry_) in ((30, 214, 20, 4), (238, 236, 24, 5)):                            # two tide pools left by the damp
        pl = soften(e(cx, cy, rx_, ry_) | e(cx + rx_ * 0.5, cy + 2, rx_ * 0.6, ry_ * 0.7)); cv.fill(ndi.binary_dilation(pl, iterations=2), 'tan')
        cv.fill(pl, 'sky'); cv.fill(pl & ~np.roll(pl, 1, 0), 'blue'); cv.a[int(cy), int(cx - rx_ * 0.4):int(cx)] = C['sky_lt']
    for i in range(46):                                                                         # shells + pebbles
        x, y = int(_h(i, 1, 70) * W), int(170 + _h(i, 2, 70) * 140)
        if y > 300 and i % 3: continue
        cv.px(x, y, ('mist', 'wood_lt', 'coral', 'gray')[i % 4]); cv.px(x + 1, y, ('white', 'tan', 'red', 'slate')[i % 4])
    s = Sprite(W, H)                                                                            # props at the sides: lobster pot, rope coil, crates of fish
    s.add(e(18, 182, 12, 8) & (YS < 186), ['wood_dk', 'wood', 'wood_lt'])
    for x in range(8, 30, 4): s.px([(x, y) for y in range(176, 186)], 'bark')
    s.add(e(44, 186, 7, 3), ['bark', 'wood_dk', 'wood']); s.add(e(44, 185, 3.4, 1.3), ['outline'], flat=True, sep=False)
    crate(s, 230, 174, 14, 9); crate(s, 244, 180, 12, 8)
    for (x, y) in ((233, 173), (238, 172), (242, 173)): s.add(e(x, y, 2.4, 1.2), ['slate', 'silver', 'mist'], sep=False)
    spr(cv, s)
    return cv
