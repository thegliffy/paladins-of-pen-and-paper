"""Procedural assets: d6, map tiles, UI chrome, damage digits."""
import json
from proclib import *
from pal import save, C, H, text, OUT
META = {}
W_ = '/workspace/paladins-art/phase0/tools/_work/'
def strip(frames):
    W, Hh = frames[0].shape[1], frames[0].shape[0]; s = layer(W * len(frames), Hh)
    for i, f in enumerate(frames): s[:, i * W:(i + 1) * W] = f
    return s

# ---------------- d6 ----------------
PIPS = {1: [(1, 1)], 2: [(0, 0), (2, 2)], 3: [(0, 0), (1, 1), (2, 2)], 4: [(0, 0), (2, 0), (0, 2), (2, 2)],
        5: [(0, 0), (2, 0), (1, 1), (0, 2), (2, 2)], 6: [(0, 0), (2, 0), (0, 1), (2, 1), (0, 2), (2, 2)]}
D6 = {'white': ('white', 'silver', 'outline'), 'red': ('red', 'red_dk', 'white'), 'blue': ('blue', 'blue_dk', 'white'),
      'green': ('leaf', 'leaf_dk', 'white'), 'yellow': ('gold', 'amber', 'outline'), 'black': ('ink', 'outline', 'white')}
allfaces = layer(48, 48)
for row, (name, (f, s, p)) in enumerate(D6.items()):
    faces = []
    for n in range(1, 7):
        L = layer(8, 8); paint(L, rect(8, 8, 0, 0, 7, 7), C['outline'])
        paint(L, rect(8, 8, 1, 1, 6, 6), C[s]); paint(L, rect(8, 8, 1, 1, 5, 5), C[f])
        for px, py in PIPS[n]: L[1 + py * 2, 1 + px * 2] = C[p] + (255,)
        faces.append(L)
    st = strip(faces); save(img(st), f'combat/d6_{name}.png'); allfaces[row * 8:(row + 1) * 8] = st
    META[f'combat/d6_{name}.png'] = dict(frames=6, frame_size=[8, 8], fps=12, anchor=[4, 7], notes='frame i = face i+1. Cycle randomly while rolling, stop on the result face.')
save(img(allfaces), 'combat/d6_all.png')
META['combat/d6_all.png'] = dict(frame_size=[8, 8], notes='6x6 grid: rows white,red,blue,green,yellow,black; columns faces 1-6.')

# ---------------- map tiles (16x16, seamless) ----------------
T = 16
def grass(seed=1, flowers=False):
    L = layer(T, T); paint(L, rect(T, T, 0, 0, 15, 15), C['grass'])
    for y in range(T):
        for x in range(T):
            h = hsh(x, y, seed)
            if h < 0.07: L[y, x] = C['lime'] + (255,)
            elif h < 0.12: L[y, x] = C['leaf'] + (255,)
    for i in range(3):   # small tufts, kept away from edges -> seamless
        tx, ty = 2 + int(hsh(i, 7, seed) * 11), 3 + int(hsh(i, 9, seed) * 10)
        for dx, dy in ((0, 0), (-1, -1), (1, -1)): L[ty + dy, tx + dx] = C['leaf'] + (255,)
    if flowers:
        cols = ['white', 'gold', 'rose', 'white', 'gold']
        for i in range(5):
            fx, fy = 2 + int(hsh(i, 3, seed + 5) * 12), 2 + int(hsh(i, 4, seed + 5) * 12)
            c = C[cols[i]]
            for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)): L[fy + dy, fx + dx] = c + (255,)
            L[fy, fx] = C['amber'] + (255,) if cols[i] != 'gold' else C['orange'] + (255,)
    return L
def pad_nb(m):   # neighbour test with edge replication (seamless along bands)
    p = np.pad(m, 1, mode='edge')
    return p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
def pad_all(m):
    p = np.pad(m, 1, mode='edge')
    return p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
def road(mask, seed=3):
    L = grass()
    paint(L, mask, C['tan'])
    for y in range(T):
        for x in range(T):
            if mask[y, x]:
                h = hsh(x, y, seed)
                if h < 0.10: L[y, x] = C['wood_lt'] + (255,)
                elif h < 0.16: L[y, x] = C['sand'] + (255,)
    paint(L, mask & ~pad_all(mask), C['wood_lt'])
    paint(L, ~mask & pad_nb(mask), C['leaf_dk'])
    return L
def river(mask, seed=4):
    L = grass()
    paint(L, mask, C['blue'])
    for y in range(T):
        for x in range(T):
            if mask[y, x] and pad_all(mask)[y, x]:
                h = hsh(x // 3, y, seed)
                if h < 0.12: L[y, x] = C['sky'] + (255,)
                elif h > 0.9: L[y, x] = C['blue_dk'] + (255,)
    paint(L, mask & ~pad_all(mask), C['blue_dk'])
    bank = ~mask & pad_nb(mask); paint(L, bank, C['wood'])
    paint(L, ~mask & ~bank & pad_nb(mask | bank), C['leaf_dk'])
    return L
xs, ys = grid(T, T)
band_h = (ys >= 5) & (ys <= 10); band_v = (xs >= 5) & (xs <= 10)
corner = ((xs >= 5) & band_h) | ((ys >= 5) & band_v)
corner &= ~(((xs == 5) & (ys == 5)))
cross = band_h | band_v
tee = band_h | (band_v & (ys >= 5))
rb_h = (ys >= 4) & (ys <= 11); rb_v = (xs >= 4) & (xs <= 11)
rcorner = ((xs >= 4) & rb_h) | ((ys >= 4) & rb_v); rcorner &= ~(((xs == 4) & (ys == 4)) | ((xs == 5) & (ys == 4)) | ((xs == 4) & (ys == 5)))
tiles = {'grass': grass(), 'grass_flowers': grass(flowers=True), 'road_h': road(band_h), 'road_v': road(band_v),
         'road_corner': road(corner), 'road_cross': road(cross), 'road_t': road(tee), 'river_h': river(rb_h), 'river_v': river(rb_v),
         'river_corner': river(rcorner)}
# bridge_h: road runs left-right over a vertical river
B = river(rb_v)
paint(B, band_h, C['wood_lt'])
for x in range(T): 
    if x % 3 == 2: B[5:11, x] = C['wood'] + (255,)
paint(B, (ys == 4) | (ys == 11), C['wood_dk']); paint(B, (ys == 3) | (ys == 12), C['outline'])
for px in (1, 14):
    B[2:4, px] = C['wood'] + (255,); B[12:14, px] = C['wood'] + (255,)
paint(B, band_h & ((xs == 0) | (xs == 15)) & False, C['tan'])
tiles['bridge_h'] = B
tiles['bridge_v'] = np.ascontiguousarray(np.rot90(B, -1))
TN = {'road_t': 'T-junction joining EAST+WEST+SOUTH; flip_v -> E+W+N; see tile_road_t_* for the vertical variants.', 'road_corner': 'connects EAST+SOUTH; flip_h -> W+S, flip_v -> E+N, flip_h+flip_v -> W+N.',
      'river_corner': 'connects EAST+SOUTH; flips give the other 3 rotations.',
      'road_v': 'road_h rotated 90.', 'river_v': 'river_h rotated 90.', 'bridge_v': 'bridge_h rotated 90 (road N-S over an E-W river).',
      'bridge_h': 'road E-W over a N-S river; joins road_h and river_v.'}
for k, L in tiles.items():
    save(img(L), f'map/tile_{k}.png'); META[f'map/tile_{k}.png'] = dict(anchor=[0, 0], notes='16x16 seamless. ' + TN.get(k, ''))
# explicit corner rotations for convenience
for sfx, fl in (('es', lambda a: a), ('ws', lambda a: a[:, ::-1]), ('en', lambda a: a[::-1]), ('wn', lambda a: a[::-1, ::-1])):
    save(img(np.ascontiguousarray(fl(tiles['road_corner']))), f'map/tile_road_corner_{sfx}.png')
    META[f'map/tile_road_corner_{sfx}.png'] = dict(anchor=[0, 0], notes=f'road corner joining {sfx.upper()} (pre-flipped copy).')
for sfx, arr_ in (('ews', tiles['road_t']), ('ewn', tiles['road_t'][::-1]), ('nse', np.rot90(tiles['road_t'], 1)), ('nsw', np.rot90(tiles['road_t'], -1))):
    save(img(np.ascontiguousarray(arr_)), f'map/tile_road_t_{sfx}.png'); META[f'map/tile_road_t_{sfx}.png'] = dict(anchor=[0, 0], notes=f'T-junction joining {sfx.upper()} (pre-rotated copy).')
# preview
lay = ["ggggfggg", "gCRRRRKg", "gVgggfVg", "rXRRbRXr", "gVffwgVg", "gLRRbRJg", "ggggwggg"]
Tm = {'g': 'grass', 'f': 'grass_flowers', 'R': 'road_h', 'V': 'road_v', 'X': 'road_cross', 'w': 'river_v', 'b': 'bridge_h', 'r': 'road_h'}
P = layer(8 * T, 7 * T)
for yy, row in enumerate(lay):
    for xx, ch in enumerate(row):
        if ch in 'CKLJ':
            base = tiles['road_corner']; t = {'C': base, 'K': base[:, ::-1], 'L': base[::-1], 'J': base[::-1, ::-1]}[ch]
        else: t = tiles[Tm[ch]]
        P[yy * T:(yy + 1) * T, xx * T:(xx + 1) * T] = t
save(img(P), 'map/tiles_preview.png'); META['map/tiles_preview.png'] = dict(notes='QA preview showing tiles assembled (not a runtime asset).')

# ---------------- UI chrome ----------------
WOOD = dict(o='outline', hi='wood_lt', mid='wood', lo='wood_dk', stud='tan', studhi='sand', studlo='wood')
GOLD = dict(o='outline', hi='cream', mid='gold', lo='amber', stud='cream', studhi='white', studlo='orange')
def frame(Wd, Ht, st, fill='ink', thick=2, studs=True):
    L = layer(Wd, Ht); full = rect(Wd, Ht, 0, 0, Wd - 1, Ht - 1)
    paint(L, full, C[st['o']])
    inner = rect(Wd, Ht, 1, 1, Wd - 2, Ht - 2); paint(L, inner, C[st['mid']])
    paint(L, e_top(inner) | e_left(inner), C[st['hi']]); paint(L, (e_bot(inner) | e_right(inner)) & ~(e_top(inner) | e_left(inner)), C[st['lo']])
    t = thick + 1
    if thick >= 1: paint(L, rect(Wd, Ht, t, t, Wd - 1 - t, Ht - 1 - t), C[st['o']])
    if fill: paint(L, rect(Wd, Ht, t + 1, t + 1, Wd - 2 - t, Ht - 2 - t), C[fill])
    else: L[t + 1:Ht - 1 - t, t + 1:Wd - 1 - t] = 0
    if studs:
        for cx, cy in ((0, 0), (Wd - 4, 0), (0, Ht - 4), (Wd - 4, Ht - 4)):
            paint(L, rect(Wd, Ht, cx, cy, cx + 3, cy + 3), C[st['o']])
            paint(L, rect(Wd, Ht, cx + 1, cy + 1, cx + 2, cy + 2), C[st['stud']])
            L[cy + 1, cx + 1] = C[st['studhi']] + (255,); L[cy + 2, cx + 2] = C[st['studlo']] + (255,)
    return L
icons = {n: arr(Image.open(W_ + f'icon_{n}.png')) for n in ['attack', 'skill', 'item', 'cover', 'run']}
for n, ic in icons.items():
    for sfx, st in (('', WOOD), ('_active', GOLD)):
        L = frame(28, 28, st, thick=2); over(L[4:24, 4:24], ic)
        save(img(L), f'ui/btn_{n}{sfx}.png')
        META[f'ui/btn_{n}{sfx}.png'] = dict(anchor=[0, 0], notes=('highlighted/selected state (gold frame).' if sfx else 'normal state.') + ' 28x28, icon area rect [4,4,20,20].')
for sfx, st in (('', WOOD), ('_active', GOLD)):
    L = frame(24, 24, st, thick=0, studs=False)
    for cx, cy in ((0, 0), (22, 0), (0, 22), (22, 22)): L[cy:cy + 2, cx:cx + 2] = C[st['stud']] + (255,)
    save(img(L), f'ui/portrait_frame{sfx}.png')
    META[f'ui/portrait_frame{sfx}.png'] = dict(anchor=[0, 0], portrait_rect=[2, 2, 20, 20], notes='24x24 (2px border). Draw the 20x20 portrait crop at [2,2]; ink fill behind.')
# bars
def bar(Wd, Hh, base, hi, lo):
    L = layer(Wd, Hh); paint(L, rect(Wd, Hh, 0, 0, Wd - 1, Hh - 1), C[base])
    paint(L, rect(Wd, Hh, 0, 0, Wd - 1, 0), C[hi]); paint(L, rect(Wd, Hh, 0, Hh - 1, Wd - 1, Hh - 1), C[lo]); return L
BW, BH = 54, 5
save(img(bar(BW, BH, 'red', 'coral', 'red_dk')), 'ui/bar_hp.png')
save(img(bar(BW, BH, 'blue', 'sky', 'blue_dk')), 'ui/bar_mp.png')
BG = layer(BW + 2, BH + 2); paint(BG, rect(BW + 2, BH + 2, 0, 0, BW + 1, BH + 1), C['outline']); paint(BG, rect(BW + 2, BH + 2, 1, 1, BW, BH), C['ink'])
paint(BG, rect(BW + 2, BH + 2, 1, BH, BW, BH), C['slate'])
save(img(BG), 'ui/bar_bg.png')
save(img(bar(12, 5, 'red', 'coral', 'red_dk')), 'ui/bar_hp_tile.png'); save(img(bar(12, 5, 'blue', 'sky', 'blue_dk')), 'ui/bar_mp_tile.png')
META['ui/bar_hp.png'] = dict(notes='TextureProgressBar fill (54x5). Row0 highlight, row4 shadow. Crop/scale width only (nearest).')
META['ui/bar_mp.png'] = dict(notes='MP fill (54x5).')
META['ui/bar_bg.png'] = dict(notes='56x7 under-texture; fill goes at offset [1,1].', fill_rect=[1, 1, 54, 5])
META['ui/bar_hp_tile.png'] = dict(notes='12x5 horizontally tileable fill for arbitrary bar lengths.')
META['ui/bar_mp_tile.png'] = dict(notes='12x5 horizontally tileable fill.')
EB = layer(32, 5); paint(EB, rect(32, 5, 0, 0, 31, 4), C['outline']); paint(EB, rect(32, 5, 1, 1, 30, 3), C['ink'])
save(img(EB), 'ui/enemy_bar_bg.png'); save(img(bar(30, 3, 'red', 'coral', 'red_dk')), 'ui/enemy_bar_hp.png')
META['ui/enemy_bar_bg.png'] = dict(anchor=[16, 4], fill_rect=[1, 1, 30, 3], notes='small monster HP bar trough; bottom-centre anchor goes on the monster hp_bar_anchor.')
META['ui/enemy_bar_hp.png'] = dict(notes='30x3 monster HP fill, draw at [1,1] inside enemy_bar_bg, crop width by HP%.')
# HP/MP card 96x28
CW, CH = 96, 28
Cd = frame(CW, CH, WOOD, thick=1)
slot = rect(CW, CH, 3, 3, 24, 24); paint(Cd, slot, C['outline']); paint(Cd, rect(CW, CH, 4, 4, 23, 23), C['slate'])
text_img = img(Cd); text(text_img, 27, 7, 'HP', C['cream']); text(text_img, 27, 17, 'MP', C['cream']); Cd = arr(text_img)
Cd[5:12, 35:35 + BW + 2] = BG; Cd[15:22, 35:35 + BW + 2] = BG
save(img(Cd), 'ui/hp_mp_card.png')
META['ui/hp_mp_card.png'] = dict(anchor=[0, 0], portrait_rect=[4, 4, 20, 20], hp_bar_rect=[36, 6, 54, 5], mp_bar_rect=[36, 16, 54, 5],
    hp_label=[27, 7], mp_label=[27, 17], notes='96x28. Empty bar troughs are baked in; draw bar_hp/bar_mp fills (54x5) at the rects, scaled/cropped horizontally by HP%.')
# 9-slice panels 48x48
def panel(st, fill, speck):
    L = frame(48, 48, st, fill=fill, thick=3)
    for y in range(5, 43):
        for x in range(5, 43):
            h = hsh(x, y, 11)
            if h < 0.05: L[y, x] = C[speck[0]] + (255,)
            elif h < 0.08 and len(speck) > 1: L[y, x] = C[speck[1]] + (255,)
    return L
save(img(panel(WOOD, 'parchment', ['sand', 'tan'])), 'ui/panel_parchment.png')
save(img(panel(WOOD, 'ink', ['slate'])), 'ui/panel_dark.png')
for k in ('ui/panel_parchment.png', 'ui/panel_dark.png'):
    META[k] = dict(nine_slice_margins=dict(left=6, top=6, right=6, bottom=6), notes='48x48 NinePatchRect source; margins 6px each side (frame 5px + 1px interior). Centre may tile or stretch (speckle is sparse).')

# ---------------- damage digits ----------------
GL = {'0': [" ### ", "## ##", "## ##", "## ##", "## ##", "## ##", " ### "], '1': ["  ## ", " ### ", "  ## ", "  ## ", "  ## ", "  ## ", " ####"],
 '2': [" ### ", "## ##", "   ##", "  ## ", " ##  ", "##   ", "#####"], '3': ["#### ", "   ##", "   ##", " ### ", "   ##", "   ##", "#### "],
 '4': ["## ##", "## ##", "## ##", "#####", "   ##", "   ##", "   ##"], '5': ["#####", "##   ", "#### ", "   ##", "   ##", "## ##", " ### "],
 '6': [" ### ", "##   ", "#### ", "## ##", "## ##", "## ##", " ### "], '7': ["#####", "   ##", "  ## ", "  ## ", " ##  ", " ##  ", " ##  "],
 '8': [" ### ", "## ##", "## ##", " ### ", "## ##", "## ##", " ### "], '9': [" ### ", "## ##", "## ##", " ####", "   ##", "   ##", " ### "],
 '+': ["     ", "  #  ", "  #  ", "#####", "  #  ", "  #  ", "     "], '-': ["     ", "     ", "     ", "#####", "     ", "     ", "     "]}
DMG = {'hp': ('coral', 'red'), 'mp': ('sky', 'blue'), 'heal': ('lime', 'grass')}
def glyph(ch, fill, shade):
    L = layer(7, 9)
    for y, row in enumerate(GL[ch]):
        for x, c in enumerate(row):
            if c == '#': L[y + 1, x + 1] = C[fill] + (255,) if y < 6 else C[shade] + (255,)
    outline(L, diag=True); return L
ORDER = '0123456789+-'
for k, (f, s) in DMG.items():
    save(img(strip([glyph(ch, f, s) for ch in ORDER])), f'ui/dmg_font_{k}.png')
    META[f'ui/dmg_font_{k}.png'] = dict(frames=12, frame_size=[7, 9], notes="glyph order '0123456789+-'; advance 6px (1px outline overlap). Colour %s / shade %s, outline #120c18." % (pal.HEX[pal.NAMES.index(f)], pal.HEX[pal.NAMES.index(s)]))
def number(s, k):
    f, sd = DMG[k]; L = layer(6 * len(s) + 1, 9)
    for i, ch in enumerate(s): over(L[:, i * 6:i * 6 + 7], glyph(ch, f, sd))
    return L
bgp = arr(Image.open(OUT + 'combat/bg_forest.png'))[100:150, 120:240].copy()
samples = [('-12', 'hp', 6, 6), ('-7', 'hp', 50, 22), ('-5', 'mp', 6, 34), ('+18', 'heal', 60, 4), ('-99', 'hp', 80, 36), ('+3', 'mp', 34, 18)]
Pv = layer(120, 50); Pv[:] = bgp
for s, k, x, y in samples:
    n = number(s, k); m = n[..., 3] > 0; Pv[y:y + 9, x:x + n.shape[1]][m] = n[m]
save(img(Pv), 'ui/dmg_numbers_preview.png')
META['ui/dmg_numbers_preview.png'] = dict(notes='QA preview of damage numbers over the forest backdrop (not a runtime asset).')

# ================= v2: procedural TABLE (300x44) =================
from PIL import ImageDraw
def make_table(TW, TH):
    T_ = layer(TW, TH); xs_t, ys_t = grid(TW, TH)
    topf = round(TH * 0.30)                       # 13 @44, 12 @40
    top = z(TW, TH)
    for y in range(1, topf + 1):
        ins = round((topf - y) * 5 / (topf - 1)); top[y, 1 + ins:TW - 1 - ins] = True
    paint(T_, top, C['wood_lt'])
    s1, s2 = 1 + topf // 3, 1 + 2 * topf // 3
    for sy in (s1, s2): paint(T_, top & (ys_t == sy), C['wood'])
    for (y0, y1), fr in {(1, s1 - 1): [0.32, 0.71], (s1 + 1, s2 - 1): [0.15, 0.53, 0.87], (s2 + 1, topf): [0.40, 0.77]}.items():
        for f in fr: paint(T_, top & (xs_t == int(TW * f)) & (ys_t >= y0) & (ys_t <= y1), C['wood'])
    lip = topf + 1; paint(T_, rect(TW, TH, 1, lip, TW - 2, lip), C['tan'])
    ap1 = lip + 6; paint(T_, rect(TW, TH, 1, lip + 1, TW - 2, ap1), C['wood']); paint(T_, rect(TW, TH, 1, ap1, TW - 2, ap1), C['wood_dk'])
    paint(T_, rect(TW, TH, 1, ap1 + 1, TW - 2, ap1 + 1), C['outline'])
    lw = max(9, TW // 26)
    for x0 in (lw + 12, TW - 2 * lw - 12): paint(T_, rect(TW, TH, x0, ap1 + 2, x0 + lw - 4, ap1 + 2 + (TH - ap1) // 2), C['wood_dk'])
    for x0 in (5, TW - 6 - lw):
        leg = rect(TW, TH, x0, ap1 + 2, x0 + lw, TH - 2); paint(T_, leg, C['wood']); paint(T_, leg & (xs_t >= x0 + lw - 2), C['wood_dk'])
    outline(T_)
    return T_, dict(top_surface_rows=[1, topf], near_edge_y=lip, apron_rows=[lip + 1, ap1])
T_, ti = make_table(300, 44)
save(img(T_), 'combat/table.png')
META['combat/table.png'] = dict(anchor=[150, 43], **ti, legacy=True,
    notes='LEGACY (landscape). v2 procedural 300x44, calm grain. Bottom-centre anchor.')
T_, ti = make_table(266, 40)
save(img(T_), 'combat/table_portrait.png')
META['combat/table_portrait.png'] = dict(anchor=[133, 39], **ti,
    notes='PORTRAIT table (v5: widened 250->266 for a 5-seat party), procedural 266x40: 3 long planks, 3 flat wood tones, tan highlight lip on the near edge. Bottom-centre anchor; GM hands/props sit on the top surface rows.')

# ================= v2: procedural D20 (24x24) =================
DS = 24
def glyphs_num(L, s, cx, y0, col):
    w = len(s) * 6 - 1; x = cx - w // 2
    for ch in s:
        for yy, row in enumerate(GLD[ch]):
            for xx, c in enumerate(row):
                if c == '#': L[y0 + yy, x + xx] = col + (255,)
        x += 6
GLD = {'0': [" ### ", "## ##", "## ##", "## ##", "## ##", "## ##", " ### "], '1': ["  ## ", " ### ", "  ## ", "  ## ", "  ## ", "  ## ", " ####"],
 '2': [" ### ", "## ##", "   ##", "  ## ", " ##  ", "##   ", "#####"], '3': ["#### ", "   ##", "   ##", " ### ", "   ##", "   ##", "#### "],
 '4': ["## ##", "## ##", "## ##", "#####", "   ##", "   ##", "   ##"], '5': ["#####", "##   ", "#### ", "   ##", "   ##", "## ##", " ### "],
 '6': [" ### ", "##   ", "#### ", "## ##", "## ##", "## ##", " ### "], '7': ["#####", "   ##", "  ## ", "  ## ", " ##  ", " ##  ", " ##  "],
 '8': [" ### ", "## ##", "## ##", " ### ", "## ##", "## ##", " ### "], '9': [" ### ", "## ##", "## ##", " ####", "   ##", "   ##", " ### "]}
def poly_mask(vs):
    im = Image.new('L', (DS, DS), 0); ImageDraw.Draw(im).polygon(vs, fill=1); return np.array(im) > 0
DIE_W = dict(face='white', side='mist', low='silver', low2='gray', ink='outline')
DIE_G = dict(face='cream', side='gold', low='amber', low2='orange', ink='outline')
HEXP = [(12, 1), (22, 6), (22, 17), (12, 22), (1, 17), (1, 6)]      # pointy-top
HEXF = [(6, 2), (17, 2), (22, 11), (17, 21), (6, 21), (1, 11)]       # flat-top (tumble)
def die_face(num, pal_=DIE_W):
    L = layer(DS, DS)
    paint(L, poly_mask(HEXP), C[pal_['low']])
    paint(L, poly_mask([(12, 1), (1, 6), (1, 17)]) | poly_mask([(12, 1), (22, 6), (22, 17)]), C[pal_['side']])
    paint(L, poly_mask([(1, 17), (12, 22), (12, 18)]), C[pal_['low2']])
    paint(L, poly_mask([(12, 2), (22, 17), (1, 17)]), C[pal_['face']])
    outline(L)
    if num is not None: glyphs_num(L, str(num), 12, 10, C[pal_['ink']])
    return L
def die_tumble(kind, num):
    L = layer(DS, DS)
    if kind == 'flat':
        paint(L, poly_mask(HEXF), C['silver'])
        paint(L, poly_mask([(6, 2), (17, 2), (22, 11), (1, 11)]), C['mist'])
        paint(L, poly_mask([(6, 3), (17, 3), (12, 19)]), C['white'])
        outline(L); glyphs_num(L, str(num), 12, 5, C['outline'])
    else:  # pointy, face turned sideways (triangle pointing right)
        paint(L, poly_mask(HEXP), C['silver'])
        paint(L, poly_mask([(12, 1), (22, 6), (1, 6)]), C['mist'])
        paint(L, poly_mask([(3, 5), (21, 12), (3, 19)]), C['white'])
        outline(L); glyphs_num(L, str(num), 10, 9, C['outline'])
    return L
roll = [die_tumble('flat', 13), die_tumble('point', 8), die_tumble('flat', 4), die_face(20)]
save(img(strip(roll)), 'combat/d20_roll.png')
META['combat/d20_roll.png'] = dict(frames=4, frame_size=[DS, DS], fps=12, anchor=[12, 23],
    notes='v2 24x24. Loop frames 0-2 while tumbling (flat/pointy silhouettes alternate), then land on frame 3 (legible 20) or swap in the rolled face from d20_results.png.')
save(img(strip([die_face(n) for n in range(1, 21)])), 'combat/d20_results.png')
META['combat/d20_results.png'] = dict(frames=20, frame_size=[DS, DS], anchor=[12, 23], notes='result faces: frame i shows number i+1 (bold 5x7 digits in #120c18 on a white triangle).')
save(img(die_face(20, DIE_G)), 'combat/d20_nat20.png')
META['combat/d20_nat20.png'] = dict(anchor=[12, 23], notes='gold natural-20 result frame (swap in for frame 3 on a nat 20).')

# ================= PORTRAIT UI (270x480 layout) =================
PW = 'ui/portrait/'
# narrow HP/MP card 130x28
NW = 130; NBW = 88
Cn = frame(NW, 28, WOOD, thick=1)
paint(Cn, rect(NW, 28, 3, 3, 24, 24), C['outline']); paint(Cn, rect(NW, 28, 4, 4, 23, 23), C['slate'])
ti_ = img(Cn); text(ti_, 27, 7, 'HP', C['cream']); text(ti_, 27, 17, 'MP', C['cream']); Cn = arr(ti_)
BGn = layer(NBW + 2, 7); paint(BGn, rect(NBW + 2, 7, 0, 0, NBW + 1, 6), C['outline']); paint(BGn, rect(NBW + 2, 7, 1, 1, NBW, 5), C['ink']); paint(BGn, rect(NBW + 2, 7, 1, 5, NBW, 5), C['slate'])
Cn[5:12, 35:35 + NBW + 2] = BGn; Cn[15:22, 35:35 + NBW + 2] = BGn
save(img(Cn), PW + 'hp_mp_card_narrow.png')
META[PW + 'hp_mp_card_narrow.png'] = dict(anchor=[0, 0], portrait_rect=[4, 4, 20, 20], hp_bar_rect=[36, 6, NBW, 5], mp_bar_rect=[36, 16, NBW, 5], hp_label=[27, 7], mp_label=[27, 17],
    notes='130x28 portrait-layout card (2x2 grid). Draw bar_hp_88/bar_mp_88 at the rects, cropped by %.')
save(img(bar(NBW, 5, 'red', 'coral', 'red_dk')), PW + 'bar_hp_88.png'); save(img(bar(NBW, 5, 'blue', 'sky', 'blue_dk')), PW + 'bar_mp_88.png')
save(img(BGn), PW + 'bar_bg_90.png')
META[PW + 'bar_hp_88.png'] = dict(notes='88x5 HP fill for the narrow card.'); META[PW + 'bar_mp_88.png'] = dict(notes='88x5 MP fill for the narrow card.')
META[PW + 'bar_bg_90.png'] = dict(fill_rect=[1, 1, 88, 5], notes='90x7 trough (already baked into the narrow card).')
# v5 compact vertical card 52x44 (one row of 5)
CW_, CH_, CBW = 52, 44, 44
TR = layer(CBW + 2, 7); paint(TR, rect(CBW + 2, 7, 0, 0, CBW + 1, 6), C['outline']); paint(TR, rect(CBW + 2, 7, 1, 1, CBW, 5), C['ink']); paint(TR, rect(CBW + 2, 7, 1, 5, CBW, 5), C['slate'])
for sfx, st in (('', WOOD), ('_active', GOLD)):
    Cc = frame(CW_, CH_, st, thick=1, studs=False)
    paint(Cc, rect(CW_, CH_, 15, 3, 36, 24), C['outline']); paint(Cc, rect(CW_, CH_, 16, 4, 35, 23), C['slate'])
    Cc[26:33, 3:3 + CBW + 2] = TR; Cc[33:40, 3:3 + CBW + 2] = TR
    ti_ = img(Cc); Cc = arr(ti_)
    save(img(Cc), PW + f'hp_mp_card_compact{sfx}.png')
    META[PW + f'hp_mp_card_compact{sfx}.png'] = dict(anchor=[0, 0], size=[CW_, CH_], portrait_rect=[16, 4, 20, 20], hp_bar_rect=[4, 27, CBW, 5], mp_bar_rect=[4, 34, CBW, 5],
        notes=('ACTIVE/current-turn highlight (gold frame). ' if sfx else '') + 'v5 compact vertical party card 52x44 for a 5-wide row (step 54 = 52 + 2px gap). Face crop (paperdoll portrait_crop_rect) at portrait_rect; bar_hp_44/bar_mp_44 at the bar rects, cropped by %. Bars are colour-coded red/blue (no HP/MP text at this size).')
save(img(bar(CBW, 5, 'red', 'coral', 'red_dk')), PW + 'bar_hp_44.png'); save(img(bar(CBW, 5, 'blue', 'sky', 'blue_dk')), PW + 'bar_mp_44.png')
META[PW + 'bar_hp_44.png'] = dict(notes='44x5 HP fill for hp_mp_card_compact (rect [4,27,44,5]).'); META[PW + 'bar_mp_44.png'] = dict(notes='44x5 MP fill for hp_mp_card_compact (rect [4,34,44,5]).')
# 32x32 thumb-reach buttons
for n, ic in icons.items():
    for sfx, st in (('', WOOD), ('_active', GOLD)):
        Lb = frame(32, 32, st, thick=2); paint(Lb, rect(32, 32, 4, 4, 27, 27), C['ink']); over(Lb[6:26, 6:26], ic)
        save(img(Lb), PW + f'btn32_{n}{sfx}.png')
        META[PW + f'btn32_{n}{sfx}.png'] = dict(anchor=[0, 0], icon_rect=[6, 6, 20, 20], notes=('selected (gold). ' if sfx else '') + '32x32 bottom-bar action button (same icon art as ui/btn_*).')
# bottom action bar panel 270x48
AB = frame(270, 48, WOOD, fill='ink', thick=2)
save(img(AB), PW + 'action_bar.png')
BTN_X = [19, 69, 119, 169, 219]
META[PW + 'action_bar.png'] = dict(anchor=[0, 47], nine_slice_margins=dict(left=6, top=6, right=6, bottom=6), button_rects=[[x, 8, 32, 32] for x in BTN_X],
    notes='270x48 bottom bar; place at y=432 (bottom-left anchor at y 479). 5 buttons 32x32, 18px gaps, order attack/skill/item/cover/run.')
# top bar 270x20, gold icon, menu button
TB = frame(270, 20, WOOD, fill='ink', thick=1, studs=False); save(img(TB), PW + 'top_bar.png')
META[PW + 'top_bar.png'] = dict(anchor=[0, 0], nine_slice_margins=dict(left=3, top=3, right=3, bottom=3), gold_icon_pos=[5, 5], gold_text_pos=[18, 8], menu_btn_pos=[249, 1], notes='270x20 map/creator top bar.')
G_ = layer(10, 10); cm = ell(10, 10, 4.5, 4.5, 4.6, 4.6); shade(G_, cm, C['gold'], C['amber'], C['cream'])
paint(G_, rect(10, 10, 4, 3, 5, 6), C['amber']); outline(G_)
save(img(G_), 'ui/icon_gold.png'); META['ui/icon_gold.png'] = dict(anchor=[0, 0], notes='10x10 gold coin.')
MB = frame(18, 18, WOOD, fill='ink', thick=1, studs=False)
for y in (5, 8, 11): paint(MB, rect(18, 18, 5, y, 12, y + 1) if False else rect(18, 18, 5, y, 12, y), C['cream'])
save(img(MB), 'ui/btn_menu.png'); META['ui/btn_menu.png'] = dict(anchor=[0, 0], notes='18x18 menu (hamburger) button.')
# map destination marker (2-frame bob)
def arrow(dy):
    A = layer(9, 12); m = z(9, 12)
    for i, (x0, x1) in enumerate([(3, 5), (3, 5), (3, 5), (1, 7), (2, 6), (3, 5), (4, 4)]): m[1 + dy + i, x0:x1 + 1] = True
    shade(A, m, C['gold'], C['amber'], C['cream']); outline(A); return A
save(img(strip([arrow(0), arrow(2)])), 'map/marker_arrow.png')
META['map/marker_arrow.png'] = dict(frames=2, frame_size=[9, 12], fps=3, anchor=[4, 11], notes='destination marker, bottom tip at the anchor; 2px bob.')
# creator buttons
GREEN = dict(o='outline', hi='lime', mid='grass', lo='leaf_dk', stud='cream', studhi='white', studlo='leaf')
BC = frame(56, 24, GREEN, fill='leaf', thick=1, studs=False)
chk = [(20, 12), (21, 13), (22, 14), (23, 15), (24, 14), (25, 13), (26, 12), (27, 11), (28, 10), (29, 9), (30, 8), (31, 7)]
cm = z(56, 24)
for x, y in chk: cm[y:y + 3, x] = True
Lc = layer(56, 24); paint(Lc, cm, C['white']); outline(Lc); over(BC, Lc)
save(img(BC), 'ui/btn_confirm.png'); META['ui/btn_confirm.png'] = dict(anchor=[0, 0], notes='56x24 confirm (check) button.')
BR = frame(56, 24, GOLD, fill='amber', thick=1, studs=False)
dz = layer(56, 24); paint(dz, rect(56, 24, 22, 5, 33, 16), C['white']); paint(dz, rect(56, 24, 22, 16, 33, 17) | rect(56, 24, 33, 6, 34, 17), C['silver'])
for px, py in [(24, 7), (30, 7), (27, 10), (24, 13), (30, 13)]: paint(dz, rect(56, 24, px, py, px + 1, py + 1), C['outline'])
outline(dz); over(BR, dz)
save(img(BR), 'ui/btn_random.png'); META['ui/btn_random.png'] = dict(anchor=[0, 0], notes='56x24 randomise (die) button.')
for nm, flip in (('right', False), ('left', True)):
    Ar = frame(14, 22, WOOD, fill='wood_dk', thick=1, studs=False)
    am = z(14, 22)
    for i in range(5): am[6 + i:16 - i, 5 + i] = True
    La = layer(14, 22); paint(La, am, C['cream']); paint(La, am & e_bot(am), C['sand'])
    over(Ar, La)
    if flip: Ar = np.ascontiguousarray(Ar[:, ::-1])
    save(img(Ar), f'ui/btn_arrow_{nm}.png'); META[f'ui/btn_arrow_{nm}.png'] = dict(anchor=[0, 0], notes='14x22 creator cycle arrow.')
for sfx, st in (('', WOOD), ('_active', GOLD)):
    SF = frame(16, 16, st, fill=None, thick=0, studs=False); save(img(SF), f'ui/swatch_frame{sfx}.png')
    META[f'ui/swatch_frame{sfx}.png'] = dict(anchor=[0, 0], swatch_rect=[2, 2, 12, 12], notes='16x16 colour swatch frame; transparent 12x12 centre for the colour.')

json.dump(META, open(W_ + 'meta_proc.json', 'w'), indent=1)
print('ok', len(META))
