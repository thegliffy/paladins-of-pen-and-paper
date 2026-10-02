# Refine pass (phase 1 sheets + refine-2 final deliverables): approval sheets. exec'd inside compose.py's globals (uses L/ROOT_, _scene, nine, label_bar, upsc).
import refine_style as RS
REF = json.load(open(W_ + 'meta_refine.json')); PRE = OUT + REF['before_root']
ITEMS_REPO = {i['id']: i for i in json.load(open('/workspace/paladins-repo-ro/data/items.json'))}
def _set_root(r):
    global ROOT_; ROOT_ = r
def _scene_at(root, seats, **kw):
    _set_root(root); ns = dict(globals()); ns.update(SCENE_SEAT_FILE=f'approval/refine/parts/{seats}/seat_{{c}}_{{st}}.png', **kw)
    exec(compile(_scene, 'scene_block', 'exec'), ns); _set_root(OUT); return ns['P']
def pair_sheet(a, b, title, la='BEFORE', lb='AFTER (REFINE-2, REVIEW)'):
    G = 6; Wd = a.width + b.width + 3 * G; S = Image.new('RGBA', (Wd, max(a.height, b.height) + 12 + 2 * G + 11), C['slate'] + (255,))
    label_bar(S, G, G, Wd - 2 * G, title)
    for k, (im, lab) in enumerate(((a, la), (b, lb))):
        x0 = G + k * (a.width + G); label_bar(S, x0, G + 11, im.width, lab, bg='outline'); S.alpha_composite(im, (x0, G + 22))
    return S
def emit(S, rel, k, note):
    save(S, rel + '.png'); save(upsc(S, k), rel + f'_{k}x.png')
    META[rel + '.png'] = dict(status='review', refine='refine-2', notes='APPROVAL SHEET (not runtime): ' + note)
    META[rel + f'_{k}x.png'] = dict(status='review', refine='refine-2', notes=f'{k}x nearest of {rel}.png.')
# (a) meadow  (b) cave
for key, lid, trio, ttl in (('combat_meadow', 'millpond', ['goblin', 'bramblet', 'grinmud_toad'], 'MEADOW COMBAT: MILLPOND'), ('combat_cave', 'howling_cleft', ['bat', 'gloomgrub', 'dripfang'], 'CAVE COMBAT: HOWLING CLEFT')):
    kw = dict(SCENE_BG=f'combat/bg_{lid}_portrait.png', SCENE_PMON=[(trio[0], 52, 262), (trio[1], 135, 222), (trio[2], 220, 266)],
              SCENE_INIT=[('p', 0), ('m', trio[0]), ('p', 4), ('p', 3), ('m', trio[1]), ('p', 2), ('m', trio[2]), ('p', 1)], SCENE_PCT={trio[0]: 1.0, trio[1]: 0.6, trio[2]: 0.85})
    bA = _scene_at(PRE, 'before', **kw); bB = _scene_at(OUT, 'after', **kw)
    emit(pair_sheet(bA, bB, ttl + ', PARTY IN CLASS KIT'), f'approval/refine/{key}_before_after', 3,
         f'{lid} combat, before (pre-refine pack + pre-refine gear) vs after (refined backdrop, {", ".join(trio)}, table, GM, seat bars, panels, gear). Seats = kit seats (noweapon back layer + gear).')
# (c) town hub mock (mirrors scripts/table/session_screen.gd show_hub: banner, caption, seats + table, 5-button bar)
HUB_BTNS = [('travel', 'TRAVEL', 'icon_run'), ('fight', 'FIGHT', 'icon_attack'), ('rest', 'REST', 'icon_cover'), ('quest', 'QUEST', 'icon_skill'), ('gear', 'GEAR', 'icon_item')]
def flat_plate(w, h):
    im = Image.new('RGBA', (w, h), C['wood_dk'] + (255,)); im.paste(C['cream'] + (255,), (2, 2, w - 2, h - 2)); return im
def repo_ui(n): return RS.to_palette(Image.open(PRE + 'repo_art_ui/' + n + '.png').convert('RGBA'))
def nine_im(src, Wd, Ht, m):
    tmp = W_ + '_nine_tmp.png'; src.save(tmp); r0 = ROOT_
    _set_root(''); out = nine(tmp, Wd, Ht, m); _set_root(r0); return out
def hub(place, after, seats=None):
    root = OUT if after else PRE
    _set_root(root)
    bg = L(f'combat/bg_{place["id"]}_portrait.png') if (after or os.path.exists(PRE + f'combat/bg_{place["id"]}_portrait.png')) else RS.to_palette(Image.open(PRE + f'repo_placeholders/combat/bg_{place["id"]}_portrait.png'))
    P_ = bg.copy()
    def put(im, ax, ay, an): P_.alpha_composite(im, (ax - an[0], ay - an[1]))
    put(L('combat/gm_idle.png'), 135, TBL_Y - 40 + 9, (22, 45)); put(L('combat/table_portrait.png'), 135, TBL_Y, (133, 39))
    scr = L('combat/gm_screen.png'); put(scr, 100, TBL_Y - 40 + 16, (scr.width // 2, scr.height - 1))
    put(frame_of('combat/d20_roll.png', 0, 24), 164, TBL_Y - 40 + 14, (12, 23))
    put(frame_of('combat/d6_blue.png', 0, 8), 214, TBL_Y - 40 + 10, (4, 7)); put(frame_of('combat/d6_red.png', 0, 8), 224, TBL_Y - 40 + 12, (4, 7))
    for i in [1, 3, 0, 2, 4]:
        put(Image.open(OUT + f'approval/refine/parts/{seats or ("after" if after else "before")}/seat_{PPARTY[i]}_idle.png').convert('RGBA'), SEAT_X[i], SEAT_Y[i], (24, 77))
    for i in range(5):
        bx, by, _, _ = seat_bar_rect(SEAT_X[i], SEAT_Y[i]); fr = L('ui/portrait/seat_bars_frame.png')
        hp, mp = HPMP[i]; fr.alpha_composite(L('ui/portrait/seat_bar_hp.png').crop((0, 0, max(1, int(42 * hp)), 4)), (1, 1))
        fr.alpha_composite(L('ui/portrait/seat_bar_mp.png').crop((0, 0, max(1, int(42 * mp)), 3)), (1, 6)); P_.alpha_composite(fr, (bx, by))
    ban = f'{place["name"].upper()}   515 GOLD'; cap = place['description'].upper()
    if after:
        P_.alpha_composite(nine('ui/hub/header_plate.png', 262, 18, 4), (4, 4)); P_.alpha_composite(nine('ui/hub/header_plate.png', 262, 28, 4), (4, 32))
    else:
        P_.alpha_composite(flat_plate(262, 18), (4, 4)); P_.alpha_composite(flat_plate(262, 28), (4, 32))
    text(P_, 135 - text_w(ban) // 2, 11, ban, C['outline']); text(P_, 135 - text_w(cap) // 2, 44, cap, C['outline'])
    for k, (bid, lab, ricon) in enumerate(HUB_BTNS):
        x = 3 + k * 53; y = 432; dis = bid == 'fight'
        if after: b = nine('ui/hub/hub_button_down.png' if dis else 'ui/hub/hub_button.png', 52, 44, 6); ic = L(f'ui/hub/icon_{bid}.png')
        else: b = nine_im(repo_ui('btn_tan_down' if dis else 'btn_tan'), 52, 44, 4); ic = repo_ui(ricon)
        if dis:
            a = np.array(ic); a[..., 3] = np.where((np.indices(a.shape[:2]).sum(0) % 2 == 0), a[..., 3], 0); ic = Image.fromarray(a)
        b.alpha_composite(ic, (18, 8)); text(b, 26 - text_w(lab) // 2, 30, lab, C['mist'] if dis else C['outline']); P_.alpha_composite(b, (x, y))
    _set_root(OUT); return P_
_rj = json.load(open('/workspace/paladins-repo-ro/data/region.json'))
def _walk(o):
    if isinstance(o, dict):
        if 'id' in o and 'description' in o and 'kind' in o: yield o
        for v in o.values(): yield from _walk(v)
    elif isinstance(o, list):
        for v in o: yield from _walk(v)
PLACES = {p_['id']: p_ for p_ in _walk(_rj)}
G = 6; HB = Image.new('RGBA', (4 * 270 + 5 * G, 480 + 2 * G + 22 + 11), C['slate'] + (255,))
label_bar(HB, G, G, HB.width - 2 * G, 'TOWN HUB (MOCK OF SESSION_SCREEN.SHOW_HUB)', 'TEXT IN PACK 3X5 FONT; GAME USES M5X7')
for k, (pid, after, lab) in enumerate((('candlewick', False, 'CANDLEWICK BEFORE'), ('candlewick', True, 'CANDLEWICK AFTER'), ('brinewick', False, 'BRINEWICK BEFORE = REPO PLACEHOLDER'), ('brinewick', True, 'BRINEWICK AFTER (NEW)'))):
    x0 = G + k * (270 + G); label_bar(HB, x0, G + 11, 270, lab, bg='outline'); HB.alpha_composite(hub(PLACES[pid], after), (x0, G + 22))
emit(HB, 'approval/refine/hub_towns_before_after', 3, 'town hub mock: Candlewick before/after, Brinewick repo placeholder (recoloured Candlewick, quantised to the palette for this sheet) vs the new Brinewick backdrop. Before UI = StyleBoxFlat plates + res://art/ui btn_tan/icons (quantised); after = ui/hub/* 9-slices + icons.')
# (d) icons
def slot(icon):
    s = Image.new('RGBA', (20, 20), C['wood_dk'] + (255,)); s.paste(C['ink'] + (255,), (1, 1, 19, 19)); s.alpha_composite(icon, (2, 2)); return s
def ic_before(i):
    p1 = PRE + f'ui/items/{i}.png'
    return Image.open(p1).convert('RGBA') if os.path.exists(p1) else RS.to_palette(Image.open(PRE + f'repo_placeholders/ui/items/{i}.png').convert('RGBA'))
QK = ['slime_gel', 'wolf_burr', 'gull_feather', 'bat_ear', 'golem_grit']; SK = ['salt_mace', 'tide_axe', 'echo_bow', 'shell_buckler', 'cave_draught', 'gull_charm']
ROWS = [('FIXED WEAPONS + BOWS: THICKER, READABLE AT 1X', ['oath_blade', 'reed_staff', 'sap_crook', 'lamp_staff', 'gravel_axe', 'thorn_bow', 'marsh_bow']),
        ('POCKET KNIFE VS NIGHT SHARD: FOLDING KNIFE VS UPRIGHT JAGGED CRYSTAL', ['pocket_knife', 'night_shard']),
        ('EXISTING CROSS-SECTION: ALREADY ON STYLE, UNCHANGED', ['kettle_shield', 'hedge_mail', 'keep_plate', 'chapel_mace', 'tonic', 'blue_ether', 'bread_charm']),
        ('NEW QUEST DROPS, PHASE-1 SAMPLES (ALL 17 IN FINAL SHEET; BEFORE = REPO PLACEHOLDER)', QK),
        ('NEW SHOP / CRAFT ICONS, PHASE-1 SAMPLES (ALL IN FINAL SHEET; BEFORE = REPO PLACEHOLDER)', SK)]
CW, CH = 54, 34; IW = 7 * CW + 2 * G
IS = Image.new('RGBA', (IW, G + 13 + len(ROWS) * (11 + CH) + 11 + 90 + G), C['slate'] + (255,))
label_bar(IS, G, G, IW - 2 * G, 'ITEM ICONS 16X16: BEFORE | AFTER', 'ON 20PX SLOTS')
y = G + 13
for ttl, ids in ROWS:
    label_bar(IS, G, y, IW - 2 * G, ttl, bg='outline'); y += 11
    for k, i in enumerate(ids):
        x = G + k * CW; IS.alpha_composite(slot(ic_before(i)), (x + 4, y)); IS.alpha_composite(slot(L(f'ui/items/{i}.png')), (x + 28, y))
        nm = ITEMS_REPO.get(i, {}).get('name', i).upper()[:13]; text(IS, x + 27 - text_w(nm) // 2, y + 24, nm, C['cream'])
    y += CH
label_bar(IS, G, y, IW - 2 * G, 'PAPERDOLL WEAPON OVERLAYS 48X78 (CROPPED): BEFORE | AFTER (FIST ON GRIP, THICKER)', bg='outline'); y += 11
GF = ['oath_blade', 'chapel_mace', 'pocket_knife', 'night_shard', 'reed_staff', 'sap_crook', 'thorn_bow']
x = G
for gid in GF:
    a_ = Image.open(PRE + f'paperdoll/gear/{gid}.png').convert('RGBA'); b_ = L(f'paperdoll/gear/{gid}.png')
    bb = np.argwhere((np.array(a_)[..., 3] > 0) | (np.array(b_)[..., 3] > 0)); y0_, x0_ = bb.min(0) - 1; y1_, x1_ = bb.max(0) + 2
    for j, im in enumerate((a_, b_)):
        cr = im.crop((x0_, y0_, x1_, y1_)); IS.paste(C['gray'] + (255,), (x + j * (cr.width + 2), y, x + j * (cr.width + 2) + cr.width, y + cr.height)); IS.alpha_composite(cr, (x + j * (cr.width + 2), y))
    nm = ITEMS_REPO[gid]['name'].upper().split()[0]; text(IS, x, y + 82, nm, C['cream']); x += max(2 * (x1_ - x0_) + 8, text_w(nm) + 6)
emit(IS, 'approval/refine/icons_before_after', 4, 'item icons before/after on 20px slots: fixed weapons/bows, Pocket Knife vs Night Shard, unchanged existing cross-section, 5 new quest drops and 6 new shop icons (before = repo parchment placeholder, quantised), plus the paperdoll weapon overlays before|after (fist on the grip, thicker blades).')

# ======================= refine-2 FINAL deliverables: approval/refine/final/ =======================
FD = 'approval/refine/final/'
def emitf(S, name, k, note):
    save(S, FD + name + '.png'); save(upsc(S, k), FD + name + f'_{k}x.png')
    META[FD + name + '.png'] = dict(status='review', refine='refine-2', notes='APPROVAL RENDER (not runtime), review at 1x: ' + note)
    META[FD + name + f'_{k}x.png'] = dict(status='review', refine='refine-2', notes=f'{k}x nearest of {FD}{name}.png.')
# (1) combat render: Gravel Keep, full party of 5 in late gear (ranger with Howl Fang -> no-quiver layer), full combat UI
FPARTY = ['paladin', 'ranger', 'barbarian', 'cleric', 'wizard']
cb = _scene_at(OUT, 'late', SCENE_PARTY=FPARTY, SCENE_BG='combat/bg_gravel_keep_portrait.png',
    SCENE_PMON=[('pebble_squire', 52, 262), ('golem', 135, 222), ('hollow_helm', 220, 266)],
    SCENE_INIT=[('p', 0), ('m', 'pebble_squire'), ('p', 4), ('p', 3), ('m', 'golem'), ('p', 2), ('m', 'hollow_helm'), ('p', 1)],
    SCENE_PCT={'pebble_squire': 1.0, 'golem': 0.6, 'hollow_helm': 0.85})
emitf(cb, 'combat_gravel_keep', 4, 'Gravel Keep combat: refined backdrop, pebble_squire / golem / hollow_helm, GM + dice + table, party ' + ', '.join(f'{c} ({", ".join(REF["late"][c])})' for c in FPARTY)
      + '; seats built with steps_with_gear + the quiver rule (ranger holds Howl Fang, a dagger -> class_back_ranger_noweapon_noquiver). Full combat UI (initiative, enemy bars, seat bars, skill bar).')
# (2) town render: Ashgate + Pebblegate hub (new backdrops, ui/hub)
for pid in ('ashgate', 'pebblegate'):
    emitf(hub(PLACES[pid], True), f'town_{pid}', 4, f'{PLACES[pid]["name"]} town hub mock (session_screen.show_hub layout): NEW backdrop, GM/table/dice, kit seats, ui/hub header plates, 5 hub buttons (Fight disabled).')
# (3) final contact sheet
def sec(S, y, title, sub=None):
    label_bar(S, G, y, S.width - 2 * G, title, sub, bg='outline'); return y + 12
def grid_items(S, y, ims, labels=None, gap=4, maxw=None):
    maxw = maxw or S.width - 2 * G; x = G; rowh = 0
    for k, im in enumerate(ims):
        lab = labels[k] if labels else None; w = max(im.width, text_w(lab) if lab else 0)
        if x + w > G + maxw: x = G; y += rowh + gap; rowh = 0
        S.alpha_composite(im, (x, y))
        if lab: text(S, x, y + im.height + 2, lab, C['cream'])
        rowh = max(rowh, im.height + (9 if lab else 0)); x += w + gap
    return y + rowh + gap + 2
FW = 6 * (270 + G) + G
blocks = []
def block(h): return Image.new('RGBA', (FW, h), C['slate'] + (255,))
# seats
CL = ['paladin', 'wizard', 'ranger', 'bard', 'cleric', 'rogue', 'barbarian', 'druid']
S1 = block(2000); y = G; label_bar(S1, G, y, FW - 2 * G, 'PALADINS OF PEN AND PAPER: REFINE-2 FINAL CONTACT SHEET (STATUS REVIEW)', '1X, ' + datetime.date.today().isoformat()); y += 14
y = sec(S1, y, 'PARTY SEATS: IDLE / ACTIVE (DEFAULT LOOKS, REFINED BACK LAYERS)')
y = grid_items(S1, y, [L(f'party/seat_{c}_{st}.png') for c in CL for st in ('idle', 'active')], [f'{c[:5].upper()} {st[0].upper()}' for c in CL for st in ('idle', 'active')])
nw = [(c, v) for c in CL for v in ('_noweapon', '_noweapon_noquiver') if os.path.exists(OUT + f'party/seat_{c}_idle{v}.png')]
y = sec(S1, y, 'NOWEAPON SEATS (MAIN-HAND WEAPON EQUIPPED) + RANGER NOQUIVER (NON-BOW MAIN HAND)', 'NQ = NO QUIVER')
y = grid_items(S1, y, [L(f'party/seat_{c}_{st}{v}.png') for c, v in nw for st in ('idle', 'active')], [f'{c[:5].upper()} {st[0].upper()}{" NQ" if "quiver" in v else ""}' for c, v in nw for st in ('idle', 'active')])
y = sec(S1, y, 'GEARED SEATS: CLASS KIT (DATA/CLASSES.JSON) AND LATE GEAR (GRAVEL KEEP RENDER)')
y = grid_items(S1, y, [L(f'approval/refine/parts/after/seat_{c}_idle.png') for c in CL] + [L(f'approval/refine/parts/late/seat_{c}_idle.png') for c in CL],
               [f'{c[:5].upper()} KIT' for c in CL] + [f'{c[:5].upper()} LATE' for c in CL])
GEAR = sorted(f[:-4] for f in os.listdir(OUT + 'paperdoll/gear'))
def gcrop(g):
    im = L(f'paperdoll/gear/{g}.png'); bb = im.getbbox(); cr = im.crop((max(0, bb[0] - 1), max(0, bb[1] - 1), min(48, bb[2] + 1), min(78, bb[3] + 1)))
    bg = Image.new('RGBA', cr.size, C['gray'] + (255,)); bg.alpha_composite(cr); return bg
held = set(REF['fist']['held'])
y = sec(S1, y, 'SEAT GEAR OVERLAYS 48X78 (CROPPED), ALL 26', 'F = HELD, FIST ON GRIP')
y = grid_items(S1, y, [gcrop(g) for g in GEAR], [(g[:8] + (' F' if g in held else '')).upper() for g in GEAR], gap=6)
blocks.append(S1.crop((0, 0, FW, y)))
# monsters
S2 = block(1200); y = G
y = sec(S2, y, 'MONSTERS: ALL 18 (IDLE FRAME 0, 80X70) + PORTRAITS 20X20', 'FRAMES/ANCHORS UNCHANGED')
MS = sorted(os.listdir(OUT + 'monsters'))
y = grid_items(S2, y, [frame_of(f'monsters/{m}/{m}_idle.png', 0, 80) for m in MS], [m.upper()[:13] for m in MS], gap=2)
y = grid_items(S2, y, [L(f'monsters/{m}/{m}_portrait.png') for m in MS], None, gap=6)
y = sec(S2, y, 'MONSTER STRIPS: GOLEM (IDLE / ATTACK / HIT / DEATH)')
for an in ('idle', 'attack', 'hit', 'death'):
    im = L(f'monsters/golem/golem_{an}.png'); S2.alpha_composite(im, (G, y)); y += im.height + 2
blocks.append(S2.crop((0, 0, FW, y + 4)))
# backdrops + towns
S3 = block(2 * (480 + 26) + 20); y = G
y = sec(S3, y, 'BACKDROPS 270X480 (ALL REFINED)')
BDS = ['millpond', 'briar_cross', 'lantern_reach', 'howling_cleft', 'gravel_keep', 'forest']
for k, b in enumerate(BDS):
    S3.alpha_composite(L(f'combat/bg_{b}_portrait.png'), (G + k * (270 + G), y)); text(S3, G + k * (270 + G), y + 482, b.upper().replace('_', ' '), C['cream'])
y += 492; y = sec(S3, y, 'TOWNS 270X480: CANDLEWICK (EDGE DRESSING), BRINEWICK, ASHGATE (NEW), PEBBLEGATE (NEW)')
for k, b in enumerate(['candlewick', 'brinewick', 'ashgate', 'pebblegate']):
    S3.alpha_composite(L(f'combat/bg_{b}_portrait.png'), (G + k * (270 + G), y)); text(S3, G + k * (270 + G), y + 482, b.upper(), C['cream'])
# pins in the free space right of the towns
px0 = G + 4 * (270 + G); text(S3, px0, y, 'MAP PINS 32X32 (ANCHOR 16,28)', C['gold'])
PINS = sorted(f[4:-4] for f in os.listdir(OUT + 'map') if f.startswith('loc_'))
for k, pn in enumerate(PINS):
    bx, by = px0 + (k % 3) * 60, y + 12 + (k // 3) * 56
    S3.paste(C['leaf'] + (255,), (bx, by, bx + 40, by + 40)); S3.alpha_composite(L(f'map/loc_{pn}.png'), (bx + 4, by + 4))
    text(S3, bx, by + 42, pn.upper()[:10], C['cream'] if pn not in ('brinewick', 'ashgate', 'pebblegate') else C['gold'])
text(S3, px0, y + 12 + 3 * 56 + 2, 'GOLD LABEL = NEW', C['gold'])
blocks.append(S3.crop((0, 0, FW, y + 492)))
# icons by type
S4 = block(900); y = G
ITL = json.load(open('/workspace/paladins-repo-ro/data/items.json'))
y = sec(S4, y, f'ITEM ICONS 16X16 ON 20PX SLOTS, GROUPED BY TYPE: {len(ITL)} ITEMS IN DATA/ITEMS.JSON @ 3103E38, {REF["icon_check"]["with_icon"]} WITH ICONS', 'NO PLACEHOLDERS LEFT')
for kind in ('weapon', 'off', 'armor', 'trinket', 'usable', 'quest'):
    ids = [it['id'] for it in ITL if it['slot'] == kind]
    text(S4, G, y, f'{kind.upper()} ({len(ids)})', C['gold']); y += 8
    y = grid_items(S4, y, [slot(L(f'ui/items/{i}.png')) for i in ids], [i.upper()[:8] for i in ids], gap=8, maxw=FW - 2 * G)
blocks.append(S4.crop((0, 0, FW, y)))
# UI + GM + dice
S5 = block(400); y = G
y = sec(S5, y, 'UI, GM, TABLE, DICE')
uis = [nine('ui/panel_parchment.png', 80, 40, 6), nine('ui/panel_dark.png', 80, 40, 6), nine('ui/hub/header_plate.png', 120, 18, 4), nine('ui/hub/hub_button.png', 52, 44, 6), nine('ui/hub/hub_button_down.png', 52, 44, 6)]
uis += [L(f'ui/hub/icon_{k}.png') for k in ('travel', 'fight', 'rest', 'quest', 'gear')]
uis += [L('ui/portrait/seat_bars_frame.png'), L('ui/portrait/seat_bars_frame_active.png'), L('ui/portrait/seat_bar_hp.png'), L('ui/portrait/seat_bar_mp.png'), L('ui/enemy_bar_hp.png')]
y = grid_items(S5, y, uis, ['PARCHMENT', 'DARK', 'HEADER', 'HUB BTN', 'BTN DOWN', 'TRAVEL', 'FIGHT', 'REST', 'QUEST', 'GEAR', 'SEAT BARS', 'ACTIVE', 'HP', 'MP', 'ENEMY HP'], gap=8)
y = grid_items(S5, y, [L('combat/gm_idle.png'), L('combat/gm_talk.png'), L('combat/gm_strip.png'), L('combat/gm_screen.png'), L('combat/table_portrait.png')], ['GM IDLE', 'GM TALK', 'GM STRIP', 'SCREEN', 'TABLE'], gap=8)
y = grid_items(S5, y, [L('combat/d6_all.png'), L('combat/d20_roll.png'), L('combat/d20_nat20.png'), L('combat/d20_results.png')], ['D6 ALL', 'D20 ROLL', 'NAT 20', 'D20 RESULTS 1-20'], gap=8)
blocks.append(S5.crop((0, 0, FW, y)))
FS = Image.new('RGBA', (FW, sum(b.height for b in blocks)), C['slate'] + (255,)); yy = 0
for b in blocks: FS.alpha_composite(b, (0, yy)); yy += b.height
save(FS, FD + 'final_contact_sheet.png'); save(upsc(FS, 2), FD + 'final_contact_sheet_2x.png')
META[FD + 'final_contact_sheet.png'] = dict(status='review', refine='refine-2', notes='APPROVAL SHEET (not runtime), review at 1x: every seat (idle/active/noweapon/noquiver, kit + late gear), all 26 gear overlays, all 18 monsters + portraits, all 10 backdrops/towns, all 9 map pins, all 101 item icons by type, UI/GM/table/dice.')
META[FD + 'final_contact_sheet_2x.png'] = dict(status='review', refine='refine-2', notes='2x nearest of final_contact_sheet.png.')
