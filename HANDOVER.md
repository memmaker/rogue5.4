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
- Prompt line (RVIP step 5 / W4, 2026-09-26): the live message row is shown in a
  box over the map by `RvipWM.prompt` (rvip-wm.js). A key hides it only while
  the game waits for a command, so a question stays up until answered.
  Here: `be_prompt(r)` from `msg_refresh()` in `port/wcurses.c` (row 0 text),
  `js_key(wc_cmd_prompt)` in `port/be_web.c`; `be_x11.c` has an empty stub.
