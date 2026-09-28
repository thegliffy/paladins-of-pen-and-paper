from cutlib import *
a = load('monsters'); fg, bg = fg_mask(a)
comps = components(fg)
rows = sorted(comps, key=lambda c: c[1])
r1 = sorted([c for c in comps if c[1] < 340], key=lambda c: c[0]); r2 = sorted([c for c in comps if c[1] >= 340], key=lambda c: c[0])
names = ['goblin','bat','slime','skeleton','wolf','mushroom','golem','imp']
sheet = Image.new('RGBA', (8*80, 70), (90, 90, 100, 255))
for i, (n, c) in enumerate(zip(names, r1 + r2)):
    s = {'golem': 4.5, 'bat': 5.5}.get(n, 5.0)
    im = cut(a, fg, c, s)
    print(n, im.size)
    sheet.alpha_composite(im, (i*80 + (80-im.width)//2, 68-im.height))
sheet.resize((sheet.width*3, sheet.height*3), Image.NEAREST).save('/tmp/t_mon.png')
