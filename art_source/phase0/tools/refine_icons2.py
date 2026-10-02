"""REFINE-2 item icons (16x16): the 12 remaining quest drops + 38 remaining shop/craft items, so no item in data/items.json
(3103e38) is left on a parchment placeholder. Same chunky rim-lit style as draft_items/refine_items (1px #120c18 outline,
top-left light, 3px shafts/blades). Tag families share a silhouette; members differ in head/material (rule readability)."""
import numpy as np
from draft_items import S, e, p, r, ln, pm, diag, STEEL, IRON, WOOD, GOLD, LEATHER, sword, bottle, coat, plate, dagger
from refine_items import fat_bow
N = 16
YS, XS = np.mgrid[0:N, 0:N]
STONE = ['ink', 'slate', 'gray', 'silver']; ASH = ['slate', 'gray', 'silver', 'mist']; COPPER = ['red_dk', 'orange', 'amber', 'gold']
SEA = ['navy', 'blue_dk', 'blue', 'sky']; KELP = ['pine_dk', 'pine', 'haze']; BONE = ['wood_lt', 'tan', 'parchment', 'cream']
GLASS = ['sky', 'sky_lt', 'ice', 'white']
# ---------------- families ----------------
def t_sword(blade, guard=IRON, grip=LEATHER, pommel=IRON, w=3, L=10):
    s = S(); sword(s, blade, L, w=w, guard=guard, grip=grip, pommel=pommel, guard_len=2); return s
def t_mace(head, flange, haft=WOOD, r_=3.8):
    s = S(); s.add(diag(2, 13, 7, 3), haft, rim=True); s.add(e(10.5, 5.5, r_, r_), head, rim=True)
    s.add(pm([(10, 1), (11, 1), (14, 5), (14, 6), (6, 5), (7, 5), (10, 9), (11, 9)]), flange, rim=True); return s
def t_axe(head, haft=WOOD, big=False):
    s = S(); s.add(diag(1, 14, 12, 3), haft, rim=True)
    s.add(p([(6, 3), (10, 0), (16, 2), (15, 11), (9, 8)] if big else [(7, 3), (10, 0), (15, 2), (14, 9), (9, 7)]), head, rim=True); return s
def t_dagger(blade, grip=LEATHER, guard=IRON, L=6):
    s = S(); dagger(s, blade, L, grip=grip, guard=guard, x0=4, y0=11, w=3); return s
def t_staff(shaft=WOOD):
    s = S(); s.add(diag(1, 14, 10, 3), shaft, rim=True); return s
def t_lute(body, neck=WOOD, peg=('bark', 'wood_dk')):
    s = S(); s.add(diag(7, 8, 7, 3), neck, rim=True); s.add(pm([(13, 1), (14, 1), (14, 2), (15, 2), (13, 0), (15, 1)]), list(peg), rim=True)
    s.add(e(5.5, 10.5, 4.8, 4.4, rot=0.7), body, rim=True); s.add(e(6, 10, 1.4, 1.4), ['outline'], flat=True, sep=False)
    s.px([(8 + i, 7 - i) for i in range(5)], 'cream'); return s
def t_orb(glass, cup=WOOD):
    s = S(); s.add(e(8, 7, 5.6, 5.6), glass, rim=True); s.add(p([(4, 12), (12, 12), (11, 15), (5, 15)]), cup, rim=True); return s
def t_robe(cols, trim):
    s = S(); rb = p([(5, 2), (11, 2), (13, 6), (14, 15), (2, 15), (3, 6)]); sl = p([(4, 3), (0, 11), (3, 12), (5, 7)]) | p([(12, 3), (16, 11), (13, 12), (11, 7)])
    s.add(sl, cols, rim=True); s.add(rb, cols, rim=True); s.add(p([(6, 2), (8, 6), (10, 2)]), ['outline'], flat=True, sep=False)
    s.px([(x, 14) for x in range(3, 14)], trim); s.px([(1, 10), (15, 10)], trim); return s
def t_mail(cols, ring='silver', belt=LEATHER):
    s = S(); coat(s, cols, cols[0], long=False)
    for y in range(4, 12, 2):
        for x in range(4, 13, 2): s.px([(x + (y // 2) % 2, y)], ring)
    s.add(r(3, 12, 14, 14), belt, rim=True); return s
def t_bead(ramp, cord='wood_dk'):
    s = S(); s.add(ln((2, 2), (6, 7), 1.1) | ln((14, 2), (10, 7), 1.1), [cord], sep=False, flat=True); s.add(e(8, 10, 4.6, 4.6), ramp, rim=True); return s
# ---------------- quest drops ----------------
def reed_tongue():
    s = S(); s.add(p([(2, 13), (3, 7), (6, 3), (10, 2), (13, 4), (13, 8), (10, 9), (8, 8), (7, 11), (5, 14)]), ['red_dk', 'red', 'coral'], rim=True)
    s.px([(9, 3), (10, 4), (11, 5), (8, 4)], 'coral'); s.px([(5, 6), (6, 9), (4, 11)], 'red_dk')
    s.px([(10, 6), (5, 8), (11, 3), (4, 12)], 'white'); return s                                         # salt grains
def thorn_chip():
    s = S(); s.add(p([(2, 14), (5, 8), (10, 3), (15, 0), (12, 6), (8, 11), (5, 14)]), ['pine_dk', 'leaf_dk', 'leaf', 'grass'], rim=True)
    s.px([(6, 10), (8, 8), (10, 6), (12, 4)], 'lime'); s.px([(4, 13)], 'wood_lt'); return s
def toad_wart():
    s = S(); s.add(e(8, 10, 6, 4.8), ['wood_dk', 'wood', 'tan', 'sand'], rim=True)
    for (x, y, rr) in ((6, 8, 1.8), (10, 9, 2.0), (8, 12, 1.5), (4, 11, 1.2)): s.add(e(x, y, rr, rr), ['pine', 'leaf_dk', 'leaf'], rim=True)
    s.px([(5, 7), (9, 8)], 'grass'); return s
def crab_shell():
    s = S(); sh = e(8, 10, 7, 5.6) & (YS <= 12); s.add(sh, ['red_dk', 'red', 'orange', 'amber'], rim=True)
    for x in (5, 8, 11): s.px([(x, y) for y in range(7, 12)], 'red_dk')
    s.add(r(2, 12, 15, 14), ['wood_dk', 'wood_lt', 'tan'], rim=True); s.px([(5, 6), (6, 6)], 'gold'); return s
def cap_spore():
    s = S(); s.add(e(8, 8, 4.6, 4.6), ['orange', 'amber', 'gold', 'cream'], rim=True); s.px([(7, 7), (6, 6)], 'white')
    for (x, y) in ((2, 3), (13, 2), (14, 11), (2, 12), (8, 1)): s.px([(x, y)], 'gold'); s.px([(x + 1, y)], 'cream')
    return s
def kelp_scale():
    s = S(); s.add(p([(3, 2), (13, 2), (14.5, 8), (8, 15.5), (1.5, 8)]), ['pine', 'haze', 'cyan', 'ice'], rim=True)
    for k, y in enumerate((5, 8, 11)): s.px([(8 + d, y + abs(d) // 2) for d in range(-5 + k * 1, 6 - k * 1)], 'pine')
    s.px([(4, 3), (5, 3)], 'ice'); return s
def bone_chip():
    s = S(); s.add(p([(2, 9), (5, 5), (9, 4), (12, 2), (14, 4), (12, 7), (9, 9), (6, 12), (3, 12)]), BONE, rim=True)
    s.add(e(12.5, 3.5, 2.2, 2.2), BONE, rim=True); s.px([(4, 10), (7, 7)], 'tan'); s.px([(6, 6)], 'white'); return s
def grub_silk():
    s = S()
    for k, (cx, cy, rx, ry) in enumerate(((8, 9, 5.6, 4.6), (8, 9, 3.6, 2.8))):
        s.add(e(cx, cy, rx, ry) & ~e(cx, cy, rx - 1.6, ry - 1.6), ['tan', 'parchment', 'cream'], rim=True)
    s.add(ln((13, 9), (15, 2), 1.2), ['parchment', 'cream'], sep=False); s.px([(15, 1)], 'white'); return s
def fang_venom():
    s = S(); s.add(p([(3, 6), (8, 2), (13, 5), (13, 11), (8, 14), (3, 11)]), GLASS, rim=True)
    s.add(e(8, 9.5, 2.6, 3.2) | p([(6.5, 8), (8, 4), (9.5, 8)]), ['leaf_dk', 'leaf', 'grass', 'lime'], sep=False); s.px([(7, 8)], 'white'); s.px([(4, 5)], 'white'); return s
def squire_pebble():
    s = S(); s.add(p([(2, 11), (3, 6), (7, 4), (12, 5), (14, 9), (12, 13), (5, 14)]), ['wood_dk', 'wood', 'tan', 'sand'], rim=True)
    s.px([(6, 8), (10, 7), (8, 11), (11, 10)], 'wood'); s.add(e(5, 10, 1.6, 1.4), ['pine', 'leaf_dk'], sep=False); s.px([(6, 6), (7, 5)], 'parchment'); return s
def helm_rivet():
    s = S(); s.add(r(6, 7, 10, 15), IRON, rim=True); s.add(e(8, 6, 6, 3.6) & (YS <= 8), STEEL, rim=True)
    s.px([(5, 4), (6, 4)], 'white'); s.px([(7, 10), (7, 12)], 'slate'); return s
def rat_whisker():
    s = S()
    for k, (a, b) in enumerate((((2, 13), (14, 3)), ((2, 13), (15, 8)), ((2, 13), (10, 1)))):
        s.add(ln(a, b, 1.3), ['slate', 'gray', 'silver'], rim=True)
    s.add(e(3, 12.5, 2.4, 2.4), ['wood_dk', 'wood', 'wood_lt'], rim=True); return s
# ---------------- shop / craft ----------------
def pier_lute():
    s = t_lute(['blue_dk', 'blue', 'sky', 'sky_lt'], neck=WOOD, peg=('pine', 'haze')); s.px([(3, 12), (8, 13)], 'white'); return s
def ash_lute():
    s = t_lute(['gray', 'silver', 'mist', 'white'], neck=['ink', 'slate', 'gray']); s.px([(4, 12), (7, 12), (3, 10)], 'slate'); return s     # pale ash body, soot
def stone_lute():
    s = t_lute(['wood_lt', 'tan', 'sand', 'parchment'], neck=['ink', 'slate', 'gray'], peg=('slate', 'gray')); s.px([(3, 9), (4, 13), (8, 12)], 'wood_lt'); return s   # sandstone body
def brine_orb():
    s = t_orb(['blue_dk', 'blue', 'sky', 'sky_lt'], cup=['wood_dk', 'wood', 'wood_lt']); s.px([(x, 8) for x in range(4, 12)], 'sky_lt'); s.px([(5, 4), (6, 4)], 'white'); return s
def keep_orb():
    s = t_orb(['slate', 'gray', 'silver', 'mist'], cup=GOLD[:3]); s.px([(7, 7), (8, 8), (9, 6)], 'orange'); s.px([(5, 4)], 'white'); return s
def salt_jack():
    s = S(); coat(s, ['wood_dk', 'wood', 'wood_lt', 'tan'], 'bark', long=False); s.add(r(3, 11, 14, 13), LEATHER, rim=True)
    s.px([(5, 5), (11, 4), (6, 9), (10, 8), (12, 10), (4, 8)], 'white'); s.px([(8, 11), (8, 12)], 'silver'); return s
def ash_coat():
    s = S(); coat(s, ASH, 'slate', hood=True); s.px([(5, 13), (11, 12), (6, 7)], 'gray'); return s
def gate_robe():
    s = t_robe(['navy', 'blue_dk', 'blue', 'sky'], 'gold'); s.px([(8, y) for y in range(6, 14)], 'gold'); return s
def burr_cloak():
    s = S(); cl = p([(5, 2), (11, 2), (14, 15), (2, 15)]); s.add(cl, ['bark', 'wood_dk', 'wood', 'wood_lt'], rim=True)
    s.add(e(8, 3, 3.6, 2), ['wood_dk', 'wood', 'wood_lt'], rim=True)
    for (x, y) in ((5, 8), (10, 7), (7, 11), (11, 12), (4, 13), (8, 6)): s.px([(x, y)], 'bark'); s.px([(x + 1, y - 1)], 'tan')
    s.px([(8, 4)], 'gold'); return s
def drip_mail():
    s = t_mail(['navy', 'blue_dk', 'blue', 'sky'], ring='sky_lt'); s.px([(5, 13), (11, 13)], 'ice'); return s
def pebble_mail():
    s = t_mail(['slate', 'gray', 'silver', 'mist'], ring='wood_lt'); s.px([(6, 6), (10, 8), (7, 10)], 'tan'); return s
def silk_mail():
    s = t_mail(['tan', 'parchment', 'cream', 'white'], ring='slate', belt=['slate', 'gray', 'silver']); return s
def cairn_plate():
    s = S(); plate(s, ['ink', 'slate', 'gray', 'silver'], trim='wood_lt', big=True); s.px([(5, 7), (6, 10), (11, 6), (10, 11)], 'ink'); s.px([(4, 5), (12, 4)], 'mist'); return s
def rivet_plate():
    s = S(); plate(s, ['slate', 'gray', 'silver', 'mist'], big=True)
    s.px([(5, 5), (11, 5), (5, 9), (11, 9), (6, 12), (10, 12), (2, 4), (14, 4)], 'gold'); return s
def cleft_sword():
    s = t_sword(STEEL); s.px([(9, 6), (12, 3)], 'slate'); s.px([(10, 4)], 'white'); return s           # nicks in the edge
def gate_sword():
    s = t_sword(STEEL, guard=GOLD[:3], grip=['navy', 'blue_dk', 'blue'], pommel=GOLD[:3]); s.px([(7 + i, 8 - i) for i in range(5)], 'mist'); return s
def ash_mace():
    s = t_mace(ASH, ['ink', 'slate', 'gray'], haft=['ink', 'slate', 'gray']); s.px([(9, 5), (12, 6)], 'orange'); return s
def banner_mace():
    s = t_mace(STEEL, GOLD[:3]); s.add(p([(3, 10), (1, 7), (5, 9), (4, 6), (6, 9)]), ['red_dk', 'red', 'coral'], rim=True); return s
def drip_staff():
    s = t_staff(['wood_dk', 'wood', 'wood_lt']); s.add(e(12.5, 3.5, 2.8, 2.8) | p([(11, 2), (13, 0), (15, 3)]), ['blue_dk', 'blue', 'sky', 'sky_lt'], rim=True)
    s.px([(11, 3)], 'white'); s.px([(5, 10), (8, 7)], 'sky'); return s
def keep_staff():
    s = t_staff(['ink', 'slate', 'gray']); s.add(p([(10, 4), (12, 0), (15, 1), (15, 5), (12, 7)]), ['slate', 'gray', 'silver', 'mist'], rim=True)
    s.px([(13, 3)], 'gold'); s.px([(12, 2)], 'white'); s.px([(9, 6), (8, 7)], GOLD[1]); return s
def tide_crook():
    s = S(); s.add(diag(1, 14, 8, 3), WOOD, rim=True)
    s.add(pm([(9, 6), (10, 6), (10, 5), (11, 5), (10, 4), (11, 4), (10, 3), (11, 3), (11, 2), (12, 1), (13, 1), (12, 2), (14, 2), (14, 3), (15, 3), (14, 4), (13, 4), (13, 2)]), WOOD, rim=True)
    s.add(e(13.5, 5.5, 2.2, 2.4), ['pine_dk', 'pine', 'haze', 'cyan'], rim=True); return s
def cave_shard():
    s = S(); s.add(p([(5, 10), (7, 6), (10, 3), (15, 0), (13, 5), (10, 9), (7, 11)]), ['blue', 'sky', 'sky_lt', 'ice'], rim=True)
    s.px([(9, 6), (11, 4), (13, 2)], 'white'); s.add(pm([(3, 12), (2, 13), (3, 13), (1, 14), (2, 14), (4, 12), (4, 11)]), LEATHER, rim=True); return s
def gate_knife():
    s = t_dagger(STEEL, grip=WOOD, L=6); s.add(e(2.5, 13.5, 1.8, 1.8), ['slate', 'gray', 'silver'], rim=True); return s   # pebble pommel
def gel_edge():
    s = S(); s.add(p([(1, 12), (5, 8), (8, 9), (9, 11), (4, 15), (2, 15)]), ['slate', 'gray', 'silver'], rim=True); s.px([(3, 13), (6, 10)], 'gold')
    s.add(p([(6, 8), (11, 3), (14, 2), (13, 5), (9, 10)]), ['blue_dk', 'blue', 'sky', 'sky_lt'], rim=True)
    s.px([(8, 7), (10, 5)], 'ice'); s.px([(12, 3)], 'white'); return s
def fang_needle():
    s = S(); s.add(p([(5, 10), (9, 5), (13, 1), (11, 6), (7, 11)]), BONE, rim=True); s.px([(8, 7), (10, 5)], 'white')
    s.add(pm([(4, 11), (5, 11), (5, 12), (3, 12), (4, 12)]), ['blue', 'sky', 'sky_lt'], rim=True)
    s.add(pm([(2, 13), (1, 14), (2, 14), (3, 13), (1, 15)]), LEATHER, rim=True); return s
def cliff_axe():
    s = t_axe(['ink', 'slate', 'gray', 'silver'], big=True); s.px([(14, 4), (14, 8)], 'gold'); return s           # sparks on the edge
def cairn_axe():
    s = S(); s.add(diag(1, 14, 12, 3), ['ink', 'slate', 'gray'], rim=True)
    s.add(p([(7, 2), (12, 0), (16, 4), (13, 10), (8, 7)]), ['wood_dk', 'wood', 'tan', 'sand'], rim=True)          # sandstone head
    s.px([(11, 3), (13, 6)], 'wood_dk'); return s
def grit_axe():
    s = t_axe(['ink', 'slate', 'gray', 'silver']); s.px([(10, 3), (12, 5), (13, 3), (11, 7)], 'orange'); s.px([(12, 4)], 'gold'); return s
def slate_shield():
    s = S(); s.add(p([(2, 3), (13, 1), (14, 13), (3, 15)]), STONE, rim=True); s.px([(4, 6), (8, 5), (6, 10), (11, 9)], 'slate')
    s.add(ln((7, 4), (9, 12), 1.4), ['wood_lt', 'tan'], sep=False); return s                                    # rope grip
def gate_shield():
    s = S(); s.add(e(8, 8, 7, 7), ['wood_dk', 'wood', 'wood_lt'], rim=True); s.add(e(8, 8, 2.8, 2.6), ['slate', 'gray', 'silver', 'mist'], rim=True)
    for k in range(4): s.px([(8, 2 + k), (8, 11 + k)], 'wood_dk')
    s.px([(7, 7)], 'white'); return s
def gravel_bow():
    s = S(); fat_bow(s, ['slate', 'gray', 'silver', 'mist'], 'cream', recurve=True); s.px([(2, 0), (2, 15)], 'tan'); return s
def cleft_bead():
    s = t_bead(STONE); s.px([(6, 8), (7, 8)], 'silver'); s.px([(8, 10), (9, 11)], 'ink'); return s
def drip_bead():
    s = t_bead(BONE, cord='bark'); s.add(e(8, 10.5, 1.8, 2.2), ['blue_dk', 'blue', 'sky'], sep=False); s.px([(7, 9)], 'white'); return s
def march_token():
    s = S(); s.add(e(8, 8, 6.4, 6.4), ['red_dk', 'orange', 'wood_lt', 'tan'][::1], rim=True); s.add(e(8, 8, 4.2, 4.2), ['wood_lt', 'tan'], line='red_dk')
    s.px([(6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (10, 6), (9, 7), (7, 9), (6, 10)], 'red_dk'); return s          # two strokes: counted twice
def kettle_band():
    s = S(); s.add(e(8, 9, 6, 5) & ~e(8, 9, 3.6, 2.6), COPPER, rim=True); s.px([(4, 6), (5, 5)], 'cream'); s.px([(11, 12)], 'red_dk')
    s.add(e(8, 3, 1.8, 1.4), ['slate', 'gray', 'mist'], rim=True); return s
def whisker_charm():
    s = S(); s.add(ln((3, 1), (8, 6), 1.1) | ln((13, 1), (8, 6), 1.1), ['bark'], sep=False, flat=True)
    for (a, b) in (((8, 9), (2, 14)), ((8, 9), (14, 14)), ((8, 9), (8, 15))): s.add(ln(a, b, 1.3), ['slate', 'gray', 'silver'], rim=True)
    s.add(e(8, 8, 2.8, 2.6), ['slate', 'gray', 'silver', 'mist'], rim=True); s.px([(7, 7)], 'white'); return s
def deep_vial():
    s = S(); s.add(r(6, 3, 10, 15), GLASS[:3], rim=True); s.add(r(7, 6, 9, 14), ['navy', 'blue_dk', 'plum_dk'], sep=False)
    s.add(r(5, 2, 11, 4), ['slate', 'gray', 'silver'], rim=True); s.add(r(6, 0, 10, 2), ['ink', 'slate'], rim=True); s.px([(7, 5)], 'white'); s.px([(8, 10)], 'violet'); return s
def keep_dram():
    s = S(); bottle(s, GLASS[:3], ['red_dk', 'red', 'coral'], big=True, cork=['slate', 'gray', 'silver'])
    s.add(e(8, 10.5, 4, 3) & (XS >= 8) & (YS >= 8), ['blue_dk', 'blue', 'sky'], sep=False); s.px([(4, 9), (4, 10)], 'white'); return s
QUEST2 = dict(reed_tongue=reed_tongue, thorn_chip=thorn_chip, toad_wart=toad_wart, crab_shell=crab_shell, cap_spore=cap_spore, kelp_scale=kelp_scale,
    bone_chip=bone_chip, grub_silk=grub_silk, fang_venom=fang_venom, squire_pebble=squire_pebble, helm_rivet=helm_rivet, rat_whisker=rat_whisker)
SHOP2 = dict(pier_lute=pier_lute, brine_orb=brine_orb, salt_jack=salt_jack, cleft_sword=cleft_sword, ash_mace=ash_mace, drip_staff=drip_staff, cave_shard=cave_shard,
    ash_lute=ash_lute, cliff_axe=cliff_axe, slate_shield=slate_shield, ash_coat=ash_coat, drip_mail=drip_mail, cleft_bead=cleft_bead, deep_vial=deep_vial,
    gate_sword=gate_sword, banner_mace=banner_mace, keep_staff=keep_staff, gravel_bow=gravel_bow, gate_knife=gate_knife, stone_lute=stone_lute, cairn_axe=cairn_axe,
    gate_shield=gate_shield, keep_orb=keep_orb, gate_robe=gate_robe, pebble_mail=pebble_mail, cairn_plate=cairn_plate, march_token=march_token, keep_dram=keep_dram,
    gel_edge=gel_edge, burr_cloak=burr_cloak, kettle_band=kettle_band, tide_crook=tide_crook, silk_mail=silk_mail, fang_needle=fang_needle, drip_bead=drip_bead,
    grit_axe=grit_axe, rivet_plate=rivet_plate, whisker_charm=whisker_charm)
