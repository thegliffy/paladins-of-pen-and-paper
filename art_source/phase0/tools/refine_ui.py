"""REFINE PASS UI: parchment/dark panels, seat + enemy bars, hub button bar (button, pressed, 5 icons), header plate.
Same filenames/sizes/margins as before for existing pieces; new hub pieces under ui/hub/. Rules: refine_style.STYLE['ui']."""
import numpy as np
from pal import C
from regionlib import Sprite, E, P, R, LN, _h
def lay(w, h): return np.zeros((h, w, 4), np.uint8)
def fill(a, x0, y0, x1, y1, col):                       # inclusive rect
    a[y0:y1 + 1, x0:x1 + 1, :3] = C[col]; a[y0:y1 + 1, x0:x1 + 1, 3] = 255
def px(a, x, y, col):
    if 0 <= y < a.shape[0] and 0 <= x < a.shape[1]: a[y, x, :3] = C[col]; a[y, x, 3] = 255

def bevel_frame(a, x0, y0, x1, y1, ramp, width):
    """frame band `width` px inside the outline; light top/left, dark bottom/right, mid elsewhere (ramp = dark, mid, light)"""
    dk, md, lt = ramp
    for k in range(width):
        X0, Y0, X1, Y1 = x0 + k, y0 + k, x1 - k, y1 - k
        fill(a, X0, Y0, X1, Y0, lt if k == 0 else md); fill(a, X0, Y0, X0, Y1, lt if k == 0 else md)
        fill(a, X0, Y1, X1, Y1, dk if k == 0 else md); fill(a, X1, Y0, X1, Y1, dk if k == 0 else md)
    fill(a, x0 + width - 1, y0 + width - 1, x1 - width + 1, y0 + width - 1, dk)          # inner lip shadow (frame steps down to the paper)
def panel(fill_col, fibre, inner_shadow, N=48, m=6):
    a = lay(N, N); fill(a, 0, 0, N - 1, N - 1, 'outline')
    bevel_frame(a, 1, 1, N - 2, N - 2, ('wood_dk', 'wood', 'wood_lt'), 4)
    fill(a, 5, 5, N - 6, N - 6, fill_col)
    fill(a, 5, 5, N - 6, 5, inner_shadow); fill(a, 5, 5, 5, N - 6, inner_shadow)            # paper sits below the frame: shadow top-left
    T = N - 2 * m                                                                           # centre tile (seamless mod T)
    for k in range(int(T * T / 46)):
        u, v = int(_h(k, 1, 7) * T), int(_h(k, 2, 7) * T); L_ = 1 + int(_h(k, 3, 7) * 3)
        for d in range(L_):
            x, y = m + (u + d) % T, m + v
            if a[y, x, :3].tolist() == list(C[fill_col]): px(a, x, y, fibre)
    for (cx, cy) in ((2, 2), (N - 3, 2), (2, N - 3), (N - 3, N - 3)):                       # brass studs
        fill(a, cx - 1, cy - 1, cx + 1, cy + 1, 'outline'); px(a, cx, cy, 'gold')
        a[cy - 1:cy + 2, cx - 1:cx + 2, :3] = [C['amber'], C['gold'], C['amber']][1]; px(a, cx - 1, cy - 1, 'cream'); px(a, cx + 1, cy + 1, 'orange')
    return a

def bar_fill(w, rows):
    a = lay(w, len(rows))
    for y, c in enumerate(rows): fill(a, 0, y, w - 1, y, c)
    return a
SEAT_HP = ['coral', 'red', 'red', 'red_dk']; SEAT_MP = ['sky_lt', 'sky', 'blue']
def seat_hp(): return bar_fill(42, SEAT_HP)
def seat_mp(): return bar_fill(42, SEAT_MP)
def seat_hp_lowflash():
    return np.concatenate([seat_hp(), bar_fill(42, ['white', 'cream', 'cream', 'amber'])], axis=1)
def seat_frame(active=False):
    W_, H_ = 44, 10; a = lay(W_, H_); fill(a, 0, 0, W_ - 1, H_ - 1, 'outline')
    fill(a, 1, 1, W_ - 2, 4, 'blood')
    fill(a, 1, 6, W_ - 2, 8, 'navy')
    for x in range(11, W_ - 2, 10): px(a, x, 4, 'outline'); px(a, x, 8, 'outline')        # 25% ticks in the empty track (read the % at 1x)
    if active:
        A = lay(W_ + 2, H_ + 2); fill(A, 0, 0, W_ + 1, H_ + 1, 'outline'); A[1:-1, 1:-1] = a
        fill(A, 1, 1, W_, 1, 'cream'); fill(A, 1, 1, 1, H_, 'cream'); fill(A, 1, H_, W_, H_, 'amber'); fill(A, W_, 1, W_, H_, 'amber')
        return A
    return a
def enemy_hp(): return bar_fill(30, ['coral', 'red', 'red_dk'])

# ---------------- hub button bar ----------------
def hub_button(down=False, N=32):
    """9-slice (margin 6) wooden-framed parchment button; pressed = bevel swapped + darker paper"""
    a = lay(N, N); fill(a, 0, 0, N - 1, N - 1, 'outline')
    ramp = ('wood_lt', 'wood', 'wood_dk') if down else ('wood_dk', 'wood', 'wood_lt')
    bevel_frame(a, 1, 1, N - 2, N - 2, ramp, 3)
    fill(a, 4, 4, N - 5, N - 5, 'sand' if down else 'parchment')
    if down: fill(a, 4, 4, N - 5, 5, 'tan'); fill(a, 4, 4, 5, N - 5, 'tan')
    else: fill(a, 4, N - 5, N - 5, N - 5, 'sand'); fill(a, N - 5, 4, N - 5, N - 5, 'sand')
    return a
def header_plate(N=24):
    """9-slice (margin 4) parchment plate for the hub place name + blurb (replaces the flat StyleBox look)"""
    a = lay(N, N); fill(a, 0, 0, N - 1, N - 1, 'outline'); bevel_frame(a, 1, 1, N - 2, N - 2, ('wood_dk', 'wood', 'wood_lt'), 2)
    fill(a, 3, 3, N - 4, N - 4, 'parchment'); fill(a, 3, 3, N - 4, 3, 'sand')
    return a

def _icon(build):
    s = Sprite(16, 16); build(s); return s.image(trim=False)
def e(*a, **k): return E(16, 16, *a, **k)
def p(pts): return P(16, 16, pts)
def r(*a): return R(16, 16, *a)
def ln(*a): return LN(16, 16, *a)
WOOD = ['wood_dk', 'wood', 'wood_lt']; STEEL = ['gray', 'silver', 'mist', 'white']; LEATHER = ['bark', 'wood_dk', 'wood']
def icon_travel(s):                    # boot + road arrow
    s.add(p([(4, 2), (9, 2), (9, 9), (13, 10), (14, 13), (3, 13)]), LEATHER + ['wood_lt'], rim=True)
    s.add(r(3, 12, 15, 14), ['bark', 'wood_dk'], rim=True); s.px([(5, 4), (5, 6), (5, 8)], 'tan')
def icon_fight(s):                     # crossed swords
    for flip in (0, 1):
        pts = [(2 + i, 13 - i) for i in range(11)] if flip == 0 else [(13 - i, 13 - i) for i in range(11)]
        m = np.zeros((16, 16), bool)
        for x, y in pts: m[y, x] = True; m[y, min(15, x + (1 if flip == 0 else -1))] = True
        s.add(m, STEEL, rim=True)
    s.add(r(1, 11, 5, 13) | r(11, 11, 15, 13), ['orange', 'amber', 'gold'], rim=True)
    s.add(r(1, 13, 3, 15) | r(13, 13, 15, 15), LEATHER, rim=True)
def icon_rest(s):                      # campfire
    s.add(ln((2, 13), (13, 11), 2.2) | ln((3, 11), (14, 13), 2.2), WOOD, rim=True)
    s.add(p([(4, 11), (6, 5), (8, 7), (9, 2), (12, 8), (12, 11)]), ['red', 'orange', 'amber', 'gold'], rim=True)
    s.add(p([(6, 11), (8, 8), (10, 11)]), ['gold', 'cream'], rim=True, sep=False)
def icon_quest(s):                     # rolled scroll with a wax seal
    s.add(r(3, 3, 13, 13), ['sand', 'parchment', 'cream'], rim=True)
    s.add(r(2, 2, 14, 4) | r(2, 12, 14, 14), ['tan', 'sand', 'parchment'], rim=True)
    for y in (6, 8, 10): s.px([(x, y) for x in range(5, 12) if (x + y) % 4], 'wood')
    s.add(e(11, 11, 2.2, 2.2), ['red_dk', 'red', 'coral'], rim=True)
def icon_gear(s):                      # backpack
    s.add(r(3, 4, 13, 14), LEATHER + ['wood_lt'], rim=True)
    s.add(r(4, 8, 12, 12), ['wood_dk', 'wood', 'wood_lt'], rim=True); s.px([(8, 9), (8, 10)], 'gold')
    s.add(p([(5, 4), (6, 1), (10, 1), (11, 4)]) & ~r(7, 2, 9, 4), ['bark', 'wood_dk'], rim=True)
HUB_ICONS = dict(travel=icon_travel, fight=icon_fight, rest=icon_rest, quest=icon_quest, gear=icon_gear)
