"""DRAFT location backdrops 270x480 (same framing as combat/bg_forest_portrait.png)."""
import numpy as np
from regionlib import Canvas, Sprite, E, P, R, LN, ground, patches, vnoise, noise1, _h, grid
from pal import C
W, H = 270, 480
HOR = 141                       # horizon / ground start, same as the forest (meadow_start_y 141)
def e(*a, **k): return E(W, H, *a, **k)
def p(pts): return P(W, H, pts)
def r(*a): return R(W, H, *a)
def ln(*a): return LN(W, H, *a)
YS, XS = np.mgrid[0:H, 0:W]
def put_ground(cv, g, y0):
    m = YS >= y0; cv.a[m] = g[m]
def spr(cv, s): cv.paint_sprite(s.image(trim=False), 0, 0)

def std_sky(cv, cols=(('blue', 34), ('sky', 58), ('sky_lt', 60)), clouds=((40, 52, 44), (178, 40, 56), (238, 76, 30), (110, 88, 26))):
    cv.sky(list(cols))
    for i, (x, y, w) in enumerate(clouds): cv.cloud(x, y, w, i + 3)

# ---------------------------------------------------------------- Millpond (meadow)
def millpond():
    cv = Canvas(); std_sky(cv)
    cv.ridge(HOR - 6, 26, 60, 11, ('pine_dk', 'pine'), rough=0.5)                  # far wood line
    m, top = cv.ridge(HOR + 2, 16, 90, 12, ('leaf_dk', 'leaf'))                     # near hills
    g = ground(W, H, HOR, ('leaf', 'grass', 'lime'), 21, tufts=('leaf', 'grass'), n_tufts=240)
    put_ground(cv, g, HOR)
    patches(cv, 250, 500, 3, ('tan', 'wood_lt'), density=0.35)
    # windmill on the left hill
    s = Sprite(W, H); bx = 44; by = int(top[bx]) + 4
    s.add(p([(bx - 11, by), (bx - 7, by - 44), (bx + 7, by - 44), (bx + 11, by)]), ['tan', 'sand', 'parchment'])
    s.add(p([(bx - 10, by - 44), (bx, by - 55), (bx + 10, by - 44)]), ['red_dk', 'red', 'coral'])
    s.add(r(bx - 3, by - 12, bx + 3, by), ['bark', 'wood_dk'], flat=True)
    s.add(r(bx - 2, by - 33, bx + 2, by - 28), ['navy', 'blue_dk'], flat=True)
    hub = (bx, by - 40)
    for a in (0.35, 0.35 + np.pi / 2, 0.35 + np.pi, 0.35 + 1.5 * np.pi):
        tip = (hub[0] + np.cos(a) * 27, hub[1] + np.sin(a) * 27)
        s.add(ln(hub, tip, 2), ['bark', 'wood_dk'], sep=False)
        nx, ny = -np.sin(a), np.cos(a); b0 = (hub[0] + np.cos(a) * 8, hub[1] + np.sin(a) * 8)
        s.add(p([b0, tip, (tip[0] + nx * 6, tip[1] + ny * 6), (b0[0] + nx * 5, b0[1] + ny * 5)]), ['wood_lt', 'tan', 'parchment'], sep=False)
    s.add(e(hub[0], hub[1], 2, 2), ['bark', 'wood'])
    spr(cv, s)
    # the pond, back-right, behind the monster stand zone
    pond = e(186, 160, 78, 15) | e(236, 154, 50, 12)
    cv.fill(pond, 'blue'); cv.fill(pond & ~np.roll(pond, 2, 0), 'blue_dk')
    cv.fill(pond & ~np.roll(pond, -2, 0), 'wood_dk')
    for i in range(22):
        x, y = int(120 + _h(i, 1, 5) * 150), int(150 + _h(i, 2, 5) * 20)
        if pond[y, x] and pond[y, min(W - 1, x + 8)]:
            cv.a[y, x:x + 3 + int(_h(i, 3, 5) * 6)] = C['sky']
    for i in range(7):                                                                   # lily pads
        x, y = int(130 + _h(i, 4, 6) * 130), int(152 + _h(i, 5, 6) * 16)
        lp = e(x, y, 4, 1.6)
        if (lp & pond).sum() == lp.sum(): cv.fill(lp, 'leaf'); cv.px(x - 1, y, 'grass'); cv.px(x + 2, y, 'leaf_dk')
    cv.px(172, 158, 'cream'); cv.px(173, 158, 'gold'); cv.px(171, 158, 'cream')
    for i in range(60):                                                                  # reeds around the back edge
        x = int(108 + _h(i, 7, 8) * 162); edge = np.nonzero(pond[:, min(W - 1, x)])[0]
        if not len(edge): continue
        y0 = edge.min() + (1 if _h(i, 9, 8) < 0.5 else int(edge.max() - edge.min()) - 1)
        hgt = 6 + int(_h(i, 8, 8) * 9)
        for k in range(hgt): cv.px(x + (k > hgt * 0.6 and i % 2), y0 - k, 'leaf_dk' if k < hgt - 3 else 'pine')
        if i % 3 == 0:
            for k in range(3): cv.px(x, y0 - hgt + k, 'wood_dk'); cv.px(x + 1, y0 - hgt + k, 'bark')
    return cv

# ---------------------------------------------------------------- Briar Cross (meadow)
def briar_cross():
    cv = Canvas(); std_sky(cv, clouds=((58, 48, 40), (200, 60, 50), (130, 84, 22)))
    cv.ridge(HOR - 4, 20, 70, 31, ('leaf_dk', 'leaf'))
    g = ground(W, H, HOR, ('leaf', 'grass', 'lime'), 33, tufts=('leaf', 'grass'), n_tufts=220)
    put_ground(cv, g, HOR)
    # roads: one runs to the horizon, one crosses under the monsters
    wob = (noise1(H, 14, 5) - 0.5) * 6
    t = np.clip((YS - HOR) / (H - HOR), 0, 1)
    half = 6 + t * 70; cx = 135 + wob[YS] + t * 8
    road = (np.abs(XS - cx) < half) & (YS >= HOR)
    xw = (noise1(W, 18, 7) - 0.5) * 6
    road |= (np.abs(YS - (206 + xw[XS])) < 13 + (XS * 0).astype(float))
    road &= YS >= HOR
    rough = vnoise(W, H, 5, 3, 91) > 0.82
    edge = road & ~(np.roll(road, 1, 0) & np.roll(road, -1, 0) & np.roll(road, 1, 1) & np.roll(road, -1, 1))
    cv.fill(road, 'sand'); cv.fill(road & rough, 'tan'); cv.fill(edge, 'tan')
    for dx in (-0.45, 0.45):                                                             # wheel ruts on the long road
        rut = (np.abs(XS - (cx + dx * half)) < 0.7 + t * 1.2) & road & (YS > HOR + 6) & ((YS < 190) | (YS > 222))
        cv.fill(rut, 'wood_lt')
    for x in range(0, W, 1):
        for yy in (199 + int(xw[x]), 213 + int(xw[x])):
            if (x // 5) % 3: cv.px(x, yy, 'wood_lt')
    # thorn hedges along the horizon, gap for the road
    hed = np.zeros((H, W), bool)
    for x0, x1 in ((-10, 118), (152, 280)):
        hh = (noise1(W, 7, 41) * 14 + 14).astype(int)
        for x in range(max(0, x0), min(W, x1)):
            taper = min(1.0, (x - x0) / 8, (x1 - x) / 8)
            hed[HOR + 6 - int(hh[x] * taper):HOR + 7, x] = True
    cv.fill(hed, 'pine'); cv.fill(hed & (vnoise(W, H, 4, 3, 5) > 0.6), 'leaf_dk'); cv.fill(hed & ~np.roll(hed, 1, 0), 'leaf')
    cv.fill(hed & ~np.roll(hed, -1, 0), 'pine_dk')
    for i in range(70):
        x, y = int(_h(i, 1, 44) * W), int(HOR - 4 + _h(i, 2, 44) * 10)
        if hed[y, x]:
            cv.px(x, y, 'bark' if i % 3 else 'red'); cv.px(x + 1, y - 1, 'wood_dk' if i % 3 else 'coral')
    # the tavern far down the road (right)
    s = Sprite(W, H); tx, ty = 214, HOR - 6
    s.add(r(tx - 14, ty - 14, tx + 14, ty), ['tan', 'sand', 'parchment'])
    s.add(p([(tx - 17, ty - 13), (tx, ty - 26), (tx + 17, ty - 13)]), ['red_dk', 'red', 'coral'])
    s.add(r(tx + 6, ty - 30, tx + 10, ty - 20), ['slate', 'gray'])
    s.add(r(tx - 3, ty - 8, tx + 3, ty), ['bark', 'wood_dk'], flat=True)
    s.add(r(tx - 11, ty - 11, tx - 6, ty - 7) | r(tx + 6, ty - 11, tx + 11, ty - 7), ['amber', 'gold'], flat=True)
    spr(cv, s)
    for k in range(4): cv.cloud(tx + 9 + k * 4, ty - 34 - k * 5, 8 + k * 2, 60 + k, cols=('mist', 'silver'))
    # signpost at the crossing (left, clear of the monster lanes)
    s = Sprite(W, H); sx, sy = 18, 190
    s.add(r(sx - 2, sy - 44, sx + 2, sy), ['bark', 'wood_dk', 'wood'])
    s.add(p([(sx - 3, sy - 42), (sx + 18, sy - 42), (sx + 22, sy - 38), (sx + 18, sy - 34), (sx - 3, sy - 34)]), ['wood_dk', 'wood', 'wood_lt'])
    s.add(p([(sx + 3, sy - 31), (sx - 12, sy - 31), (sx - 15, sy - 27), (sx - 12, sy - 23), (sx + 3, sy - 23)]), ['wood_dk', 'wood', 'wood_lt'])
    s.add(p([(sx - 3, sy - 20), (sx + 15, sy - 20), (sx + 18, sy - 16), (sx + 15, sy - 12), (sx - 3, sy - 12)]), ['wood_dk', 'wood', 'wood_lt'])
    s.add(e(sx, sy, 7, 2), ['leaf_dk', 'leaf'], sep=False)
    spr(cv, s)
    return cv

# ---------------------------------------------------------------- Lantern Reach (coast)
def lantern_reach():
    cv = Canvas(); std_sky(cv, cols=(('sky', 40), ('sky_lt', 50), ('ice', 30)), clouds=((50, 54, 40), (150, 44, 46), (110, 92, 24)))
    SEA = 116
    cv.rect(0, SEA, W, SEA + 6, 'blue_dk'); cv.rect(0, SEA + 6, W, SEA + 20, 'blue'); cv.rect(0, SEA + 20, W, 200, 'sky')
    for i in range(46):
        x, y = int(_h(i, 1, 12) * W), int(SEA + 3 + _h(i, 2, 12) * 36)
        ln_ = 3 + int(_h(i, 3, 12) * 8 + (y - SEA) / 5)
        cv.a[y, max(0, x):min(W, x + ln_)] = C['sky_lt' if y > SEA + 20 else 'sky']
    # rocky point + lighthouse (right)
    s = Sprite(W, H)
    s.add(p([(176, 162), (196, 128), (214, 112), (240, 104), (270, 100), (270, 166)]), ['ink', 'slate', 'gray', 'silver'])
    for (x, y, rx, ry) in ((200, 150, 14, 10), (244, 142, 22, 16), (222, 128, 12, 9)):
        s.add(e(x, y, rx, ry), ['slate', 'gray', 'silver'], line='ink')
    lx = 236
    s.add(p([(lx - 13, 110), (lx - 9, 50), (lx + 9, 50), (lx + 13, 110)]), ['silver', 'mist', 'white'])
    for (y0, y1) in ((64, 74), (86, 96)):
        s.add(p([(lx - 13 + (110 - y1) * 4 / 60, y1), (lx - 13 + (110 - y0) * 4 / 60, y0), (lx + 13 - (110 - y0) * 4 / 60, y0), (lx + 13 - (110 - y1) * 4 / 60, y1)]), ['red_dk', 'red', 'coral'])
    s.add(r(lx - 12, 46, lx + 12, 50), ['ink', 'slate', 'gray'])
    s.add(r(lx - 7, 36, lx + 7, 46), ['amber', 'gold', 'cream'])
    s.add(r(lx - 1, 36, lx + 1, 46), ['ink'], flat=True, sep=False)
    s.add(p([(lx - 10, 36), (lx, 27), (lx + 10, 36)]), ['red_dk', 'red', 'coral'])
    s.add(r(lx - 3, 98, lx + 3, 110), ['wood_dk', 'wood'], flat=True)
    spr(cv, s)
    for k, (dx, dy) in enumerate(((-16, 41), (-20, 41), (-24, 42), (16, 41), (20, 41), (24, 42), (-28, 42), (28, 42))):   # lamp rays
        cv.px(lx + dx, dy, 'cream' if k % 3 else 'gold')
    # beach
    shore = (158 + (noise1(W, 20, 3) - 0.5) * 10).astype(int)
    g = ground(W, H, 150, ('tan', 'sand', 'parchment'), 55, cw=12, ch=3, q=(0.1, 0.55), speck=(('wood_lt', 0.004), ('white', 0.002)))
    beach = YS >= shore[None, :]
    cv.a[beach] = g[beach]
    wet = beach & (YS < shore[None, :] + 8); cv.fill(wet, 'tan')
    foam = beach & ~np.roll(beach, 1, 0); cv.fill(foam, 'white'); cv.fill(np.roll(foam, 1, 0) & ((XS // 3) % 2 == 0), 'ice')
    cv.fill(np.roll(foam, -3, 0) & ~beach & ((XS // 4) % 3 != 0), 'white')
    patches(cv, 190, 290, 8, ('sky', 'sky_lt'), density=0.2, size=(9, 3), step=(90, 34), edge_col='tan')     # tide pools
    patches(cv, 300, 500, 9, ('parchment', 'sand'), density=0.3, size=(12, 4))
    for i in range(40):                                                                  # shells & pebbles
        x, y = int(_h(i, 1, 70) * W), int(180 + _h(i, 2, 70) * 150)
        cv.px(x, y, ('mist', 'wood_lt', 'coral', 'gray')[i % 4]); cv.px(x + 1, y, ('white', 'tan', 'red', 'slate')[i % 4])
    return cv

# ---------------------------------------------------------------- Howling Cleft (cave)
def howling_cleft():
    cv = Canvas(); cv.sky([('slate', 30), ('gray', 30), ('silver', 20)])
    top = np.full(W, 200)
    x = -4; k = 0
    while x < W:
        w = 10 + int(_h(k, 1, 17) * 18); yt = 40 + int(_h(k, 2, 17) * 40)
        tone = ('gray', 'slate', 'gray', 'silver', 'slate')[k % 5]
        col = (XS >= x) & (XS < x + w) & (YS >= yt) & (YS < HOR + 10)
        cap = p([(x, yt), (x + w * 0.4, yt - 3 - int(_h(k, 3, 17) * 6)), (x + w, yt + 2), (x + w, yt + 6), (x, yt + 6)])
        col |= cap & (YS < HOR + 10)
        cv.fill(col, tone)
        cv.fill(col & (XS < x + 2), 'silver' if tone != 'silver' else 'mist')
        cv.fill(col & (XS >= x + w - 2), 'slate' if tone != 'slate' else 'ink')
        cv.fill(col & (XS == x + w - 1), 'ink')
        cv.fill(cap & ~np.roll(cap, 1, 0), 'mist')
        for b in range(2):                                                               # horizontal fractures
            yb = yt + 14 + int(_h(k, 4 + b, 17) * 50)
            cv.fill(col & (YS == yb) & (XS > x + 1) & (XS < x + w - 2), 'slate'); cv.fill(col & (YS == yb + 1) & (XS > x + 1) & (XS < x + w - 2), 'silver')
        top[max(0, x):max(0, min(W, x + w))] = yt
        x += w; k += 1
    # the cleft mouth
    mouth = p([(64, HOR + 8), (74, 110), (92, 84), (118, 68), (140, 64), (164, 72), (186, 92), (200, 118), (208, HOR + 8)])
    cv.fill(mouth, 'outline'); cv.fill(mouth & ~np.roll(mouth, 3, 1) & (XS < 140), 'ink'); cv.fill(mouth & ~np.roll(mouth, 2, 0), 'ink')
    rim = np.zeros_like(mouth)
    for d in ((1, 0), (-1, 0), (0, 1), (0, -1)): rim |= np.roll(mouth, d, (0, 1))
    cv.fill(rim & ~mouth & (YS < HOR), 'slate')
    s = Sprite(W, H)
    for i, x in enumerate(range(84, 200, 13)):                                           # stalactite teeth
        yt = int(np.nonzero(mouth[:, x])[0].min()) if mouth[:, x].any() else 70
        Lt = 9 + int(_h(i, 1, 13) * 12)
        s.add(p([(x - 4, yt - 2), (x + 4, yt - 2), (x + 0.5, yt + Lt)]), ['slate', 'gray', 'silver'], line='ink')
    for i, x in enumerate((80, 106, 170, 194)):                                         # stalagmites
        s.add(p([(x - 5, HOR + 9), (x + 5, HOR + 9), (x + 0.5, HOR - 6 - int(_h(i, 2, 13) * 8))]), ['slate', 'gray', 'silver'], line='ink')
    spr(cv, s)
    for (x, y) in ((128, 112), (132, 112), (150, 104), (153, 104)): cv.px(x, y, 'gold')  # something answers
    g = ground(W, H, HOR, ('slate', 'gray', 'silver'), 77, cw=18, ch=5, q=(0.05, 0.74))
    fl = YS >= HOR + 8
    cv.a[fl] = g[fl]
    edge = (YS == HOR + 8); cv.fill(edge, 'ink')
    for i in range(14):                                                                  # floor cracks
        x, y = int(_h(i, 1, 23) * W), int(170 + _h(i, 2, 23) * 170); L_ = 10 + int(_h(i, 3, 23) * 18)
        for k_ in range(L_): cv.px(x + k_, y + int((noise1(40, 5, i + 3)[k_] - 0.5) * 6), 'slate')
    patches(cv, 200, 500, 17, ('slate', 'gray'), density=0.22, size=(12, 3), edge_col='slate')                 # scree
    patches(cv, 180, 300, 18, ('blue_dk', 'navy'), density=0.12, size=(8, 2), step=(96, 40), edge_col='slate') # puddles
    s = Sprite(W, H)                                                                     # boulders at the sides
    for (x, y, rx, ry) in ((10, 168, 16, 12), (30, 176, 9, 7), (258, 170, 18, 14), (238, 180, 8, 6), (4, 312, 12, 8), (268, 318, 14, 9)):
        s.add(e(x, y, rx, ry), ['ink', 'slate', 'gray', 'silver'])
    spr(cv, s)
    return cv

# ---------------------------------------------------------------- Gravel Keep (keep)
def gravel_keep():
    cv = Canvas()
    cv.sky([('plum_dk', 38), ('plum', 32), ('violet', 22), ('coral', 16), ('orange', 14), ('amber', 30)])
    cv.fill(e(196, 128, 16, 16) & (YS < 128), 'gold'); cv.fill(e(196, 128, 12, 12) & (YS < 128), 'cream')
    for (x, y, w) in ((56, 58, 46), (214, 44, 38), (140, 88, 30)):
        cv.cloud(x, y, w, x, cols=('violet', 'plum'))
    cv.ridge(HOR - 2, 12, 60, 3, ('plum_dk', 'plum'))
    s = Sprite(W, H); K = ['outline', 'ink', 'slate', 'gray']
    s.add(r(0, 112, 96, HOR + 2) | r(174, 112, 270, HOR + 2), K)                         # curtain walls
    for x in list(range(2, 96, 10)) + list(range(176, 270, 10)): s.add(r(x, 106, x + 6, 112), K)
    s.add(r(92, 70, 178, HOR + 2), K)                                                    # squat keep
    for x in range(92, 178, 12): s.add(r(x, 62, x + 8, 70), K)
    s.add(r(84, 58, 104, HOR + 2) | r(166, 58, 186, HOR + 2), K)                         # corner towers
    for x in (84, 92, 100, 166, 174, 182): s.add(r(x, 52, x + 4, 58), K)
    s.add(p([(122, HOR + 2), (122, 118), (135, 108), (148, 118), (148, HOR + 2)]), ['outline'], flat=True)   # gate
    s.add(r(134, 34, 136, 62), ['bark', 'wood_dk'], flat=True)                          # the empty flagpole
    for (x, y) in ((110, 86), (158, 86), (93, 76), (176, 76), (40, 122), (226, 122)):
        s.add(r(x, y, x + 4, y + 7), ['amber', 'gold'], flat=True, sep=False)
    spr(cv, s)
    g = ground(W, H, HOR, ('ink', 'slate', 'gray'), 91, cw=14, ch=4, q=(0.07, 0.72), speck=(('gray', 0.004), ('ink', 0.004)))
    cv.a[YS > HOR + 2] = g[YS > HOR + 2]
    cv.fill((YS == HOR + 3), 'ink')
    # flagstone path from the gate
    t = np.clip((YS - HOR) / (H - HOR), 0, 1); half = 12 + t * 60; path = (np.abs(XS - 135) < half) & (YS > HOR + 3)
    v = np.sqrt(np.clip(YS - HOR - 3, 0, None)) * 3.0                                  # perspective rows (taller toward the bottom)
    row = np.floor(v / 4).astype(int); u = (XS - 135) / np.maximum(half, 1) * 4 + (row % 2) * 0.5
    joint = path & ((np.abs(np.diff(np.pad(row, ((1, 0), (0, 0)), mode='edge'), axis=0)) > 0) | (np.abs(u - np.round(u)) < 0.07))
    cv.fill(path, 'slate'); cv.fill(path & (vnoise(W, H, 9, 4, 5) > 0.72), 'gray'); cv.fill(joint, 'ink')
    cv.fill(path & ~np.roll(path, 1, 1) | path & ~np.roll(path, -1, 1), 'ink')
    patches(cv, 190, 500, 23, ('gray', 'slate'), density=0.15, size=(8, 3), edge_col='slate')
    s = Sprite(W, H)                                                                     # rubble
    for (x, y, rx, ry) in ((16, 170, 10, 7), (32, 178, 6, 4), (252, 166, 12, 8), (236, 176, 5, 4), (8, 300, 9, 6), (262, 306, 10, 6)):
        s.add(e(x, y, rx, ry), ['ink', 'slate', 'gray', 'silver'])
    spr(cv, s)
    return cv

# ---------------------------------------------------------------- Candlewick (town)
def candlewick():
    cv = Canvas(); std_sky(cv, cols=(('sky', 36), ('sky_lt', 56), ('cream', 40)), clouds=((40, 50, 40), (200, 44, 50)))
    s = Sprite(W, H)
    houses = [(-6, 44, 96, 'red'), (38, 40, 88, 'thatch'), (80, 52, 80, 'red'), (132, 46, 90, 'thatch'), (178, 44, 84, 'red'), (222, 54, 94, 'thatch')]
    ROOF = {'red': ['red_dk', 'red', 'coral'], 'thatch': ['wood', 'wood_lt', 'tan']}
    for i, (x, w, ytop, rf) in enumerate(houses):
        yb = HOR + 2
        s.add(r(x, ytop + 16, x + w, yb), ['tan', 'sand', 'parchment'])
        s.add(p([(x - 4, ytop + 18), (x + w / 2, ytop - 8), (x + w + 4, ytop + 18)]), ROOF[rf])
        s.add(r(x + w - 12, ytop - 8, x + w - 6, ytop + 6), ['wood_dk', 'wood', 'wood_lt'] if i % 2 else ['slate', 'gray', 'silver'])
        for bx in (x, x + w // 2, x + w - 2):
            s.add(r(bx, ytop + 16, bx + 2, yb), ['bark', 'wood_dk'], flat=True, sep=False)
        s.add(r(x, ytop + 30, x + w, ytop + 32), ['bark', 'wood_dk'], flat=True, sep=False)
        s.add(r(x + 6, ytop + 20, x + 13, ytop + 27) | r(x + w - 16, ytop + 36, x + w - 9, ytop + 43), ['amber', 'gold'], flat=True)
        if i == 3:                                                                       # the inn: door + kettle sign
            s.add(r(x + 18, ytop + 38, x + 28, yb), ['bark', 'wood_dk'], flat=True)
            s.add(r(x + 34, ytop + 34, x + 36, ytop + 40), ['bark'], flat=True, sep=False)
            s.add(e(x + 35, ytop + 44, 5, 4), ['ink', 'slate', 'gray'])
            s.add(ln((x + 40, ytop + 43), (x + 43, ytop + 40), 1.6), ['slate', 'gray'], sep=False)
    spr(cv, s)
    for i, (x, w, ytop, rf) in enumerate(houses):
        if i % 2: continue
        for k in range(3): cv.cloud(x + w - 9 + k * 3, ytop - 12 - k * 7, 6 + k * 3, 30 + i * 5 + k, cols=('mist', 'silver'))
    g = ground(W, H, HOR, ('wood_lt', 'tan', 'sand'), 101, cw=12, ch=3, q=(0.1, 0.5), speck=(('wood', 0.004),))
    gm_ = (YS > HOR + 2) | ((cv.a.astype(int).sum(-1) == 0) & (YS >= HOR - 2)); cv.a[gm_] = g[gm_]
    cv.fill(YS == HOR + 3, 'wood')
    patches(cv, 190, 500, 31, ('wood_lt', 'wood'), density=0.3, size=(12, 4))
    s = Sprite(W, H)                                                                     # well + lamp post at the edges
    s.add(e(20, 184, 14, 5) | r(6, 170, 35, 184), ['slate', 'gray', 'silver'])
    s.add(e(20, 170, 12, 3), ['outline'], flat=True, sep=False)
    s.add(r(8, 146, 10, 172) | r(30, 146, 32, 172), ['bark', 'wood_dk'], flat=True)
    s.add(p([(4, 148), (20, 138), (36, 148)]), ['red_dk', 'red', 'coral'])
    s.add(r(255, 128, 258, 186), ['ink', 'slate'], flat=True)
    s.add(r(251, 120, 262, 130), ['ink', 'slate', 'gray'])
    s.add(r(253, 122, 260, 128), ['amber', 'gold', 'cream'], sep=False)
    spr(cv, s)
    return cv

LOCS = {   # id: (fn, name, kind/region)
    'candlewick': (candlewick, 'Candlewick', 'town'), 'millpond': (millpond, 'Millpond', 'meadow'),
    'briar_cross': (briar_cross, 'Briar Cross', 'meadow'), 'lantern_reach': (lantern_reach, 'Lantern Reach', 'coast'),
    'howling_cleft': (howling_cleft, 'Howling Cleft', 'cave'), 'gravel_keep': (gravel_keep, 'Gravel Keep', 'keep'),
}
