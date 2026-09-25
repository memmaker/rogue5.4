# Rogue 5.4 — RVIP port

Upstream: Rogue 5.4.5 (Toy, Arnold, Wichman; rogueforge), from the Roguelike
Restoration Project: https://github.com/RoguelikeRestorationProject/rogue5.4/tree/9d0dccc

**Our changes:** https://github.com/memmaker/rogue5.4/compare/9d0dccc...master
(commit 1 is the untouched upstream; everything after it is ours).

- `port:` builds on macOS/arm64 and WebAssembly, curses shim (`port/`) with
  an X11 frontend, NetHack tiles (`port/mktiles.py`); fixes an upstream
  out-of-bounds write when restoring a save (`rs_read_daemons`).
- `RVIP:` auto-explore (`x`), `<`/`>` walk to known stairs, Enter command
  menu, inventory with a cursor, sound events (`rvip.c` + small hooks).
- `web:` browser build (`web/build.sh`), played at https://ruzzoli.de/roguelikes/rogue54/

Tile sets: NetHack (default) or DawnHack (DragonDePlatino, palette DawnBringer, CC BY 3.0,
via Rogue Collection; `port/mkdawn.py`, credits in `port/dawnhack/CREDITS.txt`). Web: *Tiles* button;
desktop: `TILESET=dawn ./play.sh` or `echo dawn > save/tileset`.

Build: `./configure && make rogue54-x11` (XQuartz), `./play.sh`; web: `sh web/build.sh`, `web/deploy.sh`.
Notes for the next person: `HANDOVER.md`. Process: `~/Games/RVIP.md`, `~/Games/rogue2wasm.md`.
