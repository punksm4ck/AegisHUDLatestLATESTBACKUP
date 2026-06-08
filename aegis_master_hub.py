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
    hub.overrideredirect(True)
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
        canvas.config(scrollregion=r)
        if r[3] <= (h - 120):
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
        else:
            def _sc(ev): canvas.yview_scroll(-1 if ev.num == 4 else 1, "units")
            canvas.bind_all("<Button-4>", _sc)
            canvas.bind_all("<Button-5>", _sc)

    grid.bind("<Configure>", _update_scroll)
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
