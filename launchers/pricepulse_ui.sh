#!/bin/bash
# HUD tile wrapper for PricePulse (added 2026-11-19).
# pricepulse.py is a HUD module: run bare (as the hub does) its __main__ does nothing and
# exits 0; it only opens its window when given the "ui_mode" argument. In ui_mode it opens
# the window directly (no self-relaunch with bare python3).
# One-shot action, no buttons: AS SOON AS IT OPENS it reads the clipboard and, if the clipboard
# holds any text, opens eBay, Walmart and Target search tabs in the browser (keywords from an
# Amazon product URL, else "Cat 8 Ethernet Cable"). The window closes when it loses focus.
# exec keeps one process, so the hub's PID is the app's PID.
set -euo pipefail
F="$HOME/Projects/mac-gui-suite/Aegis-Contextual-HUD/modules/pricepulse.py"
cd "$(dirname "$F")"
exec /opt/homebrew/bin/python3 "$F" ui_mode
