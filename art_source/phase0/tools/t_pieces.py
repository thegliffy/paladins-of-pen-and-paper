from cutlib import *
def rowsplit(comps, ys):
    rows = [[] for _ in range(len(ys)+1)]
    for c in comps:
        k = sum(c[1] >= y for y in ys); rows[k].append(c)
    return [sorted(r, key=lambda c: c[0]) for r in rows]
out = {}
a = load('table'); fg, _ = fg_mask(a); r = rowsplit(components(fg), [270, 465])
print(r)
T = r[0][0]
out['table_a'] = cut(a, fg, T, 0, size=(300, 44))
out['table_b'] = cut(a, fg, T, 572/150)
out['gm'] = cut(a, fg, r[1][0], 6.5)
out['screen'] = cut(a, fg, r[1][1], 8.0)
for i, c in enumerate(r[1][2:5]):
    s = max(c[2]-c[0], c[3]-c[1]) / 15.5
    out['d20_%d' % i] = cut(a, fg, c, s, dark_frac=0.4)
a = load('seats'); fg, _ = fg_mask(a); comps = sorted(components(fg), key=lambda c: c[0])
for n, c in zip(['paladin','wizard','ranger','bard'], comps): out['seat_'+n] = cut(a, fg, c, 8.5)
a = load('map'); fg, _ = fg_mask(a); r = rowsplit(components(fg), [260, 450])
for n, c in zip(['tavern','village','cave','castle','windmill','shrine'], r[0]): out['loc_'+n] = cut(a, fg, c, 6.6, allowed=[i for i in pal.NOPINK])
for i, c in enumerate(r[2]): out['pawn_%d' % i] = cut(a, fg, c, 8.4)
x = 4
sheet = Image.new('RGBA', (1000, 150), (90, 90, 100, 255)); y = 4; rowh = 0
for k, im in out.items():
    print(k, im.size)
    if x + im.width > 996: x = 4; y += rowh + 4; rowh = 0
    sheet.alpha_composite(im, (x, y)); x += im.width + 4; rowh = max(rowh, im.height)
sheet = sheet.crop((0, 0, 1000, y + rowh + 4))
sheet.resize((sheet.width*2, sheet.height*2), Image.NEAREST).save('/tmp/t_pieces1.png')
