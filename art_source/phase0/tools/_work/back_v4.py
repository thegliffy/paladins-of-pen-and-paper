# ======================= v4 back/seated polish: native 48x78 polygons, sloped shoulders, arms, tapered robes =======================
from PIL import ImageDraw as _ID
def M(pts_, w=BW, h=BH):
    im = Image.new('L', (w, h), 0); _ID.Draw(im).polygon([(float(x), float(y)) for x, y in pts_], fill=1); return np.array(im) > 0
def MX(pts_): return M([(47 - x, y) for x, y in pts_])          # mirror across the seat centre line
def LNn(p, w=1):
    im = Image.new('L', (BW, BH), 0); _ID.Draw(im).line([tuple(map(float, q)) for q in p], fill=1, width=w); return np.array(im) > 0
def Ell(cx, cy, rx, ry): return ell(BW, BH, cx, cy, rx, ry)
def shade3(L, m, base, dark, light, spine=False, rim=True, dark2=None):
    """base + 2px shadow on the right/bottom, 1px lit rim on the left/top, optional darker spine band."""
    paint(L, m, base)
    r1 = e_right(m) | e_bot(m); r2 = e_right(m & ~r1)
    paint(L, r1 | r2, dark)
    if rim: paint(L, (e_left(m) | e_top(m)) & ~r1, light)
    if spine: paint(L, m & ((bxs == 23) | (bxs == 24)) & ~e_top(m), dark)
    if dark2 is not None: paint(L, e_right(m) & (bys > bys[m].min() + 3) if m.any() else m, dark2)
def folds(L, m, lines, dark, light=None):
    for p in lines:
        ln = LNn(p) & m & ~e_bot(m); paint(L, ln, dark)
        if light is not None: paint(L, sh(ln, -1, 0) & m & ~ln & ~e_left(m), light)
def part(L, fn):
    """draw a sub-part on its own layer, outline it, and stack it (keeps internal outlines between parts)."""
    Q = layer(BW, BH); fn(Q); outline(Q); over(L, Q)
# --- shared silhouettes (all layers use these, so every class fits every body) ---
NECK = M([(20, 35), (27, 35), (27, 42), (20, 42)])
TORSO = M([(18, 40), (29, 40), (35, 42), (38, 44), (38, 48), (35, 51), (33, 57), (34, 60), (13, 60), (14, 57), (12, 51), (9, 48), (9, 44), (12, 42)])
ARM_UP_L = M([(8, 44), (12, 45), (13, 52), (12, 56), (10, 58), (6, 58), (5, 54), (6, 47)])
FORE_L = M([(6, 55), (10, 54), (13, 52), (16, 53), (15, 56), (11, 59), (7, 59)])
HAND_L = Ell(16, 54.5, 1.6, 1.6)
ARM_UP_R, FORE_R, HAND_R = [np.fliplr(a) for a in (ARM_UP_L, FORE_L, HAND_L)]
HIPS = M([(13, 57), (34, 57), (36, 62), (35, 65), (12, 65), (11, 62)])
def robe_mask(hem_y=67, flare=19.5, top=40):
    """tapered robe: sloped shoulders -> narrow waist -> flared skirt draped over the seat, scalloped hem."""
    R_ = [(29, top), (35, 42), (38, 44), (38, 48), (35, 51), (33, 56), (35, 60), (23.5 + flare - 1, hem_y - 3), (23.5 + flare, hem_y - 1)]
    hem = []
    xs_ = np.linspace(23.5 + flare, 23.5 - flare, 9)
    for k, x in enumerate(xs_): hem.append((x, hem_y + (1 if k % 2 else -0.5)))
    Lh = [(47 - x, y) for x, y in reversed(R_)]
    return M([(18, top)] + [(x, y) for x, y in R_] + hem + Lh)
def sleeve_L(bell=True):
    return M([(8, 44), (12, 45), (13, 51), (15, 53), (16, 56), (11, 60), (4, 60), (4, 56), (6, 47)]) if bell else ARM_UP_L | FORE_L
def sleeve_R(bell=True): return np.fliplr(sleeve_L(bell))
def body_back(k):
    b, s, d, bl = TONES[k]; L = layer(BW, BH)
    head = E(15.5, 17.6, 8.7, 8.2); ears = R(6, 17, 6, 19) | R(25, 17, 25, 19)
    part(L, lambda Q: (shade3(Q, HIPS, C['wood'], C['wood_dk'], C['wood_lt'])))
    def torso(Q):
        shade3(Q, TORSO | NECK, C[b], C[s], C[b], spine=True)
        paint(Q, NECK & (bys >= 40), C[s])
        paint(Q, LNn([(16, 46), (19, 48)]) | LNn([(31, 46), (28, 48)]), C[s])          # shoulder blades
        paint(Q, LNn([(12, 43), (17, 41)]) & TORSO, C[bl] if False else C[b])
    part(L, torso)
    for up, fo, hd in ((ARM_UP_L, FORE_L, HAND_L), (ARM_UP_R, FORE_R, HAND_R)):
        part(L, lambda Q, fo=fo, hd=hd: (shade3(Q, fo | hd, C[b], C[s], C[b])))
        part(L, lambda Q, up=up: shade3(Q, up, C[b], C[s], C[b]))
    part(L, lambda Q: (shade3(Q, head, C[b], C[s], C[b]), shade3(Q, ears, C[b], C[s], C[b]), paint(Q, P1([(6, 18), (25, 18)]), C[s])))
    return L
def outfit_back():
    L = layer(BW, BH)
    part(L, lambda Q: (shade3(Q, HIPS, C['wood'], C['wood_dk'], C['wood_lt']), paint(Q, HIPS & (bys == 57), C['wood_dk'])))
    def shirt(Q):
        m = TORSO & (bys >= 41); shade3(Q, m, K3, K2, K4, spine=True)
        folds(Q, m, [[(17, 50), (16, 58)], [(30, 50), (31, 58)], [(20, 44), (21, 48)]], K2, K4)
        paint(Q, m & (bys == 41), K4)
    part(L, shirt)
    for up, fo in ((ARM_UP_L, FORE_L), (ARM_UP_R, FORE_R)):
        part(L, lambda Q, fo=fo: (shade3(Q, fo, K3, K2, K4), paint(Q, fo & (bxs >= 14) & (bxs <= 33) & e_left(fo) if False else z(BW, BH), K2)))
        part(L, lambda Q, up=up: (shade3(Q, up, K3, K2, K4), folds(Q, up, [[(8, 50), (10, 53)]] if up is ARM_UP_L else [[(39, 50), (37, 53)]], K2)))
    return L
def chair_back():
    L = layer(BW, BH)
    wood = lambda Q, m: shade3(Q, m, C['wood'], C['wood_dk'], C['wood_lt'])
    part(L, lambda Q: (wood(Q, M([(8, 62), (39, 62), (40, 65), (7, 65)])), [wood(Q, R_) for R_ in (M([(8, 65), (10, 65), (10, 74), (8, 74)]), M([(37, 65), (39, 65), (39, 74), (37, 74)]))]))
    def back(Q):
        for x in (12, 33): wood(Q, M([(x, 50), (x + 2, 50), (x + 2, 77), (x, 77)]))
        wood(Q, M([(15, 60), (32, 60), (32, 61), (15, 61)])); wood(Q, M([(15, 71), (32, 71), (32, 72), (15, 72)]))
        crest = M([(11, 49), (13, 47), (34, 47), (36, 49), (36, 52), (11, 52)]); wood(Q, crest)
        paint(Q, LNn([(15, 50), (32, 50)]) & crest, C['wood']); paint(Q, P1([(8, 32), (22, 32)]) & crest, C['wood_dk'])
        for x in (19, 27): wood(Q, M([(x, 53), (x + 1, 53), (x + 1, 59), (x, 59)]))
    part(L, back)
    return L
# ---------- class layers ----------
def hem_drape(Q, base, dark, light, hem_col=None, y0=60, y1=68, flare=19.5):
    m = robe_mask(y1, flare) & (bys >= y0); shade3(Q, m, base, dark, light)
    folds(Q, m, [[(14, y0), (9, y1)], [(19, y0), (17, y1)], [(28, y0), (30, y1)], [(33, y0), (38, y1)]], dark, light)
    if hem_col: paint(Q, e_bot(m) | e_bot(m & ~e_bot(m)), C[hem_col])
    return m
def robe_body(Q, base, dark, light, hem_col, trim=None, hem_y=68, flare=19.5):
    m = robe_mask(hem_y, flare); shade3(Q, m, C[base], C[dark], C[light], spine=True)
    folds(Q, m, [[(18, 52), (12, hem_y)], [(29, 52), (35, hem_y)], [(21, 57), (19, hem_y)], [(26, 57), (28, hem_y)]], C[dark], C[light])
    paint(Q, e_bot(m) | e_bot(m & ~e_bot(m)), C[hem_col])
    if trim: paint(Q, m & (bys >= 40) & (bys <= 41), C[trim])
    return m
def belt(Q, y, col, dark, knot=None):
    m = TORSO & (bys >= y) & (bys <= y + 1) | (robe_mask() & (bys >= y) & (bys <= y + 1) & (bxs >= 13) & (bxs <= 34))
    paint(Q, m, C[col]); paint(Q, e_right(m) | (m & (bys == y + 1) & (bxs % 4 == 0)), C[dark])
    if knot: paint(Q, knot, C[col])
def sleeves(L, base, dark, light, cuff=None, bell=True):
    for sl in (sleeve_L(bell), sleeve_R(bell)):
        def f(Q, sl=sl):
            shade3(Q, sl, C[base], C[dark], C[light])
            folds(Q, sl, [[(7, 49), (6, 56)], [(10, 50), (11, 57)]] if sl[50, 5] else [[(40, 49), (41, 56)], [(37, 50), (36, 57)]], C[dark])
            if cuff: paint(Q, sl & (bys >= 59) | (e_bot(sl) & (bys >= 57)), C[cuff])
        part(L, f)
def class_back(c):
    L = layer(BW, BH)
    if c == 'paladin':
        def plate(Q):
            m = TORSO | HIPS & (bys <= 60); shade3(Q, m, C['silver'], C['gray'], C['mist'], spine=True)
            for y in (47, 52, 57): paint(Q, LNn([(12, y), (35, y)]) & m, C['gray'])
            paint(Q, m & (bys == 48) | m & (bys == 53), C['mist'])
        part(L, plate)
        part(L, lambda Q: (lambda m: (shade3(Q, m, C['white'], C['mist'], C['white'], spine=True), folds(Q, m, [[(20, 46), (15, 67)], [(27, 46), (32, 67)], [(23, 50), (23, 67)]], C['silver'], C['white']),
            paint(Q, (R(15, 31, 16, 36) | R(13, 32, 18, 33)) & m, C['gold']), paint(Q, e_bot(m), C['gold'])))(M([(17, 42), (30, 42), (33, 50), (36, 60), (38, 66), (34, 68), (29, 66), (23.5, 68), (18, 66), (13, 68), (9, 66), (11, 60), (14, 50)])))
        for up, fo in ((ARM_UP_L, FORE_L), (ARM_UP_R, FORE_R)):
            part(L, lambda Q, fo=fo: shade3(Q, fo, C['silver'], C['gray'], C['mist']))
            part(L, lambda Q, up=up: (shade3(Q, up, C['silver'], C['gray'], C['mist']), paint(Q, up & (bys == 52), C['gray'])))
        for cx in (9.5, 37.5):
            part(L, lambda Q, cx=cx: (lambda m: (shade3(Q, m, C['silver'], C['gray'], C['mist']), paint(Q, m & (bys == int(46.5)), C['gray']), paint(Q, m & (bys == 45) & ~e_left(m), C['white'])))(Ell(cx, 45.5, 5.2, 4.2) & (bys <= 48)))
        part(L, lambda Q: (paint(Q, M([(4, 55), (6, 55), (6, 69), (4, 69)]), C['silver']), paint(Q, M([(5, 55), (6, 55), (6, 69), (5, 69)]), C['gray']), paint(Q, M([(2, 53), (8, 53), (8, 54), (2, 54)]), C['gold']), paint(Q, M([(4, 50), (6, 50), (6, 52), (4, 52)]), C['wood_dk'])))  # sword at the left hip
    elif c == 'wizard':
        part(L, lambda Q: robe_body(Q, 'blue', 'blue_dk', 'sky', 'gold', trim='gold'))
        part(L, lambda Q: belt(Q, 55, 'gold', 'amber', knot=M([(30, 56), (32, 56), (33, 61), (31, 61)])))
        sleeves(L, 'blue', 'blue_dk', 'sky', cuff='gold')
        part(L, lambda Q: (paint(Q, M([(41, 26), (43, 26), (43, 77), (41, 77)]), C['wood']), paint(Q, M([(43, 28), (43, 28), (43, 77), (43, 77)]) | (bxs == 43) & (bys >= 27), C['wood_dk']),
            shade3(Q, Ell(42, 23.5, 3.2, 3.2), C['violet'], C['plum'], C['pink']), paint(Q, P1([(27.6, 15)]), C['white'])))
        part(L, lambda Q: shade3(Q, Ell(40.5, 55.5, 2.0, 2.0), C['skin3'], C['skin4'], C['skin2']))    # hand on the staff
    elif c == 'ranger':
        part(L, lambda Q: (lambda m: (shade3(Q, m, C['leaf'], C['leaf_dk'], C['grass'], spine=True), folds(Q, m, [[(19, 46), (13, 67)], [(28, 46), (34, 67)], [(23, 50), (22, 67)]], C['leaf_dk'], C['grass']), paint(Q, e_bot(m), C['pine'])))(robe_mask(67, 18.5)))
        part(L, lambda Q: belt(Q, 56, 'wood', 'wood_dk', knot=M([(15, 57), (18, 57), (18, 61), (15, 61)])))
        sleeves(L, 'leaf_dk', 'pine', 'leaf', bell=False)
        part(L, lambda Q: (shade3(Q, M([(27, 32), (32, 34), (21, 58), (16, 56)]), C['wood'], C['wood_dk'], C['wood_lt']), paint(Q, LNn([(19, 55), (29, 34)]), C['wood_dk'])))   # quiver
        part(L, lambda Q: (paint(Q, P1([(19, 21), (20, 20), (21, 21), (18, 20)]), C['white']), paint(Q, P1([(20, 21)]), C['red'])))
        part(L, lambda Q: (paint(Q, LNn([(5, 30), (3, 40), (3, 54), (6, 66)], 2), C['wood_lt']), paint(Q, LNn([(6, 30), (6, 66)]), C['cream'])))     # bow at the left side
        part(L, lambda Q: shade3(Q, Ell(5, 55.5, 2.0, 2.0), C['skin3'], C['skin4'], C['skin2']))
    elif c == 'bard':
        def doub(Q):
            m = TORSO; shade3(Q, m, C['red'], C['red_dk'], C['coral'], spine=True)
            for x in (16, 31): paint(Q, LNn([(x, 43), (x + (1 if x > 23 else -1), 58)]) & m, C['red_dk'])
            paint(Q, LNn([(11, 44), (36, 58)], 2) & m, C['violet']); paint(Q, LNn([(11, 43), (36, 57)]) & m, C['rose'])       # sash
        part(L, doub)
        part(L, lambda Q: (shade3(Q, HIPS | M([(12, 60), (35, 60), (38, 66), (9, 66)]), C['violet'], C['plum'], C['rose']), folds(Q, M([(12, 60), (35, 60), (38, 66), (9, 66)]), [[(17, 60), (15, 66)], [(30, 60), (32, 66)]], C['plum'])))
        for up, fo in ((ARM_UP_L, FORE_L), (ARM_UP_R, FORE_R)):
            part(L, lambda Q, fo=fo: shade3(Q, fo, C['red'], C['red_dk'], C['coral']))
            part(L, lambda Q, up=up: (shade3(Q, up, C['cream'], C['sand'], C['white']), paint(Q, up & ((bxs % 3) == 0) & ~e_bot(up) & ~e_top(up), C['red'])))
        part(L, lambda Q: (shade3(Q, Ell(39, 57, 5.2, 6.2), C['tan'], C['wood_lt'], C['sand']), paint(Q, Ell(38.5, 56, 1.4, 1.4), C['wood_dk'])))
        part(L, lambda Q: (paint(Q, LNn([(40, 51), (42, 32)], 2), C['wood_dk']), shade3(Q, M([(41, 27), (44, 27), (44, 32), (41, 32)]), C['wood'], C['wood_dk'], C['wood_lt']), paint(Q, P1([(27, 18), (29, 20)]), C['gold'])))
    elif c == 'cleric':
        part(L, lambda Q: robe_body(Q, 'white', 'mist', 'white', 'gold'))
        part(L, lambda Q: (lambda m: (paint(Q, m, C['gold']), paint(Q, e_right(m), C['amber'])))(M([(15, 42), (19, 41), (21, 55), (19, 58), (17, 55)]) | M([(28, 41), (32, 42), (30, 55), (28, 58), (26, 55)])))  # stole
        part(L, lambda Q: (lambda m: (paint(Q, m, C['gold']), paint(Q, e_right(m) | e_bot(m), C['amber'])))(R(15, 30, 16, 38) | R(13, 32, 18, 33)))
        part(L, lambda Q: belt(Q, 56, 'cream', 'sand', knot=LNn([(16, 57), (15, 64)]) | LNn([(17, 57), (17, 63)])))
        sleeves(L, 'white', 'mist', 'white', cuff='gold')
    elif c == 'rogue':
        part(L, lambda Q: (lambda m: (shade3(Q, m, C['slate'], C['ink'], C['gray'], spine=True), folds(Q, m, [[(18, 45), (14, 64)], [(29, 45), (33, 64)]], C['ink'], C['gray'])))(M([(18, 40), (29, 40), (35, 42), (38, 45), (37, 50), (35, 56), (37, 63), (30, 65), (23.5, 63), (17, 65), (10, 63), (12, 56), (10, 50), (9, 45), (12, 42)])))
        part(L, lambda Q: (shade3(Q, HIPS, C['ink'], C['outline'], C['slate'])))
        part(L, lambda Q: belt(Q, 56, 'wood_dk', 'bark'))
        part(L, lambda Q: (shade3(Q, M([(12, 55), (16, 55), (16, 60), (12, 60)]), C['wood'], C['wood_dk'], C['wood_lt']), shade3(Q, M([(31, 55), (35, 55), (35, 60), (31, 60)]), C['wood'], C['wood_dk'], C['wood_lt'])))  # pouches
        sleeves(L, 'ink', 'outline', 'slate', bell=False)
        for p0, p1, h0 in (((15, 62), (31, 50), (32, 49)), ((32, 62), (16, 50), (15, 49))):
            part(L, lambda Q, p0=p0, p1=p1, h0=h0: (paint(Q, LNn([p0, p1], 2), C['wood_dk']), paint(Q, LNn([p1, h0], 2), C['silver']), paint(Q, P1([(p1[0] / 1.5 - 0.3, p1[1] / 1.5 + 0.7)]) & z(BW, BH), C['gold'])))
    elif c == 'barbarian':
        part(L, lambda Q: (lambda m: (shade3(Q, m, C['wood_lt'], C['wood'], C['tan']), paint(Q, m & (bxs % 3 == 0) & ~e_top(m), C['wood']), paint(Q, e_top(m), C['wood_dk'])))(M([(11, 58), (36, 58), (39, 66), (35, 64), (31, 67), (27, 64), (23, 67), (19, 64), (15, 67), (11, 64), (8, 66)])))   # fur kilt
        part(L, lambda Q: (paint(Q, LNn([(12, 44), (34, 58)], 2), C['wood_dk']), paint(Q, LNn([(12, 43), (34, 57)]) , C['wood'])))                      # harness strap
        part(L, lambda Q: (lambda m: (shade3(Q, m, C['tan'], C['wood_lt'], C['sand']), paint(Q, m & (((bxs + bys) % 4) == 0) & ~e_bot(m), C['wood_lt'])))(M([(15, 39), (32, 39), (38, 43), (39, 47), (36, 46), (34, 49), (31, 46), (27, 49), (23.5, 46), (20, 49), (16, 46), (13, 49), (11, 46), (8, 47), (9, 43)])))
        for fo in (FORE_L, FORE_R): part(L, lambda Q, fo=fo: (paint(Q, fo & (bys >= 55), C['wood']), paint(Q, e_bot(fo) & (bys >= 55), C['wood_dk'])))
        part(L, lambda Q: (paint(Q, LNn([(11, 66), (35, 30)], 2), C['wood']), paint(Q, LNn([(12, 66), (36, 30)]), C['wood_dk'])))
        part(L, lambda Q: (lambda m: (shade3(Q, m, C['silver'], C['gray'], C['mist']), paint(Q, e_right(m) & (bxs >= 40), C['white'])))(M([(33, 28), (38, 22), (43, 24), (44, 30), (42, 36), (37, 34), (35, 32)])))
    elif c == 'druid':
        part(L, lambda Q: robe_body(Q, 'leaf_dk', 'pine', 'leaf', 'wood', flare=20.5))
        part(L, lambda Q: (lambda m: (paint(Q, m, C['wood']), paint(Q, e_right(m) | e_bot(m), C['wood_dk'])))(M([(9, 44), (38, 44), (37, 47), (10, 47)]) & robe_mask()))
        for k, (cx, cy) in enumerate([(11, 44), (16, 43), (21, 44), (26, 44), (31, 43), (36, 44), (13, 47), (34, 47), (23.5, 47)]):
            part(L, lambda Q, cx=cx, cy=cy, k=k: (lambda m: (paint(Q, m, C['lime'] if k % 3 == 0 else C['leaf']), paint(Q, e_right(m) | e_bot(m), C['leaf_dk'] if k % 3 else C['grass'])))(Ell(cx, cy, 2.6, 2.0)))
        part(L, lambda Q: belt(Q, 56, 'leaf', 'leaf_dk', knot=M([(29, 57), (31, 57), (32, 62), (30, 62)])))
        sleeves(L, 'leaf_dk', 'pine', 'leaf', cuff='wood')
        part(L, lambda Q: (paint(Q, LNn([(5, 77), (5, 44), (4, 34), (6, 26)], 2), C['wood']), paint(Q, LNn([(6, 77), (6, 44)]), C['wood_dk'])))
        part(L, lambda Q: (lambda m: (shade3(Q, m, C['lime'], C['leaf'], C['cream'])))(Ell(4.5, 24, 3.2, 2.6) | Ell(8, 26, 2.2, 1.8)))
        part(L, lambda Q: shade3(Q, Ell(6, 55.5, 2.0, 2.0), C['skin3'], C['skin4'], C['skin2']))
    return L
_hb3 = hat_back
def hat_back(c):
    L = _hb3(c)
    return L
