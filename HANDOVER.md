# Rogue 5.4.5 — RVIP handover (2026-09-25)

Ported after the Advanced Rogue line (`~/Games/arogue7.7`, `arogue5.8`,
`urogue`); same curses shim and frontends, but the classic Rogue data model:

- Build: `./configure` (makes `Makefile` + `config.h`, both ignored), then
  `make rogue54-x11`. The RVIP target lives in `Makefile.in`.
- The map is `stdscr`, messages are on row 0, one status line: the shim
  gets `-DWC_STATUS_ROWS=1`; `rvip.c` defines an empty `msgw` and `morestr`.
- `port/tiles.c` is written for `THING` and `places[]` (`chat()`); monsters
  by letter (`mon_tile[ch - 'A']`). Oryx/Rogue PC tiles cover only 24 of
  the 26 monsters (no snake, no black unicorn), so NetHack tiles.
- `rvip.c` is the Advanced Rogue one with `THING *` instead of linked lists;
  pack letters come from `o_packch`; rings are `P`/`R`.
- `save_file()` saves and exits: `save_state()` (save.c) writes without
  exiting, used by the web autosave.
- **Upstream bug:** `rs_read_daemons()` cleared `d_list[cnt]` after the loop
  (one past the end, ASan). Moved into the loop.
- Web: `md_normaluser()` must not call setgid/setuid (fails in the browser).
- No town, so no music; sound effects only.
