#!/usr/bin/env python3
"""
AEGIS Contextual HUD — aegis_engine.py  (Definitive Merged Build)
© 2026 Punksm4ck. All rights reserved.

Architecture:
  - Slide-down/up auto-hide HUD at y=0 / y=-HUD_HEIGHT
  - Hover trigger: pointer at y<=1 → slide down; y>HUD_HEIGHT+30 → slide up
  - Xlib dock reservation via _NET_WM_STRUT_PARTIAL so KWin pushes windows down
  - NotificationServer: Unix socket /tmp/aegis_notif.sock, stores up to 200
  - ModuleRegistry: toggle-or-launch pattern, prevents duplicate panels
  - App-aware loop: xdotool tracks active window, injects context buttons
  - Telemetry loop: CPU / RAM / NET KB/s updated every second
  - Buttons: APPS · AI · SYS · ICE · NET · VAULT · NOTES (right-side)
"""

import sys
import os
import subprocess
import psutil
import threading
import time
import datetime
import socket
import json
import tkinter as tk
from Xlib import display as Xdisplay, Xatom
from Xlib.protocol import event as Xevent

AEGIS_DIR   = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.expanduser("~/Scripts")
LOG_FILE    = os.path.expanduser("~/.aegis.log")
NOTIF_SOCK  = __import__("tempfile").gettempdir() + "/aegis_notif.sock"
HUD_HEIGHT  = 42

ICE_WATCH  = "C:/Users/tsann/Scripts/AegisHUDLatest/gui_apps/ice_watch.py"
ICE_PYTHON = "/home/tsann/osiris_apk/build_env/bin/python3"
AI_TERMINAL = os.path.expanduser("~/Scripts/sovereign_nexus_apex.py")

C = {
    "bg":       "#020617", "surface":  "#0f172a", "surface2": "#1e293b",
    "border":   "#00F2FF", "text":     "#e2e8f0", "muted":    "#475569",
    "sky":      "#00F2FF", "violet":   "#a78bfa", "emerald":  "#10b981",
    "amber":    "#f59e0b", "rose":     "#f43f5e", "cyan":     "#06b6d4",
    "indigo":   "#6366f1", "orange":   "#fb923c",
}


# ── Xlib dock reservation ─────────────────────────────────────────────────────

def _configure_as_dock(wid: int, sw: int) -> None:
    """
    Register the HUD window as a DOCK with KWin so it reserves strut space
    and other windows are pushed down by HUD_HEIGHT pixels.
    """
    try:
        dpy = Xdisplay.Display()
        win = dpy.create_resource_object("window", wid)

        def A(name): return dpy.intern_atom(name)

        win.set_wm_class("aegis-hud", "AegisHUD")
        win.change_property(
            A("_NET_WM_WINDOW_TYPE"), Xatom.ATOM, 32,
            [A("_NET_WM_WINDOW_TYPE_DOCK")])
        win.change_property(
            A("_MOTIF_WM_HINTS"), A("_MOTIF_WM_HINTS"), 32,
            [2, 0, 0, 0, 0])
        win.change_property(
            A("_NET_WM_STRUT_PARTIAL"), Xatom.CARDINAL, 32,
            [0, 0, HUD_HEIGHT, 0,   # left right top bottom
             0, 0, 0, 0,            # left_start left_end right_start right_end
             0, sw - 1, 0, 0])      # top_start top_end bottom_start bottom_end
        win.change_property(
            A("_NET_WM_STRUT"), Xatom.CARDINAL, 32,
            [0, 0, HUD_HEIGHT, 0])
        win.change_property(
            A("_NET_WM_STATE"), Xatom.ATOM, 32,
            [A("_NET_WM_STATE_STICKY"),
             A("_NET_WM_STATE_SKIP_TASKBAR"),
             A("_NET_WM_STATE_SKIP_PAGER")])
        win.change_property(
            A("_NET_WM_DESKTOP"), Xatom.CARDINAL, 32,
            [0xFFFFFFFF])
        dpy.sync()
        dpy.close()
    except Exception as exc:
        print(f"[AEGIS] dock config error: {exc}", file=sys.stderr)


# ── Module registry ────────────────────────────────────────────────────────────

class ModuleRegistry:
    def __init__(self, root: tk.Tk):
        self._root    = root
        self._windows: dict[str, tk.Toplevel] = {}

    def is_open(self, key: str) -> bool:
        w = self._windows.get(key)
        return w is not None and w.winfo_exists()

    def register(self, key: str, window: tk.Toplevel) -> None:
        self._windows[key] = window

    def toggle_or_launch(self, key: str, launcher) -> None:
        if self.is_open(key):
            try:
                self._windows[key].destroy()
            except Exception:
                pass
            return
        try:
            launcher()
        except Exception:
            pass


# ── Notification server ───────────────────────────────────────────────────────

class NotificationServer:
    MAX_STORED = 200

    def __init__(self, root: tk.Tk):
        self._root      = root
        self._store:     list[dict] = []
        self._callbacks: list       = []

    @property
    def store(self) -> list[dict]:
        return self._store

    def subscribe(self, cb) -> None:
        self._callbacks.append(cb)

    def start(self) -> None:
        threading.Thread(target=self._serve, daemon=True).start()

    def _serve(self) -> None:
        try:
            if os.path.exists(NOTIF_SOCK):
                os.unlink(NOTIF_SOCK)
            srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            srv.bind(NOTIF_SOCK)
            os.chmod(NOTIF_SOCK, 0o600)
            srv.listen(8)
            srv.settimeout(1)
            while True:
                try:
                    conn, _ = srv.accept()
                    data = b""
                    while True:
                        chunk = conn.recv(4096)
                        if not chunk:
                            break
                        data += chunk
                    conn.close()
                    if data:
                        self._ingest(data)
                except socket.timeout:
                    pass
        except Exception:
            pass

    def _ingest(self, raw: bytes) -> None:
        try:
            payload = json.loads(raw.decode("utf-8"))
            payload["time"] = datetime.datetime.now().strftime("%H:%M:%S")
            self._store.append(payload)
            if len(self._store) > self.MAX_STORED:
                self._store = self._store[-self.MAX_STORED:]
            self._root.after(0, self._dispatch, payload)
        except Exception:
            pass

    def _dispatch(self, payload: dict) -> None:
        for cb in self._callbacks:
            try:
                cb(payload)
            except Exception:
                pass


# ── HUD ───────────────────────────────────────────────────────────────────────

class AegisHUD:
    def __init__(self, root: tk.Tk):
        self.root         = root
        self._reg         = ModuleRegistry(root)
        self._notifs      = NotificationServer(root)
        self._notif_count = 0
        self._sw          = self.root.winfo_screenwidth()
        self._sh          = self.root.winfo_screenheight()
        self.active_wid   = None
        self._net_old     = psutil.net_io_counters()

        # Slide animation state
        self._hidden_y  = -HUD_HEIGHT
        self._visible_y = 0
        self._current_y = self._hidden_y
        self._anim_job  = None

        # Tracked external processes
        self._ice_proc: subprocess.Popen | None = None
        self._ai_proc:  subprocess.Popen | None = None

        # Window setup
        self.root.withdraw()
        self.root.title("AEGIS_HUD")
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", 0.97)
        self.root.attributes("-topmost", True)
        self.root.geometry(f"{self._sw}x{HUD_HEIGHT}+0+{self._current_y}")
        self.root.configure(bg=C["bg"],
                            highlightthickness=1,
                            highlightbackground=C["border"])

        self._build_ui()
        self.root.deiconify()
        self.root.update()
        self.root.update_idletasks()

        # Register as dock (deferred so window ID is stable)
        wid = self.root.winfo_id()
        _configure_as_dock(wid, self._sw)
        self.root.after(1200, lambda: _configure_as_dock(self.root.winfo_id(), self._sw))

        # Start services
        self._notifs.subscribe(self._on_notification)
        self._notifs.start()
        threading.Thread(target=self._telemetry_loop, daemon=True).start()
        threading.Thread(target=self._app_aware_loop,  daemon=True).start()

        # Initial slide sequence
        self.root.after(500,  self._slide_down)
        self.root.after(3000, self._slide_up)
        self.root.after(300,  self._pointer_watcher)

    # ── Slide / hover ─────────────────────────────────────────────────────────

    def _pointer_watcher(self):
        try:
            py = self.root.winfo_pointery()
            if self._current_y == self._visible_y:
                if py > HUD_HEIGHT + 30:
                    self._slide_up()
            elif self._current_y == self._hidden_y:
                if py <= 1:
                    self._slide_down()
        except Exception:
            pass
        self.root.after(150, self._pointer_watcher)

    def _slide_down(self): self._animate_to(self._visible_y)
    def _slide_up(self):   self._animate_to(self._hidden_y)

    def _animate_to(self, target_y: int):
        if self._anim_job:
            self.root.after_cancel(self._anim_job)

        def step():
            dy = target_y - self._current_y
            if abs(dy) < 1:
                self._current_y = target_y
                self.root.geometry(f"{self._sw}x{HUD_HEIGHT}+0+{self._current_y}")
                self._anim_job = None
                return
            self._current_y += int(dy * 0.4) or (1 if dy > 0 else -1)
            self.root.geometry(f"{self._sw}x{HUD_HEIGHT}+0+{self._current_y}")
            self._anim_job = self.root.after(16, step)

        step()

    # ── UI build ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        bar = tk.Frame(self.root, bg=C["bg"])
        bar.pack(fill=tk.BOTH, expand=True)

        # Left: brand + active window + kill
        tk.Label(bar, text="◈ AEGIS",
                 fg=C["sky"], bg=C["bg"],
                 font=("Orbitron", 9, "bold")).pack(side=tk.LEFT, padx=(14, 4))

        self.lbl_app = tk.Label(bar, text="[ INITIALIZING ]",
                                fg=C["emerald"], bg=C["bg"],
                                font=("JetBrains Mono", 9, "bold"))
        self.lbl_app.pack(side=tk.LEFT, padx=6)

        self.btn_kill = tk.Button(bar, text="× KILL",
                                  bg=C["surface"], fg=C["rose"],
                                  relief="flat", font=("JetBrains Mono", 8, "bold"),
                                  cursor="hand2",
                                  command=self._kill_active_app)
        self.btn_kill.pack(side=tk.LEFT, padx=4)

        # Dynamic context buttons (filled by _app_aware_loop)
        self.dynamic_frame = tk.Frame(bar, bg=C["bg"])
        self.dynamic_frame.pack(side=tk.LEFT, fill=tk.Y, padx=12)

        # Right: clock + telemetry + nav buttons
        self.lbl_time = tk.Label(bar, text="00:00:00",
                                 fg=C["text"], bg=C["bg"],
                                 font=("JetBrains Mono", 10, "bold"))
        self.lbl_time.pack(side=tk.RIGHT, padx=14)

        self.lbl_tele = tk.Label(bar,
                                 text="CPU: -% | RAM: -% | NET: -KB/s",
                                 fg=C["muted"], bg=C["bg"],
                                 font=("JetBrains Mono", 8))
        self.lbl_tele.pack(side=tk.RIGHT, padx=8)
        self.lbl_tele.bind("<Button-1>",
                           lambda e: self._launch_sysmon())

        # Nav buttons (right → left order in pack)
        self._hud_btn(bar, "APPS",  C["surface"],  C["sky"],     self._launch_master)
        self._hud_btn(bar, "AI",    "#1a0533",      C["violet"],  self._launch_global_ai)
        self._hud_btn(bar, "SYS",   C["surface"],  C["cyan"],    self._launch_sysmon)
        self._hud_btn(bar, "ICE",   "#064e3b",      C["emerald"], self._launch_ice)
        self._hud_btn(bar, "NET",   C["surface"],  C["cyan"],    self._launch_net)
        self._hud_btn(bar, "VAULT", C["surface"],  C["amber"],   self._launch_vault)
        self._hud_btn(bar, "NOTES", C["surface"],  C["violet"],  self._launch_notes)

    def _hud_btn(self, parent, text: str, bg: str, fg: str, cmd):
        btn = tk.Button(parent, text=text, bg=bg, fg=fg,
                        relief="flat", font=("JetBrains Mono", 8, "bold"),
                        cursor="hand2", command=cmd)
        btn.pack(side=tk.RIGHT, padx=3, pady=6, ipady=2, ipadx=8)
        btn.bind("<Enter>", lambda e, b=btn, f=fg, bg_=bg: b.configure(bg=f, fg=C["bg"]))
        btn.bind("<Leave>", lambda e, b=btn, f=fg, bg_=bg: b.configure(bg=bg_, fg=f))

    # ── Telemetry loop ────────────────────────────────────────────────────────

    def _telemetry_loop(self):
        while True:
            try:
                cpu     = psutil.cpu_percent()
                ram     = psutil.virtual_memory().percent
                net_now = psutil.net_io_counters()
                sent_kb = (net_now.bytes_sent - self._net_old.bytes_sent) / 1024
                self._net_old = net_now
                now = datetime.datetime.now().strftime("%H:%M:%S")

                def _up(c=cpu, r=ram, s=sent_kb, t=now):
                    self.lbl_tele.config(
                        text=f"CPU: {c:.0f}% | RAM: {r:.0f}% | NET: {s:.1f}KB/s")
                    self.lbl_time.config(text=t)

                self.root.after(0, _up)
            except Exception:
                pass
            time.sleep(1)

    # ── App-aware loop ────────────────────────────────────────────────────────

    def _app_aware_loop(self):
        while True:
            try:
                wid = subprocess.check_output(
                    ["xdotool", "getactivewindow"],
                    stderr=subprocess.DEVNULL).decode().strip()
                name = subprocess.check_output(
                    ["xdotool", "getwindowname", wid],
                    stderr=subprocess.DEVNULL).decode("utf-8").strip()
                self.root.after(0, lambda n=name, i=wid: self._update_ctx(n, i))
            except Exception:
                self.root.after(0, lambda: self._update_ctx("SYSTEM IDLE", None))
            time.sleep(0.5)

    def _update_ctx(self, name: str, wid):
        clean = (name[:40] + "…") if len(name) > 40 else name
        self.lbl_app.config(
            text=f"  {clean.upper()}  ",
            fg=C["emerald"] if wid else C["muted"])
        self.active_wid = wid

        for w in self.dynamic_frame.winfo_children():
            w.destroy()
        if not wid:
            return

        lname = name.lower()
        if "konsole" in lname or "terminal" in lname:
            self._ctx_btn("▶ TERMINAL AI", C["sky"],     "TERMINAL")
        elif "kate" in lname or "code" in lname or "vscode" in lname:
            self._ctx_btn("⌥ CODE SURGEON", C["emerald"], "CODING")
        elif "firefox" in lname or "chromium" in lname or "chrome" in lname:
            self._ctx_btn("⊕ WEB AI",       C["amber"],   "GLOBAL")

    def _ctx_btn(self, text: str, fg: str, ctx: str):
        b = tk.Button(self.dynamic_frame, text=text,
                      bg=C["surface2"], fg=fg,
                      relief="flat", font=("JetBrains Mono", 8, "bold"),
                      cursor="hand2",
                      command=lambda: self._launch_ai(ctx))
        b.pack(side=tk.LEFT, padx=3)

    # ── Launchers ─────────────────────────────────────────────────────────────

    def _launch_ai(self, ctx: str = "GLOBAL"):
        # Reuse existing window if still alive
        if self._ai_proc is not None and self._ai_proc.poll() is None:
            return
        target = AI_TERMINAL
        if not os.path.exists(target):
            fallback = "C:/Users/tsann/Scripts/AegisHUDLatest/gui_apps/Aegis-Contextual-HUD/ai_terminal.py"
            target = fallback if os.path.exists(fallback) else None
        if not target:
            print("[AEGIS] ai_terminal.py not found", file=sys.stderr)
            return
        self._ai_proc = subprocess.Popen(
            [sys.executable, target, ctx],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _launch_global_ai(self):
        self._launch_ai("GLOBAL")

    def _kill_active_app(self):
        if self.active_wid:
            subprocess.Popen(["xdotool", "windowkill", self.active_wid])

    def _launch_master(self):
        hub_path = os.path.join(AEGIS_DIR, "aegis_master_hub.py")
        if not os.path.exists(hub_path):
            hub_path = os.path.expanduser("~/Scripts/AegisHUDLatest/aegis_master_hub.py")
        subprocess.Popen([sys.executable, hub_path],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _launch_sysmon(self):
        from aegis_sysmon import launch_sysmon_panel
        self._reg.toggle_or_launch("sys", lambda: launch_sysmon_panel(self.root))

    def _launch_ice(self):
        if self._ice_proc is not None and self._ice_proc.poll() is None:
            return
        if not os.path.exists(ICE_WATCH):
            print(f"[AEGIS] ICE Watch not found: {ICE_WATCH}", file=sys.stderr)
            return
        interp = ICE_PYTHON if os.path.exists(ICE_PYTHON) else sys.executable
        self._ice_proc = subprocess.Popen(
            [interp, ICE_WATCH],
            cwd=os.path.dirname(ICE_WATCH))

    def _launch_net(self):
        self._launch_module("network_monitor", "launch_network_monitor")

    def _launch_vault(self):
        self._launch_module("clipboard_vault", "launch_vault_ui")

    def _launch_notes(self):
        self._launch_module("notes_overlay", "launch_notes_overlay")

    def _launch_module(self, module_name: str, func_name: str):
        try:
            import importlib
            mod = importlib.import_module(module_name)
            getattr(mod, func_name)(self.root)
        except Exception as exc:
            print(f"[AEGIS] {module_name}.{func_name} error: {exc}", file=sys.stderr)

    # ── Notification handler ──────────────────────────────────────────────────

    def _on_notification(self, payload: dict):
        self._notif_count += 1
        # Future: flash a badge or open notification panel automatically


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    AegisHUD(root)
    root.mainloop()


if __name__ == "__main__":
    main()

