"""Item icons (16x16) for the 40 items in data/items.json. Chunky flat style, dark outline, pack palette."""
import numpy as np
from regionlib import Sprite, E, P, R, LN
N = 16
def S(): return Sprite(N, N)
def e(*a, **k): return E(N, N, *a, **k)
def p(pts): return P(N, N, pts)
def r(*a): return R(N, N, *a)
def ln(*a): return LN(N, N, *a)
def pm(pts):
    m = np.zeros((N, N), bool)
    for x, y in pts:
        if 0 <= x < N and 0 <= y < N: m[y, x] = True
    return m
def diag(x0, y0, L, w=2):            # 45-degree run up-right from (x0, y0), w px thick (horizontal)
    return pm([(x0 + i + k, y0 - i) for i in range(L) for k in range(w)])
STEEL = ['gray', 'silver', 'mist', 'white']; IRON = ['slate', 'gray', 'silver']; WOOD = ['wood_dk', 'wood', 'wood_lt']
GOLD = ['orange', 'amber', 'gold', 'cream']; LEATHER = ['bark', 'wood_dk', 'wood']

def sword(s, blade, blade_len, x0=2, y0=13, guard=IRON, grip=LEATHER, w=2, pommel=IRON, guard_len=2):
    s.add(diag(x0 + 3, y0 - 3, blade_len, w), blade, rim=True)                                  # blade
    s.add(pm([(x0 + 1 + i, y0 - 3 - guard_len + 1 + i + (0)) for i in range(0)]) | pm([(x0 + 2 - k, y0 - 4 - k) for k in range(guard_len)] + [(x0 + 4 + k, y0 - 2 + k) for k in range(guard_len)] + [(x0 + 3, y0 - 3)]), guard, rim=True)   # crossguard
    s.add(pm([(x0 + 1, y0 - 1), (x0 + 2, y0 - 2)]), grip, rim=True)
    s.add(pm([(x0, y0), (x0, y0 - 1), (x0 + 1, y0)]), pommel, rim=True)

def oath_blade():
    s = S(); sword(s, STEEL, 10); s.px([(7 + i, 8 - i) for i in range(4)], 'gold'); return s          # gold vow line in the fuller
def kiln_sword():
    s = S(); sword(s, ['blue_dk', 'sky', 'mist', 'white'], 11, guard=['red_dk', 'red', 'coral'], grip=['red_dk', 'red'], w=3, pommel=['red_dk', 'red', 'coral'], guard_len=3)
    s.px([(6 + i, 10 - i) for i in range(8)], 'sky'); return s                                    # blued edge
def sunbrand():
    s = S()
    s.add(diag(4, 11, 11, 3) | pm([(14, 1), (14, 2)]), ['amber', 'gold', 'cream', 'white'], rim=True)
    s.add(pm([(1 + k, 8 + k) for k in range(0)] + [(2, 8), (3, 9), (4, 10), (5, 11), (6, 12), (7, 13), (3, 8), (6, 13)]), ['orange', 'amber', 'gold'], rim=True)  # long guard
    s.add(pm([(2, 12), (3, 11), (1, 13), (2, 13)]), LEATHER, rim=True)
    s.add(pm([(0, 14), (1, 14), (0, 15)]) & (np.ones((N, N), bool)), GOLD, rim=True)
    s.px([(4, 10)], 'red'); s.px([(8, 7 - 0), (11, 4)], 'white')                                   # sun gem + glints
    return s
def chapel_mace():
    s = S()
    s.add(diag(2, 13, 7, 2), WOOD, rim=True)
    s.add(e(10.5, 5.5, 3.6, 3.6), STEEL, rim=True)
    s.add(pm([(10, 1), (11, 1), (14, 5), (14, 6), (6, 5), (7, 5), (10, 9), (11, 9)]), IRON, rim=True)   # flanges
    s.px([(10, 4), (10, 5), (10, 6), (9, 5), (11, 5)], 'gold')                                    # chapel cross
    s.add(pm([(1, 14), (2, 14), (1, 13)]), IRON, rim=True)
    return s
def reed_staff():
    s = S()
    s.add(diag(1, 14, 12, 2), ['wood', 'tan', 'sand'], rim=True)
    s.px([(4, 11), (5, 11), (8, 7), (9, 7)], 'wood_dk')                                           # reed nodes
    s.px([(10, 4), (11, 4), (11, 3), (12, 3)], 'orange'); s.px([(11, 4), (12, 3)], 'amber')      # copper wire
    s.add(pm([(13, 0), (14, 0), (14, 1), (15, 1), (12, 0)]), ['leaf_dk', 'leaf', 'grass'], rim=True)
    return s
def sap_crook():
    s = S()
    s.add(diag(1, 14, 8, 2), WOOD, rim=True)
    s.add(pm([(9, 6), (10, 5), (10, 4), (10, 3), (11, 2), (12, 1), (13, 1), (14, 2), (14, 3), (13, 4), (11, 3), (9, 5), (13, 2)]), WOOD, rim=True)   # hook
    s.add(pm([(5, 8), (4, 7), (5, 7), (3, 7)]), ['leaf_dk', 'leaf', 'lime'], rim=True)            # sprout leaf
    s.px([(13, 5), (13, 6)], 'amber'); s.px([(13, 5)], 'gold')                                    # sap drip
    return s
def bow(s, limb, string, recurve=False, thorns=False):
    th = np.linspace(-1.25, 1.25, 60); m = np.zeros((N, N), bool)
    for w_ in (0.0, 0.7, 1.3):
        xs = 3.5 + (6.0 - w_) * np.cos(th); ys = 7.5 + 6.6 * np.sin(th)
        for x, y in zip(xs, ys): m[int(np.clip(round(y), 0, 15)), int(np.clip(round(x), 0, 15))] = True
    if recurve: m |= pm([(3, 1), (2, 0), (3, 14), (2, 15)])
    s.add(m, limb, rim=True)
    s.px([(4, y) for y in range(2, 14)], string)
    if thorns: s.px([(10, 4), (11, 8), (10, 11), (7, 1), (7, 14)], 'bark')
def thorn_bow():
    s = S(); bow(s, WOOD, 'cream', thorns=True); return s
def marsh_bow():
    s = S(); bow(s, ['pine_dk', 'pine', 'leaf_dk', 'leaf'], 'sky_lt', recurve=True)
    s.add(r(8, 6, 11, 10), ['wood_dk', 'wood', 'wood_lt'], rim=True)                              # wrapped grip
    s.px([(9, 7), (9, 8)], 'amber'); s.px([(12, 3), (13, 4), (12, 12), (13, 11)], 'sky_lt')        # singing string sparks
    return s
def dagger(s, blade, L, grip=LEATHER, guard=IRON, x0=4, y0=11, w=2):
    s.add(diag(x0 + 2, y0 - 2, L, w), blade, rim=True)
    s.add(pm([(x0 + 1, y0 - 3), (x0 + 2, y0 - 2), (x0 + 3, y0 - 1)]), guard, rim=True)
    s.add(pm([(x0, y0 - 1), (x0 + 1, y0), (x0, y0), (x0 - 1, y0 + 1), (x0, y0 + 1)]), grip, rim=True)
def pocket_knife():
    s = S(); dagger(s, STEEL, 5, grip=WOOD, x0=4, y0=11)
    s.add(pm([(1, 14), (2, 13), (3, 12), (2, 14), (3, 13), (1, 13)]), WOOD, rim=True); s.px([(2, 13)], 'silver')   # folding handle + rivet
    return s
def night_shard():
    s = S()
    shard = p([(5, 10), (8, 5), (11, 3), (15, 0), (13, 4), (12, 7), (9, 10), (7, 11)])
    s.add(shard, ['outline', 'plum_dk', 'plum', 'violet'], rim=True)
    s.px([(9, 6), (10, 5), (11, 4), (12, 3)], 'haze'); s.px([(13, 2)], 'white')
    s.add(pm([(4, 10), (5, 11), (6, 12)]), IRON, rim=True)
    s.add(pm([(3, 12), (2, 13), (3, 13), (1, 14), (2, 14), (4, 12)]), ['navy', 'blue_dk', 'blue'], rim=True)
    return s
def howl_fang():
    s = S()
    s.add(ln((3, 3), (8, 6), 1.2) | ln((8, 6), (12, 3), 1.2), ['bark', 'red_dk'], sep=False)       # cord
    fang = p([(6, 6), (11, 6), (10, 10), (8, 14), (7.5, 11)])
    s.add(fang, ['tan', 'sand', 'parchment', 'cream'], rim=True)
    s.add(r(6, 5, 11, 7), ['wood_dk', 'wood'], rim=True)
    s.px([(9, 9), (9, 10)], 'white')
    return s
def road_lute():
    s = S()
    s.add(diag(7, 8, 7, 2), WOOD, rim=True)                                                       # neck
    s.add(pm([(13, 1), (14, 1), (14, 2), (15, 2), (13, 0)]), ['bark', 'wood_dk'], rim=True)       # pegbox
    s.add(e(5.5, 10.5, 4.6, 4.2, rot=0.7), ['wood', 'wood_lt', 'tan', 'sand'], rim=True)          # body
    s.add(e(6, 10, 1.3, 1.3), ['outline'], flat=True, sep=False)
    s.px([(3, 13), (4, 13)], 'wood_dk'); s.px([(8 + i, 7 - i) for i in range(5)], 'cream')        # bridge + strings
    return s
def gravel_axe():
    s = S()
    s.add(diag(1, 14, 12, 2), WOOD, rim=True)
    head = p([(7, 2), (11, 0), (15, 3), (13, 9), (9, 7)])
    s.add(head, ['slate', 'gray', 'silver', 'mist'], rim=True)
    s.px([(14, 5), (13, 7)], 'slate'); s.px([(10, 4), (11, 5)], 'wood_lt')                        # chips + gravel speck
    return s
def lamp_staff():
    s = S()
    s.add(diag(1, 14, 9, 2), WOOD, rim=True)
    s.add(r(9, 2, 15, 8), GOLD[:3], rim=True)                                                     # lantern frame
    s.add(r(10, 3, 14, 7), ['amber', 'gold', 'cream'], sep=False)
    s.px([(11, 4), (12, 4), (11, 5), (12, 5)], 'white'); s.px([(12, 3), (12, 7)], 'orange')
    s.add(pm([(11, 1), (12, 1), (13, 1), (12, 0)]), ['orange', 'amber'], rim=True)
    s.px([(8, 3), (8, 7)], 'cream')                                                               # glow pips
    return s

def kettle_shield():
    s = S()
    s.add(e(8, 9, 6.6, 5.6), ['slate', 'gray', 'silver', 'mist'], rim=True)                       # pot lid
    s.add(e(8, 9, 4.2, 3.2), ['gray', 'silver'], line='slate')
    s.add(r(7, 3, 10, 5), ['ink', 'slate', 'gray'], rim=True)                                     # knob
    s.px([(5, 11), (11, 7)], 'slate'); s.px([(4, 8)], 'white')                                    # dents / shine
    return s
def hymn_board():
    s = S()
    s.add(p([(3, 3), (8, 1), (13, 3), (13, 14), (3, 14)]), ['wood_dk', 'wood', 'wood_lt', 'tan'], rim=True)
    for y in (6, 8, 10, 12): s.px([(x, y) for x in range(5, 12) if (x + y) % 3], 'parchment')     # worn verse
    s.px([(8, 3), (8, 4), (7, 4), (9, 4), (8, 5)], 'gold')
    return s
def oak_buckler():
    s = S()
    s.add(e(8, 8, 7, 7), IRON + ['mist'], rim=True)
    s.add(e(8, 8, 5.4, 5.4), ['wood_dk', 'wood', 'wood_lt'], line='slate')
    for a in range(0, 360, 90):
        x, y = 8 + round(np.cos(np.radians(a)) * 4.2), 8 + round(np.sin(np.radians(a)) * 4.2); s.px([(x, y)], 'silver')
    s.add(pm([(7, 7), (8, 7), (7, 8), (8, 8), (7, 6), (9, 8), (6, 8), (8, 9)]), ['slate', 'silver', 'mist'], rim=True)   # iron rose boss
    s.px([(7, 7)], 'white')
    return s
def glass_orb():
    s = S()
    s.add(e(8, 7, 5.6, 5.6), ['sky', 'sky_lt', 'ice', 'white'], rim=True)
    s.px([(7, 7), (8, 6), (9, 7), (8, 8), (8, 7)], 'gold'); s.px([(8, 7)], 'cream')
    s.px([(5, 4), (6, 4), (5, 5)], 'white')
    s.add(p([(4, 12), (12, 12), (11, 15), (5, 15)]), WOOD, rim=True)
    return s
def void_lens():
    s = S()
    s.add(ln((9, 10), (13, 15), 2.4), GOLD[:3], rim=True)                                          # handle
    s.add(e(7, 7, 6, 6), GOLD[:3], rim=True)
    s.add(e(7, 7, 4.2, 4.2), ['outline', 'navy', 'plum_dk'], line='orange')
    s.px([(5, 6), (8, 5), (9, 8), (6, 9)], 'violet'); s.px([(7, 7)], 'ice'); s.px([(5, 5)], 'haze')
    return s

def coat(s, cols, trim, long=True, hood=False):
    body = p([(3, 3), (6, 2), (10, 2), (13, 3), (13, 15 if long else 12), (3, 15 if long else 12)])
    sleeves = p([(3, 3), (1, 9), (3, 10)]) | p([(13, 3), (15, 9), (13, 10)])
    s.add(sleeves, cols, rim=True); s.add(body, cols, rim=True)
    s.px([(8, y) for y in range(4, 15 if long else 12)], trim)
    if hood: s.add(e(8, 3, 3.5, 2), cols, rim=True)
def travel_coat():
    s = S(); coat(s, ['bark', 'wood_dk', 'wood', 'wood_lt'], 'wood_dk')
    s.add(p([(5, 2), (8, 6), (11, 2), (9, 1), (7, 1)]), ['wood', 'wood_lt', 'tan'], rim=True)    # collar
    s.px([(9, 8), (9, 11)], 'gold')
    return s
def reed_wrap():
    s = S()
    cl = p([(8, 1), (13, 5), (14, 14), (2, 14), (3, 5)])
    s.add(cl, ['leaf_dk', 'leaf', 'grass'], rim=True)
    for y in range(6, 14, 2): s.px([(x, y) for x in range(3, 14) if cl[y, x] and (x + y // 2) % 2 == 0], 'tan')   # woven reeds
    s.add(e(8, 4, 3, 2.5), ['wood', 'tan', 'sand'], rim=True)                                    # clasp / hood fold
    s.px([(8, 4)], 'amber')
    return s
def hedge_mail():
    s = S(); coat(s, ['pine_dk', 'pine', 'leaf_dk', 'leaf'], 'bark', long=False)
    for y in range(4, 12, 2):
        for x in range(4, 13, 2): s.px([(x + (y // 2) % 2, y)], 'silver')
    s.add(r(3, 12, 14, 14), ['bark', 'wood_dk', 'wood'], rim=True)                                # belt
    s.px([(8, 12), (8, 13)], 'gold')
    return s
def plate(s, cols, trim=None, big=False):
    s.add(p([(4, 3), (12, 3), (13, 9), (11, 14), (5, 14), (3, 9)]), cols, rim=True)              # breastplate
    s.px([(8, y) for y in range(4, 13)], cols[0])
    pr = 3.4 if big else 2.8
    s.add(e(3, 4.5, pr, pr - 0.6) | e(13, 4.5, pr, pr - 0.6), cols, rim=True)                     # pauldrons
    if big: s.add(e(2.5, 7, 2.2, 1.6) | e(13.5, 7, 2.2, 1.6), cols, rim=True)
    s.add(p([(6, 2), (10, 2), (9, 4), (7, 4)]), ['outline'], flat=True, sep=False)                 # neck hole
    if trim: s.px([(x, 13) for x in range(5, 12)] + [(4, 3), (12, 3)], trim)
def kiln_plate():
    s = S(); plate(s, ['blood', 'red_dk', 'red', 'coral']); s.px([(5, 6), (11, 6), (5, 11), (11, 11)], 'amber'); return s
def keep_plate():
    s = S(); plate(s, ['slate', 'gray', 'silver', 'mist'], trim='gold', big=True); s.px([(6, 7), (10, 7)], 'ink'); return s
def moon_robe():
    s = S()
    rb = p([(5, 2), (11, 2), (13, 6), (14, 15), (2, 15), (3, 6)])
    sl = p([(4, 3), (0, 11), (3, 12), (5, 7)]) | p([(12, 3), (16, 11), (13, 12), (11, 7)])
    s.add(sl, ['silver', 'mist', 'white'], rim=True); s.add(rb, ['silver', 'mist', 'white'], rim=True)
    s.add(p([(6, 2), (8, 6), (10, 2)]), ['plum', 'violet'], rim=True)                             # V neck
    s.add(e(8, 10, 2.8, 2.8) & ~e(9.4, 9.2, 2.4, 2.4), ['amber', 'gold', 'cream'], rim=True)     # crescent
    s.px([(4, 12), (12, 12), (11, 6)], 'gold'); s.px([(x, 14) for x in range(3, 14)], 'violet'); s.px([(1, 10), (15, 10)], 'violet')
    return s
def lurker_scale():
    s = S()
    s.add(p([(4, 3), (12, 3), (13, 9), (11, 14), (5, 14), (3, 9)]), ['wood_lt', 'tan', 'parchment', 'cream'], rim=True)
    for y in (6, 8, 10, 12): s.px([(x, y) for x in range(5, 12) if x != 8], 'wood_lt')           # ribs
    s.px([(8, y) for y in range(4, 14)], 'sand')
    s.add(e(3, 4, 2.6, 2) | e(13, 4, 2.6, 2), ['wood_lt', 'parchment', 'cream'], rim=True)        # knuckle-bone pauldrons
    s.add(p([(6, 2), (10, 2), (9, 4), (7, 4)]), ['outline'], flat=True, sep=False)
    s.px([(1, 3), (15, 3)], 'cream')
    return s

def bread_charm():
    s = S()
    s.add(ln((8, 1), (8, 5), 1.1), ['bark'], sep=False, flat=True)
    s.add(e(8, 10, 6, 4.4), ['wood', 'wood_lt', 'tan', 'sand'], rim=True)
    s.px([(4 + i, 7 + i) for i in range(7)] + [(12 - i, 7 + i) for i in range(7)], 'red')         # thread
    s.add(e(8, 5, 1.6, 1.6) & ~e(8, 5, 0.6, 0.6), ['red_dk', 'red'], sep=False)
    return s
def wick_ring():
    s = S()
    s.add(e(8, 10, 5.4, 4.2) & ~e(8, 10, 3.2, 2.2), ['red_dk', 'orange', 'amber'], rim=True)     # copper ring
    s.add(r(7, 4, 10, 8), ['sand', 'parchment', 'cream'], rim=True)                                # wick stub (candle)
    s.px([(8, 3), (8, 2)], 'ink'); s.add(pm([(8, 1), (9, 1), (8, 0)]), ['orange', 'gold'], sep=False)
    return s
def pond_bead():
    s = S()
    s.add(ln((2, 2), (6, 7), 1.1) | ln((14, 2), (10, 7), 1.1), ['wood_dk'], sep=False, flat=True)
    s.add(e(8, 10, 4.6, 4.6), ['pine_dk', 'haze', 'sky', 'sky_lt'], rim=True)
    s.px([(6, 8), (7, 8), (6, 9)], 'white'); s.px([(8, 10)], 'pine')
    return s
def threat_bell():
    s = S()
    s.add(p([(8, 2), (11, 5), (12, 11), (14, 13), (2, 13), (4, 11), (5, 5)]), GOLD, rim=True)
    s.add(e(8, 14, 1.6, 1.4), ['ink', 'slate'], rim=True)
    s.add(pm([(6, 1), (7, 0), (9, 0), (10, 1), (8, 1)]), ['red_dk', 'red', 'coral'], rim=True)      # ribbon
    s.px([(6, 6), (6, 7), (6, 8)], 'cream')
    return s
def ley_locket():
    s = S()
    s.px([(4, 0), (5, 1), (11, 1), (12, 0)], 'gold'); s.add(ln((5, 1), (8, 4), 1.1) | ln((11, 1), (8, 4), 1.1), ['amber'], sep=False, flat=True)
    heart = e(6, 7, 3.3, 3) | e(10, 7, 3.3, 3) | p([(3, 8), (13, 8), (8, 14)])
    s.add(heart, GOLD, rim=True)
    s.add(e(8, 8.5, 2, 2), ['plum_dk', 'violet', 'haze'], line='orange'); s.px([(7, 8)], 'white')
    s.px([(2, 5), (14, 5)], 'cream')                                                              # hum glints
    return s
def blob_crown():
    s = S()
    cr = p([(1, 7), (4, 3), (6, 7), (8, 2), (10, 7), (12, 3), (15, 7), (14, 12), (2, 12)])
    s.add(cr, ['blue_dk', 'blue', 'sky', 'sky_lt'], rim=True)
    s.px([(5, 9), (10, 9)], 'outline'); s.px([(6, 11), (7, 11), (8, 11), (9, 11), (5, 10), (10, 10)], 'outline')   # grin
    s.add(pm([(4, 13), (4, 14), (11, 13)]), ['blue', 'sky'], sep=False)                            # drips
    s.px([(4, 3), (8, 2), (12, 3)], 'ice')
    return s
def brute_heart():
    s = S()
    heart = e(5.5, 6, 4, 3.8) | e(10.5, 6, 4, 3.8) | p([(1.5, 7), (14.5, 7), (8, 15)])
    s.add(heart, ['ink', 'slate', 'gray', 'silver'], rim=True)
    s.px([(5, 5), (6, 6), (7, 7), (8, 8), (8, 9), (9, 10), (10, 7), (11, 6), (9, 11), (8, 12)], 'orange')   # hot cracks
    s.px([(7, 7), (8, 9)], 'gold')
    return s
def wisp_jar():
    s = S()
    s.add(r(4, 5, 12, 15), ['sky', 'sky_lt', 'ice'], rim=True)                                    # glass
    s.add(e(8, 10.5, 2.8, 3), ['orange', 'amber', 'gold'], sep=False); s.px([(8, 10), (7, 10)], 'cream')
    s.add(r(6, 2, 10, 5), ['wood_dk', 'wood', 'wood_lt'], rim=True)                                # cork
    s.px([(5, 7), (5, 8)], 'white')
    return s

def bottle(s, glass, liquid, round_=True, big=False, cork=WOOD):
    if round_:
        rr = 5.2 if big else 4.6
        s.add(e(8, 15 - rr - 0.5, rr, rr), glass, rim=True); s.add(e(8, 15 - rr + 0.8, rr - 1.2, rr - 2.2) & (np.mgrid[0:N, 0:N][0] >= 8), liquid, sep=False)
    s.add(r(6, 2, 10, 6), glass, rim=True); s.add(r(6, 1, 10, 3), cork, rim=True)
def tonic():
    s = S(); bottle(s, ['sky', 'sky_lt', 'ice'], ['red_dk', 'red', 'coral']); s.px([(5, 8), (5, 9)], 'white'); return s
def vial():
    s = S()
    s.add(r(6, 3, 10, 15), ['sky', 'sky_lt', 'ice'], rim=True); s.add(r(7, 7, 9, 14), ['blue_dk', 'blue', 'sky'], sep=False)
    s.add(r(5, 2, 11, 4), ['orange', 'amber', 'gold'], rim=True); s.add(r(6, 0, 10, 2), WOOD, rim=True); s.px([(7, 5)], 'white')
    return s
def blue_ether():
    s = S(); bottle(s, ['sky', 'sky_lt', 'ice', 'white'], ['navy', 'blue_dk', 'blue', 'sky'], big=True, cork=GOLD[:3])
    s.px([(4, 9), (4, 10)], 'white'); s.px([(1, 3), (14, 5), (13, 1)], 'sky_lt'); s.px([(2, 2), (13, 4)], 'white')
    s.add(r(5, 5, 11, 7), GOLD[:3], rim=True)
    return s
def loaf_crumb():
    s = S()
    s.add(e(8, 10, 6.5, 4.2), ['wood_dk', 'wood', 'wood_lt', 'tan'], rim=True)
    s.add(e(10.8, 10.5, 2.6, 3.2), ['tan', 'sand', 'parchment'], line='wood')                    # torn crumb face
    s.px([(5, 8), (7, 7), (9, 7)], 'wood_dk'); s.px([(3, 14), (13, 15)], 'tan')
    return s
def field_salve():
    s = S()
    s.add(e(8, 11, 6.5, 3.5), ['slate', 'gray', 'silver', 'mist'], rim=True)                     # tin
    s.add(e(8, 9, 6.5, 2.6), ['silver', 'mist', 'white'], line='slate')                           # lid
    s.add(pm([(8, 7), (8, 8), (8, 9), (8, 10), (6, 9), (7, 9), (9, 9), (10, 9)]), ['red_dk', 'red'], sep=False)   # red cross
    s.add(e(10, 4, 2.4, 2.2), ['leaf_dk', 'leaf', 'grass'], rim=True); s.px([(9, 6), (9, 5)], 'pine')  # herb sprig
    return s
def kettle_dram():
    s = S()
    s.add(e(8, 10.5, 5.6, 4.4), ['red_dk', 'orange', 'amber', 'gold'], rim=True)                  # copper kettle
    s.add(p([(12, 9), (15, 6), (15, 7), (13, 11)]), ['red_dk', 'orange', 'amber'], rim=True)      # spout
    s.add(r(6, 5, 11, 7), ['red_dk', 'orange', 'amber'], rim=True)
    s.add(e(8, 11, 3, 2) & (np.mgrid[0:N, 0:N][1] < 8), ['red_dk', 'red'], sep=False)             # half red
    s.add(e(8, 11, 3, 2) & (np.mgrid[0:N, 0:N][1] >= 8), ['blue_dk', 'blue'], sep=False)          # half blue
    s.px([(14, 4), (15, 3), (14, 2)], 'mist'); s.px([(5, 9)], 'cream')
    return s

ICONS = dict(oath_blade=oath_blade, chapel_mace=chapel_mace, reed_staff=reed_staff, sap_crook=sap_crook, thorn_bow=thorn_bow, pocket_knife=pocket_knife,
    road_lute=road_lute, gravel_axe=gravel_axe, kiln_sword=kiln_sword, lamp_staff=lamp_staff, marsh_bow=marsh_bow, night_shard=night_shard, sunbrand=sunbrand,
    howl_fang=howl_fang, kettle_shield=kettle_shield, hymn_board=hymn_board, glass_orb=glass_orb, oak_buckler=oak_buckler, void_lens=void_lens,
    travel_coat=travel_coat, reed_wrap=reed_wrap, hedge_mail=hedge_mail, kiln_plate=kiln_plate, moon_robe=moon_robe, keep_plate=keep_plate, lurker_scale=lurker_scale,
    bread_charm=bread_charm, wick_ring=wick_ring, pond_bead=pond_bead, threat_bell=threat_bell, ley_locket=ley_locket, blob_crown=blob_crown, brute_heart=brute_heart,
    wisp_jar=wisp_jar, tonic=tonic, vial=vial, loaf_crumb=loaf_crumb, blue_ether=blue_ether, field_salve=field_salve, kettle_dram=kettle_dram)
