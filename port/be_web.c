/* Browser frontend for the curses shim (RVIP step 7): web/xrogue.js draws
 * the panes (Module.xr); input waits with Asyncify. The save file doubles
 * as an autosave: kept while playing, removed when the game ends unless
 * the player saved with S. */
#include <emscripten.h>
#include <stdio.h>
#include <unistd.h>
#include <curses.h>
#include "../rogue.h"

EM_JS(void, js_init, (int p, int c, int r), { Module.xr.init(p, c, r); });
EM_JS(void, js_put, (int p, int y, int x, int ch, int t, int u), { Module.xr.put(p, y, x, ch, t, u); });
EM_JS(void, js_cursor, (int p, int y, int x), { Module.xr.cursor(p, y, x); });
EM_JS(void, js_popup, (int r, int c), { Module.xr.popup(r, c); });
EM_JS(void, js_flush, (int lvl, int music, int hy, int hx), { Module.xr.flush(lvl, music, hy, hx); });
EM_JS(int, js_key, (void), { return Module.xr.key(); });
EM_JS(int, js_want_save, (void), { return Module.xr.wantSave(); });
EM_JS(void, js_sound, (const char *s), { Module.xr.sound(UTF8ToString(s)); });
EM_JS(void, js_end, (int saved, int dead), { Module.xr.end(saved, dead); });

void be_init(int p, int cols, int rows) { js_init(p, cols, rows); }
void be_put(int p, int y, int x, chtype ch, int tile, int under) { js_put(p, y, x, ch, tile, under); }
void be_cursor(int p, int y, int x) { js_cursor(p, y, x); }
void be_popup(int rows, int cols) { js_popup(rows, cols); }
void be_sound(const char *s) { if (*s) js_sound(s); }

/* Visible window (RVIP 5b): monsters and objects drawn on the player's
 * view right now (invisible monsters and mimics fail the screen check) */
EM_JS(void, js_vis, (const char *s), { if (Module.xr.vis) Module.xr.vis(UTF8ToString(s)); });
static void send_visible(void)
{
    static char buf[4096];
    int n = 0, cy, cx;
    THING *l;
    getyx(stdscr, cy, cx);
    for (l = mlist; l != NULL && n < 3900; l = next(l)) {
        THING *tp = (l);
        if ((mvwinch(stdscr, tp->t_pos.y, tp->t_pos.x) & 0xff) == (tp->t_type & 0xff))
            n += snprintf(buf + n, sizeof buf - n, "M%c%s\n", tp->t_type, monsters[tp->t_type - 'A'].m_name);
    }
    for (l = lvl_obj; l != NULL && n < 3900; l = next(l)) {
        THING *o = (l);
        if ((mvwinch(stdscr, o->o_pos.y, o->o_pos.x) & 0xff) == (o->o_type & 0xff))
            n += snprintf(buf + n, sizeof buf - n, "I%c\n", o->o_type);
    }
    wmove(stdscr, cy, cx);
    buf[n] = 0;
    js_vis(buf);
}

void be_flush(void)
{
    send_visible();
    /* town music on the trading post and the outside levels */
    js_flush(level, 0, hero.y - 1, hero.x);
}

/* Save without quitting, like auto_save() on SIGHUP but keep playing. */
static void autosave(void)
{
    FILE *f;
    int y, x;
    if (!file_name[0] || pstats.s_hpt <= 0 || !(f = fopen(file_name, "wb"))) return;
    getyx(stdscr, y, x);
    save_state(f);              /* closes f */
    wmove(stdscr, y, x);
    wrefresh(stdscr);
}

int be_getkey(int wait)
{
    static double last;
    int k;
    for (;;) {
        if (wc_cmd_prompt && js_want_save()) autosave();
        if ((k = js_key()) >= 0) return k;
        if (!wait) {                /* polling (explore, running): let the page paint */
            if (emscripten_get_now() - last > 50) {
                last = emscripten_get_now();
                emscripten_sleep(0);
            }
            return -1;
        }
        emscripten_sleep(10);
    }
}

void be_end(void)
{
    if (!wc_saved) unlink(file_name);   /* died or quit: the game is over */
    js_end(wc_saved, pstats.s_hpt <= 0);
}
