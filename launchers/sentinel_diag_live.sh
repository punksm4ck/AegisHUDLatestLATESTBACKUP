#!/bin/bash
# HUD tile wrapper for Sentinel Diag (added 2026-11-19).
# The hub can only run `bash <file>` / `<python> <file>` with no arguments, but
# sentinel_diagnostics.py exits with "the following arguments are required: command"
# unless given a subcommand. "live" is its Qt GUI: opening it only builds the window
# and reads the local Sentinel config. The watcher check/auto-launch, Sightengine API
# calls and test-image fetch run only when the window's Run button is pressed.
# exec keeps one process, so the hub's PID is the app's PID.
set -euo pipefail
PROJ="$HOME/Projects/mac-gui-suite/sentinel-diag"
cd "$PROJ"
exec "$PROJ/.venv/bin/python" "$PROJ/sentinel_diagnostics.py" live
