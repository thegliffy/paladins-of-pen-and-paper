"""Procedural layered chibi paperdoll (front 32x48 + seated back 32x52)."""
import json, random
from proclib import *
from pal import save, C, OUT
META = {}
W, H = 32, 48          # front canvas, anchor (16,47)
BW, BH = 48, 78        # v2 back/seated canvas (1.5x), anchor (24,77) == party seats
K1, K2, K3, K4 = C['slate'], C['gray'], C['silver'], C['mist']      # grayscale keys darkest->lightest
REF = dict(base=C['skin3'], shadow=C['skin4'], detail=C['skin5'], blush=C['coral'])
TONES = [('skin1', 'skin2', 'skin3', 'pink'), ('skin2', 'skin3', 'skin4', 'rose'), ('skin3', 'skin4', 'skin5', 'coral'),
         ('skin4', 'skin5', 'skin6', 'red'), ('skin5', 'skin6', 'wood_dk', 'red_dk'), ('skin6', 'wood_dk', 'bark', 'red_dk')]
def tone_map(k):
    b, s, d, bl = TONES[k]
    return {REF['base']: C[b], REF['shadow']: C[s], REF['detail']: C[d], REF['blush']: C[bl]}
HAIR_RAMPS = {'black': ['outline', 'ink', 'slate', 'gray'], 'brown': ['bark', 'wood_dk', 'wood', 'wood_lt'],
    'blonde': ['wood_lt', 'tan', 'gold', 'cream'], 'ginger': ['red_dk', 'orange', 'amber', 'gold'],
    'white': ['gray', 'silver', 'mist', 'white'], 'blue': ['navy', 'blue_dk', 'blue', 'sky'],
    'pink': ['red_dk', 'rose_dk', 'rose', 'pink'], 'green': ['pine_dk', 'leaf_dk', 'leaf', 'grass']}
OUTFIT_RAMPS = {'white': ['silver', 'mist', 'white'], 'red': ['red_dk', 'red', 'coral'], 'blue': ['blue_dk', 'blue', 'sky'],
    'purple': ['plum_dk', 'plum', 'violet'], 'green': ['pine', 'leaf_dk', 'leaf'], 'yellow': ['orange', 'amber', 'gold'],
    'brown': ['wood_dk', 'wood', 'wood_lt'], 'dark': ['ink', 'slate', 'gray']}
def hair_map(name): return {k: C[v] for k, v in zip((K1, K2, K3, K4), HAIR_RAMPS[name])}
def outfit_map(name): return {k: C[v] for k, v in zip((K2, K3, K4), OUTFIT_RAMPS[name])}
O = C['outline']

def finish(L, fill_masks, diag=False):
    outline(L, diag=diag); return L

# ======================= FRONT =======================
xs, ys = grid(W, H)
def body_front(k):
    b, s, d, bl = TONES[k]
    L = layer(W, H)
    parts = [rect(W, H, 11, 27, 20, 37), rect(W, H, 11, 38, 20, 41)]
    armL = rect(W, H, 8, 28, 10, 34) & ~pts(W, H, [(8, 28)]); armR = rect(W, H, 21, 28, 23, 34) & ~pts(W, H, [(23, 28)])
    handL = rect(W, H, 8, 35, 10, 37) & ~pts(W, H, [(8, 37), (10, 37)]); handR = rect(W, H, 21, 35, 23, 37) & ~pts(W, H, [(21, 37), (23, 37)])
    legL = rect(W, H, 11, 42, 14, 44); legR = rect(W, H, 17, 42, 20, 44)
    for m in parts + [armL, armR, legL, legR]: shade(L, m, C[b], C[s])
    for m in (handL, handR): shade(L, m, C[b], C[s])
    paint(L, rect(W, H, 11, 27, 20, 27), C[s])          # chin shadow
    paint(L, pts(W, H, [(15, 33), (16, 33)]), C[s])     # belly button hint
    for m in (rect(W, H, 10, 45, 14, 46), rect(W, H, 17, 45, 21, 46)):
        shade(L, m, C['wood_dk'], C['bark'], C['wood'])
    outline(L); return L

def head_mask(shape):
    if shape == 'square':
        m = rect(W, H, 7, 11, 24, 26) & ~pts(W, H, [(7, 11), (8, 11), (7, 12), (24, 11), (23, 11), (24, 12), (7, 26), (24, 26), (8, 26), (23, 26), (7, 25), (24, 25)])
        ears = pts(W, H, [(6, 18), (6, 19), (6, 20), (25, 18), (25, 19), (25, 20)])
    elif shape == 'chubby':
        m = ell(W, H, 15.5, 19.2, 9.4, 7.7) | ell(W, H, 15.5, 18, 8.2, 7.6)
        ears = pts(W, H, [(5, 19), (5, 20), (26, 19), (26, 20)])
    else:
        m = ell(W, H, 15.5, 18.6, 8.7, 8.2)
        ears = pts(W, H, [(6, 18), (6, 19), (6, 20), (25, 18), (25, 19), (25, 20)])
    return m, ears
HEADS = ['round', 'square', 'chubby', 'freckles', 'glasses', 'beard']
def head_front(n):
    kind = HEADS[n]; shape = kind if kind in ('square', 'chubby') else 'round'
    L = layer(W, H); m, ears = head_mask(shape)
    shade(L, m, REF['base'], REF['shadow']); shade(L, ears, REF['base'], REF['shadow'])
    paint(L, pts(W, H, [(6, 19), (25, 19)] if shape != 'chubby' else [(5, 20), (26, 20)]), REF['shadow'])
    outline(L)
    # eyes 2x2 with highlight, brows, nose, mouth
    for ex in (11, 19):
        paint(L, rect(W, H, ex, 19, ex + 1, 20), O); L[19, ex + 1] = C['white'] + (255,)
        paint(L, pts(W, H, [(ex, 17), (ex + 1, 17)]), REF['detail'])
    L[21, 16] = REF['shadow'] + (255,)
    if kind == 'chubby':
        paint(L, pts(W, H, [(14, 22), (15, 23), (16, 23), (17, 22)]), REF['detail'])
        paint(L, pts(W, H, [(8, 22), (9, 22), (8, 23), (22, 22), (23, 22), (23, 23)]), REF['blush'])
    elif kind == 'square':
        paint(L, pts(W, H, [(14, 23), (15, 23), (16, 23), (17, 23)]), REF['detail'])
        paint(L, pts(W, H, [(9, 22), (10, 22), (21, 22), (22, 22)]), REF['blush'])
        paint(L, rect(W, H, 9, 25, 22, 25) & m, REF['shadow'])
    else:
        paint(L, pts(W, H, [(15, 23), (16, 23)]), REF['detail'])
        if kind != 'freckles': paint(L, pts(W, H, [(9, 22), (10, 22), (21, 22), (22, 22)]), REF['blush'])
    if kind == 'freckles':
        paint(L, pts(W, H, [(9, 21), (11, 22), (9, 23), (20, 22), (22, 21), (22, 23)]), REF['detail'])
    if kind == 'glasses':
        for x0 in (10, 18):
            r = rect(W, H, x0, 18, x0 + 3, 21) & ~rect(W, H, x0 + 1, 19, x0 + 2, 20)
            paint(L, r, O); paint(L, rect(W, H, x0 + 1, 19, x0 + 2, 20) & ~(L[..., 0] == O[0]), C['ice'])
            paint(L, pts(W, H, [(x0 + 1, 20)]), O)
        paint(L, pts(W, H, [(14, 19), (15, 19), (16, 19), (17, 19), (7, 19), (8, 19), (9, 19), (22, 19), (23, 19), (24, 19)]), O)
    if kind == 'beard':
        bm = (m | ell(W, H, 15.5, 21.5, 8.6, 7.4)) & (((ys >= 22)) | (((xs <= 8) | (xs >= 23)) & (ys >= 17)))
        bm &= ~ears
        shade(L, bm, K3, K2, K4)
        paint(L, pts(W, H, [(12, 22), (19, 22)]) & bm, K4)
        paint(L, pts(W, H, [(14, 24), (15, 24), (16, 24), (17, 24)]), REF['detail'])
        paint(L, pts(W, H, [(15, 22), (16, 22)]), K2)
        r = ring(bm) & ~m & ~ears; paint(L, r, O)
    return L

def cap(cy=17.5, rx=9.4, ry=8.6, bottom=16):
    return ell(W, H, 15.5, cy, rx, ry) & (ys <= bottom)
def spike(cx, tip, base=12, hw=2.4, lean=0.0):
    m = z(W, H)
    for y in range(tip, base + 1):
        t = (y - tip) / max(1, base - tip); c = cx + lean * (1 - t); w = hw * t + 0.5
        for x in range(int(np.floor(c - w + 0.5)), int(np.floor(c + w + 0.5))):
            if 0 <= x < W: m[y, x] = True
    return m
def hair_shade(L, m, hl_rows=(10, 12), hl_x=(9, 14)):
    shade(L, m, K3, K2)
    paint(L, m & (ys >= hl_rows[0]) & (ys <= hl_rows[1]) & (xs >= hl_x[0]) & (xs <= hl_x[1]) & ~e_bot(m) & ~e_right(m), K4)
HAIRS = ['bald', 'short', 'spiky', 'ponytail', 'long', 'braids', 'afro', 'mohawk']
BANGS = pts(W, H, [(9, 17), (10, 17), (14, 17), (15, 17), (16, 17), (21, 17), (22, 17)])
def hair_front(n):
    kind = HAIRS[n]; L = layer(W, H)
    if kind == 'bald': return L
    side = rect(W, H, 7, 16, 8, 19) | rect(W, H, 23, 16, 24, 19)
    if kind == 'short':
        m = cap() | side | BANGS; hair_shade(L, m)
    elif kind == 'spiky':
        m = cap() | side | BANGS
        for cx, tip, ln in ((8, 6, -1.5), (12, 3, -0.5), (16, 2, 0.5), (20, 3, 1.0), (24, 6, 1.5)): m |= spike(cx, tip, 12, 2.3, ln)
        hair_shade(L, m, (6, 11), (9, 15))
        paint(L, pts(W, H, [(12, 5), (16, 4), (20, 5)]) & m, K4)
    elif kind == 'ponytail':
        tail = ell(W, H, 26.5, 22, 2.3, 7.2) & (ys >= 14)
        m = cap() | side | BANGS
        hair_shade(L, m); shade(L, tail, K3, K2); paint(L, tail & (xs == 26) & (ys >= 17) & (ys <= 26) & (ys % 3 == 0), K4)
        paint(L, rect(W, H, 24, 13, 25, 15), K1)
        m = m | tail
    elif kind == 'long':
        m = cap(17.5, 10.0, 8.9) | BANGS
        curt = (rect(W, H, 5, 14, 8, 33) | rect(W, H, 23, 14, 26, 33)) & ~pts(W, H, [(5, 33), (8, 33), (23, 33), (26, 33), (5, 14), (26, 14)])
        m |= curt; hair_shade(L, m)
        paint(L, pts(W, H, [(6, y) for y in range(20, 32, 3)] + [(25, y) for y in range(21, 32, 3)]), K2)
        paint(L, pts(W, H, [(15, 9), (15, 10), (16, 10)]), K2)
    elif kind == 'braids':
        m = cap() | side | pts(W, H, [(9, 17), (10, 17), (21, 17), (22, 17)])
        hair_shade(L, m); paint(L, pts(W, H, [(15, 9), (15, 10), (15, 11), (16, 11), (16, 12)]) & m, K1)
        for bx in (5, 24):
            br = rect(W, H, bx, 17, bx + 2, 32)
            shade(L, br, K3, K2)
            for y in range(18, 32, 3): paint(L, pts(W, H, [(bx, y), (bx + 1, y + 1)]), K2); L[y, bx + 1] = K4 + (255,)
            paint(L, rect(W, H, bx, 30, bx + 2, 30), K1)
            paint(L, pts(W, H, [(bx, 33), (bx + 2, 33), (bx + 1, 33)]), K2)
            m |= br | rect(W, H, bx, 33, bx + 2, 33)
    elif kind == 'afro':
        big = ell(W, H, 15.5, 15.0, 12.4, 10.4)
        face = ell(W, H, 15.5, 21, 7.4, 6.8) & (ys >= 17)
        m = big & ~face & (ys <= 25)
        shade(L, m, K3, K2)
        for y in range(H):
            for x in range(W):
                if m[y, x] and not (e_bot(m)[y, x] or e_right(m)[y, x]):
                    h = hsh(x, y, 21)
                    if h < 0.16: L[y, x] = K4 + (255,)
                    elif h < 0.30: L[y, x] = K2 + (255,)
        paint(L, pts(W, H, [(9, 16), (10, 17), (21, 17), (22, 16)]) & m, K2)
    elif kind == 'mohawk':
        m = rect(W, H, 14, 7, 17, 15)
        for cx, tip in ((15.5, 2), (15.5, 2)): pass
        m |= spike(15.5, 1, 8, 2.0, 0) | pts(W, H, [(14, 16), (17, 16)])
        hair_shade(L, m, (2, 12), (14, 15))
        paint(L, pts(W, H, [(16, y) for y in range(4, 15, 3)]) & m, K2)
        paint(L, pts(W, H, [(8, 14), (9, 13), (22, 13), (23, 14)]), K2)     # shaved sides stubble
    outline(L); return L

def outfit_front():
    L = layer(W, H)
    shirt = (rect(W, H, 11, 27, 20, 37) | rect(W, H, 8, 28, 10, 31) | rect(W, H, 21, 28, 23, 31)) & ~pts(W, H, [(8, 28), (23, 28), (14, 27), (15, 27), (16, 27), (17, 27), (15, 28), (16, 28)])
    shade(L, shirt, K4, K3); paint(L, pts(W, H, [(10, 30), (10, 31), (21, 30), (21, 31)]), K3)
    paint(L, pts(W, H, [(13, 34), (18, 34), (12, 36)]), K3); paint(L, pts(W, H, [(14, 28), (17, 28)]), K2)
    shorts = rect(W, H, 11, 38, 20, 40) | rect(W, H, 11, 41, 14, 42) | rect(W, H, 17, 41, 20, 42)
    shade(L, shorts, C['wood'], C['wood_dk']); paint(L, rect(W, H, 11, 38, 20, 38), C['wood_dk'])
    paint(L, pts(W, H, [(15, 40), (16, 40)]), C['wood_dk'])
    outline(L); return L

def armor(L, m):
    shade(L, m, C['silver'], C['gray'], C['mist'])
CLASSES = ['paladin', 'wizard', 'ranger', 'bard']
def class_front(c):
    L = layer(W, H)
    if c == 'paladin':
        torso = rect(W, H, 11, 27, 20, 39); armor(L, torso)
        tab = rect(W, H, 13, 28, 18, 41); shade(L, tab, C['white'], C['mist'])
        paint(L, rect(W, H, 15, 30, 16, 36) | rect(W, H, 13, 32, 18, 33), C['gold']); paint(L, pts(W, H, [(16, 36), (18, 33)]), C['amber'])
        paint(L, rect(W, H, 11, 37, 12, 37) | rect(W, H, 19, 37, 20, 37), C['wood_dk'])
        for m in (ell(W, H, 9.0, 29.2, 2.7, 2.3), ell(W, H, 22.0, 29.2, 2.7, 2.3)): armor(L, m)
        for m in (rect(W, H, 8, 34, 10, 37) & ~pts(W, H, [(8, 37), (10, 37)]), rect(W, H, 21, 34, 23, 37) & ~pts(W, H, [(21, 37), (23, 37)])): armor(L, m)
        for m in (rect(W, H, 11, 42, 14, 44), rect(W, H, 17, 42, 20, 44)): armor(L, m)
        for m in (rect(W, H, 10, 45, 14, 46), rect(W, H, 17, 45, 21, 46)): shade(L, m, C['gray'], C['slate'], C['silver'])
        outline(L)
        sh_ = rect(W, H, 22, 31, 28, 37) | rect(W, H, 23, 38, 27, 38) | rect(W, H, 24, 39, 26, 39) | pts(W, H, [(25, 40)])
        S = layer(W, H); shade(S, sh_, C['blue'], C['blue_dk'], C['sky'])
        paint(S, rect(W, H, 25, 32, 25, 38) | rect(W, H, 23, 34, 27, 34), C['gold']); outline(S); over(L, S)
    elif c == 'wizard':
        robe = rect(W, H, 11, 27, 20, 37) & ~pts(W, H, [(15, 27), (16, 27)])
        for y in range(38, 45):
            g = (y - 37) // 3; robe |= rect(W, H, 11 - g, y, 20 + g, y)
        shade(L, robe, C['blue'], C['blue_dk'], C['sky'])
        paint(L, robe & (ys == 44), C['gold']); paint(L, robe & ((xs == 15) | (xs == 16)) & (ys >= 29), C['blue_dk'])
        paint(L, rect(W, H, 11, 35, 20, 35), C['gold']); paint(L, pts(W, H, [(15, 35), (16, 35)]), C['amber'])
        paint(L, pts(W, H, [(14, 27), (17, 27), (14, 28), (17, 28)]), C['gold'])
        for x0, x1, cx0, cx1 in ((7, 10, 6, 10), (21, 24, 21, 25)):
            sl = rect(W, H, x0, 28, x1, 32) | rect(W, H, cx0, 33, cx1, 35)
            shade(L, sl, C['blue'], C['blue_dk'], C['sky']); paint(L, rect(W, H, cx0, 35, cx1, 35), C['gold'])
        outline(L)
    elif c == 'ranger':
        cloak = rect(W, H, 6, 28, 7, 41) & ~pts(W, H, [(6, 28)])
        shade(L, cloak, C['pine'], C['pine_dk'])
        tun = rect(W, H, 11, 27, 20, 37) | rect(W, H, 11, 38, 20, 41) & ~pts(W, H, [(15, 41), (16, 41)])
        shade(L, tun, C['leaf'], C['leaf_dk'], C['grass'])
        paint(L, pts(W, H, [(12 + i, 27 + i) for i in range(9)]), C['wood'])
        paint(L, rect(W, H, 11, 37, 20, 37), C['wood_dk']); paint(L, pts(W, H, [(15, 37), (16, 37)]), C['tan'])
        for m in (rect(W, H, 8, 28, 10, 33) & ~pts(W, H, [(8, 28)]), rect(W, H, 21, 28, 23, 33) & ~pts(W, H, [(23, 28)])): shade(L, m, C['leaf_dk'], C['pine'])
        for m in (rect(W, H, 8, 34, 10, 35), rect(W, H, 21, 34, 23, 35)): shade(L, m, C['wood'], C['wood_dk'])
        for m in (rect(W, H, 11, 42, 14, 42), rect(W, H, 17, 42, 20, 42)): paint(L, m, C['wood_dk'])
        for m in (rect(W, H, 10, 43, 14, 46), rect(W, H, 17, 43, 21, 46)): shade(L, m, C['wood'], C['wood_dk'], C['wood_lt'])
        outline(L)
        bow = pts(W, H, [(25, 26), (26, 27), (26, 28), (27, 29), (27, 30), (27, 31), (27, 32), (27, 33), (27, 34), (27, 35), (27, 36), (26, 37), (26, 38), (25, 39)])
        Bw = layer(W, H); paint(Bw, bow, C['wood_lt']); paint(Bw, bow & (ys > 32), C['wood'])
        paint(Bw, pts(W, H, [(25, y) for y in range(27, 39)]), C['mist']); outline(Bw); over(L, Bw)
    elif c == 'bard':
        tors = rect(W, H, 11, 27, 20, 37); shade(L, tors, C['red'], C['red_dk'], C['coral'])
        paint(L, rect(W, H, 15, 28, 15, 37), C['red_dk']); paint(L, pts(W, H, [(16, 29), (16, 32), (16, 35)]), C['gold'])
        paint(L, pts(W, H, [(14, 27), (15, 27), (16, 27), (17, 27)]), C['cream'])
        for x0 in (7, 21):
            puff = rect(W, H, x0, 28, x0 + 3, 32) & ~pts(W, H, [(x0, 28), (x0 + 3, 28), (x0, 32), (x0 + 3, 32)])
            shade(L, puff, C['cream'], C['sand']); paint(L, pts(W, H, [(x0 + 1, 29), (x0 + 2, 30), (x0 + 1, 31)]), C['red'])
            shade(L, rect(W, H, x0 + 1, 33, x0 + 3, 34), C['red'], C['red_dk'])
        hip = rect(W, H, 11, 38, 20, 40) | rect(W, H, 11, 41, 14, 44) | rect(W, H, 17, 41, 20, 44)
        shade(L, hip, C['violet'], C['plum']); paint(L, rect(W, H, 11, 38, 20, 38), C['wood_dk']); L[38, 15] = C['gold'] + (255,)
        outline(L)
        Lu = layer(W, H)
        neck = pts(W, H, [(18, 31), (19, 30), (20, 29), (21, 28), (22, 27), (23, 26), (24, 25), (19, 31), (20, 30), (21, 29), (22, 28), (23, 27), (24, 26)])
        paint(Lu, neck, C['wood_dk']); paint(Lu, rect(W, H, 25, 23, 26, 25), C['wood'])
        bod = ell(W, H, 14.5, 34.5, 4.3, 3.4); shade(Lu, bod, C['tan'], C['wood_lt'], C['sand'])
        paint(Lu, pts(W, H, [(14, 34), (15, 34), (14, 35)]), O); paint(Lu, pts(W, H, [(17, 33), (17, 34)]), C['wood'])
        outline(Lu); over(L, Lu)
    return L

def hat_front(c):
    L = layer(W, H)
    if c == 'paladin':
        dome = ell(W, H, 15.5, 16.0, 9.6, 7.8) & (ys <= 16)
        guard = rect(W, H, 6, 16, 8, 22) | rect(W, H, 23, 16, 25, 22)
        m = dome | guard; shade(L, m, C['silver'], C['gray'], C['mist'])
        paint(L, rect(W, H, 6, 15, 25, 16) & m, C['gray']); paint(L, pts(W, H, [(9, 15), (15, 15), (22, 15)]), C['mist'])
        paint(L, rect(W, H, 15, 8, 16, 14) & m, C['gold'])
        pl = pts(W, H, [(15, 6), (16, 6), (16, 5), (17, 5), (17, 4), (18, 4), (15, 7), (16, 7)])
        paint(L, pl, C['blue']); paint(L, pts(W, H, [(17, 4), (18, 4)]), C['sky'])
    elif c == 'wizard':
        brim = ell(W, H, 15.5, 13.8, 12.6, 2.2)
        cone = z(W, H)
        for y in range(1, 13):
            t = (y - 1) / 11; cx = 15.5 + 3.5 * (1 - t) ** 2; hw = 0.6 + 6.4 * t
            cone |= (np.abs(xs + 0.5 - cx - 0.5) <= hw) & (ys == y)
        cone |= pts(W, H, [(20, 0), (21, 0), (21, 1)])
        shade(L, brim, C['blue'], C['blue_dk'], C['sky']); shade(L, cone, C['blue'], C['blue_dk'], C['sky'])
        paint(L, cone & ((ys == 10) | (ys == 11)), C['gold']); paint(L, pts(W, H, [(15, 6), (14, 7), (15, 7), (16, 7), (15, 8)]), C['gold'])
    elif c == 'ranger':
        outer = ell(W, H, 15.5, 17.8, 10.3, 9.8) & (ys <= 27)
        inner = ell(W, H, 15.5, 20.5, 7.5, 7.4) & (ys >= 15)
        m = outer & ~inner | pts(W, H, [(15, 7), (16, 7), (16, 6)])
        shade(L, m, C['leaf'], C['leaf_dk'], C['grass']); paint(L, ring(inner) & m & (ys >= 14), C['leaf_dk'])
    elif c == 'bard':
        capm = ell(W, H, 15.0, 13.2, 9.3, 3.6) & (ys <= 15)
        shade(L, capm, C['red'], C['red_dk'], C['coral']); paint(L, capm & (ys == 15), C['red_dk'])
        f = pts(W, H, [(20, 11), (21, 10), (22, 9), (23, 8), (24, 7), (25, 6), (26, 5), (27, 4), (21, 11), (22, 10), (23, 9), (24, 8), (25, 7), (26, 6), (27, 5), (28, 3)])
        paint(L, f, C['white']); paint(L, pts(W, H, [(22, 10), (24, 8), (26, 6)]), C['mist']); paint(L, pts(W, H, [(19, 12), (20, 12)]), C['gold'])
    outline(L); return L

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
    def jit(i, k): return (hsh(i, k, 77) - 0.5) * 1.4
    for i in range(20):
        a = i / 20 * 2 * np.pi; cl.append((cx + (rx - 3.2) * np.cos(a) + jit(i, 1), cy + (ry - 3.2) * np.sin(a) + jit(i, 2), 3.6 + jit(i, 3) * 0.5))
    for i in range(12):
        a = (i + 0.5) / 12 * 2 * np.pi; cl.append((cx + (rx * 0.6) * np.cos(a) + jit(i, 4), cy + (ry * 0.6) * np.sin(a) + jit(i, 5), 3.9))
    for i in range(6):
        a = (i + 0.25) / 6 * 2 * np.pi; cl.append((cx + (rx * 0.28) * np.cos(a) + jit(i, 6), cy + (ry * 0.28) * np.sin(a) + jit(i, 7), 3.9))
    m = ell(BW, BH, cx, cy, rx - 2.0, ry - 2.0)
    for (ccx, ccy, r) in cl[:20]: m |= ell(BW, BH, ccx, ccy, r, r)
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
def clip_hair(Lh, y):
    Lh = Lh.copy(); Lh[:y] = 0; return Lh
# ======================= WRITE =======================
P = 'paperdoll/'
FA = dict(anchor=[16, 47], canvas=[W, H]); BA = dict(anchor=[24, 77], canvas=[BW, BH])
bodies = [body_front(k) for k in range(6)]; heads = [head_front(n) for n in range(6)]
hairs = [hair_front(n) for n in range(8)]; outfit = outfit_front()
classes = {c: class_front(c) for c in CLASSES}; hats = {c: hat_front(c) for c in CLASSES}
for k in range(6): save(img(bodies[k]), P + f'body_skin_{k+1}.png'); META[P + f'body_skin_{k+1}.png'] = dict(FA, layer=0, notes=f'skin tone {k+1} ({TONES[k][0]}), light->deep. Includes shoes.')
for n in range(6):
    save(img(heads[n]), P + f'head_{n+1}.png')
    META[P + f'head_{n+1}.png'] = dict(FA, layer=3, notes=f'{HEADS[n]} head drawn in REFERENCE skin (tone 3); swap skin via skin_ramps.png. ' + ('Beard uses the grayscale hair keys -> tint with the chosen hair ramp.' if HEADS[n] == 'beard' else ''))
    for k in range(6):
        t = remap_arr(heads[n], tone_map(k))
        if HEADS[n] == 'beard': t = remap_arr(t, hair_map('brown'))
        save(img(t), P + f'tinted/head_{n+1}_skin{k+1}.png')
for n in range(8):
    save(img(hairs[n]), P + f'hair_{n+1}.png'); META[P + f'hair_{n+1}.png'] = dict(FA, layer=4, notes=f'{HAIRS[n]}; GRAYSCALE keys, tint with hair_ramps.png.' + (' (empty = bald)' if n == 0 else ''))
    if n:
        for hn in HAIR_RAMPS: save(img(remap_arr(hairs[n], hair_map(hn))), P + f'tinted/hair_{n+1}_{hn}.png')
save(img(outfit), P + 'outfit_base.png'); META[P + 'outfit_base.png'] = dict(FA, layer=1, notes='shirt in grayscale keys (tint with outfit_ramps.png), shorts fixed brown.')
for on in OUTFIT_RAMPS: save(img(remap_arr(outfit, outfit_map(on))), P + f'tinted/outfit_{on}.png')
for c in CLASSES:
    save(img(classes[c]), P + f'class_{c}.png'); META[P + f'class_{c}.png'] = dict(FA, layer=2, notes='full-colour class outfit overlay (drawn over outfit_base; may also be used without it).')
    save(img(hats[c]), P + f'class_{c}_hat.png'); META[P + f'class_{c}_hat.png'] = dict(FA, layer=5, hair_clip_y=HAT_CLIP_FRONT[c], notes='optional headgear, drawn ABOVE hair. While worn, hide hair rows y < hair_clip_y (e.g. region rect or shader).')
# back / seated
bb = [body_back(k) for k in range(6)]; hb = [hair_back(n) for n in range(8)]; ob = outfit_back(); ch = chair_back()
cb = {c: class_back(c) for c in CLASSES}; hbk = {c: hat_back(c) for c in CLASSES}
for k in range(6): save(img(bb[k]), P + f'back/body_back_skin_{k+1}.png'); META[P + f'back/body_back_skin_{k+1}.png'] = dict(BA, layer=0, notes='seated, seen from behind.')
save(img(ob), P + 'back/outfit_back.png'); META[P + 'back/outfit_back.png'] = dict(BA, layer=1, notes='grayscale shirt keys + brown shorts.')
for n in range(8): save(img(hb[n]), P + f'back/hair_back_{n+1}.png'); META[P + f'back/hair_back_{n+1}.png'] = dict(BA, layer=3, notes=f'{HAIRS[n]} (grayscale keys).')
for c in CLASSES:
    save(img(cb[c]), P + f'back/class_back_{c}.png'); META[P + f'back/class_back_{c}.png'] = dict(BA, layer=2)
    save(img(hbk[c]), P + f'back/class_back_{c}_hat.png'); META[P + f'back/class_back_{c}_hat.png'] = dict(BA, layer=4, hair_clip_y=HAT_CLIP_BACK[c], notes='drawn above hair_back; hide hair rows y < hair_clip_y while worn.')
save(img(ch), P + 'back/chair_back.png'); META[P + 'back/chair_back.png'] = dict(BA, layer=5, notes='chair backrest, drawn LAST (in front of the seated body). Active seat: raise all layers 3px and add a 1px gold #f8d040 outline around the union.')

# ramps (machine-readable, 1px per entry) + previews
def ramp_png(ramps):
    names = list(ramps); n = len(ramps[names[0]]); L = layer(n, len(names))
    for r, nm in enumerate(names):
        for i, cn in enumerate(ramps[nm]): L[r, i] = C[cn] + (255,)
    return L
save(img(ramp_png(HAIR_RAMPS)), P + 'palettes/hair_ramps.png')
save(img(ramp_png(OUTFIT_RAMPS)), P + 'palettes/outfit_ramps.png')
SK = {f'tone{k+1}': [TONES[k][3], TONES[k][2], TONES[k][1], TONES[k][0]] for k in range(6)}
save(img(ramp_png(SK)), P + 'palettes/skin_ramps.png')
META[P + 'palettes/hair_ramps.png'] = dict(notes='4x8 px. Row = colour (black,brown,blonde,ginger,white,blue,pink,green); column i replaces grayscale key i (K1 #46424e, K2 #6c6a76, K3 #9c9ca6, K4 #cfd0d4).')
META[P + 'palettes/outfit_ramps.png'] = dict(notes='3x8 px. Row = colour (white,red,blue,purple,green,yellow,brown,dark); columns replace K2,K3,K4.')
META[P + 'palettes/skin_ramps.png'] = dict(notes='4x6 px. Row = tone 1..6; columns replace the reference-skin keys [blush #ec5a44, detail #8c5836, shadow #b27a4e, base #d89c72] in head_*.png (apply as ONE simultaneous lookup).')

def compose_front(skin, head, hair, hcol, ocol, cls, hat):
    L = layer(W, H)
    over(L, bodies[skin])
    if ocol: over(L, remap_arr(outfit, outfit_map(ocol)))
    if cls: over(L, classes[cls])
    hd = remap_arr(heads[head], tone_map(skin))
    if HEADS[head] == 'beard': hd = remap_arr(hd, hair_map(hcol))
    over(L, hd)
    hl = remap_arr(hairs[hair], hair_map(hcol))
    if cls and hat: hl = clip_hair(hl, HAT_CLIP_FRONT[cls])
    over(L, hl)
    if cls and hat: over(L, hats[cls])
    return L
def compose_back(skin, hair, hcol, ocol, cls, hat, active=False):
    L = layer(BW, BH)
    over(L, bb[skin]); over(L, remap_arr(ob, outfit_map(ocol)))
    if cls: over(L, cb[cls])
    hl = remap_arr(hb[hair], hair_map(hcol))
    if cls and hat: hl = clip_hair(hl, HAT_CLIP_BACK[cls])
    over(L, hl)
    if cls and hat: over(L, hbk[cls])
    over(L, ch)
    if active:
        L2 = layer(BW, BH); L2[:-3] = L[3:]; L = L2; outline(L, C['gold'])
    return L
# hair ramp preview: swatches + tinted heads
HP = layer(4 * 6 + 8 * 34, 8 * 34 // 8 * 1 + 40)
HP = layer(8 * 34, 40 + 34)
for i, hn in enumerate(HAIR_RAMPS):
    for j, cn in enumerate(HAIR_RAMPS[hn]): HP[2:8, i * 34 + 2 + j * 7:i * 34 + 8 + j * 7] = C[cn] + (255,)
    d = compose_front(1, [0, 5, 0, 3, 4, 5, 2, 0][i], [1, 2, 3, 4, 5, 6, 7, 3][i], hn, 'white', None, False)
    over(HP[10:58, i * 34 + 1:i * 34 + 33], d)
save(img(HP), P + 'palettes/hair_ramps_preview.png'); META[P + 'palettes/hair_ramps_preview.png'] = dict(notes='swatches + pre-tinted example per hair colour.')
OP = layer(8 * 34, 58)
for i, on in enumerate(OUTFIT_RAMPS):
    for j, cn in enumerate(OUTFIT_RAMPS[on]): OP[2:8, i * 34 + 2 + j * 7:i * 34 + 8 + j * 7] = C[cn] + (255,)
    over(OP[10:58, i * 34 + 1:i * 34 + 33], compose_front(i % 6, 0, 1, 'brown', on, None, False))
save(img(OP), P + 'palettes/outfit_ramps_preview.png'); META[P + 'palettes/outfit_ramps_preview.png'] = dict(notes='swatches + pre-tinted example per outfit colour.')

# preview grid: 12 random front combos + 4 seated back combos (3x)
rnd = random.Random(7)
cells = []
for i in range(12):
    cls = rnd.choice(CLASSES + [None, None])
    cells.append(compose_front(rnd.randrange(6), rnd.randrange(6), rnd.randrange(8), rnd.choice(list(HAIR_RAMPS)), rnd.choice(list(OUTFIT_RAMPS)), cls, rnd.random() < 0.6))
backs = []
for i in range(4):
    backs.append(compose_back(rnd.randrange(6), rnd.randrange(1, 8), rnd.choice(list(HAIR_RAMPS)), rnd.choice(list(OUTFIT_RAMPS)), CLASSES[i], i % 2 == 0, active=(i == 1)))
cw, chh = 36, 56
G = layer(6 * cw + 4, 2 * chh + 86 + 4); G[:] = C['sand'] + (255,)
for i, d in enumerate(cells):
    x, y = 2 + (i % 6) * cw, 2 + (i // 6) * chh
    G[y:y + chh - 2, x:x + cw - 2] = C['parchment'] + (255,)
    over(G[y + 4:y + 4 + H, x + 1:x + 1 + W], d)
for i, d in enumerate(backs):
    x, y = 2 + i * 55, 2 + 2 * chh
    G[y:y + 84, x:x + 52] = C['tan'] + (255,)
    over(G[y + 3:y + 3 + BH, x + 2:x + 2 + BW], d)
G = np.repeat(np.repeat(G, 3, 0), 3, 1)
save(img(G), 'paperdoll/paperdoll_preview.png')
META['paperdoll/paperdoll_preview.png'] = dict(notes='3x nearest. 12 random front combos built from the layers + 4 seated back combos (2nd one shows the active raise + gold outline).')
# afro back check in all 8 hair colours
AF = layer(8 * 50 + 2, 82); AF[:] = C['tan'] + (255,)
for i, hn in enumerate(HAIR_RAMPS):
    over(AF[2:2 + BH, 2 + i * 50:2 + i * 50 + BW], compose_back(i % 6, 6, hn, 'white', None, False))
save(img(AF), P + 'palettes/afro_back_check.png'); META[P + 'palettes/afro_back_check.png'] = dict(notes='QA: back-view afro (hair_back_7) in all 8 hair ramps on the seated body.')
# portrait sample strip
PS = layer(6 * 22, 22)
for i in range(6):
    d = compose_front(i, i, [1, 2, 3, 4, 6, 7][i], list(HAIR_RAMPS)[i], 'blue', None, False)
    over(PS[1:21, i * 22 + 1:i * 22 + 21], d[8:28, 6:26])
save(img(PS), 'paperdoll/portrait_crop_examples.png'); META['paperdoll/portrait_crop_examples.png'] = dict(portrait_crop_rect=[6, 8, 20, 20], notes='examples of the 20x20 portrait crop taken from the composed front doll.')
json.dump(dict(meta=META, hair_ramps=HAIR_RAMPS, outfit_ramps=OUTFIT_RAMPS, tones=TONES), open('/workspace/paladins-art/phase0/tools/_work/meta_doll.json', 'w'), indent=1)
import pickle
np.save('/workspace/paladins-art/phase0/tools/_work/doll_samples.npy', np.stack([compose_front(k % 6, [0, 3, 5, 1][k], [2, 4, 6, 3][k], ['brown', 'blonde', 'black', 'ginger'][k], 'white', CLASSES[k], True) for k in range(4)]))
np.save('/workspace/paladins-art/phase0/tools/_work/doll_backs.npy', np.stack([compose_back(k + 1, [1, 4, 3, 6][k], ['brown', 'blonde', 'black', 'ginger'][k], 'white', CLASSES[k], True) for k in range(4)]))
print('ok', len(META))
