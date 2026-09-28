"""APPROVED 2026-09-28 (Kyle via Chief of Staff; pushed art/phase0-pack @122a66a): Greenmere location backdrops + region monsters. Writes art + tools/_work/meta_regions.json."""
import json, numpy as np
from PIL import Image
import pal
from pal import C, save
from draft_backdrops import LOCS
from draft_monsters import DRAFT
OUT = pal.OUT
META = {}
STATUS = 'approved'
APPROVED = 'approved 2026-09-28 by Kyle (via Chief of Staff); pushed to art/phase0-pack @ 122a66a'

# ---------------- backdrops ----------------
for lid, (fn, name, kind) in LOCS.items():
    rel = f'combat/bg_{lid}_portrait.png'
    save(fn().image(), rel)
    META[rel] = dict(anchor=[0, 0], status=STATUS, location=lid, location_name=name, region=kind, horizon_y=141, monster_feet_band=[222, 266],
        approval=APPROVED, notes=f'{name} ({kind}) combat backdrop, 270x480, same framing as bg_forest_portrait: sky/landmarks above the horizon (y141), '
              'monster stand zone y~180-270 kept low-contrast, calmer texture below y~300 (table y343-382, seats and bars below). '
              'Procedural, flat shading, pack palette, alpha 255.' + (' Candlewick has no monsters in data/region.json (town / inn); backdrop provided for completeness.' if lid == 'candlewick' else ''))

# ---------------- monsters (same strip logic as build_cut) ----------------
FW, FH, BASE = 80, 70, 64
FLY = {'squallgull', 'hollow_helm'}
HEAD = dict(bramblet=(36, 40), grinmud_toad=(36, 38), bottlecrab=(36, 42), squallgull=(37, 33), kelpback=(11, 38), gloomgrub=(14, 44),
            dripfang=(37, 32), pebble_squire=(36, 24), hollow_helm=(36, 25), cobble_rat=(16, 48))
WHITE = C['white'] + (255,)
def frame(spr, dx=0, dy=0, clip_base=False):
    c = np.zeros((FH, FW, 4), np.uint8)
    h, w = spr.shape[:2]; x = FW // 2 - w // 2 + dx; y = BASE + 1 - h + dy
    for yy in range(h):
        Y = y + yy
        if 0 <= Y < FH and (not clip_base or Y <= BASE):
            row = spr[yy]; m = row[:, 3] > 0
            xs = np.arange(w) + x; ok = m & (xs >= 0) & (xs < FW)
            c[Y, xs[ok]] = row[ok]
    return c
def flash(s):
    s = s.copy(); s[s[..., 3] > 0] = WHITE; return s
def shear(s, amt):
    h, w = s.shape[:2]; o = np.zeros((h, w + abs(amt), 4), np.uint8)
    for y in range(h):
        k = int(round(amt * max(0, (h * 0.6 - y)) / (h * 0.6)))
        off = (k if amt > 0 else abs(amt) + k)
        o[y, off:off + w] = s[y]
    return o
def dissolve(fr, level):
    ys, xs = np.mgrid[0:FH, 0:FW]
    kill = {1: (xs % 2 == 0) & (ys % 2 == 0), 2: (xs + ys) % 2 == 0, 3: ~((xs % 2 == 1) & (ys % 2 == 1))}[level]
    fr = fr.copy(); fr[kill] = 0; return fr
def img(a): return Image.fromarray(a, 'RGBA')
def strip(frames):
    o = Image.new('RGBA', (FW * len(frames), FH))
    for i, f in enumerate(frames): o.paste(f, (i * FW, 0))
    return o
MON = {}
for n, (fn, region, size, name, concept) in DRAFT.items():
    sp = fn(); base = sp.image(); bx, by = sp.bbox
    h, w = base.shape[:2]
    if n in FLY: idle2 = frame(base, 0, -1)
    else:
        k = int(h * 0.4); sq = np.concatenate([base[:k], base[k + 1:]]); idle2 = frame(sq)
    idle = [frame(base), idle2]
    attack = [frame(shear(base, 1), 0, -2), frame(base, 0, 4), frame(base, 0, 1)]
    hit = [frame(flash(base)), frame(base, 0, -2)]
    death = [frame(flash(base))]
    for lvl, sink in ((1, 0.15), (2, 0.35), (3, 0.55)):
        death.append(dissolve(frame(base, 0, int(h * sink), clip_base=True), lvl))
    fx0, fy0 = FW // 2 - w // 2, BASE + 1 - h
    hx, hy = HEAD[n]; px_ = int(np.clip(fx0 + hx - bx - 10, 0, FW - 20)); py_ = int(np.clip(fy0 + hy - by - 10, 0, FH - 20))
    PR = [px_, py_, 20, 20]; hp_anchor = [FW // 2, max(1, BASE + 1 - h - 4)]
    for key, frs, fps in (('idle', idle, 2), ('attack', attack, 5), ('hit', hit, 8), ('death', death, 8)):
        save(strip([img(f) for f in frs]), f'monsters/{n}/{n}_{key}.png')
        META[f'monsters/{n}/{n}_{key}.png'] = dict(frames=len(frs), frame_size=[FW, FH], fps=fps, anchor=[FW // 2, BASE],
            hp_bar_anchor=hp_anchor, portrait_rect=PR, loop=key == 'idle', status=STATUS, region=region, monster_size=size)
    fr0 = img(frame(base))
    save(fr0.crop((px_, py_, px_ + 20, py_ + 20)), f'monsters/{n}/{n}_portrait.png')
    META[f'monsters/{n}/{n}_portrait.png'] = dict(notes=f'20x20 head crop (rect {PR} of the rest frame) for the initiative strip.', status=STATUS)
    save(fr0, f'monsters/{n}/{n}_still.png')
    META[f'monsters/{n}/{n}_still.png'] = dict(anchor=[FW // 2, BASE], hp_bar_anchor=hp_anchor, notes='single rest frame (portraits / initiative).', status=STATUS)
    MON[n] = dict(name=name, region=region, size=size, concept=concept, sprite_size=[w, h], top=BASE + 1 - h, portrait_rect=PR, hp_bar_anchor=hp_anchor, flying=n in FLY, status=STATUS, approval=APPROVED)

# ---------------- region table (from data/region.json + data/monsters.json on cursor/phase-0-playable-slice-9a5e) ----------------
EXISTING = {  # id: (name, size, pack sprite used by data/monsters.json)
    'puddleblob': ('Puddleblob', 'regular', 'slime'), 'thicket_imp': ('Thicket Imp', 'regular', 'imp'), 'cinder_mite': ('Cinder Mite', 'regular', 'goblin'),
    'briar_hound': ('Briar Hound', 'large', 'wolf'), 'lantern_wisp': ('Lantern Wisp', 'regular', 'mushroom'), 'cave_howler': ('Cave Howler', 'regular', 'bat'),
    'marshlurker': ('Marshlurker', 'large', 'skeleton'), 'gravel_brute': ('Gravel Brute', 'large', 'golem')}
PLACES = [  # id, name, kind(region), level, monsters in data/region.json
    ('candlewick', 'Candlewick', 'town', 1, []), ('millpond', 'Millpond', 'meadow', 1, ['puddleblob', 'thicket_imp']),
    ('briar_cross', 'Briar Cross', 'meadow', 2, ['cinder_mite', 'briar_hound', 'thicket_imp']),
    ('lantern_reach', 'Lantern Reach', 'coast', 2, ['lantern_wisp', 'cinder_mite', 'briar_hound']),
    ('howling_cleft', 'Howling Cleft', 'cave', 3, ['cave_howler', 'marshlurker', 'briar_hound', 'lantern_wisp']),
    ('gravel_keep', 'Gravel Keep', 'keep', 4, ['gravel_brute', 'cave_howler', 'marshlurker', 'briar_hound'])]
SUGGEST_PLACE = dict(bramblet='briar_cross', grinmud_toad='millpond', bottlecrab='lantern_reach', squallgull='lantern_reach', kelpback='lantern_reach',
                     gloomgrub='howling_cleft', dripfang='howling_cleft', pebble_squire='gravel_keep', hollow_helm='gravel_keep', cobble_rat='gravel_keep')
REG = {}
for pid, pname, kind, lvl, mons in PLACES:
    r_ = REG.setdefault(kind, dict(places=[], existing=[], new=[]))
    r_['places'].append(pid)
    for m in mons:
        if m not in r_['existing']: r_['existing'].append(m)
for n, v in MON.items(): REG[v['region']]['new'].append(n)
for kind, r_ in REG.items():
    size = lambda m: EXISTING[m][1] if m in EXISTING else MON[m]['size']
    allm = r_['existing'] + r_['new']
    r_['regular'] = sum(size(m) == 'regular' for m in allm); r_['large'] = sum(size(m) == 'large' for m in allm)
    r_['meets_4_regular_1_large'] = r_['regular'] >= 4 and r_['large'] >= 1
REGIONS = dict(source='thegliffy/paladins-of-pen-and-paper @ cursor/phase-0-playable-slice-9a5e: data/region.json (places[].kind = region) + data/monsters.json',
    note='The region is the place "kind" (town/meadow/coast/cave/keep); the map itself is one region file (greenmere). Town (Candlewick) has no monsters by design, so it is excluded from the 4-regular/1-large rule.',
    places=[dict(id=pid, name=pn, region=k, level=l, monsters=m, suggested_new=[n for n, pp in SUGGEST_PLACE.items() if pp == pid],
                 backdrop=f'combat/bg_{pid}_portrait.png') for pid, pn, k, l, m in PLACES],
    regions=REG, existing=EXISTING, draft_monsters=MON, status=STATUS, approval=APPROVED,
    existing_names_note='data side is renaming the existing 8 monsters to match their art (ids unchanged here); no redraws needed.')
json.dump(dict(meta=META, regions=REGIONS), open(OUT + 'tools/_work/meta_regions.json', 'w'), indent=1)
for k, v in REG.items(): print(k, v['regular'], v['large'], v['meets_4_regular_1_large'], v['new'])
