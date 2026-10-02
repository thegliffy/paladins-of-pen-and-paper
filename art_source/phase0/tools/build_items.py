"""APPROVED 2026-09-28 (art/phase0-pack @7946500): 40 item icons (ui/items/<id>.png, 16x16) + 26 back-view gear overlays (paperdoll/gear/<id>.png, 48x78)
+ approval sheets. Item list: data/items.json on cursor/phase-0-playable-slice-9a5e (40 items). Writes tools/_work/meta_items.json."""
import json, numpy as np
from PIL import Image
import pal
from pal import C, save, text, text_w
from draft_items import ICONS
from draft_gear import GEAR, PLACEMENT
OUT = pal.OUT; STATUS = 'approved'   # APPROVED by Kyle (item icons + gear overlays), art/phase0-pack @7946500
NW_STATUS = 'draft_pending_approval'   # weapon-less class layers (class_noweapon) - new, not yet approved
def L(rel): return Image.open(OUT + rel).convert('RGBA')
def up(im, k): return im.resize((im.width * k, im.height * k), Image.NEAREST)
ITEMS = [  # id, name, slot, tag/weight, rarity, hands, visual note   (mirrors data/items.json)
 ('oath_blade', 'Oath Blade', 'weapon', 'sword', 'common', 1, 'plain short steel sword, gold vow line in the fuller'),
 ('chapel_mace', 'Chapel Mace', 'weapon', 'mace', 'common', 1, 'flanged steel ball on a wooden haft, small gold cross'),
 ('reed_staff', 'Reed Staff', 'weapon', 'staff', 'common', 2, 'jointed pale reed with copper wire bands and a green tuft'),
 ('sap_crook', 'Sap Crook', 'weapon', 'staff', 'common', 2, 'hooked shepherd crook, leaf sprout and an amber sap drip'),
 ('thorn_bow', 'Thorn Bow', 'weapon', 'bow', 'common', 2, 'simple wooden bow with thorn nubs, cream string'),
 ('pocket_knife', 'Pocket Knife', 'weapon', 'dagger', 'common', 1, 'tiny folding knife, wooden handle with rivet (smallest blade)'),
 ('road_lute', 'Road Lute', 'weapon', 'lute', 'common', 1, 'pear-shaped wooden lute, dark sound hole, cream strings'),
 ('gravel_axe', 'Gravel Axe', 'weapon', 'axe', 'common', 2, 'long haft, chipped grey stone-like axe head'),
 ('kiln_sword', 'Kiln Sword', 'weapon', 'sword', 'rare', 1, 'longer, wider blade with a blued edge; brick-red guard and grip'),
 ('lamp_staff', 'Lamp Staff', 'weapon', 'staff', 'rare', 2, 'staff topped with a glowing gold lantern'),
 ('marsh_bow', 'Marsh Bow', 'weapon', 'bow', 'rare', 2, 'dark-green waxed recurve, wrapped grip, sky string sparks'),
 ('night_shard', 'Night Shard', 'weapon', 'dagger', 'rare', 1, 'jagged black-violet glass shard on a blue grip'),
 ('sunbrand', 'Sunbrand', 'weapon', 'sword', 'legendary', 2, 'full-diagonal gold greatsword, long guard, red sun gem, glints'),
 ('howl_fang', 'Howl Fang', 'weapon', 'dagger', 'unique', 1, 'a curved bone fang bound to a cord'),
 ('kettle_shield', 'Kettle Shield', 'off', 'shield', 'common', 1, 'dented grey pot lid with a knob handle'),
 ('hymn_board', 'Hymn Board', 'off', 'shield', 'common', 1, 'arched wooden board with faded verse lines and a gold cross'),
 ('glass_orb', 'Glass Orb', 'off', 'orb', 'common', 1, 'clear glass ball with a gold spark inside, on a wooden stand'),
 ('oak_buckler', 'Oak Buckler', 'off', 'shield', 'rare', 1, 'round oak with an iron rim, studs and an iron rose boss'),
 ('void_lens', 'Void Lens', 'off', 'orb', 'rare', 1, 'gold-framed hand lens full of dark violet void and a star'),
 ('travel_coat', 'Travel Coat', 'armor', 'light', 'common', 1, 'long brown waxed coat, tan collar, gold buttons'),
 ('reed_wrap', 'Reed Wrap', 'armor', 'light', 'common', 1, 'green marsh cloak with woven tan reed strands'),
 ('hedge_mail', 'Hedge Mail', 'armor', 'medium', 'common', 1, 'hedge-green jack studded with silver rings, leather belt'),
 ('kiln_plate', 'Kiln Plate', 'armor', 'heavy', 'common', 1, 'brick-red breastplate and pauldrons, amber rivets'),
 ('moon_robe', 'Moon Robe', 'armor', 'light', 'rare', 1, 'pale robe with violet V-neck and hem, gold crescent'),
 ('keep_plate', 'Keep Plate', 'armor', 'heavy', 'rare', 1, 'broad steel plate, double pauldrons, gold trim (heaviest silhouette)'),
 ('lurker_scale', 'Bone Plate', 'armor', 'medium', 'unique', 1, 'pale bone rib-plate with knuckle-bone pauldrons'),
 ('bread_charm', 'Bread Charm', 'trinket', '', 'common', 1, 'bread crust bound with a red thread cross, on a loop'),
 ('wick_ring', 'Wick Ring', 'trinket', '', 'common', 1, 'copper ring with a tiny candle stub and flame'),
 ('pond_bead', 'Pond Bead', 'trinket', '', 'rare', 1, 'mill-water teal glass bead on a cord'),
 ('threat_bell', 'Threat Bell', 'trinket', '', 'rare', 1, 'gold bell with a red ribbon and dark clapper'),
 ('ley_locket', 'Ley Locket', 'trinket', '', 'legendary', 1, 'gold heart locket with a violet gem, chain and glints'),
 ('blob_crown', 'Grinning Crown', 'trinket', '', 'unique', 1, 'blue slime crown with a grin and drips'),
 ('brute_heart', 'Brute Heart', 'trinket', '', 'unique', 1, 'grey stone heart with glowing orange cracks'),
 ('wisp_jar', 'Cap Jar', 'trinket', '', 'unique', 1, 'corked glass jar holding an orange glow'),
 ('tonic', 'Hearth Tonic', 'usable', 'heal_hp', 'common', 1, 'round glass flask of red tonic, cork'),
 ('vial', 'Lamp Vial', 'usable', 'heal_mp', 'common', 1, 'slim blue vial with a gold collar'),
 ('loaf_crumb', 'Loaf Crumb', 'usable', 'heal_hp', 'common', 1, 'torn chunk of brown loaf'),
 ('blue_ether', 'Blue Ether', 'usable', 'heal_mp', 'rare', 1, 'bigger blue flask, gold collar and cork, sparkles'),
 ('field_salve', 'Field Salve', 'usable', 'heal_hp', 'rare', 1, 'silver salve tin with a red cross and a herb sprig'),
 ('kettle_dram', 'Kettle Dram', 'usable', 'heal_both', 'common', 1, 'little copper kettle, half red / half blue contents, steam'),
]
assert len(ITEMS) == 40 and set(i[0] for i in ITEMS) == set(ICONS)
META = {}
for iid, name, slot, tag, rar, hands, note in ITEMS:
    save(Image.fromarray(ICONS[iid]().image(trim=False), 'RGBA'), f'ui/items/{iid}.png')
    META[f'ui/items/{iid}.png'] = dict(status=STATUS, item=iid, name=name, slot=slot, rarity=rar, notes=f'16x16 item icon ({name}): {note}. No rarity border (UI tints by rarity).')

CHAIR = L('paperdoll/back/chair_back.png'); CHAIR_M = np.array(CHAIR)[..., 3] > 0
GEAR_IM = {}
for gid, (kind, fn) in GEAR.items():
    a = fn().image(trim=False); a[CHAIR_M] = 0                  # never paint over the chair: identical result whether drawn under or over chair_back
    im = Image.fromarray(a, 'RGBA'); GEAR_IM[gid] = im
    save(im, f'paperdoll/gear/{gid}.png')
    META[f'paperdoll/gear/{gid}.png'] = dict(status=STATUS, item=gid, anchor=[24, 77], canvas=[48, 78], gear_layer={'main1': 'main', 'main2': 'main', 'off': 'off', 'armor': 'armor'}[kind],
        two_handed=kind == 'main2', notes='back-view seat overlay, 48x78, anchor (24,77). ' + PLACEMENT[kind] + '. Pixels under chair_back are cleared.')

# ---------------- back-doll composer with gear (same steps as build_doll.compose_back) ----------------
K = [C['slate'], C['gray'], C['silver'], C['mist']]
HAIR_RAMPS = {'black': ['outline', 'ink', 'slate', 'gray'], 'brown': ['bark', 'wood_dk', 'wood', 'wood_lt'], 'blonde': ['wood_lt', 'tan', 'gold', 'cream'],
    'ginger': ['red_dk', 'orange', 'amber', 'gold'], 'white': ['gray', 'silver', 'mist', 'white'], 'blue': ['navy', 'blue_dk', 'blue', 'sky'], 'green': ['pine_dk', 'leaf_dk', 'leaf', 'grass']}
OUTFIT_RAMPS = {'white': ['silver', 'mist', 'white'], 'red': ['red_dk', 'red', 'coral'], 'blue': ['blue_dk', 'blue', 'sky'], 'purple': ['plum_dk', 'plum', 'violet'],
    'green': ['pine', 'leaf_dk', 'leaf'], 'yellow': ['orange', 'amber', 'gold'], 'brown': ['wood_dk', 'wood', 'wood_lt'], 'dark': ['ink', 'slate', 'gray']}
HAT_CLIP_BACK = {'paladin': 33, 'wizard': 21, 'ranger': 60, 'bard': 21, 'cleric': 19, 'rogue': 60, 'barbarian': 30, 'druid': 0}
SEATD = {'paladin': (2, 2, 'brown', 'white'), 'wizard': (1, 5, 'blonde', 'blue'), 'ranger': (3, 4, 'ginger', 'green'), 'bard': (5, 6, 'black', 'red'),
    'cleric': (4, 2, 'white', 'white'), 'rogue': (2, 3, 'black', 'dark'), 'barbarian': (3, 8, 'ginger', None), 'druid': (6, 1, 'white', 'green')}
def remap(im, keys, cols):
    a = np.array(im); o = a.copy()
    for k, c in zip(keys, cols):
        m = (a[..., :3] == k).all(-1) & (a[..., 3] > 0); o[m, :3] = C[c]
    return Image.fromarray(o, 'RGBA')
NOWEAPON = ['paladin', 'druid', 'wizard', 'barbarian', 'bard', 'ranger']   # classes whose back layer has a baked weapon (see build_doll.NOWEAPON)
def compose_back_gear(cls, gear=(), order='recommended', active=False, flip_off=True, noweapon=False):
    skin, hair, hcol, ocol = SEATD[cls]
    g = {}
    for x in gear:                                                               # armor / main / off (a second main-hand item goes to the off hand)
        k = GEAR[x][0].replace('1', '').replace('2', '')
        g['off' if (k == 'main' and 'main' in g) else k] = x
    im = Image.new('RGBA', (48, 78)); im.alpha_composite(L(f'paperdoll/back/body_back_skin_{skin}.png'))
    if ocol: im.alpha_composite(remap(L('paperdoll/back/outfit_back.png'), K[1:], OUTFIT_RAMPS[ocol]))
    im.alpha_composite(L(f'paperdoll/back/class_back_{cls}_noweapon.png' if (noweapon and cls in NOWEAPON) else f'paperdoll/back/class_back_{cls}.png'))
    if order == 'recommended' and 'armor' in g: im.alpha_composite(GEAR_IM[g['armor']])
    hl = remap(L(f'paperdoll/back/hair_back_{hair}.png'), K, HAIR_RAMPS[hcol]); ha = np.array(hl); ha[:HAT_CLIP_BACK[cls]] = 0
    im.alpha_composite(Image.fromarray(ha, 'RGBA')); im.alpha_composite(L(f'paperdoll/back/class_back_{cls}_hat.png'))
    def off_img():
        o = GEAR_IM[g['off']]
        return o.transpose(Image.FLIP_LEFT_RIGHT) if (flip_off and GEAR[g['off']][0] != 'off') else o
    if order == 'recommended':
        if 'off' in g: im.alpha_composite(off_img())
        if 'main' in g: im.alpha_composite(GEAR_IM[g['main']])
        im.alpha_composite(CHAIR)
    else:                                                        # current runtime: overlays on top of the finished doll
        im.alpha_composite(CHAIR)
        for k in ('armor', 'off', 'main'):
            if k in g: im.alpha_composite(off_img() if k == 'off' else GEAR_IM[g[k]])
    if active:
        a = np.array(im); a2 = np.zeros_like(a); a2[:-3] = a[3:]; op = a2[..., 3] > 0
        n = np.zeros_like(op); n[1:] |= op[:-1]; n[:-1] |= op[1:]; n[:, 1:] |= op[:, :-1]; n[:, :-1] |= op[:, 1:]
        a2[n & ~op] = C['gold'] + (255,); im = Image.fromarray(a2, 'RGBA')
    return im
# sanity: bare composer == shipped seats
for c in SEATD:
    assert (np.array(compose_back_gear(c)) == np.array(L(f'party/seat_{c}_idle.png'))).all(), c
for c in NOWEAPON:
    for st, act in (('idle', False), ('active', True)):
        assert (np.array(compose_back_gear(c, noweapon=True, active=act)) == np.array(L(f'party/seat_{c}_{st}_noweapon.png'))).all(), (c, st)

CLASSES = ['paladin', 'cleric', 'rogue', 'druid', 'wizard', 'barbarian', 'bard', 'ranger']
LOADOUT = {'paladin': ('keep_plate', 'oath_blade', 'kettle_shield'), 'cleric': ('hedge_mail', 'chapel_mace', 'hymn_board'), 'rogue': ('travel_coat', 'night_shard', 'pocket_knife'),
    'druid': ('reed_wrap', 'sap_crook'), 'wizard': ('moon_robe', 'lamp_staff'), 'barbarian': ('kiln_plate', 'gravel_axe'), 'bard': ('travel_coat', 'road_lute', 'glass_orb'),
    'ranger': ('lurker_scale', 'marsh_bow')}
ROWS = [('BARE (SHIPPED SEAT)', lambda c: ()), ('CLASS LOADOUT', lambda c: LOADOUT[c]), ('HEAVY PLATE + TWO-HANDER: KEEP PLATE + SUNBRAND', lambda c: ('keep_plate', 'sunbrand')),
    ('PLATE + SWORD + SHIELD: KILN PLATE + KILN SWORD + OAK BUCKLER', lambda c: ('kiln_plate', 'kiln_sword', 'oak_buckler')), ('STAFF: MOON ROBE + LAMP STAFF', lambda c: ('moon_robe', 'lamp_staff'))]
def seated_sheet(order):
    cw, rh = 54, 96; im = Image.new('RGBA', (8 + 8 * cw, 6 + len(ROWS) * rh + 10), C['slate'] + (255,))
    for i, c in enumerate(CLASSES): text(im, 8 + i * cw + 24 - text_w(c.upper()) // 2 + 3, 4, c.upper(), C['cream'])
    for r_, (lab, fn) in enumerate(ROWS):
        y0 = 14 + r_ * rh; im.paste(C['ink'] + (255,), (0, y0, im.width, y0 + 9)); text(im, 4, y0 + 2, lab, C['gold'])
        for i, c in enumerate(CLASSES):
            im.paste(C['gray'] + (255,), (8 + i * cw, y0 + 11, 8 + i * cw + 50, y0 + 11 + 82))
            im.alpha_composite(compose_back_gear(c, fn(c), order), (8 + i * cw + 1, y0 + 13))
    return im
GS = seated_sheet('recommended'); save(GS, 'approval/gear_seated.png'); save(up(GS, 4), 'approval/gear_seated_4x.png')
GR = seated_sheet('runtime_on_top'); save(GR, 'approval/gear_seated_runtime_on_top.png')
META['approval/gear_seated.png'] = dict(status=STATUS, notes='APPROVAL SHEET: all 8 classes seated (back view) bare, with a class loadout, heavy plate + two-hander, plate + sword + shield, and robe + staff; recommended layer order (armor under hair/hat, weapons over, chair last). Off-hand daggers are drawn mirrored.')
META['approval/gear_seated_4x.png'] = dict(status=STATUS, notes='4x nearest of approval/gear_seated.png.')
META['approval/gear_seated_runtime_on_top.png'] = dict(status=STATUS, notes='QA: the same rows drawn the way PaperDoll.show_gear() currently does it (every overlay on top of the finished doll), to show the hair/hood clash.')

# item icon sheets grouped by slot
GROUPS = [('WEAPONS', 'weapon'), ('OFF-HAND', 'off'), ('ARMOR', 'armor'), ('TRINKETS', 'trinket'), ('USABLES', 'usable')]
cw, chh, per = 66, 30, 7; SH = Image.new('RGBA', (8 + per * cw, 8 + sum(10 + ((sum(1 for i in ITEMS if i[2] == s) + per - 1) // per) * chh for _, s in GROUPS) + 4), C['slate'] + (255,))
y = 4
for gl, sl in GROUPS:
    its = [i for i in ITEMS if i[2] == sl]; SH.paste(C['ink'] + (255,), (0, y, SH.width, y + 9)); text(SH, 4, y + 2, f'{gl} ({len(its)})', C['gold']); y += 11
    for k, it in enumerate(its):
        x0, y0 = 6 + (k % per) * cw, y + (k // per) * chh
        SH.paste(C['gray'] + (255,), (x0, y0, x0 + 18, y0 + 18)); SH.alpha_composite(L(f'ui/items/{it[0]}.png'), (x0 + 1, y0 + 1))
        w1, w2 = [], []
        for wd in it[1].upper().split():
            (w1 if not w2 and len(' '.join(w1 + [wd])) <= 11 else w2).append(wd)
        text(SH, x0 + 20, y0 + 1, ' '.join(w1), C['white']); text(SH, x0 + 20, y0 + 7, ' '.join(w2)[:11], C['white'])
        text(SH, x0 + 20, y0 + 13, it[4].upper()[:9], {'common': C['mist'], 'rare': C['sky'], 'legendary': C['gold'], 'unique': C['coral']}[it[4]])
        text(SH, x0, y0 + 20, it[0].upper()[:16], C['silver'])
    y += ((len(its) + per - 1) // per) * chh
save(SH, 'approval/items_1x.png'); save(up(SH, 4), 'approval/items_4x.png')
META['approval/items_1x.png'] = dict(status=STATUS, notes='APPROVAL SHEET: all 40 item icons at 1x grouped by slot, labelled name / rarity / id (rarity colour on the label only; the icons have no border).')
META['approval/items_4x.png'] = dict(status=STATUS, notes='4x nearest of approval/items_1x.png.')
# all 26 overlays on the rogue seat (no baked class weapon)
OV = Image.new('RGBA', (8 + 13 * 52, 8 + 2 * 92), C['slate'] + (255,))
for k, gid in enumerate(GEAR):
    x0, y0 = 4 + (k % 13) * 52, 4 + (k // 13) * 92
    OV.paste(C['gray'] + (255,), (x0, y0, x0 + 50, y0 + 80)); OV.alpha_composite(compose_back_gear('rogue', (gid,)), (x0 + 1, y0 + 1))
    text(OV, x0, y0 + 82, gid.upper()[:12], C['cream'])
save(OV, 'approval/gear_overlays.png'); save(up(OV, 3), 'approval/gear_overlays_3x.png')
META['approval/gear_overlays.png'] = dict(status=STATUS, notes='QA: each of the 26 overlays on the rogue seat (the one class with no baked weapon, so each overlay is seen alone).')
META['approval/gear_overlays_3x.png'] = dict(status=STATUS, notes='3x nearest.')
# geared party seats for the scene composite
PARTY = ['paladin', 'cleric', 'rogue', 'druid', 'wizard']
for i, c in enumerate(PARTY):
    for st, act in (('idle', False), ('active', True)):
        save(compose_back_gear(c, LOADOUT[c], active=act), f'approval/gear_seats/seat_{c}_{st}.png')
        META[f'approval/gear_seats/seat_{c}_{st}.png'] = dict(status=STATUS, anchor=[24, 77], notes=f'QA seat: {c} wearing {", ".join(LOADOUT[c])} (recommended layer order). Used by scene_test_portrait_gear.png.')

# class_noweapon check: original / weapon-less / weapon-less + a typical main-hand weapon (recommended seat_recipe order)
NW_WEAPON = {'paladin': 'oath_blade', 'druid': 'sap_crook', 'wizard': 'reed_staff', 'barbarian': 'gravel_axe', 'bard': 'road_lute', 'ranger': 'thorn_bow'}
NAME = {i[0]: i[1] for i in ITEMS}
NW_ROWS = [('ORIGINAL CLASS LAYER (SHIPPED SEAT)', lambda c: compose_back_gear(c)), ('NOWEAPON CLASS LAYER', lambda c: compose_back_gear(c, noweapon=True)),
           ('NOWEAPON + EQUIPPED MAIN-HAND WEAPON', lambda c: compose_back_gear(c, (NW_WEAPON[c],), noweapon=True))]
cw, rh = 54, 96; NWS = Image.new('RGBA', (8 + 6 * cw, 14 + 3 * rh + 16), C['slate'] + (255,))
for i, c in enumerate(NOWEAPON): text(NWS, 8 + i * cw + 24 - text_w(c.upper()) // 2 + 3, 4, c.upper(), C['cream'])
for r_, (lab, fn) in enumerate(NW_ROWS):
    y0 = 14 + r_ * rh; NWS.paste(C['ink'] + (255,), (0, y0, NWS.width, y0 + 9)); text(NWS, 4, y0 + 2, lab, C['gold'])
    for i, c in enumerate(NOWEAPON):
        NWS.paste(C['gray'] + (255,), (8 + i * cw, y0 + 11, 8 + i * cw + 50, y0 + 11 + 82)); NWS.alpha_composite(fn(c), (8 + i * cw + 1, y0 + 13))
for i, c in enumerate(NOWEAPON):
    nm = NAME[NW_WEAPON[c]].upper(); text(NWS, 8 + i * cw + 25 - text_w(nm) // 2, 14 + 3 * rh + 2, nm, C['white'])
save(NWS, 'approval/class_noweapon_check.png'); save(up(NWS, 4), 'approval/class_noweapon_check_4x.png')
META['approval/class_noweapon_check.png'] = dict(status=NW_STATUS, notes='APPROVAL SHEET: the 6 classes with a baked weapon (paladin, druid, wizard, barbarian, bard, ranger): shipped seat, the same seat built with class_back_<c>_noweapon, and noweapon + a typical main-hand weapon (' + ', '.join(f'{c} {NAME[w]}' for c, w in NW_WEAPON.items()) + '); all composed in the recommended seat_recipe order (steps_with_gear).')
META['approval/class_noweapon_check_4x.png'] = dict(status=NW_STATUS, notes='4x nearest of approval/class_noweapon_check.png.')

GEAR_ORDER = ['back/body_back_skin_<skin>', 'back/outfit_back (tinted)', 'back/class_back_<class> (class_back_<class>_noweapon when a main-hand weapon is equipped and the class has one, see class_noweapon)', 'gear ARMOR: paperdoll/gear/<armor id>',
    'back/hair_back_<hair> (tinted, hat-clipped)', 'back/class_back_<class>_hat', 'gear OFF HAND: paperdoll/gear/<off id> (flip horizontally when the off-hand item is a weapon/dagger drawn for the main hand)',
    'gear MAIN HAND: paperdoll/gear/<main id> (a two-hander fills both hands; skip the off-hand)', 'back/chair_back (always last; gear pixels under the chair are already cleared)',
    'ACTIVE: shift up 3px, then 1px #f8d040 outline around the union (includes the gear)']
ITEMS_BLOCK = dict(status=STATUS, source='data/items.json (40 items) @ cursor/phase-0-playable-slice-9a5e; v0.2.8 report Art Director section',
    icons=dict(dir='ui/items/', size=[16, 16], border=False, style='chunky flat, 1px #120c18 outline, 3-4 tone rim shading from the top-left, pack palette, binary alpha',
               placeholders_note='category placeholders (sword, bow, potion...) stay as fallbacks; point data/items.json "icon" at ui/items/<id>.png'),
    gear=dict(dir='paperdoll/gear/', canvas=[48, 78], anchor=[24, 77], face='back (seat doll)', placement=PLACEMENT, layer_order=GEAR_ORDER,
              runtime_note='PaperDoll.show_gear() currently draws only main + armor, on top of the finished doll, stretched to the doll size. For these overlays: add the off hand, draw armor before hair/hat (see layer_order), and do not stretch them onto the 32x48 FRONT doll used on the gear screen (these are back-view art).'),
    list=[dict(id=i[0], name=i[1], slot=i[2], tag=i[3], rarity=i[4], hands=i[5], icon=f'ui/items/{i[0]}.png', doll=(f'paperdoll/gear/{i[0]}.png' if i[0] in GEAR else ''), visual=i[6]) for i in ITEMS])
json.dump(dict(meta=META, items=ITEMS_BLOCK), open(OUT + 'tools/_work/meta_items.json', 'w'), indent=1)
print('icons', len(ICONS), 'gear', len(GEAR))
