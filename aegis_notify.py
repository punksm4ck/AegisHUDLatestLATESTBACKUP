#!/usr/bin/env python3
"""
AEGIS Notification Helper v3.0
Push alerts to the HUD from any process.

Python usage:
    from aegis_notify import notify
    notify("OSIRIS", "Tracker position updated", level="info")

CLI usage:
    python3 aegis_notify.py "TITLE" "Message body" "warn"

Levels: info | warn | error | success
"""
import socket
import json
import sys

NOTIF_SOCKET = __import__("tempfile").gettempdir() + "/aegis_notif.sock"
VALID_LEVELS = frozenset(["info", "warn", "error", "success"])


def notify(title: str, message: str, level: str = "info") -> bool:
    """
    Send a notification to the running AEGIS HUD.
    Returns True on success, False if the HUD is not reachable.
    """
    if level not in VALID_LEVELS:
        level = "info"
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect(NOTIF_SOCKET)
        payload = json.dumps({
            "title":   str(title),
            "message": str(message),
            "level":   level,
        }).encode("utf-8")
        s.sendall(payload)
        s.close()
        return True
    except Exception:
        return False


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        print("Usage: aegis_notify.py <title> <message> [level]")
        print(f"Levels: {', '.join(sorted(VALID_LEVELS))}")
        sys.exit(0)

    title   = args[0]
    message = args[1]
    level   = args[2] if len(args) > 2 else "info"

    ok = notify(title, message, level)
    if not ok:
        print("Warning: AEGIS HUD not reachable (socket not found).", file=sys.stderr)
