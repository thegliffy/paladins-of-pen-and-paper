"""REFINE PASS - PHASE 1 (2026-10-01): refines/creates the pieces shown in the before/after sheets (approval/refine/), status 'review'.
Run after build_items.py and before compose.py. 'Before' = tools/_work/pre_refine/ (frozen snapshot of the pack + repo placeholders).
Pieces NOT listed here are untouched in phase 1 (the full pass waits for approval)."""
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
    META[rel] = dict(status='review', refine='phase1', what=what, before=(before or ('tools/_work/pre_refine/' + rel if not new else 'none (new file)')), **kw)
    REFINED.append(dict(path=rel, new=new, what=what))

# ---------------- backdrops ----------------
BG = dict(millpond=('meadow: calm perspective grass (no dirt blotches), two-depth tree line, knoll + windmill, pond with banks, worn path, sparse tufts/flowers', False),
          howling_cleft=('cave: natural faceted cliff (Voronoi rock facets, crevices, lit top), irregular mouth with passage floor, grey grit floor with perspective cracks, faceted boulders, puddle; no camo floor', False),
          candlewick=('town: cobbled lane in perspective, calm packed-earth square with soft ruts, well/barrels/crates/lamp props, steam from chimneys', False),
          brinewick=('NEW town (coast fishing town): sea horizon + sail, net shed + net-drying rack, salt-bread bakery with striped awning and loaf sign, damp stone forge with glowing arch/anvil/quench barrel/steam, plank boardwalk on pilings, wet sand with tide pools', True))
for k, (what, new) in BG.items():
    rel = f'combat/bg_{k}_portrait.png'
    out(RS.to_palette(getattr(RB, k)().image()), rel, what,              # snap guards stray non-palette px (2 black px at a house seam)
        before=('tools/_work/pre_refine/repo_placeholders/' + rel + ' (repo placeholder)') if new else None, new=new,
        anchor=[0, 0], horizon_y=141, monster_feet_band=[222, 266], calm_below_y=300, **({'region': 'greenmere', 'town': True} if new else {}))

# ---------------- monsters in the phase-1 scenes: style pass + contact shadow ----------------
SCENE_MON = ['goblin', 'bramblet', 'grinmud_toad', 'bat', 'gloomgrub', 'dripfang']
FLYING = {'bat', 'squallgull'}
def shadow_params(m):
    a = np.array(Lp(f'monsters/{m}/{m}_idle.png'))[:, :80]; op = a[..., 3] > 0
    ys, xs = np.nonzero(op)
    if m in FLYING: return dict(cx=40, rx=max(6, min(12, (xs.max() - xs.min()) * 0.22)), ry=2.0, fly=True, area=op.sum())
    low = op[58:67]; xs2 = np.nonzero(low.any(0))[0]
    return dict(cx=(xs2.min() + xs2.max() + 1) / 2, rx=float(np.clip((xs2.max() - xs2.min()) / 2 + 4, 10, 28)), ry=3.0, fly=False, area=op.sum())
for m in SCENE_MON:
    sp = shadow_params(m)
    for anim in ('idle', 'attack', 'hit', 'death', 'still'):
        rel = f'monsters/{m}/{m}_{anim}.png'; a = np.array(Lp(rel)); nf = a.shape[1] // 80; outa = a.copy()
        for f in range(nf):
            fr = a[:, f * 80:(f + 1) * 80]; fr, _ = RS.style_sprite(fr); op = fr[..., 3] > 0
            ratio = op.sum() / max(1, sp['area'])
            if anim == 'death' and ratio < 0.2: outa[:, f * 80:(f + 1) * 80] = fr; continue
            cx = sp['cx']
            if not sp['fly']:
                low = np.nonzero(op[58:67].any(0))[0]
                if len(low): cx = (low.min() + low.max() + 1) / 2
            rx = sp['rx'] * (min(1.0, np.sqrt(ratio)) if anim == 'death' else 1.0)
            outa[:, f * 80:(f + 1) * 80] = RS.contact_shadow(fr, cx, 64 if sp['fly'] else 65, rx, sp['ry'])
        out(outa, rel, 'style pass (closed #120c18 outline, despeckle) + 50% checker contact shadow under the feet' + (' (flyer: small shadow at the feet anchor)' if sp['fly'] else ''),
            frames=nf, frame_size=[80, 70], anchor=[40, 64])

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
gm, n = RS.style_sprite(np.array(Lp('combat/gm_idle.png')))
out(gm, 'combat/gm_idle.png', f'style pass only ({n} speckle px cleaned, outline closed)', anchor=[22, 45])

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
    out(a, f'ui/items/{k}.png', 'NEW icon (sample for the phase-1 sheet)', new=True, before='tools/_work/pre_refine/repo_placeholders/ui/items/%s.png (parchment placeholder)' % k,
        kind='quest drop' if k in RI.QUEST else 'shop/craft')

# ---------------- seat gear overlays ----------------
CHAIR = np.array(Ln('paperdoll/back/chair_back.png'))[..., 3] > 0
GNOTE = dict(oath_blade='gloved fist on the grip, blade 3.6px', chapel_mace='gloved fist, haft 3px', pocket_knife='REDESIGN: folding knife (fat handle, broad short blade) + fist',
             night_shard='REDESIGN: tall jagged crystal shard + wrapped grip + fist', reed_staff='staff 3.4px + fist', sap_crook='staff/hook 3.2-3.4px + fist', thorn_bow='limbs 3.4px, grip wrap, carry strap (slung: no hand)')
for k, fn in RI.GEAR_FIX.items():
    a = fn().image(trim=False); a[CHAIR] = 0
    out(a, f'paperdoll/gear/{k}.png', GNOTE[k], anchor=[24, 77], canvas=[48, 78])

# ---------------- kit seats for the before/after scenes (recipe order, noweapon when a main weapon is held) ----------------
K = [C['slate'], C['gray'], C['silver'], C['mist']]
HAIR_RAMPS = {'black': ['outline', 'ink', 'slate', 'gray'], 'brown': ['bark', 'wood_dk', 'wood', 'wood_lt'], 'blonde': ['wood_lt', 'tan', 'gold', 'cream'],
    'ginger': ['red_dk', 'orange', 'amber', 'gold'], 'white': ['gray', 'silver', 'mist', 'white'], 'blue': ['navy', 'blue_dk', 'blue', 'sky'], 'green': ['pine_dk', 'leaf_dk', 'leaf', 'grass']}
OUTFIT_RAMPS = {'white': ['silver', 'mist', 'white'], 'red': ['red_dk', 'red', 'coral'], 'blue': ['blue_dk', 'blue', 'sky'], 'purple': ['plum_dk', 'plum', 'violet'],
    'green': ['pine', 'leaf_dk', 'leaf'], 'yellow': ['orange', 'amber', 'gold'], 'brown': ['wood_dk', 'wood', 'wood_lt'], 'dark': ['ink', 'slate', 'gray']}
HAT_CLIP_BACK = {'paladin': 33, 'wizard': 21, 'ranger': 60, 'bard': 21, 'cleric': 19, 'rogue': 60, 'barbarian': 30, 'druid': 0}
SEATD = {'paladin': (2, 2, 'brown', 'white'), 'wizard': (1, 5, 'blonde', 'blue'), 'ranger': (3, 4, 'ginger', 'green'), 'bard': (5, 6, 'black', 'red'),
    'cleric': (4, 2, 'white', 'white'), 'rogue': (2, 3, 'black', 'dark'), 'barbarian': (3, 8, 'ginger', None), 'druid': (6, 1, 'white', 'green')}
NOWEAPON = ['paladin', 'druid', 'wizard', 'barbarian', 'bard', 'ranger']
KIT = {'paladin': ('oath_blade', 'kettle_shield'), 'wizard': ('reed_staff',), 'ranger': ('thorn_bow',), 'bard': ('road_lute',), 'cleric': ('chapel_mace', 'hymn_board'),
       'rogue': ('pocket_knife',), 'barbarian': ('gravel_axe',), 'druid': ('sap_crook',)}                       # data/classes.json kits
OFFS = {'kettle_shield', 'hymn_board', 'oak_buckler', 'glass_orb', 'void_lens'}
def remap(im, keys, cols):
    a = np.array(im); o = a.copy()
    for k, c in zip(keys, cols): m = (a[..., :3] == k).all(-1) & (a[..., 3] > 0); o[m, :3] = C[c]
    return Image.fromarray(o, 'RGBA')
def kit_seat(L, cls, active=False):
    skin, hair, hcol, ocol = SEATD[cls]; g = {('off' if x in OFFS else 'main'): x for x in KIT[cls]}
    im = Image.new('RGBA', (48, 78)); im.alpha_composite(L(f'paperdoll/back/body_back_skin_{skin}.png'))
    if ocol: im.alpha_composite(remap(L('paperdoll/back/outfit_back.png'), K[1:], OUTFIT_RAMPS[ocol]))
    im.alpha_composite(L(f'paperdoll/back/class_back_{cls}_noweapon.png' if ('main' in g and cls in NOWEAPON) else f'paperdoll/back/class_back_{cls}.png'))
    ha = np.array(remap(L(f'paperdoll/back/hair_back_{hair}.png'), K, HAIR_RAMPS[hcol])); ha[:HAT_CLIP_BACK[cls]] = 0
    im.alpha_composite(Image.fromarray(ha, 'RGBA')); im.alpha_composite(L(f'paperdoll/back/class_back_{cls}_hat.png'))
    if 'off' in g: im.alpha_composite(L(f'paperdoll/gear/{g["off"]}.png'))
    if 'main' in g: im.alpha_composite(L(f'paperdoll/gear/{g["main"]}.png'))
    im.alpha_composite(L('paperdoll/back/chair_back.png'))
    if active:
        a = np.array(im); a2 = np.zeros_like(a); a2[:-3] = a[3:]; op = a2[..., 3] > 0
        n = np.zeros_like(op); n[1:] |= op[:-1]; n[:-1] |= op[1:]; n[:, 1:] |= op[:, :-1]; n[:, :-1] |= op[:, 1:]
        a2[n & ~op] = C['gold'] + (255,); im = Image.fromarray(a2, 'RGBA')
    return im
for c in KIT:
    for st, act in (('idle', False), ('active', True)):
        for tag, L in (('before', Lp), ('after', Ln)):
            rel = f'approval/refine/parts/{tag}/seat_{c}_{st}.png'; save(kit_seat(L, c, act), rel)
            META[rel] = dict(status='review', anchor=[24, 77], notes=f'QA seat for the refine sheets ({tag}): {c} with the data/classes.json kit {", ".join(KIT[c])}, seat_recipe order, noweapon layer when a main weapon is held.')

json.dump(dict(meta=META, refined=REFINED, style=RS.STYLE, before_root='tools/_work/pre_refine/', kit=KIT), open(OUT + 'tools/_work/meta_refine.json', 'w'), indent=1)
print('refined/new', len(REFINED), '(new', sum(r['new'] for r in REFINED), ')')
