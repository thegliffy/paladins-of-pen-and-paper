# ======================= v3: 4 more classes (cleric, rogue, barbarian, druid) =======================
NEW_CLASSES = ['cleric', 'rogue', 'barbarian', 'druid']
def line_f(p0, p1):
    (x0, y0), (x1, y1) = p0, p1; n = max(abs(x1 - x0), abs(y1 - y0)) + 1
    return pts(W, H, [(int(round(x0 + (x1 - x0) * t / max(1, n - 1))), int(round(y0 + (y1 - y0) * t / max(1, n - 1)))) for t in range(n)])
def robe_front(L, base, sh, hi, hem, trim_mid=True):
    robe = rect(W, H, 11, 27, 20, 37) & ~pts(W, H, [(15, 27), (16, 27)])
    for y in range(38, 45):
        g = (y - 37) // 3; robe |= rect(W, H, 11 - g, y, 20 + g, y)
    shade(L, robe, C[base], C[sh], C[hi]); paint(L, robe & (ys == 44), C[hem])
    if trim_mid: paint(L, robe & ((xs == 15) | (xs == 16)) & (ys >= 29), C[hem])
    for x0, x1, cx0, cx1 in ((7, 10, 6, 10), (21, 24, 21, 25)):
        sl = rect(W, H, x0, 28, x1, 32) | rect(W, H, cx0, 33, cx1, 35)
        shade(L, sl, C[base], C[sh], C[hi]); paint(L, rect(W, H, cx0, 35, cx1, 35), C[hem])
    return robe
def class_front_new(c):
    L = layer(W, H)
    if c == 'cleric':
        robe_front(L, 'white', 'mist', 'white', 'gold')
        paint(L, rect(W, H, 11, 35, 20, 35), C['gold'])
        sym = pts(W, H, [(15, 29), (16, 29), (15, 30), (16, 30), (13, 31), (14, 31), (15, 31), (16, 31), (17, 31), (18, 31), (15, 32), (16, 32), (15, 33), (16, 33)])
        paint(L, sym, C['gold']); paint(L, pts(W, H, [(16, 33), (18, 31)]), C['amber'])
        outline(L)
    elif c == 'rogue':
        tor = rect(W, H, 11, 27, 20, 37); shade(L, tor, C['ink'], C['outline'], C['slate'])
        paint(L, line_f((12, 28), (19, 35)), C['wood_dk']); paint(L, line_f((19, 28), (12, 35)), C['wood_dk'])
        paint(L, rect(W, H, 11, 36, 20, 36), C['wood']); paint(L, pts(W, H, [(15, 36)]), C['silver'])
        for m in (rect(W, H, 8, 28, 10, 35) & ~pts(W, H, [(8, 28)]), rect(W, H, 21, 28, 23, 35) & ~pts(W, H, [(23, 28)])): shade(L, m, C['slate'], C['ink'])
        for m in (rect(W, H, 8, 34, 10, 35), rect(W, H, 21, 34, 23, 35)): paint(L, m, C['wood_dk'])
        hip = rect(W, H, 11, 37, 20, 40) | rect(W, H, 11, 41, 14, 44) | rect(W, H, 17, 41, 20, 44); shade(L, hip, C['slate'], C['ink'])
        for m in (rect(W, H, 10, 43, 14, 46), rect(W, H, 17, 43, 21, 46)): shade(L, m, C['wood_dk'], C['bark'], C['wood'])
        outline(L)
        D = layer(W, H); paint(D, rect(W, H, 23, 37, 23, 43), C['mist']); paint(D, rect(W, H, 24, 38, 24, 42), C['silver'])
        paint(D, rect(W, H, 22, 36, 25, 36), C['gold']); outline(D); over(L, D)
    elif c == 'barbarian':
        pelt = z(W, H)
        for y in range(26, 34):
            pelt |= rect(W, H, 7 + (y - 26) // 2, y, 13 + (y - 26), y)
        pelt |= ell(W, H, 9, 28.5, 3.2, 2.6)
        shade(L, pelt, C['tan'], C['wood_lt'], C['sand'])
        paint(L, pelt & (((xs + ys) % 3) == 0) & ~e_bot(pelt), C['wood_lt'])
        paint(L, pts(W, H, [(8 + i, 33 + (i % 2)) for i in range(0, 12, 2)]) , C['wood_lt'])
        belt = rect(W, H, 11, 37, 20, 38); paint(L, belt, C['wood_dk']); paint(L, rect(W, H, 15, 37, 16, 38), C['gold'])
        kilt = rect(W, H, 11, 39, 20, 41) | pts(W, H, [(11, 42), (13, 42), (15, 42), (17, 42), (19, 42)])
        shade(L, kilt, C['wood_lt'], C['wood']); paint(L, kilt & (xs % 3 == 0), C['wood'])
        for m in (rect(W, H, 8, 34, 10, 35), rect(W, H, 21, 34, 23, 35)): shade(L, m, C['wood'], C['wood_dk'])
        for m in (rect(W, H, 10, 43, 14, 46), rect(W, H, 17, 43, 21, 46)): shade(L, m, C['tan'], C['wood_lt'], C['sand'])
        outline(L)
    elif c == 'druid':
        robe_front(L, 'leaf_dk', 'pine', 'leaf', 'wood', trim_mid=False)
        paint(L, rect(W, H, 11, 35, 20, 35), C['leaf']); paint(L, pts(W, H, [(12, 35), (15, 35), (18, 35)]), C['lime'])
        paint(L, pts(W, H, [(12, 30), (18, 32), (14, 39), (19, 41), (10, 43), (21, 43)]), C['lime'])
        paint(L, line_f((14, 27), (15, 30)) | line_f((17, 27), (16, 30)), C['wood'])
        outline(L)
        S_ = layer(W, H); st = rect(W, H, 26, 18, 26, 46); paint(S_, st, C['wood']); paint(S_, rect(W, H, 27, 20, 27, 46), C['wood_dk'])
        paint(S_, pts(W, H, [(25, 16), (26, 15), (27, 16), (26, 17), (25, 18), (27, 18), (28, 17), (24, 17)]), C['lime'])
        paint(S_, pts(W, H, [(26, 16), (25, 17), (27, 17)]), C['leaf']); outline(S_); over(L, S_)
    return L
def hat_front_new(c):
    L = layer(W, H)
    if c == 'cleric':
        m = z(W, H)
        for y in range(3, 15):
            t = (y - 3) / 11; hw = 1.0 + 5.2 * t ** 0.7
            m |= (np.abs(xs - 15.5) <= hw) & (ys == y)
        shade(L, m, C['white'], C['mist'], C['white']); paint(L, m & ((xs == 15) | (xs == 16)), C['gold'])
        paint(L, m & (ys >= 13), C['gold']); paint(L, pts(W, H, [(15, 7), (16, 7), (14, 8), (17, 8)]) & m, C['gold'])
    elif c == 'rogue':
        outer = ell(W, H, 15.5, 17.6, 10.0, 9.6) & (ys <= 27)
        inner = ell(W, H, 15.5, 20.8, 7.2, 6.9) & (ys >= 15)
        m = outer & ~inner | pts(W, H, [(18, 7), (19, 7), (20, 6), (21, 6), (22, 7)])
        shade(L, m, C['slate'], C['ink'], C['gray']); paint(L, ring(inner) & m & (ys >= 14), C['ink'])
        mask_ = rect(W, H, 9, 23, 22, 25) & ell(W, H, 15.5, 21, 7.6, 6.5)
        paint(L, mask_, C['ink']); paint(L, mask_ & (ys == 23), C['slate'])
    elif c == 'barbarian':
        dome = ell(W, H, 15.5, 15.5, 8.6, 6.6) & (ys <= 15)
        shade(L, dome, C['gray'], C['slate'], C['silver']); paint(L, dome & (ys == 15), C['wood']); paint(L, pts(W, H, [(10, 15), (15, 15), (21, 15)]) & dome, C['tan'])
        hl = pts(W, H, [(7, 13), (6, 12), (5, 11), (4, 10), (4, 9), (4, 8), (5, 7), (7, 14), (6, 13), (5, 12)])
        hr = pts(W, H, [(31 - x, y) for x, y in [(7, 13), (6, 12), (5, 11), (4, 10), (4, 9), (4, 8), (5, 7), (7, 14), (6, 13), (5, 12)]])
        paint(L, hl | hr, C['cream']); paint(L, pts(W, H, [(4, 8), (5, 7), (27, 8), (26, 7)]), C['sand'])
    elif c == 'druid':
        band = rect(W, H, 7, 14, 24, 15) & ell(W, H, 15.5, 16, 9.5, 8); paint(L, band, C['wood']); paint(L, band & (ys == 15), C['wood_dk'])
        for sgn in (-1, 1):
            base = 10 if sgn < 0 else 21
            a = line_f((base, 13), (base + sgn * 2, 5)) | line_f((base + sgn * 1, 9), (base + sgn * 5, 7)) | line_f((base + sgn * 2, 6), (base + sgn * 4, 3)) | line_f((base, 11), (base - sgn * 1, 8))
            paint(L, a, C['wood_lt'])
        paint(L, pts(W, H, [(12, 14), (15, 14), (19, 14), (13, 13), (18, 13)]), C['lime'])
    outline(L); return L
def class_back_new(c):
    L = layer(BW, BH)
    tor = R(9, 27, 22, 40) & ~(E(9, 27, 1.2, 1.2) | E(22, 27, 1.2, 1.2))
    if c == 'cleric':
        robe = tor | R(9, 41, 22, 44) | R(6, 29, 8, 38) | R(23, 29, 25, 38); robe &= ~PB([(6, 29), (25, 29)])
        shade(L, robe, C['white'], C['mist'], C['white']); paint(L, robe & (bys >= _s(44)), C['gold'])
        paint(L, R(6, 38, 8, 38) | R(23, 38, 25, 38), C['gold'])
        paint(L, R(15, 29, 16, 38) | R(12, 31, 19, 32), C['gold']); paint(L, R(16, 29, 16, 38) & e_right(R(15, 29, 16, 38)), C['amber'])
        for x in (11, 20): paint(L, LN((x, 33), (x, 43)) & robe, C['mist'])
    elif c == 'rogue':
        cl = z(BW, BH)
        for y in range(26, 43):
            g = (y - 26) // 6; cl |= R(9 - g, y, 22 + g, y)
        shade(L, cl, C['slate'], C['ink'], C['gray'])
        for p0, p1 in (((12, 31), (11, 42)), ((19, 31), (20, 42))): paint(L, LN(p0, p1) & cl, C['ink'])
        outline(L)
        Q = layer(BW, BH); sh = LN((10, 40), (21, 28)); sh2 = pts(BW, BH, [(x + 1, y) for y, x in zip(*np.nonzero(sh))])
        paint(Q, sh | sh2, C['wood_dk']); paint(Q, LN((21, 28), (23, 26)) | PB([(23, 25)]), C['silver']); paint(Q, P1([(21, 28)]) | P1([(20, 29)]), C['gold'])
        outline(Q); over(L, Q); return L
    elif c == 'barbarian':
        mant = z(BW, BH)
        for y in range(26, 32): mant |= R(8, y, 23, y)
        mant |= PB([(x, 32) for x in range(8, 24, 2)])
        shade(L, mant, C['tan'], C['wood_lt'], C['sand']); paint(L, mant & (((bxs + bys) % 3) == 0) & ~e_bot(mant), C['wood_lt'])
        kilt = R(10, 40, 21, 43); shade(L, kilt, C['wood_lt'], C['wood']); paint(L, R(10, 40, 21, 40), C['wood_dk'])
        outline(L)
        Q = layer(BW, BH); hd = LN((9, 44), (22, 23)); hd2 = pts(BW, BH, [(x + 1, y) for y, x in zip(*np.nonzero(hd))])
        paint(Q, hd | hd2, C['wood'])
        blade = E(24, 22.5, 3.2, 3.8) & (bxs >= _s(22)); shade(Q, blade, C['silver'], C['gray'], C['mist'])
        paint(Q, E(20.5, 24.5, 2.0, 2.4) & (bxs <= _e(21)), C['silver'])
        outline(Q); over(L, Q); return L
    elif c == 'druid':
        robe = tor | R(9, 41, 22, 44) | R(6, 29, 8, 38) | R(23, 29, 25, 38); robe &= ~PB([(6, 29), (25, 29)])
        shade(L, robe, C['leaf_dk'], C['pine'], C['leaf']); paint(L, robe & (bys >= _s(44)), C['wood'])
        paint(L, R(6, 38, 8, 38) | R(23, 38, 25, 38), C['wood'])
        paint(L, P1([(12, 31), (19, 33), (14, 38), (18, 41), (11, 42), (16, 35)]), C['lime'])
        paint(L, LN((10, 30), (21, 30)) & robe, C['leaf'])
        outline(L)
        Q = layer(BW, BH); st = rect(BW, BH, _s(27), _s(13), _s(27) + 1, BH - 3)
        paint(Q, st, C['wood']); paint(Q, st & (bxs == _s(27) + 1), C['wood_dk'])
        top = E(27.5, 12, 2.6, 2.2); shade(Q, top, C['lime'], C['leaf']); paint(Q, P1([(27, 11)]), C['cream'])
        outline(Q); over(L, Q); return L
    outline(L); return L
def hat_back_new(c):
    L = layer(BW, BH)
    if c == 'cleric':
        m = z(BW, BH)
        for y in range(_s(3), _e(14) + 1):
            t = (y - _s(3)) / (_e(14) - _s(3)); hw = 1.5 + 7.8 * t ** 0.7
            m |= (np.abs(bxs - 23.5) <= hw) & (bys == y)
        shade(L, m, C['white'], C['mist'], C['white']); paint(L, m & (np.abs(bxs - 23.5) < 1), C['gold']); paint(L, m & (bys >= _s(13)), C['gold'])
        lap = R(13, 15, 14, 24) | R(17, 15, 18, 24); paint(L, lap, C['gold']); paint(L, lap & (bys >= _s(23)), C['amber'])
    elif c == 'rogue':
        m = E(15.5, 17.6, 10.0, 9.6) & YB(27) | PB([(18, 7), (19, 7), (20, 6), (21, 6), (22, 7), (23, 8)])
        shade(L, m, C['slate'], C['ink'], C['gray']); paint(L, LN((15, 9), (15, 26)) & m, C['ink'])
    elif c == 'barbarian':
        dome = E(15.5, 16.5, 9.0, 7.5) & YB(20); shade(L, dome, C['gray'], C['slate'], C['silver'])
        paint(L, dome & (bys >= _s(20)), C['wood']); paint(L, P1([(9, 20), (15, 20), (21, 20)]) & dome, C['tan'])
        horn = z(BW, BH)
        for side in (-1, 1):
            base = 6 if side < 0 else 25
            for p0, p1 in (((base, 15), (base + side * 2, 12)), ((base + side * 2, 12), (base + side * 2, 8)), ((base + side * 2, 8), (base + side * 1, 6))):
                l = LN(p0, p1); horn |= l | pts(BW, BH, [(x - side, y) for y, x in zip(*np.nonzero(l))])
        paint(L, horn, C['cream']); paint(L, horn & (bys <= _s(8)), C['sand'])
    elif c == 'druid':
        band = R(6, 16, 25, 17) & E(15.5, 17.5, 10.2, 9); paint(L, band, C['wood']); paint(L, band & (bys >= _s(17)), C['wood_dk'])
        for sgn in (-1, 1):
            base = 10 if sgn < 0 else 21
            a = LN((base, 15), (base + sgn * 3, 5)) | LN((base + sgn * 1, 10), (base + sgn * 6, 7)) | LN((base + sgn * 2, 7), (base + sgn * 5, 2)) | LN((base + sgn * 1, 12), (base - sgn * 1, 8))
            a |= pts(BW, BH, [(x + 1, y) for y, x in zip(*np.nonzero(a))])
            paint(L, a, C['wood_lt'])
        paint(L, P1([(9, 16), (13, 16), (18, 16), (22, 16)]), C['lime'])
    outline(L); return L
_cf, _hf, _cb, _hb = class_front, hat_front, class_back, hat_back
def class_front(c): return class_front_new(c) if c in NEW_CLASSES else _cf(c)
def hat_front(c): return hat_front_new(c) if c in NEW_CLASSES else _hf(c)
def class_back(c): return class_back_new(c) if c in NEW_CLASSES else _cb(c)
def hat_back(c): return hat_back_new(c) if c in NEW_CLASSES else _hb(c)
CLASSES = CLASSES + NEW_CLASSES
USE_OUTFIT = {c: c != 'barbarian' for c in CLASSES}     # barbarian shows bare arms/back: skip outfit_base
# default seat / party picks (1-based skin/head/hair indices, as in the file names)
SEAT_DEFAULTS = {
    'paladin':   dict(skin=2, head=1, hair=2, hair_color='brown',  outfit='white',  hat=True),
    'wizard':    dict(skin=1, head=5, hair=5, hair_color='blonde', outfit='blue',   hat=True),
    'ranger':    dict(skin=3, head=4, hair=4, hair_color='ginger', outfit='green',  hat=True),
    'bard':      dict(skin=5, head=3, hair=6, hair_color='black',  outfit='red',    hat=True),
    'cleric':    dict(skin=4, head=6, hair=2, hair_color='white',  outfit='white',  hat=True),
    'rogue':     dict(skin=2, head=2, hair=3, hair_color='black',  outfit='dark',   hat=True),
    'barbarian': dict(skin=3, head=3, hair=5, hair_color='ginger', outfit=None,     hat=True),
    'druid':     dict(skin=6, head=1, hair=7, hair_color='brown',  outfit='green',  hat=True)}
