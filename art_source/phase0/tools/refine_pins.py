"""refine-2: three NEW 32x32 map pins in the existing loc_* style (dirt island base, building on top, #120c18 outline, light from the top-left)."""
import numpy as np
from regionlib import Sprite, E, P, R, LN
N = 32
def S(): return Sprite(N, N)
def e(*a, **k): return E(N, N, *a, **k)
def p(pts): return P(N, N, pts)
def r(*a): return R(N, N, *a)
def ln(*a): return LN(N, N, *a)
def base(s, grass=True, water=False):
    s.add(e(16, 26, 14, 4.6), ['bark', 'wood_dk'], flat=False)                               # island side (thickness)
    s.add(e(16, 24.4, 14, 4.4), ['wood', 'wood_lt', 'tan'], sep=False)                        # dirt top
    if grass:
        s.add(e(6, 24, 4, 1.8) | e(26, 25, 3.5, 1.6), ['leaf_dk', 'leaf', 'grass'], sep=False)
    if water: s.add(e(23, 25, 6, 2.2), ['blue_dk', 'blue', 'sky'], sep=False)
def brinewick():
    s = S(); base(s, water=True)
    s.add(r(5, 14, 17, 24), ['wood_dk', 'wood', 'wood_lt'])                                   # net shed walls
    s.add(p([(3, 15), (11, 7), (19, 15)]), ['navy', 'blue_dk', 'blue', 'sky'])               # blue roof
    s.add(r(9, 18, 12, 24), ['bark', 'wood_dk'], flat=True)                                     # door
    s.add(r(14, 16, 16, 18), ['amber', 'gold'], flat=True, sep=False)                           # lit window
    s.add(ln((20, 12), (20, 23), 1.2) | ln((28, 12), (28, 23), 1.2), ['wood_dk', 'wood'], flat=True)   # net-drying poles
    s.add(r(20, 13, 29, 15), ['gray', 'silver', 'mist'], sep=False)                             # hung net
    s.px([(22, 14), (24, 14), (26, 14)], 'slate')
    s.add(e(24, 24.5, 4, 1.4) & (np.mgrid[0:N, 0:N][0] >= 24), ['wood_dk', 'wood', 'wood_lt'])  # little boat in the water
    return s
def ashgate():
    s = S(); base(s)
    yy, xx = np.mgrid[0:N, 0:N]
    cliff = p([(1, 24), (2, 12), (5, 6), (10, 3), (16, 5), (20, 10), (21, 24)])
    s.add(cliff, ['slate', 'gray', 'silver', 'mist'])
    for a_, b_ in (((5, 9), (9, 12)), ((13, 6), (12, 11)), ((16, 9), (19, 13)), ((3, 15), (5, 18)), ((18, 16), (20, 20))):
        s.add(ln(a_, b_, 1.0), ['ink'], flat=True, sep=False)                                   # rock cracks / facets
    s.px([(6, 6), (7, 5), (11, 4), (12, 4), (3, 11)], 'white')
    s.add(e(10, 21, 4.4, 6) & (yy <= 24), ['outline'], flat=True)                             # dark cave mouth
    s.px([(9, 19), (11, 18)], 'amber')                                                           # eyes glinting in the dark
    s.add(p([(15, 12), (31, 16), (31, 18), (15, 15)]), ['wood_dk', 'wood', 'wood_lt'])        # lean-to roof planks off the cliff
    s.px([(19, 14), (23, 15), (27, 16)], 'wood_dk')
    s.add(r(29, 18, 31, 25), ['bark', 'wood_dk'], flat=True)                                     # front post
    s.add(r(22, 19, 28, 21), ['wood_dk', 'wood'], sep=False)                                    # crates/bench under the lean-to
    s.add(e(25, 26, 3.4, 1.4), ['slate', 'gray'])                                                # fire ring
    s.add(p([(22, 26), (24, 20), (25, 22), (26, 19), (28, 26)]), ['red', 'orange', 'amber', 'gold'])   # fire
    s.px([(25, 23), (25, 24), (26, 24)], 'cream')
    return s
def tent(s, x, y, w, h, ramp, stripe='cream'):
    s.add(p([(x - w, y), (x, y - h), (x + w, y)]) | r(x - w, y, x + w + 1, y + 2), ramp)
    for dx in (-w // 2, w // 2):
        s.px([(x + dx, yy) for yy in range(y - h + (abs(dx) * h) // w + 2, y + 2)], stripe)
    s.add(r(x - 1, y - 2, x + 2, y + 2), ['outline'], flat=True, sep=False)                    # dark doorway
    s.px([(x, y - h - 1)], 'gold')
def pebblegate():
    s = S(); base(s)
    s.add(r(2, 11, 30, 21), ['slate', 'gray', 'silver'])                                        # gate wall
    for x in range(2, 30, 4): s.add(r(x, 9, x + 2, 11), ['gray', 'silver'])                   # crenels
    s.add(r(12, 6, 21, 21), ['slate', 'gray', 'silver', 'mist'])                                # gatehouse
    for x in (12, 15, 18): s.add(r(x, 4, x + 2, 6), ['gray', 'silver'])
    s.add(e(16.5, 18, 2.6, 4) & (np.mgrid[0:N, 0:N][0] <= 20), ['outline'], flat=True)       # arch
    s.px([(15, 16), (17, 16), (16, 15)], 'slate')                                              # portcullis
    s.px([(4, 14), (8, 13), (24, 14), (27, 13)], 'mist')                                       # lit stones
    tent(s, 7, 23, 6, 9, ['red_dk', 'red'])                                            # striped stall tents in front
    tent(s, 25, 24, 5, 8, ['blue_dk', 'blue'])
    return s
PINS = dict(brinewick=brinewick, ashgate=ashgate, pebblegate=pebblegate)
