"""Back-view paper-doll gear overlays, 48x78, anchor (24,77) = the seated back doll canvas."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from regionlib import Sprite, E, P, R, LN
import pal
W, H = 48, 78
def S(): return Sprite(W, H)
def e(*a, **k): return E(W, H, *a, **k)
def p(pts): return P(W, H, pts)
def r(*a): return R(W, H, *a)
def ln(*a): return LN(W, H, *a)
YS, XS = np.mgrid[0:H, 0:W]
BODY = np.array(Image.open(pal.OUT + 'paperdoll/back/body_back_skin_3.png'))[..., 3] > 0
TORSO = BODY & (YS >= 41)
def dil(m, k=1): return ndi.binary_dilation(m, iterations=k)
STEEL = ['slate', 'gray', 'silver', 'mist']; IRON = ['ink', 'slate', 'gray']; WOOD = ['wood_dk', 'wood', 'wood_lt']
GOLD = ['orange', 'amber', 'gold', 'cream']; LEATHER = ['bark', 'wood_dk', 'wood']

# ---------------- armor (layer: after class_back, before hair) ----------------
def travel_coat():
    s = S(); m = dil(TORSO, 1) & (YS >= 41)
    s.add(m, ['bark', 'wood_dk', 'wood', 'wood_lt'])
    s.add(e(24, 41, 8, 3) & (YS <= 43), ['wood', 'wood_lt', 'tan'])                                # collar
    s.px([(24, y) for y in range(45, 66)], 'bark')
    s.px([(x, 47 + (x % 2)) for x in list(range(7, 13)) + list(range(35, 41))], 'wood_dk')          # shoulder seams
    return s
def reed_wrap():
    s = S(); cl = p([(15, 40), (33, 40), (43, 46), (46, 67), (2, 67), (5, 46)])
    s.add(cl, ['pine_dk', 'leaf_dk', 'leaf', 'grass'])
    for y in range(47, 66, 3):
        s.px([(x, y) for x in range(3, 46) if cl[y, x] and (x // 2 + y) % 3 == 0], 'tan')
    s.add(e(24, 42, 10, 4), ['wood', 'tan', 'sand'])                                               # rolled hood
    s.px([(24, 42), (25, 42)], 'amber')
    return s
def hedge_mail():
    s = S(); m = dil(TORSO, 1) & (YS >= 42)
    s.add(m, ['pine_dk', 'pine', 'leaf_dk', 'leaf'])
    for y in range(45, 66, 2):
        for x in range(4, 45, 2):
            if m[y, x] and m[y, min(W - 1, x + 1)]: s.px([(x + (y // 2) % 2, y)], 'silver')
    s.add((r(12, 42, 15, 66) | r(33, 42, 36, 66)) & m, LEATHER, flat=True)                          # leather straps
    return s
def pauldron_pair(s, cols, cx, cy, rx, ry, trim=None, lames=0):
    for sx in (-1, 1):
        x = 24 + sx * cx
        for k in range(lames, 0, -1): s.add(e(x + sx * 1, cy + 4 * k, rx - k, ry - 1), cols)
        s.add(e(x, cy, rx, ry), cols)
        if trim: s.px([(x + i, cy + ry - 1 - (abs(i) > rx - 3)) for i in range(-int(rx) + 2, int(rx) - 1)], trim)
def kiln_plate():
    s = S(); bp = TORSO & (YS >= 43)
    s.add(bp, ['blood', 'red_dk', 'red', 'coral'])
    s.px([(24, y) for y in range(45, 66)], 'blood'); s.px([(23, y) for y in range(45, 66)], 'coral')     # ridge
    pauldron_pair(s, ['blood', 'red_dk', 'red', 'coral'], 15, 45, 7.5, 5)
    s.px([(9, 44), (39, 44), (16, 52), (32, 52), (16, 58), (32, 58)], 'amber')                       # rivets
    return s
def keep_plate():
    s = S(); bp = dil(TORSO, 1) & (YS >= 43)
    s.add(bp, STEEL)
    s.px([(24, y) for y in range(45, 66)], 'slate'); s.px([(23, y) for y in range(45, 66)], 'mist')
    s.add(r(14, 38, 34, 44), STEEL)                                                                 # gorget
    pauldron_pair(s, STEEL, 16, 43, 9, 6, trim='gold', lames=2)
    s.px([(x, 60) for x in range(12, 37)], 'gold')                                                  # trim band (no banner)
    return s
def moon_robe():
    s = S(); mt = p([(14, 40), (34, 40), (45, 48), (45, 67), (3, 67), (3, 48)])
    s.add(mt, ['silver', 'mist', 'white'])
    s.add(e(24, 42, 11, 4), ['plum', 'violet', 'haze'])                                             # hood fold
    s.add(e(24, 55, 4, 4) & ~e(26, 54, 3.4, 3.4), ['amber', 'gold', 'cream'])                       # crescent
    s.px([(12, 52), (36, 50), (33, 61), (14, 62)], 'gold'); s.px([(x, 66) for x in range(4, 45)], 'violet')
    return s
def lurker_scale():
    s = S(); bp = TORSO & (YS >= 43)
    s.add(bp, ['wood_dk', 'wood', 'wood_lt'], flat=True)                                           # leather backing
    for k, y in enumerate(range(46, 64, 4)):                                                       # ribs
        w_ = 13 - k
        s.add(ln((24 - w_, y + 2), (23, y), 2.2) | ln((25, y), (25 + w_, y + 2), 2.2), ['tan', 'parchment', 'cream'])
    for y in range(43, 64, 3): s.add(e(24, y, 2, 1.4), ['wood_lt', 'parchment', 'cream'])          # vertebrae
    pauldron_pair(s, ['wood_lt', 'tan', 'parchment', 'cream'], 15, 45, 6, 4)
    s.add(p([(4, 45), (1, 40), (6, 43)]) | p([(44, 45), (47, 40), (42, 43)]), ['tan', 'parchment', 'cream'])   # bone spurs
    return s

# ---------------- main hand, 1h: held at the hero's right side, pointing up and out ----------------
def sword1(s, blade, L_top, guard, grip, wblade=3, fuller=None):
    s.add(ln((43, 64), (44, 57), 2.4), grip)
    s.add(e(43, 65, 1.6, 1.6), guard)
    s.add(ln((44.5, 55), (46.2, L_top), wblade), blade)
    s.add(ln((40, 56.5), (47.5, 55.5), 2.2), guard)
    if fuller: s.px([(45, y) for y in range(L_top + 4, 53)], fuller)
def oath_blade():
    s = S(); sword1(s, ['gray', 'silver', 'mist', 'white'], 30, IRON, LEATHER, fuller='gold'); return s
def kiln_sword():
    s = S(); sword1(s, ['blue_dk', 'sky', 'mist', 'white'], 25, ['red_dk', 'red', 'coral'], ['red_dk', 'red'], wblade=4, fuller='sky'); return s
def chapel_mace():
    s = S()
    s.add(ln((43, 65), (45, 42), 2.4), WOOD)
    s.add(e(45.3, 37, 3.6, 4.4), STEEL)
    s.add(p([(45, 31), (46.5, 33), (43.5, 33)]) | r(40, 36, 42, 39), IRON)                          # flanges
    s.px([(45, 36), (45, 37), (45, 38), (44, 37), (46, 37)], 'gold')
    return s
def dagger1(s, blade, top, grip=LEATHER, guard=IRON, w=2.4):
    s.add(ln((43, 64), (44, 59), 2.4), grip)
    s.add(ln((41, 58.5), (47, 57.5), 1.8), guard)
    s.add(ln((44.3, 57), (45.8, top), w), blade)
def pocket_knife():
    s = S(); dagger1(s, ['gray', 'silver', 'mist'], 49, grip=WOOD); return s
def night_shard():
    s = S(); dagger1(s, ['outline', 'plum_dk', 'plum', 'violet'], 44, grip=['navy', 'blue_dk', 'blue'], w=3.2)
    s.px([(45, 47), (46, 50)], 'haze'); return s
def howl_fang():
    s = S()
    s.add(ln((42, 62), (47, 60), 1.2), ['bark', 'red_dk'], sep=False)
    s.add(p([(42.5, 60), (46.5, 60), (46, 52), (45, 46), (43.5, 53)]), ['tan', 'sand', 'parchment', 'cream'])
    s.add(r(42, 60, 47, 63), LEATHER)
    return s
def road_lute():                     # slung across the back, neck over the right shoulder
    s = S()
    s.add(ln((13, 62), (40, 28), 1.2), ['bark'], flat=True, sep=False)                              # strap
    s.add(ln((18, 52), (37, 27), 3.2), WOOD)
    s.add(p([(35, 25), (40, 20), (43, 23), (38, 28)]), LEATHER)
    s.add(e(13, 57, 8, 7, rot=0.7), ['wood', 'wood_lt', 'tan', 'sand'])
    s.add(e(15, 55, 2, 2), ['outline'], flat=True, sep=False)
    return s
# ---------------- main hand, 2h ----------------
def staff(s, shaft, top=10):
    s.add(ln((45, 72), (44.5, top), 2.6), shaft)
def reed_staff():
    s = S(); staff(s, ['wood', 'tan', 'sand'], 8)
    s.px([(44, y) for y in (20, 34, 48, 62)], 'wood_dk')
    s.px([(44, 12), (45, 12), (44, 14), (45, 14)], 'orange')
    s.add(p([(44, 8), (40, 2), (44, 5), (46, 1), (46, 6), (48, 4), (46, 9)]), ['leaf_dk', 'leaf', 'grass'])
    return s
def sap_crook():
    s = S(); staff(s, WOOD, 12)
    hook = ln((44.5, 12), (43, 6), 2.6) | ln((43, 6), (39, 4), 2.6) | ln((39, 4), (37, 8), 2.6) | ln((37, 8), (38, 11), 2.4)
    s.add(hook, WOOD)
    s.add(p([(45, 30), (47.5, 26), (46, 32)]), ['leaf_dk', 'leaf', 'lime'])
    s.px([(38, 13), (38, 14)], 'amber')
    return s
def lamp_staff():
    s = S(); staff(s, WOOD, 16)
    s.add(r(40, 5, 48, 16), ['orange', 'amber', 'gold'])
    s.add(r(42, 7, 46, 14), ['amber', 'gold', 'cream'], sep=False); s.px([(43, 9), (44, 9), (43, 10)], 'white')
    s.add(p([(41, 5), (44, 1), (47, 5)]), ['orange', 'amber'])
    s.px([(38, 8), (38, 12), (39, 3)], 'cream')
    return s
def bow_back(s, limb, string, recurve=False, thorns=False):
    a, b = np.array([40.0, 16.0]), np.array([7.0, 62.0]); mid = (a + b) / 2; nrm = np.array([-(b - a)[1], (b - a)[0]]); nrm /= np.linalg.norm(nrm)
    ctrl = mid - nrm * 13                                                                             # bulge up/left
    pts = [tuple((1 - t) ** 2 * a + 2 * (1 - t) * t * ctrl + t * t * b) for t in np.linspace(0, 1, 24)]
    m = np.zeros((H, W), bool)
    for q0, q1 in zip(pts[:-1], pts[1:]): m |= ln(q0, q1, 2.6)
    if recurve: m |= ln(pts[0], (a[0] + 4, a[1] + 1), 2.2) | ln(pts[-1], (b[0] + 1, b[1] + 4), 2.2)
    s.add(ln(tuple(a), tuple(b), 1.0), [string], flat=True, sep=False)
    s.add(m, limb)
    if thorns: s.px([(int(x) - 1, int(y) - 1) for x, y in pts[4:20:4]], 'bark')
def thorn_bow():
    s = S(); bow_back(s, WOOD, 'cream', thorns=True); return s
def marsh_bow():
    s = S(); bow_back(s, ['pine_dk', 'pine', 'leaf_dk', 'leaf'], 'sky_lt', recurve=True)
    s.add(e(17, 33, 2.4, 2.4), ['wood_dk', 'wood', 'wood_lt']); return s
def gravel_axe():                    # haft runs up the right edge of the head, head beside the ear
    s = S()
    s.add(ln((27, 70), (42, 22), 3.2), WOOD)
    s.add(p([(36, 18), (42, 9), (46.5, 12), (46.5, 25), (40, 26)]), ['slate', 'gray', 'silver', 'mist'])
    s.px([(45, 16), (45, 21)], 'slate')
    return s
def sunbrand():                      # greatsword slung steeply, hilt above the right shoulder, blade down behind the chair
    s = S()
    s.add(ln((42, 18), (26, 72), 5.2), ['orange', 'amber', 'gold', 'cream'])
    s.px([(int(round(42 - t * 16)) - 2, int(round(18 + t * 54))) for t in np.linspace(0.08, 1, 40)], 'white')
    s.add(ln((37, 16), (46.4, 19.5), 3), ['orange', 'amber', 'gold'])
    s.add(ln((42.5, 15), (44, 7), 3), LEATHER)
    s.add(e(44.3, 5, 2.2, 2.2), GOLD)
    s.px([(42, 17), (41, 18)], 'red')
    return s
# ---------------- off hand: on the hero's LEFT arm edge ----------------
def kettle_shield():
    s = S(); s.add(e(5, 53, 4.6, 8.5), ['slate', 'gray', 'silver', 'mist'])
    s.add(e(2, 53, 1.6, 2.4), IRON); s.px([(6, 49), (5, 58)], 'slate'); return s
def hymn_board():
    s = S(); s.add(p([(1, 43), (9, 40), (10, 65), (2, 67)]), ['wood_dk', 'wood', 'wood_lt', 'tan'])
    for y in (47, 51, 55, 59): s.px([(x, y + (x > 5)) for x in range(3, 9) if (x + y) % 3], 'parchment')
    return s
def oak_buckler():
    s = S(); s.add(e(5, 52, 5.2, 7.2), ['ink', 'slate', 'gray', 'silver'])
    s.add(e(5, 52, 3.6, 5.4), ['wood_dk', 'wood', 'wood_lt'], line='slate')
    s.add(e(4.5, 52, 1.8, 2.2), ['slate', 'silver', 'mist']); return s
def glass_orb():
    s = S(); s.add(e(5, 57, 4.2, 4.2), ['sky', 'sky_lt', 'ice', 'white'])
    s.px([(5, 57), (6, 56), (5, 58)], 'gold'); s.px([(3, 55)], 'white'); s.px([(1, 51), (9, 52)], 'cream'); return s
def void_lens():
    s = S(); s.add(ln((5, 58), (7, 66), 2.2), ['orange', 'amber', 'gold'])
    s.add(e(5, 52, 4.6, 5.6), ['orange', 'amber', 'gold'])
    s.add(e(5, 52, 3, 4), ['outline', 'navy', 'plum_dk'], line='orange'); s.px([(4, 51), (6, 53)], 'violet'); s.px([(5, 50)], 'ice'); return s

GEAR = dict(oath_blade=('main1', oath_blade), chapel_mace=('main1', chapel_mace), reed_staff=('main2', reed_staff), sap_crook=('main2', sap_crook),
    thorn_bow=('main2', thorn_bow), pocket_knife=('main1', pocket_knife), road_lute=('main1', road_lute), gravel_axe=('main2', gravel_axe),
    kiln_sword=('main1', kiln_sword), lamp_staff=('main2', lamp_staff), marsh_bow=('main2', marsh_bow), night_shard=('main1', night_shard),
    sunbrand=('main2', sunbrand), howl_fang=('main1', howl_fang), kettle_shield=('off', kettle_shield), hymn_board=('off', hymn_board),
    glass_orb=('off', glass_orb), oak_buckler=('off', oak_buckler), void_lens=('off', void_lens), travel_coat=('armor', travel_coat),
    reed_wrap=('armor', reed_wrap), hedge_mail=('armor', hedge_mail), kiln_plate=('armor', kiln_plate), moon_robe=('armor', moon_robe),
    keep_plate=('armor', keep_plate), lurker_scale=('armor', lurker_scale))
PLACEMENT = dict(armor='shoulders + upper back; drawn after class_back and BEFORE hair/hood (long hair and hoods fall over the back plate)',
    main1='held at the hero\'s right side (screen right, x40-47), pointing up/out past the shoulder; the lute is slung diagonally across the back instead',
    main2='staffs held upright at the right side (x40-48, top y1-16); bows, the gravel axe and Sunbrand slung diagonally across the back, top end over the right shoulder, lower end hidden by the chair',
    off='on the hero\'s left arm edge (screen left, x0-10, y40-67)')
