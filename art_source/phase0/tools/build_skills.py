"""v3: 32 class skill icons (20x20), skill slot frames, skill sheet, 7 skill FX strips."""
import json, math
import numpy as np
from PIL import Image, ImageDraw
import pal
from pal import C, save, text, text_w
from proclib import layer, paint, outline, over, img, ring, sh, e_bot, e_right, e_top, e_left, hsh, rect, ell, z, pts
META = {}
W_ = '/workspace/paladins-art/phase0/tools/_work/'
NAMES = pal.NAMES
# ======================= ICONS =======================
class Ic:
    def __init__(s, n=20):
        s.n = n; s.im = Image.new('L', (n, n), 0); s.d = ImageDraw.Draw(s.im)
    def k(s, col): return NAMES.index(col) + 1
    def poly(s, p, col): s.d.polygon(p, fill=s.k(col)); return s
    def line(s, p, col, w=1): s.d.line(p, fill=s.k(col), width=w); return s
    def ell(s, b, col, w=None):
        (s.d.ellipse(b, fill=s.k(col)) if w is None else s.d.ellipse(b, outline=s.k(col), width=w)); return s
    def arc(s, b, a0, a1, col, w=1): s.d.arc(b, a0, a1, fill=s.k(col), width=w); return s
    def rect(s, b, col): s.d.rectangle(b, fill=s.k(col)); return s
    def px(s, lst, col):
        for p in lst: s.d.point(p, fill=s.k(col))
        return s
    def clear(s, b): s.d.rectangle(b, fill=0); return s
    def clear_ell(s, b): s.d.ellipse(b, fill=0); return s
    def done(s):
        a = np.array(s.im); L = layer(s.n, s.n)
        for i in np.unique(a):
            if i: L[a == i] = C[NAMES[i - 1]] + (255,)
        outline(L); return L
def arrow(ic, x0, y0, x1, y1, shaft='wood', head='silver', fl='red'):
    ic.line([(x0, y0), (x1, y1)], shaft, 1)
    dx, dy = x1 - x0, y1 - y0; l = math.hypot(dx, dy); ux, uy = dx / l, dy / l; px_, py_ = -uy, ux
    tip = (x1 + ux * 1.5, y1 + uy * 1.5); b = (x1 - ux * 3.5, y1 - uy * 3.5)
    ic.poly([tip, (b[0] + px_ * 2.6, b[1] + py_ * 2.6), (b[0] - px_ * 2.6, b[1] - py_ * 2.6)], head)
    for t in (0, 1.5):
        f = (x0 + ux * t, y0 + uy * t)
        ic.line([f, (f[0] + (px_ - ux) * 2.2, f[1] + (py_ - uy) * 2.2)], fl); ic.line([f, (f[0] + (-px_ - ux) * 2.2, f[1] + (-py_ - uy) * 2.2)], fl)
def star_poly(cx, cy, ro, ri, n, rot=-math.pi / 2):
    return [(cx + (ro if i % 2 == 0 else ri) * math.cos(rot + i * math.pi / n), cy + (ro if i % 2 == 0 else ri) * math.sin(rot + i * math.pi / n)) for i in range(2 * n)]
def note(ic, x, y, col='gold', sh_='amber', s=1.0):
    ic.ell((x, y + 9 * s, x + 5 * s, y + 13 * s), col); ic.rect((x + 4 * s, y, x + 5 * s, y + 11 * s), col)
    ic.poly([(x + 5 * s, y), (x + 10 * s, y + 3 * s), (x + 10 * s, y + 6 * s), (x + 5 * s, y + 3 * s)], col)
    ic.px([(x + 1 * s, y + 12 * s), (x + 2 * s, y + 12 * s)], sh_)

ICONS = {}; MOTIF = {}
def reg(name, motif, L): ICONS[name] = L; MOTIF[name] = motif
# ---- paladin
i = Ic(); i.line([(12, 7), (12, 17)], 'cream'); i.line([(8, 12), (17, 12)], 'cream'); i.line([(10, 10), (14, 14)], 'gold'); i.line([(14, 10), (10, 14)], 'gold'); i.px([(12, 12)], 'white')
i.line([(6, 12), (16, 2)], 'mist', 2); i.line([(7, 12), (16, 3)], 'silver'); i.px([(16, 2)], 'white'); i.line([(3, 10), (8, 15)], 'gold', 2); i.line([(2, 17), (5, 14)], 'wood', 2); i.px([(1, 18), (2, 18)], 'gold')
reg('paladin_1', 'sword of light (holy strike)', i.done())
i = Ic(); i.poly([(7, 2), (17, 2), (17, 10), (12, 17), (7, 10)], 'gold'); i.poly([(8, 3), (16, 3), (16, 10), (12, 15), (8, 10)], 'blue'); i.poly([(12, 3), (16, 3), (16, 10), (12, 15)], 'blue_dk')
i.rect((11, 4, 12, 13), 'gold'); i.rect((9, 7, 15, 8), 'gold'); i.line([(1, 5), (4, 5)], 'mist'); i.line([(1, 9), (5, 9)], 'white'); i.line([(1, 13), (4, 13)], 'mist')
reg('paladin_2', 'shield bash', i.done())
i = Ic()
for a in range(8):
    t = a * math.pi / 4; i.line([(9.5 + 6.5 * math.cos(t), 9.5 + 6.5 * math.sin(t)), (9.5 + 8.5 * math.cos(t), 9.5 + 8.5 * math.sin(t))], 'gold')
i.ell((4, 4, 15, 15), 'gold'); i.ell((5, 5, 14, 14), 'cream'); i.ell((7, 7, 12, 12), 'white'); i.arc((5, 5, 14, 14), 20, 110, 'amber')
reg('paladin_3', 'holy aura (radiant halo)', i.done())
i = Ic(); i.poly(star_poly(9.5, 9.5, 9.4, 6.2, 8), 'red'); i.poly(star_poly(9.5, 9.5, 6.6, 4.6, 8), 'coral'); i.rect((9, 3, 10, 11), 'white'); i.rect((9, 13, 10, 15), 'white'); i.px([(10, 4), (10, 5)], 'mist')
reg('paladin_4', 'taunt (shout burst "!")', i.done())
# ---- wizard
i = Ic(); i.poly([(9, 6), (1, 18), (6, 16), (4, 18), (13, 14)], 'red'); i.poly([(10, 8), (4, 16), (12, 13)], 'orange')
i.ell((7, 3, 18, 14), 'orange'); i.ell((8, 4, 16, 12), 'amber'); i.ell((10, 5, 15, 10), 'gold'); i.ell((11, 6, 13, 8), 'cream')
reg('wizard_1', 'fireball', i.done())
i = Ic(); i.poly([(3, 7), (6, 9), (4, 15), (1, 11)], 'sky_lt'); i.poly([(16, 6), (18, 11), (15, 16), (13, 10)], 'sky_lt')
i.poly([(9.5, 1), (14, 9), (9.5, 18), (5, 9)], 'ice'); i.poly([(9.5, 1), (14, 9), (9.5, 18)], 'sky_lt'); i.line([(8, 5), (7, 9)], 'white'); i.px([(3, 9), (15, 9)], 'white')
reg('wizard_2', 'ice shard', i.done())
i = Ic(); i.poly([(12, 1), (4, 10), (9, 10), (6, 18), (16, 7), (11, 7), (15, 1)], 'gold'); i.line([(12, 2), (6, 9)], 'cream'); i.line([(9, 11), (7, 16)], 'cream'); i.px([(14, 7), (15, 7)], 'amber')
reg('wizard_3', 'lightning bolt', i.done())
hexp = lambda r: [(9.5 + r * math.cos(a * math.pi / 3 + math.pi / 6), 9.5 + r * math.sin(a * math.pi / 3 + math.pi / 6)) for a in range(6)]
i = Ic(); i.poly(hexp(9.4), 'violet'); i.poly(hexp(7.6), 'plum'); i.poly(hexp(4.8), 'violet'); i.poly(hexp(3.2), 'plum'); i.poly(star_poly(9.5, 9.5, 2.6, 1.0, 4), 'pink'); i.line([(4, 5), (8, 3)], 'rose')
reg('wizard_4', 'arcane shield (hex ward)', i.done())
# ---- ranger
i = Ic(); arrow(i, 3, 16, 15, 4); reg('ranger_1', 'arrow shot', i.done())
i = Ic(); arrow(i, 1, 8, 7, 2, fl='wood'); arrow(i, 3, 16, 14, 5); arrow(i, 11, 18, 17, 12, fl='wood'); reg('ranger_2', 'multi-shot (3 arrows)', i.done())
i = Ic(); i.rect((2, 15, 17, 17), 'gray'); i.rect((2, 15, 17, 15), 'silver'); i.line([(18, 16), (18, 18)], 'slate')
i.line([(8, 15), (4, 12), (2, 8), (2, 3)], 'silver', 2); i.line([(11, 15), (15, 12), (17, 8), (17, 3)], 'silver', 2)
for (x, y) in ((4, 4), (4, 8), (6, 11)): i.poly([(x, y - 1), (x + 2, y), (x, y + 1)], 'mist'); i.poly([(19 - x, y - 1), (17 - x, y), (19 - x, y + 1)], 'mist')
i.rect((7, 13, 12, 14), 'wood'); i.px([(9, 13), (10, 13)], 'red'); reg('ranger_3', 'snare trap (bear trap)', i.done())
i = Ic(); i.ell((4, 9, 15, 18), 'wood_lt'); i.ell((5, 10, 12, 15), 'tan'); i.ell((1, 5, 5, 10), 'wood_lt'); i.ell((5, 1, 9, 6), 'wood_lt'); i.ell((10, 1, 14, 6), 'wood_lt'); i.ell((14, 5, 18, 10), 'wood_lt')
i.px([(2, 6), (6, 2), (11, 2), (15, 6)], 'tan'); reg('ranger_4', 'animal companion (paw print)', i.done())
# ---- bard
i = Ic(); note(i, 3, 2, s=1.2); i.px([(14, 3), (16, 5)], 'cream'); reg('bard_1', 'music note (damage note)', i.done())
i = Ic(); note(i, 1, 4); i.poly([(14, 1), (19, 7), (16, 7), (16, 17), (12, 17), (12, 7), (9, 7)], 'lime'); i.poly([(14, 1), (19, 7), (16, 7), (16, 17), (14, 17)], 'grass'); reg('bard_2', 'song buff (note + up arrow)', i.done())
i = Ic(); i.ell((1, 4, 14, 17), 'cream'); i.clear_ell((5, 2, 17, 13)); i.px([(3, 11), (4, 13)], 'sand')
i.line([(11, 2), (15, 2), (11, 6), (15, 6)], 'sky_lt'); i.line([(15, 9), (18, 9), (15, 12), (18, 12)], 'ice'); reg('bard_3', 'lullaby (moon + zz)', i.done())
i = Ic(); i.line([(9, 10), (16, 3)], 'wood_dk', 2); i.rect((15, 1, 18, 4), 'wood'); i.px([(14, 1), (18, 5)], 'gold')
i.ell((1, 7, 12, 18), 'wood_lt'); i.arc((1, 7, 12, 18), 0, 120, 'wood', 1); i.ell((5, 11, 8, 14), 'wood_dk'); i.line([(5, 15), (8, 16)], 'wood_dk'); reg('bard_4', 'lute', i.done())
# ---- cleric
i = Ic(); i.rect((7, 2, 12, 17), 'lime'); i.rect((2, 7, 17, 12), 'lime'); i.rect((11, 2, 12, 17), 'grass'); i.rect((2, 11, 17, 12), 'grass'); i.rect((7, 3, 8, 8), 'cream'); reg('cleric_1', 'heal (green cross)', i.done())
i = Ic()
for a in range(8):
    t = a * math.pi / 4 + math.pi / 8; i.line([(9.5 + 5 * math.cos(t), 7 + 5 * math.sin(t)), (9.5 + 9 * math.cos(t), 7 + 9 * math.sin(t))], 'cream')
i.rect((8, 1, 11, 18), 'gold'); i.rect((3, 5, 16, 8), 'gold'); i.rect((11, 1, 11, 18), 'amber'); i.rect((3, 8, 16, 8), 'amber'); reg('cleric_2', 'holy cross (bless)', i.done())
i = Ic(); i.ell((6, 1, 13, 9), 'ice', 2); i.rect((3, 8, 16, 10), 'ice'); i.rect((8, 10, 11, 18), 'ice'); i.rect((11, 10, 11, 18), 'sky_lt'); i.rect((3, 10, 16, 10), 'sky_lt'); i.px([(7, 3), (2, 2), (17, 3)], 'white')
reg('cleric_3', 'resurrect (spirit ankh)', i.done())
i = Ic(); i.poly(star_poly(5, 14, 5, 2.2, 5), 'cream'); i.px([(5, 14)], 'white'); i.line([(8, 11), (16, 3)], 'wood', 2)
i.poly([(9, 1), (13, 1), (18, 6), (18, 10), (14, 10), (9, 5)], 'silver'); i.poly([(13, 1), (18, 6), (18, 10), (15, 7)], 'gray'); i.line([(11, 3), (16, 8)], 'gold'); reg('cleric_4', 'smite (holy hammer)', i.done())
# ---- rogue
i = Ic(); i.poly([(9, 1), (10, 1), (12, 4), (12, 11), (7, 11), (7, 4)], 'mist'); i.poly([(10, 1), (12, 4), (12, 11), (10, 11)], 'silver'); i.rect((4, 12, 15, 13), 'gold'); i.rect((8, 14, 11, 17), 'ink'); i.rect((8, 18, 11, 18), 'gold'); i.line([(8, 4), (8, 10)], 'white')
reg('rogue_1', 'dagger strike', i.done())
i = Ic(); i.rect((8, 1, 11, 2), 'wood'); i.rect((8, 3, 11, 6), 'mist'); i.ell((3, 5, 16, 18), 'mist'); i.ell((4, 9, 15, 17), 'grass'); i.rect((4, 9, 15, 10), 'lime'); i.ell((4, 6, 15, 12), 'mist'); i.rect((5, 9, 14, 10), 'lime')
i.px([(7, 13), (11, 12), (9, 15)], 'lime'); i.px([(6, 7), (5, 8)], 'white'); i.ell((4, 9, 15, 17), 'grass', 1); i.px([(9, 3), (9, 4)], 'white'); reg('rogue_2', 'poison vial', i.done())
i = Ic(); i.ell((1, 8, 10, 16), 'gray'); i.ell((9, 9, 18, 17), 'gray'); i.ell((5, 3, 15, 12), 'silver'); i.ell((4, 11, 14, 18), 'silver'); i.ell((7, 5, 11, 8), 'mist'); i.ell((3, 10, 6, 12), 'mist'); i.px([(12, 14), (13, 13)], 'mist')
reg('rogue_3', 'smoke bomb', i.done())
i = Ic(); i.line([(2, 2), (5, 5)], 'ink', 2); i.line([(3, 7), (7, 3)], 'gold', 2); i.line([(7, 7), (15, 15)], 'mist', 2); i.line([(8, 7), (15, 14)], 'white'); i.px([(16, 16)], 'mist')
i.poly([(16, 14), (18, 17), (17, 18), (14, 17)], 'red'); i.px([(13, 18), (18, 12)], 'red'); i.line([(10, 1), (18, 9)], 'red_dk'); reg('rogue_4', 'backstab (bloody dagger)', i.done())
# ---- barbarian
i = Ic(); i.line([(5, 18), (12, 3)], 'wood', 2); i.px([(5, 17), (6, 15)], 'wood_dk'); i.poly([(10, 4), (16, 1), (18, 5), (18, 11), (16, 14), (10, 8)], 'silver'); i.poly([(16, 1), (18, 5), (18, 11), (16, 14), (15, 8)], 'mist'); i.line([(10, 5), (11, 8)], 'gray')
reg('barbarian_1', 'axe chop', i.done())
i = Ic(); fl = [(9, 1), (12, 5), (14, 2), (17, 9), (17, 14), (14, 18), (5, 18), (2, 14), (2, 8), (5, 10), (6, 4)]
i.poly(fl, 'red'); i.poly([(9, 6), (12, 9), (14, 8), (15, 13), (13, 17), (6, 17), (4, 13), (6, 11)], 'orange'); i.poly([(9, 11), (12, 13), (12, 16), (7, 16), (7, 13)], 'amber')
i.line([(5, 11), (8, 13)], 'outline'); i.line([(14, 11), (11, 13)], 'outline'); reg('barbarian_2', 'rage (angry flame)', i.done())
i = Ic(); i.poly([(1, 8), (7, 5), (7, 14), (1, 11)], 'sand'); i.rect((5, 5, 6, 14), 'wood'); i.px([(2, 9)], 'cream')
for r, col in ((5, 'amber'), (8, 'coral'), (11, 'red')): i.arc((6 - r, 9.5 - r, 6 + r, 9.5 + r), -50, 50, col, 2)
reg('barbarian_3', 'war cry (horn + sound waves)', i.done())
i = Ic(); i.ell((1, 14, 18, 18), 'amber', 1); i.rect((6, 1, 11, 9), 'wood'); i.rect((6, 8, 16, 12), 'wood'); i.rect((6, 12, 16, 13), 'wood_dk'); i.rect((6, 1, 11, 2), 'tan'); i.px([(7, 3), (7, 5)], 'wood_lt')
i.line([(1, 11), (3, 13)], 'cream'); i.line([(18, 10), (16, 13)], 'cream'); i.px([(3, 9), (17, 8)], 'cream'); reg('barbarian_4', 'stomp (boot + shockwave)', i.done())
# ---- druid
i = Ic(); i.poly([(2, 17), (3, 9), (8, 4), (17, 2), (15, 10), (10, 15)], 'grass'); i.poly([(2, 17), (17, 2), (15, 10), (10, 15)], 'leaf'); i.line([(3, 16), (15, 4)], 'leaf_dk'); i.line([(7, 12), (7, 8)], 'leaf_dk'); i.line([(10, 9), (13, 9)], 'leaf_dk')
i.rect((14, 12, 15, 17), 'lime'); i.rect((12, 14, 17, 15), 'lime'); i.px([(14, 14), (15, 15)], 'cream'); reg('druid_1', 'leaf heal', i.done())
i = Ic(); vine = [(2, 18), (6, 13), (5, 8), (9, 4), (14, 3), (17, 1)]; i.line(vine, 'wood', 2)
for (x, y, dx, dy) in ((5, 14, 3, 0), (4, 10, -3, -1), (7, 6, 1, -3), (11, 4, 1, 3), (15, 2, 2, 2), (6, 11, 3, 1)): i.poly([(x, y), (x + dx, y + dy), (x + (1 if dy else 0), y + (1 if dx else 0))], 'sand')
i.ell((10, 9, 14, 12), 'leaf'); i.px([(11, 10)], 'lime'); reg('druid_2', 'thorns (thorny vine)', i.done())
i = Ic(); i.ell((2, 2, 7, 7), 'wood'); i.ell((12, 2, 17, 7), 'wood'); i.ell((1, 4, 18, 18), 'wood'); i.ell((3, 3, 5, 5), 'tan'); i.ell((14, 3, 16, 5), 'tan'); i.arc((1, 4, 18, 18), 20, 160, 'wood_dk', 1)
i.ell((6, 10, 13, 16), 'tan'); i.ell((8, 10, 11, 12), 'outline'); i.px([(6, 8), (13, 8)], 'outline'); i.line([(9, 13), (9, 14)], 'wood_dk'); i.px([(5, 6), (4, 7)], 'wood_lt'); reg('druid_3', 'bear form', i.done())
i = Ic(); i.rect((1, 14, 18, 18), 'wood_dk'); i.rect((1, 14, 18, 14), 'grass'); i.px([(3, 16), (9, 17), (15, 16)], 'bark')
i.line([(4, 15), (3, 10), (5, 6), (8, 5)], 'wood_lt', 2); i.line([(10, 15), (10, 8), (12, 4), (10, 2)], 'wood_lt', 2); i.line([(15, 15), (16, 10), (14, 7)], 'wood_lt', 2); i.px([(8, 5), (10, 2), (14, 7)], 'tan')
reg('druid_4', 'entangling roots', i.done())

# ---- skill 5 (v5: 5 skills per class, several passive) ----
KIND = {}
i = Ic(); i.poly([(3, 2), (16, 2), (16, 10), (9.5, 17), (3, 10)], 'blue'); i.poly([(9.5, 2), (16, 2), (16, 10), (9.5, 17)], 'blue_dk'); i.ell((5, 4, 14, 13), 'red', 2); i.rect((9, 3, 10, 14), 'red'); i.rect((4, 8, 15, 9), 'red'); i.clear((9, 7, 10, 10)); i.px([(9, 8), (10, 8), (9, 9), (10, 9)], 'cream')
reg('paladin_5', 'guardian (aggro passive: target reticle on shield)', i.done()); KIND['paladin_5'] = 'passive'
i = Ic(); i.poly([(8, 1), (14, 9), (15, 13), (13, 17), (8, 18), (4, 16), (3, 12), (4, 8)], 'sky'); i.poly([(9.5, 3), (14, 9), (15, 13), (13, 17), (9.5, 18)], 'blue'); i.px([(6, 9), (5, 11), (5, 12)], 'sky_lt')
i.poly([(9.5, 6), (13, 10), (11, 10), (11, 15), (8, 15), (8, 10), (6, 10)], 'white'); reg('wizard_5', 'mana flow (mana-regen passive: drop + up arrow)', i.done()); KIND['wizard_5'] = 'passive'
i = Ic(); i.poly([(1, 9.5), (5, 5), (9.5, 4), (14, 5), (18, 9.5), (14, 14), (9.5, 15), (5, 14)], 'white'); i.ell((6, 6, 13, 13), 'leaf'); i.ell((8, 8, 11, 11), 'outline'); i.px([(8, 7)], 'lime'); i.line([(1, 9), (4, 6)], 'mist'); i.line([(9, 1), (10, 1)], 'amber'); i.px([(9, 18), (10, 18)], 'amber')
reg('ranger_5', 'keen eye (accuracy/crit passive)', i.done()); KIND['ranger_5'] = 'passive'
i = Ic(); i.line([(2, 2), (8, 8)], 'wood_lt', 2); i.line([(17, 2), (11, 8)], 'wood_lt', 2); i.px([(2, 2), (17, 2)], 'cream'); i.ell((3, 7, 16, 18), 'red'); i.ell((3, 7, 16, 11), 'sand'); i.ell((4, 8, 15, 10), 'parchment')
for x in (5, 9, 13): i.line([(x, 12), (x + 2, 16)], 'gold')
reg('bard_5', 'war drum (active: party haste)', i.done()); KIND['bard_5'] = 'active'
i = Ic(); i.ell((4, 1, 15, 5), 'gold', 1); i.poly([(9.5, 18), (2, 10), (2, 7), (4, 5), (7, 5), (9.5, 8), (12, 5), (15, 5), (17, 7), (17, 10)], 'lime'); i.poly([(9.5, 18), (9.5, 8), (12, 5), (15, 5), (17, 7), (17, 10)], 'grass'); i.px([(4, 7), (5, 7)], 'cream')
reg('cleric_5', 'blessed (regen passive: haloed heart)', i.done()); KIND['cleric_5'] = 'passive'
i = Ic(); i.ell((2, 9, 13, 17), 'amber'); i.ell((2, 8, 13, 15), 'gold'); i.ell((5, 10, 10, 13), 'amber'); i.ell((7, 3, 18, 11), 'amber'); i.ell((7, 2, 18, 9), 'gold'); i.ell((10, 4, 15, 7), 'amber'); i.px([(9, 3), (4, 9)], 'cream'); i.px([(3, 3), (2, 4), (4, 4), (3, 5)], 'white')
reg('rogue_5', 'pickpocket (active: steal gold)', i.done()); KIND['rogue_5'] = 'active'
i = Ic(); i.ell((2, 2, 17, 17), 'coral'); i.arc((2, 2, 17, 17), 300, 120, 'red', 2); i.line([(5, 6), (8, 8)], 'outline', 2); i.line([(14, 6), (11, 8)], 'outline', 2); i.ell((6, 10, 13, 16), 'outline'); i.rect((7, 11, 12, 11), 'white'); i.rect((8, 14, 11, 15), 'red_dk')
reg('barbarian_5', 'provoke (taunt/aggro passive: shouting face)', i.done()); KIND['barbarian_5'] = 'passive'
i = Ic(); i.rect((2, 14, 17, 18), 'wood_dk'); i.rect((2, 14, 17, 14), 'wood'); i.line([(9, 14), (9, 7)], 'leaf', 2); i.poly([(9, 9), (3, 4), (2, 7), (5, 10)], 'grass'); i.poly([(10, 8), (16, 3), (17, 6), (13, 9)], 'lime'); i.line([(4, 6), (8, 9)], 'leaf_dk'); i.line([(15, 5), (11, 8)], 'grass')
i.px([(4, 1), (15, 11), (3, 11)], 'cream'); reg('druid_5', 'regrowth (passive: sprout, heal over time)', i.done()); KIND['druid_5'] = 'passive'
for k_ in ICONS: KIND.setdefault(k_, 'active')

CLS = ['paladin', 'wizard', 'ranger', 'bard', 'cleric', 'rogue', 'barbarian', 'druid']
for k, L in ICONS.items():
    save(img(L), f'ui/skills/{k}.png')
    META[f'ui/skills/{k}.png'] = dict(size=[20, 20], anchor=[10, 10], motif=MOTIF[k], kind=KIND[k], slot_frame='ui/skills/skill_slot_passive.png' if KIND[k] == 'passive' else 'ui/skills/skill_slot.png', cls=k.split('_')[0], slot=int(k.split('_')[1]),
        notes='placeholder name; map to docs/CLASSES.md later. Draw centred in a 32x32 slot/button at offset (6,6).')
# slot frames 32x32
def slot(rim, rim_hi, inner):
    L = layer(32, 32); paint(L, rect(32, 32, 0, 0, 31, 31) & ~(rect(32, 32, 0, 0, 0, 0) | rect(32, 32, 31, 0, 31, 0) | rect(32, 32, 0, 31, 0, 31) | rect(32, 32, 31, 31, 31, 31)), C['outline'])
    paint(L, rect(32, 32, 1, 1, 30, 30), C[rim]); paint(L, rect(32, 32, 1, 1, 30, 1) | rect(32, 32, 1, 1, 1, 30), C[rim_hi])
    paint(L, rect(32, 32, 3, 3, 28, 28), C['outline']); paint(L, rect(32, 32, 4, 4, 27, 27), C[inner]); paint(L, rect(32, 32, 4, 27, 27, 27) | rect(32, 32, 27, 4, 27, 27), C['outline'] if inner == 'ink' else C['slate'])
    return L
for nm, args in (('skill_slot', ('wood', 'wood_lt', 'ink')), ('skill_slot_active', ('gold', 'cream', 'ink')), ('skill_slot_locked', ('gray', 'silver', 'slate'))):
    save(img(slot(*args)), f'ui/skills/{nm}.png'); META[f'ui/skills/{nm}.png'] = dict(size=[32, 32], icon_offset=[6, 6], notes='32x32 skill slot, same footprint as ui/portrait/btn32_*. Icon area 24x24 inside (4..27).')
def oct_slot(rim, rim_hi, rim_dk, inner):
    xs_, ys_ = np.mgrid[0:32, 0:32][1], np.mgrid[0:32, 0:32][0]
    def octm(r, c=9):
        a = np.abs(xs_ - 15.5); b = np.abs(ys_ - 15.5); return (a <= r) & (b <= r) & (a + b <= r + c * r / 16)
    L = layer(32, 32); o = octm(16, 9.5); paint(L, o, C['outline']); rm = octm(15, 9); paint(L, rm, C[rim])
    paint(L, rm & ~sh(rm, 1, 1), C[rim_hi]); paint(L, rm & ~sh(rm, -1, -1), C[rim_dk])
    inn = octm(12.5, 7.5); paint(L, octm(13.5, 8), C['outline']); paint(L, inn, C[inner]); paint(L, inn & ~sh(inn, -1, -1), C['outline'] if inner == 'ink' else C['slate'])
    for (x, y) in ((15, 1), (16, 1), (15, 30), (16, 30), (1, 15), (1, 16), (30, 15), (30, 16)): L[y, x] = C[rim_hi] + (255,)   # rivets
    return L
for nm, args in (('skill_slot_passive', ('gold', 'cream', 'amber', 'ink')), ('skill_slot_passive_locked', ('gray', 'silver', 'slate', 'slate'))):
    save(img(oct_slot(*args)), f'ui/skills/{nm}.png')
    META[f'ui/skills/{nm}.png'] = dict(size=[32, 32], icon_offset=[6, 6], notes='PASSIVE slot: octagon with gold rim (reads differently from the square active slot). Not pressable, so there is no active/pressed state; dim with _locked while unlearned.')
cd = layer(24, 24); cd[::2, ::2] = C['outline'] + (255,); cd[1::2, 1::2] = C['outline'] + (255,)
save(img(cd), 'ui/skills/skill_cooldown_mask.png'); META['ui/skills/skill_cooldown_mask.png'] = dict(size=[24, 24], offset_in_slot=[4, 4], notes='50% checker dither; crop from the top by remaining-cooldown fraction and draw over the icon (binary alpha keeps the pixel look).')
# skill sheet 8 cols (class) x 5 rows (skill 1..5); passives in the octagon slot + "P" tag
CWd, CHt = 40, 36; SW = 8 * CWd + 26; SH = 12 + 5 * CHt + 14
S = Image.new('RGBA', (SW, SH), C['ink'] + (255,))
for ci, c in enumerate(CLS):
    x0 = 24 + ci * CWd; lab = c.upper(); text(S, x0 + 16 - text_w(lab) // 2, 3, lab, C['gold'])
    for r in range(5):
        k = f'{c}_{r+1}'; y0 = 12 + r * CHt
        fr = img(oct_slot('gold', 'cream', 'amber', 'ink')) if KIND[k] == 'passive' else img(slot('wood', 'wood_lt', 'ink'))
        fr.alpha_composite(img(ICONS[k]), (6, 6)); S.alpha_composite(fr, (x0, y0))
        if KIND[k] == 'passive': S.paste(C['plum'] + (255,), (x0 + 25, y0 + 24, x0 + 32, y0 + 32)); text(S, x0 + 27, y0 + 25, 'P', C['cream'])
for r in range(5): text(S, 6, 12 + r * CHt + 13, str(r + 1), C['cream'])
ly = 12 + 5 * CHt + 3; S.paste(C['wood'] + (255,), (24, ly, 31, ly + 7)); text(S, 34, ly, 'ACTIVE (SQUARE SLOT)', C['mist'])
S.paste(C['plum'] + (255,), (150, ly, 157, ly + 8)); text(S, 152, ly + 1, 'P', C['cream']); text(S, 160, ly, 'PASSIVE (OCTAGON SLOT)', C['mist'])
save(S, 'ui/skills/skill_sheet.png'); save(S.resize((SW * 3, SH * 3), Image.NEAREST), 'ui/skills/skill_sheet_3x.png')
META['ui/skills/skill_sheet.png'] = dict(notes='8 columns (class) x 5 rows (skill 1..5). Active skills in skill_slot.png, passives in skill_slot_passive.png with a P tag. QA/reference sheet, not a runtime asset.')
META['ui/skills/skill_sheet_3x.png'] = dict(notes='3x nearest of skill_sheet.png.')


# ======================= v6: per-character action bar assets =======================
PWP = 'ui/portrait/'
# bar panel 270x50: outline, 2px wood rim with light/dark bevel, ink interior, studs
def bar_panel(Wd=270, Ht=50):
    L = layer(Wd, Ht); paint(L, rect(Wd, Ht, 0, 0, Wd - 1, Ht - 1), C['outline'])
    paint(L, rect(Wd, Ht, 1, 1, Wd - 2, Ht - 2), C['wood']); paint(L, rect(Wd, Ht, 1, 1, Wd - 2, 1), C['wood_lt']); paint(L, rect(Wd, Ht, 1, Ht - 2, Wd - 2, Ht - 2), C['wood_dk'])
    paint(L, rect(Wd, Ht, 2, 2, Wd - 3, Ht - 3), C['outline']); paint(L, rect(Wd, Ht, 3, 3, Wd - 4, Ht - 4), C['ink'])
    paint(L, rect(Wd, Ht, 3, Ht - 13, Wd - 4, Ht - 13), C['slate'])          # faint shelf line above the cost-badge row
    for cx in (0, Wd - 4):
        for cy in (0, Ht - 4):
            paint(L, rect(Wd, Ht, cx, cy, cx + 3, cy + 3), C['outline']); paint(L, rect(Wd, Ht, cx + 1, cy + 1, cx + 2, cy + 2), C['tan'])
    return L
BAR_SLOTS = dict(attack=[4, 4], cover=[37, 4], divider_x=71, skills=[[75 + k * 33, 4] for k in range(5)], item=[245, 4], run=[245, 26], cost_badges=[[75 + k * 33 + 8, 38] for k in range(5)])
Lb = bar_panel(); paint(Lb, rect(270, 50, 71, 5, 71, 44), C['amber']); paint(Lb, rect(270, 50, 72, 5, 72, 44), C['wood_dk'])
save(img(Lb), PWP + 'action_bar_v2.png')
META[PWP + 'action_bar_v2.png'] = dict(size=[270, 50], anchor=[0, 0], slots=BAR_SLOTS, slot_size=32, mini_size=20,
    notes='v6 per-character action bar (replaces ui/portrait/action_bar.png). Slot top-lefts in bar-local px: attack/cover default abilities (32x32), gold divider at x71, 5 class skills (32x32, step 33), Item/Run mini buttons (20x20) stacked at the right, 16x7 MP cost badges centred under each active skill (y38).')
# default ability slots: square skill_slot style + the existing attack/cover icons
for n in ('attack', 'cover'):
    ic = np.array(Image.open(W_ + f'icon_{n}.png').convert('RGBA'))
    for sfx, args in (('', ('wood', 'wood_lt', 'ink')), ('_active', ('gold', 'cream', 'ink'))):
        Lx = slot(*args); over(Lx[6:26, 6:26], ic); save(img(Lx), PWP + f'ability_{n}{sfx}.png')
        META[PWP + f'ability_{n}{sfx}.png'] = dict(size=[32, 32], notes=('selected state. ' if sfx else '') + f'default ability "{n}" in the skill-slot style (always available for every class).')
# mini buttons 20x20 with 12x12 icons
def mini(icon_fn, rim, hi):
    L = layer(20, 20); paint(L, rect(20, 20, 0, 0, 19, 19) & ~(rect(20, 20, 0, 0, 0, 0) | rect(20, 20, 19, 0, 19, 0) | rect(20, 20, 0, 19, 0, 19) | rect(20, 20, 19, 19, 19, 19)), C['outline'])
    paint(L, rect(20, 20, 1, 1, 18, 18), C[rim]); paint(L, rect(20, 20, 1, 1, 18, 1) | rect(20, 20, 1, 1, 1, 18), C[hi]); paint(L, rect(20, 20, 2, 2, 17, 17), C['outline']); paint(L, rect(20, 20, 3, 3, 16, 16), C['ink'])
    ic = Ic(14); icon_fn(ic); over(L[3:17, 3:17], ic.done()); return L
def ic_item(i): i.rect((6, 1, 8, 2), 'wood'); i.rect((6, 3, 8, 4), 'mist'); i.ell((2, 4, 12, 13), 'mist'); i.ell((3, 7, 11, 12), 'red'); i.rect((3, 7, 11, 8), 'coral'); i.px([(4, 6)], 'white')
def ic_run(i): i.poly([(2, 2), (7, 2), (7, 12), (2, 12)], 'wood'); i.rect((3, 3, 6, 11), 'wood_dk'); i.px([(6, 7)], 'gold'); i.poly([(8, 5), (10, 5), (10, 3), (13, 7), (10, 11), (10, 9), (8, 9)], 'lime')
for n, fn in (('item', ic_item), ('run', ic_run)):
    for sfx, args in (('', ('wood', 'wood_lt')), ('_active', ('gold', 'cream'))):
        save(img(mini(fn, *args)), PWP + f'mini_{n}{sfx}.png'); META[PWP + f'mini_{n}{sfx}.png'] = dict(size=[20, 20], icon_rect=[3, 3, 14, 14], notes=('pressed/selected. ' if sfx else '') + ('utility: open inventory (potion).' if n == 'item' else 'utility: flee (door + arrow).'))
# tiny 3x5 digits + MP cost badge 16x7
D35 = {'0': ['###', '# #', '# #', '# #', '###'], '1': [' # ', '## ', ' # ', ' # ', '###'], '2': ['###', '  #', '###', '#  ', '###'], '3': ['###', '  #', ' ##', '  #', '###'], '4': ['# #', '# #', '###', '  #', '  #'],
       '5': ['###', '#  ', '###', '  #', '###'], '6': ['###', '#  ', '###', '# #', '###'], '7': ['###', '  #', ' # ', ' # ', ' # '], '8': ['###', '# #', '###', '# #', '###'], '9': ['###', '# #', '###', '  #', '###']}
def d35(L, x, y, ch, col):
    for r, row in enumerate(D35[ch]):
        for c_, v in enumerate(row):
            if v == '#': L[y + r, x + c_] = C[col] + (255,)
dg = layer(40, 5)
for k in range(10): d35(dg, k * 4, 0, str(k), 'white')
save(img(dg), PWP + 'digits_3x5.png'); META[PWP + 'digits_3x5.png'] = dict(frames=10, frame_size=[4, 5], notes="tiny white digits 0-9 (3x5 glyph + 1px advance) for cost badges / cooldown counters. Tint by modulate if needed.")
def cost_badge(n=None):
    L = layer(16, 7); m = rect(16, 7, 0, 0, 15, 6) & ~(rect(16, 7, 0, 0, 0, 0) | rect(16, 7, 15, 0, 15, 0) | rect(16, 7, 0, 6, 0, 6) | rect(16, 7, 15, 6, 15, 6))
    paint(L, m, C['outline']); paint(L, rect(16, 7, 1, 1, 14, 5), C['blue_dk']); paint(L, rect(16, 7, 1, 1, 14, 1), C['blue'])
    paint(L, pts(16, 7, [(3, 1), (3, 2), (2, 3), (3, 3), (4, 3), (2, 4), (3, 4), (4, 4), (3, 5)]), C['sky']); L[3, 2] = C['sky_lt'] + (255,); L[4, 4] = C['blue'] + (255,)
    if n is not None:
        s_ = str(n); x0 = 7 if len(s_) == 1 else 6
        for j, ch in enumerate(s_): d35(L, x0 + j * 4, 1, ch, 'white')
    return L
save(img(cost_badge()), PWP + 'cost_badge.png'); META[PWP + 'cost_badge.png'] = dict(size=[16, 7], digit_origin=[7, 1], notes='MP cost badge (blue pill + drop). Draw digits_3x5 at digit_origin (x 6 for 2 digits). Centre under each ACTIVE skill slot (slot x + 8, bar y 38). Passives get no badge.')
cb = layer(160, 7)
for k in range(10): over(cb[:, k * 16:k * 16 + 16], cost_badge(k))
save(img(cb), PWP + 'cost_badge_0_9.png'); META[PWP + 'cost_badge_0_9.png'] = dict(frames=10, frame_size=[16, 7], notes='pre-rendered cost badges for MP 0..9 (frame i = cost i).')
# name tab 64x10 (gold, sits on top of the bar's left edge, open at the bottom)
def name_tab(Wd=64, Ht=10):
    L = layer(Wd, Ht); m = rect(Wd, Ht, 0, 0, Wd - 1, Ht - 1) & ~(rect(Wd, Ht, 0, 0, 1, 0) | rect(Wd, Ht, 0, 1, 0, 1) | rect(Wd, Ht, Wd - 2, 0, Wd - 1, 0) | rect(Wd, Ht, Wd - 1, 1, Wd - 1, 1))
    paint(L, m, C['outline']); inn = rect(Wd, Ht, 1, 1, Wd - 2, Ht - 1) & ~(rect(Wd, Ht, 1, 1, 1, 1) | rect(Wd, Ht, Wd - 2, 1, Wd - 2, 1))
    paint(L, inn, C['gold']); paint(L, e_top(inn), C['cream']); paint(L, e_right(inn) & ~e_top(inn), C['amber'])
    return L
save(img(name_tab()), PWP + 'name_tab.png'); META[PWP + 'name_tab.png'] = dict(size=[64, 10], text_origin=[5, 2], text_color='#120c18', notes='active-character nameplate tab: draw at bar top-left (x 4, bar_y - 10); class/hero name in the pixel font at text_origin (max ~13 chars). Gold = same highlight as hp_mp_card_compact_active.')
# passive dim overlay (25% ink checker) + lock glyph for locked skills
dm = layer(24, 24); dm[::2, ::2] = C['ink'] + (255,)
save(img(dm), PWP + 'passive_dim_mask.png'); META[PWP + 'passive_dim_mask.png'] = dict(size=[24, 24], offset_in_slot=[4, 4], notes='25% ink dither drawn over a PASSIVE icon so it reads as non-pressable (binary alpha).')
lk = Ic(10); lk.arc((2, 0, 7, 6), 180, 360, 'silver', 1); lk.rect((1, 4, 8, 9), 'gold'); lk.rect((1, 8, 8, 9), 'amber'); lk.px([(4, 6), (5, 6), (4, 7)], 'outline')
save(img(lk.done()), PWP + 'lock_icon.png'); META[PWP + 'lock_icon.png'] = dict(size=[10, 10], notes='locked-skill padlock, draw at slot [11,11] over a dimmed icon in skill_slot_locked.')
BAR_COSTS = {'paladin': [2, 3, 4, 1, None], 'wizard': [3, 4, 5, 3, None], 'rogue': [2, 3, 2, 4, 1], 'cleric': [3, 2, 6, 4, None], 'ranger': [1, 3, 2, 2, None], 'bard': [1, 2, 3, 2, 3], 'barbarian': [0, 2, 3, 2, None], 'druid': [2, 3, 4, 3, None]}
for c_ in BAR_COSTS: BAR_COSTS[c_] = [None if KIND[f'{c_}_{k+1}'] == 'passive' else (v if v is not None else 2) for k, v in enumerate(BAR_COSTS[c_])]


# ======================= v7: seat-mounted HP/MP bars =======================
SBW, SBH = 44, 10         # v7b frame: 1px outline | HP 4px | 1px outline | MP 3px | 1px outline
def seat_frame(active=False):
    L = layer(SBW, SBH); paint(L, rect(SBW, SBH, 0, 0, SBW - 1, SBH - 1), C['outline'])
    paint(L, rect(SBW, SBH, 1, 1, SBW - 2, 4), C['blood']); paint(L, rect(SBW, SBH, 1, 6, SBW - 2, 8), C['navy'])
    if active:
        A = layer(SBW + 2, SBH + 2); paint(A, rect(SBW + 2, SBH + 2, 0, 0, SBW + 1, SBH + 1), C['outline']); A[1:-1, 1:-1] = L
        paint(A, rect(SBW + 2, SBH + 2, 1, 1, SBW, 1) | rect(SBW + 2, SBH + 2, 1, SBH, SBW, SBH) | rect(SBW + 2, SBH + 2, 1, 1, 1, SBH) | rect(SBW + 2, SBH + 2, SBW, 1, SBW, SBH), C['gold'])
        paint(A, rect(SBW + 2, SBH + 2, 2, 6, SBW - 1, 6), C['outline']); return A
    return L
save(img(seat_frame()), PWP + 'seat_bars_frame.png')
META[PWP + 'seat_bars_frame.png'] = dict(size=[SBW, SBH], anchor=[22, 0], hp_fill_rect=[1, 1, 42, 4], mp_fill_rect=[1, 6, 42, 3],
    notes='v7 seat-mounted HP/MP bars: #120c18 outline frame with dark empty tracks (HP #3e1016, MP #161c40). Anchor = top-centre; place at (seat_x, seat_feet_y - 11) so it overlaps the chair seat front + lower rails. Fill with seat_bar_hp/mp (crop by %) or stretch the 1px tiles.')
save(img(seat_frame(True)), PWP + 'seat_bars_frame_active.png')
META[PWP + 'seat_bars_frame_active.png'] = dict(size=[SBW + 2, SBH + 2], anchor=[23, 1], hp_fill_rect=[2, 2, 42, 4], mp_fill_rect=[2, 7, 42, 3],
    notes='ACTIVE seat variant: gold inner ring + dark outer outline (1px larger each side). Same anchor point as the normal frame (top-centre of the inner frame at [23,1]).')
hpf = layer(42, 4); paint(hpf, rect(42, 4, 0, 0, 41, 3), C['coral']); paint(hpf, rect(42, 4, 0, 3, 41, 3), C['red']); paint(hpf, rect(42, 4, 0, 0, 41, 0), C['amber'] if False else C['coral'])
mpf = layer(42, 3); paint(mpf, rect(42, 3, 0, 0, 41, 1), C['sky']); paint(mpf, rect(42, 3, 0, 2, 41, 2), C['blue'])
save(img(hpf), PWP + 'seat_bar_hp.png'); save(img(mpf), PWP + 'seat_bar_mp.png')
save(img(hpf[:, :1]), PWP + 'seat_bar_hp_tile.png'); save(img(mpf[:, :1]), PWP + 'seat_bar_mp_tile.png')
META[PWP + 'seat_bar_hp.png'] = dict(size=[42, 4], notes='HP fill (#ec5a44, #c02c2c bottom shade). Crop width = round(42 * hp%).')
META[PWP + 'seat_bar_mp.png'] = dict(size=[42, 3], notes='MP fill (#4c9ce8 over #3466cc). Crop width = round(42 * mp%).')
META[PWP + 'seat_bar_hp_tile.png'] = dict(size=[1, 4], notes='1px HP fill column; stretch horizontally (nearest) instead of cropping the full strip.')
META[PWP + 'seat_bar_mp_tile.png'] = dict(size=[1, 3], notes='1px MP fill column; stretch horizontally.')
fl = [hpf.copy(), hpf.copy()]; paint(fl[1], rect(42, 4, 0, 0, 41, 3), C['cream']); paint(fl[1], rect(42, 4, 0, 3, 41, 3), C['amber'])
save(img(np.concatenate(fl, axis=1)), PWP + 'seat_bar_hp_lowflash.png')
META[PWP + 'seat_bar_hp_lowflash.png'] = dict(frames=2, frame_size=[42, 4], fps=4, loop=True, notes='low-HP (<25%) flash: frame 0 normal red, frame 1 cream/amber. Crop both frames to the same fill width.')


# outlined HP digits: 3x5 cream glyph + 1px #120c18 outline -> 5x7 cells, advance 4 (outlines overlap)
do = layer(50, 7)
for k in range(10):
    g = layer(5, 7); d35(g, 1, 1, str(k), 'white'); m_ = g[..., 3] > 0
    paint(g, m_, C['cream']); paint(g, m_ & (np.arange(7)[:, None] == 5), C['sand']); outline(g, diag=True); do[:, k * 5:k * 5 + 5] = g
save(img(do), PWP + 'digits_3x5_outlined.png')
META[PWP + 'digits_3x5_outlined.png'] = dict(frames=10, frame_size=[5, 7], advance=4, notes='HP-number digits: cream 3x5 glyph (sand bottom row) with a 1px #120c18 outline (diagonals included) so it reads on any robe incl. white. Draw successive digits 4px apart (outline columns overlap).')
# ======================= v8: skill card popup assets =======================
from pal import text as ptext
# 9-slice notebook panel 48x48: margins L14 T10 R6 B6 (spiral holes on top, red margin line on the left, ruled lines every 8px)
KL, KT, KR, KB = 14, 10, 6, 6
Pn = layer(48, 48); full = rect(48, 48, 0, 0, 47, 47) & ~(rect(48, 48, 0, 0, 0, 0) | rect(48, 48, 47, 0, 47, 0) | rect(48, 48, 0, 47, 0, 47) | rect(48, 48, 47, 47, 47, 47))
paint(Pn, full, C['outline']); inn = rect(48, 48, 1, 1, 46, 46); paint(Pn, inn, C['parchment'])
paint(Pn, rect(48, 48, 1, 45, 46, 46) | rect(48, 48, 45, 1, 46, 46), C['sand'])            # bottom/right paper shade
paint(Pn, rect(48, 48, 1, 1, 44, 1), C['white'])                                          # lit top edge
for y in range(KT + 7, 44, 8): paint(Pn, rect(48, 48, KL, y, 44, y), C['sky_lt'])        # ruled lines (tile period 8)
paint(Pn, rect(48, 48, 11, 1, 11, 44), C['coral'])                                        # margin line
for x in range(3, 46, 8):                                                                 # spiral holes (period 8)
    paint(Pn, rect(48, 48, x + 1, 3, x + 3, 6), C['outline']); paint(Pn, rect(48, 48, x + 2, 2, x + 2, 2), C['silver']); paint(Pn, rect(48, 48, x + 2, 7, x + 2, 7), C['sand'])
save(img(Pn), PWP + 'skill_card_panel.png')
META[PWP + 'skill_card_panel.png'] = dict(size=[48, 48], nine_slice_margins=dict(left=KL, top=KT, right=KR, bottom=KB), tile_period=8,
    notes='notebook-page 9-slice for the skill card: dark outline, parchment, spiral holes along the top edge, red margin line on the left, faint ruled lines. TILE (not stretch) the edges/centre so holes and ruling keep an 8px rhythm; pick widths/heights = 48 + 8k for a seamless look.')
# tail (points down at the tapped slot); top 2 rows overlap the card's bottom edge
Tl = layer(13, 8)
for y in range(8):
    hw = 6 - y
    if hw < 0: break
    paint(Tl, rect(13, 8, 6 - hw, y, 6 + hw, y), C['outline'])
    if hw >= 1: paint(Tl, rect(13, 8, 6 - hw + 1, y, 6 + hw - 1, y), C['sand'] if y >= 2 else C['parchment'])
paint(Tl, rect(13, 8, 1, 0, 11, 1), C['sand']); paint(Tl, rect(13, 8, 1, 0, 11, 0), C['sand'])
save(img(Tl), PWP + 'skill_card_tail.png')
META[PWP + 'skill_card_tail.png'] = dict(size=[13, 8], anchor=[6, 7], overlap_rows=2, notes='pointer: tip (anchor) aims at the tapped slot centre; place so rows 0-1 cover the card bottom edge (tail y = card_bottom - 2).')
# prompt strip 3-slice 24x14 (caps 5px): ready (2-frame pulse), passive, disabled (no MP), cooldown
def strip3(band, edge, edge2):
    L = layer(24, 14); m = rect(24, 14, 0, 0, 23, 13) & ~(rect(24, 14, 0, 0, 0, 0) | rect(24, 14, 23, 0, 23, 0) | rect(24, 14, 0, 13, 0, 13) | rect(24, 14, 23, 13, 23, 13))
    paint(L, m, C['outline']); paint(L, rect(24, 14, 1, 1, 22, 12), C[band]); paint(L, rect(24, 14, 1, 1, 22, 1), C[edge]); paint(L, rect(24, 14, 1, 12, 22, 12), C[edge2])
    for x in (2, 21):
        for y in range(4, 11, 3): L[y, x] = C[edge] + (255,)
    return L
STRIPS = dict(ready=[strip3('ink', 'gold', 'amber'), strip3('ink', 'cream', 'gold')], passive=[strip3('plum', 'violet', 'plum_dk')], nomp=[strip3('blood', 'red', 'red_dk')], cooldown=[strip3('slate', 'gray', 'ink')])
STRIP_TXT = dict(ready=('TAP AGAIN TO CAST', ['gold', 'cream']), passive=('PASSIVE: ALWAYS ACTIVE', ['pink']), nomp=('NOT ENOUGH MP', ['coral']), cooldown=('ON COOLDOWN: {n}', ['mist']))
for k_, frs in STRIPS.items():
    save(img(np.concatenate(frs, axis=1)), PWP + f'skill_card_strip_{k_}.png')
    META[PWP + f'skill_card_strip_{k_}.png'] = dict(frames=len(frs), frame_size=[24, 14], three_slice=dict(left=5, right=5), text_y=5, text=STRIP_TXT[k_][0], text_colors=['#' + pal.HEX[pal.NAMES.index(c_)] for c_ in STRIP_TXT[k_][1]],
        fps=3 if len(frs) > 1 else None, notes='prompt strip: 3-slice (caps 5px, tile the middle). Text centred at y 5 in the pack 3x5 font.' + (' 2-frame pulse: swap frame + text colour gold/cream at 3 fps.' if len(frs) > 1 else ''))
# armed slot glow 36x36 x2 frames (drawn at slot - 2px), distinct from the gold selected frame
def armed(f):
    L = layer(36, 36); o = rect(36, 36, 0, 0, 35, 35) & ~rect(36, 36, 2, 2, 33, 33)
    c1, c2 = (('cream', 'gold') if f else ('gold', 'amber'))
    paint(L, o, C[c2]); paint(L, rect(36, 36, 0, 0, 35, 35) & ~rect(36, 36, 1, 1, 34, 34), C[c1])
    for (x, y) in ((0, 0), (35, 0), (0, 35), (35, 35)): L[y, x] = 0
    sp = [(17, 0), (18, 0), (0, 17), (0, 18), (35, 17), (35, 18), (17, 35), (18, 35)]
    for (x, y) in sp: L[y, x] = C['white'] + (255,)
    if f:
        for (x, y) in ((4, 0), (31, 0), (0, 4), (0, 31), (35, 4), (35, 31), (4, 35), (31, 35)): L[y, x] = C['white'] + (255,)
    return L
save(img(np.concatenate([armed(0), armed(1)], axis=1)), PWP + 'skill_slot_armed.png')
META[PWP + 'skill_slot_armed.png'] = dict(frames=2, frame_size=[36, 36], fps=4, offset_from_slot=[-2, -2], loop=True, notes='ARMED state (skill card open, next tap casts): 2px pulsing gold/cream glow ring drawn around the 32px slot (outside the frame). Distinct from skill_slot_active (selected).')
dmb = layer(32, 32); dmb[::2, ::2] = C['outline'] + (255,); dmb[1::2, 1::2] = C['outline'] + (255,)
save(img(dmb), PWP + 'bar_dim_mask.png'); META[PWP + 'bar_dim_mask.png'] = dict(size=[32, 32], notes='50% dither drawn over every OTHER bar slot while a skill card is open (optional focus dim).')
# 2x icon frames 44x44 (square active / octagon passive)
def big_frame(passive):
    if passive:
        L = oct_slot('gold', 'cream', 'amber', 'ink'); return np.array(Image.fromarray(L).resize((44, 44), Image.NEAREST)) if False else None
    L = layer(44, 44); paint(L, rect(44, 44, 0, 0, 43, 43) & ~(rect(44, 44, 0, 0, 0, 0) | rect(44, 44, 43, 0, 43, 0) | rect(44, 44, 0, 43, 0, 43) | rect(44, 44, 43, 43, 43, 43)), C['outline'])
    paint(L, rect(44, 44, 1, 1, 42, 42), C['wood']); paint(L, rect(44, 44, 1, 1, 42, 1) | rect(44, 44, 1, 1, 1, 42), C['wood_lt']); paint(L, rect(44, 44, 1, 42, 42, 42) | rect(44, 44, 42, 1, 42, 42), C['wood_dk'])
    paint(L, rect(44, 44, 2, 2, 41, 41), C['outline']); paint(L, rect(44, 44, 3, 3, 40, 40), C['ink']); return L
def big_oct():
    ys_, xs_ = np.mgrid[0:44, 0:44]
    def octm(r, c):
        a = np.abs(xs_ - 21.5); b = np.abs(ys_ - 21.5); return (a <= r) & (b <= r) & (a + b <= r + c)
    L = layer(44, 44); paint(L, octm(22, 12), C['outline']); rm = octm(21, 11.5); paint(L, rm, C['gold']); paint(L, rm & ~sh(rm, 1, 1), C['cream']); paint(L, rm & ~sh(rm, -1, -1), C['amber'])
    paint(L, octm(19, 10.5), C['outline']); paint(L, octm(18, 10), C['ink']); return L
save(img(big_frame(False)), PWP + 'skill_card_icon_frame.png'); save(img(big_oct()), PWP + 'skill_card_icon_frame_passive.png')
for n_ in ('skill_card_icon_frame', 'skill_card_icon_frame_passive'):
    META[PWP + f'{n_}.png'] = dict(size=[44, 44], icon_rect=[2, 2, 40, 40], notes='holds the 20x20 skill icon at 2x (nearest) at [2,2].' + (' Octagon = passive.' if 'passive' in n_ else ''))
# tags (baked words)
def tag(word, band, edge, txt):
    w = len(word) * 4 + 5; L = img(layer(w, 9)); a = np.array(L)
    a[:, :] = 0; m = rect(w, 9, 0, 0, w - 1, 8) & ~(rect(w, 9, 0, 0, 0, 0) | rect(w, 9, w - 1, 0, w - 1, 0) | rect(w, 9, 0, 8, 0, 8) | rect(w, 9, w - 1, 8, w - 1, 8))
    paint(a, m, C['outline']); paint(a, rect(w, 9, 1, 1, w - 2, 7), C[band]); paint(a, rect(w, 9, 1, 1, w - 2, 1), C[edge])
    im_ = Image.fromarray(a).copy(); ptext(im_, 3, 2, word, C[txt]); return im_
save(tag('ACTIVE', 'leaf_dk', 'leaf', 'cream'), PWP + 'skill_tag_active.png'); save(tag('PASSIVE', 'plum', 'violet', 'cream'), PWP + 'skill_tag_passive.png')
for n_ in ('active', 'passive'): META[PWP + f'skill_tag_{n_}.png'] = dict(notes=f'{n_.upper()} tag pill (word baked in the pack 3x5 font), top-right of the card.')
# tiny info icons 9x7
def ti(fn):
    i_ = Ic(9); fn(i_); a_ = i_.done(); return a_[1:8, :]
tic = {
 'target_enemy': lambda i: (i.ell((1, 0, 7, 6), 'red', 1), i.px([(4, 3)], 'red'), i.px([(4, 0), (4, 6), (1, 3), (7, 3)], 'coral')),
 'target_all_enemies': lambda i: (i.ell((0, 1, 4, 5), 'red', 1), i.ell((4, 1, 8, 5), 'red', 1), i.px([(2, 3), (6, 3)], 'coral')),
 'target_ally': lambda i: (i.rect((3, 1, 5, 7), 'lime'), i.rect((1, 3, 7, 5), 'lime')),
 'target_all_allies': lambda i: (i.rect((1, 2, 2, 6), 'lime'), i.rect((0, 3, 3, 5), 'lime'), i.rect((6, 2, 7, 6), 'lime'), i.rect((5, 3, 8, 5), 'lime')),
 'target_self': lambda i: (i.ell((2, 1, 6, 5), 'gold'), i.px([(4, 3)], 'outline'), i.px([(4, 6), (4, 7)], 'gold')),
 'icon_cooldown': lambda i: (i.rect((2, 1, 6, 1), 'wood'), i.rect((2, 7, 6, 7), 'wood'), i.poly([(3, 2), (5, 2), (4, 4)], 'sand'), i.poly([(4, 4), (6, 6), (2, 6)], 'sand')),
}
for k_, fn in tic.items():
    a_ = ti(fn); save(img(a_), PWP + f'{k_}.png'); META[PWP + f'{k_}.png'] = dict(size=[9, 7], notes='tiny skill-card info icon' + (' (target type)' if 'target' in k_ else ' (cooldown turns)') + '; text starts 2px to its right.')

# ======================= FX =======================
def strip(frames):
    h, w = frames[0].shape[:2]; s = layer(w * len(frames), h)
    for k, f in enumerate(frames): s[:, k * w:(k + 1) * w] = f
    return s
def G(w, h):
    ys, xs = np.mgrid[0:h, 0:w]; return xs.astype(float), ys.astype(float)
def dith(w, h, keep, seed=0):
    """binary-alpha fade: keep fraction via ordered 4x4 bayer."""
    B = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 + 1 / 32
    xs, ys = np.mgrid[0:w, 0:h]; return (B[(ys.T + seed) % 4, (xs.T + seed) % 4] < keep)
def spark(L, cx, cy, r, core='white', arm='lime'):
    h, w = L.shape[:2]
    for d in range(-r, r + 1):
        for (x, y) in ((cx + d, cy), (cx, cy + d)):
            if 0 <= x < w and 0 <= y < h: L[y, x] = C[arm if abs(d) > 0 else core] + (255,)
    if r >= 2:
        for dx, dy in ((1, 1), (-1, -1), (1, -1), (-1, 1)):
            x, y = cx + dx, cy + dy
            if 0 <= x < w and 0 <= y < h: L[y, x] = C[arm] + (255,)
        for d in (-1, 1):
            for (x, y) in ((cx + d, cy), (cx, cy + d)):
                if 0 <= x < w and 0 <= y < h: L[y, x] = C[core] + (255,)
FX = {}
# --- slash: 48x48, 5f
w = h = 48; xs, ys = G(w, h); cx, cy = 24, 12
r = np.hypot(xs - cx, ys - cy); th = np.degrees(np.arctan2(ys - cy, xs - cx))   # arc sweeps from 0deg (right) to ~170 (left) through the bottom
frames = []
for head, tail, fade in ((70, 5, 1), (130, 8, 1), (172, 12, 1), (176, 80, 0.55), (178, 135, 0.25)):
    t = np.clip((th - tail) / max(1, head - tail), 0, 1); inarc = (th >= tail) & (th <= head)
    thick = 1 + 8 * np.sin(np.pi * t ** 1.3) ** 0.8
    band = inarc & (r <= 23) & (r >= 23 - thick)
    L = layer(w, h); paint(L, band, C['sky_lt']); paint(L, band & (r >= 23 - thick * 0.75), C['ice']); paint(L, band & (r >= 23 - thick * 0.45), C['white'])
    if fade < 1: L[~dith(w, h, fade, 1)] = 0
    frames.append(L)
FX['fx_slash'] = (frames, dict(frame_size=[48, 48], frames=5, fps=20, anchor=[24, 24], loop=False, notes='diagonal arc sweep; centre anchor on the target body (e.g. monster centre). Flip h for the other direction. Frame 2 = impact (spawn damage number / hit anim).'))
# --- fireball: 48x48, 8f (0-2 travel loop, 3-7 burst)
def fire_col(L, m, d):
    paint(L, m, C['red']); paint(L, m & (d < 0.8), C['orange']); paint(L, m & (d < 0.58), C['amber']); paint(L, m & (d < 0.36), C['gold']); paint(L, m & (d < 0.18), C['cream'])
frames = []
for f in range(3):
    L = layer(w, h); bx, by = 32, 24
    nz = np.array([[hsh(int(x) // 2, int(y) // 2, f + 3) for x in range(w)] for y in range(h)])
    trail_t = np.clip((bx - xs) / 24, 0, 1); rad = 6 * (1 - trail_t) + 0.8 + (nz - 0.5) * 2.2 * trail_t
    tr = (xs <= bx) & (xs >= bx - 24) & (np.abs(ys - by - np.sin((xs + f * 4) / 3) * 1.2 * trail_t) <= rad)
    d_tr = np.clip(np.abs(ys - by) / np.maximum(rad, 0.5) * 0.5 + trail_t * 0.7, 0, 1)
    fire_col(L, tr, d_tr + 0.2)
    ball = np.hypot(xs - bx, ys - by) / 6.5; fire_col(L, ball <= 1, ball * 0.9)
    frames.append(L)
for f, (rr, fade) in enumerate(((9, 1), (15, 1), (20, 0.85), (22, 0.5), (23, 0.22))):
    L = layer(w, h); nz = np.array([[hsh(int(x) // 3, int(y) // 3, f + 11) for x in range(w)] for y in range(h)])
    d = np.hypot(xs - 24, ys - 26) / rr + (nz - 0.5) * 0.28
    m = d <= 1
    if f >= 2: m &= d >= 0.25 * (f - 1)
    shift = 0.14 * f
    fire_col(L, m, np.clip(d + shift, 0, 1))
    if f >= 3:
        sm = m & (nz > 0.55); paint(L, sm, C['gray']); paint(L, sm & (nz > 0.8), C['silver'])
    if fade < 1: L[~dith(w, h, fade, f)] = 0
    frames.append(L)
FX['fx_fireball'] = (frames, dict(frame_size=[48, 48], frames=8, fps=14, anchor=[24, 24], loop=False,
    segments=dict(travel=dict(frames=[0, 1, 2], fps=12, loop=True, notes='projectile faces +x; tween the sprite from caster to target, rotate/flip toward the target'), burst=dict(frames=[3, 4, 5, 6, 7], fps=14, loop=False, notes='play at the target centre; frame 4 = impact')),
    notes='one strip: travel loop (0-2) + burst (3-7). Same 48x48 cell for both, anchor = ball/burst centre.'))
# --- heal sparkle: 48x64, 6f, anchor feet
w, h = 48, 64; xs, ys = G(w, h); frames = []
SP = [(int(6 + hsh(k, 1, 5) * 36), hsh(k, 2, 5), 1 + int(hsh(k, 3, 5) * 2.4)) for k in range(20)]
for f in range(6):
    L = layer(w, h)
    rg = ((xs - 24) / 22) ** 2 + ((ys - 58) / 5) ** 2
    if f <= 3:
        rin = [0.2, 0.45, 0.7, 0.9][f]; ringm = (rg <= 1) & (rg >= rin); paint(L, ringm, C['grass']); paint(L, ringm & (ys <= 58), C['lime'])
        if f == 3: L[~dith(w, h, 0.5, 2)] = 0
    for k, (x, ph, sz) in enumerate(SP):
        life = (f / 6 + ph) % 1.0; y = int(58 - life * 54)
        if life < 0.12 or life > 0.92: continue
        s = sz if life < 0.7 else max(1, sz - 1)
        spark(L, x, y, s, 'white' if k % 3 == 0 else 'cream', 'lime' if k % 2 else 'grass')
    frames.append(L)
FX['fx_heal_sparkle'] = (frames, dict(frame_size=[48, 64], frames=6, fps=10, anchor=[24, 63], loop=True, notes='anchor on the seat/monster feet (bottom-centre). Loop 1-2x. Heal colour lime #b4dc62; pair with ui/dmg_font_heal.'))
# --- buff aura: 56x72, 6f loop
w, h = 56, 72; xs, ys = G(w, h); frames = []
cols = [6, 13, 20, 28, 36, 43, 50]
for f in range(6):
    L = layer(w, h); rg = ((xs - 28) / 25) ** 2 + ((ys - 65) / 6) ** 2
    back = (rg <= 1) & (rg >= 0.62) & (ys < 65); front = (rg <= 1) & (rg >= 0.62) & (ys >= 65)
    paint(L, back, C['amber'])
    for k, cx_ in enumerate(cols):
        ph = (hsh(k, 7, 2) * 60 + f * 10) % 60; y1 = int(64 - ph); ln = 5 + int(hsh(k, 8, 2) * 5)
        amp = abs(cx_ - 28) / 28; ytop = 18 + int(amp * 16)
        if y1 - ln < ytop: continue
        m = (xs == cx_) & (ys <= y1) & (ys > y1 - ln); paint(L, m, C['gold']); paint(L, m & (ys > y1 - 2), C['cream'])
    for k in range(3):
        cyv = 58 - ((f * 8 + k * 20) % 48)
        if cyv < 12: continue
        ch = (np.abs(xs - 28) - (cyv - ys) * 1.0 == 0) & (ys <= cyv) & (ys > cyv - 4); paint(L, ch | sh(ch, 0, 1), C['gold']); paint(L, ch, C['cream'])
    paint(L, front, C['gold']); paint(L, front & (rg >= 0.85), C['amber'])
    frames.append(L)
FX['fx_buff_aura'] = (frames, dict(frame_size=[56, 72], frames=6, fps=10, anchor=[28, 71], loop=True, notes='gold rising aura + chevrons; anchor on feet. Draw the whole strip BEHIND the seat for a softer look, or in front (ring front arc overlaps feet).'))
# --- poison cloud: 56x48, 6f
w, h = 56, 48; xs, ys = G(w, h); frames = []
PU = [(28, 26, 10), (18, 28, 8), (38, 28, 8), (23, 18, 7), (34, 18, 7), (12, 33, 5), (44, 33, 5), (28, 34, 7)]
for f, (sc, fade) in enumerate(((0.45, 1), (0.75, 1), (1.0, 1), (1.08, 1), (1.14, 0.6), (1.2, 0.28))):
    L = layer(w, h); m = z(w, h); dm = np.full((h, w), 9.0)
    for k, (px_, py_, pr) in enumerate(PU):
        rr = pr * sc; py2 = py_ - f * 1.2; d = np.hypot(xs - px_, (ys - py2) * 1.1) / rr; m |= d <= 1; dm = np.minimum(dm, d + (ys - py2) / (rr * 4))
    paint(L, m, C['plum_dk']); paint(L, m & (dm < 0.85), C['plum']); paint(L, m & (dm < 0.45), C['violet']); paint(L, m & (dm < 0.2) & (ys < 30), C['rose'])
    for k in range(7):
        bx_ = int(8 + hsh(k, 1, 9) * 40); by_ = int(40 - ((hsh(k, 2, 9) * 30 + f * 6) % 34))
        if 0 <= by_ < h - 1 and f >= 1:
            bb = (np.abs(xs - bx_) + np.abs(ys - by_) <= 1); paint(L, bb, C['grass']); L[by_, bx_] = C['lime'] + (255,)
    if fade < 1: L[~dith(w, h, fade, f)] = 0
    frames.append(L)
FX['fx_poison_cloud'] = (frames, dict(frame_size=[56, 48], frames=6, fps=8, anchor=[28, 36], loop=False, notes='toxic purple puffs with acid-green bubbles (purple keeps it readable over the green meadow); anchor ~ target waist/centre. Frames 2-3 can loop while a DoT ticks.'))
# --- shield: 56x72, 5f (0-1 form, 2-4 hold loop)
w, h = 56, 72; xs, ys = G(w, h); frames = []
bub = ((xs - 27.5) / 26) ** 2 + ((ys - 37) / 34) ** 2
rim = (bub <= 1) & (bub >= 0.86)
hexl = (((xs + ys) % 8) == 0) | (((xs - ys) % 8) == 0)
for f in range(5):
    L = layer(w, h)
    if f < 2:
        grow = [0.45, 0.8][f]; b2 = ((xs - 27.5) / (26 * grow)) ** 2 + ((ys - 71 + 34 * grow) / (34 * grow)) ** 2
        r2 = (b2 <= 1) & (b2 >= 0.8); paint(L, r2, C['sky']); paint(L, r2 & (b2 >= 0.9), C['ice'])
    else:
        band = np.abs(ys - (14 + (f - 2) * 20)) <= 6
        inside = (bub < 0.86) & hexl & band
        paint(L, inside, C['sky_lt']); paint(L, inside & band, C['ice'])
        paint(L, rim, C['sky']); paint(L, rim & (bub >= 0.93), C['ice'])
        hl = (bub <= 0.8) & (bub >= 0.66) & (xs < 20) & (ys < 30); paint(L, hl, C['white'])
    frames.append(L)
FX['fx_shield'] = (frames, dict(frame_size=[56, 72], frames=5, fps=10, anchor=[28, 71], loop=False, segments=dict(form=dict(frames=[0, 1], loop=False), hold=dict(frames=[2, 3, 4], loop=True)),
    notes='force bubble around a 48x70 seat/monster; anchor on feet. Play 0-1 once then loop 2-4 while the shield lasts; pixel-hex fill keeps the target visible (binary alpha).'))
# --- lightning: 32x96, 5f
w, h = 32, 96; frames = []
def bolt(seed, x_end=16):
    pts_ = []; x = 16 + (hsh(seed, 0, 4) - 0.5) * 10
    for k, y in enumerate(range(0, 90, 6)):
        pts_.append((x, y)); x = np.clip(x + (hsh(seed, k + 1, 4) - 0.5) * 12, 5, 26)
        x = x * 0.75 + x_end * 0.25 if y > 60 else x
    pts_.append((x_end, 90)); return pts_
def draw_path(L, p, core_w, col_core, col_rim):
    im_c = Image.new('L', (w, h), 0); dd = ImageDraw.Draw(im_c); dd.line(p, fill=1, width=core_w)
    mc = np.array(im_c) > 0; paint(L, ring(mc, True) & (L[..., 3] == 0), C[col_rim]); paint(L, mc, C[col_core])
for f in range(5):
    L = layer(w, h)
    if f in (0, 1, 2):
        p = bolt(1 if f != 2 else 2)
        if f == 0: p = p[:len(p) // 2 + 1]
        draw_path(L, p, 2 if f == 1 else 1, 'white', 'gold')
        if f >= 1:
            br = [p[5], (p[5][0] + 7, p[5][1] + 8), (p[5][0] + 9, p[5][1] + 15)]; br2 = [p[9], (p[9][0] - 7, p[9][1] + 6), (p[9][0] - 8, p[9][1] + 12)]
            draw_path(L, br, 1, 'cream', 'amber'); draw_path(L, br2, 1, 'cream', 'amber')
        if f == 2:
            xs2, ys2 = G(w, h); st = np.array(Image.new('L', (w, h)))
            ex = ((xs2 - 16) / 13) ** 2 + ((ys2 - 91) / 4.5) ** 2; paint(L, ex <= 1, C['gold']); paint(L, ex <= 0.5, C['cream']); paint(L, ex <= 0.2, C['white'])
    elif f == 3:
        draw_path(L, bolt(2), 1, 'cream', 'amber'); L[~dith(w, h, 0.5, 1)] = 0
        for k in range(6): spark(L, int(4 + hsh(k, 1, 6) * 24), int(80 + hsh(k, 2, 6) * 14), 1, 'white', 'gold')
    else:
        for k in range(5): spark(L, int(3 + hsh(k, 3, 6) * 26), int(78 + hsh(k, 4, 6) * 16), 1, 'cream', 'amber')
    frames.append(L)
FX['fx_lightning'] = (frames, dict(frame_size=[32, 96], frames=5, fps=16, anchor=[16, 95], loop=False, notes='strike from above; anchor = impact point at the target feet (bottom-centre). Frame 2 = impact flash. Hold frame 1-2 alternation for longer zaps.'))

# --- taunt badge 12x13, 2f bob; taunt aura 56x16, 3f pulse
frames = []
for f in range(2):
    L = layer(12, 13); bm = ell(12, 13, 5.5, 5.5 + f, 5.4, 5.4); paint(L, bm, C['red']); paint(L, bm & ell(12, 13, 5.0, 5.0 + f, 4.2, 4.2), C['coral'])
    paint(L, rect(12, 13, 5, 2 + f, 6, 6 + f), C['white']); paint(L, rect(12, 13, 5, 8 + f, 6, 9 + f), C['white']); paint(L, bm & e_bot(bm), C['red_dk'])
    outline(L); frames.append(L)
FX['taunt_badge'] = (frames, dict(frame_size=[12, 13], frames=2, fps=3, anchor=[6, 12], loop=True, notes='overhead taunt/aggro badge (red "!" shout). Place the anchor ~2px above the top of the seat/monster sprite (e.g. seat top y = feet-78+hat). 1px bob. Has a dark outline like UI icons.'))
frames = []
w, h = 56, 16; xs, ys = G(w, h)
for f in range(3):
    L = layer(w, h); rg = ((xs - 27.5) / (24 + f)) ** 2 + ((ys - 8) / (5.5 + f * 0.3)) ** 2
    ringm = (rg <= 1) & (rg >= 0.72); paint(L, ringm, C['red_dk']); paint(L, ringm & (rg >= 0.86) & (ys >= 8), C['red'])
    ticks = ringm & ((((xs + f * 3) // 3) % 3) == 0); L[ticks & (ys < 8)] = 0
    frames.append(L)
FX['taunt_aura'] = (frames, dict(frame_size=[56, 16], frames=3, fps=6, anchor=[28, 8], loop=True, notes='optional subtle red ground ring for a taunting seat/monster; centre it on the feet row (seat anchor) and draw BEHIND the sprite.'))
# --- mana tick: 16x28, 6f
frames = []
w, h = 16, 28
for f in range(6):
    L = layer(w, h)
    for k, (x0, ph) in enumerate(((5, 0.0), (10, 0.35), (7, 0.7))):
        life = (f / 6 + ph) % 1.0; y = int(25 - life * 22)
        if life > 0.85: continue
        sz = 1 if life > 0.55 or k == 2 else 2
        spark(L, x0, y, sz, 'white' if life < 0.3 else 'sky_lt', 'sky')
    frames.append(L)
FX['mana_tick'] = (frames, dict(frame_size=[16, 28], frames=6, fps=10, anchor=[8, 27], loop=False, notes='subtle MP-regen tick in the MP colour #4c9ce8: blue sparkles rising. Anchor at the seat feet/centre or on the MP bar of the card; play once per regen tick. Pair with fx/mp_plus.png.'))
# --- '+MP' float: letters in the damage-font style (MP colours)
GLM = {'M': ["## ##", "#####", "# # #", "## ##", "## ##", "## ##", "## ##"], 'P': ["#### ", "## ##", "## ##", "#### ", "##   ", "##   ", "##   "],
       '+': ["     ", "  #  ", "  #  ", "#####", "  #  ", "  #  ", "     "]}
def glyph_mp(ch):
    L = layer(7, 9)
    for y, row in enumerate(GLM[ch]):
        for x, c_ in enumerate(row):
            if c_ == '#': L[y + 1, x + 1] = C['sky'] + (255,) if y < 6 else C['blue'] + (255,)
    outline(L, diag=True); return L
save(img(strip([glyph_mp('M'), glyph_mp('P')])), 'ui/dmg_font_mp_letters.png')
META['ui/dmg_font_mp_letters.png'] = dict(frames=2, frame_size=[7, 9], notes="glyph order 'MP', same style/advance (6px) as ui/dmg_font_mp.png so code can draw '+5 MP' (digits from dmg_font_mp).")
pm = layer(19, 9)
for k, ch in enumerate('+MP'): over(pm[:, k * 6:k * 6 + 7], glyph_mp(ch))
frames = []
for f in range(4):
    L = layer(19, 14); y = 4 - f + (0 if f < 3 else 0); over(L[max(0, y):max(0, y) + 9], pm)
    if f == 3: L[~dith(19, 14, 0.5, 0)] = 0
    frames.append(L)
FX['mp_plus'] = (frames, dict(frame_size=[19, 14], frames=4, fps=8, anchor=[9, 13], loop=False, notes="'+MP' float in MP colours: rises 1px/frame, last frame dithered out. For numbers use dmg_font_mp + dmg_font_mp_letters instead."))
# save FX + preview
for n, (frs, meta) in FX.items():
    save(img(strip(frs)), f'fx/{n}.png'); META[f'fx/{n}.png'] = dict(meta, style='no black outline (glow FX): bright core -> darker coloured rim, binary alpha, fades via ordered dither')
json.dump(dict(meta=META, motifs=MOTIF, kinds=KIND, bar_slots=BAR_SLOTS, costs=BAR_COSTS), open(W_ + 'meta_skills.json', 'w'), indent=1)
print('ok', len(ICONS), 'icons', len(FX), 'fx')
