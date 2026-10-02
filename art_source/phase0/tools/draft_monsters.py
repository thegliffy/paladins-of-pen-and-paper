"""DRAFT region monsters (pending approval): procedural native-res sprites -> same 80x70 strips / anchors / anims as build_cut."""
import numpy as np
from regionlib import Sprite, E, P, R, LN, eye
W, H = 72, 64
def S(): return Sprite(W, H)
def e(*a, **k): return E(W, H, *a, **k)
def p(pts): return P(W, H, pts)
def r(*a): return R(W, H, *a)
def ln(*a): return LN(W, H, *a)
GREEN = ['pine_dk', 'leaf_dk', 'leaf', 'grass']
MUD = ['bark', 'wood_dk', 'wood', 'wood_lt']
STONE = ['ink', 'slate', 'gray', 'silver']
STEEL = ['slate', 'gray', 'silver', 'mist']
SANDST = ['wood_dk', 'wood', 'wood_lt', 'tan']

def bramblet():            # meadow, regular: a hedge-ball with a grudge
    s = S(); cx, cy = 36, 42
    for i, a in enumerate(np.linspace(0, 2 * np.pi, 13)[:-1]):       # thorns behind the ball
        if np.sin(a) > 0.75: continue
        dx, dy = np.cos(a), np.sin(a); b = np.array([cx + dx * 14, cy + dy * 13]); t = np.array([cx + dx * 21, cy + dy * 19])
        nrm = np.array([-dy, dx]) * 2.6
        s.add(p([tuple(b + nrm), tuple(t), tuple(b - nrm)]), ['bark', 'wood_dk', 'wood'], sep=False)
    s.add(e(29, 60, 4, 3) | e(43, 60, 4, 3), ['bark', 'wood_dk', 'wood'])                          # root feet
    s.add(e(cx, cy, 17, 16), GREEN)
    for (x, y, rr) in ((28, 34, 5), (42, 33, 5), (26, 48, 5), (46, 47, 5), (36, 54, 4)):          # leaf clumps
        s.add(e(x, y, rr, rr - 1), ['leaf_dk', 'leaf', 'grass', 'lime'], line='pine_dk')
    s.add(p([(27, 28), (19, 16), (31, 25)]) | p([(45, 28), (53, 16), (41, 25)]), ['leaf_dk', 'grass', 'lime'])   # leaf ears
    s.add(r(28, 38, 45, 45), ['pine_dk'], flat=True, sep=False)                                    # face shadow band
    eye(s, 31, 40, 1, look=(1, 0)); eye(s, 41, 40, 1, look=(-1, 0))
    s.px([(29, 37), (30, 37), (31, 38), (43, 37), (42, 37), (41, 38)], 'outline')                  # angry brows
    s.px([(33, 44), (34, 45), (35, 44), (36, 45), (37, 44), (38, 45), (39, 44)], 'cream')        # zig-zag grin
    for (x, y) in ((24, 42), (47, 39), (33, 52), (44, 53), (22, 51)):                              # berries
        s.px([(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)], 'red'); s.px([(x, y)], 'coral')
    return s

def grinmud_toad():        # meadow, regular: squat mud toad, lily-pad cap, enormous grin
    s = S()
    s.add(e(36, 60, 25, 3), ['wood_dk', 'wood'], flat=True, sep=False)                          # mud puddle
    s.add(e(16, 55, 7, 5) | e(56, 55, 7, 5), MUD)                                                  # back legs
    s.add(e(36, 47, 21, 13), MUD)                                                                  # body
    s.add(e(36, 52, 14, 7), ['wood_lt', 'tan', 'sand'], line='wood')                               # belly
    s.add(e(24, 33, 7, 7) | e(48, 33, 7, 7), MUD)                                                  # eye bumps
    s.add(e(24, 32, 4, 4) | e(48, 32, 4, 4), ['amber', 'gold', 'cream'], line='wood_dk')
    s.px([(24, 31), (24, 32), (24, 33), (48, 31), (48, 32), (48, 33)], 'outline')                 # slit pupils
    s.add(e(36, 28, 10, 3), ['leaf_dk', 'leaf', 'grass'])                                         # lily pad cap
    s.px([(36, 25), (35, 25), (37, 25), (36, 24)], 'cream'); s.px([(36, 25)], 'gold')
    m = e(36, 44, 15, 5) & (np.mgrid[0:H, 0:W][0] >= 44)                                           # grin
    s.add(m, ['outline'], flat=True, sep=False)
    s.add(e(36, 45, 11, 2) & (np.mgrid[0:H, 0:W][0] >= 45), ['red_dk'], flat=True, sep=False)
    s.px([(x, 44) for x in range(23, 50, 3)], 'cream')                                            # teeth
    s.add(e(22, 58, 5, 3) | e(50, 58, 5, 3), MUD)                                                  # front feet
    for (x, y) in ((27, 40), (46, 41), (33, 38), (52, 47), (19, 46)):                             # warts
        s.px([(x, y)], 'wood_lt'); s.px([(x + 1, y + 1)], 'wood_dk')
    return s

def bottlecrab():          # coast, regular: hermit crab living in a washed-up bottle
    s = S()
    for k in range(3):                                                                              # legs
        s.add(ln((30 - k * 4, 50), (20 - k * 5, 60), 2.2) | ln((42 + k * 4, 50), (52 + k * 5, 60), 2.2), ['red_dk', 'red'], sep=False)
    bottle = p([(20, 44), (38, 18), (46, 22), (48, 30), (32, 52)])
    s.add(e(31, 36, 12, 15, rot=-0.55) | bottle, ['blue_dk', 'blue', 'sky', 'sky_lt'])             # bottle shell
    s.add(p([(44, 18), (50, 10), (55, 13), (49, 22)]), ['blue', 'sky', 'sky_lt'])                  # neck
    s.add(p([(50, 9), (53, 5), (58, 8), (55, 12)]), ['wood', 'wood_lt', 'tan'])                    # cork
    s.add(p([(26, 34), (34, 26), (38, 30), (30, 38)]), ['tan', 'sand', 'parchment'], line='wood')  # message scroll inside
    s.px([(22 + i, 34 - i) for i in range(12)], 'ice'); s.px([(23 + i, 36 - i) for i in range(4)], 'white')
    s.add(e(36, 49, 13, 8), ['red_dk', 'red', 'coral'])                                            # crab body
    s.add(ln((31, 45), (29, 38), 2) | ln((41, 45), (43, 38), 2), ['red_dk', 'red'], sep=False)     # eye stalks
    s.add(e(29, 37, 2.2, 2.2) | e(43, 37, 2.2, 2.2), ['white'], flat=True)
    s.px([(29, 37), (43, 37)], 'outline')
    for sx in (-1, 1):                                                                              # claws
        cx = 36 + sx * 19
        s.add(ln((36 + sx * 9, 50), (cx, 47), 3), ['red_dk', 'red'])
        s.add(e(cx + sx * 2, 44, 6, 5), ['red_dk', 'red', 'coral'])
        s.add(p([(cx + sx * 2, 44), (cx + sx * 9, 36), (cx + sx * 5, 44)]), ['red_dk', 'red'], line='outline')
    s.px([(34, 52), (35, 53), (36, 53), (37, 53), (38, 52)], 'red_dk')
    return s

def squallgull():          # coast, regular flyer: a gull with its own storm cloud
    s = S()
    s.add(p([(34, 36), (6, 20), (2, 28), (14, 36), (30, 44)]), ['gray', 'silver', 'mist'])        # left wing
    s.add(p([(40, 36), (66, 16), (70, 24), (60, 34), (44, 44)]), ['gray', 'silver', 'mist'])      # right wing
    s.add(p([(6, 20), (2, 28), (8, 28), (11, 23)]) | p([(66, 16), (70, 24), (65, 25), (63, 19)]), ['outline', 'ink'])
    s.add(e(37, 44, 11, 9), ['silver', 'mist', 'white'])                                          # body
    s.add(p([(28, 50), (37, 58), (46, 50)]), ['gray', 'silver'])                                   # tail
    s.add(e(37, 33, 7, 6), ['silver', 'mist', 'white'])                                           # head
    s.add(p([(35, 36), (39, 36), (37, 43)]), ['orange', 'amber', 'gold'])                          # beak (down/forward)
    s.px([(37, 38), (37, 39)], 'red_dk')
    eye(s, 34, 32, 0, glow='outline'); eye(s, 40, 32, 0, glow='outline')
    s.px([(32, 30), (33, 30), (33, 31), (42, 30), (41, 30), (41, 31)], 'outline')                 # scowl
    s.add(e(37, 23, 11, 4) | e(31, 21, 6, 5) | e(42, 20, 6, 5) | e(37, 18, 5, 4), ['slate', 'gray', 'silver'])   # storm cloud
    s.px([(38, 24), (37, 25), (38, 25), (36, 26), (37, 26), (38, 26), (37, 27)], 'gold')   # bolt
    s.px([(38, 23)], 'cream')
    s.add(ln((33, 52), (31, 59), 2) | ln((41, 52), (43, 59), 2), ['orange', 'amber'], sep=False)  # dangling feet
    s.px([(29, 60), (30, 60), (31, 60), (32, 60), (42, 60), (43, 60), (44, 60), (45, 60)], 'orange')
    return s

def kelpback():            # coast, LARGE: barnacled snapping turtle draped in kelp
    s = S()
    SKIN = ['pine_dk', 'pine', 'haze', 'sky_lt']
    s.add(e(52, 57, 6, 5) | e(26, 57, 6, 5), SKIN)                                                # back legs
    s.add(e(40, 38, 25, 18), ['bark', 'wood_dk', 'wood', 'wood_lt'])                              # shell dome
    s.add(e(40, 51, 27, 5), ['wood_dk', 'wood', 'tan'])                                           # shell rim
    for (x, y, rr) in ((32, 30, 5), (45, 28, 5), (52, 38, 4), (38, 40, 5), (26, 41, 4)):           # plates
        s.add(e(x, y, rr, rr - 1), ['wood_dk', 'wood', 'wood_lt'], line='bark')
    for (x, y) in ((28, 26), (48, 22), (56, 32), (42, 34), (34, 46), (58, 44)):                    # barnacles
        s.px([(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)], 'mist'); s.px([(x + 1, y + 1)], 'gray'); s.px([(x, y)], 'white')
    for i, x in enumerate((20, 27, 35, 44, 53, 60)):                                               # hanging kelp
        L_ = 7 + (i * 5) % 6
        s.add(ln((x, 48), (x - 1 + (i % 2) * 2, 48 + L_), 3), ['leaf_dk', 'leaf', 'grass'], line='pine_dk')
    s.add(e(20, 21, 8, 6) | e(26, 28, 5, 3), ['leaf_dk', 'leaf', 'grass'])                       # kelp on top
    s.add(e(14, 56, 7, 5) | e(64, 57, 6, 5), SKIN)                                                # front legs
    s.add(ln((18, 46), (11, 40), 10), SKIN)                                                       # neck
    s.add(e(10, 36, 10, 8), SKIN)                                                                 # head
    s.add(p([(1, 40), (12, 43), (4, 50)]), ['outline'], flat=True)                                 # open jaw
    s.add(p([(3, 44), (11, 44), (5, 49)]), ['red_dk'], flat=True, sep=False)
    s.add(p([(0, 36), (6, 33), (11, 39), (1, 41)]), ['slate', 'gray', 'silver'])                  # hooked beak
    s.add(p([(3, 49), (12, 45), (13, 49), (6, 51)]), ['slate', 'gray'])                           # lower beak
    eye(s, 11, 33, 1, pupil='outline', white='gold', look=(-1, 0))
    s.px([(8, 30), (9, 30), (10, 30), (11, 30), (12, 29), (13, 29)], 'outline')
    return s

def gloomgrub():           # cave, regular: pale lamp-spotted cave grub
    s = S(); PALE = ['tan', 'sand', 'parchment', 'cream']
    segs = [(58, 54, 9, 7), (47, 51, 9, 9), (36, 48, 9, 10), (25, 44, 9, 11)]
    for (x, y, rx, ry) in segs:
        s.add(e(x, y, rx, ry), PALE, line='wood')
    for (x, y) in ((58, 49), (47, 44), (36, 40), (27, 36)):                                        # glow spots
        s.px([(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)], 'cyan'); s.px([(x, y)], 'white')
    for (x, y, rx, ry) in segs[:3]:
        s.add(ln((x - 2, y + ry - 1), (x - 4, 61), 2) | ln((x + 3, y + ry - 1), (x + 3, 61), 2), ['wood', 'wood_lt'], sep=False)
    s.add(e(14, 44, 10, 10), PALE, line='wood')                                                    # head
    s.add(p([(5, 50), (1, 57), (8, 53)]) | p([(13, 53), (11, 60), (16, 54)]), ['bark', 'wood_dk', 'wood'])  # mandibles
    s.add(e(8, 50, 5, 3), ['outline'], flat=True, sep=False)
    eye(s, 10, 41, 1, glow='cyan'); eye(s, 17, 40, 1, glow='cyan'); s.px([(10, 41), (17, 40)], 'white')
    s.add(ln((12, 35), (6, 27), 1.6) | ln((17, 35), (20, 26), 1.6), ['wood', 'wood_lt'], sep=False)  # feelers
    s.px([(5, 26), (6, 26), (20, 25), (21, 25)], 'cyan')
    return s

def dripfang():            # cave, regular: a stalagmite that bites
    s = S()
    body = p([(22, 61), (26, 44), (30, 28), (34, 10), (37, 4), (40, 12), (44, 26), (48, 42), (52, 61)])
    s.add(e(24, 58, 7, 4) | e(51, 58, 7, 4), STONE)                                                # stubby rock feet
    s.add(body, STONE)
    for (y, x0, x1) in ((22, 32, 43), (35, 29, 46), (50, 26, 49)):                                 # strata ridges
        s.px([(x, y + (x % 3 == 0)) for x in range(x0, x1)], 'ink')
    s.add(e(37, 41, 9, 7), ['outline'], flat=True, sep=False)                                      # maw
    s.add(e(37, 43, 7, 4), ['blood', 'red_dk'], flat=True, sep=False)
    s.px([(31, 36), (32, 37), (35, 36), (36, 37), (39, 36), (40, 37), (43, 36), (42, 37)], 'white')  # upper fangs
    s.px([(33, 47), (33, 46), (37, 47), (37, 46), (41, 47), (41, 46)], 'mist')                    # lower fangs
    eye(s, 33, 27, 1, glow='gold'); eye(s, 41, 27, 1, glow='gold'); s.px([(33, 27), (41, 27)], 'cream')
    s.px([(31, 24), (32, 24), (33, 25), (43, 24), (42, 24), (41, 25)], 'outline')
    for (x, y) in ((28, 18), (46, 30), (25, 34)):                                                  # drips
        s.px([(x, y), (x, y + 1)], 'sky_lt'); s.px([(x, y + 2)], 'ice')
    s.add(e(15, 59, 4, 3) | e(58, 60, 3, 2), STONE)                                                # pebbles
    return s

def pebble_squire():       # keep, regular: a pile of pebbles playing knight
    s = S()
    s.add(e(29, 59, 5, 4) | e(43, 59, 5, 4), SANDST)                                               # feet
    s.add(ln((56, 50), (60, 16), 3), ['wood_dk', 'wood', 'wood_lt'])                               # wooden sword blade
    s.add(r(53, 46, 62, 49), ['bark', 'wood_dk'], flat=True)                                       # guard
    s.add(e(36, 46, 12, 11), SANDST)                                                               # torso stone
    s.add(e(30, 42, 4, 3) | e(41, 50, 4, 3), ['wood', 'wood_lt', 'tan'], line='wood_dk')          # pebble inlays
    s.add(e(57, 44, 3, 3) | e(51, 44, 3, 3), SANDST)                                               # right arm pebbles
    s.add(e(36, 27, 10, 9), SANDST)                                                                # rock head
    s.add(p([(25, 30), (27, 13), (45, 13), (47, 30)]), STEEL)                                      # bucket helm
    s.add(r(26, 12, 46, 15), ['slate', 'gray'])                                                    # rim
    s.add(r(28, 22, 44, 25), ['outline'], flat=True, sep=False)                                    # visor slit
    s.px([(32, 23), (33, 23), (39, 23), (40, 23)], 'gold')
    s.px([(37, 17), (38, 18), (38, 19)], 'slate')                                                  # dent
    s.add(ln((47, 12), (51, 7), 1.6), ['slate', 'gray'], sep=False)                                # bucket handle stub
    s.add(e(21, 46, 9, 10), ['wood_dk', 'wood', 'wood_lt'])                                        # plank shield
    s.add(e(21, 46, 9, 10) & ~e(21, 46, 7, 8), ['slate', 'gray', 'silver'], sep=False)             # iron rim
    s.px([(21, y) for y in range(38, 55)], 'wood_dk')
    s.px([(20, 45), (22, 45), (20, 47), (22, 47)], 'silver')
    return s

def hollow_helm():         # keep, regular floater: an empty great helm, still on guard
    s = S(); CLOTH = ['plum_dk', 'plum', 'violet']
    s.add(p([(26, 34), (46, 34), (50, 50), (44, 46), (40, 60), (35, 50), (30, 61), (27, 48), (21, 52)]), CLOTH)   # tattered tabard
    s.add(e(36, 25, 12, 14), STEEL)                                                                 # helm
    s.add(r(24, 14, 49, 17), ['slate', 'gray'], sep=False)
    s.add(r(26, 22, 47, 25), ['outline'], flat=True, sep=False)                                    # eye slit
    s.add(r(35, 25, 38, 34), ['outline'], flat=True, sep=False)                                    # breath slot
    s.px([(29, 23), (30, 23), (31, 23), (41, 23), (42, 23), (43, 23)], 'cyan'); s.px([(30, 23), (42, 23)], 'white')
    for i in range(4): s.px([(30 + i * 2, 30), (41 + i * 2 - 2, 30)], 'slate')                       # rivets / vents
    s.add(p([(36, 11), (33, 4), (36, 1), (39, 4)]), ['red_dk', 'red', 'coral'])                     # plume stub
    s.add(r(56, 8, 59, 62), ['wood_dk', 'wood', 'wood_lt'])                                        # floating halberd
    s.add(p([(59, 12), (67, 9), (68, 20), (59, 22)]), STEEL)                                        # axe blade
    s.add(p([(53, 14), (56, 13), (56, 18), (53, 16)]), STEEL)                                       # back spike
    s.add(p([(55, 8), (57.5, 1), (60, 8)]), STEEL)                                                 # tip
    s.add(e(14, 44, 6, 5), STEEL)                                                                   # one floating fist
    s.add(p([(9, 47), (19, 47), (18, 54), (10, 54)]), ['slate', 'gray', 'silver'])                  # cuff
    s.px([(11, 41), (13, 41), (15, 41), (17, 42)], 'slate'); s.px([(10, 44), (11, 45)], 'slate')
    return s

def cobble_rat():          # keep, regular: a rat wearing a patch of courtyard
    s = S(); FUR = ['ink', 'slate', 'gray', 'silver']
    s.add(ln((58, 55), (66, 44), 2.5) | ln((66, 44), (69, 36), 2), ['skin4', 'skin3', 'skin2'], sep=False)  # tail
    s.add(e(26, 60, 5, 3) | e(50, 60, 5, 3), ['skin4', 'skin3'])                                   # feet
    s.add(e(40, 50, 20, 11), ['bark', 'wood_dk', 'wood', 'wood_lt'])                               # body fur
    shell = e(42, 45, 18, 10) & (np.mgrid[0:H, 0:W][0] <= 50)
    s.add(shell, STONE)                                                                             # cobble shell base
    for (x, y, rx, ry) in ((32, 44, 5, 3), (43, 40, 5, 3), (53, 45, 5, 3), (38, 48, 4, 2), (49, 49, 4, 2), (43, 44, 3, 2)):
        s.add(e(x, y, rx, ry), ['slate', 'gray', 'silver', 'mist'], line='ink', clip=shell)
    s.add(e(21, 38, 5, 6) | e(29, 40, 4, 5), ['skin4', 'skin3', 'skin2'])                          # ears
    s.add(e(19, 48, 11, 10), ['bark', 'wood_dk', 'wood', 'wood_lt'])                               # head
    s.add(p([(10, 46), (1, 53), (4, 56), (12, 56)]), ['wood_dk', 'wood', 'wood_lt'])               # snout
    s.px([(1, 53), (2, 53), (2, 52)], 'outline')
    eye(s, 15, 46, 1, glow='red'); s.px([(15, 45)], 'coral'); s.px([(16, 46)], 'blood')
    s.px([(6, 57), (6, 58), (7, 57), (7, 58)], 'cream')                                            # incisors
    s.px([(3, 50), (4, 50), (5, 49), (6, 49)], 'silver')                                           # whiskers
    return s

DRAFT = {   # id: (fn, region, size, name, concept, sprite portrait rect guess (x,y) in frame coords is auto)
    'bramblet': (bramblet, 'meadow', 'regular', 'Bramblet', 'A rolling hedge-ball with leaf ears, berries and a grudge against anyone who cuts the Briar Cross hedge.'),
    'grinmud_toad': (grinmud_toad, 'meadow', 'regular', 'Grinmud Toad', 'The thing that grins from the Millpond mud: a squat brown toad with a lily-pad cap and far too many teeth.'),
    'bottlecrab': (bottlecrab, 'coast', 'regular', 'Bottlecrab', 'A hermit crab that moved into a washed-up message bottle; snips first, reads never.'),
    'squallgull': (squallgull, 'coast', 'regular', 'Squallgull', 'A scowling grey gull that drags its own tiny storm cloud around the lighthouse.'),
    'kelpback': (kelpback, 'coast', 'large', 'Kelpback Snapper', 'A barnacled snapping turtle draped in kelp that hauls itself out of the shallows.'),
    'gloomgrub': (gloomgrub, 'cave', 'regular', 'Gloomgrub', 'A pale segmented cave grub with glowing cyan spots and clacking mandibles.'),
    'dripfang': (dripfang, 'cave', 'regular', 'Dripfang', 'A stalagmite that is not a stalagmite: yellow eyes, a stony maw, drips down its sides.'),
    'pebble_squire': (pebble_squire, 'keep', 'regular', 'Pebble Squire', 'A pile of walking pebbles in a dented bucket helm with a wooden sword; the small stones that walk at dusk.'),
    'hollow_helm': (hollow_helm, 'keep', 'regular', 'Hollow Helm', 'An empty great helm and two gauntlets floating over a tattered tabard, still keeping watch.'),
    'cobble_rat': (cobble_rat, 'keep', 'regular', 'Cobble Rat', 'A courtyard rat wearing a patch of cobblestones as a shell.'),
}
