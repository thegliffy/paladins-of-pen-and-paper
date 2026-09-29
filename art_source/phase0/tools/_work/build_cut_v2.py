"""Cuts sheet-derived assets: bg, table, GM, screen, d20, seats, monsters, map icons, pawn, UI icons."""
import json
from cutlib import *
from pal import save, new, C, outline_img, OUT
META = {}
def rowsplit(comps, ys):
    rows = [[] for _ in range(len(ys)+1)]
    for c in comps:
        rows[sum(c[1] >= y for y in ys)].append(c)
    return [sorted(r, key=lambda c: c[0]) for r in rows]
def place(im, W, H, bottom=None, cx=None):
    c = new(W, H); bottom = H - 1 if bottom is None else bottom; cx = W // 2 if cx is None else cx
    c.paste(im, (cx - im.width // 2, bottom + 1 - im.height), im); return c
def strip(frames):
    W, H = frames[0].size; s = new(W * len(frames), H)
    for i, f in enumerate(frames): s.paste(f, (i * W, 0), f)
    return s
def arr(im): return np.array(im)
def img(a): return Image.fromarray(a, 'RGBA')

# ---------------- background ----------------
a = load('forest')
bg_allowed = [i for i in pal.NOPINK if pal.NAMES[i] != 'cyan']
top = np.array(cut_full(a[150:720], (480, 214), bg_allowed))
pad = top[214 - 56:214][::-1]          # mirrored meadow band fills the bottom (sits behind table/UI)
save(Image.fromarray(np.concatenate([top, pad]), 'RGBA'), 'combat/bg_forest.png')
META['combat/bg_forest.png'] = dict(anchor=[0, 0], notes='480x270 full-screen backdrop; sky/treeline top, meadow starts ~y108; place monster feet on y~115-135 (upper half). Rows 214-269 are a mirrored meadow band (normally hidden by table/UI).')

# ---------------- portrait backdrop 270x480 ----------------
ptop = np.array(cut_full(a[60:720, 280:1000], (270, 247), bg_allowed))
band = ptop[150:247]; fill = []; flip = True
while sum(len(b) for b in fill) < 480 - 247:
    fill.append(band[::-1] if flip else band); flip = not flip
pbg = np.concatenate([ptop] + fill)[:480]
save(Image.fromarray(pbg, 'RGBA'), 'combat/bg_forest_portrait.png')
META['combat/bg_forest_portrait.png'] = dict(anchor=[0, 0], meadow_start_y=141, monster_feet_band=[150, 200],
    notes='PORTRAIT 270x480 backdrop recomposed from the same forest source: sky 0-~40, tree line to y~141, meadow below. Rows 247-479 are alternating mirrored meadow bands (behind table/party/UI).')
META['combat/bg_forest.png']['legacy'] = True
META['combat/bg_forest.png']['notes'] = 'LEGACY (landscape). ' + META['combat/bg_forest.png']['notes']

# ---------------- table sheet ----------------
a = load('table'); fg, _ = fg_mask(a); r = rowsplit(components(fg), [270, 465])
# table.png is now drawn procedurally in build_proc.py (fix pass v2)
gm = cut(a, fg, r[1][0], 6.5)                 # 37x44
GW, GH = 44, 46
idle = place(gm, GW, GH)
ga = arr(gm).copy()
# talk frame: open mouth (3x2 dark + tongue) and 1px head bob (rows 0..22 up by 1)
O = C['outline'] + (255,); R = C['red_dk'] + (255,)
ga[18, 17:20] = O; ga[19, 17] = O; ga[19, 18] = R; ga[19, 19] = O; ga[20, 18] = O
tk = np.zeros((GH, GW, 4), np.uint8)
ox, oy = GW // 2 - gm.width // 2, GH - gm.height
tk[oy:oy + gm.height, ox:ox + gm.width] = ga
head = tk[oy:oy + 23].copy(); tk[oy - 1:oy + 22] = head
talk = img(tk)
save(idle, 'combat/gm_idle.png'); save(talk, 'combat/gm_talk.png'); save(strip([idle, talk]), 'combat/gm_strip.png')
for k in ('combat/gm_idle.png', 'combat/gm_talk.png'):
    META[k] = dict(anchor=[22, 45], notes='bottom-centre anchor; place so the table overlaps his hands (bottom ~8px).')
META['combat/gm_strip.png'] = dict(frames=2, frame_size=[GW, GH], fps=6, anchor=[22, 45], notes='frame0 idle, frame1 talk (mouth open + 1px head bob); alternate while GM speaks.')
screen = cut(a, fg, r[1][1], 8.0)
save(screen, 'combat/gm_screen.png'); META['combat/gm_screen.png'] = dict(anchor=[screen.width // 2, screen.height - 1], notes='bottom-centre anchor; stands on the table top in front of the GM.')
# d20 is now drawn procedurally in build_proc.py (fix pass v2)

# ---------------- seats ----------------
a = load('seats'); fg, _ = fg_mask(a); comps = sorted(components(fg), key=lambda c: c[0])
SW, SH = 48, 78     # v2: 1.5x seats (re-cut from the source at 1:1 native pixels, not upscaled)
for n, c in zip(['paladin', 'wizard', 'ranger', 'bard'], comps):
    s = cut(a, fg, c, 8.5 / 1.5)
    save(place(s, SW, SH), f'party/seat_{n}_idle.png')
    act = place(s, SW, SH, bottom=SH - 1 - 3)
    act = outline_img(act, C['gold'])
    save(act, f'party/seat_{n}_active.png')
    META[f'party/seat_{n}_idle.png'] = dict(anchor=[24, 77], notes='48x78, bottom-centre anchor (chair feet). Matches paperdoll/back/* canvas.')
    META[f'party/seat_{n}_active.png'] = dict(anchor=[24, 77], notes='same anchor as idle; sprite raised 3px with 1px gold (#f8d040) outline.')

# ---------------- map icons + pawn ----------------
a = load('map'); fg, _ = fg_mask(a); r = rowsplit(components(fg), [260, 450])
for n, c in zip(['tavern', 'village', 'cave', 'castle', 'windmill', 'shrine'], r[0]):
    save(place(cut(a, fg, c, 6.6), 32, 32, bottom=31), f'map/loc_{n}.png')
    META[f'map/loc_{n}.png'] = dict(anchor=[16, 28], notes='32x32; anchor = node centre on the round ground base.')
pw = [place(cut(a, fg, c, 8.4), 24, 20) for c in r[2][:4]]
save(strip(pw), 'map/pawn_walk.png')
META['map/pawn_walk.png'] = dict(frames=4, frame_size=[24, 20], fps=8, anchor=[12, 19], notes='faces right; flip_h for left. Bottom-centre (hooves).')

# ---------------- UI icons (from sheet, placed on procedural frames later) ----------------
a = load('ui'); fg, _ = fg_mask(a); r = rowsplit(components(fg), [175, 340])
icons = {}
for n, c in zip(['attack', 'skill', 'item', 'cover', 'run'], r[0]):
    x0, y0, x1, y1 = c[:4]; cx, cy = (x0 + x1) // 2, (y0 + y1) // 2; side = min(x1 - x0, y1 - y0) - 46
    bb = (cx - side // 2, cy - side // 2, cx + side // 2, cy + side // 2)
    panel = a[y0 + 30, x0 + 30]
    d = np.sqrt(((a - panel) ** 2).sum(-1))
    f2 = np.zeros_like(fg); f2[bb[1]:bb[3], bb[0]:bb[2]] = d[bb[1]:bb[3], bb[0]:bb[2]] > 26
    lab_, nl = ndi.label(f2); sizes = ndi.sum(f2, lab_, range(1, nl + 1))
    f2 = np.isin(lab_, [i + 1 for i, sz in enumerate(sizes) if sz > 150])
    f2 = ndi.binary_fill_holes(ndi.binary_closing(f2, iterations=2))
    ic = cut(a, f2, bb, 0, size=(20, 20))
    icons[n] = ic; ic.save(f'/workspace/paladins-art/phase0/tools/_work/icon_{n}.png')

# ---------------- monsters ----------------
a = load('monsters'); fg, _ = fg_mask(a); comps = components(fg)
r1 = sorted([c for c in comps if c[1] < 340], key=lambda c: c[0]); r2 = sorted([c for c in comps if c[1] >= 340], key=lambda c: c[0])
FW, FH, BASE = 80, 70, 64
FLY = {'bat', 'imp'}
SCALE = {'golem': 4.5, 'bat': 5.5}
DFRAC = {'bat': 0.45}
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
def shear(s, amt):   # lean: shift top rows by up to amt px (positive = right)
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
names = ['goblin', 'bat', 'slime', 'skeleton', 'wolf', 'mushroom', 'golem', 'imp']
MON = {}
PR = dict(goblin=[26, 16, 20, 20], bat=[30, 28, 20, 20], slime=[30, 38, 20, 20], skeleton=[33, 13, 20, 20], wolf=[12, 17, 20, 20], mushroom=[30, 33, 20, 20], golem=[22, 4, 20, 20], imp=[19, 17, 20, 20])
for n, c in zip(names, r1 + r2):
    base = arr(cut(a, fg, c, SCALE.get(n, 5.0), dark_frac=DFRAC.get(n, 0.28)))
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
    for key, frs, fps in (('idle', idle, 2), ('attack', attack, 5), ('hit', hit, 8), ('death', death, 8)):
        save(strip([img(f) for f in frs]), f'monsters/{n}/{n}_{key}.png')
        META[f'monsters/{n}/{n}_{key}.png'] = dict(frames=len(frs), frame_size=[FW, FH], fps=fps, anchor=[FW // 2, BASE],
            hp_bar_anchor=[FW // 2, BASE + 1 - h - 4], portrait_rect=PR[n], loop=key == 'idle')
    MON[n] = dict(sprite_size=[w, h], top=BASE + 1 - h, portrait_rect=PR[n])
    fr0 = img(frame(base)); x_, y_ = PR[n][:2]
    save(fr0.crop((x_, y_, x_ + 20, y_ + 20)), f'monsters/{n}/{n}_portrait.png')
    META[f'monsters/{n}/{n}_portrait.png'] = dict(notes=f'20x20 head crop (rect {PR[n]} of the rest frame) for the initiative strip.')
    save(img(frame(base)), f'monsters/{n}/{n}_still.png')
    META[f'monsters/{n}/{n}_still.png'] = dict(anchor=[FW // 2, BASE], hp_bar_anchor=[FW // 2, BASE + 1 - h - 4], notes='single rest frame (portraits / initiative).')
json.dump(dict(meta=META, monsters=MON), open('/workspace/paladins-art/phase0/tools/_work/meta_cut.json', 'w'), indent=1)
print('ok', len(META))
