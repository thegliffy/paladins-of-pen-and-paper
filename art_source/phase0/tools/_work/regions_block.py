# ---------- DRAFT regions: approval sheets + example composite ----------
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
META['approval/backdrops_1x.png'] = dict(status='draft_pending_approval', notes='APPROVAL SHEET (not runtime): the 6 Greenmere location backdrops at 1x, labelled name / region / level.')
META['approval/backdrops_2x.png'] = dict(status='draft_pending_approval', notes='2x nearest of approval/backdrops_1x.png.')
# B) monster lineup grouped by region, each card on a crop of that region's backdrop stand zone
REG_BG = dict(meadow='millpond', coast='lantern_reach', cave='howling_cleft', keep='gravel_keep')
EXM = RGJ['existing']; DRM = RGJ['draft_monsters']
CWd, CHt = 88, 96; rows = []
for kind in ('meadow', 'coast', 'cave', 'keep'):
    r_ = RGJ['regions'][kind]; rows.append((kind, r_))
maxn = max(len(r_['existing']) + len(r_['new']) for _, r_ in rows)
LW = 8 + maxn * (CWd + 4) + 4; LH = 8 + len(rows) * (CHt + 20) + 16
LU = Image.new('RGBA', (LW, LH), C['slate'] + (255,))
text(LU, 8, 4, 'GREENMERE MONSTERS BY REGION  -  NEW = DRAFT, PENDING APPROVAL  -  LARGE = WIDER TABLE SLOT (COST 5)', C['cream'])
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
META['approval/monster_lineup.png'] = dict(status='draft_pending_approval', notes='APPROVAL SHEET (not runtime): monsters grouped by region (existing first, NEW drafts tagged gold), each on a crop of its region backdrop stand zone; existing ones show the pack sprite that data/monsters.json maps them to.')
META['approval/monster_lineup_2x.png'] = dict(status='draft_pending_approval', notes='2x nearest of approval/monster_lineup.png.')
# C) example composite: Lantern Reach with coast monsters (incl. the new large Kelpback), full party/table/bar UI
_src = open(os.path.abspath(__file__)).read()
_scene = _src.split('# ---------- scene_test_portrait ----------\n', 1)[1].split("\nsave(P, 'scene_test_portrait.png')", 1)[0]
_ns = dict(globals()); _ns.update(SCENE_BG='combat/bg_lantern_reach_portrait.png',
    SCENE_PMON=[('bottlecrab', 52, 262), ('kelpback', 135, 222), ('squallgull', 220, 266)],
    SCENE_INIT=[('p', 0), ('m', 'bottlecrab'), ('p', 4), ('p', 3), ('m', 'kelpback'), ('p', 2), ('m', 'squallgull'), ('p', 1)],
    SCENE_PCT={'bottlecrab': 1.0, 'kelpback': 0.6, 'squallgull': 0.85})
exec(compile(_scene, 'scene_block', 'exec'), _ns)
save(_ns['P'], 'scene_test_portrait_lantern_reach.png'); save(upsc(_ns['P'], 4), 'scene_test_portrait_lantern_reach_4x.png')
META['scene_test_portrait_lantern_reach.png'] = dict(status='draft_pending_approval', notes='QA composite (not runtime): DRAFT Lantern Reach backdrop + coast monsters Bottlecrab / Kelpback Snapper (LARGE) / Squallgull at the standard monster marks, with the v7 party, table, seat bars + HP numbers and v6 action bar.')
META['scene_test_portrait_lantern_reach_4x.png'] = dict(status='draft_pending_approval', notes='4x nearest.')
# D) per-region monsters on their own backdrops (extra check)
for kind, lid, trio in (('meadow', 'briar_cross', ['bramblet', 'briar_hound', 'grinmud_toad']), ('cave', 'howling_cleft', ['gloomgrub', 'marshlurker', 'dripfang']), ('keep', 'gravel_keep', ['pebble_squire', 'gravel_brute', 'hollow_helm'])):
    _ns = dict(globals()); spr3 = [m if m in DRM else EXM[m][2] for m in trio]
    _ns.update(SCENE_BG=f'combat/bg_{lid}_portrait.png', SCENE_PMON=[(spr3[0], 52, 262), (spr3[1], 135, 222), (spr3[2], 220, 266)],
        SCENE_INIT=[('p', 0), ('m', spr3[0]), ('p', 4), ('p', 3), ('m', spr3[1]), ('p', 2), ('m', spr3[2]), ('p', 1)], SCENE_PCT={spr3[0]: 1.0, spr3[1]: 0.6, spr3[2]: 0.85})
    exec(compile(_scene, 'scene_block', 'exec'), _ns)
    save(_ns['P'], f'approval/scene_{lid}.png')
    META[f'approval/scene_{lid}.png'] = dict(status='draft_pending_approval', notes=f'QA composite (not runtime): {lid} backdrop with {", ".join(trio)} and the full portrait UI.')
