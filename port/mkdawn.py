#!/usr/bin/env python3
"""Second tile set: DawnLike (DragonDePlatino, palette DawnBringer, CC BY 4.0),
sprites picked by name from rvip-tools/tilesets/dawnlike_names.tsv
(names: Tommy Ettinger's DawnLikeAtlas). DawnLike is the full set DawnHack
was cut from, so it replaces DawnHack here.

Writes tiles-dawn.png/.rgba (frame 0) and tiles-dawn-1.png (frame 1, the
opt-in animation) with the same slot layout as tiles.png (mktiles.py).
Every slot the game uses gets a DawnLike sprite, nothing is left NetHack:
tile sets are never mixed. Stand-ins for monsters DawnLike lacks are in MON.
Run after mktiles.py: python3 port/mkdawn.py"""
import os, re, sys, glob
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TS = os.path.expanduser('~/Games/rvip-tools/tilesets')
sys.path.insert(0, TS)
from dawnlike_preview import pos, sprite

h = open(os.path.join(HERE, 'tilemap.h')).read()
arr = lambda n: [int(v) for v in re.search(r'%s\[[^]]*\] = \{([^}]*)\}' % n, h).group(1).split(',')]
dfn = lambda n: int(re.search(r'#define %s (\d+)' % n, h).group(1))
PER = dfn('TILES_PER_ROW')
CSRC = ''.join(open(f, encoding='latin-1').read() for f in sorted(glob.glob(os.path.join(HERE, '..', '*.c'))))

def table(name, plain=False):
    m = re.search(r'\b%s\s*\[[^]]*\]\s*=\s*\{' % name, CSRC)
    if not m: return []
    body = re.sub(r'/\*.*?\*/', '', CSRC[m.end():CSRC.index('};', m.end())], flags=re.S)
    return re.findall(r'"([^"]*)"' if plain else r'\{\s*"([^"]*)"', body)

MON = {  # game name -> DawnLike name, where they differ
 'bat': 'giant bat', 'centaur': 'forest centaur', 'dragon': 'firedrake',
 'invisible stalker': 'stalker', 'mimic': 'large mimic', 'nymph': 'wood nymph',
 'violet fungi': 'violet fungus', 'zombie': 'human zombie',
 'aquator': 'rust monster', 'griffin': 'griffon', 'ice monster': 'ice vortex',
 'kestrel': 'nighthawk', 'phantom': 'ghost', 'quagga': 'gray horse', 'rattlesnake': 'pit viper',
 'venus flytrap': 'large rotting plant', 'xeroc': 'large mimic',
}
WEAP = {'short bow': 'shortbow', 'long bow': 'longbow', 'two-handed sword': 'two handed sword'}
ARMOR = {'leather armor': 'bronze armor', 'ring mail': 'hotrock mail',
         'studded leather armor': 'lacquered armor', 'scale mail': 'scale armor',
         'chain mail': 'grandmaster mail', 'splint mail': 'iron armor',
         'banded mail': 'banded mail', 'plate mail': 'full plate'}
TERRAIN = {'%': 'small stairs down', '^': 'magic trap tile', '$': 'crystal ball',
           '.': 'day tile floor c', '#': 'night stone floor c', '+': 'day tile floor c'}
GENERIC = {'!': 'clear potion', '?': 'blank scroll', ':': 'food ration', ')': 'long sword',
           ']': 'iron armor', ',': 'amulet of yendor', '=': 'gold ring', '/': 'oak wand',
           '*': 'pile of gold coins'}
WALL = 'lit brick wall '
FIXED = {'HWALL': WALL + 'left right', 'VWALL': WALL + 'up down', 'TL': WALL + 'right down',
         'TR': WALL + 'left down', 'BL': WALL + 'right up', 'BR': WALL + 'left up',
         'HDOOR': 'day tile floor c', 'VDOOR': 'day tile floor c',   # doors are gaps
         'FLOOR': 'day tile floor c', 'CORR': 'night stone floor c'}

img = Image.new('RGBA', Image.open(os.path.join(HERE, 'tiles.png')).size, (0, 0, 0, 0))
img1 = img.copy()                   # frame 1: DawnLike's <sheet>1.png where it has one
def sprite1(name):
    sheet, c, r = pos[name]
    p = os.path.join(TS, 'DawnLike', sheet.replace('0.png', '1.png'))
    if not sheet.endswith('0.png') or not os.path.exists(p): return sprite(name)
    return Image.open(p).convert('RGBA').crop((c*16, r*16, c*16+16, r*16+16))
filled, missing = {}, []
def put(slot, name):
    if slot < 0: return
    if name not in pos: missing.append(name); return
    filled[slot] = name
    img.paste(sprite(name), ((slot % PER) * 16, (slot // PER) * 16))
    img1.paste(sprite1(name), ((slot % PER) * 16, (slot // PER) * 16))

# weapon/armour names: the tables mktiles.py read
weap = table('weaps') or table('weap_info') or table('w_names', True)
arm = table('armors') or table('arm_info') or table('a_names', True)
for n, slot in zip(table('monsters'), arr('mon_tile')): put(slot, MON.get(n, n))
put(arr('class_tile')[0], 'fighter')
for n, slot in zip(weap, arr('weap_tile')): put(slot, WEAP.get(n, n))
for n, slot in zip(arm, arr('armor_tile')): put(slot, ARMOR.get(n, n))
terr, gen = arr('terrain_tile'), arr('generic_tile')
for ch, n in TERRAIN.items(): put(terr[ord(ch)], n)
for ch, n in GENERIC.items(): put(gen[ord(ch)], n)
for slot in arr('food_tile'): put(slot, 'food ration')
for k, n in FIXED.items(): put(dfn('T_' + k), n)
# autotiled floors: slot base+m is bordered on the sides of mask m (n8 s4 w2 e1)
for m in range(16):
    sides = ''.join(c for b, c in ((8, 'n'), (4, 's'), (2, 'w'), (1, 'e')) if m & b) or 'c'
    put(dfn('T_FLOORS') + m, 'day tile floor ' + sides)
    put(dfn('T_CORRS') + m, 'night stone floor ' + sides)

# random looks: tiles.c hashes the look's name into a slot range; give each slot
# the sprite named after a look that lands there, else the next unused one
def hslot(s, first, n):
    v = 5381
    for c in s.encode('latin-1'): v = (v * 33 + c) & 0xffffffff
    return first + v % n
for cls, looks, suffix in (('POTION', table('rainbow', True), ' potion'),
                           ('RING', table('stones', True), ' ring'),
                           ('WAND', table('wood', True) + table('metal', True), ' wand'),
                           ('SCROLL', [], ' scroll')):
    first, n = dfn(cls + '_TILES'), dfn(cls + '_NTILES')
    for l in looks:
        nm = l.lower() + suffix
        if nm in pos and hslot(l, first, n) not in filled: put(hslot(l, first, n), nm)
    spare = iter(sorted(k for k in pos if k.endswith(suffix) and k not in filled.values()))
    for s in range(first, first + n):
        if s not in filled: put(s, next(spare))

if missing: sys.exit('no DawnLike sprite (add a stand-in): ' + ', '.join(sorted(set(missing))))
img.save(os.path.join(HERE, 'tiles-dawn.png'))
img1.save(os.path.join(HERE, 'tiles-dawn-1.png'))
open(os.path.join(HERE, 'tiles-dawn.rgba'), 'wb').write(
    img.size[0].to_bytes(4, 'little') + img.size[1].to_bytes(4, 'little') + img.tobytes())
print(len(filled), 'slots, all DawnLike;', len(MON) + len(WEAP) + len(ARMOR), 'stand-ins by hand')
