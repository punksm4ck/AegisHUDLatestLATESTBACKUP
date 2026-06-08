#!/usr/bin/env python3
"""
AEGIS System Monitor Panel v3.0
Full system drill-down: per-core CPU, RAM, disk, top processes, temps, network.
Launched from the SYS button or clicking the CPU/RAM telemetry label.
"""
import tkinter as tk
import psutil
import threading
import time
import subprocess

_panel_ref = None

BG      = "#020617"
SURFACE = "#0f172a"
S2      = "#1e293b"
TEXT    = "#e2e8f0"
MUTED   = "#64748b"
GREEN   = "#22c55e"
YELLOW  = "#f59e0b"
RED     = "#ef4444"
BLUE    = "#38bdf8"
PURPLE  = "#a78bfa"
CYAN    = "#06b6d4"


def _color_pct(pct: float, warn: float = 70, crit: float = 85) -> str:
    if pct >= crit:
        return RED
    if pct >= warn:
        return YELLOW
    return GREEN


def _fmt_bytes(b: float) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024:
            return f"{b:.1f}{unit}"
        b /= 1024
    return f"{b:.1f}PB"


def _make_panel(parent_root: tk.Tk) -> tk.Toplevel:
    """Build and return the Toplevel panel (does not start update loop)."""
    global _panel_ref

    sw = parent_root.winfo_screenwidth()
    sh = parent_root.winfo_screenheight()

    panel = tk.Toplevel(parent_root)
    _panel_ref = panel
    panel.overrideredirect(True)
    panel.attributes("-topmost", True)
    panel.configure(bg=BG, highlightthickness=1, highlightbackground=BLUE)

    w, h = 700, min(sh - 100, 860)
    x = (sw - w) // 2
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
    def _watch_clicks():
        try:
            from Xlib import display as Xd, X
            dpy  = Xd.Display()
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

    threading.Thread(target=_watch_clicks, daemon=True).start()

    # ── Header ───────────────────────────────────────────────────────────────
    hdr = tk.Frame(panel, bg=SURFACE)
    hdr.pack(fill=tk.X)
    tk.Label(hdr, text="◈ AEGIS SYSTEM MONITOR",
             bg=SURFACE, fg=BLUE, font=("JetBrains Mono", 11, "bold")).pack(
                 side=tk.LEFT, padx=14, pady=10)
    tk.Button(hdr, text="✕", bg=SURFACE, fg=RED,
              relief="flat", font=("JetBrains Mono", 11), cursor="hand2",
              command=close).pack(side=tk.RIGHT, padx=10, pady=8)
    tk.Button(hdr, text="↻ REFRESH", bg=SURFACE, fg=MUTED,
              relief="flat", font=("Inter", 8, "bold"), cursor="hand2",
              command=lambda: _refresh(content_frame, panel, parent_root, w, close)).pack(
                  side=tk.RIGHT, padx=6, pady=8)

    # ── Scrollable body ───────────────────────────────────────────────────────
    outer = tk.Frame(panel, bg=BG)
    outer.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

    canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
    sb     = tk.Scrollbar(outer, orient="vertical", command=canvas.yview,
                          bg=S2, troughcolor=BG, width=8)

    content_frame = tk.Frame(canvas, bg=BG)
    content_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.create_window((0, 0), window=content_frame, anchor="nw",
                         width=w - 40, tags="inner")
    canvas.configure(yscrollcommand=sb.set)
    canvas.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")

    def _sc(e):
        canvas.yview_scroll(-1 if e.num == 4 else 1, "units")
    canvas.bind("<Button-4>", _sc)
    canvas.bind("<Button-5>", _sc)

    _populate(content_frame, panel, parent_root, w, close)

    panel.after(60, lambda: canvas.yview_moveto(0))
    return panel


def _section(parent: tk.Frame, title: str, color: str = BLUE) -> tk.Frame:
    f = tk.Frame(parent, bg=BG)
    f.pack(fill=tk.X, pady=(12, 3))
    tk.Label(f, text=title, bg=BG, fg=color,
             font=("JetBrains Mono", 8, "bold")).pack(side=tk.LEFT, padx=2)
    tk.Frame(f, bg=S2, height=1).pack(fill=tk.X, expand=True, pady=(10, 0))
    return f


def _bar_row(parent: tk.Frame, label: str, pct: float,
             color: str = None, detail: str = "") -> None:
    color = color or _color_pct(pct)
    row = tk.Frame(parent, bg=BG)
    row.pack(fill=tk.X, pady=1)
    tk.Label(row, text=label, bg=BG, fg=MUTED,
             font=("JetBrains Mono", 8), width=20, anchor="w").pack(side=tk.LEFT)
    bar_bg = tk.Frame(row, bg=S2, height=10, width=280)
    bar_bg.pack(side=tk.LEFT, padx=4)
    bar_bg.pack_propagate(False)
    fill_w = int(280 * min(max(pct, 0), 100) / 100)
    if fill_w > 0:
        tk.Frame(bar_bg, bg=color, height=10, width=fill_w).place(x=0, y=0)
    tk.Label(row, text=f"{pct:.1f}%  {detail}", bg=BG, fg=color,
             font=("JetBrains Mono", 8)).pack(side=tk.LEFT, padx=4)


def _populate(frame: tk.Frame, panel, parent_root, w: int, close_fn) -> None:
    """Populate the scrollable frame with current system data."""

    # ── CPU ──────────────────────────────────────────────────────────────────
    _section(frame, "CPU", BLUE)
    cpu_pct = psutil.cpu_percent(interval=0.3)
    freq    = psutil.cpu_freq()
    freq_s  = f"{freq.current:.0f} MHz" if freq else ""
    _bar_row(frame, f"Total  ({psutil.cpu_count()}c)", cpu_pct, detail=freq_s)

    per_core = psutil.cpu_percent(percpu=True, interval=0)
    for i, pct in enumerate(per_core):
        _bar_row(frame, f"Core {i}", pct)

    # ── Temps ─────────────────────────────────────────────────────────────────
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            _section(frame, "TEMPERATURES", YELLOW)
            for name, entries in temps.items():
                for e in entries[:4]:
                    t = e.current
                    c = RED if t > 80 else YELLOW if t > 65 else GREEN
                    lbl = f"{name}/{e.label}" if e.label else name
                    _bar_row(frame, lbl[:20], t, color=c,
                             detail=f"{t:.0f}°C")
    except Exception:
        pass

    # ── RAM ───────────────────────────────────────────────────────────────────
    _section(frame, "MEMORY", PURPLE)
    mem = psutil.virtual_memory()
    _bar_row(frame, "Used",
             mem.percent, detail=f"{_fmt_bytes(mem.used)} / {_fmt_bytes(mem.total)}")
    _bar_row(frame, "Available",
             (mem.available / mem.total) * 100, color=GREEN,
             detail=_fmt_bytes(mem.available))
    try:
        swap = psutil.swap_memory()
        if swap.total > 0:
            _bar_row(frame, "Swap",
                     swap.percent,
                     detail=f"{_fmt_bytes(swap.used)} / {_fmt_bytes(swap.total)}")
    except Exception:
        pass

    # ── Disk ──────────────────────────────────────────────────────────────────
    _section(frame, "DISK")
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            label = part.mountpoint[:20]
            _bar_row(frame, label, usage.percent,
                     detail=f"{_fmt_bytes(usage.used)} / {_fmt_bytes(usage.total)}")
        except Exception:
            pass

    # ── Top Processes ─────────────────────────────────────────────────────────
    _section(frame, "TOP PROCESSES", PURPLE)

    hdr = tk.Frame(frame, bg=S2)
    hdr.pack(fill=tk.X, pady=(2, 1))
    for col, col_w in [("PID", 6), ("NAME", 22), ("CPU%", 6), ("RAM%", 6),
                       ("THREADS", 8), ("STATUS", 10)]:
        tk.Label(hdr, text=col, bg=S2, fg=MUTED,
                 font=("JetBrains Mono", 7, "bold"),
                 width=col_w, anchor="w").pack(side=tk.LEFT, padx=2, pady=3)

    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent",
                                    "memory_percent", "num_threads", "status"]):
        try:
            procs.append(p.info)
        except Exception:
            pass
    procs.sort(key=lambda x: x.get("cpu_percent") or 0, reverse=True)

    for proc in procs[:25]:
        cpu_p = proc.get("cpu_percent") or 0
        ram_p = proc.get("memory_percent") or 0
        c     = _color_pct(cpu_p, 20, 50)
        row   = tk.Frame(frame, bg=BG)
        row.pack(fill=tk.X, pady=1)

        for txt, col_w in [
            (str(proc.get("pid", "")),           6),
            (str(proc.get("name", ""))[:22],     22),
            (f"{cpu_p:.1f}",                     6),
            (f"{ram_p:.1f}",                     6),
            (str(proc.get("num_threads", "?")),  8),
            (str(proc.get("status", ""))[:10],   10),
        ]:
            tk.Label(row, text=txt, bg=BG, fg=c if "." in txt else TEXT,
                     font=("JetBrains Mono", 7), width=col_w,
                     anchor="w").pack(side=tk.LEFT, padx=2)

        def _kill(pid=proc.get("pid")):
            try:
                subprocess.call(["kill", "-9", str(pid)])
            except Exception:
                pass
            # Rebuild
            for child in frame.winfo_children():
                child.destroy()
            _populate(frame, panel, parent_root, w, close_fn)

        tk.Button(row, text="KILL", bg="#450a0a", fg=RED,
                  font=("Inter", 6, "bold"), relief="flat", cursor="hand2",
                  command=_kill).pack(side=tk.LEFT, padx=3)

    # ── Network ───────────────────────────────────────────────────────────────
    _section(frame, "NETWORK INTERFACES", CYAN)
    try:
        net_io = psutil.net_io_counters(pernic=True)
        net_if = psutil.net_if_addrs()
        for nic, stats in net_io.items():
            if stats.bytes_sent == 0 and stats.bytes_recv == 0:
                continue
            row = tk.Frame(frame, bg=BG)
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=nic[:16], bg=BG, fg=MUTED,
                     font=("JetBrains Mono", 8), width=18, anchor="w").pack(side=tk.LEFT)
            tk.Label(row,
                     text=f"↑ {_fmt_bytes(stats.bytes_sent)}   ↓ {_fmt_bytes(stats.bytes_recv)}",
                     bg=BG, fg=CYAN, font=("JetBrains Mono", 8)).pack(side=tk.LEFT, padx=8)
            # Show first IP
            addrs = net_if.get(nic, [])
            for addr in addrs:
                if "." in addr.address and not addr.address.startswith("127."):
                    tk.Label(row, text=addr.address, bg=BG, fg=MUTED,
                             font=("JetBrains Mono", 7)).pack(side=tk.LEFT)
                    break
    except Exception:
        pass


def _refresh(frame: tk.Frame, panel, parent_root, w: int, close_fn) -> None:
    for child in frame.winfo_children():
        child.destroy()
    _populate(frame, panel, parent_root, w, close_fn)


def launch_sysmon_panel(parent_root: tk.Tk) -> None:
    global _panel_ref
    if _panel_ref is not None and _panel_ref.winfo_exists():
        return
    _make_panel(parent_root)
