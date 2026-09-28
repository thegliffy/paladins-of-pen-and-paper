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
        from PIL import ImageDraw as _D
        im_ = Image.new('L', (BW, BH)); dr = _D.Draw(im_)
        dr.polygon([(10, 26), (37, 26), (38, 36), (36, 44), (35, 49), (32, 47), (29, 51), (26, 48), (23.5, 52), (21, 48), (18, 51), (15, 47), (12, 49), (11, 44), (9, 36)], fill=1)
        m = E(15.5, 17.2, 9.8, 8.9) & YB(22) | (np.array(im_) > 0)
        hs(m)
        for p0, p1 in (((14, 34), (15, 47)), ((19, 36), (20, 49)), ((28, 36), (27, 49)), ((33, 34), (32, 46)), ((23, 40), (23, 50))):
            paint(L, pts(BW, BH, [(int(round(p0[0] + (p1[0] - p0[0]) * t / 12)), int(round(p0[1] + (p1[1] - p0[1]) * t / 12))) for t in range(13)]) & m & ~e_bot(m), K2)
        paint(L, pts(BW, BH, [(13, y) for y in range(30, 38)] + [(12, y) for y in range(38, 42)]) & m, K4)
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
    'barbarian': dict(skin=3, head=3, hair=8, hair_color='ginger', outfit=None,     hat=True),
    'druid':     dict(skin=6, head=6, hair=1, hair_color='white',  outfit='green',  hat=True)}

# ======================= v4 back/seated polish: native 48x78 polygons, sloped shoulders, arms, tapered robes =======================
from PIL import ImageDraw as _ID
def M(pts_, w=BW, h=BH):
    im = Image.new('L', (w, h), 0); _ID.Draw(im).polygon([(float(x), float(y)) for x, y in pts_], fill=1); return np.array(im) > 0
def MX(pts_): return M([(47 - x, y) for x, y in pts_])          # mirror across the seat centre line
def LNn(p, w=1):
    im = Image.new('L', (BW, BH), 0); _ID.Draw(im).line([tuple(map(float, q)) for q in p], fill=1, width=w); return np.array(im) > 0
def Ell(cx, cy, rx, ry): return ell(BW, BH, cx, cy, rx, ry)
def shade3(L, m, base, dark, light, spine=False, rim=True, dark2=None):
    """base + 2px shadow on the right/bottom, 1px lit rim on the left/top, optional darker spine band."""
    paint(L, m, base)
    r1 = e_right(m) | e_bot(m); r2 = e_right(m & ~r1)
    paint(L, r1 | r2, dark)
    if rim: paint(L, (e_left(m) | e_top(m)) & ~r1, light)
    if spine: paint(L, m & ((bxs == 23) | (bxs == 24)) & ~e_top(m), dark)
    if dark2 is not None: paint(L, e_right(m) & (bys > bys[m].min() + 3) if m.any() else m, dark2)
def folds(L, m, lines, dark, light=None):
    for p in lines:
        ln = LNn(p) & m & ~e_bot(m); paint(L, ln, dark)
        if light is not None: paint(L, sh(ln, -1, 0) & m & ~ln & ~e_left(m), light)
def part(L, fn):
    """draw a sub-part on its own layer, outline it, and stack it (keeps internal outlines between parts)."""
    Q = layer(BW, BH); fn(Q); outline(Q); over(L, Q)
# --- shared silhouettes (all layers use these, so every class fits every body) ---
NECK = M([(20, 35), (27, 35), (27, 42), (20, 42)])
TORSO = M([(18, 40), (29, 40), (35, 42), (38, 44), (38, 48), (35, 51), (33, 57), (34, 60), (13, 60), (14, 57), (12, 51), (9, 48), (9, 44), (12, 42)])
ARM_UP_L = M([(8, 44), (12, 45), (13, 52), (12, 56), (10, 58), (6, 58), (5, 54), (6, 47)])
FORE_L = M([(6, 55), (10, 54), (13, 52), (16, 53), (15, 56), (11, 59), (7, 59)])
HAND_L = Ell(16, 54.5, 1.6, 1.6)
ARM_UP_R, FORE_R, HAND_R = [np.fliplr(a) for a in (ARM_UP_L, FORE_L, HAND_L)]
HIPS = M([(13, 57), (34, 57), (36, 62), (35, 65), (12, 65), (11, 62)])
def robe_mask(hem_y=67, flare=19.5, top=40):
    """tapered robe: sloped shoulders -> narrow waist -> flared skirt draped over the seat, scalloped hem."""
    R_ = [(29, top), (35, 42), (38, 44), (38, 48), (35, 51), (33, 56), (35, 60), (23.5 + flare - 1, hem_y - 3), (23.5 + flare, hem_y - 1)]
    hem = []
    xs_ = np.linspace(23.5 + flare, 23.5 - flare, 9)
    for k, x in enumerate(xs_): hem.append((x, hem_y + (1 if k % 2 else -0.5)))
    Lh = [(47 - x, y) for x, y in reversed(R_)]
    return M([(18, top)] + [(x, y) for x, y in R_] + hem + Lh)
def sleeve_L(bell=True):
    return M([(8, 44), (12, 45), (13, 51), (15, 53), (16, 56), (11, 60), (4, 60), (4, 56), (6, 47)]) if bell else ARM_UP_L | FORE_L
def sleeve_R(bell=True): return np.fliplr(sleeve_L(bell))
def body_back(k):
    b, s, d, bl = TONES[k]; L = layer(BW, BH)
    head = E(15.5, 17.6, 8.7, 8.2); ears = R(6, 17, 6, 19) | R(25, 17, 25, 19)
    part(L, lambda Q: (shade3(Q, HIPS, C['wood'], C['wood_dk'], C['wood_lt'])))
    def torso(Q):
        shade3(Q, TORSO | NECK, C[b], C[s], C[b], spine=True)
        paint(Q, NECK & (bys >= 40), C[s])
        paint(Q, LNn([(16, 46), (19, 48)]) | LNn([(31, 46), (28, 48)]), C[s])          # shoulder blades
        paint(Q, LNn([(12, 43), (17, 41)]) & TORSO, C[bl] if False else C[b])
    part(L, torso)
    for up, fo, hd in ((ARM_UP_L, FORE_L, HAND_L), (ARM_UP_R, FORE_R, HAND_R)):
        part(L, lambda Q, fo=fo, hd=hd: (shade3(Q, fo | hd, C[b], C[s], C[b])))
        part(L, lambda Q, up=up: shade3(Q, up, C[b], C[s], C[b]))
    part(L, lambda Q: (shade3(Q, head, C[b], C[s], C[b]), shade3(Q, ears, C[b], C[s], C[b]), paint(Q, P1([(6, 18), (25, 18)]), C[s])))
    return L
def outfit_back():
    L = layer(BW, BH)
    part(L, lambda Q: (shade3(Q, HIPS, C['wood'], C['wood_dk'], C['wood_lt']), paint(Q, HIPS & (bys == 57), C['wood_dk'])))
    def shirt(Q):
        m = TORSO & (bys >= 41); shade3(Q, m, K3, K2, K4, spine=True)
        folds(Q, m, [[(17, 50), (16, 58)], [(30, 50), (31, 58)], [(20, 44), (21, 48)]], K2, K4)
        paint(Q, m & (bys == 41), K4)
    part(L, shirt)
    for up, fo in ((ARM_UP_L, FORE_L), (ARM_UP_R, FORE_R)):
        part(L, lambda Q, fo=fo: (shade3(Q, fo, K3, K2, K4), paint(Q, fo & (bxs >= 14) & (bxs <= 33) & e_left(fo) if False else z(BW, BH), K2)))
        part(L, lambda Q, up=up: (shade3(Q, up, K3, K2, K4), folds(Q, up, [[(8, 50), (10, 53)]] if up is ARM_UP_L else [[(39, 50), (37, 53)]], K2)))
    return L
def chair_back():
    L = layer(BW, BH)
    wood = lambda Q, m: shade3(Q, m, C['wood'], C['wood_dk'], C['wood_lt'])
    part(L, lambda Q: (wood(Q, M([(8, 65), (39, 65), (40, 68), (7, 68)])), [wood(Q, R_) for R_ in (M([(8, 68), (10, 68), (10, 75), (8, 75)]), M([(37, 68), (39, 68), (39, 75), (37, 75)]))]))
    def back(Q):
        for x in (12, 33): wood(Q, M([(x, 62), (x + 2, 62), (x + 2, 77), (x, 77)]))
        wood(Q, M([(15, 71), (32, 71), (32, 72), (15, 72)]))
        crest = M([(10, 62), (12, 60), (35, 60), (37, 62), (37, 64), (10, 64)]); wood(Q, crest)
        paint(Q, LNn([(14, 63), (33, 63)]) & crest, C['wood_dk'])
    part(L, back)
    return L
# ---------- class layers ----------
def hem_drape(Q, base, dark, light, hem_col=None, y0=60, y1=68, flare=19.5):
    m = robe_mask(y1, flare) & (bys >= y0); shade3(Q, m, base, dark, light)
    folds(Q, m, [[(14, y0), (9, y1)], [(19, y0), (17, y1)], [(28, y0), (30, y1)], [(33, y0), (38, y1)]], dark, light)
    if hem_col: paint(Q, e_bot(m) | e_bot(m & ~e_bot(m)), C[hem_col])
    return m
def robe_body(Q, base, dark, light, hem_col, trim=None, hem_y=68, flare=19.5):
    m = robe_mask(hem_y, flare); shade3(Q, m, C[base], C[dark], C[light], spine=True)
    folds(Q, m, [[(18, 52), (12, hem_y)], [(29, 52), (35, hem_y)], [(21, 57), (19, hem_y)], [(26, 57), (28, hem_y)]], C[dark], C[light])
    paint(Q, e_bot(m) | e_bot(m & ~e_bot(m)), C[hem_col])
    if trim: paint(Q, m & (bys >= 40) & (bys <= 41), C[trim])
    return m
def belt(Q, y, col, dark, knot=None):
    m = TORSO & (bys >= y) & (bys <= y + 1) | (robe_mask() & (bys >= y) & (bys <= y + 1) & (bxs >= 13) & (bxs <= 34))
    paint(Q, m, C[col]); paint(Q, e_right(m) | (m & (bys == y + 1) & (bxs % 4 == 0)), C[dark])
    if knot is not None: paint(Q, knot, C[col])
def sleeves(L, base, dark, light, cuff=None, bell=True):
    for sl in (sleeve_L(bell), sleeve_R(bell)):
        def f(Q, sl=sl):
            shade3(Q, sl, C[base], C[dark], C[light])
            folds(Q, sl, [[(7, 49), (6, 56)], [(10, 50), (11, 57)]] if sl[50, 5] else [[(40, 49), (41, 56)], [(37, 50), (36, 57)]], C[dark])
            if cuff: paint(Q, sl & (bys >= 59) | (e_bot(sl) & (bys >= 57)), C[cuff])
        part(L, f)
def class_back(c):
    L = layer(BW, BH)
    if c == 'paladin':
        def plate(Q):
            m = TORSO | HIPS & (bys <= 60); shade3(Q, m, C['silver'], C['gray'], C['mist'], spine=True)
            for y in (47, 52, 57): paint(Q, LNn([(12, y), (35, y)]) & m, C['gray'])
            paint(Q, m & (bys == 48) | m & (bys == 53), C['mist'])
        part(L, plate)
        part(L, lambda Q: (lambda m: (shade3(Q, m, C['white'], C['mist'], C['white'], spine=True), folds(Q, m, [[(20, 46), (15, 67)], [(27, 46), (32, 67)], [(23, 50), (23, 67)]], C['silver'], C['white']),
            paint(Q, (R(15, 31, 16, 36) | R(13, 32, 18, 33)) & m, C['gold']), paint(Q, e_bot(m), C['gold'])))(M([(17, 42), (30, 42), (33, 50), (36, 60), (38, 66), (34, 68), (29, 66), (23.5, 68), (18, 66), (13, 68), (9, 66), (11, 60), (14, 50)])))
        for up, fo in ((ARM_UP_L, FORE_L), (ARM_UP_R, FORE_R)):
            part(L, lambda Q, fo=fo: shade3(Q, fo, C['silver'], C['gray'], C['mist']))
            part(L, lambda Q, up=up: (shade3(Q, up, C['silver'], C['gray'], C['mist']), paint(Q, up & (bys == 52), C['gray'])))
        for cx in (9.5, 37.5):
            part(L, lambda Q, cx=cx: (lambda m: (shade3(Q, m, C['silver'], C['gray'], C['mist']), paint(Q, m & (bys == int(46.5)), C['gray']), paint(Q, m & (bys == 45) & ~e_left(m), C['white'])))(Ell(cx, 45.5, 5.2, 4.2) & (bys <= 48)))
        part(L, lambda Q: (paint(Q, M([(4, 55), (6, 55), (6, 69), (4, 69)]), C['silver']), paint(Q, M([(5, 55), (6, 55), (6, 69), (5, 69)]), C['gray']), paint(Q, M([(2, 53), (8, 53), (8, 54), (2, 54)]), C['gold']), paint(Q, M([(4, 50), (6, 50), (6, 52), (4, 52)]), C['wood_dk'])))  # sword at the left hip
    elif c == 'wizard':
        part(L, lambda Q: robe_body(Q, 'blue', 'blue_dk', 'sky', 'gold', trim='gold'))
        part(L, lambda Q: belt(Q, 55, 'gold', 'amber', knot=M([(30, 56), (32, 56), (33, 61), (31, 61)])))
        sleeves(L, 'blue', 'blue_dk', 'sky', cuff='gold')
        part(L, lambda Q: (paint(Q, M([(41, 26), (43, 26), (43, 77), (41, 77)]), C['wood']), paint(Q, M([(43, 28), (43, 28), (43, 77), (43, 77)]) | (bxs == 43) & (bys >= 27), C['wood_dk']),
            shade3(Q, Ell(42, 23.5, 3.2, 3.2), C['violet'], C['plum'], C['sky_lt']), paint(Q, P1([(27.6, 15)]), C['white'])))
        part(L, lambda Q: shade3(Q, Ell(40.5, 55.5, 2.0, 2.0), C['skin3'], C['skin4'], C['skin2']))    # hand on the staff
    elif c == 'ranger':
        part(L, lambda Q: (lambda m: (shade3(Q, m, C['leaf'], C['leaf_dk'], C['grass'], spine=True), folds(Q, m, [[(19, 46), (13, 67)], [(28, 46), (34, 67)], [(23, 50), (22, 67)]], C['leaf_dk'], C['grass']), paint(Q, e_bot(m), C['pine'])))(robe_mask(67, 18.5)))
        part(L, lambda Q: belt(Q, 56, 'wood', 'wood_dk', knot=M([(15, 57), (18, 57), (18, 61), (15, 61)])))
        sleeves(L, 'leaf_dk', 'pine', 'leaf', bell=False)
        part(L, lambda Q: (shade3(Q, M([(27, 32), (32, 34), (21, 58), (16, 56)]), C['wood'], C['wood_dk'], C['wood_lt']), paint(Q, LNn([(19, 55), (29, 34)]), C['wood_dk'])))   # quiver
        part(L, lambda Q: (paint(Q, P1([(19, 21), (20, 20), (21, 21), (18, 20)]), C['white']), paint(Q, P1([(20, 21)]), C['red'])))
        part(L, lambda Q: (paint(Q, LNn([(5, 30), (3, 40), (3, 54), (6, 66)], 2), C['wood_lt']), paint(Q, LNn([(6, 30), (6, 66)]), C['cream'])))     # bow at the left side
        part(L, lambda Q: shade3(Q, Ell(5, 55.5, 2.0, 2.0), C['skin3'], C['skin4'], C['skin2']))
    elif c == 'bard':
        def doub(Q):
            m = TORSO; shade3(Q, m, C['red'], C['red_dk'], C['coral'], spine=True)
            for x in (16, 31): paint(Q, LNn([(x, 43), (x + (1 if x > 23 else -1), 58)]) & m, C['red_dk'])
            paint(Q, LNn([(11, 44), (36, 58)], 2) & m, C['violet']); paint(Q, LNn([(11, 43), (36, 57)]) & m, C['sky_lt'])       # sash
        part(L, doub)
        part(L, lambda Q: (shade3(Q, HIPS | M([(12, 60), (35, 60), (38, 66), (9, 66)]), C['violet'], C['plum'], C['violet']), folds(Q, M([(12, 60), (35, 60), (38, 66), (9, 66)]), [[(17, 60), (15, 66)], [(30, 60), (32, 66)]], C['plum'])))
        for up, fo in ((ARM_UP_L, FORE_L), (ARM_UP_R, FORE_R)):
            part(L, lambda Q, fo=fo: shade3(Q, fo, C['red'], C['red_dk'], C['coral']))
            part(L, lambda Q, up=up: (shade3(Q, up, C['cream'], C['sand'], C['white']), paint(Q, up & ((bxs % 3) == 0) & ~e_bot(up) & ~e_top(up), C['red'])))
        part(L, lambda Q: (shade3(Q, Ell(39, 57, 5.2, 6.2), C['tan'], C['wood_lt'], C['sand']), paint(Q, Ell(38.5, 56, 1.4, 1.4), C['wood_dk'])))
        part(L, lambda Q: (paint(Q, LNn([(40, 51), (42, 32)], 2), C['wood_dk']), shade3(Q, M([(41, 27), (44, 27), (44, 32), (41, 32)]), C['wood'], C['wood_dk'], C['wood_lt']), paint(Q, P1([(27, 18), (29, 20)]), C['gold'])))
    elif c == 'cleric':
        part(L, lambda Q: robe_body(Q, 'white', 'mist', 'white', 'gold'))
        part(L, lambda Q: (lambda m: (paint(Q, m, C['gold']), paint(Q, e_right(m), C['amber'])))(LNn([(15, 42), (18, 56)], 2) | LNn([(32, 42), (29, 56)], 2)))  # stole bands
        part(L, lambda Q: (lambda m: (paint(Q, m, C['gold']), paint(Q, e_right(m) | e_bot(m), C['amber'])))(M([(23, 44), (24, 44), (24, 55), (23, 55)]) | M([(20, 47), (27, 47), (27, 48), (20, 48)])))
        part(L, lambda Q: belt(Q, 56, 'cream', 'sand', knot=LNn([(16, 57), (15, 64)]) | LNn([(17, 57), (17, 63)])))
        sleeves(L, 'white', 'mist', 'white', cuff='gold')
    elif c == 'rogue':
        def jerk(Q):
            m = TORSO; shade3(Q, m, C['wood'], C['wood_dk'], C['wood_lt'], spine=True)
            for y in (50, 54): paint(Q, LNn([(14, y), (33, y)]) & m, C['wood_dk'])
            paint(Q, P1([(12, 34), (19, 34), (12, 36), (19, 36)]), C['silver'])
        part(L, jerk)
        part(L, lambda Q: (lambda m: (shade3(Q, m, C['slate'], C['ink'], C['gray'], spine=True), folds(Q, m, [[(18, 44), (15, 50)], [(29, 44), (32, 50)], [(23.5, 45), (23.5, 51)]], C['ink'], C['gray'])))(M([(17, 40), (30, 40), (37, 43), (39, 47), (35, 50), (30, 48), (23.5, 52), (17, 48), (12, 50), (8, 47), (10, 43)])))
        part(L, lambda Q: (shade3(Q, HIPS, C['ink'], C['outline'], C['slate'])))
        part(L, lambda Q: belt(Q, 56, 'wood_dk', 'bark'))
        part(L, lambda Q: (shade3(Q, M([(12, 55), (16, 55), (16, 60), (12, 60)]), C['wood'], C['wood_dk'], C['wood_lt']), shade3(Q, M([(31, 55), (35, 55), (35, 60), (31, 60)]), C['wood'], C['wood_dk'], C['wood_lt'])))  # pouches
        sleeves(L, 'wood_dk', 'bark', 'wood', bell=False)
        for p0, p1, h0 in (((15, 62), (31, 50), (32, 49)), ((32, 62), (16, 50), (15, 49))):
            part(L, lambda Q, p0=p0, p1=p1, h0=h0: (paint(Q, LNn([p0, p1], 2), C['wood_dk']), paint(Q, LNn([p1, h0], 2), C['silver']), paint(Q, P1([(p1[0] / 1.5 - 0.3, p1[1] / 1.5 + 0.7)]) & z(BW, BH), C['gold'])))
    elif c == 'barbarian':
        part(L, lambda Q: (lambda m: (shade3(Q, m, C['wood_lt'], C['wood'], C['tan']), paint(Q, m & (bxs % 3 == 0) & ~e_top(m), C['wood']), paint(Q, e_top(m), C['wood_dk'])))(M([(11, 58), (36, 58), (39, 66), (35, 64), (31, 67), (27, 64), (23, 67), (19, 64), (15, 67), (11, 64), (8, 66)])))   # fur kilt
        part(L, lambda Q: (paint(Q, LNn([(12, 44), (34, 58)], 2), C['wood_dk']), paint(Q, LNn([(12, 43), (34, 57)]) , C['wood'])))                      # harness strap
        part(L, lambda Q: (lambda m: (shade3(Q, m, C['tan'], C['wood_lt'], C['sand']), paint(Q, m & (((bxs + bys) % 4) == 0) & ~e_bot(m), C['wood_lt'])))(M([(15, 39), (32, 39), (38, 43), (39, 47), (36, 46), (34, 49), (31, 46), (27, 49), (23.5, 46), (20, 49), (16, 46), (13, 49), (11, 46), (8, 47), (9, 43)])))
        for fo in (FORE_L, FORE_R): part(L, lambda Q, fo=fo: (paint(Q, fo & (bys >= 55), C['wood']), paint(Q, e_bot(fo) & (bys >= 55), C['wood_dk'])))
        part(L, lambda Q: (paint(Q, LNn([(11, 66), (35, 30)], 2), C['wood']), paint(Q, LNn([(12, 66), (36, 30)]), C['wood_dk'])))
        part(L, lambda Q: (lambda m: (shade3(Q, m, C['silver'], C['gray'], C['mist']), paint(Q, e_right(m) & (bxs >= 40), C['white'])))(M([(33, 28), (38, 22), (43, 24), (44, 30), (42, 36), (37, 34), (35, 32)])))
    elif c == 'druid':
        part(L, lambda Q: robe_body(Q, 'leaf_dk', 'pine', 'leaf', 'wood', flare=20.5))
        part(L, lambda Q: (lambda m: (paint(Q, m, C['wood']), paint(Q, e_right(m) | e_bot(m), C['wood_dk'])))(M([(9, 44), (38, 44), (37, 47), (10, 47)]) & robe_mask()))
        for k, (cx, cy) in enumerate([(11, 44), (16, 43), (21, 44), (26, 44), (31, 43), (36, 44), (13, 47), (34, 47), (23.5, 47)]):
            part(L, lambda Q, cx=cx, cy=cy, k=k: (lambda m: (paint(Q, m, C['lime'] if k % 3 == 0 else C['leaf']), paint(Q, e_right(m) | e_bot(m), C['leaf_dk'] if k % 3 else C['grass'])))(Ell(cx, cy, 2.6, 2.0)))
        part(L, lambda Q: belt(Q, 56, 'leaf', 'leaf_dk', knot=M([(29, 57), (31, 57), (32, 62), (30, 62)])))
        sleeves(L, 'leaf_dk', 'pine', 'leaf', cuff='wood')
        part(L, lambda Q: (paint(Q, LNn([(5, 77), (5, 44), (4, 34), (6, 26)], 2), C['wood']), paint(Q, LNn([(6, 77), (6, 44)]), C['wood_dk'])))
        part(L, lambda Q: (lambda m: (shade3(Q, m, C['lime'], C['leaf'], C['cream'])))(Ell(4.5, 24, 3.2, 2.6) | Ell(8, 26, 2.2, 1.8)))
        part(L, lambda Q: shade3(Q, Ell(6, 55.5, 2.0, 2.0), C['skin3'], C['skin4'], C['skin2']))
    return L
_hb3 = hat_back
def hat_back(c):
    if c not in ('ranger', 'rogue'): return _hb3(c)
    base, dark, light, deep = (('leaf', 'leaf_dk', 'grass', 'pine') if c == 'ranger' else ('slate', 'ink', 'gray', 'outline'))
    L = layer(BW, BH)
    hood = E(15.5, 17.4, 9.4, 9.0) & (bys <= 38)
    cowl = (M([(15, 33), (32, 33), (36, 40), (38, 44), (33, 44), (29, 47), (23.5, 50), (18, 47), (14, 44), (9, 44), (11, 40)]) if c == 'ranger' else
            M([(16, 33), (31, 33), (33, 38), (31, 41), (27, 43), (23.5, 45), (20, 43), (16, 41), (14, 38)]))
    tip = M([(24, 4), (27, 3), (26, 8), (22, 10)]) if c == 'rogue' else M([(22, 8), (25, 6), (26, 10), (23, 11)])
    m = hood | cowl | tip
    shade3(L, m, C[base], C[dark], C[light])
    paint(L, pts(BW, BH, [(23, y) for y in range(12, 49)]) & m & ~e_bot(m), C[dark])          # centre seam / spine band
    folds(L, m, [[(17, 34), (14, 43)], [(30, 34), (33, 43)], [(20, 38), (19, 46)], [(27, 38), (28, 46)]], C[dark], C[light])
    paint(L, LNn([(11, 16), (9, 30)]) & m & ~e_left(m), C[light])
    paint(L, e_bot(cowl) & m, C[deep])
    outline(L); return L

HAT_CLIP_FRONT = {'paladin': 16, 'wizard': 14, 'ranger': 17, 'bard': 14, 'cleric': 13, 'rogue': 17, 'barbarian': 14, 'druid': 0}
HAT_CLIP_BACK = {'paladin': _s(22), 'wizard': _s(14), 'ranger': 60, 'bard': _s(14), 'cleric': _s(13), 'rogue': 60, 'barbarian': _s(20), 'druid': 0}
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
    over(L, bb[skin])
    if ocol: over(L, remap_arr(ob, outfit_map(ocol)))
    if cls: over(L, cb[cls])
    hl = remap_arr(hb[hair], hair_map(hcol))
    if cls and hat: hl = clip_hair(hl, HAT_CLIP_BACK[cls])
    over(L, hl)
    if cls and hat: over(L, hbk[cls])
    over(L, ch)
    if active:
        L2 = layer(BW, BH); L2[:-3] = L[3:]; L = L2; outline(L, C['gold'])
    return L
# ---------- party seats = composed back dolls (v3) ----------
def seat(c, active):
    d = SEAT_DEFAULTS[c]
    return compose_back(d['skin'] - 1, d['hair'] - 1, d['hair_color'], d['outfit'], c, d['hat'], active=active)
for c in CLASSES:
    for st, act in (('idle', False), ('active', True)):
        save(img(seat(c, act)), f'party/seat_{c}_{st}.png')
        META[f'party/seat_{c}_{st}.png'] = dict(anchor=[24, 77], canvas=[BW, BH], composed_from='paperdoll/back/* (see manifest paperdoll.seat_recipe)', defaults=SEAT_DEFAULTS[c],
            notes='48x78 seat built from the back-view paperdoll layers.' + (' Active: all layers raised 3px + 1px gold #f8d040 outline around the union.' if act else ''))
def front_default(c):
    d = SEAT_DEFAULTS[c]
    return compose_front(d['skin'] - 1, d['head'] - 1, d['hair'] - 1, d['hair_color'], d['outfit'], c, d['hat'])
CC = layer(8 * 50 + 2, 48 + 82 + 6); CC[:] = C['tan'] + (255,)
for i, c in enumerate(CLASSES):
    over(CC[2:50, 2 + i * 50 + 8:2 + i * 50 + 40], front_default(c)); over(CC[54:54 + BH, 2 + i * 50:2 + i * 50 + BW], seat(c, i == 0))
save(img(CC), P + 'palettes/classes_check.png'); META[P + 'palettes/classes_check.png'] = dict(notes='QA: all 8 classes, default front doll (top) and composed seat (bottom; paladin active).')
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
json.dump(dict(meta=META, hair_ramps=HAIR_RAMPS, outfit_ramps=OUTFIT_RAMPS, tones=TONES, seat_defaults=SEAT_DEFAULTS), open('/workspace/paladins-art/phase0/tools/_work/meta_doll.json', 'w'), indent=1)
import pickle
np.save('/workspace/paladins-art/phase0/tools/_work/doll_samples.npy', np.stack([compose_front(k % 6, [0, 3, 5, 1][k], [2, 4, 6, 3][k], ['brown', 'blonde', 'black', 'ginger'][k], 'white', CLASSES[k], True) for k in range(4)]))
np.save('/workspace/paladins-art/phase0/tools/_work/doll_backs.npy', np.stack([compose_back(k + 1, [1, 4, 3, 6][k], ['brown', 'blonde', 'black', 'ginger'][k], 'white', CLASSES[k], True) for k in range(4)]))
print('ok', len(META))
