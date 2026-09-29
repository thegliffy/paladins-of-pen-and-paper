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
TBL_Y = 292                     # table bottom row
pput(L('combat/gm_idle.png'), 135, TBL_Y - 40 + 9, (22, 45))
pput(L('combat/table_portrait.png'), 135, TBL_Y, (125, 39))
scr = L('combat/gm_screen.png'); pput(scr, 104, TBL_Y - 40 + 16, (scr.width // 2, scr.height - 1))
pput(frame_of('combat/d20_roll.png', 3, 24), 160, TBL_Y - 40 + 14, (12, 23))
pput(frame_of('combat/d6_blue.png', 4, 8), 181, TBL_Y - 40 + 10, (4, 7)); pput(frame_of('combat/d6_red.png', 2, 8), 191, TBL_Y - 40 + 12, (4, 7))
SEATS_P = [('paladin', 38, 343, True), ('wizard', 102, 339, False), ('ranger', 168, 339, False), ('bard', 232, 343, False)]
for c, x, y, act in SEATS_P: pput(L(f'party/seat_{c}_{"active" if act else "idle"}.png'), x, y, (24, 77))
for i, p in enumerate(party):
    cd = L('ui/portrait/hp_mp_card_narrow.png'); cd.alpha_composite(portrait_of(p), (4, 4))
    hp = [1.0, 0.7, 0.45, 0.9][i]; mp = [0.5, 1.0, 0.6, 0.8][i]
    cd.alpha_composite(L('ui/portrait/bar_hp_88.png').crop((0, 0, int(88 * hp), 5)), (36, 6)); cd.alpha_composite(L('ui/portrait/bar_mp_88.png').crop((0, 0, int(88 * mp), 5)), (36, 16))
    P.alpha_composite(cd, (4 + (i % 2) * 132, 368 + (i // 2) * 30))
P.alpha_composite(L('ui/portrait/action_bar.png'), (0, 432))
for i, n in enumerate(['attack', 'skill', 'item', 'cover', 'run']):
    P.alpha_composite(L(f'ui/portrait/btn32_{n}{"_active" if i == 0 else ""}.png'), (META['ui/portrait/action_bar.png']['button_rects'][i][0], 432 + 8))
save(P, 'scene_test_portrait.png'); save(upsc(P, 4), 'scene_test_portrait_4x.png')
PORTRAIT_LAYOUT = dict(initiative_strip=dict(y=4, frame='ui/portrait_frame*.png', step=26),
    monsters=[dict(name=n, feet=[x, y]) for n, x, y in PMON], table=dict(file='combat/table_portrait.png', bottom_centre=[135, TBL_Y]),
    gm=dict(file='combat/gm_idle.png', bottom_centre=[135, TBL_Y - 31]),
    seats=[dict(cls=c, bottom_centre=[x, y], active=a) for c, x, y, a in SEATS_P], seat_note='outer seats 4px lower (stagger) so all 4 silhouettes read; GM stays clear between the inner seats.',
    hp_cards=dict(file='ui/portrait/hp_mp_card_narrow.png', grid_origin=[4, 368], step=[132, 30]),
    action_bar=dict(file='ui/portrait/action_bar.png', pos=[0, 432]))

# ---------- map_test_portrait ----------
TL = {k: L(f'map/tile_{k}.png') for k in ['grass', 'grass_flowers', 'road_h', 'road_v', 'road_cross', 'river_h', 'bridge_v']}
for k in ('es', 'ws', 'en', 'wn'): TL['c_' + k] = L(f'map/tile_road_corner_{k}.png')
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
            elif cnt >= 3: k = 'road_cross'
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
    y += 24 + 5
def swatches(cols, active):
    global y; x = 10
    for i, col in enumerate(cols):
        f = L('ui/swatch_frame_active.png' if i == active else 'ui/swatch_frame.png'); f.paste(col + (255,), (2, 2, 14, 14)); CR.alpha_composite(f, (x, y)); x += 20
    y += 16 + 5
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

