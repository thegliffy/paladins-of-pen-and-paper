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
for f in ('meta_cut.json', 'meta_proc.json', 'meta_doll.json'):
    d = json.load(open(W_ + f)); META.update(d['meta'] if 'meta' in d else d)
DOLL = json.load(open(W_ + 'meta_doll.json'))

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
    for rel in [f'paperdoll/body_skin_{skin}.png', f'paperdoll/tinted/outfit_{ocol}.png'] + ([f'paperdoll/class_{cls}.png'] if cls else []) + \
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
         doll_front(3, 4, 4, 'ginger', 'green', 'ranger', True), doll_front(5, 3, 7, 'black', 'red', 'bard', True)]
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

# ---------- scene_test_portrait ----------
P = L('combat/bg_forest_portrait.png')
def pput(im, ax, ay, anchor): P.alpha_composite(im, (ax - anchor[0], ay - anchor[1]))
ini = [L(f'monsters/{n}/{n}_portrait.png') for n in ('goblin', 'bat', 'slime')] + [portrait_of(p) for p in party[:2]]
x0 = 135 - (len(ini) * 26 - 2) // 2
for i, p in enumerate(ini):
    fr = L('ui/portrait_frame_active.png' if i == 0 else 'ui/portrait_frame.png'); fr.alpha_composite(p, (2, 2)); P.alpha_composite(fr, (x0 + i * 26, 4))
PMON = [('goblin', 52, 190), ('bat', 135, 160), ('slime', 220, 194)]
for n, x, y in PMON:
    m = META[f'monsters/{n}/{n}_idle.png']; im = frame_of(f'monsters/{n}/{n}_idle.png', 0, 80); pput(im, x, y, m['anchor'])
    hx, hy = x - 40 + m['hp_bar_anchor'][0], y - 64 + m['hp_bar_anchor'][1]
    pput(L('ui/enemy_bar_bg.png'), hx, hy, (16, 4)); pct = {'goblin': 1.0, 'bat': 0.6, 'slime': 0.85}[n]
    P.alpha_composite(L('ui/enemy_bar_hp.png').crop((0, 0, int(30 * pct), 3)), (hx - 15, hy - 3))
for i, ch in enumerate('-7'):
    k = '0123456789+-'.index(ch); P.alpha_composite(DIG.crop((k * 7, 0, k * 7 + 7, 9)), (158 + i * 6, 100))
TBL_Y = 300                     # table bottom row
pput(L('combat/gm_idle.png'), 135, TBL_Y - 40 + 9, (22, 45))
pput(L('combat/table_portrait.png'), 135, TBL_Y, (125, 39))
scr = L('combat/gm_screen.png'); pput(scr, 104, TBL_Y - 40 + 16, (scr.width // 2, scr.height - 1))
pput(frame_of('combat/d20_roll.png', 3, 24), 160, TBL_Y - 40 + 14, (12, 23))
pput(frame_of('combat/d6_blue.png', 4, 8), 181, TBL_Y - 40 + 10, (4, 7)); pput(frame_of('combat/d6_red.png', 2, 8), 191, TBL_Y - 40 + 12, (4, 7))
SEATS_P = [('paladin', 38, 336, True), ('wizard', 102, 332, False), ('ranger', 168, 332, False), ('bard', 232, 336, False)]
for c, x, y, act in SEATS_P: pput(L(f'party/seat_{c}_{"active" if act else "idle"}.png'), x, y, (24, 77))
for i, p in enumerate(party):
    cd = L('ui/portrait/hp_mp_card_narrow.png'); cd.alpha_composite(portrait_of(p), (4, 4))
    hp = [1.0, 0.7, 0.45, 0.9][i]; mp = [0.5, 1.0, 0.6, 0.8][i]
    cd.alpha_composite(L('ui/portrait/bar_hp_88.png').crop((0, 0, int(88 * hp), 5)), (36, 6)); cd.alpha_composite(L('ui/portrait/bar_mp_88.png').crop((0, 0, int(88 * mp), 5)), (36, 16))
    P.alpha_composite(cd, (4 + (i % 2) * 132, 366 + (i // 2) * 30))
P.alpha_composite(L('ui/portrait/action_bar.png'), (0, 432))
for i, n in enumerate(['attack', 'skill', 'item', 'cover', 'run']):
    P.alpha_composite(L(f'ui/portrait/btn32_{n}{"_active" if i == 0 else ""}.png'), (META['ui/portrait/action_bar.png']['button_rects'][i][0], 432 + 8))
save(P, 'scene_test_portrait.png'); save(upsc(P, 4), 'scene_test_portrait_4x.png')
PORTRAIT_LAYOUT = dict(initiative_strip=dict(y=4, frame='ui/portrait_frame*.png', step=26),
    monsters=[dict(name=n, feet=[x, y]) for n, x, y in PMON], table=dict(file='combat/table_portrait.png', bottom_centre=[135, TBL_Y]),
    gm=dict(file='combat/gm_idle.png', bottom_centre=[135, TBL_Y - 31]),
    seats=[dict(cls=c, bottom_centre=[x, y], active=a) for c, x, y, a in SEATS_P], seat_note='outer seats 4px lower (stagger) so all 4 silhouettes read; GM stays clear between the inner seats.',
    hp_cards=dict(file='ui/portrait/hp_mp_card_narrow.png', grid_origin=[4, 366], step=[132, 30]),
    action_bar=dict(file='ui/portrait/action_bar.png', pos=[0, 432]))

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
    y += 24 + 9
def swatches(cols, active):
    global y; x = 10
    for i, col in enumerate(cols):
        f = L('ui/swatch_frame_active.png' if i == active else 'ui/swatch_frame.png'); f.paste(col + (255,), (2, 2, 14, 14)); CR.alpha_composite(f, (x, y)); x += 20
    y += 16 + 9
label('HEAD'); thumbs([portrait_of(doll_front(cur['skin'], h, 1, 'brown', 'white')) for h in range(1, 7)], cur['head'] - 1)
label('HAIR'); thumbs([portrait_of(doll_front(cur['skin'], 1, h, cur['hcol'], 'white')) for h in range(1, 9)], cur['hair'] - 1)
label('SKIN'); swatches([C['skin%d' % k] for k in range(1, 7)], cur['skin'] - 1)
HR = DOLL['hair_ramps']; label('HAIR COLOUR'); swatches([C[v[2]] for v in HR.values()], list(HR).index(cur['hcol']))
OR = DOLL['outfit_ramps']; label('OUTFIT COLOUR'); swatches([C[v[1]] for v in OR.values()], list(OR).index(cur['ocol']))
label('CLASS'); x = 10
for i, c in enumerate(['paladin', 'wizard', 'ranger', 'bard']):
    cell = nine('ui/panel_dark.png' if c != cur['cls'] else 'ui/panel_parchment.png', 40, 56, 6) if False else None
    fr = L('ui/portrait_frame_active.png' if c == cur['cls'] else 'ui/portrait_frame.png')
    box = Image.new('RGBA', (40, 54)); box.paste(C['sand'] + (255,), (0, 0, 40, 54))
    box.alpha_composite(doll_front(cur['skin'], cur['head'], cur['hair'], cur['hcol'], cur['ocol'], c, True), (4, 4))
    edge = C['gold'] if c == cur['cls'] else C['wood']
    for bx in range(40): box.putpixel((bx, 0), edge + (255,)); box.putpixel((bx, 53), edge + (255,))
    for by in range(54): box.putpixel((0, by), edge + (255,)); box.putpixel((39, by), edge + (255,))
    CR.alpha_composite(box, (x, y)); text(CR, x + 20 - text_w(c.upper()) // 2, y + 56, c.upper(), C['bark']); x += 46
y += 66
CR.alpha_composite(L('ui/btn_confirm.png'), (135 - 56 - 6, 440)); CR.alpha_composite(L('ui/btn_random.png'), (135 + 6, 440))
save(CR, 'creator_test_portrait.png'); save(upsc(CR, 4), 'creator_test_portrait_4x.png')
print('creator rows end y', y)
for k in ('scene_test_portrait.png', 'map_test_portrait.png', 'creator_test_portrait.png'):
    META[k] = dict(notes='PORTRAIT 270x480 mock built only from pack files (QA).'); META[k.replace('.png', '_4x.png')] = dict(notes='4x nearest upscale.')


# ---------------- contact sheet ----------------
BGc = C['gray']; CW = 796
secs = [('COMBAT', ['combat/*.png']), ('MONSTERS', ['monsters/*/*_idle.png', 'monsters/*/*_attack.png', 'monsters/*/*_hit.png', 'monsters/*/*_death.png', 'monsters/*/*_still.png', 'monsters/*/*_portrait.png']),
        ('PARTY SEATS', ['party/*.png']), ('PAPERDOLL FRONT LAYERS', ['paperdoll/body_*.png', 'paperdoll/head_*.png', 'paperdoll/hair_*.png', 'paperdoll/outfit_base.png', 'paperdoll/class_*.png']),
        ('PAPERDOLL BACK SEATED LAYERS', ['paperdoll/back/*.png']), ('PAPERDOLL RAMPS + PORTRAITS', ['paperdoll/palettes/*.png', 'paperdoll/portrait_crop_examples.png']),
        ('MAP', ['map/tile_*.png', 'map/loc_*.png', 'map/pawn_walk.png', 'map/tiles_preview.png']), ('UI', ['ui/*.png']), ('UI PORTRAIT', ['ui/portrait/*.png']), ('PALETTE', ['palette/palette48.png'])]
items = []
seen = set()
for title, pats in secs:
    items.append(('__H__', title))
    for pt in pats:
        for p in sorted(glob.glob(OUT + pt)):
            rel = p[len(OUT):]
            if rel in seen or rel == 'combat/bg_forest.png' and False: continue
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
            dict(path='tools/', notes='reproducible build scripts: build_cut.py -> build_proc.py -> build_doll.py -> compose.py (python w/ pillow+numpy+scipy). tools/_work holds intermediates.')]
LEGACY = {'combat/bg_forest.png': 'use combat/bg_forest_portrait.png', 'combat/table.png': 'use combat/table_portrait.png (250x40)',
    'ui/hp_mp_card.png': 'use ui/portrait/hp_mp_card_narrow.png', 'ui/bar_hp.png': 'use ui/portrait/bar_hp_88.png or bar_hp_tile', 'ui/bar_mp.png': 'use ui/portrait/bar_mp_88.png or bar_mp_tile',
    'ui/bar_bg.png': 'baked into the narrow card', 'scene_test.png': 'see scene_test_portrait.png', 'scene_test_4x.png': 'see scene_test_portrait_4x.png'}
for n in ['attack', 'skill', 'item', 'cover', 'run']:
    for sfx in ('', '_active'): LEGACY[f'ui/btn_{n}{sfx}.png'] = f'portrait bottom bar uses ui/portrait/btn32_{n}{sfx}.png'
for e in entries:
    if e['path'] in LEGACY:
        e['legacy'] = True; e['notes'] = 'LEGACY (landscape 480x270): ' + LEGACY[e['path']] + '. ' + e.get('notes', '').replace('LEGACY (landscape). ', '')
PORTRAIT_FILES = ['combat/bg_forest_portrait.png', 'combat/table_portrait.png', 'combat/d20_roll.png', 'combat/d20_results.png', 'combat/d20_nat20.png'] + \
    [f'party/seat_{c_}_{s_}.png' for c_ in ['paladin', 'wizard', 'ranger', 'bard'] for s_ in ('idle', 'active')] + \
    sorted(p[len(OUT):] for p in glob.glob(OUT + 'ui/portrait/*.png')) + ['ui/icon_gold.png', 'ui/btn_menu.png', 'ui/btn_confirm.png', 'ui/btn_random.png', 'ui/btn_arrow_left.png', 'ui/btn_arrow_right.png',
    'ui/swatch_frame.png', 'ui/swatch_frame_active.png', 'map/marker_arrow.png'] + [f'map/tile_road_t_{k}.png' for k in ('ews', 'ewn', 'nse', 'nsw')] + ['map/tile_road_t.png'] + \
    ['scene_test_portrait.png', 'scene_test_portrait_4x.png', 'map_test_portrait.png', 'map_test_portrait_4x.png', 'creator_test_portrait.png', 'creator_test_portrait_4x.png']
EMAP = {e['path']: e for e in entries}
PORTRAIT = dict(native_resolution=[270, 480], display_scale='4x nearest (1080x1920)',
    carried_over_unchanged='monsters/*, map/loc_*, map/pawn_walk, map tiles, front paperdoll layers, ui icons, portrait frames, 9-slice panels (48x48, margins 6 - still valid at 270 wide), damage fonts, d6.',
    layout=PORTRAIT_LAYOUT,
    files=[dict(path=p, size=EMAP[p]['size'], anchor=EMAP[p].get('anchor'), frames=EMAP[p].get('frames', 1), frame_size=EMAP[p].get('frame_size'), notes=EMAP[p].get('notes', '')) for p in PORTRAIT_FILES if p in EMAP],
    legacy_landscape_files=sorted(LEGACY))
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
        back_seated=dict(canvas=[48, 78], anchor=[24, 77], scale_note='v2: 1.5x redraw, matches party/seat_* exactly', layer_order=['back/body_back_skin_<1-6>', 'back/outfit_back (tinted)', 'back/class_back_<c>', 'back/hair_back_<1-8> (tinted)', 'back/class_back_<c>_hat', 'back/chair_back'],
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
    files=entries)
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
      '## Portrait (270x480)', 'Top to bottom in `scene_test_portrait.png`: initiative strip (y4), 3 monsters staggered (feet y160-194), GM behind `combat/table_portrait.png` (250x40, bottom-centre [135,300]), 4 seats at 1.5x (bottom-centre x 38/102/168/232, y 336/332/332/336, outer pair 4px lower), 2x2 narrow HP/MP cards (130x28, origin [4,366], step [132,30]), `ui/portrait/action_bar.png` at y432 with 5 `btn32_*` buttons at x 19/69/119/169/219, y440.', '',
      '| portrait file | size | anchor | frames | notes |', '|---|---|---|---|---|'] + ['| %s | %dx%d | %s | %s | %s |' % (f['path'], f['size'][0], f['size'][1], fmt(f['anchor']) if f['anchor'] else '', f['frames'], f['notes']) for f in PORTRAIT['files']] + ['',
      '**Legacy (landscape-only):** ' + ', '.join('`%s`' % p for p in PORTRAIT['legacy_landscape_files']), '',
      '## Files', '| path | size | frames | frame size | fps | anchor | extra | notes |', '|---|---|---|---|---|---|---|---|']
for e in entries:
    extra = {k: v for k, v in e.items() if k not in ('path', 'size', 'frames', 'frame_size', 'fps', 'anchor', 'notes', 'canvas', 'loop')}
    if 'size' not in e: md.append('| %s | - | | | | | | %s |' % (e['path'], e['notes'])); continue
    md.append('| %s | %dx%d | %s | %s | %s | %s | %s | %s |' % (e['path'], e['size'][0], e['size'][1], e.get('frames', 1), 'x'.join(map(str, e.get('frame_size', e['size']))), e.get('fps', ''), fmt(e.get('anchor', '')), ', '.join(f'{k}={fmt(v)}' for k, v in extra.items()), e.get('notes', '')))
open(OUT + 'MANIFEST.md', 'w').write('\n'.join(md) + '\n')
print('manifest entries', len(entries))
