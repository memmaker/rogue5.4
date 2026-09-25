#!/bin/sh
# Rogue 5.4, X11 frontend (curses shim, port/): tiled map on top,
# Messages + Status below left, Inventory right (layout in port/be_x11.c;
# override with XROGUE_MAP/_MSG/_STATUS/_INV="x,y"). Saves and scores in save/.
cd "$(dirname "$0")" || exit 1
mkdir -p save
export HOME="$PWD/save" ROGUEHOME="$PWD/save"
if [ -f save/rogue.save ]; then exec ./rogue54-x11 save/rogue.save "$@"; fi
exec ./rogue54-x11 "$@"
