"""REFINE-2 seat gear overlays (all 26, 48x78, anchor 24,77). Rule readability: every HELD weapon/focus gets a 6x4 gloved fist
(8x6 with its outline) with a knuckle highlight row and finger creases; slung or strapped items (bows, Gravel Axe, Sunbrand,
Road Lute, shields, Hymn Board) get none. Shafts/blades >= 3px. Everything is relit with refine_style.relight afterwards."""
import numpy as np
import draft_gear as DG, refine_items as RI, refine_style as RS
from draft_gear import S as GS, e as ge, p as gp, r as gr, ln as gl, STEEL, IRON, WOOD, GOLD, LEATHER
GLOVE = ['wood', 'wood_lt', 'tan', 'sand']          # light tan leather glove: reads against dark grips + every skin
def fist(s, x, y):
    """gloved fist round a vertical grip at (x, y): 6x4 of glove inside a closed #120c18 ring (8x6 at 1x). Row 1 = lit knuckles
    with creases between the four fingers, rows 2-3 = fingers, row 4 = palm shade; thumb on the left. Light tan leather so it
    reads on any grip and any skin tone. The ring is part of the overlay so it also separates the fist from the shaft."""
    xi, yi = min(int(round(x)), 44), int(round(y))
    m = gr(xi - 4, yi - 3, xi + 4, yi + 3); m[yi - 3, xi - 4] = m[yi - 3, xi + 3] = m[yi + 2, xi - 4] = m[yi + 2, xi + 3] = False
    s.add(m, ['outline'], flat=True, sep=False)
    s.add(gr(xi - 3, yi - 2, xi + 3, yi + 2), ['tan'], flat=True, sep=False)
    s.px([(xi - 2, yi - 2), (xi, yi - 2), (xi + 2, yi - 2)], 'parchment'); s.px([(xi - 1, yi - 2), (xi + 1, yi - 2)], 'wood_lt')   # knuckles + creases
    s.px([(xi - 1, yi - 1), (xi + 1, yi - 1)], 'wood_lt'); s.px([(xi - 1, yi), (xi + 1, yi)], 'wood_lt')                         # finger creases
    s.px([(xi - 2 + k, yi + 1) for k in range(0, 5)], 'wood_lt'); s.px([(xi + 2, yi), (xi + 2, yi + 1)], 'wood')                 # palm shade
    s.px([(xi - 3, yi - 2), (xi - 3, yi - 1)], 'sand'); s.px([(xi - 3, yi), (xi - 3, yi + 1)], 'tan')                            # thumb
RI.fist = fist                                                    # phase-1 overlays now use the bigger fist
def kiln_sword():
    return RI.g_sword1(['blue_dk', 'sky', 'mist', 'white'], 25, ['red_dk', 'red', 'coral'], ['red_dk', 'red'], wblade=4.4, fuller='sky')
def howl_fang():
    s = GS(); s.add(gl((42, 63), (47, 61), 1.2), ['bark', 'red_dk'], sep=False)
    s.add(gp([(42.0, 59), (47.0, 59), (46.6, 51), (45.2, 44), (43.2, 52)]), ['tan', 'sand', 'parchment', 'cream'])
    s.add(gr(42, 59, 47, 66), LEATHER); fist(s, 44.4, 62); return s
def lamp_staff():
    s = RI.g_staff(WOOD, 16, w=3.4)
    s.add(gr(40, 5, 48, 16), ['orange', 'amber', 'gold']); s.add(gr(42, 7, 46, 14), ['amber', 'gold', 'cream'], sep=False); s.px([(43, 9), (44, 9), (43, 10)], 'white')
    s.add(gp([(41, 5), (44, 1), (47, 5)]), ['orange', 'amber']); s.px([(38, 8), (38, 12), (39, 3)], 'cream'); fist(s, 44.6, 52); return s
def marsh_bow():
    s = RI.g_bow_back(['pine_dk', 'pine', 'leaf_dk', 'leaf'], 'sky_lt', recurve=True); s.add(ge(17, 33, 2.4, 2.4), ['wood_dk', 'wood', 'wood_lt']); return s
def gravel_axe():
    s = GS(); s.add(gl((27, 70), (42, 22), 4.0), WOOD)
    s.add(gp([(35, 18), (42, 8), (47.5, 11), (47.5, 26), (39.5, 27)]), ['slate', 'gray', 'silver', 'mist']); s.px([(45, 16), (45, 21)], 'slate'); return s
def glass_orb():
    s = GS(); s.add(ge(5, 55, 4.4, 4.4), ['sky', 'sky_lt', 'ice', 'white'])
    s.px([(5, 55), (6, 54), (5, 56)], 'gold'); s.px([(3, 53)], 'white'); s.px([(1, 49), (9, 50)], 'cream'); fist(s, 5, 61); return s
def void_lens():
    s = GS(); s.add(gl((5, 58), (6, 67), 3.0), ['orange', 'amber', 'gold']); s.add(ge(5, 52, 4.6, 5.6), ['orange', 'amber', 'gold'])
    s.add(ge(5, 52, 3, 4), ['outline', 'navy', 'plum_dk'], line='orange'); s.px([(4, 51), (6, 53)], 'violet'); s.px([(5, 50)], 'ice'); fist(s, 5.6, 63); return s
HELD = ['oath_blade', 'kiln_sword', 'chapel_mace', 'pocket_knife', 'night_shard', 'howl_fang', 'reed_staff', 'sap_crook', 'lamp_staff', 'glass_orb', 'void_lens']
NO_FIST = dict(thorn_bow='slung on a strap', marsh_bow='slung on a strap', gravel_axe='slung across the back', sunbrand='slung across the back',
               road_lute='slung across the back', kettle_shield='strapped to the forearm', oak_buckler='strapped to the forearm', hymn_board='strapped to the forearm')
NEW = dict(kiln_sword=kiln_sword, howl_fang=howl_fang, lamp_staff=lamp_staff, marsh_bow=marsh_bow, gravel_axe=gravel_axe, glass_orb=glass_orb, void_lens=void_lens)
def build(gid):
    if gid in NEW: s = NEW[gid]()
    elif gid in RI.GEAR_FIX: s = RI.GEAR_FIX[gid]()
    else: s = DG.GEAR[gid][1]()
    return s.image(trim=False)
def finish(a, chair):
    a = a.copy(); a[chair] = 0
    a = RS.relight(a, hi=0.22, lo=0.24, hi_min=0.74, spec=0.05, lock=('sand', 'parchment', 'tan'))     # keep the fist knuckle highlights
    a[chair] = 0; return a
