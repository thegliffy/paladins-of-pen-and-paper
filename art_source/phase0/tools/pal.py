import numpy as np, os, json
from PIL import Image

OUT = '/workspace/paladins-art/phase0/'
HEX = """120c18 2a2530 46424e 6c6a76 9c9ca6 cfd0d4 f6f6f2
2c1810 4c2c1a 744526 9c6636 c48c4e e2bc82 f4dcae
ffe2cc f0c09c d89c72 b27a4e 8c5836 5e3822
16302a 1f4a34 2f6a34 4c9434 7cbc3c b4dc62
161c40 243a8a 3466cc 4c9ce8 86c8f8 c4ecff
3e1016 7c1c22 c02c2c ec5a44
c8601c f09a2c f8d040 fcf0a0
2a1844 52288a 8450c8 5e9c8c
b03c78 ec78aa fcb8d4 3ce0dc""".split()
assert len(HEX) == 48 and len(set(HEX)) == 48
PAL = [tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) for h in HEX]
NAMES = ['outline','ink','slate','gray','silver','mist','white',
 'bark','wood_dk','wood','wood_lt','tan','sand','parchment',
 'skin1','skin2','skin3','skin4','skin5','skin6',
 'pine_dk','pine','leaf_dk','leaf','grass','lime',
 'navy','blue_dk','blue','sky','sky_lt','ice',
 'blood','red_dk','red','coral',
 'orange','amber','gold','cream',
 'plum_dk','plum','violet','haze',
 'rose_dk','rose','pink','cyan']
C = {n: PAL[i] for i, n in enumerate(NAMES)}
def H(h): return tuple(int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

def _lab(rgb):
    c = np.asarray(rgb, dtype=np.float64) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)
PAL_LAB = _lab(np.array(PAL))
PINKS = [NAMES.index(n) for n in ('rose_dk', 'rose', 'pink')]

def quant_idx(rgb, allowed=None):
    """rgb: (...,3) array -> palette index array"""
    lab = _lab(rgb)
    d = ((lab[..., None, :] - PAL_LAB) ** 2).sum(-1)
    if allowed is not None:
        mask = np.full(len(PAL), np.inf); mask[allowed] = 0
        d = d + mask
    return d.argmin(-1)

NOPINK = [i for i in range(48) if i not in PINKS]
PAL_NP = np.array(PAL, dtype=np.uint8)

def idx_to_img(idx, alpha):
    h, w = idx.shape
    a = np.zeros((h, w, 4), np.uint8)
    a[..., :3] = PAL_NP[idx]
    a[..., 3] = np.where(alpha, 255, 0)
    a[~alpha, :3] = 0
    return Image.fromarray(a, 'RGBA')

def save(img, rel):
    p = OUT + rel
    os.makedirs(os.path.dirname(p), exist_ok=True)
    img = img.convert('RGBA')
    a = np.array(img)
    a[a[..., 3] < 128] = 0
    a[a[..., 3] >= 128, 3] = 255
    Image.fromarray(a, 'RGBA').save(p)
    return p

def new(w, h, col=None):
    return Image.new('RGBA', (w, h), (col + (255,)) if col else (0, 0, 0, 0))

def remap(img, mapping):
    """mapping: {rgb: rgb}"""
    a = np.array(img.convert('RGBA'))
    out = a.copy()
    for k, v in mapping.items():
        m = (a[..., 0] == k[0]) & (a[..., 1] == k[1]) & (a[..., 2] == k[2]) & (a[..., 3] == 255)
        out[m, :3] = v
    return Image.fromarray(out, 'RGBA')

def outline_img(img, col=None, diag=False):
    """add 1px outline outside opaque pixels (in place, within canvas)"""
    col = col or C['outline']
    a = np.array(img); op = a[..., 3] > 0
    n = np.zeros_like(op)
    n[1:] |= op[:-1]; n[:-1] |= op[1:]; n[:, 1:] |= op[:, :-1]; n[:, :-1] |= op[:, 1:]
    if diag:
        n[1:, 1:] |= op[:-1, :-1]; n[:-1, :-1] |= op[1:, 1:]; n[1:, :-1] |= op[:-1, 1:]; n[:-1, 1:] |= op[1:, :-1]
    ring = n & ~op
    a[ring] = col + (255,)
    return Image.fromarray(a, 'RGBA')

def shift(img, dx, dy, size=None):
    size = size or img.size
    c = new(*size); c.alpha_composite(img, (0, 0)) if False else None
    c.paste(img, (dx, dy), img)
    return c

def check_palette(img):
    a = np.array(img.convert('RGBA'))
    op = a[..., 3] == 255
    bad_alpha = int(((a[..., 3] != 0) & (a[..., 3] != 255)).sum())
    cols = set(map(tuple, a[op][:, :3].tolist()))
    bad = cols - set(PAL)
    return bad_alpha, bad

# ---- tiny original 3x5 pixel font for labels / numbers ----
FONT = {
 'A':"010101111101101",'B':"110101110101110",'C':"011100100100011",'D':"110101101101110",
 'E':"111100110100111",'F':"111100110100100",'G':"011100101101011",'H':"101101111101101",
 'I':"111010010010111",'J':"001001001101010",'K':"101101110101101",'L':"100100100100111",
 'M':"101111111101101",'N':"110101101101101",'O':"010101101101010",'P':"110101110100100",
 'Q':"010101101110011",'R':"110101110101101",'S':"011100010001110",'T':"111010010010010",
 'U':"101101101101111",'V':"101101101101010",'W':"101101111111101",'X':"101101010101101",
 'Y':"101101010010010",'Z':"111001010100111",
 '0':"111101101101111",'1':"010110010010111",'2':"110001010100111",'3':"110001010001110",
 '4':"101101111001001",'5':"111100110001110",'6':"011100111101111",'7':"111001010010010",
 '8':"111101111101111",'9':"111101111001110",
 '_':"000000000000111",'-':"000000111000000",'+':"000010111010000",'.':"000000000000010",
 '/':"001001010100100",' ':"000000000000000",'x':"000101010101000",':':"000010000010000",
 '(':"010100100100010",')':"010001001001010",'#':"101111101111101",'!':"010010010000010",
 '%':"101001010100101",',':"000000000010100","'":"010010000000000",'=':"000111000111000",'?':"110001010000010",
}
def text(img, x, y, s, col, scale=1):
    px = img.load()
    for ch in s.upper() if s.upper() != s else s:
        g = FONT.get(ch.upper(), FONT[' '])
        for i, b in enumerate(g):
            if b == '1':
                for sy in range(scale):
                    for sx in range(scale):
                        X, Y = x + (i % 3) * scale + sx, y + (i // 3) * scale + sy
                        if 0 <= X < img.width and 0 <= Y < img.height:
                            px[X, Y] = col + (255,)
        x += 4 * scale
    return x
def text_w(s, scale=1): return len(s) * 4 * scale - scale
