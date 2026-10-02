"""REFINE-2 backdrops (270x480): Forest, Gravel Keep, Briar Cross, Lantern Reach + new towns Ashgate and Pebblegate.
Same framing as phase 1 (horizon y141, monster feet y222-266 clear, calm below y300); terrain unoutlined, props outlined."""
import numpy as np
from scipy import ndimage as ndi
from regionlib import Canvas, Sprite, _h, noise1, shade_idx
from pal import C
from refine_backdrops import (W, H, HOR, YS, XS, e, p, r, ln, spr, vn, YV, SC, GU, GV, gnoise, bands, soften, CALM, tuft, flower, tree_line,
                              cells, rock_facets, rock_poly, rock_prop, edge_of, cobbles, barrel, crate, house, steam)

def scatter(n, sd, y0, y1, skip=None, calm_keep=0.3):
    """deterministic (x, y, depth) points; fewer below y300; skip(x, y) -> True to drop"""
    out = []
    for i in range(n):
        x, y = int(_h(i, 1, sd) * W), int(y0 + _h(i, 2, sd) ** 0.9 * (y1 - y0))
        if y > 300 and _h(i, 3, sd) > calm_keep: continue
        if skip is not None and skip(x, y): continue
        out.append((i, x, y, (y - HOR) / (H - HOR)))
    return out
def trunk(s, x, y0, y1, w, ramp=('bark', 'wood_dk', 'wood'), roots=True):
    s.add(r(int(x - w / 2), y0, int(x + w / 2), y1), list(ramp))
    s.px([(int(x - w / 2) + 1, yy) for yy in range(y0 + 2, y1 - 1) if yy % 7 < 3], ramp[2])               # lit bark ridges (left)
    s.px([(int(x + w / 2) - 2, yy) for yy in range(y0 + 4, y1 - 1, 9)], ramp[0])
    if roots: s.add(p([(x - w / 2 - 4, y1), (x - w / 2, y1 - 6), (x + w / 2, y1 - 6), (x + w / 2 + 4, y1)]), list(ramp))
def canopy(s, cx, cy, rx, ry, sd, ramp=('pine_dk', 'pine', 'leaf_dk', 'leaf')):
    m = np.zeros((H, W), bool)
    for k in range(7):
        a = k / 7 * 2 * np.pi; m |= e(cx + np.cos(a) * rx * 0.55, cy + np.sin(a) * ry * 0.45, rx * (0.45 + 0.15 * _h(k, 1, sd)), ry * (0.5 + 0.12 * _h(k, 2, sd)))
    m |= e(cx, cy, rx * 0.7, ry * 0.7); s.add(m, list(ramp), bulge=0.6)
    return m
def fern(cv, x, y, sz, cols=('pine', 'leaf_dk', 'leaf')):
    for side in (-1, 1):
        for k in range(sz + 2):
            xx = x + side * k; yy = y - k // 2 - (k == sz + 1)
            cv.px(xx, yy, cols[1] if k < sz else cols[2]); cv.px(xx, yy + 1, cols[0])
    for k in range(sz): cv.px(x, y - k, cols[2])
def mushroom_px(cv, x, y, cap='red'):
    cv.px(x, y, 'cream'); cv.px(x, y - 1, 'cream'); cv.px(x - 1, y - 2, cap); cv.px(x, y - 2, cap); cv.px(x + 1, y - 2, 'red_dk' if cap == 'red' else 'wood'); cv.px(x, y - 3, cap); cv.px(x - 1, y - 2, 'coral' if cap == 'red' else 'tan')

# ================================================================ Forest (default combat backdrop)
def forest():
    cv = Canvas(); cv.sky([('sky', 22), ('sky_lt', 30), ('ice', 18)])
    for i, (x, y, w) in enumerate(((60, 30, 40), (200, 22, 50))): cv.cloud(x, y, w, i + 41)
    tree_line(cv, HOR - 40, ('haze', 'grass'), 51, crown=(8, 13), step=(6, 10))                     # far wood, hazy
    tree_line(cv, HOR - 18, ('pine', 'leaf_dk'), 52, crown=(10, 16), step=(7, 12), rim='leaf')
    cv.fill((YS >= HOR - 18) & (YS < HOR + 2), 'pine'); cv.fill((YS >= HOR - 6) & (YS < HOR + 2), 'pine_dk')    # shade under the far wood
    for i in range(18):                                                                          # far thin trunks in the shade
        x = int(_h(i, 1, 53) * W); cv.rect(x, HOR - 14, x + 2, HOR + 2, 'wood_dk' if i % 2 else 'bark')
    g = YS >= HOR + 2; n = gnoise(70, 26, 54)
    bands(cv, g, n, ('leaf_dk', 'leaf', 'grass'), (0.2 - 0.1 * CALM, 0.78 + 0.12 * CALM))
    cv.fill(g & (YS < HOR + 6), 'leaf_dk')
    sun = soften(g & (gnoise(46, 16, 55) > 0.7) & (YS > 165) & (CALM < 0.5), 2); cv.fill(sun & (n > 0.45), 'grass'); cv.fill(sun & (n > 0.7), 'lime')   # broad sun patches through the canopy
    # forest path: packed earth, 2-tone edges, winding to the right
    t = np.clip((YS - HOR) / (H - HOR), 0, 1); cxp = 150 + 40 * t + 18 * np.sin(t * 4.2) + (noise1(H, 24, 56)[YS] - 0.5) * 4
    half = 2.5 + t * 17; path = soften((np.abs(XS - cxp) < half) & (YS > HOR + 4))
    pn = gnoise(12, 5, 57)
    cv.fill(path, 'wood_lt'); cv.fill(path & (pn > 0.62), 'tan'); cv.fill(path & (pn < 0.28) & (YS > 200), 'wood')
    cv.fill(path & ~ndi.binary_erosion(path) & (XS < cxp), 'leaf_dk'); cv.fill(path & ~ndi.binary_erosion(path) & (XS > cxp), 'wood_dk')   # edges
    for (i, x, y, d) in scatter(260, 58, HOR + 8, H, skip=lambda x, y: path[min(H - 1, y + 1), x]):
        tuft(cv, x, y, 0 if d < 0.12 else (1 if d < 0.45 else 2), ('leaf_dk', 'leaf', 'grass') if i % 3 else ('pine', 'leaf_dk', 'leaf'), i)
    for (i, x, y, d) in scatter(30, 59, 160, 300, skip=lambda x, y: path[y, x] or (40 < x < 230 and 205 < y < 275)):
        if i % 3 == 0: mushroom_px(cv, x, y, 'red' if i % 2 else 'wood')
        else: fern(cv, x, y, 2 + int(d * 4))
    s = Sprite(W, H)                                                                              # near trees framing the sides (props)
    for (x, w, y0, y1) in ((52, 6, 60, 150), (214, 7, 56, 152), (84, 4, 80, 146), (190, 4, 84, 146)):     # mid-distance trunks
        trunk(s, x, y0, y1, w, roots=False)
    for (cx, cy, rx, ry, sd) in ((52, 62, 20, 16, 65), (214, 58, 22, 16, 66), (84, 82, 12, 10, 67), (190, 86, 12, 9, 68)):
        canopy(s, cx, cy, rx, ry, sd, ramp=('pine', 'leaf_dk', 'leaf', 'grass'))
    for (x, w, y1) in ((2, 26, 238), (32, 12, 200), (254, 28, 250), (228, 12, 194)):
        trunk(s, x, 0, y1, w)
    canopy(s, 14, 18, 62, 44, 61); canopy(s, 258, 14, 64, 46, 62); canopy(s, 70, -6, 40, 26, 63); canopy(s, 200, -8, 44, 26, 64)
    s.add(p([(0, 300), (40, 296), (52, 304), (44, 312), (0, 312)]), ['bark', 'wood_dk', 'wood'])     # fallen log at the left edge
    s.add(e(48, 304, 4, 6), ['wood_lt', 'tan', 'sand']); s.px([(48, 304), (47, 303)], 'wood')
    for k, (x, y, rx, ry) in enumerate(((264, 300, 14, 9), (14, 186, 8, 5), (238, 194, 6, 4))): rock_prop(s, x, y, rx, ry, 700 + k, ramp=('slate', 'gray', 'silver', 'mist'))
    spr(cv, s)
    for (x, y) in ((20, 70), (244, 64), (60, 40), (210, 40), (14, 112), (258, 96)):              # canopy light flecks
        cv.px(x, y, 'grass'); cv.px(x + 1, y, 'lime')
    return cv

# ================================================================ Gravel Keep (keep)
def gravel_keep():
    cv = Canvas(); cv.sky([('plum_dk', 26), ('plum', 34), ('violet', 26), ('amber', 18), ('gold', 12)])     # dusk
    for i, (x, y, w) in enumerate(((50, 40, 52), (210, 30, 60), (140, 70, 30))): cv.cloud(x, y, w, i + 81, cols=('violet', 'plum'))
    hills, _ = cv.ridge(HOR - 6, 18, 60, 82, ('plum', 'violet'))
    s = Sprite(W, H)
    WALL = ('ink', 'slate', 'gray', 'silver')
    s.add(r(56, 66, 214, HOR + 2), list(WALL), bulge=0.4)                                          # curtain wall
    for x in range(56, 214, 10): s.add(r(x, 60, x + 6, 67), list(WALL))                            # merlons
    for (x0, x1, yt) in ((40, 76, 34), (194, 230, 34), (114, 156, 20)):                             # towers
        s.add(r(x0, yt, x1, HOR + 2), list(WALL), bulge=0.4)
        for x in range(x0, x1, 8): s.add(r(x, yt - 6, x + 5, yt + 1), list(WALL))
        for yy in range(yt + 10, HOR - 4, 16): s.add(r((x0 + x1) // 2 - 2, yy, (x0 + x1) // 2 + 2, yy + 6), ['orange', 'amber', 'gold'], flat=True)   # lit slit windows
    s.add(r(122, 104, 148, HOR + 2) | e(135, 104, 13, 9), ['outline'], flat=True)                  # gate arch
    s.add(r(124, 108, 146, HOR + 2) & ((XS - 124) % 4 < 1) | r(124, 108, 146, HOR + 2) & ((YS - 108) % 5 < 1), ['slate', 'gray'], flat=True, sep=False)   # portcullis
    for (x, c) in ((95, 'red'), (175, 'red')):                                                      # banners
        s.add(r(x - 5, 76, x + 5, 104) | p([(x - 5, 104), (x, 110), (x + 5, 104)]), ['red_dk', 'red', 'coral'])
        s.add(e(x, 88, 2.4, 2.4), ['amber', 'gold'], sep=False)
    spr(cv, s)
    stone = (YS >= 34) & (YS < HOR + 2) & (XS >= 40) & (XS < 230)                                 # mortar courses on the masonry
    for yy in range(36, HOR, 6):
        m = (YS == yy) & stone & (cv.a[..., 0] == C['gray'][0]) & (cv.a[..., 1] == C['gray'][1]); cv.fill(m, 'slate')
        for x in range(42 + (yy // 6 % 2) * 5, 230, 10):
            for k in range(1, 6):
                if yy + k < H and stone[yy + k, x] and (cv.a[yy + k, x] == C['gray']).all(): cv.px(x, yy + k, 'slate')
    # ground: gravel courtyard (grey-brown ramp, soft perspective), flagstone road to the gate, ruts
    g = YS >= HOR + 2; n = gnoise(80, 30, 84)
    dep = (YS - HOR) / (H - HOR); v = (1 - dep) * 0.5 + n * 0.5
    cv.fill(g, 'gray'); cv.fill(g & (v > 0.72), 'silver'); cv.fill(g & (v < 0.3) & (CALM < 0.5), 'slate')      # soft value falloff, no camo
    cv.fill(g & (YS < HOR + 6), 'slate'); cv.fill(g & (YS < HOR + 4), 'ink')
    t = np.clip((YS - HOR) / (H - HOR), 0, 1); half = 12 + t * 60
    road = (np.abs(XS - 135) < half) & (YS > HOR + 2)
    # perspective flagstones: rows grow toward the viewer, joints offset per row
    y = HOR + 3; row = 0
    while y < H:
        hh = 2 + int((y - HOR) / 40); tt = (y - HOR) / (H - HOR); wv = int(8 + tt * 30)
        off = (row * 7) % wv
        for x in range(-wv, W + wv, wv):
            st = road & (YS >= y) & (YS < y + hh - 1) & (XS >= x + off) & (XS < x + off + wv - 1)
            tone = _h(x, row, 85); cv.fill(st, 'gray' if tone < 0.6 else ('silver' if tone < 0.82 else 'slate'))
            cv.fill(st & (YS == y), 'mist' if tone > 0.82 else 'silver')
        cv.fill(road & (YS == y + hh - 1), 'slate')
        cv.fill(road & (YS >= y) & (YS < y + hh) & (((XS - off) % wv) == wv - 1), 'slate')
        y += hh; row += 1
    edge = road & ~ndi.binary_erosion(road); cv.fill(edge, 'ink')
    for (i, x, y, d) in scatter(320, 86, HOR + 8, H, skip=lambda x, y: road[y, x]):                   # gravel grit
        cv.px(x, y, 'silver' if i % 3 else 'mist'); cv.px(x, y + 1, 'slate')
        if d > 0.4 and i % 2: cv.px(x + 1, y, 'gray'); cv.px(x + 1, y + 1, 'slate')
    for (i, x, y, d) in scatter(60, 87, 160, 320, skip=lambda x, y: road[y, x] or (30 < x < 240 and 205 < y < 275)):
        tuft(cv, x, y, 0 if d < 0.2 else 1, ('pine', 'leaf_dk', 'leaf'), i)                        # weeds between the stones
    s = Sprite(W, H)                                                                              # rubble at the sides
    for k, (x, y, rx, ry) in enumerate(((12, 180, 14, 9), (34, 186, 7, 5), (256, 184, 15, 10), (238, 190, 6, 4), (8, 318, 12, 8), (262, 326, 13, 9))):
        rock_prop(s, x, y, rx, ry, 800 + k)
    s.add(r(20, 150, 24, 178), ['bark', 'wood_dk', 'wood']); s.add(r(16, 144, 28, 151), ['ink', 'slate', 'gray']); s.add(r(18, 146, 26, 150), ['orange', 'amber', 'gold'], sep=False)   # brazier post
    s.add(r(246, 150, 250, 178), ['bark', 'wood_dk', 'wood']); s.add(r(242, 144, 254, 151), ['ink', 'slate', 'gray']); s.add(r(244, 146, 252, 150), ['orange', 'amber', 'gold'], sep=False)
    spr(cv, s)
    for (x, y) in ((22, 141), (21, 139), (248, 141), (249, 138)): cv.px(x, y, 'gold')
    return cv

def briar(s, cx, cy, rx, ry, sd):
    """bramble clump prop: dark thorny mass, lit top-left leaves, red berries, thorn ticks on the rim"""
    m = np.zeros((H, W), bool)
    for k in range(6): m |= e(cx + (_h(k, 1, sd) - 0.5) * rx * 1.2, cy - _h(k, 2, sd) * ry * 0.6, rx * (0.4 + 0.3 * _h(k, 3, sd)), ry * (0.5 + 0.3 * _h(k, 4, sd)))
    m &= YS <= cy + ry * 0.4; s.add(m, ['pine_dk', 'pine', 'leaf_dk', 'leaf'], bulge=0.6)
    ys, xs = np.nonzero(edge_of(m))
    for j in range(0, len(ys), 5): s.px([(xs[j] + (1 if xs[j] > cx else -1), ys[j] - 1)], 'bark')
    for j in range(len(ys) // 9):
        k = int(_h(j, 5, sd) * len(ys)); x, y = xs[k] + int((cx - xs[k]) * 0.3), ys[k] + 2
        if m[y, x]: s.px([(x, y)], 'red'); s.px([(x, y - 1)], 'coral')

# ================================================================ Briar Cross (meadow crossroads)
def briar_cross():
    cv = Canvas(); cv.sky([('blue', 26), ('sky', 50), ('sky_lt', 68)])
    for i, (x, y, w) in enumerate(((40, 46, 44), (170, 34, 60), (236, 82, 26))): cv.cloud(x, y, w, i + 91)
    tree_line(cv, HOR - 8, ('haze', 'grass'), 92, crown=(5, 9), step=(5, 8))
    tree_line(cv, HOR - 1, ('pine', 'leaf_dk'), 93, crown=(5, 10), step=(5, 12), rim='leaf')
    s = Sprite(W, H)                                                                              # a far farmhouse on the right
    house(s, 206, 30, HOR - 34, ('red_dk', 'red', 'coral'), HOR - 1, chimney=True, door=None)
    spr(cv, s); steam(cv, 230, HOR - 50, 2, 94)
    g = YS >= HOR; n = gnoise(70, 26, 95)
    bands(cv, g, n, ('leaf', 'grass', 'lime'), (0.28 - 0.12 * CALM, 0.76 + 0.14 * CALM))
    cv.fill(g & (YS < HOR + 4), 'grass')
    # two roads: one across at the horizon band, one from the bottom; both packed earth with lit/dark edges and ruts
    t = np.clip((YS - HOR) / (H - HOR), 0, 1)
    cross = (YS >= HOR + 14 + (noise1(W, 40, 96) * 3).astype(int)[None, :]) & (YS < HOR + 22 + (noise1(W, 30, 97) * 3).astype(int)[None, :])
    cxp = 132 + 8 * np.sin(t * 2.6) + (noise1(H, 30, 98)[YS] - 0.5) * 3; half = 4 + t * 36
    down = (np.abs(XS - cxp) < half) & (YS >= HOR + 18)
    up = (np.abs(XS - (132 + (YS - HOR) * 0.1)) < 2.6) & (YS >= HOR) & (YS < HOR + 18)
    road = soften(cross | down | up)
    pn = gnoise(12, 5, 99)
    cv.fill(road, 'wood_lt'); cv.fill(road & (pn > 0.55), 'tan'); cv.fill(road & (pn < 0.18) & (YS > 260), 'wood')
    ed = road & ~ndi.binary_erosion(road); cv.fill(ed & ~np.roll(road, 1, 0), 'grass'); cv.fill(ed & ~np.roll(road, -1, 0), 'leaf'); cv.fill(ed & np.roll(road, -1, 0) & np.roll(road, 1, 0), 'leaf')
    for dx in (-0.45, 0.45):                                                                      # cart ruts in the near road
        rut = down & (np.abs(XS - (cxp + dx * half)) < 0.5 + t * 0.9) & (YS > 175) & (vn(XS / 3.0, YS / 8.0, 7) > 0.25); cv.fill(rut, 'wood')
    for (i, x, y, d) in scatter(300, 100, HOR + 6, H, skip=lambda x, y: road[min(H - 1, y + 1), x]):
        tuft(cv, x, y, 0 if d < 0.12 else (1 if d < 0.45 else 2), ('leaf', 'leaf_dk', 'lime') if n[y, x] > 0.5 else ('leaf_dk', 'leaf', 'grass'), i)
    for (i, x, y, d) in scatter(40, 101, 172, 300, skip=lambda x, y: road[y, x] or (30 < x < 240 and 205 < y < 275)):
        flower(cv, x, y, ('cream', 'gold', 'white', 'violet')[i % 4])
    s = Sprite(W, H)                                                                              # signpost at the crossing, briars at the sides
    s.add(r(100, 136, 104, 168), ['bark', 'wood_dk', 'wood'])
    s.add(p([(86, 138), (112, 136), (116, 140), (112, 144), (86, 144)]), ['wood_dk', 'wood', 'wood_lt'])
    s.add(p([(118, 148), (92, 146), (88, 150), (92, 154), (118, 154)]), ['wood_dk', 'wood', 'wood_lt'])
    s.px([(x, 141) for x in range(90, 110, 2)] + [(x, 151) for x in range(95, 115, 2)], 'wood_dk')
    for k, (x, y, rx, ry) in enumerate(((14, 190, 22, 16), (40, 182, 12, 9), (256, 196, 22, 16), (232, 186, 11, 8), (6, 318, 18, 14), (264, 324, 18, 13))):
        briar(s, x, y, rx, ry, 1100 + k)
    for k, (x, y, rx, ry) in enumerate(((70, 176, 5, 3), (210, 300, 7, 4))): rock_prop(s, x, y, rx, ry, 1200 + k, ramp=('slate', 'gray', 'silver', 'mist'))
    spr(cv, s)
    return cv

# ================================================================ Lantern Reach (coast)
def lantern_reach():
    cv = Canvas(); cv.sky([('sky', 30), ('sky_lt', 50), ('ice', 26)])
    for i, (x, y, w) in enumerate(((50, 40, 48), (160, 28, 56), (120, 76, 24))): cv.cloud(x, y, w, i + 111)
    SEA = 98
    cv.rect(0, SEA, W, SEA + 3, 'blue_dk'); cv.rect(0, SEA + 3, W, SEA + 16, 'blue'); cv.rect(0, SEA + 16, W, HOR + 2, 'sky')
    for i in range(48):
        x, y = int(_h(i, 1, 112) * W), int(SEA + 2 + _h(i, 2, 112) * (HOR - SEA)); L_ = 3 + int(_h(i, 3, 112) * 6 + (y - SEA) / 5)
        cv.a[y, max(0, x):min(W, x + L_)] = C['sky_lt' if y > SEA + 16 else 'sky']
    # right headland: faceted cliff + lighthouse (props)
    head = p([(176, HOR + 6), (186, 98), (198, 82), (214, 74), (240, 70), (270, 66), (270, HOR + 6)])
    lab, gap = cells(XS.astype(float), YS.astype(float), 26, 113, (170, 60, 280, HOR + 10), aniso=(0.8, 1.3))
    rock_facets(cv, head, lab, ['slate', 'gray', 'silver', 'mist'], 'ink', 113, bulge=0.55, gap=gap, crack_w=1.1)
    cv.fill(head & ~np.roll(head, 1, 0), 'mist'); cv.fill(edge_of(head) & (XS < 200), 'ink')
    cv.fill(head & ~np.roll(head, 2, 0) & (YS < 80), 'leaf'); cv.fill(head & ~np.roll(head, 1, 0) & (YS < 80), 'grass')     # turf on top
    s = Sprite(W, H)
    s.add(p([(228, 72), (231, 26), (243, 26), (246, 72)]), ['silver', 'mist', 'white'])
    for yy in (34, 48, 62): s.add(p([(228 + (72 - yy - 6) * 0.07, yy), (246 - (72 - yy - 6) * 0.07, yy), (246 - (72 - yy) * 0.07, yy + 6), (228 + (72 - yy) * 0.07, yy + 6)]), ['red_dk', 'red', 'coral'], sep=False)
    s.add(r(229, 16, 245, 27), ['ink', 'slate', 'gray']); s.add(r(232, 18, 242, 25), ['amber', 'gold', 'cream'], sep=False); s.add(p([(228, 16), (237, 8), (246, 16)]), ['red_dk', 'red', 'coral'])
    s.add(r(234, 62, 240, 72), ['bark', 'wood_dk'], flat=True)
    spr(cv, s)
    for k in range(5): cv.px(222 - k * 3, 21 - (k % 2), 'cream'); cv.px(252 + k * 3, 21 - (k % 2), 'cream')   # lamp rays
    # surf: foam line + wet sand band, then dry sand with soft ripples (not camo)
    g = YS >= HOR + 2
    shore = HOR + 2 + (noise1(W, 26, 114) * 5).astype(int)
    wet = g & (YS < shore[None, :] + 12)
    n = gnoise(70, 26, 115)
    bands(cv, g, n, ('tan', 'sand', 'parchment'), (0.16 - 0.1 * CALM, 0.82 + 0.1 * CALM))
    ripple = g & ~wet & (np.sin(GV / 9.0 + (vn(GU / 40.0, GV / 30.0, 116) - 0.5) * 5) > 0.93) & (CALM < 0.6) & (YS > HOR + 20)
    cv.fill(ripple, 'tan'); cv.fill(np.roll(ripple, -1, 0) & g & ~ripple & ~wet, 'parchment')
    cv.fill(wet, 'wood_lt'); cv.fill(wet & (YS > shore[None, :] + 8), 'tan')
    cv.fill(g & (YS >= shore[None, :] - 1) & (YS < shore[None, :] + 1), 'white'); cv.fill(g & (YS == shore[None, :] + 1) & (XS % 7 < 4), 'mist')
    cv.fill(g & (YS < shore[None, :] - 1), 'sky_lt')
    for (cx, cy, rx_, ry_) in ((36, 236, 18, 3.5), (232, 214, 14, 3)):                            # tide pools
        pl = soften(e(cx, cy, rx_, ry_) | e(cx + rx_ * 0.5, cy + 1.5, rx_ * 0.6, ry_ * 0.7)); cv.fill(ndi.binary_dilation(pl, iterations=2), 'tan')
        cv.fill(pl, 'sky'); cv.fill(pl & ~np.roll(pl, 1, 0), 'blue'); cv.a[int(cy), int(cx - rx_ * 0.4):int(cx)] = C['sky_lt']
    for (i, x, y, d) in scatter(60, 117, HOR + 18, H):
        cv.px(x, y, ('mist', 'wood_lt', 'coral', 'gray')[i % 4]); cv.px(x + 1, y, ('white', 'tan', 'red', 'slate')[i % 4])
    s = Sprite(W, H)                                                                              # driftwood, rocks, rope post
    s.add(ln((8, 188), (40, 180), 3.4), ['bark', 'wood_dk', 'wood_lt']); s.add(ln((30, 182), (36, 174), 2), ['bark', 'wood_dk', 'wood_lt'])
    for k, (x, y, rx, ry) in enumerate(((256, 188, 16, 11), (236, 194, 7, 5), (10, 320, 14, 9), (266, 312, 10, 7))): rock_prop(s, x, y, rx, ry, 1300 + k)
    s.add(r(150, 128, 153, 150), ['bark', 'wood_dk', 'wood']); s.add(ln((153, 132), (176, 140), 1.2), ['wood_lt'], flat=True, sep=False)
    spr(cv, s)
    s = Sprite(W, H); s.add(p([(60, SEA + 1), (66, SEA - 12), (67, SEA + 1)]), ['mist', 'white'], sep=False); s.add(r(54, SEA + 1, 72, SEA + 4), ['bark', 'wood_dk'], flat=True); spr(cv, s)
    return cv

def grit_floor(cv, y0, sd, cols=('slate', 'gray', 'silver')):
    fl = YS >= y0; n = gnoise(80, 30, sd); dep = (YS - HOR) / (H - HOR)
    v = (1 - dep) * 0.55 + n * 0.45
    cv.fill(fl, cols[1]); cv.fill(fl & (v > 0.74), cols[2]); cv.fill(fl & (v < 0.28) & (CALM < 0.5), cols[0])
    return fl, n
def stall_tent(s, x0, x1, ytop, yb, stripe, base=('silver', 'mist', 'white'), goods=None):
    """peaked market tent: striped canvas roof, front valance, dark opening, trestle counter"""
    cx = (x0 + x1) / 2
    roof = p([(x0 - 4, ytop + 18), (cx, ytop), (x1 + 4, ytop + 18)]); s.add(roof, list(base))
    for k, x in enumerate(np.arange(x0 - 4, x1 + 4, 6)):
        if k % 2: s.add(p([(cx, ytop), (x, ytop + 18), (x + 6, ytop + 18)]) & roof, list(stripe), sep=False)
    s.add(r(int(x0), ytop + 18, int(x1), yb), ['ink', 'slate'], flat=True)                           # shaded inside
    s.add(r(int(x0) - 4, ytop + 18, int(x1) + 4, ytop + 23), list(stripe))                            # valance
    for x in range(int(x0) - 4, int(x1) + 4, 6): s.add(p([(x, ytop + 23), (x + 6, ytop + 23), (x + 3, ytop + 26)]), list(stripe), sep=False)
    for x in (int(x0), int(x1) - 2): s.add(r(x, ytop + 18, x + 2, yb), ['bark', 'wood_dk'], flat=True)
    s.add(r(int(x0) + 2, yb - 9, int(x1) - 2, yb - 6), ['wood_dk', 'wood', 'wood_lt']); s.add(r(int(x0) + 4, yb - 6, int(x0) + 6, yb) | r(int(x1) - 6, yb - 6, int(x1) - 4, yb), ['bark', 'wood_dk'], flat=True)
    if goods: goods(s, int(x0) + 3, yb - 10, int(x1) - 3)

# ================================================================ Ashgate (town: lean-to under a cliff at the cave mouth; NEW)
def ashgate():
    cv = Canvas(); cv.sky([('slate', 12), ('gray', 16), ('silver', 14)])
    top = (8 + noise1(W, 24, 121) * 22 + (noise1(W, 6, 122) - 0.5) * 6).astype(int)
    cliff = (YS >= top[None, :]) & (YS < HOR + 4)
    lab, gap = cells(XS.astype(float), YS.astype(float), 80, 123, (-10, 0, W + 10, HOR + 10), aniso=(0.75, 1.35))
    rock_facets(cv, cliff, lab, ['slate', 'gray', 'silver', 'mist'], 'ink', 123, bulge=0.55, gap=gap, crack_w=1.15)
    cv.fill(cliff & (gap < 0.55) & (YS > 40), 'outline')
    cv.fill(cliff & ~np.roll(cliff, 1, 0), 'mist'); cv.fill(cliff & ~np.roll(cliff, 2, 0) & np.roll(cliff, 1, 0), 'silver')
    for i in range(10):                                                                           # soot streaks above the fire
        x = 166 + int(_h(i, 1, 124) * 30); cv.fill(cliff & (np.abs(XS - x - (YS - 60) * 0.05) < 1.2) & (YS > 40) & (YS < 120) & (vn(XS / 2.0, YS / 6.0, 125) > 0.4), 'slate')
    # cave mouth (left of centre) with mine rails running in
    mp_ = [(28, HOR + 4), (32, 112), (40, 96), (54, 84), (72, 78), (90, 82), (104, 94), (112, 110), (116, HOR + 4)]
    mouth = soften(p(mp_)); ring = ndi.binary_dilation(mouth, iterations=3) & ~mouth & cliff
    cv.fill(ring, 'slate'); cv.fill(mouth, 'outline'); cv.fill(mouth & (YS > 124) & (vn(XS / 8.0, YS / 3.0, 126) > 0.5 - (YS - 124) / 30.0), 'ink')
    s = Sprite(W, H)
    s.add(r(36, 80, 40, HOR + 4) | r(104, 80, 108, HOR + 4) | r(34, 76, 110, 82), ['bark', 'wood_dk', 'wood'])     # timber frame of the adit
    for (x, y) in ((70, 108), (76, 108)): s.px([(x, y)], 'gold')
    # the lean-to: poles + plank roof leaning on the cliff, hide flap, counter with goods, lantern
    s.add(ln((132, 142), (140, 70), 3), ['bark', 'wood_dk', 'wood']); s.add(ln((252, 142), (246, 78), 3), ['bark', 'wood_dk', 'wood'])
    roof = p([(124, 92), (262, 96), (266, 104), (120, 100)]); s.add(roof, ['wood_dk', 'wood', 'wood_lt'])
    for x in range(124, 264, 9): s.px([(x, y) for y in range(93, 101) if roof[y, x]], 'wood_dk')
    s.add(p([(150, 64), (240, 70), (262, 96), (124, 92)]), ['wood', 'wood_lt', 'tan'])                 # slanted plank roof back to the rock
    for x in range(150, 250, 10): s.add(ln((x, 66 + (x - 150) * 0.06), (x - 22, 92), 1.0) & p([(150, 64), (240, 70), (262, 96), (124, 92)]), ['wood_dk'], flat=True, sep=False)
    s.add(r(134, 104, 250, HOR + 2), ['ink', 'slate'], flat=True)                                      # shade under the roof
    s.add(p([(214, 100), (250, 102), (246, 126), (226, 120)]), ['wood_lt', 'tan', 'sand'])              # hide flap
    s.add(r(140, 124, 210, 129), ['wood_dk', 'wood', 'wood_lt'])                                       # counter
    for x in (144, 204): s.add(r(x, 129, x + 3, HOR + 2), ['bark', 'wood_dk'], flat=True)
    s.add(r(146, 117, 156, 124), ['ink', 'slate', 'gray']); s.add(r(160, 118, 170, 124), ['wood_dk', 'wood', 'wood_lt'])     # ore bin, crate
    for (x, c) in ((176, 'orange'), (182, 'cyan'), (188, 'violet'), (194, 'silver')): s.add(e(x, 121.5, 2.4, 2.4), [c if c != 'silver' else 'gray', c], sep=False)   # glinting ore
    s.add(r(156, 104, 159, 112), ['bark'], flat=True); s.add(r(153, 110, 162, 117), ['ink', 'slate', 'gray']); s.add(r(155, 112, 160, 116), ['amber', 'gold', 'cream'], sep=False)   # hanging lamp
    s.add(ln((222, 130), (232, 108), 1.6), ['bark', 'wood_dk']); s.add(p([(226, 106), (240, 110), (238, 112), (228, 109)]), ['slate', 'gray', 'silver'])   # pick against the post
    spr(cv, s)
    fl, n = grit_floor(cv, HOR + 4, 127, cols=('slate', 'gray', 'silver'))
    foot = (noise1(W, 9, 128) * 4).astype(int); cv.fill(fl & (YS < HOR + 6 + foot[None, :]), 'slate'); cv.fill(fl & (YS < HOR + 5), 'ink')
    for k, x0 in enumerate((56, 82)):                                                             # rails out of the adit
        t = np.clip((YS - HOR) / 80.0, 0, 1); rx_ = x0 + (x0 - 72) * t * 1.6 - t * 18
        rail = (np.abs(XS - rx_) < 0.8 + t * 0.6) & (YS > HOR + 3) & (YS < HOR + 70); cv.fill(rail, 'silver'); cv.fill(np.roll(rail, 1, 0) & ~rail & (YS < HOR + 71), 'ink')
    for yy in range(HOR + 6, HOR + 68, 6):
        t = (yy - HOR) / 80.0; xa = 56 + (56 - 72) * t * 1.6 - t * 18; xb = 82 + (82 - 72) * t * 1.6 - t * 18
        cv.rect(int(xa) - 1, yy, int(xb) + 2, yy + 1 + int(t * 2), 'wood_dk')
    for (i, x, y, d) in scatter(240, 129, HOR + 10, H):                                          # grit + ash flecks
        cv.px(x, y, 'silver' if i % 4 else 'mist'); cv.px(x, y + 1, 'slate')
    s = Sprite(W, H)                                                                              # campfire, logs, sacks, barrels at the edges
    s.add(e(196, 176, 14, 4), ['ink', 'slate', 'gray'])
    for a in (-0.5, 0.0, 0.5): s.add(ln((196 - np.sin(a) * 12, 176 + 2), (196 + np.sin(a) * 4, 166), 2.4), ['bark', 'wood_dk', 'wood'])
    s.add(p([(188, 174), (192, 160), (196, 166), (200, 154), (204, 174)]), ['orange', 'amber', 'gold'], sep=False); s.add(p([(193, 174), (196, 164), (199, 174)]), ['gold', 'cream'], sep=False, flat=True)
    for k, (x, y) in enumerate(((12, 186), (22, 190), (250, 188))): barrel(s, x, y, 9, 11, ramp=('bark', 'wood_dk', 'wood', 'wood_lt'))
    s.add(e(236, 190, 7, 5), ['wood', 'wood_lt', 'tan', 'sand']); s.add(e(246, 192, 6, 4), ['wood', 'wood_lt', 'tan', 'sand']); s.px([(236, 186), (246, 189)], 'wood')   # ore sacks
    for k, (x, y, rx, ry) in enumerate(((6, 320, 14, 9), (266, 326, 14, 10), (40, 178, 6, 4))): rock_prop(s, x, y, rx, ry, 1400 + k)
    spr(cv, s)
    steam(cv, 194, 140, 3, 131, cols=('silver', 'gray'))
    for (x, y) in ((190, 150), (202, 146), (198, 138)): cv.px(x, y, 'gold')
    return cv

# ================================================================ Pebblegate (town: tent stalls before the keep; NEW)
def pebblegate():
    cv = Canvas(); cv.sky([('blue', 26), ('sky', 44), ('sky_lt', 40)])
    for i, (x, y, w) in enumerate(((40, 40, 44), (190, 30, 56))): cv.cloud(x, y, w, i + 141)
    s = Sprite(W, H); WALL = ('ink', 'slate', 'gray', 'silver')
    s.add(r(0, 58, W, HOR - 10), list(WALL), bulge=0.3)                                            # the keep's outer wall
    for x in range(0, W, 10): s.add(r(x, 52, x + 6, 59), list(WALL))
    for (x0, x1) in ((96, 174),):                                                                   # gatehouse
        s.add(r(x0, 30, x1, HOR - 10), list(WALL), bulge=0.4)
        for x in range(x0, x1, 8): s.add(r(x, 24, x + 5, 31), list(WALL))
        s.add(r(120, 72, 150, HOR - 10) | e(135, 72, 15, 10), ['outline'], flat=True)
        s.add(r(122, 76, 148, HOR - 10) & ((XS - 122) % 4 < 1) | r(122, 76, 148, HOR - 10) & ((YS - 76) % 5 < 1), ['slate', 'gray'], flat=True, sep=False)
    for (x, c) in ((40, ('blue_dk', 'blue', 'sky')), (230, ('blue_dk', 'blue', 'sky'))):
        s.add(r(x - 5, 66, x + 5, 94) | p([(x - 5, 94), (x, 100), (x + 5, 94)]), list(c)); s.add(e(x, 78, 2.4, 2.4), ['slate', 'silver'], sep=False)
    spr(cv, s)
    for yy in range(62, HOR - 10, 6):                                                             # mortar
        m = (YS == yy) & (cv.a == C['gray']).all(-1); cv.fill(m, 'slate')
    cv.fill((YS >= HOR - 10) & (YS < HOR - 6), 'slate')
    # tent stalls in front of the wall
    s = Sprite(W, H); yb = HOR + 4
    def pebbles(s, x0, y, x1):
        for k, x in enumerate(range(x0 + 2, x1 - 2, 5)): s.add(e(x, y - 1, 2.2, 1.8), [('slate', 'gray', 'silver'), ('wood_dk', 'wood', 'tan'), ('gray', 'silver', 'mist')][k % 3], sep=False)
    def shields(s, x0, y, x1):
        for k, x in enumerate(range(x0 + 4, x1 - 2, 10)): s.add(e(x, y - 3, 3.6, 4), ['wood_dk', 'wood', 'wood_lt']); s.add(e(x, y - 3, 1.4, 1.4), ['slate', 'silver'], sep=False)
    def robes(s, x0, y, x1):
        for k, x in enumerate(range(x0 + 3, x1 - 4, 9)): s.add(p([(x, y - 9), (x + 6, y - 9), (x + 7, y), (x - 1, y)]), [('navy', 'blue_dk', 'blue'), ('pine', 'leaf_dk', 'leaf'), ('plum_dk', 'plum', 'violet')][k % 3])
    stall_tent(s, 6, 70, 92, yb, ('red_dk', 'red', 'coral'), goods=pebbles)
    stall_tent(s, 100, 170, 98, yb, ('blue_dk', 'blue', 'sky'), goods=shields)
    stall_tent(s, 200, 264, 90, yb, ('pine', 'leaf_dk', 'leaf'), goods=robes)
    spr(cv, s)
    for (xa, xb, y0, sag) in ((70, 100, 104, 5), (170, 200, 104, 5)):                                # pennant strings between the tents
        for x in range(xa, xb):
            t = (x - xa) / (xb - xa); y = int(y0 + sag * 4 * t * (1 - t)); cv.px(x, y, 'bark')
            if (x - xa) % 5 == 2: cv.px(x, y + 1, ('red', 'gold', 'sky')[(x // 5) % 3]); cv.px(x, y + 2, ('red', 'gold', 'sky')[(x // 5) % 3]); cv.px(x + 1, y + 1, ('red', 'gold', 'sky')[(x // 5) % 3])
    # ground: trampled earth with a flagstone path to the gate
    g = YS >= HOR + 4; n = gnoise(70, 26, 142)
    bands(cv, g, n, ('wood_lt', 'tan', 'sand'), (0.18 - 0.1 * CALM, 0.8 + 0.1 * CALM))
    cv.fill(g & (YS < HOR + 7), 'wood')
    t = np.clip((YS - HOR) / (H - HOR), 0, 1); road = (np.abs(XS - 135) < 8 + t * 34) & g
    cobbles(cv, road, ('wood_lt', 'tan', 'sand', 'wood_lt'), 143, HOR + 5, H)
    cv.fill(road & ~ndi.binary_erosion(road), 'wood')
    for (i, x, y, d) in scatter(80, 144, 172, 320, skip=lambda x, y: road[y, x]):
        if i % 2: cv.px(x, y, 'gold'); cv.px(x + 1, y - (i % 4 == 1), 'amber')
        else: cv.px(x, y, 'gray'); cv.px(x, y + 1, 'slate')
    s = Sprite(W, H)
    crate(s, 8, 176, 12, 10); crate(s, 18, 184, 11, 9); barrel(s, 252, 190, 9, 12); barrel(s, 240, 194, 8, 10)
    s.add(e(36, 192, 8, 4), ['wood', 'wood_lt', 'tan', 'sand']); s.add(e(36, 190, 5, 2), ['wood_lt', 'tan'], sep=False)   # hay bundle
    for k, (x, y, rx, ry) in enumerate(((6, 322, 12, 8), (266, 316, 12, 8))): rock_prop(s, x, y, rx, ry, 1500 + k)
    spr(cv, s)
    return cv
