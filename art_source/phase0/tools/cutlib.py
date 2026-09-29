import numpy as np
from PIL import Image
from scipy import ndimage as ndi

SRC = '/workspace/src/'

def load(name):
    return np.asarray(Image.open(SRC + name + '.png').convert('RGB')).astype(np.int32)

def magenta_like(a):
    """pixels whose hue is magenta/pink and strongly saturated (bg or AA fringe)"""
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = np.maximum(np.maximum(r, g), b); mn = np.minimum(np.minimum(r, g), b)
    sat = (mx - mn) / np.maximum(mx, 1)
    # magenta: r and b both clearly above g, r>=0.55*b, b >= 0.35*r
    bright = (r - g > 60) & (b - g > 35) & (b > 0.30 * r) & (r > 0.55 * b) & (sat > 0.45)
    dark = (r - g > 25) & (b - g > 15) & (r >= 1.1 * b) & (b >= 0.35 * r)   # magenta mixed with dark outline (AA fringe)
    return bright | dark

def fg_mask(a, tol=110):
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    bg = np.median(border, axis=0)
    d = np.sqrt(((a - bg) ** 2).sum(-1))
    near = (d < tol) | magenta_like(a)
    # flood fill from edges through 'near' pixels
    lab, n = ndi.label(near)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bgmask = np.isin(lab, list(edge))
    fg = ~bgmask
    # also kill enclosed pure-bg holes (very close to bg)
    fg &= ~(d < 60)
    fg = ndi.binary_fill_holes(fg) & ~(d < 60)
    return fg, bg

def components(fg, min_area=300, close=6):
    m = ndi.binary_closing(fg, iterations=close) | fg
    lab, n = ndi.label(m)
    objs = ndi.find_objects(lab)
    out = []
    for i, sl in enumerate(objs):
        area = (lab[sl] == i + 1).sum()
        if area >= min_area:
            y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
            out.append((x0, y0, x1, y1, int(area)))
    out.sort(key=lambda t: (t[1] // 120, t[0]))
    return out

import pal
DARK = [i for i in range(48) if pal.PAL_LAB[i][0] < 22]
OUTL = pal.NAMES.index('outline')

def cut(a, fg, bbox, sx, sy=None, allowed=pal.NOPINK, dark_frac=0.28, outline=True, size=None, orphan=True, despeckle=True):
    sy = sy or sx
    x0, y0, x1, y1 = bbox[:4]
    A = a[y0:y1, x0:x1]; F = fg[y0:y1, x0:x1]
    fr = magenta_like(A) & F
    idx = pal.quant_idx(A, allowed)
    if size:
        W, Hh = size; sx = (x1 - x0) / W; sy = (y1 - y0) / Hh
    else:
        W = max(1, round((x1 - x0) / sx)); Hh = max(1, round((y1 - y0) / sy))
    out = np.zeros((Hh, W), int); al = np.zeros((Hh, W), bool)
    darkset = np.zeros(48, bool); darkset[DARK] = True
    for ty in range(Hh):
        ya, yb = int(ty * sy), max(int(ty * sy) + 1, int((ty + 1) * sy))
        for tx in range(W):
            xa, xb = int(tx * sx), max(int(tx * sx) + 1, int((tx + 1) * sx))
            f = F[ya:yb, xa:xb]; r = fr[ya:yb, xa:xb]
            cov = (f.sum() - 0.5 * r.sum()) / f.size
            if cov < 0.5: continue
            good = f & ~r
            vals = idx[ya:yb, xa:xb][good]
            al[ty, tx] = True
            if vals.size == 0: out[ty, tx] = OUTL; continue
            cnt = np.bincount(vals, minlength=48)
            dk = cnt[darkset].sum()
            if dk / vals.size >= dark_frac:
                c2 = cnt.copy(); c2[~darkset] = 0; out[ty, tx] = c2.argmax()
            else:
                c2 = cnt.copy(); c2[darkset] = 0; out[ty, tx] = c2.argmax()
    if orphan:
        n = np.zeros_like(al, int)
        n[1:] += al[:-1]; n[:-1] += al[1:]; n[:, 1:] += al[:, :-1]; n[:, :-1] += al[:, 1:]
        al &= ~(n == 0)
        hole = (~al) & (n >= 4); al |= hole
        for y, x in zip(*np.nonzero(hole)):
            nb = [out[yy, xx] for yy, xx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)) if 0<=yy<Hh and 0<=xx<W]
            out[y, x] = max(set(nb), key=nb.count)
    if despeckle:
        L = pal.PAL_LAB[:, 0]
        for _ in range(2):
            o2 = out.copy()
            for y in range(1, Hh - 1):
                for x in range(1, W - 1):
                    if not al[y, x] or out[y, x] == OUTL: continue
                    nb = [out[y-1, x], out[y+1, x], out[y, x-1], out[y, x+1]]
                    if not all(al[yy, xx] for yy, xx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1))): continue
                    m = max(set(nb), key=nb.count)
                    if nb.count(m) >= 3 and m != out[y, x] and abs(L[m] - L[out[y, x]]) < 14:
                        o2[y, x] = m
            out = o2
    if outline:
        pad = np.pad(al, 1)
        edge = al & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
        out[edge] = OUTL      # every silhouette pixel -> outline (kills dark-magenta fringe, crisp edge)
    return pal.idx_to_img(out, al)

def cut_full(a, size, allowed=None):
    """full-frame box downscale + quantise (no key)"""
    im = Image.fromarray(a.astype(np.uint8)).resize(size, Image.BOX)
    idx = pal.quant_idx(np.asarray(im).astype(float), allowed)
    return pal.idx_to_img(idx, np.ones(idx.shape, bool))
