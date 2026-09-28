"""Palette files, scene test, contact sheet, validation, manifest."""
import json, os, glob, datetime
import numpy as np
from PIL import Image
import pal
from pal import C, OUT, save, text, text_w, HEX, NAMES
W_ = OUT + 'tools/_work/'
def L(rel): return Image.open(OUT + rel).convert('RGBA')
def frame_of(rel, i, fw):
    im = L(rel); return im.crop((i * fw, 0, (i + 1) * fw, im.height))
META = {}
for f in ('meta_cut.json', 'meta_proc.json', 'meta_doll.json', 'meta_skills.json', 'meta_regions.json', 'meta_items.json'):
    d = json.load(open(W_ + f)); META.update(d['meta'] if 'meta' in d else d)
DOLL = json.load(open(W_ + 'meta_doll.json')); SKM = json.load(open(W_ + 'meta_skills.json'))['motifs']; SKK = json.load(open(W_ + 'meta_skills.json'))['kinds']

# ---------------- palette ----------------
sw = Image.new('RGBA', (48 * 8, 8))
for i, c in enumerate(pal.PAL): sw.paste(c + (255,), (i * 8, 0, i * 8 + 8, 8))
save(sw, 'palette/palette48.png')
with open(OUT + 'palette/palette48.gpl', 'w') as f:
    f.write('GIMP Palette\nName: Paladins of Pen and Paper 48\nColumns: 8\n#\n')
    for c, n in zip(pal.PAL, NAMES): f.write('%3d %3d %3d\t%s\n' % (c + (n,)))
open(OUT + 'palette/palette48.hex', 'w').write('\n'.join(HEX) + '\n')
META['palette/palette48.png'] = dict(notes='48 swatches, 8x8 each, index order = palette48.hex order.')

# ---------------- doll composition from pack files ----------------
def doll_front(skin, head, hair, hcol, ocol, cls=None, hat=False):
    im = Image.new('RGBA', (32, 48))
    if cls == 'barbarian': ocol = None     # bare arms: barbarian skips outfit_base
    for rel in [f'paperdoll/body_skin_{skin}.png'] + ([f'paperdoll/tinted/outfit_{ocol}.png'] if ocol else []) + ([f'paperdoll/class_{cls}.png'] if cls else []) + \
               [f'paperdoll/tinted/head_{head}_skin{skin}.png'] + ([f'paperdoll/tinted/hair_{hair}_{hcol}.png'] if hair > 1 else []) + \
               ([f'paperdoll/class_{cls}_hat.png'] if cls and hat else []):
        l = L(rel)
        if 'hair_' in rel and cls and hat:
            a = np.array(l); a[:META[f'paperdoll/class_{cls}_hat.png']['hair_clip_y']] = 0; l = Image.fromarray(a)
        im.alpha_composite(l)
    return im
def portrait_of(im, rect=(6, 8, 20, 20)):
    x, y, w, h = rect; return im.crop((x, y, x + w, y + h))

# ---------------- scene test ----------------
S = L('combat/bg_forest.png')
def put(im, ax, ay, anchor):
    S.alpha_composite(im, (ax - anchor[0], ay - anchor[1]))
mons = [('goblin', 128, 132), ('bat', 238, 112), ('slime', 348, 134)]
for n, x, y in mons:
    m = META[f'monsters/{n}/{n}_idle.png']; im = frame_of(f'monsters/{n}/{n}_idle.png', 0, m['frame_size'][0])
    put(im, x, y, m['anchor'])
    hx, hy = x - m['anchor'][0] + m['hp_bar_anchor'][0], y - m['anchor'][1] + m['hp_bar_anchor'][1]
    bg = L('ui/enemy_bar_bg.png'); put(bg, hx, hy, (16, 4))
    fill = L('ui/enemy_bar_hp.png'); pct = {'goblin': 1.0, 'bat': 0.6, 'slime': 0.85}[n]
    fill = fill.crop((0, 0, max(1, int(30 * pct)), 3)); S.alpha_composite(fill, (hx - 16 + 1, hy - 4 + 1))
# damage number on the bat
dn = L('ui/dmg_font_hp.png')
for i, ch in enumerate('-7'):
    g = dn.crop(('0123456789+-'.index(ch) * 7, 0, '0123456789+-'.index(ch) * 7 + 7, 9)); S.alpha_composite(g, (262 + i * 6, 68))
# initiative strip
ini = []
for n in ('goblin', 'bat', 'slime'):
    ini.append(L(f'monsters/{n}/{n}_portrait.png'))
party = [doll_front(2, 1, 2, 'brown', 'white', 'paladin', True), doll_front(1, 5, 5, 'blonde', 'blue', 'wizard', True),
         doll_front(3, 4, 4, 'ginger', 'green', 'ranger', True), doll_front(5, 3, 6, 'black', 'red', 'bard', True)]
ini += [portrait_of(p) for p in party[:2]]
x0 = 240 - (len(ini) * 26 - 2) // 2
for i, p in enumerate(ini):
    fr = L('ui/portrait_frame_active.png' if i == 0 else 'ui/portrait_frame.png'); fr.alpha_composite(p, (2, 2)); S.alpha_composite(fr, (x0 + i * 26, 3))
# GM, table, screen, dice
put(L('combat/gm_idle.png'), 240, 184, (22, 45))
put(L('combat/table.png'), 240, 222, (150, 43))
put(L('combat/gm_screen.png'), 212, 196, (L('combat/gm_screen.png').width // 2, L('combat/gm_screen.png').height - 1))
put(frame_of('combat/d20_roll.png', 3, 24), 254, 198, (12, 23))
put(frame_of('combat/d6_blue.png', 4, 8), 272, 190, (4, 7)); put(frame_of('combat/d6_red.png', 2, 8), 283, 194, (4, 7))
# seats
for i, (c, x) in enumerate(zip(['paladin', 'wizard', 'ranger', 'bard'], [70, 162, 318, 408])):
    put(L(f'party/seat_{c}_{"active" if i == 0 else "idle"}.png'), x, 238, (24, 77))
# HP cards
for i, p in enumerate(party):
    cd = L('ui/hp_mp_card.png'); cd.alpha_composite(portrait_of(p), (4, 4))
    hp = [1.0, 0.7, 0.45, 0.9][i]; mp = [0.5, 1.0, 0.6, 0.8][i]
    cd.alpha_composite(L('ui/bar_hp.png').crop((0, 0, int(54 * hp), 5)), (36, 6)); cd.alpha_composite(L('ui/bar_mp.png').crop((0, 0, int(54 * mp), 5)), (36, 16))
    S.alpha_composite(cd, (6 + i * 98, 240))
for i, n in enumerate(['attack', 'skill', 'item', 'cover', 'run']):
    S.alpha_composite(L(f'ui/btn_{n}{"_active" if i == 0 else ""}.png'), (446, 88 + i * 30))
save(S, 'scene_test.png'); save(S.resize((1920, 1080), Image.NEAREST), 'scene_test_4x.png')
META['scene_test.png'] = dict(notes='480x270 composite built only from pack files (QA).'); META['scene_test_4x.png'] = dict(notes='4x nearest upscale of scene_test.png.')

# ======================= PORTRAIT (270x480) =======================
PWID, PHEI = 270, 480
def nine(rel, Wd, Ht, m=6):
    src = L(rel); sw_, sh_ = src.size; out = Image.new('RGBA', (Wd, Ht))
    def tile(box, dst):
        piece = src.crop(box); pw, ph = piece.size
        x0, y0, x1, y1 = dst
        for yy in range(y0, y1, ph):
            for xx in range(x0, x1, pw):
                out.paste(piece.crop((0, 0, min(pw, x1 - xx), min(ph, y1 - yy))), (xx, yy))
    xs_ = [0, m, sw_ - m, sw_]; ys_ = [0, m, sh_ - m, sh_]; xd = [0, m, Wd - m, Wd]; yd = [0, m, Ht - m, Ht]
    for j in range(3):
        for i in range(3): tile((xs_[i], ys_[j], xs_[i + 1], ys_[j + 1]), (xd[i], yd[j], xd[i + 1], yd[j + 1]))
    return out
def upsc(im, k): return im.resize((im.width * k, im.height * k), Image.NEAREST)
DIG = L('ui/dmg_font_hp.png')

# ---------- v6 per-character action bar ----------
SKJ = json.load(open(W_ + 'meta_skills.json')); BSL = SKJ['bar_slots']; COSTS = SKJ['costs']
def dig35(im, x, y, sN):
    d = L('ui/portrait/digits_3x5.png')
    for j, ch in enumerate(sN): im.alpha_composite(d.crop((int(ch) * 4, 0, int(ch) * 4 + 3, 5)), (x + j * 4, y))
def render_bar(cls, selected=0, cooldown=None, cd_turns=2, locked=None, name=None):
    im = Image.new('RGBA', (270, 60)); bar = L('ui/portrait/action_bar_v2.png'); im.alpha_composite(bar, (0, 10))
    tab = L('ui/portrait/name_tab.png'); nm = (name or cls).upper(); text(tab, 5, 2, nm, C['outline']); im.alpha_composite(tab, (4, 0))
    for n in ('attack', 'cover'):
        im.alpha_composite(L(f'ui/portrait/ability_{n}.png'), (BSL[n][0], 10 + BSL[n][1])); t_ = n.upper(); text(im, BSL[n][0] + 16 - text_w(t_) // 2, 10 + 38, t_, C['mist'])
    for k in range(5):
        key = f'{cls}_{k+1}'; x, y = BSL['skills'][k]; y += 10; passive = SKK[key] == 'passive'
        if passive: sl = L('ui/skills/skill_slot_passive.png')
        elif k == locked: sl = L('ui/skills/skill_slot_locked.png')
        elif k == selected: sl = L('ui/skills/skill_slot_active.png')
        else: sl = L('ui/skills/skill_slot.png')
        sl.alpha_composite(L(f'ui/skills/{key}.png'), (6, 6))
        if passive:
            sl.alpha_composite(L('ui/portrait/passive_dim_mask.png'), (4, 4)); sl.paste(C['plum'] + (255,), (24, 23, 31, 31)); text(sl, 26, 24, 'P', C['cream'])
        elif k == locked:
            sl.alpha_composite(L('ui/skills/skill_cooldown_mask.png'), (4, 4)); sl.alpha_composite(L('ui/portrait/lock_icon.png'), (11, 11))
        elif k == cooldown:
            m = L('ui/skills/skill_cooldown_mask.png'); sl.alpha_composite(m.crop((0, 8, 24, 24)), (4, 12))
            sl.paste(C['outline'] + (255,), (12, 12, 20, 20)); dig35(sl, 14, 14, str(cd_turns))
        im.alpha_composite(sl, (x, y))
        cst = COSTS[cls][k]
        if cst is not None:
            b = L('ui/portrait/cost_badge_0_9.png').crop((cst * 16, 0, cst * 16 + 16, 7)); im.alpha_composite(b, (BSL['cost_badges'][k][0], 10 + BSL['cost_badges'][k][1]))
        else: text(im, x + 4, 10 + 38, 'PAS', C['gold'])
    for n in ('item', 'run'): im.alpha_composite(L(f'ui/portrait/mini_{n}.png'), (BSL[n][0], 10 + BSL[n][1]))
    return im
EX = Image.new('RGBA', (270 + 8, 3 * 72 + 4), C['gray'] + (255,))
for r, (c, sel, cd, lk) in enumerate([('paladin', 0, 2, 3), ('wizard', 2, 0, None), ('rogue', 4, 1, None)]):
    EX.alpha_composite(render_bar(c, sel, cd, 2, lk), (4, 4 + r * 72 + 8))
    text(EX, 6, 4 + r * 72, f'{c.upper()}: SELECTED={c}_{sel+1}  COOLDOWN={c}_{cd+1}' + (f'  LOCKED={c}_{lk+1}' if lk is not None else '') + ('  (5 = PASSIVE)' if SKK[f'{c}_5'] == 'passive' else '  (5 = ACTIVE)'), C['cream'])
save(EX, 'ui/portrait/action_bar_examples.png'); save(EX.resize((EX.width * 3, EX.height * 3), Image.NEAREST), 'ui/portrait/action_bar_examples_3x.png')
META['ui/portrait/action_bar_examples.png'] = dict(notes='QA: the v6 bar swapping per active character (paladin: selected/cooldown/locked + passive 5; wizard: passive 5; rogue: all 5 active). Not a runtime asset.')
META['ui/portrait/action_bar_examples_3x.png'] = dict(notes='3x nearest.')

# ---------- scene_test_portrait ----------
P = L(globals().get('SCENE_BG', 'combat/bg_forest_portrait.png'))
def pput(im, ax, ay, anchor): P.alpha_composite(im, (ax - anchor[0], ay - anchor[1]))
PPARTY = ['paladin', 'cleric', 'rogue', 'druid', 'wizard']          # v5: max party 5, mixed
def dflt_front(c):
    d = DOLL['seat_defaults'][c]; return doll_front(d['skin'], d['head'], d['hair'], d['hair_color'], d['outfit'], c, d['hat'])
pparty = [dflt_front(c) for c in PPARTY]
# initiative strip: 5 party + 3 monsters, scrollable-looking (dark rail, next-round portrait clipped at the right edge)
INIT = globals().get('SCENE_INIT', [('p', 0), ('m', 'goblin'), ('p', 4), ('p', 3), ('m', 'bat'), ('p', 2), ('m', 'slime'), ('p', 1)])
ini = [portrait_of(pparty[v]) if k == 'p' else L(f'monsters/{v}/{v}_portrait.png') for k, v in INIT]
INI_Y, INI_STEP, INI_X0 = 3, 29, 4
rail = nine('ui/panel_dark.png', 270, 30); P.alpha_composite(rail, (0, INI_Y - 3))
strip_im = Image.new('RGBA', (300, 24))
for i, p in enumerate(ini + [portrait_of(pparty[0])]):
    fr = L('ui/portrait_frame_active.png' if i == 0 else 'ui/portrait_frame.png'); fr.alpha_composite(p, (2, 2))
    xx = i * INI_STEP + (1 if i == len(ini) else 0); strip_im.alpha_composite(fr, (xx, 0))
    if i == len(ini) - 1:
        rx = xx + 26; strip_im.paste(C['gold'] + (255,), (rx, 1, rx + 1, 23))         # round divider
P.alpha_composite(strip_im.crop((0, 0, 256 - INI_X0, 24)), (INI_X0, INI_Y))
for k_, (x_, y_) in enumerate([(265, INI_Y + 9), (266, INI_Y + 10), (265, INI_Y + 11), (264, INI_Y + 8), (264, INI_Y + 12), (264, INI_Y + 10)]): P.putpixel((x_, y_), C['cream'] + (255,))   # scroll chevron
PMON = globals().get('SCENE_PMON', [('goblin', 52, 262), ('bat', 135, 222), ('slime', 220, 266)])
for n, x, y in PMON:
    m = META[f'monsters/{n}/{n}_idle.png']; im = frame_of(f'monsters/{n}/{n}_idle.png', 0, 80); pput(im, x, y, m['anchor'])
    hx, hy = x - 40 + m['hp_bar_anchor'][0], y - 64 + m['hp_bar_anchor'][1]
    pput(L('ui/enemy_bar_bg.png'), hx, hy, (16, 4)); pct = globals().get('SCENE_PCT', {'goblin': 1.0, 'bat': 0.6, 'slime': 0.85})[n]
    P.alpha_composite(L('ui/enemy_bar_hp.png').crop((0, 0, int(30 * pct), 3)), (hx - 15, hy - 3))
for i, ch in enumerate('-7'):
    k = '0123456789+-'.index(ch); P.alpha_composite(DIG.crop((k * 7, 0, k * 7 + 7, 9)), (158 + i * 6, 162))
BAR_Y = 430; TAB_Y = BAR_Y - 10; CARD_Y = TAB_Y - 2;   # v7: no card row; CARD_Y = feet row of the front seats (1px above the name tab) CARD_STEP = 54; CARD_X0 = 1
SEAT_X = [27, 81, 135, 189, 243]; SEAT_Y = [CARD_Y, CARD_Y - 4, CARD_Y, CARD_Y - 4, CARD_Y]     # chair feet sit on the card top; 2nd/4th seats 4px higher
TBL_Y = CARD_Y - 36                                                                            # table bottom row
pput(L('combat/gm_idle.png'), 135, TBL_Y - 40 + 9, (22, 45))
pput(L('combat/table_portrait.png'), 135, TBL_Y, (133, 39))
scr = L('combat/gm_screen.png'); pput(scr, 100, TBL_Y - 40 + 16, (scr.width // 2, scr.height - 1))
pput(frame_of('combat/d20_roll.png', 3, 24), 164, TBL_Y - 40 + 14, (12, 23))
pput(frame_of('combat/d6_blue.png', 4, 8), 214, TBL_Y - 40 + 10, (4, 7)); pput(frame_of('combat/d6_red.png', 2, 8), 224, TBL_Y - 40 + 12, (4, 7))
SEATS_P = [(c, x, y, i == 0) for i, (c, x, y) in enumerate(zip(PPARTY, SEAT_X, SEAT_Y))]
pput(frame_of('fx/taunt_aura.png', 1, 56), SEAT_X[0], SEAT_Y[0] - 4, (28, 8))          # tank taunting: ground ring behind the seat
order = [1, 3, 0, 2, 4]                                                                 # draw the raised (farther) seats first
for i in order:
    c, x, y, act = SEATS_P[i]; pput(L(globals().get('SCENE_SEAT_FILE', 'party/seat_{c}_{st}.png').format(c=c, st='active' if act else 'idle')), x, y, (24, 77))
pput(frame_of('fx/taunt_badge.png', 0, 12), SEAT_X[0] + 12, SEAT_Y[0] - 72, (6, 12))
wz = PPARTY.index('wizard')
pput(frame_of('fx/mp_plus.png', 1, 19), SEAT_X[wz] - 2, SEAT_Y[wz] - 80, (9, 13))
HPV = [(50, 50), (28, 40), (16, 36), (34, 38), (6, 30)]        # placeholder current/max HP
MPF = [0.5, 1.0, 0.6, 0.8, 0.35]
HPMP = [(h / m, mp) for (h, m), mp in zip(HPV, MPF)]
SHOW_HP_NUM = True             # v7b: outlined cream digits just above the bar's left end
def seat_bar_rect(x, y, active=False):
    yy = y - 11 - (3 if active else 0); return [x - 22, yy, 44, 10]
def hp_num(im, x, y, n):
    d = L('ui/portrait/digits_3x5_outlined.png')
    for j, ch in enumerate(str(n)): im.alpha_composite(d.crop((int(ch) * 5, 0, int(ch) * 5 + 5, 7)), (x + j * 4, y))
SEAT_BARS = []; HP_NUM_POS = []
for i, (c, x, y, act) in enumerate(SEATS_P):
    bx, by, _, _ = seat_bar_rect(x, y, act); SEAT_BARS.append([bx, by, 44, 10])
    fr = L('ui/portrait/seat_bars_frame_active.png' if act else 'ui/portrait/seat_bars_frame.png'); ox = 1 if act else 0
    hp, mp = HPMP[i]; hpf = L('ui/portrait/seat_bar_hp_lowflash.png').crop((0, 0, 42, 4)) if hp < 0.25 else L('ui/portrait/seat_bar_hp.png')
    fr.alpha_composite(hpf.crop((0, 0, max(1, round(42 * hp)), 4)), (1 + ox, 1 + ox)); fr.alpha_composite(L('ui/portrait/seat_bar_mp.png').crop((0, 0, max(1, round(42 * mp)), 3)), (1 + ox, 6 + ox))
    P.alpha_composite(fr, (bx - ox, by - ox))
    if SHOW_HP_NUM:
        nx, ny = bx + 1, by - 6 - ox; HP_NUM_POS.append([nx, ny]); hp_num(P, nx, ny, HPV[i][0])
wb = SEAT_BARS[wz]; pput(frame_of('fx/mana_tick.png', 3, 16), wb[0] + 1 + round(42 * HPMP[wz][1]), wb[1] + 9, (8, 27))   # regen tick rising from the wizard's MP fill end
P.alpha_composite(render_bar('paladin', 0, 2, 2, 3), (0, TAB_Y))
save(P, 'scene_test_portrait.png'); save(upsc(P, 4), 'scene_test_portrait_4x.png')
PORTRAIT_LAYOUT = dict(max_party=5,
    initiative_strip=dict(rail='ui/panel_dark.png 9-slice 270x30 at [0,0]', frame='ui/portrait_frame*.png (24x24)', origin=[INI_X0, INI_Y], step=INI_STEP, visible=9,
        notes='8 combatants (5 party + 3 monsters) at step 29; a gold 1px divider marks the round end and the next-round portrait is clipped at the right edge (+ cream chevron) so the rail reads as scrollable. Scroll horizontally for >9.', order=[('party:' + PPARTY[v]) if k == 'p' else ('monster:' + v) for k, v in INIT]),
    monsters=[dict(name=n, feet=[x, y]) for n, x, y in PMON], table=dict(file='combat/table_portrait.png', size=[266, 40], bottom_centre=[135, TBL_Y], anchor=[133, 39]),
    gm=dict(file='combat/gm_idle.png', bottom_centre=[135, TBL_Y - 31], note='centred behind the middle seat; face stays above the middle seat head/hat'),
    seats=[dict(slot=i, cls=c, bottom_centre=[x, y], active=a) for i, (c, x, y, a) in enumerate(SEATS_P)],
    seat_slots=[dict(slot=i, bottom_centre=[x, y]) for i, (x, y) in enumerate(zip(SEAT_X, SEAT_Y))],
    seat_note='5 slots at x 27/81/135/189/243 (step 54, so 48px seats never overlap); slots 1 and 3 sit 4px higher (draw them first). v7: chair feet of slots 0/2/4 end 1px above the name tab (y418), 1/3 at y414. Smaller parties: see party_layouts.',
    seats_v6_card_row_note='v5/v6 had a 5-card row (hp_mp_card_compact) at y374 and feet at y374/370; dropped in v7.',
    seats_v4_4party_note=dict(x=[38, 102, 168, 232], y=[366, 363, 363, 366], table_bottom=328, cards='2x2 hp_mp_card_narrow at [4,366] step [132,30]'),
    seat_bars=dict(frame='ui/portrait/seat_bars_frame.png', frame_active='ui/portrait/seat_bars_frame_active.png', fills=['ui/portrait/seat_bar_hp.png', 'ui/portrait/seat_bar_mp.png'], tiles=['ui/portrait/seat_bar_hp_tile.png', 'ui/portrait/seat_bar_mp_tile.png'],
        low_hp='ui/portrait/seat_bar_hp_lowflash.png (hp < 25%)', size=[44, 10], hp_fill_rect=[1, 1, 42, 4], mp_fill_rect=[1, 6, 42, 3], version='v7b: MP bar 3px (was 2px)',
        rule='bar rect = [seat_x - 22, seat_feet_y - 11 (- 3 if the seat is active/raised), 44, 10]; overlaps the chair seat front + lower rails; 10px clear gap between neighbours at pitch 54.',
        rects_5=SEAT_BARS,
        hp_number=dict(font='ui/portrait/digits_3x5_outlined.png', cell=[5, 7], advance=4, content='current HP only (e.g. 34), no max', align='left',
            origin_rule='top-left of the first digit cell = [bar_x + 1, bar_y - 6] (for the active frame use its outer top: bar_y - 7); the digit outline bottom row overlaps the bar top outline',
            origins_5=HP_NUM_POS, max_digits=3, colors=dict(fill='#fcf0a0', bottom_row='#e2bc82', outline='#120c18'))),
    party_layouts={n: [dict(bottom_centre=[round(135 + (k - (n - 1) / 2) * 54), CARD_Y - (4 if k % 2 else 0)], bar_rect=[round(135 + (k - (n - 1) / 2) * 54) - 22, CARD_Y - (4 if k % 2 else 0) - 11, 44, 10], hp_number_origin=[round(135 + (k - (n - 1) / 2) * 54) - 21, CARD_Y - (4 if k % 2 else 0) - 17]) for k in range(n)] for n in range(1, 6)},
    party_layout_note='centred subsets at pitch 54 (odd slots 4px higher). The active seat is raised 3px, so its bar rect moves up 3px too.',
    action_bar=dict(version='v6 per-character', panel='ui/portrait/action_bar_v2.png', pos=[0, BAR_Y], size=[270, 50],
        name_tab=dict(file='ui/portrait/name_tab.png', pos=[4, TAB_Y], size=[64, 10], text_origin=[5, 2], note='shows the ACTIVE character name; gold matches hp_mp_card_compact_active'),
        default_abilities={n: dict(file=f'ui/portrait/ability_{n}.png', selected=f'ui/portrait/ability_{n}_active.png', rect=[BSL[n][0], BAR_Y + BSL[n][1], 32, 32]) for n in ('attack', 'cover')},
        skill_slots=[dict(skill=f'<active_class>_{k+1}', rect=[BSL['skills'][k][0], BAR_Y + BSL['skills'][k][1], 32, 32], icon_offset=[6, 6], cost_badge_pos=[BSL['cost_badges'][k][0], BAR_Y + BSL['cost_badges'][k][1]]) for k in range(5)],
        utility={n: dict(file=f'ui/portrait/mini_{n}.png', pressed=f'ui/portrait/mini_{n}_active.png', rect=[BSL[n][0], BAR_Y + BSL[n][1], 20, 20]) for n in ('item', 'run')},
        divider=dict(x=BSL['divider_x'], note='gold 1px + dark 1px line baked into the panel'),
        states=dict(normal='ui/skills/skill_slot.png', selected='ui/skills/skill_slot_active.png', cooldown='ui/skills/skill_cooldown_mask.png cropped from the top by remaining fraction at slot [4,4] + turns counter (digits_3x5 on an 8x8 outline box at slot [12,12])',
            locked='ui/skills/skill_slot_locked.png + full cooldown mask + ui/portrait/lock_icon.png at slot [11,11]', passive='ui/skills/skill_slot_passive.png + ui/portrait/passive_dim_mask.png at [4,4] + plum P tag [24,23,7,8]; not pressable; no cost badge ("PAS" label)'),
        cost_badge=dict(file='ui/portrait/cost_badge.png', prerendered='ui/portrait/cost_badge_0_9.png', digits='ui/portrait/digits_3x5.png', size=[16, 7]),
        placeholder_mp_costs=COSTS, scene_state=dict(active='paladin', selected='paladin_1', cooldown='paladin_3 (2 turns)', locked='paladin_4', passive='paladin_5'),
        why='Attack/Cover stay full 32px slots (most-used, thumb targets); 5 skills at 32px (>=28 rule) with 1px gaps; Item/Run are rarely used, so they drop to 20px minis stacked at the right end instead of tabs (tabs above the bar would collide with the name tab and the card row).',
        legacy_note='ui/portrait/action_bar.png and ui/portrait/btn32_* (attack/skill/item/cover/run) are LEGACY fallbacks.'),
    status_fx=dict(taunt_badge=dict(file='fx/taunt_badge.png', anchor_at=[SEAT_X[0] + 12, SEAT_Y[0] - 72], on=PPARTY[0]), taunt_aura=dict(file='fx/taunt_aura.png', anchor_at=[SEAT_X[0], SEAT_Y[0] - 4], draw='behind seat'),
        mana_tick=[dict(file='fx/mana_tick.png', on='wizard seat'), dict(file='fx/mana_tick.png', on='wizard MP bar')], mp_plus=dict(file='fx/mp_plus.png', on='above wizard hat')))


# ---------- v8 skill card popup ----------
def nine4(rel, Wd, Ht, l, t, r, b):
    src = L(rel); sw_, sh_ = src.size; out = Image.new('RGBA', (Wd, Ht))
    xs_ = [0, l, sw_ - r, sw_]; ys_ = [0, t, sh_ - b, sh_]; xd = [0, l, Wd - r, Wd]; yd = [0, t, Ht - b, Ht]
    for j in range(3):
        for i in range(3):
            piece = src.crop((xs_[i], ys_[j], xs_[i + 1], ys_[j + 1])); pw, ph = piece.size
            for yy in range(yd[j], yd[j + 1], ph):
                for xx in range(xd[i], xd[i + 1], pw):
                    out.paste(piece.crop((0, 0, min(pw, xd[i + 1] - xx), min(ph, yd[j + 1] - yy))), (xx, yy))
    return out
def strip3(state, Wd, txt, frame=0):
    src = L(f'ui/portrait/skill_card_strip_{state}.png'); src = src.crop((frame * 24, 0, frame * 24 + 24, 14)); out = Image.new('RGBA', (Wd, 14))
    out.paste(src.crop((0, 0, 5, 14)), (0, 0)); mid = src.crop((5, 0, 19, 14))
    for xx in range(5, Wd - 5, 14): out.paste(mid.crop((0, 0, min(14, Wd - 5 - xx), 14)), (xx, 0))
    out.paste(src.crop((19, 0, 24, 14)), (Wd - 5, 0))
    col = {'ready': [C['gold'], C['cream']], 'passive': [C['pink']], 'nomp': [C['coral']], 'cooldown': [C['mist']]}[state][frame if state == 'ready' else 0]
    text(out, Wd // 2 - text_w(txt) // 2, 5, txt, col)
    if state == 'ready':
        for dx in (-text_w(txt) // 2 - 9, text_w(txt) // 2 + 4):
            ax = Wd // 2 + dx
            for k_, row in enumerate([(0, 4), (1, 3), (2, 2)]): out.paste(col + (255,), (ax + row[0], 5 + k_, ax + row[0] + row[1] - row[0] + 1, 6 + k_))
    return out
SKI = {
 'paladin_1': dict(name='HOLY STRIKE', cost=2, target=('target_enemy', 'ONE ENEMY'), cd=1, desc='DEAL 120% DAMAGE TO ONE ENEMY. HOLY DAMAGE IGNORES 10% ARMOR. (PLACEHOLDER)'),
 'paladin_2': dict(name='SHIELD BASH', cost=3, target=('target_enemy', 'ONE ENEMY'), cd=2, desc='BASH ONE ENEMY FOR 80% DAMAGE AND STUN IT FOR 1 TURN. (PLACEHOLDER)'),
 'paladin_3': dict(name='HOLY AURA', cost=4, target=('target_all_allies', 'ALL ALLIES'), cd=3, desc='ALLIES REGAIN 10% HP AT THE START OF EACH TURN FOR 3 TURNS. (PLACEHOLDER)'),
 'paladin_4': dict(name='TAUNT', cost=1, target=('target_all_enemies', 'ALL ENEMIES'), cd=2, desc='FORCE ALL ENEMIES TO ATTACK YOU NEXT TURN. (PLACEHOLDER)'),
 'paladin_5': dict(name='GUARDIAN', cost=None, target=('target_self', 'SELF'), cd=None, desc='ENEMIES PREFER TO TARGET YOU. TAKE 10% LESS DAMAGE WHILE TAUNTING. (PLACEHOLDER)'),
}
def wrap(t, n):
    out, cur = [], ''
    for w in t.split():
        if len(cur) + len(w) + (1 if cur else 0) > n: out.append(cur); cur = w
        else: cur = (cur + ' ' + w) if cur else w
    return out + ([cur] if cur else [])
CARD_W = 224
CARD_RECTS = dict(icon_frame=[16, 12, 44, 44], name=[66, 13], name_scale=2, tag_right_margin=8, tag_y=12, cost_row=[66, 25], target_row=[66, 35], cd_row=[66, 45], desc=[16, 62], desc_line_h=8, desc_chars=49, strip_h=14, strip_margin_x=8, bottom_pad=5)
def render_card(key, state='ready', cd_n=2, frame=0):
    info = SKI[key]; passive = info['cost'] is None
    lines = wrap(info['desc'], CARD_RECTS['desc_chars'])[:3]
    Ht = CARD_RECTS['desc'][1] + len(lines) * CARD_RECTS['desc_line_h'] + 3 + CARD_RECTS['strip_h'] + CARD_RECTS['bottom_pad']
    card = nine4('ui/portrait/skill_card_panel.png', CARD_W, Ht, 14, 10, 6, 6)
    fr = L('ui/portrait/skill_card_icon_frame_passive.png' if passive else 'ui/portrait/skill_card_icon_frame.png')
    ic = L(f'ui/skills/{key}.png').resize((40, 40), Image.NEAREST); fr.alpha_composite(ic, (2, 2)); card.alpha_composite(fr, tuple(CARD_RECTS['icon_frame'][:2]))
    _nm = Image.new('RGBA', (text_w(info['name']) + 1, 5), (0, 0, 0, 0)); text(_nm, 0, 0, info['name'], C['outline'])
    card.alpha_composite(_nm.resize((_nm.width * 2, 10), Image.NEAREST), (66, 13))      # name = 3x5 font at 2x (6x10 glyphs, advance 8); max ~14 chars before the tag
    tg = L('ui/portrait/skill_tag_passive.png' if passive else 'ui/portrait/skill_tag_active.png'); card.alpha_composite(tg, (CARD_W - 8 - tg.width, 12))
    x, y = CARD_RECTS['cost_row']
    if passive: text(card, x, y + 1, 'NO COST', C['wood'])
    else:
        b = L('ui/portrait/cost_badge_0_9.png').crop((info['cost'] * 16, 0, info['cost'] * 16 + 16, 7)); card.alpha_composite(b, (x, y))
        text(card, x + 19, y + 1, 'MP COST', C['blue_dk'] if state != 'nomp' else C['red'])
    x, y = CARD_RECTS['target_row']; card.alpha_composite(L(f'ui/portrait/{info["target"][0]}.png'), (x, y)); text(card, x + 12, y + 1, info['target'][1], C['wood_dk'])
    x, y = CARD_RECTS['cd_row']; card.alpha_composite(L('ui/portrait/icon_cooldown.png'), (x, y))
    text(card, x + 12, y + 1, 'ALWAYS ON' if passive else f'COOLDOWN {info["cd"]} TURN' + ('S' if info['cd'] != 1 else ''), C['wood_dk'])
    for k_, ln in enumerate(lines): text(card, CARD_RECTS['desc'][0], CARD_RECTS['desc'][1] + k_ * CARD_RECTS['desc_line_h'], ln, C['bark'])
    st = 'passive' if passive else state
    txt = {'ready': 'TAP AGAIN TO CAST', 'passive': 'PASSIVE: ALWAYS ACTIVE', 'nomp': 'NOT ENOUGH MP', 'cooldown': f'ON COOLDOWN: {cd_n}'}[st]
    card.alpha_composite(strip3(st, CARD_W - 16, txt, frame), (8, Ht - CARD_RECTS['bottom_pad'] - CARD_RECTS['strip_h']))
    return card
def card_with_tail(card, tail_x):
    out = Image.new('RGBA', (card.width, card.height + 6)); out.alpha_composite(card, (0, 0))
    out.alpha_composite(L('ui/portrait/skill_card_tail.png'), (tail_x - 6, card.height - 2)); return out
# examples sheet
EXS = [('paladin_1', 'ready', 'ACTIVE: READY (TAP AGAIN TO CAST)'), ('paladin_5', 'passive', 'PASSIVE (NO CAST)'), ('paladin_2', 'nomp', 'DISABLED: NOT ENOUGH MP'), ('paladin_3', 'cooldown', 'DISABLED: ON COOLDOWN')]
cards_ = [render_card(k, st) for k, st, _ in EXS]
EXW = 2 * (CARD_W + 12) + 8; rowh = max(c.height for c in cards_) + 22
SKX = Image.new('RGBA', (EXW, 2 * rowh + 8), C['gray'] + (255,))
for i, (c_, (_, _, lab)) in enumerate(zip(cards_, EXS)):
    x0 = 8 + (i % 2) * (CARD_W + 12); y0 = 6 + (i // 2) * rowh; text(SKX, x0, y0, lab, C['cream']); SKX.alpha_composite(card_with_tail(c_, 40 + i * 30), (x0, y0 + 9))
save(SKX, 'ui/portrait/skill_card_examples.png'); save(SKX.resize((SKX.width * 3, SKX.height * 3), Image.NEAREST), 'ui/portrait/skill_card_examples_3x.png')
META['ui/portrait/skill_card_examples.png'] = dict(notes='QA: skill card states (active ready, passive, not enough MP, on cooldown). Placeholder copy. Not a runtime asset.')
META['ui/portrait/skill_card_examples_3x.png'] = dict(notes='3x nearest.')
# scene mock: paladin_1 armed, card open
SC = P.copy()
slot0 = [BSL['skills'][0][0], BAR_Y + BSL['skills'][0][1]]
for k_ in range(1, 5):
    sx_, sy_ = BSL['skills'][k_]; SC.alpha_composite(L('ui/portrait/bar_dim_mask.png'), (sx_, BAR_Y + sy_))
for n_ in ('attack', 'cover'): SC.alpha_composite(L('ui/portrait/bar_dim_mask.png'), (BSL[n_][0], BAR_Y + BSL[n_][1]))
SC.alpha_composite(frame_of('ui/portrait/skill_slot_armed.png', 0, 36), (slot0[0] - 2, slot0[1] - 2))
cd0 = render_card('paladin_1', 'ready'); CARD_BOTTOM = min(SEAT_BARS[i][1] for i in range(5)) - 6 - 8   # clear the seat bars + HP numbers
CARD_X = max(4, min(270 - 4 - CARD_W, slot0[0] + 16 - CARD_W // 2)); CARD_Y0 = CARD_BOTTOM - cd0.height
SC.alpha_composite(card_with_tail(cd0, slot0[0] + 16 - CARD_X), (CARD_X, CARD_Y0))
save(SC, 'scene_test_portrait_skillcard.png'); save(upsc(SC, 4), 'scene_test_portrait_skillcard_4x.png')
META['scene_test_portrait_skillcard.png'] = dict(notes='PORTRAIT mock: paladin_1 tapped once -> slot armed (pulsing glow), other slots dimmed, skill card open above the seats (clears the seat bars + HP numbers). Placeholder copy.')
META['scene_test_portrait_skillcard_4x.png'] = dict(notes='4x nearest.')
SKILL_CARD_LAYOUT = dict(width=CARD_W, height='desc_y + lines*8 + 3 + strip 14 + pad 5 (95 px for 3 lines)', panel=dict(file='ui/portrait/skill_card_panel.png', nine_slice=dict(left=14, top=10, right=6, bottom=6), mode='tile'),
    tail=dict(file='ui/portrait/skill_card_tail.png', tip_x='selected slot centre x', y='card_bottom - 2', note='tail tip ends above the seat bars; the armed glow + x alignment tie card and slot together'),
    rects=CARD_RECTS, icon='20x20 skill icon scaled 2x (nearest) into skill_card_icon_frame(_passive).png at [2,2]',
    tags=['ui/portrait/skill_tag_active.png', 'ui/portrait/skill_tag_passive.png'], info_icons=['ui/portrait/target_enemy.png', 'target_all_enemies', 'target_ally', 'target_all_allies', 'target_self', 'icon_cooldown'],
    strips=dict(ready='skill_card_strip_ready.png (2-frame pulse, 3 fps, "TAP AGAIN TO CAST" gold/cream + chevrons)', passive='skill_card_strip_passive.png "PASSIVE: ALWAYS ACTIVE"', nomp='skill_card_strip_nomp.png "NOT ENOUGH MP" (coral)', cooldown='skill_card_strip_cooldown.png "ON COOLDOWN: n"'),
    placement=dict(x='clamp(slot_cx - width/2, 4, 270 - 4 - width)', bottom=f'min(seat bar top) - 14 = y{CARD_BOTTOM} in the 5-seat layout (covers the table/heads, never the seat bars or HP numbers)', scene_rect=[CARD_X, CARD_Y0, CARD_W, cd0.height]),
    armed_slot=dict(file='ui/portrait/skill_slot_armed.png', frames=2, fps=4, offset_from_slot=[-2, -2]), dim_others='ui/portrait/bar_dim_mask.png over every other bar slot (optional)',
    interaction=['tap 1 on a skill slot: open its card, slot -> ARMED, others dim', 'tap 2 on the SAME slot: cast/use (then target selection if needed); card closes', 'tap another slot: switch the card to that skill (it becomes armed)',
                 'tap anywhere else (scene, table, empty bar area): close the card, no cast', 'passive skill: card opens with PASSIVE tag and "PASSIVE: ALWAYS ACTIVE"; a second tap only closes it',
                 'disabled (not enough MP / on cooldown): card opens with the red/grey strip; a second tap does nothing except a small shake'],
    copy_note='all skill names/descriptions in the mocks are PLACEHOLDER until docs/CLASSES.md lands.', font='pack 3x5 pixel font (pal.py FONT, original; added % , \' = ?). m5x7 (CC0) is referenced but not bundled.')

PORTRAIT_LAYOUT['skill_card'] = SKILL_CARD_LAYOUT
# ---------- regions (approved 2026-09-28): approval sheets + example composite ----------
RGJ = json.load(open(W_ + 'meta_regions.json'))['regions']
LOC_ORDER = [p_['id'] for p_ in RGJ['places']]
def label_bar(im, x, y, w, s1, s2=None, bg='ink'):
    im.paste(C[bg] + (255,), (x, y, x + w, y + 9)); text(im, x + 2, y + 2, s1, C['gold'])
    if s2: text(im, x + w - 2 - text_w(s2), y + 2, s2, C['mist'])
# A) backdrops side by side
GAP = 6; BW = len(LOC_ORDER) * (270 + GAP) + GAP
AB = Image.new('RGBA', (BW, 480 + 14 + 2 * GAP), C['slate'] + (255,))
for i, lid in enumerate(LOC_ORDER):
    pl = RGJ['places'][i]; x0 = GAP + i * (270 + GAP)
    label_bar(AB, x0, GAP, 270, pl['name'].upper(), (pl['region'].upper() + ' / LV ' + str(pl['level'])))
    AB.alpha_composite(L(f'combat/bg_{lid}_portrait.png'), (x0, GAP + 12))
save(AB, 'approval/backdrops_1x.png'); save(upsc(AB, 2), 'approval/backdrops_2x.png')
META['approval/backdrops_1x.png'] = dict(status='approved', notes='APPROVAL SHEET (not runtime): the 6 Greenmere location backdrops at 1x, labelled name / region / level.')
META['approval/backdrops_2x.png'] = dict(status='approved', notes='2x nearest of approval/backdrops_1x.png.')
# B) monster lineup grouped by region, each card on a crop of that region's backdrop stand zone
REG_BG = dict(meadow='millpond', coast='lantern_reach', cave='howling_cleft', keep='gravel_keep')
EXM = RGJ['existing']; DRM = RGJ['draft_monsters']
CWd, CHt = 88, 96; rows = []
for kind in ('meadow', 'coast', 'cave', 'keep'):
    r_ = RGJ['regions'][kind]; rows.append((kind, r_))
maxn = max(len(r_['existing']) + len(r_['new']) for _, r_ in rows)
LW = 8 + maxn * (CWd + 4) + 4; LH = 8 + len(rows) * (CHt + 20) + 16
LU = Image.new('RGBA', (LW, LH), C['slate'] + (255,))
text(LU, 8, 4, 'GREENMERE MONSTERS BY REGION  -  NEW = ADDED IN REGION PASS (APPROVED)  -  LARGE = WIDER TABLE SLOT (COST 5)', C['cream'])
y = 14
for kind, r_ in rows:
    places = ', '.join(p_['name'].upper() for p_ in RGJ['places'] if p_['region'] == kind)
    label_bar(LU, 4, y, LW - 8, f'{kind.upper()}: {places}', f"{r_['regular']} REGULAR + {r_['large']} LARGE")
    y += 12; bgim = L(f'combat/bg_{REG_BG[kind]}_portrait.png')
    for j, mid in enumerate(r_['existing'] + r_['new']):
        new_ = mid in DRM
        if new_: nm, sz, spr_ = DRM[mid]['name'], DRM[mid]['size'], mid
        else: nm, sz, spr_ = EXM[mid]
        x0 = 8 + j * (CWd + 4)
        card = bgim.crop((135 - CWd // 2 - 40 + (j * 23) % 80, 196, 135 - CWd // 2 - 40 + (j * 23) % 80 + CWd, 196 + 74))
        card.alpha_composite(L(f'monsters/{spr_}/{spr_}_still.png'), ((CWd - 80) // 2, 2))
        LU.alpha_composite(card, (x0, y))
        LU.paste(C['gold' if new_ else 'gray'] + (255,), (x0, y + 74, x0 + CWd, y + 75))
        LU.paste(C['ink'] + (255,), (x0, y + 75, x0 + CWd, y + CHt))
        text(LU, x0 + 2, y + 77, nm.upper()[:21], C['white'])
        text(LU, x0 + 2, y + 84, ('LARGE' if sz == 'large' else 'REGULAR'), C['coral'] if sz == 'large' else C['mist'])
        if new_:
            LU.paste(C['gold'] + (255,), (x0 + CWd - 15, y + 83, x0 + CWd - 1, y + 90)); text(LU, x0 + CWd - 14, y + 84, 'NEW', C['outline'])
        else: text(LU, x0 + 2, y + 90, ('SPRITE ' + spr_).upper(), C['gray'])
    y += CHt + 8
save(LU, 'approval/monster_lineup.png'); save(upsc(LU, 2), 'approval/monster_lineup_2x.png')
META['approval/monster_lineup.png'] = dict(status='approved', notes='APPROVAL SHEET (not runtime): monsters grouped by region (existing first, NEW drafts tagged gold), each on a crop of its region backdrop stand zone; existing ones show the pack sprite that data/monsters.json maps them to.')
META['approval/monster_lineup_2x.png'] = dict(status='approved', notes='2x nearest of approval/monster_lineup.png.')
# C) example composite: Lantern Reach with coast monsters (incl. the new large Kelpback), full party/table/bar UI
_src = open(os.path.abspath(__file__)).read()
_scene = _src.split('# ---------- scene_test_portrait ----------\n', 1)[1].split("\nsave(P, 'scene_test_portrait.png')", 1)[0]
_ns = dict(globals()); _ns.update(SCENE_BG='combat/bg_lantern_reach_portrait.png',
    SCENE_PMON=[('bottlecrab', 52, 262), ('kelpback', 135, 222), ('squallgull', 220, 266)],
    SCENE_INIT=[('p', 0), ('m', 'bottlecrab'), ('p', 4), ('p', 3), ('m', 'kelpback'), ('p', 2), ('m', 'squallgull'), ('p', 1)],
    SCENE_PCT={'bottlecrab': 1.0, 'kelpback': 0.6, 'squallgull': 0.85})
exec(compile(_scene, 'scene_block', 'exec'), _ns)
save(_ns['P'], 'scene_test_portrait_lantern_reach.png'); save(upsc(_ns['P'], 4), 'scene_test_portrait_lantern_reach_4x.png')
META['scene_test_portrait_lantern_reach.png'] = dict(status='approved', notes='QA composite (not runtime): Lantern Reach backdrop + coast monsters Bottlecrab / Kelpback Snapper (LARGE) / Squallgull at the standard monster marks, with the v7 party, table, seat bars + HP numbers and v6 action bar.')
META['scene_test_portrait_lantern_reach_4x.png'] = dict(status='approved', notes='4x nearest.')
# D) per-region monsters on their own backdrops (extra check)
for kind, lid, trio in (('meadow', 'briar_cross', ['bramblet', 'briar_hound', 'grinmud_toad']), ('cave', 'howling_cleft', ['gloomgrub', 'marshlurker', 'dripfang']), ('keep', 'gravel_keep', ['pebble_squire', 'gravel_brute', 'hollow_helm'])):
    _ns = dict(globals()); spr3 = [m if m in DRM else EXM[m][2] for m in trio]
    _ns.update(SCENE_BG=f'combat/bg_{lid}_portrait.png', SCENE_PMON=[(spr3[0], 52, 262), (spr3[1], 135, 222), (spr3[2], 220, 266)],
        SCENE_INIT=[('p', 0), ('m', spr3[0]), ('p', 4), ('p', 3), ('m', spr3[1]), ('p', 2), ('m', spr3[2]), ('p', 1)], SCENE_PCT={spr3[0]: 1.0, spr3[1]: 0.6, spr3[2]: 0.85})
    exec(compile(_scene, 'scene_block', 'exec'), _ns)
    save(_ns['P'], f'approval/scene_{lid}.png')
    META[f'approval/scene_{lid}.png'] = dict(status='approved', notes=f'QA composite (not runtime): {lid} backdrop with {", ".join(trio)} and the full portrait UI.')

# ---------- items (DRAFT 2026-09-28): scene composite with the party wearing gear ----------
ITJ = json.load(open(W_ + 'meta_items.json'))['items']
_ns = dict(globals()); _ns.update(SCENE_SEAT_FILE='approval/gear_seats/seat_{c}_{st}.png', SCENE_BG='combat/bg_gravel_keep_portrait.png',
    SCENE_PMON=[('pebble_squire', 52, 262), ('golem', 135, 222), ('hollow_helm', 220, 266)],
    SCENE_INIT=[('p', 0), ('m', 'pebble_squire'), ('p', 4), ('p', 3), ('m', 'golem'), ('p', 2), ('m', 'hollow_helm'), ('p', 1)],
    SCENE_PCT={'pebble_squire': 1.0, 'golem': 0.6, 'hollow_helm': 0.85})
exec(compile(_scene, 'scene_block', 'exec'), _ns)
save(_ns['P'], 'scene_test_portrait_gear.png'); save(upsc(_ns['P'], 4), 'scene_test_portrait_gear_4x.png')
META['scene_test_portrait_gear.png'] = dict(status='draft_pending_approval', notes='QA composite (not runtime): party wearing DRAFT gear overlays (paladin keep_plate+oath_blade+kettle_shield, cleric hedge_mail+chapel_mace+hymn_board, rogue travel_coat+night_shard+pocket_knife (mirrored off hand), druid reed_wrap+sap_crook, wizard moon_robe+lamp_staff) at Gravel Keep.')
META['scene_test_portrait_gear_4x.png'] = dict(status='draft_pending_approval', notes='4x nearest.')

# ---------- map_test_portrait ----------
TL = {k: L(f'map/tile_{k}.png') for k in ['grass', 'grass_flowers', 'road_h', 'road_v', 'road_cross', 'river_h', 'bridge_v']}
for k in ('es', 'ws', 'en', 'wn'): TL['c_' + k] = L(f'map/tile_road_corner_{k}.png')
for k in ('ews', 'ewn', 'nse', 'nsw'): TL['t_' + k] = L(f'map/tile_road_t_{k}.png')
COLS, ROWS = 17, 30
NODES = [('tavern', 8, 27), ('village', 3, 22), ('shrine', 13, 22), ('windmill', 12, 12), ('cave', 4, 8), ('castle', 10, 3)]
EDGES = [(0, 1), (0, 2), (1, 3), (3, 4), (4, 5)]
RIVER_ROW = 17
road = set()
for a, b in EDGES:
    (_, ax, ay), (_, bx, by) = NODES[a], NODES[b]
    for y in range(min(ay, by), max(ay, by) + 1): road.add((ax, y))
    for x in range(min(ax, bx), max(ax, bx) + 1): road.add((x, by))
M = Image.new('RGBA', (COLS * 16, ROWS * 16))
for r in range(ROWS):
    for c in range(COLS):
        k = 'grass_flowers' if hash((c * 31 + r * 17) % 11) in (3,) else 'grass'
        if r == RIVER_ROW: k = 'river_h'
        if (c, r) in road:
            n_, s_, e_, w_ = (c, r - 1) in road, (c, r + 1) in road, (c + 1, r) in road, (c - 1, r) in road
            cnt = n_ + s_ + e_ + w_
            if r == RIVER_ROW: k = 'bridge_v'
            elif cnt == 4: k = 'road_cross'
            elif cnt == 3: k = 't_' + ('ews' if not n_ else 'ewn' if not s_ else 'nse' if not w_ else 'nsw')
            elif (n_ or s_) and not (e_ or w_): k = 'road_v'
            elif (e_ or w_) and not (n_ or s_): k = 'road_h'
            elif e_ and s_: k = 'c_es'
            elif w_ and s_: k = 'c_ws'
            elif e_ and n_: k = 'c_en'
            elif w_ and n_: k = 'c_wn'
            else: k = 'road_v'
        M.paste(TL[k], (c * 16, r * 16))
for n, c, r in NODES:
    ic = L(f'map/loc_{n}.png'); M.alpha_composite(ic, (c * 16 + 8 - 16, r * 16 + 10 - 28))
pw = frame_of('map/pawn_walk.png', 1, 24); M.alpha_composite(pw, (7 * 16 + 8 - 12, 12 * 16 + 12 - 19))
mk = frame_of('map/marker_arrow.png', 0, 9); M.alpha_composite(mk, (12 * 16 + 8 - 4, 12 * 16 - 20 - 11))
MP = M.crop((1, 0, 271, 480))
MP.alpha_composite(L('ui/portrait/top_bar.png'), (0, 0)); MP.alpha_composite(L('ui/icon_gold.png'), (5, 5))
text(MP, 18, 8, '250', C['gold']); t = 'WORLD MAP'; text(MP, 135 - text_w(t) // 2, 8, t, C['cream'])
MP.alpha_composite(L('ui/btn_menu.png'), (249, 1))
save(MP, 'map_test_portrait.png'); save(upsc(MP, 4), 'map_test_portrait_4x.png')

# ---------- creator_test_portrait ----------
CR = nine('ui/panel_parchment.png', PWID, PHEI)
t = 'CREATE YOUR HERO'; text(CR, 135 - text_w(t) // 2, 9, t, C['wood_dk'])
CR.alpha_composite(nine('ui/panel_dark.png', 84, 114), (93, 20))
cur = dict(skin=3, head=1, hair=4, hcol='ginger', ocol='green', cls='ranger')
doll = doll_front(cur['skin'], cur['head'], cur['hair'], cur['hcol'], cur['ocol'], cur['cls'], True)
CR.alpha_composite(upsc(doll, 2), (135 - 32, 28))
CR.alpha_composite(L('ui/btn_arrow_left.png'), (72, 66)); CR.alpha_composite(L('ui/btn_arrow_right.png'), (184, 66))
y = 142
def label(s):
    global y; text(CR, 10, y, s, C['bark']); y += 7
def thumbs(ims, active, step=26):
    global y; x = 10
    for i, im in enumerate(ims):
        fr = L('ui/portrait_frame_active.png' if i == active else 'ui/portrait_frame.png'); fr.alpha_composite(im, (2, 2)); CR.alpha_composite(fr, (x, y)); x += step
    y += 24 + 6
def swatches(cols, active):
    global y; x = 10
    for i, col in enumerate(cols):
        f = L('ui/swatch_frame_active.png' if i == active else 'ui/swatch_frame.png'); f.paste(col + (255,), (2, 2, 14, 14)); CR.alpha_composite(f, (x, y)); x += 20
    y += 16 + 6
label('HEAD'); thumbs([portrait_of(doll_front(cur['skin'], h, 1, 'brown', 'white')) for h in range(1, 7)], cur['head'] - 1)
label('HAIR'); thumbs([portrait_of(doll_front(cur['skin'], 1, h, cur['hcol'], 'white')) for h in range(1, 9)], cur['hair'] - 1)
label('SKIN'); swatches([C['skin%d' % k] for k in range(1, 7)], cur['skin'] - 1)
HR = DOLL['hair_ramps']; label('HAIR COLOUR'); swatches([C[v[2]] for v in HR.values()], list(HR).index(cur['hcol']))
OR = DOLL['outfit_ramps']; label('OUTFIT COLOUR'); swatches([C[v[1]] for v in OR.values()], list(OR).index(cur['ocol']))
CLASSES8 = ['paladin', 'wizard', 'ranger', 'bard', 'cleric', 'rogue', 'barbarian', 'druid']
label('CLASS')
for i, c in enumerate(CLASSES8):
    x = 15 + (i % 4) * 64; yy = y + (i // 4) * 56
    box = Image.new('RGBA', (40, 46)); box.paste(C['sand'] + (255,), (0, 0, 40, 46))
    d = doll_front(cur['skin'], cur['head'], cur['hair'], cur['hcol'], cur['ocol'], c, True)
    box.alpha_composite(d.crop((0, 0, 32, 43)), (4, 2))
    edge = C['gold'] if c == cur['cls'] else C['wood']
    for bx in range(40): box.putpixel((bx, 0), edge + (255,)); box.putpixel((bx, 45), edge + (255,))
    for by in range(46): box.putpixel((0, by), edge + (255,)); box.putpixel((39, by), edge + (255,))
    CR.alpha_composite(box, (x, yy)); text(CR, x + 20 - text_w(c.upper()) // 2, yy + 48, c.upper(), C['red'] if c == cur['cls'] else C['bark'])
y += 2 * 56
CR.alpha_composite(L('ui/btn_confirm.png'), (135 - 56 - 6, 440)); CR.alpha_composite(L('ui/btn_random.png'), (135 + 6, 440))
save(CR, 'creator_test_portrait.png'); save(upsc(CR, 4), 'creator_test_portrait_4x.png')
print('creator rows end y', y)
for k in ('scene_test_portrait.png', 'map_test_portrait.png', 'creator_test_portrait.png'):
    META[k] = dict(notes='PORTRAIT 270x480 mock built only from pack files (QA).'); META[k.replace('.png', '_4x.png')] = dict(notes='4x nearest upscale.')


# ---------- fx_test_portrait: FX readability on monsters + seats ----------
FXT = L('combat/bg_forest_portrait.png').crop((0, 120, 270, 480))
FXT = FXT.crop((0, 0, 270, 360))
def fxp(im, x, y, anchor): FXT.alpha_composite(im, (x - anchor[0], y - anchor[1]))
FXROW1 = [('goblin', 'fx_slash', 2), ('slime', 'fx_fireball', 4), ('mushroom', 'fx_poison_cloud', 2), ('skeleton', 'fx_lightning', 2)]
for k, (mn, fx, fi) in enumerate(FXROW1):
    x = 36 + k * 66; fy = 130; m = META[f'monsters/{mn}/{mn}_idle.png']; fxp(frame_of(f'monsters/{mn}/{mn}_idle.png', 0, 80), x, fy, m['anchor'])
    fm = META[f'fx/{fx}.png']; fw = fm['frame_size'][0]; fr = frame_of(f'fx/{fx}.png', fi, fw)
    if fm['anchor'][1] == fm['frame_size'][1] - 1: fxp(fr, x, fy, fm['anchor'])
    else: fxp(fr, x, fy - 24, fm['anchor'])
    FXT.paste(C['ink'] + (255,), (x - text_w(fx[3:].upper()) // 2 - 2, fy + 4, x + text_w(fx[3:].upper()) // 2 + 2, fy + 13)); text(FXT, x - text_w(fx[3:].upper()) // 2, fy + 6, fx[3:].upper(), C['cream'])
for k, (c, fx, fi) in enumerate([('cleric', 'fx_heal_sparkle', 3), ('barbarian', 'fx_buff_aura', 2), ('paladin', 'fx_shield', 3)]):
    x = 50 + k * 85; fy = 228; fm = META[f'fx/{fx}.png']; fr = frame_of(f'fx/{fx}.png', fi, fm['frame_size'][0])
    fxp(L(f'party/seat_{c}_idle.png'), x, fy, (24, 77)); fxp(fr, x, fy + 2, fm['anchor'])
    FXT.paste(C['ink'] + (255,), (x - text_w(fx[3:].upper()) // 2 - 2, fy + 6, x + text_w(fx[3:].upper()) // 2 + 2, fy + 15)); text(FXT, x - text_w(fx[3:].upper()) // 2, fy + 8, fx[3:].upper(), C['cream'])
for k, (c, fx) in enumerate([('barbarian', 'taunt'), ('wizard', 'mana')]):
    x = 80 + k * 110; fy = 334
    if fx == 'taunt':
        fxp(frame_of('fx/taunt_aura.png', 1, 56), x, fy - 2, (28, 8)); fxp(L(f'party/seat_{c}_idle.png'), x, fy, (24, 77)); fxp(frame_of('fx/taunt_badge.png', 0, 12), x + 13, fy - 70, (6, 12)); lab = 'TAUNT_BADGE+AURA'
    else:
        fxp(L(f'party/seat_{c}_idle.png'), x, fy, (24, 77)); fxp(frame_of('fx/mana_tick.png', 2, 16), x - 12, fy - 40, (8, 27)); fxp(frame_of('fx/mana_tick.png', 4, 16), x + 12, fy - 34, (8, 27)); fxp(frame_of('fx/mp_plus.png', 0, 19), x, fy - 80, (9, 13)); lab = 'MANA_TICK+MP_PLUS'
    tw = text_w(lab); FXT.paste(C['ink'] + (255,), (x - tw // 2 - 2, fy + 5, x + tw // 2 + 2, fy + 14)); text(FXT, x - tw // 2, fy + 7, lab, C['cream'])
save(FXT, 'fx_test_portrait.png'); save(upsc(FXT, 3), 'fx_test_portrait_3x.png')
META['fx_test_portrait.png'] = dict(notes='QA: one representative frame of each FX on monsters (fx centred on body, lightning/heal/buff/shield on feet) and composed seats, at native scale.')
META['fx_test_portrait_3x.png'] = dict(notes='3x nearest.')

# ---------------- contact sheet ----------------
BGc = C['gray']; CW = 796
secs = [('COMBAT', ['combat/*.png']), ('MONSTERS', ['monsters/*/*_idle.png', 'monsters/*/*_attack.png', 'monsters/*/*_hit.png', 'monsters/*/*_death.png', 'monsters/*/*_still.png', 'monsters/*/*_portrait.png']),
        ('PARTY SEATS', ['party/*.png']), ('PAPERDOLL FRONT LAYERS', ['paperdoll/body_*.png', 'paperdoll/head_*.png', 'paperdoll/hair_*.png', 'paperdoll/outfit_base.png', 'paperdoll/class_*.png']),
        ('PAPERDOLL BACK SEATED LAYERS', ['paperdoll/back/*.png']), ('PAPERDOLL RAMPS + PORTRAITS', ['paperdoll/palettes/*.png', 'paperdoll/portrait_crop_examples.png']),
        ('MAP', ['map/tile_*.png', 'map/loc_*.png', 'map/pawn_walk.png', 'map/tiles_preview.png']), ('UI', ['ui/*.png']), ('UI PORTRAIT', ['ui/portrait/*.png']), ('SKILL ICONS', ['ui/skills/*_?.png', 'ui/skills/skill_slot*.png', 'ui/skills/skill_cooldown_mask.png', 'ui/skills/skill_sheet.png']), ('ITEM ICONS (DRAFT)', ['ui/items/*.png']), ('GEAR OVERLAYS (DRAFT)', ['paperdoll/gear/*.png']), ('FX', ['fx/*.png']), ('PALETTE', ['palette/palette48.png'])]
items = []
seen = set()
for title, pats in secs:
    items.append(('__H__', title))
    for pt in pats:
        for p in sorted(glob.glob(OUT + pt)):
            rel = p[len(OUT):]
            if rel in seen or rel.endswith('_3x.png'): continue
            seen.add(rel); items.append((rel, None))
# layout (native), then 3x
placed = []; x = y = 4; rowh = 0
for rel, title in items:
    if rel == '__H__':
        if x > 4: y += rowh + 6
        placed.append(('H', title, 4, y)); y += 10; x = 4; rowh = 0; continue
    im = L(rel); iw, ih = im.size
    sc = 2 if max(iw, ih) <= 8 else 1
    lab = os.path.basename(rel)[:-4]
    w = max(iw * sc, text_w(lab)) ; h = ih * sc + 8
    if x + w > CW: x = 4; y += rowh + 4; rowh = 0
    placed.append(('I', rel, x, y, sc, lab)); x += w + 6; rowh = max(rowh, h)
Htot = y + rowh + 8
CS = Image.new('RGBA', (CW + 4, Htot), BGc + (255,))
for it in placed:
    if it[0] == 'H':
        _, t, hx, hy = it; CS.paste(C['ink'] + (255,), (0, hy - 2, CW + 4, hy + 7)); text(CS, hx, hy, t, C['gold'])
    else:
        _, rel, ix, iy, sc, lab = it; im = L(rel)
        if sc > 1: im = im.resize((im.width * sc, im.height * sc), Image.NEAREST)
        CS.paste(C['slate'] + (255,), (ix, iy, ix + im.width, iy + im.height)); CS.alpha_composite(im, (ix, iy))
        text(CS, ix, iy + im.height + 2, lab, C['white'])
k = 3 if (CW + 4) * 3 <= 2400 else 2
save(CS.resize((CS.width * k, CS.height * k), Image.NEAREST), 'contact_sheet.png')
META['contact_sheet.png'] = dict(notes=f'every primary asset at {k}x nearest (items <=8px shown at an extra 2x). paperdoll/tinted/* variants are represented by the ramp previews and paperdoll_preview.png.')
print('contact sheet', CS.width * k, CS.height * k)

# ---------------- validation ----------------
files = sorted(p for p in glob.glob(OUT + '**/*.png', recursive=True) if '/tools/' not in p)
problems = []; CUT = ('combat/', 'party/', 'monsters/', 'map/loc_', 'map/pawn')
for p in files:
    im = Image.open(p)
    if im.mode != 'RGBA': problems.append((p, 'mode ' + im.mode))
    ba, bad = pal.check_palette(im)
    if ba: problems.append((p, f'{ba} semi-transparent px'))
    if bad: problems.append((p, f'{len(bad)} off-palette colours'))
    rel = p[len(OUT):]
    if rel.startswith(CUT) and 'd6_' not in rel:
        a = np.array(im); op = a[..., 3] == 255
        pinks = set(pal.PAL[i] for i in pal.PINKS)
        n = sum(int(((a[..., 0] == c[0]) & (a[..., 1] == c[1]) & (a[..., 2] == c[2]) & op).sum()) for c in pinks)
        if n: problems.append((p, f'{n} pink/magenta px in a keyed asset'))
print('checked', len(files), 'PNGs; problems:', problems[:20])


# ---------------- manifest ----------------
files = sorted(p for p in glob.glob(OUT + '**/*.png', recursive=True) if '/tools/' not in p)
entries = []
for p in files:
    rel = p[len(OUT):]; im = Image.open(p)
    e = dict(path=rel, size=list(im.size))
    m = dict(META.get(rel, {}))
    if rel.startswith('paperdoll/tinted/'):
        m.setdefault('notes', 'pre-tinted variant (same canvas/anchor as its grayscale/reference source).'); m.setdefault('anchor', [16, 47])
    if 'frames' not in m: m['frames'] = 1; m.setdefault('frame_size', list(im.size))
    e.update(m); entries.append(e)
entries += [dict(path='palette/palette48.gpl', notes='GIMP/Aseprite palette, 48 named colours.'), dict(path='palette/palette48.hex', notes='48 hex colours, one per line (Lospec .hex format).'),
            dict(path='tools/', notes='reproducible build scripts: build_cut.py -> build_proc.py -> build_doll.py -> build_skills.py -> build_regions.py -> build_items.py -> compose.py (python w/ pillow+numpy+scipy). tools/_work holds intermediates.')]
LEGACY = {'combat/bg_forest.png': 'use combat/bg_forest_portrait.png', 'combat/table.png': 'use combat/table_portrait.png (250x40)',
    'ui/hp_mp_card.png': 'use ui/portrait/hp_mp_card_narrow.png', 'ui/bar_hp.png': 'use ui/portrait/bar_hp_88.png or bar_hp_tile', 'ui/bar_mp.png': 'use ui/portrait/bar_mp_88.png or bar_mp_tile',
    'ui/bar_bg.png': 'baked into the narrow card', 'scene_test.png': 'see scene_test_portrait.png', 'scene_test_4x.png': 'see scene_test_portrait_4x.png'}
for n in ['attack', 'skill', 'item', 'cover', 'run']:
    for sfx in ('', '_active'):
        LEGACY[f'ui/btn_{n}{sfx}.png'] = 'portrait bottom bar is now the v6 per-character bar (ui/portrait/action_bar_v2.png)'
        LEGACY[f'ui/portrait/btn32_{n}{sfx}.png'] = 'fallback only; the v6 bar uses ability_attack/ability_cover, class skill slots and mini_item/mini_run'
for f_ in ('ui/portrait/hp_mp_card_compact.png', 'ui/portrait/hp_mp_card_compact_active.png', 'ui/portrait/bar_hp_44.png', 'ui/portrait/bar_mp_44.png', 'ui/portrait/hp_mp_card_narrow.png', 'ui/portrait/bar_hp_88.png', 'ui/portrait/bar_mp_88.png', 'ui/portrait/bar_bg_90.png'):
    LEGACY[f_] = 'v7: party HP/MP now shown as seat-mounted bars (ui/portrait/seat_bars_frame*.png + seat_bar_hp/mp)'
LEGACY['ui/portrait/action_bar.png'] = 'use ui/portrait/action_bar_v2.png (v6 per-character bar)'
for e in entries:
    if e['path'] in LEGACY:
        e['legacy'] = True; e['notes'] = 'LEGACY (landscape 480x270): ' + LEGACY[e['path']] + '. ' + e.get('notes', '').replace('LEGACY (landscape). ', '')
PORTRAIT_FILES = ['combat/bg_forest_portrait.png', 'combat/table_portrait.png', 'combat/d20_roll.png', 'combat/d20_results.png', 'combat/d20_nat20.png'] + \
    [f'party/seat_{c_}_{s_}.png' for c_ in CLASSES8 for s_ in ('idle', 'active')] + \
    sorted(p[len(OUT):] for p in glob.glob(OUT + 'ui/portrait/*.png')) + sorted(p[len(OUT):] for p in glob.glob(OUT + 'ui/skills/*.png')) + sorted(p[len(OUT):] for p in glob.glob(OUT + 'fx/*.png')) + ['ui/icon_gold.png', 'ui/btn_menu.png', 'ui/btn_confirm.png', 'ui/btn_random.png', 'ui/btn_arrow_left.png', 'ui/btn_arrow_right.png',
    'ui/swatch_frame.png', 'ui/swatch_frame_active.png', 'map/marker_arrow.png'] + [f'map/tile_road_t_{k}.png' for k in ('ews', 'ewn', 'nse', 'nsw')] + ['map/tile_road_t.png'] + \
    ['scene_test_portrait.png', 'scene_test_portrait_4x.png', 'map_test_portrait.png', 'map_test_portrait_4x.png', 'creator_test_portrait.png', 'creator_test_portrait_4x.png', 'fx_test_portrait.png', 'fx_test_portrait_3x.png']
EMAP = {e['path']: e for e in entries}
PORTRAIT = dict(native_resolution=[270, 480], display_scale='4x nearest (1080x1920)',
    carried_over_unchanged='monsters/*, map/loc_*, map/pawn_walk, map tiles, front paperdoll layers, ui icons, portrait frames, 9-slice panels (48x48, margins 6 - still valid at 270 wide), damage fonts, d6.',
    layout=PORTRAIT_LAYOUT,
    files=[dict(path=p, size=EMAP[p]['size'], anchor=EMAP[p].get('anchor'), frames=EMAP[p].get('frames', 1), frame_size=EMAP[p].get('frame_size'), notes=EMAP[p].get('notes', '')) for p in PORTRAIT_FILES if p in EMAP],
    legacy_landscape_files=sorted(LEGACY))
SEATD = DOLL.get('seat_defaults', {})
CLASSES_BLOCK = dict(list=CLASSES8, reads=dict(paladin='plate + visor helm, shield', wizard='blue robe, pointed hat, staff', ranger='green hood, bow', bard='beret + feather, lute',
    cleric='white/gold robe, gold holy cross on the back, mitre with lappets', rogue='dark leather + half-mask hood (pointed tip), dagger on the back', barbarian='bare arms, fur pelt/mantle, horned helm, axe on the back (skips outfit_base)', druid='leaf-green robe, antler circlet, tall leaf-topped staff'),
    layers=dict(front=['paperdoll/class_<c>.png', 'paperdoll/class_<c>_hat.png'], back=['paperdoll/back/class_back_<c>.png', 'paperdoll/back/class_back_<c>_hat.png']),
    skip_outfit_base=['barbarian'], seat_defaults=SEATD)
SEAT_RECIPE = dict(canvas=[48, 78], anchor=[24, 77],
    steps=['back/body_back_skin_<skin>', 'back/outfit_back tinted with outfit ramp (skip for barbarian)', 'back/class_back_<class>', 'back/hair_back_<hair> tinted with hair ramp, rows y < class hat hair_clip_y cleared when the hat is worn',
           'back/class_back_<class>_hat (if hat)', 'back/chair_back (always last)', 'ACTIVE: shift the composed image up 3px, then add a 1px #f8d040 outline (4-neighbour) around the union'],
    note='party/seat_<class>_idle/active.png are exactly this recipe applied to classes.seat_defaults (built in tools/build_doll.py seat()). A player-made hero uses the same recipe with the creator choices, so seat == creator doll.')
SKILLS_BLOCK = dict(size=[20, 20], naming='ui/skills/<class>_<1-4>.png (placeholder names; map to docs/CLASSES.md later)', slot='ui/skills/skill_slot*.png (32x32, icon at offset [6,6]); ui/skills/skill_cooldown_mask.png (24x24 at [4,4])',
    reason_20px='20px sits inside the 32px portrait buttons/slots with a 6px border; 16px looked lost in the 24px inner area.', motifs={k: SKM[k] for k in sorted(SKM)}, kinds={k: SKK[k] for k in sorted(SKK)}, per_class=5, passive_slot='ui/skills/skill_slot_passive.png (+_locked): octagon, gold rim, not pressable (no active state)', sheet='ui/skills/skill_sheet.png (+ _3x), 8x5, passives in octagon slots with a P tag')
FX_BLOCK = {p[3:-4]: {k: v for k, v in META[p].items() if k in ('frame_size', 'frames', 'fps', 'anchor', 'loop', 'segments', 'notes', 'style')} for p in sorted(META) if p.startswith('fx/')}
MAN = dict(
    project='Paladins of Pen and Paper', phase='0', generated=datetime.date.today().isoformat(),
    native_resolution=[270, 480], orientation='portrait (was landscape 480x270; landscape-only files are flagged legacy)', portrait=PORTRAIT, display_scale='4x integer, nearest-neighbour (texture_filter = NEAREST, snap 2D transforms/vertices to pixel)',
    palette=dict(file='palette/palette48.hex', count=48, colors=['#' + h for h in HEX], names=NAMES),
    conventions=dict(anchor='pixel coordinates [x,y] from the top-left of ONE frame; for bottom-centre anchors the point is the feet row.',
        strips='horizontal strips, frames left->right, all frames equal size.', alpha='binary (0 or 255) everywhere.'),
    damage_colors=dict(hp_damage='#ec5a44', mp='#4c9ce8', heal='#b4dc62', outline='#120c18',
        glyph_shade=dict(hp='#c02c2c', mp='#3466cc', heal='#7cbc3c'), files=['ui/dmg_font_hp.png', 'ui/dmg_font_mp.png', 'ui/dmg_font_heal.png']),
    font=dict(name='m5x7 (Daniel Linssen)', size_px=16, note='TTF font size 16 renders the 1x pixel grid at native 270x480 (cap height ~7px). Pair: m6x11 (same author) for headings; fallback Pixel Operator 8 (CC0).',
        license='CC0 1.0 Universal (attribution appreciated)', url='https://managore.itch.io/m5x7', bundled=False,
        alt=dict(name='Pixel Operator', license='CC0 1.0 (since v2018.10.04-1)', url='https://notabug.org/HarvettFox96/ttf-pixeloperator')),
    monsters={n: dict(frame_size=[80, 70], feet_anchor=[40, 64], hp_bar_anchor=META[f'monsters/{n}/{n}_idle.png']['hp_bar_anchor'],
        anims=dict(idle=dict(frames=2, fps=2, loop=True), attack=dict(frames=3, fps=5), hit=dict(frames=2, fps=8), death=dict(frames=4, fps=8)),
        notes='forward = +y (toward the party at the bottom of the screen); lunge +4px, knock-back -2px (up). Unchanged for portrait.') for n in ['goblin', 'bat', 'slime', 'skeleton', 'wolf', 'mushroom', 'golem', 'imp']},
    paperdoll=dict(
        front=dict(canvas=[32, 48], anchor=[16, 47], layer_order=['body_skin_<1-6>', 'outfit_base (tinted)', 'class_<c> (optional)', 'head_<1-6> (skin-remapped)', 'hair_<1-8> (tinted; clipped to y>=hair_clip_y if a hat is worn)', 'class_<c>_hat (optional)'],
            portrait_crop_rect=[6, 8, 20, 20]),
        seat_recipe=SEAT_RECIPE,
        back_seated=dict(canvas=[48, 78], anchor=[24, 77], scale_note='v4 polish: native 48x78 polygons (sloped shoulders wider than the waist, upper arms + forward-bent forearms, tapered robes with draped hems, belts/sashes, 3-tone shading with spine band + left rim light, low chair crest y60-64); party/seat_* are composed FROM these layers (seat_recipe)', layer_order=['back/body_back_skin_<1-6>', 'back/outfit_back (tinted)', 'back/class_back_<c>', 'back/hair_back_<1-8> (tinted)', 'back/class_back_<c>_hat', 'back/chair_back'],
            active_state='offset all layers -3px in y and add a 1px #f8d040 outline around the union (same as party/seat_*_active).'),
        heads=['round', 'square', 'chubby', 'freckles', 'glasses', 'beard'], hairs=['bald', 'short', 'spiky', 'ponytail', 'long', 'braids', 'afro', 'mohawk'],
        grayscale_keys=dict(K1='#46424e', K2='#6c6a76', K3='#9c9ca6', K4='#cfd0d4'),
        hair_ramps={k: ['#' + HEX[NAMES.index(c)] for c in v] for k, v in DOLL['hair_ramps'].items()},
        outfit_ramps={k: ['#' + HEX[NAMES.index(c)] for c in v] for k, v in DOLL['outfit_ramps'].items()},
        skin_reference=dict(base='#d89c72', shadow='#b27a4e', detail='#8c5836', blush='#ec5a44'),
        skin_tones=[dict(tone=i + 1, base='#' + HEX[NAMES.index(t[0])], shadow='#' + HEX[NAMES.index(t[1])], detail='#' + HEX[NAMES.index(t[2])], blush='#' + HEX[NAMES.index(t[3])]) for i, t in enumerate(DOLL['tones'])],
        shader_gdscript_note=SHADER if (SHADER := """shader_type canvas_item;
// Remap grayscale keys to a ramp row. Hair: ramp=hair_ramps.png (4 cols), outfit: outfit_ramps.png (3 cols, keys K2..K4),
// skin: skin_ramps.png with keys = skin_reference [blush, detail, shadow, base].
uniform sampler2D ramp : filter_nearest;
uniform int row = 0;
uniform vec3 k0 = vec3(0.275, 0.259, 0.306); // #46424e
uniform vec3 k1 = vec3(0.424, 0.416, 0.463); // #6c6a76
uniform vec3 k2 = vec3(0.612, 0.612, 0.651); // #9c9ca6
uniform vec3 k3 = vec3(0.812, 0.816, 0.831); // #cfd0d4
uniform int first_col = 0; // 0 for hair (K1..K4); outfit: set k0..k2 = K2..K4 and use 3 columns
void fragment() {
    vec4 c = texture(TEXTURE, UV);
    vec3 keys[4] = {k0, k1, k2, k3};
    for (int i = 0; i < 4; i++) {
        if (distance(c.rgb, keys[i]) < 0.01) { c.rgb = texelFetch(ramp, ivec2(i + first_col, row), 0).rgb; }
    }
    COLOR = c;
}
// GDScript alternative (bake once, no shader):
// var img := tex.get_image(); for y in img.get_height(): for x in img.get_width():
//     var c := img.get_pixel(x, y); var i := KEYS.find(c.to_html(false)); if i >= 0 and c.a > 0.5: img.set_pixel(x, y, ramp_img.get_pixel(i, row))
// return ImageTexture.create_from_image(img)
""") else ''),
    classes=CLASSES_BLOCK, skills=SKILLS_BLOCK, fx=FX_BLOCK,
    files=entries)
for _n, _v in RGJ['draft_monsters'].items():
    MAN['monsters'][_n] = dict(frame_size=[80, 70], feet_anchor=[40, 64], hp_bar_anchor=_v['hp_bar_anchor'], status=_v['status'], name=_v['name'], region=_v['region'], size=_v['size'], concept=_v['concept'], flying=_v['flying'],
        anims=dict(idle=dict(frames=2, fps=2, loop=True), attack=dict(frames=3, fps=5), hit=dict(frames=2, fps=8), death=dict(frames=4, fps=8)),
        approval=_v.get('approval', ''), notes='APPROVED 2026-09-28 (region pass). Same 80x70 strips / feet anchor / anims as the existing monsters; not referenced by data/monsters.json yet.')
MAN['regions'] = RGJ
MAN['items'] = ITJ
MAN['paperdoll']['seat_recipe']['steps_with_gear'] = ITJ['gear']['layer_order']
MAN['paperdoll']['seat_recipe']['gear_note'] = 'Gear overlays (paperdoll/gear/<id>.png, 48x78, anchor 24,77) slot into the recipe as steps_with_gear: armor after class_back and before hair/hat; off hand then main hand after the hat; chair_back stays last. Status: draft_pending_approval.'
MAN['paperdoll']['back_seated']['layer_order_with_gear'] = ITJ['gear']['layer_order']
MAN['location_backdrops'] = {p_['id']: dict(file=p_['backdrop'], region=p_['region'], status='approved', horizon_y=141, monster_feet_band=[222, 266], calm_below_y=300) for p_ in RGJ['places']}
json.dump(MAN, open(OUT + 'manifest.json', 'w'), indent=1)
# markdown
def fmt(v): return json.dumps(v) if not isinstance(v, str) else v
md = ['# Paladins of Pen and Paper: Phase 0 sprite pack', '', f'Generated {MAN["generated"]}. **Native 270x480 PORTRAIT** (was 480x270 landscape; landscape-only files are marked LEGACY), displayed at 4x with nearest-neighbour. Every PNG is RGBA with binary alpha and uses only the 48 colours in `palette/palette48.hex` (checked in `tools/compose.py`).', '',
      '## Conventions', '- Anchors are `[x, y]` pixel coordinates within ONE frame, measured from the top-left. A bottom-centre anchor marks the feet row.', '- Strips are horizontal with equal-size frames, read left to right.',
      '- Monsters: frames are 80x70, feet anchor [40,64]. Forward is +y, toward the party: attack lunges +4px and a hit knocks back 2px up. Death: white flash, then sinking plus a checkerboard dissolve (25/50/75%).', '',
      '## Damage colours', '| use | fill | shade | outline |', '|---|---|---|---|', '| HP damage | `#ec5a44` | `#c02c2c` | `#120c18` |', '| MP | `#4c9ce8` | `#3466cc` | `#120c18` |', '| Heal | `#b4dc62` | `#7cbc3c` | `#120c18` |', '',
      '## Font', '**m5x7** by Daniel Linssen, font size **16** (renders 1:1 on the native grid, cap height about 7px). Licence: **CC0 1.0** (attribution appreciated). URL: https://managore.itch.io/m5x7. Not bundled; download it from itch.io. Use m6x11 (same author) for headings. Fallback: Pixel Operator 8 (CC0 since v2018.10.04-1).', '',
      '## Paperdoll', '- Front canvas 32x48, anchor [16,47]. Layer order: `body_skin_N` → `outfit_base` (tinted) → `class_<c>` → `head_N` (skin-remapped) → `hair_N` (tinted) → `class_<c>_hat`.',
      '- While a hat is worn, hide hair rows with y < `hair_clip_y` (see the hat entries).', '- Back/seated canvas **48x78, anchor [24,77]** (v2 1.5x redraw, identical to `party/seat_*`). Order: `body_back_skin_N` → `outfit_back` → `class_back_<c>` → `hair_back_N` → `class_back_<c>_hat` → `chair_back`.',
      '- Hair, the shirt and the beard use grayscale keys K1 `#46424e`, K2 `#6c6a76`, K3 `#9c9ca6` and K4 `#cfd0d4`. The ramps are in `paperdoll/palettes/*_ramps.png` (1px per entry). Heads use reference skin tone 3; remap them with `skin_ramps.png` in a single simultaneous lookup. Pre-tinted copies are in `paperdoll/tinted/`.',
      '- Portrait crop: rect `[6,8,20,20]` of the composed front doll. Draw it at [2,2] in `portrait_frame` and at [4,4] in `hp_mp_card`.', '', '### Ramp remap shader (Godot 4)', '```glsl', SHADER.strip(), '```', '',
      '## Portrait (270x480)', 'Top to bottom in `scene_test_portrait.png` (v7, **max party 5**): scrollable initiative rail (8 combatants at step 29, next-round portrait clipped at the right), 3 monsters (feet y222-266), GM behind `combat/table_portrait.png` (**266x40**, anchor [133,39], bottom-centre [135,' + str(TBL_Y) + ']), 5 composed seats paladin(active)/cleric/rogue/druid/wizard at x 27/81/135/189/243, y ' + '/'.join(map(str, SEAT_Y)) + ' (slots 1 and 3 are 4px higher), HP/MP shown as seat-mounted bars (`seat_bars_frame` 44x10: HP 4px over MP 3px, at [seat_x-22, feet_y-11], current-HP number in outlined 3x5 digits at [bar_x+1, bar_y-6], gold-ringed `_active` for the active seat; no card row), v6 per-character action bar `ui/portrait/action_bar_v2.png` (270x50) at y430 with the gold `name_tab` at [4,420]: Attack/Cover (32px), gold divider, the active class skills 1-5 (32px, passives in the octagon slot, MP cost badges below), Item/Run 20px minis at the right. The old 4-seat layout is kept as a note in `portrait.layout.seats_v4_4party_note`.', '',
      '| portrait file | size | anchor | frames | notes |', '|---|---|---|---|---|'] + ['| %s | %dx%d | %s | %s | %s |' % (f['path'], f['size'][0], f['size'][1], fmt(f['anchor']) if f['anchor'] else '', f['frames'], f['notes']) for f in PORTRAIT['files']] + ['',
      '## Classes (8)', '| class | read | seat defaults (skin/head/hair/hair colour/outfit) |', '|---|---|---|'] + ['| %s | %s | %s |' % (c, CLASSES_BLOCK['reads'][c], ', '.join('%s=%s' % kv for kv in SEATD.get(c, {}).items())) for c in CLASSES8] + ['',
      '### Seat = creator doll (recipe)', 'Canvas 48x78, anchor [24,77]. ' + ' → '.join(SEAT_RECIPE['steps'][:6]) + '. ' + SEAT_RECIPE['steps'][6] + '. ' + SEAT_RECIPE['note'], '',
      '## Skill icons (20x20, 5 per class)', SKILLS_BLOCK['reason_20px'] + ' Active slot: ' + SKILLS_BLOCK['slot'] + '. Passive slot: ' + SKILLS_BLOCK['passive_slot'] + '.', '', '| file | motif | suggested |', '|---|---|---|'] + ['| ui/skills/%s.png | %s | %s |' % (k, v, SKK[k]) for k, v in sorted(SKM.items())] + ['',
      '## Skill card popup (portrait)', 'Tap a skill once to open its notebook card (9-slice `ui/portrait/skill_card_panel.png`, margins L14 T10 R6 B6, tiled; tail `skill_card_tail.png`) and arm the slot (`skill_slot_armed.png`, 2 frames). Tap the same slot again to cast; another slot switches; elsewhere closes; passives never cast. Card: 2x icon frame, name, ACTIVE/PASSIVE tag, MP badge, target icon + text, cooldown, 3-line description, prompt strip (ready pulse / passive / NOT ENOUGH MP / ON COOLDOWN: n). Rects: `' + json.dumps(CARD_RECTS) + '`. Mocks: `scene_test_portrait_skillcard(+_4x).png`, `ui/portrait/skill_card_examples(+_3x).png`. All copy is PLACEHOLDER.', '',
      '## Greenmere regions (approved 2026-09-28)', 'Regions = `places[].kind` in data/region.json. Backdrops `combat/bg_<location>_portrait.png` (270x480, horizon y141, monster feet y222-266, calm below y300). New monsters (same 80x70 strips/anchors/anims) are listed in `manifest.json` under `monsters` with `status: approved`, and the full table is in `regions`. Approval sheets: `approval/backdrops_1x.png` / `_2x`, `approval/monster_lineup.png` / `_2x`, composite `scene_test_portrait_lantern_reach(+_4x).png`, extra `approval/scene_*.png`.', '',
      '| location | region | lv | existing monsters | new | backdrop |', '|---|---|---|---|---|---|'] + ['| %s | %s | %d | %s | %s | %s |' % (p_['name'], p_['region'], p_['level'], ', '.join(p_['monsters']) or '(none, town)', ', '.join(p_['suggested_new']) or '-', p_['backdrop']) for p_ in RGJ['places']] + ['',
      '| new monster | region | size | concept |', '|---|---|---|---|'] + ['| %s (`%s`) | %s | %s | %s |' % (v['name'], k, v['region'], v['size'], v['concept']) for k, v in RGJ['draft_monsters'].items()] + ['',
      '## Items + gear overlays (DRAFT, pending approval)', '40 item icons `ui/items/<id>.png` (16x16, no rarity border, 1px #120c18 outline, pack palette) and 26 back-view gear overlays `paperdoll/gear/<id>.png` (48x78, anchor [24,77], same canvas as the seat doll; pixels under `chair_back` are cleared). Built by `tools/build_items.py` (art in `draft_items.py`, `draft_gear.py`). Approval: `approval/items_1x.png` / `items_4x.png`, `approval/gear_seated.png` / `gear_seated_4x.png` (+ `gear_seated_runtime_on_top.png`), `approval/gear_overlays(_3x).png`, composite `scene_test_portrait_gear(+_4x).png`.', '',
      '**Seat layer order with gear:** ' + ' -> '.join('`%s`' % x for x in ITJ['gear']['layer_order']) + '.', '', '**Placement:** ' + '; '.join('%s: %s' % kv for kv in ITJ['gear']['placement'].items()) + '.', '', '**Runtime note:** ' + ITJ['gear']['runtime_note'], '',
      '| id | name | slot | rarity | icon | doll | visual |', '|---|---|---|---|---|---|---|'] + ['| %s | %s | %s | %s | %s | %s | %s |' % (i['id'], i['name'], i['slot'], i['rarity'], i['icon'], i['doll'] or '-', i['visual']) for i in ITJ['list']] + ['',
      '## Skill FX', '| strip | frame size | frames | fps | anchor | loop / segments | notes |', '|---|---|---|---|---|---|---|'] + ['| fx/%s.png | %s | %s | %s | %s | %s | %s |' % (k, 'x'.join(map(str, v['frame_size'])), v['frames'], v['fps'], fmt(v['anchor']), fmt(v.get('segments', v.get('loop'))), v['notes']) for k, v in FX_BLOCK.items()] + ['',
      'FX style: no black outline (glow effects); bright core stepping to a darker coloured rim, binary alpha, fades via ordered dither. `fx_test_portrait.png` shows one frame of each at native scale.', '',
      '**Legacy (landscape-only):** ' + ', '.join('`%s`' % p for p in PORTRAIT['legacy_landscape_files']), '',
      '## Files', '| path | size | frames | frame size | fps | anchor | extra | notes |', '|---|---|---|---|---|---|---|---|']
for e in entries:
    extra = {k: v for k, v in e.items() if k not in ('path', 'size', 'frames', 'frame_size', 'fps', 'anchor', 'notes', 'canvas', 'loop')}
    if 'size' not in e: md.append('| %s | - | | | | | | %s |' % (e['path'], e['notes'])); continue
    md.append('| %s | %dx%d | %s | %s | %s | %s | %s | %s |' % (e['path'], e['size'][0], e['size'][1], e.get('frames', 1), 'x'.join(map(str, e.get('frame_size', e['size']))), e.get('fps', ''), fmt(e.get('anchor', '')), ', '.join(f'{k}={fmt(v)}' for k, v in extra.items()), e.get('notes', '')))
open(OUT + 'MANIFEST.md', 'w').write('\n'.join(md) + '\n')
print('manifest entries', len(entries))
