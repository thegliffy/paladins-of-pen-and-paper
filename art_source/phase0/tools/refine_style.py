"""REFINE PASS (phase 1, 2026-10-01): the one style rule set for the whole pack + the helpers that enforce it.
Every refined/new piece goes through these helpers, so outline, light and shadow are identical everywhere."""
import numpy as np
from PIL import Image
from pal import C, PAL

STYLE = dict(
    version='refine-2 (2026-10-01)',
    look='clean, simple low-res pixel art; monsters on top, wooden table + GM in front, players seated with their backs to us; 270x480 portrait shown at integer 4x nearest-neighbour.',
    palette='only the 48 colours of palette/palette48.hex; binary alpha (0/255); no pink family (rose_dk/rose/pink) in combat/, party/, monsters/.',
    pixel_grid='1 art pixel = 1 native pixel. No scaled-up pixels, no rotation or anti-aliasing, no sub-pixel blur. Mixed pixel sizes are not allowed.',
    light='one key light from the top-left. Top/left edges get the light tone, bottom/right the shadow tone. 3-4 tones per material ramp (dark, mid, light, optional highlight). No pillow shading (dark ring all round).',
    outline_sprites='every free-standing sprite (heroes, gear, monsters, GM, table, dice, props, icons, map pins, UI frames) has a closed 1px exterior outline in #120c18, 4-connected (convex corners stay open, which rounds the silhouette). The outermost opaque pixels are always #120c18.',
    outline_interior='inside a sprite, #120c18 lines only separate major parts (arm over body, weapon over cloth, hat brim). Inside one part use the material\'s darkest tone, never black noise. No isolated single pixels except deliberate glints/eyes (white, cream, gold, ice).',
    outline_backdrops='terrain (sky, ground, water, distant hills) has NO outline. Free-standing props in a backdrop (rocks, boulders, buildings, trees, posts, stalls) get the sprite outline (#120c18).',
    backdrop_layout='horizon y141; monster feet band y222-266 stays low-contrast and clear of props; below y300 is the calm zone behind the table/seats/UI (detail density and contrast drop). Ground detail grows toward the bottom (perspective) and is drawn as soft clusters of <=3 adjacent tones of one ramp: no blotchy camo patches, no speckle noise.',
    readability='at 1x a held weapon or bow is >=2px of solid colour plus its outline (>=4px across). Items that share a slot must differ in silhouette, not only in colour. Every HELD weapon/focus overlay on a seat has a 6x4 gloved fist (8x6 with its outline) on the grip: lit knuckle row with finger creases, tan leather glove so it fits every skin tone. Slung or strapped items (bows, Gravel Axe, Sunbrand, Road Lute, shields, Hymn Board) have no fist. A ranger without a bow has no quiver (manifest paperdoll.ranger_quiver).',
    shading='every refined sprite is relit per part (refine_style.relight): a dome normal from the part shape lit from the top-left; the lit share steps one tone up its material ramp, the shadowed bottom-right share one tone down, metal/gold get a second spec step. Hair/outfit layers only move inside their grayscale keys so runtime tinting still works. Skin layers are not relit.',
    shadows='monsters get a contact shadow: 50% checker of #120c18 under the feet (reads as translucent on any ground). Flyers get a smaller one at the feet anchor. Heroes use the chair.',
    dithering='only a 2-row checker at sky band boundaries and the contact shadows. No noise dither on sprites.',
    ui='parchment panels: parchment fill with a sand inner bevel and a wood frame inside the outline; dark panels: ink fill, slate bevel. Bars: 1px light top row, fill, 1px dark bottom row, inside an outline frame; empty track is ink. Buttons: 2px bevel (light top-left, dark bottom-right), pressed = bevel swapped + content 1px down.',
)
OUTL = np.array(C['outline'], np.uint8)
GLINT = [C[n] for n in ('white', 'cream', 'gold', 'ice')]

def A(im): return np.array(im.convert('RGBA')) if isinstance(im, Image.Image) else im.copy()
def I(a): return Image.fromarray(a.astype(np.uint8), 'RGBA')
def n4(m):
    p = np.pad(m, 1); return p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]
def edge_px(op):
    u, d, l, r = n4(op); return op & ~(u & d & l & r)

def enforce_outline(a, close_gaps=True):
    """rule outline_sprites: the outermost opaque pixels become #120c18; orphan opaque pixels (no 4-neighbour) are removed."""
    a = A(a); op = a[..., 3] > 0
    u, d, l, r = n4(op); orphan = op & ~(u | d | l | r)
    a[orphan] = 0; op &= ~orphan
    e = edge_px(op)
    if close_gaps: a[e, :3] = OUTL
    return a

def despeckle(a, protect_glints=True):
    """rule outline_interior: a single interior pixel whose 4 neighbours all share one colour X takes colour X
    (cleans cut-art jaggies / noise), except glint colours and outline pixels (deliberate lines stay)."""
    a = A(a); op = a[..., 3] > 0; rgb = a[..., :3].astype(np.int32); key = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
    p = np.pad(key, 1, constant_values=-1); po = np.pad(op, 1)
    up, dn, lf, rt = p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]
    allop = po[:-2, 1:-1] & po[2:, 1:-1] & po[1:-1, :-2] & po[1:-1, 2:]
    same = (up == dn) & (dn == lf) & (lf == rt) & (up != key) & allop & op
    ok = key != ((int(OUTL[0]) << 16) | (int(OUTL[1]) << 8) | int(OUTL[2]))
    if protect_glints:
        for g in GLINT: ok &= key != ((g[0] << 16) | (g[1] << 8) | g[2])
    nbr_out = up == ((int(OUTL[0]) << 16) | (int(OUTL[1]) << 8) | int(OUTL[2]))
    m = same & ok & ~nbr_out
    a[m, 0] = (up[m] >> 16) & 255; a[m, 1] = (up[m] >> 8) & 255; a[m, 2] = up[m] & 255
    return a, int(m.sum())

def style_sprite(a):
    a, n = despeckle(a); return enforce_outline(a), n

def contact_shadow(a, cx, cy, rx, ry=2.5, phase=0):
    """rule shadows: 50% checker of #120c18 ellipse, only where the frame is transparent (drawn behind)."""
    a = A(a); H, W = a.shape[:2]; ys, xs = np.mgrid[0:H, 0:W]
    m = (((xs + 0.5 - cx) / max(rx, 1)) ** 2 + ((ys + 0.5 - cy) / ry) ** 2 <= 1) & (((xs + ys + phase) % 2) == 0) & (a[..., 3] == 0)
    a[m, :3] = OUTL; a[m, 3] = 255
    return a

def outline_ring(a, col=None):
    """add a 1px 4-connected outline ring outside the opaque pixels (within the canvas)."""
    a = A(a); op = a[..., 3] > 0; u, d, l, r = n4(op); ring = (u | d | l | r) & ~op
    a[ring, :3] = np.array(col or C['outline'], np.uint8); a[ring, 3] = 255; return a

def to_palette(im):
    """nearest-palette quantise (used only to show off-palette 'before' placeholders inside the approval sheets)."""
    import pal
    a = np.array(im.convert('RGBA')); idx = pal.quant_idx(a[..., :3]); out = a.copy(); out[..., :3] = pal.PAL_NP[idx]
    out[..., 3] = np.where(a[..., 3] >= 128, 255, 0); out[out[..., 3] == 0] = 0; return Image.fromarray(out, 'RGBA')

# ======================= FULL PASS (refine-2): material relight under the top-left key light =======================
from scipy import ndimage as _ndi
RAMPS = dict(
    grey=['ink', 'slate', 'gray', 'silver', 'mist', 'white'],
    wood=['bark', 'wood_dk', 'wood', 'wood_lt', 'tan', 'sand', 'parchment'],
    skin=['skin6', 'skin5', 'skin4', 'skin3', 'skin2', 'skin1'],
    green=['pine_dk', 'pine', 'leaf_dk', 'leaf', 'grass', 'lime'],
    blue=['navy', 'blue_dk', 'blue', 'sky', 'sky_lt', 'ice'],
    red=['blood', 'red_dk', 'red', 'coral'],
    gold=['orange', 'amber', 'gold', 'cream'],
    plum=['plum_dk', 'plum', 'violet'])
METAL_KEYS = None
KEYS_HAIR = ['slate', 'gray', 'silver', 'mist']          # grayscale keys K1..K4 (hair/beard); tint must keep working
KEYS_OUTFIT = ['gray', 'silver', 'mist']                 # K2..K4 (outfit shirt)
def _key(c): return (int(c[0]) << 16) | (int(c[1]) << 8) | int(c[2])
METAL_KEYS = {_key(C[n]) for n in RAMPS['grey'] + RAMPS['gold']}
def _step_table(restrict=None, ramps=None):
    """{rgbkey: (darker rgb, lighter rgb)}; restrict = list of colour names that may only move inside that list."""
    t = {}
    for rp in (ramps or RAMPS).values():
        for i, n in enumerate(rp):
            t[_key(C[n])] = (C[rp[max(0, i - 1)]], C[rp[min(len(rp) - 1, i + 1)]])
    if restrict:
        for i, n in enumerate(restrict): t[_key(C[n])] = (C[restrict[max(0, i - 1)]], C[restrict[min(len(restrict) - 1, i + 1)]])
    return t
LIGHT3 = np.array([-0.55, -0.75, 0.9]); LIGHT3 = LIGHT3 / np.linalg.norm(LIGHT3)
def relight(a, restrict=None, hi=0.16, lo=0.18, min_px=8, bulge=1.0, lock=(), ramps=None, hi_min=0.80, lo_max=0.62, spec=0.0):
    """per part (4-connected run of non-outline pixels): dome normal from the distance transform, lambert-lit from the top-left.
    The brightest `hi` share of a part steps one tone up its material ramp, the darkest `lo` share one tone down.
    Keeps every drawn detail (folds, seams, trims), adds volume + a consistent light direction. Colours not in a ramp stay."""
    a = A(a); op = a[..., 3] > 0; key = (a[..., 0].astype(np.int64) << 16) | (a[..., 1].astype(np.int64) << 8) | a[..., 2]
    ol = key == _key(C['outline']); body = op & ~ol
    for n in lock: body &= key != _key(C[n])
    lab, nl = _ndi.label(body); t = _step_table(restrict, ramps); out = a.copy()
    for i, sl in enumerate(_ndi.find_objects(lab), 1):
        if sl is None: continue
        sl = (slice(max(0, sl[0].start - 1), sl[0].stop + 1), slice(max(0, sl[1].start - 1), sl[1].stop + 1))
        m = lab[sl] == i; n = int(m.sum())
        if n < min_px: continue
        d = _ndi.distance_transform_edt(np.pad(m, 1))[1:-1, 1:-1]; dm = max(d.max(), 1.0); tt = np.clip(d / dm, 0, 1)
        h = np.sqrt(1 - (1 - tt) ** 2) * dm * bulge
        gy, gx = np.gradient(_ndi.gaussian_filter(h, 0.9)); nv = np.stack([-gx, -gy, np.ones_like(h)], -1); nv /= np.linalg.norm(nv, axis=-1, keepdims=True)
        I = np.clip(nv @ LIGHT3, 0, 1); v = I[m]
        q_hi, q_lo = np.quantile(v, 1 - hi), np.quantile(v, lo)
        up = m & (I >= max(q_hi, hi_min)); dn = m & (I <= min(q_lo, lo_max))
        sp = m & (I >= max(np.quantile(v, 1 - spec), 0.9)) if spec > 0 else None
        ks = key[sl]; o = out[sl]
        for msk, j in ((up, 1), (dn, 0)):
            ys, xs = np.nonzero(msk)
            for y, x in zip(ys, xs):
                s_ = t.get(int(ks[y, x]))
                if s_ is not None: o[y, x, :3] = s_[j]
        if sp is not None:                                                   # metal specular: a second step up (grey / gold ramps only)
            for y, x in zip(*np.nonzero(sp)):
                k0 = int(ks[y, x])
                if k0 in METAL_KEYS:
                    s1 = t.get(k0)
                    if s1: s2 = t.get(_key(s1[1])); o[y, x, :3] = (s2 or s1)[1]
    return out
def eye_glints(a, eye_cols=('outline', 'ink'), white=('white', 'cream', 'mist')):
    """not used blindly: helper to place 1px glints at given points"""
    return a

def cast_shadow(a, caster, dx=1, dy=2, ramps=None):
    """rule light: a part lying UNDER another (head/hood/hat over the shoulders, pauldron over the arm) gets a 1-tone-darker band
    where the caster, shifted down-right by (dx,dy), falls on it. caster = bool mask of the occluding part(s)."""
    a = A(a); t = _step_table(None, ramps); H_, W_ = caster.shape
    sh_ = np.zeros_like(caster); sh_[dy:, dx:] = caster[:H_ - dy, :W_ - dx]
    key = (a[..., 0].astype(np.int64) << 16) | (a[..., 1].astype(np.int64) << 8) | a[..., 2]
    m = sh_ & ~caster & (a[..., 3] > 0) & (key != _key(C['outline']))
    for y, x in zip(*np.nonzero(m)):
        s_ = t.get(int(key[y, x]))
        if s_: a[y, x, :3] = s_[0]
    return a

EYE_COLS = ['gold', 'amber', 'cyan', 'ice', 'sky_lt', 'lime', 'cream', 'coral', 'red']
def eye_glints(a, cols=EYE_COLS, max_px=6, top_frac=0.62):
    """clearer faces: every small bright eye blob (2..max_px px of an eye colour, in the upper part of the sprite, enclosed by
    darker pixels) gets a 1px white catch-light on its top-left pixel (the key light)."""
    a = A(a); op = a[..., 3] > 0
    if not op.any(): return a
    ys, xs = np.nonzero(op); y0, y1 = ys.min(), ys.max(); ylim = y0 + (y1 - y0) * top_frac
    key = (a[..., 0].astype(np.int64) << 16) | (a[..., 1].astype(np.int64) << 8) | a[..., 2]
    for cn in cols:
        m = (key == _key(C[cn])) & op; lab, n = _ndi.label(m)
        for i in range(1, n + 1):
            yy, xx = np.nonzero(lab == i)
            if not (2 <= len(yy) <= max_px) or yy.min() > ylim: continue
            ring = _ndi.binary_dilation(lab == i) & ~(lab == i)
            if not (ring & op).all(): continue
            rk = key[ring]; dark = np.isin(rk, [_key(C[k]) for k in ('outline', 'ink', 'slate', 'navy', 'plum_dk', 'blood', 'bark', 'wood_dk', 'pine_dk', 'red_dk', 'pine', 'leaf_dk', 'blue_dk', 'gray', 'plum')]).mean()
            if dark < 0.6: continue
            j = np.argmin(yy * 100 + xx); a[yy[j], xx[j], :3] = C['white']
    return a
