#!/usr/bin/env python3
import tkinter as tk
import os
import subprocess
import threading
import time
import sys
import re

_hub_ref = None

BG, SURFACE, S2 = "#0b1120", "#0f172a", "#1e293b"
TEXT, MUTED, BLUE, BORDER = "#e2e8f0", "#475569", "#3b82f6", "#1e3a5f"
ACCENT_COLORS = ["#10b981", "#38bdf8", "#a78bfa", "#f43f5e", "#06b6d4", "#f59e0b", "#ec4899", "#ff0055", "#00d4ff"]

# =========================================================
# 🚀 FULLY MERGED REGISTRY: 73 TOOLS
# (Legacy Baseline + New Orphaned Modules)
# =========================================================
MASTER_REGISTRY = [
    # --- NEW & ORPHANED MODULES (From Audit) ---
    ("Aegis Command Center", ["~/Scripts/aegis_command_center.py"]),
    ("Aegis Sentinel Apex Nexus", ["~/Scripts/build_aegis_v23_nexus.py", "~/Scripts/build_aegis_v22_omnilink.py", "~/Scripts/build_aegis_v21_apex.py"]),
    ("Aegis Sentinel C2 Arrays", ["~/Scripts/build_aegis_zenith.py", "~/Scripts/build_aegis_v20_globus.py", "~/Scripts/build_aegis_v19_continental.py", "~/Scripts/build_aegis_v18_sovereign_ii.py"]),
    ("Aether Orchestrator", ["~/Scripts/aether_orchestrator.py"]),
    ("AI Watcher Diagnostic", ["~/Scripts/watcher_diagnostics.py"]),
    ("Enterprise WiFi Manager", ["~/Scripts/enterprise_wifi_manager.py", "~/Scripts/wifi_tray.py"]),
    ("Mic HUD", ["~/Scripts/mic_manager.py"]),
    ("Network Guardian", ["~/Scripts/network_guardian_gui.py", "~/Scripts/network_guardian_gui_BACKUP.py"]),
    ("OSIRIS Diagnostic Surgeon", ["~/Scripts/osiris_diagnostic_surgeon.py"]),
    ("OSIRIS Nuclear Command", ["~/Scripts/open_multi_agent_gui.py"]),
    ("Singularity Master", ["~/singularity_master.py"]),
    ("SSOC Command", ["~/Scripts/ssoc.py"]),

    # --- ORIGINAL BASELINE APPS ---
    ("Aether Singularity Suite", ["~/Scripts/aether_singularityv1.py", "~/Scripts/aether_singularity.py", "~/Scripts/AetherSuite/main.py", "~/Scripts/Osiris-GUI-Suite/aether_singularity.py"]),
    ("AI Datacenter Tracker", ["~/Scripts/DatacenterTracker/main.py", "~/Scripts/AI_Datacenter_Tracker/main.py"]),
    ("AI-SPY", ["~/Scripts/ai_watcher_enterprise.py", "~/Scripts/ai_watcher_enterprise_v5.py", "~/Scripts/AegisHUDLatest/ai_watcher_enterprise_v5.py"]),
    ("AI Terminal", ["~/Scripts/AegisHUDLatest/ai_terminal.py", "~/Scripts/ai_terminal.py"]),
    ("AI Water Tracker", ["~/Scripts/WaterTracker/main.py", "~/Scripts/Water-Tracker/main.py"]),
    ("APK Architect Pro", ["~/Scripts/apk_architect.py", "~/Scripts/ApkArchitect/main.py", "~/Scripts/APKArchitect/main.py"]),
    ("ColorNote Matrix", ["/home/tsann/.local/share/applications/colornote-osiris.desktop"]),
    ("CSS Server Browser", ["~/Scripts/css_server_browser2.py", "~/Scripts/css_server_browser.py", "~/Scripts/Osiris-GUI-Suite/css_server_browser.py", "~/Scripts/SteamServerBrowser/main.py"]),
    ("CX Operations Module", ["~/Scripts/job_listings_app.py", "~/Scripts/cx-ops/main.py", "~/Scripts/CXOps/main.py", "~/Scripts/JobListings/main.py"]),
    ("Facial Rec GUI", ["~/Scripts/facial-rec-gui/main.py", "~/Scripts/FacialRec/main.py", "~/Scripts/FaceRec/main.py"]),
    ("FNV Mod Manager", ["~/FNV_OSIRIS_Mod_Manager.py", "~/Scripts/FNV_OSIRIS_Mod_Manager.py"]),
    ("Ghost Framework", ["~/Scripts/Ghost/main.py", "~/Scripts/GhostFramework/main.py"]),
    ("Grid Walker", ["~/Scripts/Grid_Walkerv2.py", "~/Scripts/Grid_Walker.py", "~/Scripts/GridWalker/main.py", "~/Scripts/Osiris-GUI-Suite/grid_walker.py"]),
    ("Gun Stats GUI", ["~/Scripts/gun_stats_gui.py", "~/Scripts/GunStats/main.py", "~/Scripts/Osiris-GUI-Suite/gun_stats.py"]),
    ("HEPHAESTUS Forge", ["~/Scripts/Hephaestus/main.py", "~/Scripts/HEPHAESTUS/main.py"]),
    ("Heuristic Diagnostic UI", ["~/Scripts/diagnostic_tool_mockup.py", "~/Scripts/AegisHUDLatest/diagnostic_tool_mockup.py"]),
    ("Heuristic Reporter", ["~/Scripts/auto_diagnostic_reporter.py", "~/Scripts/AegisHUDLatest/auto_diagnostic_reporter.py"]),
    ("ICE Detention Tracker", ["~/Scripts/ICEDetentionCenterTracker/main.py", "~/Scripts/ICEDetentionGUI/ICEDetentionCenterTracker/main.py", "~/Scripts/ICEDetentionGUI/main.py"]),
    ("ICE Watch", ["~/Scripts/ice_watch.py", "~/Scripts/AegisHUDLatest/ice_watch.py"]),
    ("Inbox Zero", ["~/Scripts/aegis_inbox_zero_enterprise.py", "~/Scripts/inbox_zero.py", "~/Scripts/inbox_zero_public.py", "~/Scripts/inbox_zero_gmail2.py", "~/Scripts/InboxZero/main.py", "~/Scripts/Inbox-Zero/main.py"]),
    ("JobNexus Enterprise", ["~/Scripts/JohsNexus_GUI/main.py", "~/Scripts/JohsNexus_GUI/launch_jobnexus.py", "~/Scripts/JobNexus_GUI/launch_jobnexus.py"]),
    ("LVT Clone UI", ["~/Scripts/LVT_Clone/main.py", "~/Scripts/LVT_Clone/app.py"]),
    ("Meme Sync Pro", ["~/Scripts/meme_sync_gui.py", "~/Scripts/MemeSyncMaster/main.py"]),
    ("Mohuan LED Dashboard", ["~/Scripts/MohuanLED/main.py", "~/Scripts/Osiris-GUI-Suite/mohuan_led_dashboard.py"]),
    ("NAS Drive GUI", ["~/Scripts/Osiris-GUI-Suite/GDrive_clone_GUI/NASDriveGUI.py", "~/Scripts/NASDriveGUI/main.py"]),
    ("Network GUI", ["~/Scripts/Osiris-GUI-Suite/network_gui.py", "~/Scripts/NetworkGUI/main.py"]),
    ("Network Sentry", ["~/Scripts/NetSentry/main.py", "~/Scripts/NetworkSentry/main.py"]),
    ("OmniFeed Pro", ["~/Scripts/OmniFeedPro.py", "~/Scripts/Omnifeed/main.py", "~/Scripts/OmniFeed/main.py"]),
    ("OmniSurgeon Pro", ["~/Scripts/omnisurgeon-pro/omnisurgeon.py", "~/Scripts/omnisurgeon.py"]),
    ("OSIRIS Matrix UI", ["~/Scripts/OsirisMatrix/main.py", "~/Scripts/Osiris-Matrix/main.py"]),
    ("OSIRIS Pipeline", ["~/Scripts/osiris_pipeline/main.py", "~/Scripts/OsirisPipeline/main.py"]),
    ("OSIRIS SmartThings Tile", ["~/Scripts/SamsungSmartThings/main.py", "~/Scripts/SmartThings/main.py"]),
    ("OSIRIS Tracker", ["~/Scripts/OsirisTracker/main.py", "~/Scripts/OSIRIS_Tracker/main.py"]),
    ("OSIRIS Unified Tracker", ["~/Scripts/osiris_unified_tracker.py", "~/Scripts/UnifiedTracker/main.py", "~/Scripts/OSIRIS_Unified_Tracker/main.py"]),
    ("Paywall Remover GUI", ["~/Scripts/paywall-remover-gui/main.py", "~/Scripts/PaywallRemover/main.py"]),
    ("Price Sniper", ["~/Scripts/PriceSniper/main.py", "~/Scripts/Osiris-GUI-Suite/price_sniper.py", "~/Scripts/PriceHunter/main.py"]),
    ("Prop 22 Calculator", ["~/Scripts/prop22_calculator.py", "~/Scripts/Prop22/main.py", "~/Scripts/Prop-22/main.py"]),
    ("Punks Omni Dashboard", ["~/Scripts/punks_omni_dashboard.py", "~/Scripts/omni_dashboard_portable.py", "~/Scripts/PunksDashboard/main.py", "~/Scripts/Punks-Dashboard/main.py"]),
    ("Punks Tactical", ["~/Scripts/PunksTactical/main.py", "~/Scripts/PunksTactical/app.py"]),
    ("Punks Wifi Tray", ["~/Scripts/PunksWifi/main.py", "~/Scripts/Punks-Wifi/main.py"]),
    ("PyFixer Utility", ["~/Scripts/Osiris-GUI-Suite/pyfixer.py", "~/Scripts/PyFixer/main.py"]),
    ("Restaurant Roulette", ["~/Scripts/food_roulette.py", "~/Scripts/Restaurant-Roulette/main.py"]),
    ("RGB Controller", ["~/Scripts/RGB/open_rgb_controller.sh", "~/Scripts/OpenRGB/main.py"]),
    ("Safe Backend Processor", ["~/Scripts/safe_backend_processor.py"]),
    ("Scrape GUI", ["~/Scripts/scrape_gui.py", "~/Scripts/Osiris-GUI-Suite/scrape_gui.py", "~/Scripts/ScrapeGUI/main.py"]),
    ("Sentinel Diagnostics", ["~/Scripts/sentinel-diag/main.py", "~/Scripts/sentinel-diag/app.py"]),
    ("Sider AI Pro", ["~/Scripts/SiderAI/main.py", "~/Scripts/SiderAI/sider.py"]),
    ("Singularity NOC", ["~/Scripts/SingularityNOC/main.py", "~/Scripts/Singularity-NOC/main.py", "~/Scripts/Singularity/main.py"]),
    ("Sonic Forge", ["~/Scripts/sonic-forge/main.py", "~/Scripts/SonicForge/main.py"]),
    ("Storage Command", ["~/Scripts/StorageCommand/main.py", "~/Scripts/Storage-Command/main.py"]),
    ("Substrate OS Overlay", ["~/Scripts/SubstrateOS/main.py", "~/Scripts/Osiris-GUI-Suite/substrate_os.py"]),
    ("System Monitor", ["~/Scripts/Osiris-GUI-Suite/system_monitor.py", "~/Scripts/SystemMonitor/main.py"]),
    ("The Tile App", ["~/Scripts/TheTileApp/main.py", "~/Scripts/TileApp/main.py"]),
    ("TubeMaster Pro Elite", ["~/Scripts/tubemaster_pro.py", "~/Scripts/Osiris-GUI-Suite/tubemaster_pro.py", "~/Scripts/TubeMaster/main.py"]),
    ("URL Bypass Verifier", ["~/Scripts/UrlBypass/main.py", "~/Scripts/URL-Bypass/main.py"]),
    ("USB Performance Tester", ["~/Scripts/usb_performance_tester.py", "~/Scripts/USB-Performance/main.py"]),
    ("Voyager Telemetry", ["~/Scripts/Voyager/main.py", "~/Scripts/VoyagerTelemetry/main.py"]),
    ("Wake Dell", ["~/Scripts/WakeDell/main.py", "~/Scripts/Wake-Dell/main.py"]),
    ("Wake HP", ["~/Scripts/wake-hp/main.py", "~/Scripts/Wake-HP/main.py"]),
    ("Waydroid Script", ["~/Scripts/waydroid_script.py", "~/Scripts/Waydroid/main.py", "~/Scripts/waydroid_script/main.py", "~/Scripts/waydroid_script/waydroid.py"]),
    ("WiFi Airspace Scanner", ["~/Scripts/WifiScanner/main.py", "~/Scripts/Osiris-GUI-Suite/wifi_scanner.py"])
]

# --- Extra one-off apps merged in from the older fork's registry -----------
# (~/Scripts/AegisHUDLatest/aegis_master_hub.py). Folded into
# MASTER_REGISTRY below as extra path candidates where the app is already
# registered, or as new tiles where it isn't -- not duplicated as separate
# tiles pointing at the same script.
EXTRA_APPS = [
    ("AI Datacenter Tracker", "~/Scripts/DatacenterTracker/main.py"),
    ("FNV Mod Manager", "~/FNV_OSIRIS_Mod_Manager.py"),
    ("ICE Detention Center Tracker", "~/Scripts/ICEDetentionGUI/ICEDetentionCenterTracker/main.py"),
    ("Mohuan LED Dashboard", "~/Scripts/MohuanLED/main.py"),
    ("NAS Drive GUI", "~/Scripts/NASDriveGUI/main.py"),
    ("OSIRIS Matrix UI", "~/Scripts/OsirisMatrix/main.py"),
    ("Singularity NOC", "~/Scripts/SingularityNOC/main.py"),
    ("Storage GUI", "~/Scripts/StorageGUI/main.py"),
    ("TubeMaster Pro", "~/Scripts/TubeMasterPro/main.py"),
]

_registry_by_name = {n: ps for n, ps in MASTER_REGISTRY}
for _extra_name, _extra_path in EXTRA_APPS:
    if _extra_name in _registry_by_name:
        if _extra_path not in _registry_by_name[_extra_name]:
            _registry_by_name[_extra_name].append(_extra_path)
    else:
        _new_ps = [_extra_path]
        _registry_by_name[_extra_name] = _new_ps
        MASTER_REGISTRY.append((_extra_name, _new_ps))

# --- macOS path-resolution shim (auto-added) --------------------------------
import glob as _glob
_MAC_ROOT = os.path.expanduser("~/Projects/mac-gui-suite")
_BY_NAME, _BY_DIR = {}, {}
if os.path.isdir(_MAC_ROOT):
    for _p in (_glob.glob(os.path.join(_MAC_ROOT, "*", "*.py"))
               + _glob.glob(os.path.join(_MAC_ROOT, "*", "*", "*.py"))):
        if "BACKUP" in _p or "backup" in _p:
            continue
        _base = os.path.basename(_p)
        _parent = os.path.basename(os.path.dirname(_p)).lower().replace("-", "").replace("_", "")
        if _base == "main.py":
            _BY_DIR.setdefault(_parent, _p)
        else:
            _BY_NAME.setdefault(_base, _p)

def _resolve_candidates(paths):
    out = []
    for p in paths:
        xp = os.path.expanduser(p)
        if os.path.exists(xp):
            out.append(xp); continue
        base = os.path.basename(xp)
        if base == "main.py":
            parent = os.path.basename(os.path.dirname(xp)).lower().replace("-", "").replace("_", "")
            hit = _BY_DIR.get(parent)
        else:
            hit = _BY_NAME.get(base)
        if hit:
            out.append(hit)
    return out

MASTER_REGISTRY = [(n, _resolve_candidates(ps)) for n, ps in MASTER_REGISTRY]
MASTER_REGISTRY = [(n, ps) for n, ps in MASTER_REGISTRY if ps]
print(f"[HUB] macOS shim: {len(MASTER_REGISTRY)} tiles resolved", file=sys.stderr)

# --- Auto-discover unregistered local projects (auto-added) ------------------
_claimed = {p for _, ps in MASTER_REGISTRY for p in ps}
_skip_dirs = {"AegisHUD-macOS"}  # the HUD itself
_auto = []
if os.path.isdir(_MAC_ROOT):
    for _d in sorted(os.listdir(_MAC_ROOT)):
        _dp = os.path.join(_MAC_ROOT, _d)
        if (not os.path.isdir(_dp) or "BACKUP" in _d.upper()
                or _d in _skip_dirs or _d.startswith(".")):
            continue
        _entry = None
        _snake = _d.lower().replace("-", "_") + ".py"
        for _cand in ("main.py", "app.py", _snake):
            _c = os.path.join(_dp, _cand)
            if os.path.exists(_c):
                _entry = _c
                break
        if _entry is None:
            _pys = [f for f in os.listdir(_dp)
                    if f.endswith(".py") and "test" not in f.lower()]
            if len(_pys) == 1:
                _entry = os.path.join(_dp, _pys[0])
        if _entry and _entry not in _claimed:
            _title = _d.replace("-", " ").replace("_", " ").title()
            _auto.append((_title, [_entry]))

MASTER_REGISTRY = sorted(MASTER_REGISTRY + _auto, key=lambda t: t[0].lower())
print(f"[HUB] auto-discovered {len(_auto)} additional projects "
      f"({len(MASTER_REGISTRY)} tiles total)", file=sys.stderr)
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------


# =========================================================
# ⚡ INSTANT LOAD ENGINE (O(1) PATH RESOLUTION)
# =========================================================
def _smart_resolve(name, paths):
    """
    Checks explicit paths only. Removing os.walk guarantees
    instant 0ms UI blocking on launch.
    """
    for p in paths:
        exp = os.path.expanduser(p)
        if os.path.exists(exp):
            return exp
    return None

def _is_running(full_path):
    try:
        abs_p = os.path.abspath(os.path.expanduser(full_path))
        res = subprocess.run(["pgrep", "-f", abs_p], capture_output=True, text=True)
        return res.returncode == 0
    except: return False

def _launch_app(name, path, close_callback):
    exp = os.path.expanduser(path)
    if "TubeMaster" not in name and _is_running(exp): return
    err_log = os.path.expanduser("~/.aegis_app_errors.log")

    try:
        with open(err_log, "a") as err_out:
            err_out.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Launching: {name}\n")
            if exp.endswith(".desktop"):
                executed = False
                with open(exp, 'r') as f:
                    for line in f:
                        if line.startswith("Exec="):
                            cmd = line.strip().split("=", 1)[1]
                            cmd = re.sub(r'%[a-zA-Z]', '', cmd).strip()
                            subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=err_out, start_new_session=True)
                            executed = True
                            break
                if not executed:
                    subprocess.Popen(["xdg-open", exp], stdout=subprocess.DEVNULL, stderr=err_out, start_new_session=True)
            else:
                interp = "bash" if exp.endswith(".sh") else "python3"
                subprocess.Popen([interp, exp], cwd=os.path.dirname(exp), stdout=subprocess.DEVNULL, stderr=err_out, start_new_session=True)

        if "TubeMaster" not in name: close_callback()
    except: pass

def launch_master_hub(parent_root=None):
    global _hub_ref
    if _hub_ref:
        try: _hub_ref.destroy()
        except: pass

    hub = tk.Tk() if not parent_root else tk.Toplevel(parent_root)
    _hub_ref = hub
    hub.title("AEGIS_MASTER_HUB")
    hub.overrideredirect(True)
    try:
        hub.attributes("-alpha", 0.0)   # invisible until AppKit styling lands
    except Exception:
        pass
    hub.attributes("-topmost", True)
    hub.configure(bg=BG, highlightthickness=1, highlightbackground=BLUE)

    sw, sh = hub.winfo_screenwidth(), hub.winfo_screenheight()
    w, h = 1350, min(sh - 120, 900)
    x_pos = sw - w - 20
    hub.geometry(f"{w}x{h}+{x_pos}+44")

    def close(event=None):
        if hub.winfo_exists():
            hub.destroy()

    _mouse_entered = [False]

    def _monitor_pointer():
        if not hub.winfo_exists(): return
        try:
            x, y = hub.winfo_pointerxy()
            rx, ry = hub.winfo_rootx(), hub.winfo_rooty()
            inside = rx <= x <= rx + w and ry <= y <= ry + h
            if inside:
                _mouse_entered[0] = True
            elif _mouse_entered[0]:
                close()
                return
            hub.after(200, _monitor_pointer)
        except: pass

    hub.update()

    # macOS: Tk ignores overrideredirect — strip decorations via AppKit,
    # exactly as the AEGIS engine does (title-based NSWindow selection).
    try:
        from AppKit import (NSApplication, NSWindowStyleMaskBorderless,
                            NSStatusWindowLevel)
        for _w in NSApplication.sharedApplication().windows():
            if str(_w.title()) == "AEGIS_MASTER_HUB":
                _w.setStyleMask_(NSWindowStyleMaskBorderless)
                _w.setLevel_(NSStatusWindowLevel)
                _w.makeKeyAndOrderFront_(None)
                # Position via AppKit directly — Tk's geometry manager
                # still offsets for a title bar that no longer exists.
                from AppKit import NSMakeRect, NSScreen
                _sh_pt = NSScreen.mainScreen().frame().size.height
                _w.setFrame_display_(
                    NSMakeRect(x_pos, _sh_pt - 34 - h, w, h), True)
                try:
                    hub.attributes("-alpha", 1.0)
                except Exception:
                    pass
                print("[HUB] AppKit borderless applied", file=sys.stderr)
                break
        else:
            print("[HUB] WARNING: hub NSWindow not found by title",
                  file=sys.stderr)
            hub.attributes("-alpha", 1.0)
    except Exception as exc:
        print(f"[HUB] AppKit styling failed: {exc}", file=sys.stderr)
        try:
            hub.attributes("-alpha", 1.0)
        except Exception:
            pass

    # Start the mouse-off watchdog (was defined but never invoked).
    hub.after(400, _monitor_pointer)

    # macOS: overrideredirect windows never become key on their own, and
    # scroll/keyboard events are only delivered to the key window. Claim
    # key status now and whenever the pointer enters.
    def _claim_key(event=None):
        try:
            hub.focus_force()
            from AppKit import NSApplication
            for _w in NSApplication.sharedApplication().windows():
                if _w.isVisible() and _w.frame().size.width >= 1000:
                    _w.makeKeyAndOrderFront_(None)
                    break
        except Exception as exc:
            print(f"[HUB] claim-key: {exc}", file=sys.stderr)

    _claim_key()
    hub.bind("<Enter>", _claim_key)

    # AEGIS COMMAND CENTER / Enterprise Application Matrix branding, ported
    # from the older aegis_master_hub.py fork. `close` is looked up by name
    # at click time (not bound directly) since the NSEvent scroll-monitor
    # block below re-wraps `close` to also tear down its monitor -- a direct
    # `command=close` here would capture the pre-wrap version and leak it.
    hdr = tk.Frame(hub, bg=SURFACE)
    hdr.pack(fill=tk.X)
    title_frame = tk.Frame(hdr, bg=SURFACE)
    title_frame.pack(side=tk.LEFT, padx=16, pady=12)
    tk.Label(title_frame, text="AEGIS COMMAND CENTER", bg=SURFACE, fg=BLUE,
             font=("JetBrains Mono", 14, "bold")).pack(anchor="w")
    tk.Label(title_frame, text="Enterprise Application Matrix", bg=SURFACE, fg=MUTED,
             font=("Inter", 9)).pack(anchor="w")
    tk.Button(hdr, text="✕", bg=SURFACE, fg="#ef4444", relief="flat",
              font=("JetBrains Mono", 14), cursor="hand2",
              command=lambda: close()).pack(side=tk.RIGHT, padx=16, pady=10)

    s_var = tk.StringVar()
    s_row = tk.Frame(hub, bg=S2); s_row.pack(fill=tk.X, padx=12, pady=(15, 5))
    s_entry = tk.Entry(s_row, textvariable=s_var, bg=S2, fg=TEXT, font=("Inter", 18), relief="flat", insertbackground=BLUE)
    s_entry.pack(fill=tk.X, padx=8, ipady=12)

    outer = tk.Frame(hub, bg=BG); outer.pack(fill=tk.BOTH, expand=True, padx=12, pady=5)
    canvas = tk.Canvas(outer, bg=BG, highlightthickness=0); canvas.pack(side="left", fill="both", expand=True)
    grid = tk.Frame(canvas, bg=BG)
    canvas.create_window((0, 0), window=grid, anchor="nw", width=w-30)

    def _update_scroll(e=None):
        hub.update_idletasks()
        r = canvas.bbox("all")
        if not r:
            return
        canvas.config(scrollregion=r)
        print(f"[HUB] scrollregion={r} viewport_h={h-120} "
              f"scrollable={r[3] > (h - 120)}", file=sys.stderr)
        if r[3] <= (h - 120):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
        else:
            # macOS: two-finger trackpad scroll arrives as <MouseWheel>
            # with small signed deltas (positive = scroll up).
            def _wheel(ev):
                print(f"[HUB] wheel event: delta={ev.delta}", file=sys.stderr)
                canvas.yview_scroll(-ev.delta, "units")
            canvas.bind_all("<MouseWheel>", _wheel)
            # Keep X11 bindings so the same file still works on Linux.
            def _sc(ev): canvas.yview_scroll(-1 if ev.num == 4 else 1, "units")
            canvas.bind_all("<Button-4>", _sc)
            canvas.bind_all("<Button-5>", _sc)

    grid.bind("<Configure>", _update_scroll)

    # macOS fallback: intercept scroll events at the AppKit layer via an
    # NSEvent local monitor — Tk's port drops <MouseWheel> for
    # overrideredirect windows, so we bypass Tk event routing entirely.
    try:
        from AppKit import NSEvent
        NSEventMaskScrollWheel = 1 << 22
        _monitor_ref = [None]

        def _ns_scroll(event):
            try:
                if not hub.winfo_exists():
                    return event
                px, py = hub.winfo_pointerxy()
                rx, ry = hub.winfo_rootx(), hub.winfo_rooty()
                if rx <= px <= rx + w and ry <= py <= ry + h:
                    dy = event.scrollingDeltaY()
                    if dy:
                        canvas.yview_scroll(int(-dy), "units")
                    return None  # consumed
            except Exception as exc:
                print(f"[HUB] ns-scroll: {exc}", file=sys.stderr)
            return event

        _monitor_ref[0] = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(
            NSEventMaskScrollWheel, _ns_scroll)
        print("[HUB] NSEvent scroll monitor active", file=sys.stderr)

        _orig_close = close
        def close(event=None):
            if _monitor_ref[0] is not None:
                try:
                    NSEvent.removeMonitor_(_monitor_ref[0])
                except Exception:
                    pass
                _monitor_ref[0] = None
            _orig_close(event)
    except Exception as exc:
        print(f"[HUB] NSEvent monitor unavailable: {exc}", file=sys.stderr)
    grid.columnconfigure((0, 1, 2, 3, 4), weight=1)

    apps_found = []
    for name, p_list in MASTER_REGISTRY:
        res = _smart_resolve(name, p_list)
        if res: apps_found.append((name, res))
    apps_found.sort(key=lambda x: x[0].lower())

    _btn_frames = {}
    for i, (name, path) in enumerate(apps_found):
        c = ACCENT_COLORS[i % len(ACCENT_COLORS)]
        b = tk.Frame(grid, bg=BORDER, padx=1, pady=1)
        b.grid(row=i//5, column=i%5, padx=5, pady=5, sticky="ew")
        btn = tk.Button(b, text=f"▸ {name.upper()}", bg=SURFACE, fg=c, activebackground=S2, activeforeground=c, relief="flat", anchor="w", font=("Inter", 13, "bold"), command=lambda n=name, p=path: _launch_app(n, p, close))
        btn.pack(fill=tk.BOTH, expand=True, ipady=10, ipadx=8)
        _btn_frames[name.lower()] = b

    def _search(*_):
        q = s_var.get().lower()
        vis_idx = 0
        for name, _ in apps_found:
            f = _btn_frames[name.lower()]
            if q in name.lower():
                f.grid()
                f.grid(row=vis_idx//5, column=vis_idx%5)
                vis_idx += 1
            else: f.grid_remove()
        canvas.yview_moveto(0)
        _update_scroll()

    s_var.trace_add("write", _search)

    hub.bind("<Escape>", lambda e: close())
    hub.after(20, lambda: [hub.focus_force(), s_entry.focus_set(), _monitor_pointer()])

    if not parent_root: hub.mainloop()

if __name__ == "__main__":
    launch_master_hub()
