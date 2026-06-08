#!/usr/bin/env python3
"""
AEGIS Notification Panel v3.0
Persistent alert tray. Receives JSON notifications from the Unix socket
at /tmp/aegis_notif.sock pushed by aegis_notify.py (or any other process).
"""
import tkinter as tk
import threading
import time

_panel_ref = None

LEVEL_COLORS = {
    "info":    "#38bdf8",
    "warn":    "#f59e0b",
    "error":   "#ef4444",
    "success": "#10b981",
}

LEVEL_ICONS = {
    "info":    "ℹ",
    "warn":    "⚠",
    "error":   "✗",
    "success": "✓",
}

BG      = "#0b1120"
SURFACE = "#0f172a"
S2      = "#1e293b"
TEXT    = "#e2e8f0"
MUTED   = "#475569"
PINK    = "#f472b6"


def launch_notification_panel(parent_root: tk.Tk,
                               notifications: list) -> None:
    global _panel_ref
    if _panel_ref is not None and _panel_ref.winfo_exists():
        return

    sw = parent_root.winfo_screenwidth()
    sh = parent_root.winfo_screenheight()

    panel = tk.Toplevel(parent_root)
    _panel_ref = panel
    panel.overrideredirect(True)
    panel.attributes("-topmost", True)
    panel.configure(bg=BG, highlightthickness=1, highlightbackground=PINK)

    w = 500
    h = min(sh - 100, 720)
    x = sw - w - 20
    y = 44
    panel.geometry(f"{w}x{h}+{x}+{y}")

    _dead = [False]

    def close(event=None):
        if _dead[0]:
            return
        _dead[0] = True
        try:
            panel.destroy()
        except Exception:
            pass

    panel.bind("<Escape>", close)

    # Outside-click watcher
    def _watch():
        try:
            from Xlib import display as Xdisplay, X
            dpy  = Xdisplay.Display()
            root = dpy.screen().root
            root.grab_button(X.AnyButton, X.AnyModifier, True,
                             X.ButtonPressMask, X.GrabModeSync,
                             X.GrabModeAsync, X.NONE, X.NONE)
            dpy.sync()
            while not _dead[0]:
                if dpy.pending_events() > 0:
                    ev = dpy.next_event()
                    if ev.type == X.ButtonPress:
                        mx, my = ev.root_x, ev.root_y
                        inside = (x <= mx <= x + w) and (y <= my <= y + h)
                        dpy.allow_events(X.ReplayPointer, X.CurrentTime)
                        dpy.sync()
                        if not inside:
                            parent_root.after(0, close)
                            break
                    else:
                        dpy.allow_events(X.ReplayPointer, X.CurrentTime)
                        dpy.sync()
                else:
                    time.sleep(0.02)
            root.ungrab_button(X.AnyButton, X.AnyModifier)
            dpy.sync()
            dpy.close()
        except Exception:
            pass

    threading.Thread(target=_watch, daemon=True).start()

    # ── Header ────────────────────────────────────────────────────────────────
    hdr = tk.Frame(panel, bg=SURFACE)
    hdr.pack(fill=tk.X)
    tk.Label(hdr, text="◈ AEGIS ALERT LOG",
             bg=SURFACE, fg=PINK,
             font=("JetBrains Mono", 11, "bold")).pack(side=tk.LEFT, padx=14, pady=10)
    tk.Button(hdr, text="✕", bg=SURFACE, fg="#ef4444",
              relief="flat", font=("JetBrains Mono", 11), cursor="hand2",
              command=close).pack(side=tk.RIGHT, padx=10, pady=8)

    # Level filter
    filter_var = tk.StringVar(value="ALL")
    filter_row = tk.Frame(panel, bg=S2)
    filter_row.pack(fill=tk.X)
    tk.Label(filter_row, text="FILTER:", bg=S2, fg=MUTED,
             font=("JetBrains Mono", 7, "bold")).pack(side=tk.LEFT, padx=(10, 4), pady=5)
    for level in ["ALL", "info", "warn", "error", "success"]:
        c = LEVEL_COLORS.get(level, MUTED)
        tk.Radiobutton(filter_row, text=level.upper(),
                       variable=filter_var, value=level,
                       bg=S2, fg=c, selectcolor=S2,
                       activebackground=S2, font=("Inter", 7, "bold"),
                       command=lambda: _refresh(notif_frame, notifications, filter_var.get())
                       ).pack(side=tk.LEFT, padx=4)

    count_str = (f"{len(notifications)} total  ·  "
                 f"{sum(1 for n in notifications if n.get('level') == 'error')} errors  ·  "
                 f"{sum(1 for n in notifications if n.get('level') == 'warn')} warnings")
    tk.Label(panel, text=count_str, bg=BG, fg=MUTED,
             font=("JetBrains Mono", 7)).pack(anchor="w", padx=14, pady=(6, 2))

    # ── Scrollable notifications ───────────────────────────────────────────────
    outer = tk.Frame(panel, bg=BG)
    outer.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

    canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
    sb     = tk.Scrollbar(outer, orient="vertical", command=canvas.yview,
                          bg=S2, troughcolor=BG, width=8)
    notif_frame = tk.Frame(canvas, bg=BG)

    notif_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=notif_frame, anchor="nw",
                          width=w - 40)
    canvas.configure(yscrollcommand=sb.set)
    canvas.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")

    def _sc(e):
        canvas.yview_scroll(-1 if e.num == 4 else 1, "units")
    canvas.bind("<Button-4>", _sc)
    canvas.bind("<Button-5>", _sc)

    def _refresh(container: tk.Frame, notifs: list, level_filter: str):
        for child in container.winfo_children():
            child.destroy()

        filtered = [
            n for n in notifs
            if level_filter == "ALL" or n.get("level") == level_filter
        ]

        if not filtered:
            tk.Label(container, text="No notifications.",
                     bg=BG, fg=MUTED, font=("JetBrains Mono", 9)).pack(pady=20)
            return

        for notif in reversed(filtered[-60:]):
            level = notif.get("level", "info")
            c     = LEVEL_COLORS.get(level, LEVEL_COLORS["info"])
            icon  = LEVEL_ICONS.get(level, "·")

            card = tk.Frame(container, bg=SURFACE, pady=6, padx=10,
                            highlightthickness=1, highlightbackground=c)
            card.pack(fill=tk.X, pady=3)

            top = tk.Frame(card, bg=SURFACE)
            top.pack(fill=tk.X)
            tk.Label(top, text=f"{icon}  {notif.get('title', 'AEGIS')}",
                     bg=SURFACE, fg=c,
                     font=("JetBrains Mono", 9, "bold")).pack(side=tk.LEFT)
            tk.Label(top, text=notif.get("time", ""),
                     bg=SURFACE, fg=MUTED,
                     font=("JetBrains Mono", 7)).pack(side=tk.RIGHT)

            msg = notif.get("message", "")
            if msg:
                tk.Label(card, text=msg, bg=SURFACE, fg=TEXT,
                         font=("Inter", 9), anchor="w",
                         wraplength=w - 60, justify=tk.LEFT).pack(
                             anchor="w", pady=(3, 0))

    _refresh(notif_frame, notifications, "ALL")
    panel.after(60, lambda: canvas.yview_moveto(0.0))
