#!/usr/bin/env python3
"""Second tileset: DawnHack art (DragonDePlatino, CC BY 3.0; palette by
DawnBringer) as sheeted by Rogue Collection (github.com/mikeyk730/Rogue-Collection,
res/tilemap_v*.bmp: 26 monsters A-Z, then player, walls, items; 16x16).

Writes tiles-dawn.png/.rgba with the same slot layout as tiles.png (mktiles.py),
so the game picks either sheet without code changes. Every slot the game can
show is replaced (the two sets never mix); the rest are other variants' chars.
Usage: mkdawn.py <tilemap_vN.bmp>   (v1: Rogue 3.6/5.2/5.3 monsters, v2: 5.4, v4: PC 1.48)"""
import os, re, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
h = open(os.path.join(HERE, 'tilemap.h')).read()
arr = lambda n: [int(v) for v in re.search(r'%s\[[^]]*\] = \{([^}]*)\}' % n, h).group(1).split(',')]
dfn = lambda n: int(re.search(r'#define %s (\d+)' % n, h).group(1))
PER = dfn('TILES_PER_ROW')

rc = Image.open(sys.argv[1]).convert('RGBA')
src = lambda i: rc.crop((i * 16, 0, i * 16 + 16, 16))
img = Image.open(os.path.join(HERE, 'tiles.png')).convert('RGBA')
put = lambda slot, i: slot >= 0 and img.paste(src(i), ((slot % PER) * 16, (slot // PER) * 16))

for n, slot in enumerate(arr('mon_tile')[:26]):        # A-Z
    put(slot, n)
put(arr('class_tile')[0], 26)                           # player
for k, i in (('TL', 27), ('TR', 28), ('BL', 29), ('BR', 30), ('HWALL', 31), ('VWALL', 32),
             ('FLOOR', 33), ('CORR', 34), ('HDOOR', 35), ('VDOOR', 35)):
    put(dfn('T_' + k), i)
terr, gen = arr('terrain_tile'), arr('generic_tile')
for ch, i in (('%', 36), ('^', 37), ('.', 33), ('#', 34), ('+', 35), ('$', 47)):  # $: detected magic
    put(terr[ord(ch)], i)
for ch, i in ((',', 38), (':', 39), ('*', 40), ('!', 41), ('=', 42), ('?', 43), ('/', 44), (')', 45), (']', 46)):
    put(gen[ord(ch)], i)
for name, i in (('POTION', 41), ('RING', 42), ('SCROLL', 43), ('WAND', 44)):  # every random look
    for s in range(dfn(name + '_TILES'), dfn(name + '_TILES') + dfn(name + '_NTILES')):
        put(s, i)
for s in arr('weap_tile'): put(s, 45)
for s in arr('armor_tile'): put(s, 46)
for s in arr('food_tile'): put(s, 39)

img.save(os.path.join(HERE, 'tiles-dawn.png'))
open(os.path.join(HERE, 'tiles-dawn.rgba'), 'wb').write(
    img.size[0].to_bytes(4, 'little') + img.size[1].to_bytes(4, 'little') + img.tobytes())
print('tiles-dawn.png written from', os.path.basename(sys.argv[1]))
