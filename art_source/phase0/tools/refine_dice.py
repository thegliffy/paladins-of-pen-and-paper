"""refine-2: dice + GM pass. d6 faces are redrawn (bevelled, rounded corners, same pip layout/frame order);
d20 frames keep their facet layout + number pixels and get facet relight + a top-left glint; GM gets relight + eye glints."""
import numpy as np
from PIL import Image
from pal import C
import refine_style as RS

PIPS = {1: [(1, 1)], 2: [(0, 0), (2, 2)], 3: [(0, 0), (1, 1), (2, 2)], 4: [(0, 0), (2, 0), (0, 2), (2, 2)],
        5: [(0, 0), (2, 0), (1, 1), (0, 2), (2, 2)], 6: [(0, 0), (2, 0), (0, 1), (2, 1), (0, 2), (2, 2)]}
#            lo (bottom/right bevel), face, hi (top/left bevel), pip
D6R = {'white': ('silver', 'white', 'white', 'outline'), 'red': ('red_dk', 'red', 'coral', 'white'),
       'blue': ('blue_dk', 'blue', 'sky', 'white'), 'green': ('leaf_dk', 'leaf', 'grass', 'white'),
       'yellow': ('amber', 'gold', 'cream', 'outline'), 'black': ('outline', 'ink', 'slate', 'white')}
ORDER = ['white', 'red', 'blue', 'green', 'yellow', 'black']
def px(a, x, y, n): a[y, x] = C[n] + (255,)
def d6_face(name, n):
    lo, f, hi, p = D6R[name]; a = np.zeros((8, 8, 4), np.uint8)
    for y in range(8):
        for x in range(8):
            if (x in (0, 7)) and (y in (0, 7)): continue                 # rounded corners
            if x in (0, 7) or y in (0, 7): px(a, x, y, 'outline'); continue
            if (x in (1, 6)) and (y in (1, 6)):                           # inner corners close the round
                px(a, x, y, hi if (x, y) == (1, 1) else lo); continue
            px(a, x, y, hi if (y == 1 or x == 1) else lo if (y == 6 or x == 6) else f)
    for gx, gy in PIPS[n]: px(a, 1 + gx * 2, 1 + gy * 2, p)   # original pip grid (1,3,5): even 1px gaps; pips sit over the lit bevel
    if name == 'white': px(a, 2, 1, 'white')
    return a
def d6_strip(name): return np.concatenate([d6_face(name, n) for n in range(1, 7)], 1)
def d6_all(): return np.concatenate([d6_strip(n) for n in ORDER], 0)

def d20(a):
    """facet relight on the grey/gold ramps; outline + number pixels (outline colour) are untouched; glint on the upper-left facet."""
    a = RS.A(a); h, w = a.shape[:2]; out = []
    for fx in range(0, w, 24):
        f = a[:, fx:fx + 24].copy()
        f = RS.relight(f, hi=0.22, lo=0.24, min_px=6, spec=0.06)
        op = f[..., 3] > 0; key = (f[..., 0].astype(int) << 16) | (f[..., 1].astype(int) << 8) | f[..., 2]
        ol = key == RS._key(C['outline'])
        ys, xs = np.nonzero(op & ~ol)
        if len(ys):
            s = xs + ys; i = np.argsort(s)
            for j in i[:40]:
                y, x = ys[j], xs[j]
                # first lit pixel 2 px inside the silhouette from the top-left
                if all(op[min(h - 1, y + d), min(23, x + d)] and not ol[min(h - 1, y + d), min(23, x + d)] for d in (1, 2)) and not ol[y, x]:
                    f[y + 1, x + 1] = C['white'] + (255,); break
        out.append(f)
    return np.concatenate(out, 1)

def gm(a): return RS.eye_glints(RS.relight(RS.A(a), hi=0.22, lo=0.24, spec=0.05, lock=('skin1',)))
