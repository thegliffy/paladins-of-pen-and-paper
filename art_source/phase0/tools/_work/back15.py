# ======================= BACK (seated) v2: 1.5x, canvas 48x78, anchor (24,77) =======================
S = 1.5
bxs, bys = grid(BW, BH)
def _s(v): return int(np.floor(v * S))
def _e(v): return int(np.ceil((v + 1) * S)) - 1
def R(x0, y0, x1, y1): return rect(BW, BH, _s(x0), _s(y0), _e(x1), _e(y1))
def E(cx, cy, rx, ry): return ell(BW, BH, (cx + 0.5) * S - 0.5, (cy + 0.5) * S - 0.5, rx * S, ry * S)
def PB(lst):
    m = z(BW, BH)
    for x, y in lst: m |= R(x, y, x, y)
    return m
def P1(lst): return pts(BW, BH, [(int(round((x + 0.5) * S - 0.5)), int(round((y + 0.5) * S - 0.5))) for x, y in lst])
def LN(p0, p1):
    (x0, y0), (x1, y1) = [((x + 0.5) * S - 0.5, (y + 0.5) * S - 0.5) for x, y in (p0, p1)]
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    return pts(BW, BH, [(int(round(x0 + (x1 - x0) * t / max(1, n - 1))), int(round(y0 + (y1 - y0) * t / max(1, n - 1)))) for t in range(n)])
def YB(v): return bys <= _e(v)
def spikeB(cx, tip, base, hw, lean):
    m = z(BW, BH); cx, tip, base, hw, lean = (cx + 0.5) * S - 0.5, _s(tip), _e(base), hw * S, lean * S
    for y in range(tip, base + 1):
        t = (y - tip) / max(1, base - tip); c = cx + lean * (1 - t); w = hw * t + 0.5
        for x in range(int(np.floor(c - w + 0.5)), int(np.floor(c + w + 0.5))):
            if 0 <= x < BW: m[y, x] = True
    return m
def body_back(k):
    b, s, d, bl = TONES[k]; L = layer(BW, BH)
    head = E(15.5, 17.6, 8.7, 8.2); ears = R(6, 17, 6, 19) | R(25, 17, 25, 19)
    neck = R(13, 25, 18, 27)
    tor = R(9, 27, 22, 40) & ~(E(9, 27, 1.2, 1.2) | E(22, 27, 1.2, 1.2))
    arms = [R(7, 29, 8, 38) & ~PB([(7, 29)]), R(23, 29, 24, 38) & ~PB([(24, 29)])]
    hips = R(10, 40, 21, 43)
    for m in [tor, hips] + arms: shade(L, m, C[b], C[s])
    shade(L, neck, C[b], C[s]); paint(L, R(13, 27, 18, 27) & neck, C[s])
    shade(L, head, C[b], C[s]); shade(L, ears, C[b], C[s]); paint(L, P1([(6, 18), (25, 18)]), C[s])
    paint(L, pts(BW, BH, [(23, y) for y in range(44, 58)]) | pts(BW, BH, [(24, y) for y in range(44, 58)]), C[s])   # spine hint
    paint(L, pts(BW, BH, [(17, 45), (18, 46), (30, 45), (29, 46)]), C[s])   # shoulder blades
    outline(L); return L
def outfit_back():
    L = layer(BW, BH)
    sh_ = (R(9, 27, 22, 39) | R(7, 29, 8, 32) | R(23, 29, 24, 32)) & ~(PB([(7, 29), (24, 29)]) | E(9, 27, 1.2, 1.2) | E(22, 27, 1.2, 1.2))
    shade(L, sh_, K4, K3); paint(L, R(13, 27, 18, 27) & sh_, K3)
    for p0, p1 in (((12, 32), (13, 36)), ((19, 33), (18, 37)), ((10, 30), (11, 32)), ((21, 30), (20, 32))): paint(L, LN(p0, p1) & sh_, K3)
    paint(L, R(7, 32, 8, 32) | R(23, 32, 24, 32), K2)
    shorts = R(10, 40, 21, 43); shade(L, shorts, C['wood'], C['wood_dk']); paint(L, R(10, 40, 21, 40), C['wood_dk'])
    outline(L); return L
def chair_back():
    L = layer(BW, BH)
    wood = lambda m: shade(L, m, C['wood'], C['wood_dk'], C['wood_lt'])
    wood(R(6, 43, 25, 44))
    for x in (8, 22): wood(R(x, 33, x + 1, 51))
    wood(R(8, 33, 23, 34)); wood(R(10, 38, 21, 38)); wood(R(10, 48, 21, 48))
    for x in (6, 24): wood(R(x, 45, x + 1, 51))
    for x in (13, 18): wood(rect(BW, BH, _s(x), _e(34) + 1, _s(x) + 1, _s(38) - 1))   # back spindles
    paint(L, pts(BW, BH, [(x, _s(33) + 1) for x in range(_s(8) + 3, _e(23) - 2, 6)]), C['wood_dk'])  # grain ticks
    outline(L); return L
def afro_back():
    L = layer(BW, BH)
    cx, cy, rx, ry = 23.5, 23.3, 18.4, 15.8
    cl = []
    for i in range(16):
        a = i / 16 * 2 * np.pi; cl.append((cx + (rx - 3.6) * np.cos(a), cy + (ry - 3.6) * np.sin(a), 4.3))
    for i in range(8):
        a = (i + 0.5) / 8 * 2 * np.pi; cl.append((cx + (rx * 0.5) * np.cos(a), cy + (ry * 0.5) * np.sin(a), 4.8))
    cl.append((cx, cy, 5.0))
    m = ell(BW, BH, cx, cy, rx - 2.2, ry - 2.2)
    for (ccx, ccy, r) in cl[:16]: m |= ell(BW, BH, ccx, ccy, r, r)
    idx = np.full((BH, BW), -1); best = np.full((BH, BW), 9e9)
    for i, (ccx, ccy, r) in enumerate(cl):
        d = np.sqrt((bxs - ccx) ** 2 + (bys - ccy) ** 2) / r
        u = d < best; best[u] = d[u]; idx[u] = i
    tone = np.full((BH, BW), 2)   # 0=K1 1=K2 2=K3 3=K4
    for i, (ccx, ccy, r) in enumerate(cl):
        sel = idx == i
        rel = ((bxs - ccx) + (bys - ccy)) / r
        tone[sel & (rel > 0.5)] = 1
        tone[sel & (rel < -0.75) & (ccy < cy + 0.25 * ry)] = 3
    crease = (idx != np.roll(idx, -1, 1)) | (idx != np.roll(idx, -1, 0))
    tone[crease] = np.minimum(tone[crease], 1)
    low = bys > cy + 0.42 * ry; tone[low] = np.maximum(tone[low] - 1, 0)
    tone[bys > cy + 0.72 * ry] = 0
    tone[crease & low] = 0
    keys = [K1, K2, K3, K4]
    for t in range(4): paint(L, m & (tone == t), keys[t])
    outline(L); return L
def hair_back(n):
    kind = HAIRS[n]; L = layer(BW, BH)
    if kind == 'bald': return L
    if kind == 'afro': return afro_back()
    capb = E(15.5, 17.2, 9.3, 8.7) & YB(23)
    def hs(m):
        shade(L, m, K3, K2)
        paint(L, m & (bys >= _s(10)) & (bys <= _e(12)) & (bxs >= _s(9)) & (bxs <= _e(14)) & ~e_bot(m) & ~e_right(m), K4)
        for p0, p1 in (((12, 17), (12, 21)), ((15, 16), (15, 22)), ((19, 17), (19, 21)), ((13, 13), (13, 15)), ((18, 14), (18, 16))):
            paint(L, LN(p0, p1) & m & ~e_bot(m), K2)
    if kind == 'short': m = capb | PB([(12, 24), (15, 24), (16, 24), (19, 24)]); hs(m)
    elif kind == 'spiky':
        m = capb.copy()
        for cx, tip, ln in ((8, 6, -1.5), (12, 3, -0.5), (16, 2, 0.5), (20, 3, 1.0), (24, 6, 1.5)): m |= spikeB(cx, tip, 12, 2.3, ln)
        hs(m); paint(L, P1([(12, 5), (16, 4), (20, 5)]) & m, K4)
    elif kind == 'ponytail':
        m = capb; tail = R(14, 22, 17, 33) & ~(PB([(14, 33), (17, 33)]))
        hs(m); shade(L, tail, K3, K2); paint(L, R(14, 22, 17, 22), K1)
        for y in range(25, 33, 2): paint(L, LN((15, y), (16, y + 1)) & tail, K4 if y % 4 == 1 else K2)
        m = m | tail
    elif kind == 'long':
        m = E(15.5, 17.2, 9.8, 8.9) & YB(22) | (R(7, 18, 24, 34) & ~PB([(7, 34), (24, 34)]))
        hs(m)
        for x in (10, 13, 18, 21): paint(L, LN((x, 23), (x, 33)) & m & ~e_bot(m), K2)
        paint(L, LN((11, 23), (11, 28)) | LN((20, 23), (20, 28)), K4)
    elif kind == 'braids':
        m = capb; hs(m); paint(L, LN((15, 9), (15, 23)) & m, K1)
        for bx in (10, 19):
            br = R(bx, 23, bx + 2, 35); shade(L, br, K3, K2)
            for y in range(24, 34, 2): paint(L, LN((bx, y), (bx + 2, y + 1)) & br, K2)
            paint(L, R(bx, 33, bx + 2, 33), K1); m = m | br
    elif kind == 'mohawk':
        m = R(14, 7, 17, 24) | spikeB(15.5, 1, 8, 2.0, 0)
        shade(L, m, K3, K2); paint(L, LN((15, 4), (15, 23)), K4); paint(L, LN((16, 6), (16, 23)) & m & ~e_right(m), K2)
    outline(L); return L
def class_back(c):
    L = layer(BW, BH)
    tor = R(9, 27, 22, 40) & ~(E(9, 27, 1.2, 1.2) | E(22, 27, 1.2, 1.2))
    if c == 'paladin':
        armor(L, tor)
        paint(L, LN((9, 33), (22, 33)) & tor, C['gray']); paint(L, LN((9, 37), (22, 37)) & tor, C['gray'])
        for m in (R(7, 33, 8, 38), R(23, 33, 24, 38)): armor(L, m)
        cape = R(11, 28, 20, 44); shade(L, cape, C['white'], C['mist'])
        for x in (13, 18): paint(L, LN((x, 31), (x, 44)) & cape, C['mist'])
        paint(L, R(15, 30, 16, 34) | R(14, 31, 17, 32), C['gold'])
        for m in (E(8.5, 29.0, 3.0, 2.4), E(23.0, 29.0, 3.0, 2.4)): armor(L, m)
    elif c == 'wizard':
        robe = tor | R(9, 41, 22, 44) | R(6, 29, 8, 38) | R(23, 29, 25, 38)
        robe &= ~PB([(6, 29), (25, 29)])
        shade(L, robe, C['blue'], C['blue_dk'], C['sky']); paint(L, robe & (bys >= _s(44)), C['gold'])
        paint(L, (R(6, 38, 8, 38) | R(23, 38, 25, 38)), C['gold'])
        for x, y0 in ((13, 30), (18, 31)): paint(L, LN((x, y0), (x, 43)) & robe, C['blue_dk'])
        paint(L, P1([(15, 34), (16, 38), (12, 40), (19, 36)]), C['gold'])
    elif c == 'ranger':
        cl = z(BW, BH)
        for y in range(26, 45):
            g = (y - 26) // 5; cl |= R(8 - g, y, 23 + g, y)
        shade(L, cl, C['leaf'], C['leaf_dk'], C['grass'])
        for p0, p1 in (((12, 32), (11, 44)), ((19, 32), (20, 44)), ((15, 36), (15, 44))): paint(L, LN(p0, p1) & cl, C['leaf_dk'])
        Q = layer(BW, BH); shade(Q, R(19, 24, 21, 33), C['wood'], C['wood_dk'])
        paint(Q, P1([(19, 22), (20, 21), (21, 22)]) | PB([(20, 23)]), C['white']); paint(Q, P1([(20, 22)]), C['red'])
        bow = LN((6, 43), (24, 25)); bw2 = pts(BW, BH, [(x + 1, y) for y, x in zip(*np.nonzero(bow))])
        paint(Q, bow | bw2, C['wood_lt']); paint(Q, bw2 & (bys > 50), C['wood'])
        outline(L); outline(Q); over(L, Q); return L
    elif c == 'bard':
        shade(L, tor, C['red'], C['red_dk'], C['coral']); paint(L, R(15, 28, 16, 39), C['red_dk'])
        paint(L, P1([(12, 31), (19, 31), (12, 36), (19, 36)]), C['gold'])
        for m in (E(8.0, 29.5, 2.6, 2.3), E(23.5, 29.5, 2.6, 2.3)):
            shade(L, m, C['cream'], C['sand'])
        paint(L, P1([(8, 29), (23, 30)]), C['red'])
        shade(L, R(10, 40, 21, 43), C['violet'], C['plum']); paint(L, R(10, 40, 21, 40), C['wood_dk'])
        outline(L)
        Lu = layer(BW, BH); nk = LN((24, 33), (27, 27)); nk2 = pts(BW, BH, [(x + 1, y) for y, x in zip(*np.nonzero(nk))])
        paint(Lu, nk | nk2, C['wood_dk']); paint(Lu, R(27, 25, 28, 27), C['wood']); paint(Lu, P1([(27, 25), (28, 26)]), C['tan'])
        bod = E(23.5, 37, 2.6, 3.2); shade(Lu, bod, C['tan'], C['wood_lt'], C['sand'])
        outline(Lu); over(L, Lu); return L
    outline(L); return L
def hat_back(c):
    L = layer(BW, BH)
    if c == 'paladin':
        m = E(15.5, 17.2, 9.6, 8.8) & YB(24); shade(L, m, C['silver'], C['gray'], C['mist'])
        paint(L, R(6, 21, 25, 21) & m, C['gray']); paint(L, R(15, 9, 16, 20) & m, C['gold'])
        paint(L, P1([(9, 21), (12, 21), (19, 21), (22, 21)]) & m, C['mist'])
        pl = LN((16, 7), (19, 3)) | LN((17, 7), (20, 3)); paint(L, pl, C['blue']); paint(L, P1([(19, 3)]), C['sky'])
    elif c == 'wizard':
        brim = E(15.5, 13.8, 12.6, 2.2); cone = z(BW, BH)
        for y in range(_s(1), _e(12) + 1):
            t = (y - _s(1)) / (_e(12) - _s(1)); cxx = 23.5 - 5.2 * (1 - t) ** 2; hw = 0.9 + 9.6 * t
            cone |= (np.abs(bxs - cxx) <= hw) & (bys == y)
        shade(L, brim, C['blue'], C['blue_dk'], C['sky']); shade(L, cone, C['blue'], C['blue_dk'], C['sky'])
        paint(L, cone & (bys >= _s(10)) & (bys <= _e(11)), C['gold'])
        paint(L, P1([(14, 6), (17, 8)]) & cone, C['gold'])
    elif c == 'ranger':
        m = E(15.5, 17.6, 10.2, 9.6) & YB(27) | PB([(15, 7), (16, 7), (16, 6)])
        shade(L, m, C['leaf'], C['leaf_dk'], C['grass']); paint(L, LN((15, 9), (15, 26)) & m, C['leaf_dk'])
        paint(L, LN((11, 12), (9, 22)) & m & ~e_left(m), C['grass'])
    elif c == 'bard':
        capm = E(16.0, 13.2, 9.3, 3.6) & YB(15); shade(L, capm, C['red'], C['red_dk'], C['coral'])
        paint(L, capm & (bys >= _s(15)), C['red_dk'])
        f = LN((10, 11), (3, 4)) | LN((10, 10), (4, 4)) | LN((9, 11), (3, 5))
        paint(L, f, C['white']); paint(L, LN((9, 11), (4, 6)) & f, C['mist']); paint(L, P1([(11, 12), (12, 12)]), C['gold'])
    outline(L); return L

HAT_CLIP_FRONT = {'paladin': 16, 'wizard': 14, 'ranger': 17, 'bard': 14}
HAT_CLIP_BACK = {'paladin': _s(22), 'wizard': _s(14), 'ranger': _s(24), 'bard': _s(14)}
