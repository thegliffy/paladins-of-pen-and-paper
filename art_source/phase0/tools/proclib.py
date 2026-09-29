import numpy as np
from PIL import Image
import pal
from pal import C
def z(W, H): return np.zeros((H, W), bool)
def grid(W, H):
    ys, xs = np.mgrid[0:H, 0:W]; return xs, ys
def ell(W, H, cx, cy, rx, ry):
    xs, ys = grid(W, H); return ((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2 <= 1.0
def rect(W, H, x0, y0, x1, y1):
    m = z(W, H); m[max(0, y0):y1 + 1, max(0, x0):x1 + 1] = True; return m
def pts(W, H, lst):
    m = z(W, H)
    for x, y in lst:
        if 0 <= x < W and 0 <= y < H: m[y, x] = True
    return m
def sh(m, dx, dy):
    o = np.zeros_like(m); H, W = m.shape
    ys = slice(max(0, dy), min(H, H + dy)); yd = slice(max(0, -dy), min(H, H - dy))
    xs = slice(max(0, dx), min(W, W + dx)); xd = slice(max(0, -dx), min(W, W - dx))
    o[ys, xs] = m[yd, xd]; return o
def ring(m, diag=False):
    n = sh(m, 1, 0) | sh(m, -1, 0) | sh(m, 0, 1) | sh(m, 0, -1)
    if diag: n |= sh(m, 1, 1) | sh(m, -1, -1) | sh(m, 1, -1) | sh(m, -1, 1)
    return n & ~m
def e_right(m): return m & ~sh(m, -1, 0)
def e_left(m): return m & ~sh(m, 1, 0)
def e_top(m): return m & ~sh(m, 0, 1)
def e_bot(m): return m & ~sh(m, 0, -1)
def layer(W, H): return np.zeros((H, W, 4), np.uint8)
def paint(L, m, col):
    L[m] = tuple(col) + (255,)
def shade(L, m, base, shadow=None, light=None, dark=None, shw=1):
    paint(L, m, base)
    if shadow is not None:
        s = e_right(m) | e_bot(m)
        if shw > 1: s |= e_right(m & ~s) | e_bot(m & ~s)
        paint(L, s, shadow)
    if light is not None:
        paint(L, (e_top(m) | e_left(m)) & ~(e_right(m) | e_bot(m)), light)
def outline(L, col=None, diag=False, where=None):
    op = L[..., 3] > 0; r = ring(op, diag)
    if where is not None: r &= where
    paint(L, r, col or C['outline'])
def over(dst, src):
    m = src[..., 3] > 0; dst[m] = src[m]; return dst
def img(L): return Image.fromarray(np.ascontiguousarray(L), 'RGBA').copy()
def arr(im): return np.array(im.convert('RGBA'))
def remap_arr(L, mapping):
    out = L.copy()
    for k, v in mapping.items():
        m = (L[..., 0] == k[0]) & (L[..., 1] == k[1]) & (L[..., 2] == k[2]) & (L[..., 3] == 255)
        out[m, :3] = v
    return out
def hsh(x, y, seed=0):
    v = (x * 374761393 + y * 668265263 + seed * 2246822519) & 0xffffffff
    v = ((v ^ (v >> 13)) * 1274126177) & 0xffffffff
    return (v ^ (v >> 16)) / 0xffffffff
