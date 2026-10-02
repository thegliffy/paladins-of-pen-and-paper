"""REFINE PASS - FULL SET (refine-2, 2026-10-01; phase 1 approved). Everything written here is status 'review'.
Run after build_items.py and before compose.py. Reads ONLY frozen sources (tools/_work/pre_refine/ snapshot, tools/_work/doll_raw/,
or the drawing modules), so it is idempotent: rerunning gives the same bytes. Same filenames / sizes / anchors as before (asserted).
Covers: all 10 portrait backdrops (+2 new towns), all 18 monsters, GM, dice, table, UI (+ui/hub), 3 new map pins, every item icon,
all 26 seat gear overlays, every back-view paperdoll layer except the 6 body/skin layers, and every party seat (recomposed)."""
import json, os, numpy as np
from PIL import Image
import pal
from pal import C, OUT, save
import refine_style as RS, refine_backdrops as RB, refine_ui as RU, refine_items as RI
PRE = OUT + 'tools/_work/pre_refine/'
assert os.path.isdir(PRE), 'pre-refine snapshot missing: tools/_work/pre_refine/'
def Lp(rel): return Image.open(PRE + rel).convert('RGBA')                          # BEFORE (frozen)
def Ln(rel): return Image.open(OUT + rel).convert('RGBA')
META = {}; REFINED = []
def out(a, rel, what, before=None, new=False, **kw):
    im = a if isinstance(a, Image.Image) else Image.fromarray(a.astype(np.uint8), 'RGBA')
    if not new:
        assert os.path.exists(PRE + rel), rel; b = Lp(rel)
        assert b.size == im.size, (rel, b.size, im.size)                              # KEEP every existing size
    save(im, rel)
    META[rel] = dict(status='review', refine='refine-2', what=what, before=(before or ('tools/_work/pre_refine/' + rel if not new else 'none (new file)')), **kw)
    REFINED.append(dict(path=rel, new=new, what=what))

import refine_backdrops2 as RB2, refine_gear as RG, refine_icons2 as RI2, refine_doll as RD, refine_dice as RDc, refine_pins as RP
# ---------------- backdrops (all 10 portrait backdrops) ----------------
BG = dict(millpond=(RB, 'meadow: calm perspective grass, two-depth tree line, knoll + windmill, pond with banks; refine-2: path 5px wide at the horizon widening to ~40px, lit left verge + tan lip, shaded right verge + wood lip', False),
          howling_cleft=(RB, 'cave: natural faceted cliff (Voronoi rock facets, crevices, lit top), irregular mouth with passage floor, grey grit floor with perspective cracks, faceted boulders, puddle (re-checked in refine-2, unchanged)', False),
          candlewick=(RB, 'town: cobbled lane in perspective, calm packed-earth square with soft ruts, well/barrels/crates/lamp; refine-2: edge dressing (flower trough, bench, hay bale, cart wheel, fence, crate, barrel, worn flagstones, grass tufts) kept outside x50-220 below y195 so the seats/table/hub UI area stays clean', False),
          brinewick=(RB, 'NEW town (coast fishing town): sea horizon + sail, net shed + net rack, salt-bread bakery, damp stone forge, plank boardwalk, wet sand with tide pools', True),
          forest=(RB2, 'forest: layered trunks + canopies in depth, light shafts, ferns/mushrooms at the sides, calm leaf-litter floor', False),
          gravel_keep=(RB2, 'keep: squat stone keep with gate and towers, gravel yard in perspective, rubble and pebbles, calm floor below y300', False),
          briar_cross=(RB2, 'crossroads: four-way dirt road widening in perspective, thorn hedges with berries, signpost, distant cottage, calm grass', False),
          lantern_reach=(RB2, 'coast: white lighthouse with lit lamp, blue shallows with foam lines, rocks, pale sand, calm foreground', False),
          ashgate=(RB2, 'NEW town (cave-mouth camp): faceted grey cliff with a timbered mine mouth, plank lean-to off the cliff with a goods bench + hanging sign, cart rails, campfire, ore sacks, grey grit floor', True),
          pebblegate=(RB2, 'NEW town (market before the keep): crenellated gate wall + gatehouse with portcullis, banners, three striped stall tents with goods, bunting, flagged road to the gate, packed-earth square', True))
for k, (mod, what, new) in BG.items():
    rel = f'combat/bg_{k}_portrait.png'
    kw = dict(anchor=[0, 0], horizon_y=141, monster_feet_band=[222, 266], calm_below_y=300) if (mod is RB or new) else {}
    if new: kw.update(region='greenmere', town=True)
    out(RS.to_palette(getattr(mod, k)().image()), rel, what,              # snap guards stray non-palette px
        before=('tools/_work/pre_refine/repo_placeholders/' + rel + ' (repo placeholder)') if new else None, new=new, **kw)

# ---------------- monsters: all 18, every strip + portrait ----------------
MONSTERS = sorted(os.listdir(PRE + 'monsters'))
assert len(MONSTERS) == 18, MONSTERS
FLYING = {'bat', 'squallgull', 'hollow_helm'}
def shadow_params(m):
    a = np.array(Lp(f'monsters/{m}/{m}_idle.png'))[:, :80]; op = a[..., 3] > 0
    ys, xs = np.nonzero(op)
    if m in FLYING: return dict(cx=40, rx=max(6, min(12, (xs.max() - xs.min()) * 0.22)), ry=2.0, fly=True, area=op.sum())
    low = op[58:67]; xs2 = np.nonzero(low.any(0))[0]
    return dict(cx=(xs2.min() + xs2.max() + 1) / 2, rx=float(np.clip((xs2.max() - xs2.min()) / 2 + 4, 10, 28)), ry=3.0, fly=False, area=op.sum())
def mon_px(fr):
    fr, _ = RS.style_sprite(fr)
    return RS.eye_glints(RS.relight(fr, hi=0.28, lo=0.30, spec=0.06, hi_min=0.70, lo_max=0.66))
MWHAT = ('style pass (closed #120c18 outline, despeckle) + relight (per-part dome shading from the top-left: lit share +1 tone, '
         'shadowed bottom-right share -1 tone, metal/gold spec) + white catch-light in the eyes + 50% checker contact shadow')
for m in MONSTERS:
    sp = shadow_params(m)
    for anim in ('idle', 'attack', 'hit', 'death', 'still'):
        rel = f'monsters/{m}/{m}_{anim}.png'; a = np.array(Lp(rel)); nf = a.shape[1] // 80; outa = a.copy()
        assert a.shape[0] == 70, (rel, a.shape)
        for f in range(nf):
            fr = mon_px(a[:, f * 80:(f + 1) * 80]); op = fr[..., 3] > 0
            ratio = op.sum() / max(1, sp['area'])
            if anim == 'death' and ratio < 0.2: outa[:, f * 80:(f + 1) * 80] = fr; continue
            cx = sp['cx']
            if not sp['fly']:
                low = np.nonzero(op[58:67].any(0))[0]
                if len(low): cx = (low.min() + low.max() + 1) / 2
            rx = sp['rx'] * (min(1.0, np.sqrt(ratio)) if anim == 'death' else 1.0)
            outa[:, f * 80:(f + 1) * 80] = RS.contact_shadow(fr, cx, 64 if sp['fly'] else 65, rx, sp['ry'])
        out(outa, rel, MWHAT + (' (flyer: small shadow at the feet anchor)' if sp['fly'] else ''), frames=nf, frame_size=[80, 70], anchor=[40, 64])
    rel = f'monsters/{m}/{m}_portrait.png'
    out(mon_px(np.array(Lp(rel))), rel, 'style pass + relight + eye catch-light (no shadow)')

# ---------------- table, GM, dice ----------------
def refine_table(a):
    a = a.copy(); op = a[..., 3] > 0; Hh, Ww = op.shape; ys, xs = np.mgrid[0:Hh, 0:Ww]
    col = lambda n: (a[..., :3] == C[n]).all(-1) & op
    top = op & (ys >= 1) & (ys <= 12) & ~col('outline'); seam = top & col('wood')
    a[top & ~seam, :3] = C['wood_lt']
    for k in range(110):                                                                  # long soft grain streaks along the planks
        x0, y0 = int(RB._h(k, 1, 5) * (Ww - 20)) + 4, 2 + int(RB._h(k, 2, 5) * 10)
        L_ = 8 + int(RB._h(k, 3, 5) * 18)
        m = top & ~seam & (ys == y0) & (xs >= x0) & (xs < x0 + L_)
        a[m, :3] = C['tan'] if k % 5 else C['wood']
    a[seam, :3] = C['wood_dk']
    a[top & (ys == 1), :3] = C['tan']                                                     # lit far edge
    for x in range(8, Ww - 8, 44):                                                         # nail heads at plank ends
        for y in (3, 7, 11):
            if top[y, x]: a[y, x, :3] = C['bark']; a[y - 1, x, :3] = C['wood']
    ap = op & (ys >= 14) & (ys <= 19) & ~col('outline'); a[ap, :3] = C['wood']
    a[ap & (ys == 14), :3] = C['wood_lt']; a[ap & (ys == 19), :3] = C['wood_dk']
    for x in range(30, Ww - 30, 53):
        a[ap & (xs == x), :3] = C['wood_dk']
    legs = op & (ys >= 21) & ~col('outline') & col('wood')
    lft = legs & ~np.roll(legs, 1, 1); a[lft, :3] = C['wood_lt']
    return a
out(refine_table(np.array(Lp('combat/table_portrait.png'))), 'combat/table_portrait.png', 'same silhouette; lit far edge, darker plank seams, grain dashes, nail heads, apron light/shadow rows + posts, lit left edge on the legs',
    anchor=[133, 39])
GMW = 'style pass + relight (hoodie folds, hair and beard get top-left light + bottom-right shade) + eye catch-light'
for k, kw in dict(gm_idle=dict(anchor=[22, 45]), gm_talk=dict(anchor=[22, 45]), gm_strip=dict(frames=2, frame_size=[44, 46], anchor=[22, 45])).items():
    out(RDc.gm(RS.style_sprite(np.array(Lp(f'combat/{k}.png')))[0]), f'combat/{k}.png', GMW, **kw)
out(RS.relight(np.array(Lp('combat/gm_screen.png')), hi=0.22, lo=0.24, spec=0.05), 'combat/gm_screen.png', 'relight (panel light top-left, shade bottom-right)')
for c in RDc.ORDER:
    out(RDc.d6_strip(c), f'combat/d6_{c}.png', 'REDRAWN 8x8 faces: rounded corners, lit top/left bevel, shaded bottom/right bevel, same pip grid + frame order (frame i = face i+1)',
        frames=6, frame_size=[8, 8], fps=12, anchor=[4, 7])
out(RDc.d6_all(), 'combat/d6_all.png', 'grid of the redrawn d6 faces (rows white,red,blue,green,yellow,black; columns 1-6)', frame_size=[8, 8])
out(RDc.d20(np.array(Lp('combat/d20_roll.png'))), 'combat/d20_roll.png', 'facet relight + glint; same silhouettes and numbers', frames=4, frame_size=[24, 24], fps=12, anchor=[12, 23])
out(RDc.d20(np.array(Lp('combat/d20_results.png'))), 'combat/d20_results.png', 'facet relight + glint on all 20 faces; digits untouched', frames=20, frame_size=[24, 24], anchor=[12, 23])
out(RDc.d20(np.array(Lp('combat/d20_nat20.png'))), 'combat/d20_nat20.png', 'facet relight + glint (gold)', anchor=[12, 23])

# ---------------- map pins ----------------
PW = dict(brinewick='blue-roof net shed, lit window, net-drying rack, pool with a little boat', ashgate='faceted grey cliff with a dark cave mouth (glinting eyes), plank lean-to off the cliff, campfire',
          pebblegate='crenellated gate wall + gatehouse with portcullis, red and blue striped stall tents')
for k, fn in RP.PINS.items():
    a = RS.relight(fn().image(trim=False), hi=0.2, lo=0.22)
    out(a, f'map/loc_{k}.png', 'NEW 32x32 map pin in the loc_* style (dirt island base): ' + PW[k], new=True, anchor=[16, 28], frame_size=[32, 32],
        place=k, note=f'region.json place {k}: set "sprite": "{k}" (currently "village") so map_screen.gd loads map/loc_{k}.png')

# ---------------- UI ----------------
out(RU.panel('parchment', 'sand', 'tan'), 'ui/panel_parchment.png', 'bevelled wood frame (light top-left, dark bottom-right, lip shadow), paper set below the frame, sparse seamless fibres, brass studs', nine_slice_margin=6)
out(RU.panel('ink', 'slate', 'outline'), 'ui/panel_dark.png', 'same frame as panel_parchment; ink fill with sparse slate fibres', nine_slice_margin=6)
out(RU.seat_hp(), 'ui/portrait/seat_bar_hp.png', '3-tone fill: coral top light, red body, red_dk bottom shade')
out(RU.seat_hp()[:, :1], 'ui/portrait/seat_bar_hp_tile.png', '1px column of the refined HP fill')
out(RU.seat_mp(), 'ui/portrait/seat_bar_mp.png', '3-tone fill: sky_lt top light, sky body, blue bottom shade')
out(RU.seat_mp()[:, :1], 'ui/portrait/seat_bar_mp_tile.png', '1px column of the refined MP fill')
out(RU.seat_hp_lowflash(), 'ui/portrait/seat_bar_hp_lowflash.png', '2 frames (42 each): refined HP fill / white-cream-amber flash', frames=2, frame_size=[42, 4])
out(RU.seat_frame(), 'ui/portrait/seat_bars_frame.png', 'same frame; 25/50/75% ticks in the empty tracks', anchor=[22, 0], hp_fill_rect=[1, 1, 42, 4], mp_fill_rect=[1, 6, 42, 3])
out(RU.seat_frame(True), 'ui/portrait/seat_bars_frame_active.png', 'active ring now bevelled (cream top-left, amber bottom-right) + ticks', anchor=[23, 1], hp_fill_rect=[2, 2, 42, 4], mp_fill_rect=[2, 7, 42, 3])
out(RU.enemy_hp(), 'ui/enemy_bar_hp.png', '3-tone fill matching the seat HP bar')
out(RU.hub_button(), 'ui/hub/hub_button.png', 'NEW hub button-bar button (9-slice, margin 6): bevelled wood frame, parchment face', new=True, nine_slice_margin=6, replaces='res://art/ui/btn_tan.png')
out(RU.hub_button(True), 'ui/hub/hub_button_down.png', 'NEW pressed/disabled state: bevel swapped, darker face', new=True, nine_slice_margin=6, replaces='res://art/ui/btn_tan_down.png')
out(RU.header_plate(), 'ui/hub/header_plate.png', 'NEW 9-slice (margin 4) parchment plate for the hub place name + blurb', new=True, nine_slice_margin=4, replaces='Widgets.header_plate() StyleBoxFlat')
for k, fn in RU.HUB_ICONS.items():
    a, _ = RS.style_sprite(RU._icon(fn))
    out(a, f'ui/hub/icon_{k}.png', f'NEW 16x16 hub icon ({k})', new=True, replaces={'travel': 'icon_run', 'fight': 'icon_attack', 'rest': 'icon_cover', 'quest': 'icon_skill', 'gear': 'icon_item'}[k])

# ---------------- item icons ----------------
NOTE = dict(oath_blade='blade 3px wide', reed_staff='shaft 3px', sap_crook='shaft + hook 3px', thorn_bow='limbs 4 passes + grip wrap', marsh_bow='limbs 4 passes + grip wrap',
            lamp_staff='shaft 3px', gravel_axe='haft 3px', pocket_knife='REDESIGN: folding knife, fat wooden handle + rivets, short broad blade, no guard', night_shard='REDESIGN: upright jagged violet crystal, wrapped grip, no metal')
for k, fn in RI.ICON_FIX.items():
    a, _ = RS.style_sprite(fn().image(trim=False)); out(a, f'ui/items/{k}.png', 'readability fix: ' + NOTE[k])
for k, fn in {**RI.QUEST, **RI.SHOP}.items():
    a, _ = RS.style_sprite(fn().image(trim=False))
    out(a, f'ui/items/{k}.png', 'NEW icon (refine-1 sample, kept)', new=True, before='tools/_work/pre_refine/repo_placeholders/ui/items/%s.png (parchment placeholder)' % k,
        kind='quest drop' if k in RI.QUEST else 'shop/craft')

for k, fn in {**RI2.QUEST2, **RI2.SHOP2}.items():
    a, _ = RS.style_sprite(fn().image(trim=False))
    out(a, f'ui/items/{k}.png', 'NEW icon (refine-2)', new=True, before='tools/_work/pre_refine/repo_placeholders/ui/items/%s.png (parchment placeholder)' % k,
        kind='quest drop' if k in RI2.QUEST2 else 'shop/craft')
ITEMS = json.load(open('/workspace/paladins-repo-ro/data/items.json'))
MISSING = [it['id'] for it in ITEMS if not os.path.exists(OUT + f'ui/items/{it["id"]}.png')]
OLD40 = set(os.listdir(PRE + 'ui/items'))
PLACEHOLDER = [it['id'] for it in ITEMS if f'ui/items/{it["id"]}.png' not in META and f'{it["id"]}.png' not in OLD40]
assert not MISSING and not PLACEHOLDER, (MISSING, PLACEHOLDER)
ICON_CHECK = dict(items=len(ITEMS), with_icon=len(ITEMS) - len(MISSING), missing=MISSING, still_placeholder=PLACEHOLDER, source='data/items.json @ 3103e38',
                  by_kind={kd: sum(1 for it in ITEMS if (it['slot'] or 'none') == kd) for kd in sorted({it['slot'] or 'none' for it in ITEMS})})
print('icon check', ICON_CHECK)

# ---------------- seat gear overlays: all 26 ----------------
CHAIR = np.array(Lp('paperdoll/back/chair_back.png'))[..., 3] > 0
GEAR_IDS = sorted(f[:-4] for f in os.listdir(PRE + 'paperdoll/gear') if f.endswith('.png'))
assert len(GEAR_IDS) == 26, GEAR_IDS
for k in GEAR_IDS:
    held = k in RG.HELD
    what = ('held: 6x4 gloved fist (8x6 with its outline) with lit knuckles + finger creases on the grip; ' if held else
            ('no fist (%s); ' % RG.NO_FIST[k]) if k in RG.NO_FIST else 'armour overlay; ') + 'relit from the top-left (cloth/metal/wood ramps, metal spec)'
    if k in RG.NEW: what = 'REDRAWN shape + ' + what
    out(RG.finish(RG.build(k), CHAIR), f'paperdoll/gear/{k}.png', what, anchor=[24, 77], canvas=[48, 78], fist=held)

# ---------------- back-view paperdoll layers + recomposed party seats ----------------
RAW = OUT + 'tools/_work/doll_raw/'
def src(rel):
    p = PRE + rel if os.path.exists(PRE + rel) else RAW + rel
    return np.array(Image.open(p).convert('RGBA'))
BACK = sorted(f for f in set(os.listdir(PRE + 'paperdoll/back')) | set(os.listdir(RAW + 'paperdoll/back')) if f.endswith('.png'))
REF_L = {}
for f in BACK:
    rel = 'paperdoll/back/' + f
    if f.startswith('body_back_skin'): REF_L[rel] = src(rel); continue           # skin layers untouched: their tones ARE the skin choice
    kind = RD.kind_of(rel); cls = f[len('class_back_'):-4].split('_')[0] if f.startswith('class_back_') else None
    caster = RD.head_mask(src, cls) if (cls and not f.endswith('_hat.png')) else None
    a = RD.refine_layer(src(rel), kind, caster); REF_L[rel] = a
    new = not os.path.exists(PRE + rel)
    out(a, rel, {'hair': 'relight inside the 4 grayscale hair keys only (runtime ramp tint still works)', 'outfit': 'relight inside the 3 grayscale outfit keys only (tint still works)',
                 'colour': 'relight (cloth/metal/leather/wood ramps, metal spec)' + (' + collar/hood shadow cast from the head' if caster is not None else '')}[kind],
        new=new, before=None if not new else 'tools/_work/doll_raw/' + rel + ' (unrefined build_doll output)', anchor=[24, 77], canvas=[48, 78])
get_ref = lambda rel: REF_L[rel]
SEATS = []
for c in RD.SEAT_DEFAULTS:
    variants = [''] + (['_noweapon'] if os.path.exists(PRE + f'paperdoll/back/class_back_{c}_noweapon.png') else []) + (['_noweapon_noquiver'] if c == 'ranger' else [])
    for v in variants:
        for st, act in (('idle', False), ('active', True)):
            rel = f'party/seat_{c}_{st}{v}.png'; new = not os.path.exists(PRE + rel)
            out(RD.compose(get_ref, c, act, v), rel, 'recomposed (seat_recipe) from the refined back layers', new=new, before=None if not new else 'none (new in refine-2)', anchor=[24, 77], canvas=[48, 78])
            SEATS.append(rel)

# ---------------- kit / gear seats for the refine sheets + final renders ----------------
KIT = {'paladin': ('oath_blade', 'kettle_shield'), 'wizard': ('reed_staff',), 'ranger': ('thorn_bow',), 'bard': ('road_lute',), 'cleric': ('chapel_mace', 'hymn_board'),
       'rogue': ('pocket_knife',), 'barbarian': ('gravel_axe',), 'druid': ('sap_crook',)}                       # data/classes.json kits
LATE = {'paladin': ('kiln_sword', 'oak_buckler', 'keep_plate'), 'wizard': ('lamp_staff', 'void_lens', 'moon_robe'), 'ranger': ('howl_fang', 'lurker_scale'),
        'bard': ('road_lute', 'travel_coat'), 'cleric': ('chapel_mace', 'kettle_shield', 'hedge_mail'), 'rogue': ('night_shard', 'reed_wrap'),
        'barbarian': ('sunbrand', 'kiln_plate'), 'druid': ('sap_crook', 'glass_orb', 'reed_wrap')}           # Gravel Keep party (class tags/weights respected)
OFFS = {'kettle_shield', 'hymn_board', 'oak_buckler', 'glass_orb', 'void_lens'}
ARMOR = {'travel_coat', 'reed_wrap', 'hedge_mail', 'kiln_plate', 'moon_robe', 'keep_plate', 'lurker_scale'}
BOWS = {'thorn_bow', 'marsh_bow'}
NOWEAPON = [c for c in RD.SEAT_DEFAULTS if os.path.exists(PRE + f'paperdoll/back/class_back_{c}_noweapon.png')]
def class_layer(cls, main):
    """THE QUIVER RULE (manifest paperdoll.ranger_quiver): no main-hand weapon -> class_back_<c>; main-hand weapon -> class_back_<c>_noweapon
    when the class has one; ranger with a main-hand weapon whose tag is not 'bow' -> class_back_ranger_noweapon_noquiver."""
    if not main or cls not in NOWEAPON: return f'paperdoll/back/class_back_{cls}.png'
    if cls == 'ranger' and main not in BOWS: return 'paperdoll/back/class_back_ranger_noweapon_noquiver.png'
    return f'paperdoll/back/class_back_{cls}_noweapon.png'
def gear_seat(L, G, cls, items, active=False):
    """steps_with_gear order. L(rel)->array of a back layer, G(id)->array of a gear overlay."""
    d = RD.SEAT_DEFAULTS[cls]; main = next((x for x in items if x not in OFFS and x not in ARMOR), None)
    off = next((x for x in items if x in OFFS), None); arm = next((x for x in items if x in ARMOR), None)
    im = np.zeros((78, 48, 4), np.uint8); RD.over(im, L(f'paperdoll/back/body_back_skin_{d["skin"]}.png'))
    if d['outfit']: RD.over(im, RD.remap(L('paperdoll/back/outfit_back.png'), RD.KO, RD.OUTFIT_RAMPS[d['outfit']]))
    RD.over(im, L(class_layer(cls, main)))
    if arm: RD.over(im, G(arm))
    hl = RD.remap(L(f'paperdoll/back/hair_back_{d["hair"]}.png'), RD.KH, RD.HAIR_RAMPS[d['hair_color']]); hl[:RD.HAT_CLIP_BACK[cls]] = 0; RD.over(im, hl)
    RD.over(im, L(f'paperdoll/back/class_back_{cls}_hat.png'))
    if off: RD.over(im, G(off))
    if main: RD.over(im, G(main))
    RD.over(im, L('paperdoll/back/chair_back.png'))
    return RD.active_ring(im) if active else im
LB = lambda rel: src(rel if not rel.endswith('noquiver.png') else 'paperdoll/back/class_back_ranger_noweapon.png')   # before: no noquiver layer existed
GB = lambda g: np.array(Lp(f'paperdoll/gear/{g}.png')); GA = lambda g: np.array(Ln(f'paperdoll/gear/{g}.png'))
for c in KIT:
    for st, act in (('idle', False), ('active', True)):
        for tag, L, G in (('before', LB, GB), ('after', get_ref, GA)):
            rel = f'approval/refine/parts/{tag}/seat_{c}_{st}.png'; save(Image.fromarray(gear_seat(L, G, c, KIT[c], act), 'RGBA'), rel)
            META[rel] = dict(status='review', anchor=[24, 77], notes=f'QA seat for the refine sheets ({tag}): {c} with the data/classes.json kit {", ".join(KIT[c])}, steps_with_gear order + quiver rule.')
        rel = f'approval/refine/parts/late/seat_{c}_{st}.png'; save(Image.fromarray(gear_seat(get_ref, GA, c, LATE[c], act), 'RGBA'), rel)
        META[rel] = dict(status='review', anchor=[24, 77], notes=f'QA seat for the final Gravel Keep render: {c} in {", ".join(LATE[c])} (steps_with_gear order + quiver rule).')

QUIVER = dict(status='review',
    rule=('Ranger back layer: NO main-hand weapon -> paperdoll/back/class_back_ranger.png (baked bow + quiver). Main-hand BOW (item tag "bow": thorn_bow, marsh_bow) -> '
          'class_back_ranger_noweapon.png (baked bow removed, quiver stays; the bow overlay is slung). Main-hand weapon with ANY OTHER tag (dagger: pocket_knife, night_shard, '
          'howl_fang, ...) -> class_back_ranger_noweapon_noquiver.png (no quiver, no fletching: no arrows without a bow). Prebuilt seats follow the same rule: '
          'party/seat_ranger_<state>.png / _noweapon.png / _noweapon_noquiver.png.'),
    layers=dict(none='paperdoll/back/class_back_ranger.png', bow='paperdoll/back/class_back_ranger_noweapon.png', other='paperdoll/back/class_back_ranger_noweapon_noquiver.png'),
    seats=dict(none=['party/seat_ranger_idle.png', 'party/seat_ranger_active.png'], bow=['party/seat_ranger_idle_noweapon.png', 'party/seat_ranger_active_noweapon.png'],
               other=['party/seat_ranger_idle_noweapon_noquiver.png', 'party/seat_ranger_active_noweapon_noquiver.png']),
    bow_tags=['bow'],
    gdscript=('# art_pack.gd pick_class_back / seat_sheet_rel: pass the main-hand item tag\n'
              'if class_id == "ranger" and main_weapon and main_tag != "bow":\n'
              '    return "paperdoll/back/class_back_ranger_noweapon_noquiver.png"  # seats: party/seat_ranger_<state>_noweapon_noquiver.png'))
FIST = dict(rule=('Every HELD main-hand weapon / held focus overlay carries a 6x4 gloved fist (8x6 including its #120c18 outline) on the grip: lit sand/parchment knuckle row '
                  'with 3 finger creases, tan fingers, wood palm shade, thumb on the left. Slung or strapped items carry NO fist.'), held=RG.HELD, no_fist=RG.NO_FIST)

json.dump(dict(meta=META, refined=REFINED, style=RS.STYLE, before_root='tools/_work/pre_refine/', kit=KIT, late=LATE, quiver=QUIVER, fist=FIST, icon_check=ICON_CHECK, seats=SEATS),
          open(OUT + 'tools/_work/meta_refine.json', 'w'), indent=1)
print('refined/new', len(REFINED), '(new', sum(r['new'] for r in REFINED), ')')
