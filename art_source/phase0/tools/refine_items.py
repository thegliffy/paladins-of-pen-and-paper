"""REFINE PASS items: thicker weapon/bow icons, Pocket Knife vs Night Shard redesign, sample quest-drop + shop icons (16x16),
and seat gear overlays (48x78) with a gloved fist on every held weapon + thicker shafts/limbs. Rules: refine_style.STYLE."""
import numpy as np
import draft_items as DI, draft_gear as DG
from draft_items import S, e, p, r, ln, pm, diag, STEEL, IRON, WOOD, GOLD, LEATHER, sword, bow, bottle
N = 16

# ================= icons: fixes =================
def oath_blade():
    s = S(); sword(s, STEEL, 10, w=3); s.px([(7 + i, 8 - i) for i in range(5)], 'gold'); return s
def reed_staff():
    s = S(); s.add(diag(1, 14, 12, 3), ['wood', 'tan', 'sand'], rim=True)
    s.px([(4, 11), (5, 11), (8, 7), (9, 7)], 'wood_dk'); s.px([(10, 4), (11, 4), (12, 4), (11, 3), (12, 3)], 'orange'); s.px([(11, 4), (12, 3)], 'amber')
    s.add(pm([(13, 0), (14, 0), (14, 1), (15, 1), (12, 0), (15, 0)]), ['leaf_dk', 'leaf', 'grass'], rim=True); return s
def sap_crook():
    s = S(); s.add(diag(1, 14, 8, 3), WOOD, rim=True)
    s.add(pm([(9, 6), (10, 6), (10, 5), (11, 5), (10, 4), (11, 4), (10, 3), (11, 3), (11, 2), (12, 1), (13, 1), (12, 2), (14, 2), (14, 3), (15, 3), (14, 4), (13, 4), (13, 2)]), WOOD, rim=True)
    s.add(pm([(5, 8), (4, 7), (5, 7), (3, 7), (4, 6)]), ['leaf_dk', 'leaf', 'lime'], rim=True)
    s.px([(14, 5), (14, 6)], 'amber'); s.px([(14, 5)], 'gold'); return s
def fat_bow(s, limb, string, recurve=False, thorns=False):
    th = np.linspace(-1.25, 1.25, 80); m = np.zeros((N, N), bool)
    for w_ in (0.0, 0.6, 1.2, 1.8):
        xs = 3.5 + (6.2 - w_) * np.cos(th); ys = 7.5 + 6.6 * np.sin(th)
        for x, y in zip(xs, ys): m[int(np.clip(round(y), 0, 15)), int(np.clip(round(x), 0, 15))] = True
    if recurve: m |= pm([(3, 1), (2, 0), (3, 14), (2, 15), (4, 1), (4, 14)])
    s.add(m, limb, rim=True)
    s.px([(4, y) for y in range(2, 14)], string)
    s.add(r(8, 6, 11, 10), ['bark', 'wood_dk', 'wood'], rim=True)                                  # leather grip wrap
    if thorns: s.px([(11, 3), (12, 8), (11, 12)], 'bark')
def thorn_bow():
    s = S(); fat_bow(s, WOOD, 'cream', thorns=True); return s
def marsh_bow():
    s = S(); fat_bow(s, ['pine_dk', 'pine', 'leaf_dk', 'leaf'], 'sky_lt', recurve=True)
    s.px([(9, 7), (9, 8)], 'amber'); s.px([(12, 2), (13, 13)], 'sky_lt'); return s
def lamp_staff():
    s = DI.S(); s.add(diag(1, 14, 9, 3), WOOD, rim=True)
    s.add(r(9, 2, 15, 8), GOLD[:3], rim=True); s.add(r(10, 3, 14, 7), ['amber', 'gold', 'cream'], sep=False)
    s.px([(11, 4), (12, 4), (11, 5), (12, 5)], 'white'); s.px([(12, 3), (12, 7)], 'orange')
    s.add(pm([(11, 1), (12, 1), (13, 1), (12, 0)]), ['orange', 'amber'], rim=True); return s
def gravel_axe():
    s = S(); s.add(diag(1, 14, 12, 3), WOOD, rim=True)
    s.add(p([(7, 2), (11, 0), (15, 3), (13, 9), (9, 7)]), ['slate', 'gray', 'silver', 'mist'], rim=True)
    s.px([(14, 5), (13, 7)], 'slate'); return s
def pocket_knife():
    """FOLDING knife: chunky rounded wooden handle with two brass rivets, short broad drop-point blade, no guard"""
    s = S()
    s.add(p([(1, 12), (5, 8), (8, 9), (9, 11), (4, 15), (2, 15)]), ['wood_dk', 'wood', 'wood_lt'], rim=True)   # handle (fat, lower-left)
    s.px([(3, 13), (6, 10)], 'gold')
    s.add(p([(6, 8), (11, 3), (14, 2), (13, 5), (9, 10)]), ['gray', 'silver', 'mist', 'white'], rim=True)      # broad blade, curved belly
    s.px([(7, 8), (8, 7), (9, 6), (10, 5), (11, 4)], 'gray'); s.px([(12, 3)], 'white')                         # spine line + tip glint
    return s
def night_shard():
    """CRYSTAL dagger: tall jagged violet shard standing upright, faceted, wrapped grip, no metal"""
    s = S()
    s.add(p([(7, 11), (5, 6), (7, 4), (8, 0), (10, 4), (12, 3), (11, 7), (9, 11)]), ['plum_dk', 'plum', 'violet', 'haze'], rim=True)
    s.px([(8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (9, 8)], 'violet'); s.px([(7, 5), (11, 4)], 'haze'); s.px([(8, 1)], 'white')
    s.add(r(7, 11, 10, 15), ['navy', 'blue_dk', 'blue'], rim=True)                                  # cloth-wrapped grip
    s.px([(7, 12), (8, 13), (9, 14)], 'sky'); s.add(r(6, 11, 11, 12), ['plum_dk', 'plum'], rim=True)
    return s

# ================= icons: quest drops (samples) =================
def slime_gel():
    s = S(); s.add(e(8, 10, 6.4, 4.6) | e(6, 6.5, 3, 3) | e(10.5, 7, 2.4, 2.4), ['blue_dk', 'blue', 'sky', 'sky_lt'], rim=True)
    s.px([(5, 5), (6, 5), (5, 6)], 'white'); s.px([(4, 14), (12, 14)], 'blue'); return s
def wolf_burr():
    s = S(); s.add(e(8, 9, 4.6, 4.6), ['bark', 'wood_dk', 'wood', 'wood_lt'], rim=True)
    for (x, y) in ((8, 2), (13, 5), (14, 10), (11, 14), (5, 14), (2, 10), (3, 5)): s.add(ln((8, 9), (x, y), 1.2) & ~e(8, 9, 3.6, 3.6), ['wood_dk', 'wood'], rim=True)
    s.add(ln((10, 7), (15, 1), 1.3), ['gray', 'silver'], sep=False); s.px([(6, 7), (7, 6)], 'tan'); return s       # snagged grey fur
def gull_feather():
    s = S(); vane = p([(3, 14), (6, 7), (11, 2), (14, 1), (13, 5), (8, 11)])
    s.add(vane, ['silver', 'mist', 'white'], rim=True); s.px([(4 + i, 13 - i) for i in range(10)], 'gray')
    s.px([(12, 2), (13, 2), (13, 3)], 'slate'); s.px([(2, 15), (3, 14)], 'wood_lt'); return s                 # grey tip, quill
def bat_ear():
    s = S(); s.add(p([(3, 15), (2, 9), (5, 2), (8, 1), (13, 6), (12, 12), (8, 15)]), ['plum_dk', 'plum', 'violet'], rim=True)
    s.add(p([(5, 13), (5, 8), (7, 4), (10, 7), (9, 12)]), ['coral', 'red', 'red_dk'][::-1], rim=True, sep=False)   # inner ear (flesh)
    s.px([(7, 6), (7, 7)], 'coral'); return s
def golem_grit():
    s = S(); s.add(p([(1, 15), (4, 9), (8, 6), (12, 9), (15, 15)]), ['slate', 'gray', 'silver'], rim=True)       # heap
    for (x, y, rx) in ((5, 11, 1.6), (9, 9, 1.8), (11, 12, 1.4), (7, 13, 1.2)): s.add(e(x, y, rx, rx * 0.8), ['ink', 'slate', 'gray', 'silver'], rim=True)
    s.px([(9, 8), (4, 13)], 'orange'); s.px([(9, 7)], 'gold'); return s                                       # still-warm fleck
QUEST = dict(slime_gel=slime_gel, wolf_burr=wolf_burr, gull_feather=gull_feather, bat_ear=bat_ear, golem_grit=golem_grit)

# ================= icons: shop / craft (samples) =================
def salt_mace():
    s = S(); s.add(diag(2, 13, 7, 3), WOOD, rim=True); s.add(e(10.5, 5.5, 3.8, 3.8), STEEL, rim=True)
    s.add(pm([(10, 1), (11, 1), (14, 5), (14, 6), (6, 5), (7, 5), (10, 9), (11, 9)]), IRON, rim=True)
    s.px([(9, 4), (11, 4), (12, 6), (10, 7), (9, 6)], 'white'); s.px([(1, 14), (2, 14)], 'slate'); return s     # salt crust
def tide_axe():
    s = S(); s.add(diag(1, 14, 12, 3), ['wood_dk', 'wood', 'wood_lt'], rim=True)
    s.add(p([(7, 3), (10, 0), (15, 2), (14, 9), (9, 7)]), ['blue_dk', 'blue', 'sky', 'sky_lt'], rim=True)
    s.add(pm([(5, 9), (6, 10), (4, 9), (5, 10), (6, 9)]), ['pine_dk', 'pine', 'haze'], rim=True)            # kelp wrap
    s.px([(13, 4), (12, 6)], 'white'); return s
def echo_bow():
    s = S(); fat_bow(s, ['ink', 'slate', 'gray', 'silver'], 'ice', recurve=True)
    s.px([(1, 6), (0, 8), (1, 10)], 'ice'); s.px([(13, 3), (14, 12)], 'sky_lt'); return s                     # string answers (sound ticks)
def shell_buckler():
    s = S(); s.add(e(8, 8, 7, 7), ['wood_dk', 'wood', 'wood_lt'], rim=True)
    s.add(p([(8, 2), (13, 7), (12, 12), (4, 12), (3, 7)]), ['red_dk', 'orange', 'amber', 'sand'], line='wood_dk')   # crab shell plate
    for x in (6, 8, 10): s.px([(x, y) for y in range(5, 12)], 'red_dk')
    s.px([(6, 4), (5, 5)], 'cream'); return s
def cave_draught():
    s = S(); bottle(s, ['sky', 'sky_lt', 'ice'], ['pine_dk', 'pine', 'leaf_dk'], big=True, cork=['ink', 'slate', 'gray'])
    s.px([(4, 9), (4, 10)], 'white'); s.px([(8, 11), (9, 12)], 'lime'); return s
def gull_charm():
    s = S(); s.add(ln((3, 1), (8, 6), 1.1) | ln((13, 1), (8, 6), 1.1), ['bark'], sep=False, flat=True)
    for k, (x0, y0, x1, y1) in enumerate(((8, 6, 4, 14), (8, 6, 8, 15), (8, 6, 12, 14))):
        s.add(ln((x0, y0), (x1, y1), 2.6), ['silver', 'mist', 'white'], rim=True)
    s.add(e(8, 6.5, 1.8, 1.6), ['red_dk', 'red'], rim=True); return s
SHOP = dict(salt_mace=salt_mace, tide_axe=tide_axe, echo_bow=echo_bow, shell_buckler=shell_buckler, cave_draught=cave_draught, gull_charm=gull_charm)
ICON_FIX = dict(oath_blade=oath_blade, reed_staff=reed_staff, sap_crook=sap_crook, thorn_bow=thorn_bow, marsh_bow=marsh_bow, lamp_staff=lamp_staff,
                gravel_axe=gravel_axe, pocket_knife=pocket_knife, night_shard=night_shard)

# ================= seat gear overlays (48x78, anchor 24,77) =================
from draft_gear import S as GS, e as ge, p as gp, r as gr, ln as gl
def fist(s, x, y):
    """small leather-gloved fist round the grip: knuckles to the left (palm faces the body), lit top-left"""
    s.add(ge(x, y, 3.0, 2.6), ['wood', 'wood_lt', 'tan', 'sand'])
    xi, yi = int(x), int(y); s.px([(xi - 2, yi - 1), (xi - 1, yi - 2), (xi, yi - 2)], 'sand')         # knuckle highlight
    s.px([(xi - 1, yi), (xi, yi), (xi + 1, yi)], 'wood'); s.px([(xi - 1, yi + 1), (xi + 1, yi + 1)], 'wood_dk')   # finger creases
def g_sword1(blade, L_top, guard, grip, wblade=3.6, fuller=None):
    s = GS(); s.add(gl((43, 66), (44, 57), 2.6), grip); s.add(ge(43, 67, 1.7, 1.7), guard)
    s.add(gl((44.5, 55), (46.2, L_top), wblade), blade); s.add(gl((40, 56.5), (47.5, 55.5), 2.4), guard)
    if fuller: s.px([(45, y) for y in range(L_top + 4, 53)], fuller)
    fist(s, 43.5, 61); return s
def g_oath_blade(): return g_sword1(['gray', 'silver', 'mist', 'white'], 30, IRON, LEATHER, fuller='gold')
def g_chapel_mace():
    s = GS(); s.add(gl((43, 67), (45, 42), 3.0), WOOD); s.add(ge(45.3, 37, 3.8, 4.6), ['slate', 'gray', 'silver', 'mist'])
    s.add(gp([(45, 31), (46.5, 33), (43.5, 33)]) | gr(40, 36, 42, 39), ['ink', 'slate', 'gray']); s.px([(45, 36), (45, 37), (45, 38), (44, 37), (46, 37)], 'gold')
    fist(s, 43.6, 61); return s
def g_pocket_knife():
    """folding knife: fat wooden handle in the fist, short BROAD steel blade angled outward, no guard"""
    s = GS(); s.add(gl((43, 66), (44, 58), 3.2), ['wood_dk', 'wood', 'wood_lt'])
    s.add(gp([(43, 57), (46, 56), (47.6, 51), (46.5, 48), (44.2, 52)]), ['gray', 'silver', 'mist', 'white'])
    s.px([(45, 50)], 'white'); s.px([(43, 64)], 'gold'); fist(s, 43.4, 61); return s
def g_night_shard():
    """crystal dagger: tall jagged violet shard, faceted zig-zag edge, cloth-wrapped grip"""
    s = GS(); s.add(gl((43.5, 66), (44, 58), 2.8), ['navy', 'blue_dk', 'blue'])
    s.add(gp([(42.5, 58), (41.5, 51), (43.5, 47), (43.5, 40), (46, 35), (47.6, 42), (46, 46), (47.6, 52), (46, 58)]), ['plum_dk', 'plum', 'violet', 'haze'])
    s.px([(44, 44), (45, 40), (44, 50), (45, 54)], 'haze'); s.px([(46, 37)], 'white'); fist(s, 43.6, 61); return s
def g_staff(shaft, top, w=3.4):
    s = GS(); s.add(gl((45, 72), (44.5, top), w), shaft); return s
def g_reed_staff():
    s = g_staff(['wood', 'tan', 'sand'], 8); s.px([(44, y) for y in (20, 34, 48)], 'wood_dk'); s.px([(44, 12), (45, 12), (44, 14), (45, 14)], 'orange')
    s.add(gp([(44, 8), (40, 2), (44, 5), (46, 1), (46, 6), (48, 4), (46, 9)]), ['leaf_dk', 'leaf', 'grass'])
    fist(s, 44.6, 52); return s
def g_sap_crook():
    s = g_staff(WOOD, 12)
    hook = gl((44.5, 12), (43, 6), 3.2) | gl((43, 6), (39, 4), 3.2) | gl((39, 4), (37, 8), 3.2) | gl((37, 8), (38, 11), 3.0)
    s.add(hook, WOOD); s.add(gp([(45, 30), (47.5, 26), (46, 32)]), ['leaf_dk', 'leaf', 'lime']); s.px([(38, 13), (38, 14)], 'amber')
    fist(s, 44.6, 52); return s
def g_bow_back(limb, string, recurve=False, thorns=False):
    """slung bow (no hand: it hangs on a strap); limbs 3.4px so it reads at 1x"""
    s = GS(); a, b = np.array([40.0, 16.0]), np.array([7.0, 62.0]); mid = (a + b) / 2; nrm = np.array([-(b - a)[1], (b - a)[0]]); nrm /= np.linalg.norm(nrm)
    ctrl = mid - nrm * 13; pts = [tuple((1 - t) ** 2 * a + 2 * (1 - t) * t * ctrl + t * t * b) for t in np.linspace(0, 1, 28)]
    m = np.zeros((78, 48), bool)
    for q0, q1 in zip(pts[:-1], pts[1:]): m |= gl(q0, q1, 3.4)
    if recurve: m |= gl(pts[0], (a[0] + 4, a[1] + 1), 2.6) | gl(pts[-1], (b[0] + 1, b[1] + 4), 2.6)
    s.add(gl(tuple(a), tuple(b), 1.0), [string], flat=True, sep=False)
    s.add(m, limb); s.add(gl(pts[12], pts[15], 3.8), ['bark', 'wood_dk', 'wood'])                  # grip wrap mid-limb
    s.add(gl((14, 40), (33, 60), 1.4), ['bark'], flat=True, sep=False)                             # carry strap across the back
    if thorns: s.px([(int(x) - 2, int(y) - 1) for x, y in pts[4:24:5]], 'bark')
    return s
def g_thorn_bow(): return g_bow_back(WOOD, 'cream', thorns=True)
GEAR_FIX = dict(oath_blade=g_oath_blade, chapel_mace=g_chapel_mace, pocket_knife=g_pocket_knife, night_shard=g_night_shard,
                reed_staff=g_reed_staff, sap_crook=g_sap_crook, thorn_bow=g_thorn_bow)
