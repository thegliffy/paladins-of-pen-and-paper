"""REFINE-2: back-view (seated) paperdoll layers + composed seats. Relight under the top-left key light (refine_style.relight),
hair/outfit kept inside their grayscale keys so runtime tinting still works. Seats are recomposed from the refined layers with the
exact build_doll.compose_back recipe (verified byte-identical on the pre-refine layers)."""
import numpy as np, glob, os
from PIL import Image
from pal import C, OUT
import refine_style as RS
SEAT_DEFAULTS = {
    'paladin': dict(skin=2, hair=2, hair_color='brown', outfit='white'), 'wizard': dict(skin=1, hair=5, hair_color='blonde', outfit='blue'),
    'ranger': dict(skin=3, hair=4, hair_color='ginger', outfit='green'), 'bard': dict(skin=5, hair=6, hair_color='black', outfit='red'),
    'cleric': dict(skin=4, hair=2, hair_color='white', outfit='white'), 'rogue': dict(skin=2, hair=3, hair_color='black', outfit='dark'),
    'barbarian': dict(skin=3, hair=8, hair_color='ginger', outfit=None), 'druid': dict(skin=6, hair=1, hair_color='white', outfit='green')}
HAIR_RAMPS = {'black': ['outline', 'ink', 'slate', 'gray'], 'brown': ['bark', 'wood_dk', 'wood', 'wood_lt'], 'blonde': ['wood_lt', 'tan', 'gold', 'cream'],
    'ginger': ['red_dk', 'orange', 'amber', 'gold'], 'white': ['gray', 'silver', 'mist', 'white'], 'blue': ['navy', 'blue_dk', 'blue', 'sky'], 'pink': ['rose_dk', 'rose', 'pink', 'cream'], 'green': ['pine_dk', 'leaf_dk', 'leaf', 'grass']}
OUTFIT_RAMPS = {'white': ['silver', 'mist', 'white'], 'red': ['red_dk', 'red', 'coral'], 'blue': ['blue_dk', 'blue', 'sky'], 'purple': ['plum_dk', 'plum', 'violet'],
    'green': ['pine', 'leaf_dk', 'leaf'], 'yellow': ['orange', 'amber', 'gold'], 'brown': ['wood_dk', 'wood', 'wood_lt'], 'dark': ['ink', 'slate', 'gray']}
HAT_CLIP_BACK = {'paladin': 33, 'wizard': 21, 'ranger': 60, 'bard': 21, 'cleric': 19, 'rogue': 60, 'barbarian': 30, 'druid': 0}
KH = [C[n] for n in RS.KEYS_HAIR]; KO = [C[n] for n in RS.KEYS_OUTFIT]
def remap(a, keys, names):
    a = np.array(a); o = a.copy()
    for k, n in zip(keys, names):
        m = (a[..., :3] == k).all(-1) & (a[..., 3] > 0); o[m, :3] = C[n]
    return o
def over(d, s):
    m = s[..., 3] > 0; d[m] = s[m]
def kind_of(rel):
    b = os.path.basename(rel)
    if b.startswith('hair_back'): return 'hair'
    if b.startswith('outfit_back'): return 'outfit'
    return 'colour'
HEAD = None
def head_mask(get, cls):
    """union of the head (body layer), the class hat/hood and its outline: casts the collar shadow onto the class layer."""
    m = (get('paperdoll/back/body_back_skin_3.png')[..., 3] > 0) & (np.mgrid[0:78, 0:48][0] < 34)
    return m | (get(f'paperdoll/back/class_back_{cls}_hat.png')[..., 3] > 0)
def refine_layer(a, kind, caster=None):
    a = RS.A(a)
    if kind == 'hair': return RS.relight(a, restrict=RS.KEYS_HAIR, hi=0.26, lo=0.28, ramps={}, hi_min=0.72)       # only the 4 keys move
    if kind == 'outfit': return RS.relight(a, restrict=RS.KEYS_OUTFIT, hi=0.24, lo=0.28, hi_min=0.72)
    a = RS.relight(a, hi=0.26, lo=0.28, hi_min=0.72, lo_max=0.66, spec=0.05)
    if caster is not None: a = RS.cast_shadow(a, caster, 1, 2)
    return a
def compose(get, cls, active=False, variant=''):
    """get(rel)->RGBA array. variant: '' | '_noweapon' | '_noweapon_noquiver' (class layer suffix)."""
    d = SEAT_DEFAULTS[cls]; L = np.zeros((78, 48, 4), np.uint8)
    over(L, get(f'paperdoll/back/body_back_skin_{d["skin"]}.png'))
    if d['outfit']: over(L, remap(get('paperdoll/back/outfit_back.png'), KO, OUTFIT_RAMPS[d['outfit']]))
    over(L, get(f'paperdoll/back/class_back_{cls}{variant}.png'))
    hl = remap(get(f'paperdoll/back/hair_back_{d["hair"]}.png'), KH, HAIR_RAMPS[d['hair_color']]); hl[:HAT_CLIP_BACK[cls]] = 0; over(L, hl)
    over(L, get(f'paperdoll/back/class_back_{cls}_hat.png')); over(L, get('paperdoll/back/chair_back.png'))
    if active: L = active_ring(L)
    return L
def active_ring(L):
    L2 = np.zeros_like(L); L2[:-3] = L[3:]; op = L2[..., 3] > 0
    n = np.zeros_like(op); n[1:] |= op[:-1]; n[:-1] |= op[1:]; n[:, 1:] |= op[:, :-1]; n[:, :-1] |= op[:, 1:]
    L2[n & ~op] = C['gold'] + (255,); return L2
