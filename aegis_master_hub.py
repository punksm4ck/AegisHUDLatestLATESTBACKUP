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
    # Real-project copy first (2026-11-19): this tile otherwise resolved nowhere and the app only
    # appeared as a dashboard tile running the wayland_tripwire duplicate-cluster copy.
    ("AI Water Tracker", ["~/Projects/mac-gui-suite/Osiris-GUI-Suite/ai_water_tracker.py", "~/Scripts/WaterTracker/main.py", "~/Scripts/Water-Tracker/main.py"]),
    ("APK Architect Pro", ["~/Scripts/apk_architect.py", "~/Scripts/ApkArchitect/main.py", "~/Scripts/APKArchitect/main.py"]),
    ("ColorNote Matrix", ["/home/tsann/.local/share/applications/colornote-osiris.desktop"]),
    # Project copy first (2026-11-19): the ~/Scripts basename fallback below resolved to the
    # Osiris-GUI-Suite copy, which has no interpreter (bare python3, no PyQt6/dotenv). Claiming
    # this path also stops auto-discovery adding it again as a second "Css Server Browser2" tile.
    ("CSS Server Browser", ["~/Projects/mac-gui-suite/css-server-browser2/css_server_browser2.py", "~/Scripts/css_server_browser2.py", "~/Scripts/css_server_browser.py", "~/Scripts/Osiris-GUI-Suite/css_server_browser.py", "~/Scripts/SteamServerBrowser/main.py"]),
    ("CX Operations Module", ["~/Scripts/job_listings_app.py", "~/Scripts/cx-ops/main.py", "~/Scripts/CXOps/main.py", "~/Scripts/JobListings/main.py"]),
    ("Facial Rec GUI", ["~/Scripts/facial-rec-gui/main.py", "~/Scripts/FacialRec/main.py", "~/Scripts/FaceRec/main.py"]),
    ("FNV Mod Manager", ["~/FNV_OSIRIS_Mod_Manager.py", "~/Scripts/FNV_OSIRIS_Mod_Manager.py"]),
    ("Ghost Framework", ["~/Scripts/Ghost/main.py", "~/Scripts/GhostFramework/main.py"]),
    ("Grid Walker", ["~/Scripts/Grid_Walkerv2.py", "~/Scripts/Grid_Walker.py", "~/Scripts/GridWalker/main.py", "~/Scripts/Osiris-GUI-Suite/grid_walker.py"]),
    ("Gun Stats GUI", ["~/Scripts/gun_stats_gui.py", "~/Scripts/GunStats/main.py", "~/Scripts/Osiris-GUI-Suite/gun_stats.py"]),
    ("HEPHAESTUS Forge", ["~/Scripts/Hephaestus/main.py", "~/Scripts/HEPHAESTUS/main.py"]),
    ("Heuristic Diagnostic UI", ["~/Scripts/diagnostic_tool_mockup.py", "~/Scripts/AegisHUDLatest/diagnostic_tool_mockup.py"]),
    ("Heuristic Reporter", ["~/Scripts/auto_diagnostic_reporter.py", "~/Scripts/AegisHUDLatest/auto_diagnostic_reporter.py"]),
    # Was "ICE Detention Tracker", which resolved to ICEDetentionCenterTracker/main.py --
    # the same file as the "ICE Detention Center Tracker" tile (double tile), while
    # ICEDetentionGUI ("ICE DRI Tracker — Logistics Command") had no tile. Re-pointed 2026-11-19.
    ("ICE DRI Tracker", ["~/Projects/mac-gui-suite/ICEDetentionGUI/main.py"]),
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
    # Hidden 2026-11-19: PunksTactical/main.py has never parsed (15 CSS #id selector lines
    # stripped from its HTML f-string, in every commit). Also blocked in _skip_dirs and
    # _DASH_SKIP_PARTS below so auto-discovery / the dashboard can't re-add it.
    # ("Punks Tactical", ["~/Scripts/PunksTactical/main.py", "~/Scripts/PunksTactical/app.py"]),
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
    ("URL Bypass Verifier", ["~/Scripts/UrlBypass/main.py", "~/Scripts/URL-Bypass/main.py", "~/Scripts/url_bypass_verifier.py"]),
    ("USB Performance Tester", ["~/Scripts/usb_performance_tester.py", "~/Scripts/USB-Performance/main.py"]),
    ("Voyager Telemetry", ["~/Scripts/Voyager/main.py", "~/Scripts/VoyagerTelemetry/main.py"]),
    ("Wake Dell", ["~/Scripts/WakeDell/main.py", "~/Scripts/Wake-Dell/main.py"]),
    ("Wake HP", ["~/Scripts/wake-hp/main.py", "~/Scripts/Wake-HP/main.py"]),
    ("Waydroid Script", ["~/Scripts/waydroid_script.py", "~/Scripts/Waydroid/main.py", "~/Scripts/waydroid_script/main.py", "~/Scripts/waydroid_script/waydroid.py"]),
    ("WiFi Airspace Scanner", ["~/Scripts/WifiScanner/main.py", "~/Scripts/Osiris-GUI-Suite/wifi_scanner.py"]),

    # --- Added by Claude: previously-unregistered GUI apps (2026-11-15) ------
    # Python apps in project folders with zero existing tiles:
    ("Aegis Core AI Watcher", ["~/Projects/mac-gui-suite/Aegis-Core/ai_watcher_enterprise.py"]),
    # sentinel_diagnostics.py needs the "live" subcommand for its GUI (run bare it exits
    # with an argparse error), so these tiles run wrappers in this repo's launchers/.
    ("Aegis Core Sentinel Diagnostics", ["~/Projects/mac-gui-suite/AegisHUDLatestLATESTBACKUP/launchers/aegis_core_sentinel_live.sh"]),
    ("Sentinel Diag", ["~/Projects/mac-gui-suite/AegisHUDLatestLATESTBACKUP/launchers/sentinel_diag_live.sh"]),
    ("Ai Content Detector Sentinel Diag Suite", ["~/Projects/mac-gui-suite/AegisHUDLatestLATESTBACKUP/launchers/diag_suite_sentinel_live.sh"]),
    # SwiftUI apps, launched via their built .app bundle:
    # NativeCam.app was rebuilt and renamed to Camera.app (same bundle id
    # com.punksm4ck.nativecam, same dev team, Camera.app is the newer
    # build -- Jul 27 02:09 vs Jul 26 22:41) -- point at the current build.
    ("NativeCam", ["/Applications/Camera.app"]),
    # Native Swift WKWebView window onto the local Open WebUI server at
    # http://127.0.0.1:8081 (bundle id com.aegis.webui; built by
    # ~/Scripts/aegis/openwebui/build-aegis-native.sh). The server itself is run
    # by the com.aegis.openwebui LaunchAgent; this tile only opens the window.
    # Launched by its own path: /Applications/AEGIS.app is a different app.
    ("AEGIS Open WebUI", ["~/Applications/AEGIS.app"]),
    # NOT SwiftUI: a PyInstaller bundle of the AEGIS Chat app (bundle id
    # com.punksm4ck.aegis, embedded Python; built from ~/.aegis_chat).
    # Renamed from "AEGIS Web Shell" 2026-11-19.
    ("AEGIS Chat (PyInstaller)", ["/Applications/AEGIS.app"]),
    # .app bundles that wrap an already-tiled script with the correct
    # interpreter/venv (added alongside the existing script-path tiles,
    # not replacing them):
    ("AEGIS Chat (App)", ["~/Applications/AEGIS Chat.app"]),
    ("AEGIS TV-OPS", ["~/Desktop/AEGIS TV-OPS.app"]),
    ("AI Limit Tracker (App)", ["~/Applications/AILimitTracker.app"]),
    ("OpenTorrent (App)", ["~/Desktop/OpenTorrent.app"]),

    # --- Added by Claude (2026-11-17) -----------------------------------
    # `scribe` is a pip-installed console script (scribe ui -> PyQt6 notepad
    # GUI), not a .py file -- the hub's launcher can't pass it the "ui" arg
    # directly, so launch_scribe.sh wraps it.
    ("AEGIS Scribe", ["~/Scripts/aegis-scribe/launch_scribe.sh"]),

    # --- Added by Claude (2026-11-18) -----------------------------------
    # SwiftUI menu-bar app (source: ~/Scripts/NetSec-VPS), built Release
    # with xcodebuild and installed to ~/Applications.
    ("NetSec-VPS", ["~/Applications/NetSec-VPS.app"]),

    # --- Added by Claude (2026-11-19) -----------------------------------
    # Electron app (source: ~/Downloads/pinboard-desktop-app, GitHub
    # punksm4ck/Pin_Dashboard_HTML), built with `npm run dist:mac` and
    # installed to ~/Applications.
    ("Pinboard Server", ["~/Applications/Pinboard Server.app"]),

    # --- Added by Claude (2026-11-19, later) ------------------------------
    # Variants with their own repo and materially different code that had no
    # tile (their paths were only fallback candidates of other tiles, or not
    # auto-discoverable). Static-checked on Homebrew python; NOT test-launched.
    # Launcher hub; it starts its child scripts with bare "python3".
    ("OSIRIS Unified Tracker Hub", ["~/Projects/mac-gui-suite/UnifiedTracker/main.py"]),
    # The non-v1 Aether Singularity (2,035 lines; "Aether Singularity Suite" runs v1).
    ("Aether Singularity (original)", ["~/Projects/mac-gui-suite/aether-singularity/aether_singularity.py"]),
    # Differs from the "Xenn Engagement Auditor" tile's copy; folder has no main.py.
    ("XENN Engagement Auditor (xenn)", ["~/Projects/mac-gui-suite/xenn/xenn_engagement_auditor.py"]),
    # ai-datacenter-tracker variant (differs from the "AI Datacenter Tracker" tile's
    # datacentertracker copy). Needs its own .venv: without groq it runs
    # `pip install groq --break-system-packages` into whatever python launched it.
    ("AI Datacenter Tracker (USA)", ["~/Projects/mac-gui-suite/ai-datacenter-tracker/main.py"]),
    # Was a dashboard tile on the wayland_tripwire copy; same code in Aegis-Contextual-HUD (2026-11-19).
    # Run bare it exits without a window (needs the "ui_mode" argument), so the tile runs a wrapper.
    ("PricePulse", ["~/Projects/mac-gui-suite/AegisHUDLatestLATESTBACKUP/launchers/pricepulse_ui.sh"]),
    # Cloned 2026-11-19 from GitHub punksm4ck/enterprisecomm (synced from the Windows PC) into
    # ~/Projects/github-staging. Mock UI: its one button only appends text to a log (the SIP/Asterisk
    # connection is a placeholder; `socket` is imported but unused). No network, files or installers.
    ("EnterpriseComm", ["~/Projects/github-staging/enterprisecomm/EnterpriseComm.py"]),
    # Restored 2026-11-19 (was the wayland_tripwire dashboard tile "substrate_os_overlay", removed in
    # 77768fe). Differs from "Substrate OS Overlay" (SubstrateOS/main.py). Borderless, always-on-top
    # 45 px CPU/clock bar above the Dock; no close button -- quit it from Activity Monitor or by PID.
    ("Substrate OS Overlay (variant)", ["~/Projects/mac-gui-suite/Aegis-Contextual-HUD/scripts/substrate_os_overlay.py"]),
    # World Monitor 2.11.8 (2026-11-19): upstream koala73/worldmonitor release (your fork: punksm4ck/worldmonitor),
    # aarch64 .app.tar.gz, sha256 matched GitHub's digest; Developer ID ELIAS HABIB (YC5UXN97NZ), notarized,
    # hardened runtime, no entitlements. Bundles a Node sidecar (Node.js Foundation signed) serving 127.0.0.1
    # only. Network dashboard: fetches news/data when open; stores its own keys in the login keychain.
    ("World Monitor", ["~/Applications/World Monitor.app"]),
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
# Was 3 separate glob.glob() passes over the whole ~177-project tree (one per
# depth) plus an os.path.exists() check on every match -- ~75s on every single
# launch (29s of that just the depth-3 glob re-walking vendored library trees
# it was going to throw away anyway, 40s more stat()-ing ~3500 matches one by
# one). Replaced with a single pruned os.walk (skips vendored/venv/backup
# dirs *before* descending into them, so it never pays to walk something it
# will discard) plus a disk cache so repeat launches pay ~0ms instead of
# re-walking the tree every time -- same cache-with-background-refresh
# pattern as the dashboard sync further down.
import json as _json0
_MAC_ROOT = os.path.expanduser("~/Projects/mac-gui-suite")
# Vendored third-party libraries pulled in wholesale as top-level folders --
# never a real match for a registered app's basename (e.g. their generic
# app.py/main.py would otherwise shadow an actual project's file once the
# dangling-symlink check below stops a broken match from winning first).
_VENDORED_DIRS = {"Pillow", "tqdm", "kivy", "mpv", "PySimpleGUI", "CustomTkinter",
                  "PyQt-Fluent-Widgets", "python-for-android"}
# Known duplicate-copy clusters (per CLAUDE.md) -- old-machine/backup copies
# of other projects' files, not a project of their own. The basename
# fallback below must never resolve a registered app's name into one of
# these: besides being a stale copy, a dangling symlink inside one of them
# can lose the tie-break race against a real file elsewhere purely on
# os.walk's directory-visit order, silently swapping a working app's target
# for the stale duplicate (seen in practice: "AI Datacenter Tracker" and
# "Network Guardian" both resolved in here instead of their real project
# folders, which then got auto-discovered a second time under a different
# name -- i.e. the same app double-tiled).
_DUPLICATE_CLUSTER_DIRS = {"wayland_tripwire", "watcher_diagnostics",
                           "tray_fixer", "aula_scanner"}
_SHIM_PRUNE_DIRS = ({"venv", ".venv", "env", "site-packages", "node_modules",
                    "__pycache__", ".git", "build", "dist"}
                    | _VENDORED_DIRS | _DUPLICATE_CLUSTER_DIRS)
_SHIM_CACHE = os.path.expanduser("~/.gui_dashboard/hub_shim.json")
_SHIM_CACHE_MAX_AGE = 6 * 3600


def _shim_scan():
    """One pruned walk of ~/Projects/mac-gui-suite, depth-capped to match the
    old glob's */*/*/*.py reach (3 levels under the project root).

    When the same basename/parent-key shows up more than once (a project's
    own file plus a copy bundled inside *another* app's scripts/applications/
    modules subtree, e.g. AegisHUDLatest/scripts/ carries copies of a dozen
    other tools), keep the SHALLOWEST match. A real project's entry point
    lives at <project>/main.py (depth 1); anything bundled inside another
    app's own resource folder is necessarily deeper. os.walk's visit order
    is not alphabetical like the old glob() happened to be, so without this
    tie-break the winner is arbitrary -- confirmed in practice: it flipped
    "AI Datacenter Tracker" onto a bundled copy instead of the real project
    folder, which then got auto-discovered a second time under a different
    name (same app, double-tiled)."""
    by_name, by_dir = {}, {}
    _name_depth, _dir_depth = {}, {}
    if not os.path.isdir(_MAC_ROOT):
        return by_name, by_dir
    for _dp, _dns, _fns in os.walk(_MAC_ROOT):
        _top = os.path.relpath(_dp, _MAC_ROOT).split(os.sep)[0]
        if _top in _VENDORED_DIRS or _top in _DUPLICATE_CLUSTER_DIRS:
            _dns[:] = []
            continue
        _depth = _dp[len(_MAC_ROOT):].count(os.sep)
        if _depth >= 3:
            _dns[:] = []
        _dns[:] = [_d for _d in _dns
                   if _d not in _SHIM_PRUNE_DIRS and "BACKUP" not in _d.upper()]
        for _fn in _fns:
            if not _fn.endswith(".py") or "backup" in _fn.lower():
                continue
            _p = os.path.join(_dp, _fn)
            if not os.path.exists(_p):
                continue  # dangling symlink (e.g. leftover Linux-box copies
                          # under wayland_tripwire/) -- os.path.exists
                          # follows the link, reports False if target is gone
            _parent = os.path.basename(_dp).lower().replace("-", "").replace("_", "")
            if _fn == "main.py":
                if _parent not in _dir_depth or _depth < _dir_depth[_parent]:
                    by_dir[_parent] = _p
                    _dir_depth[_parent] = _depth
            else:
                if _fn not in _name_depth or _depth < _name_depth[_fn]:
                    by_name[_fn] = _p
                    _name_depth[_fn] = _depth
    return by_name, by_dir


def _shim_write_cache():
    by_name, by_dir = _shim_scan()
    os.makedirs(os.path.dirname(_SHIM_CACHE), exist_ok=True)
    tmp = _SHIM_CACHE + ".tmp"
    with open(tmp, "w") as f:
        _json0.dump({"generated": time.time(), "by_name": by_name, "by_dir": by_dir}, f)
    os.replace(tmp, _SHIM_CACHE)
    return by_name, by_dir


if "--rebuild-shim-cache" in sys.argv:
    _shim_write_cache()
    sys.exit(0)

try:
    with open(_SHIM_CACHE) as _f:
        _shim_blob = _json0.load(_f)
    _BY_NAME, _BY_DIR = _shim_blob["by_name"], _shim_blob["by_dir"]
    if time.time() - _shim_blob.get("generated", 0) > _SHIM_CACHE_MAX_AGE:
        os.utime(_SHIM_CACHE, None)     # avoid several hubs refreshing at once
        subprocess.Popen([sys.executable, os.path.abspath(__file__), "--rebuild-shim-cache"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
except Exception:
    _BY_NAME, _BY_DIR = _shim_write_cache()    # first run: build it once, now

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
# Resolved + case-folded (APFS is case-insensitive): the "<folder>.py" probe below
# matches e.g. Grid_Walkerv2.py as grid_walkerv2.py, and an exact-string check then
# missed the registry's claim and tiled the same file twice (fixed 2026-11-19).
_claimed = {os.path.realpath(p).lower() for _, ps in MASTER_REGISTRY for p in ps}
_skip_dirs = {"AegisHUD-macOS",  # the HUD itself
              # CLI patchers that rewrite files under ~/Scripts on launch -- not apps;
              # hidden from the APPS menu (2026-11-19). Run them from a terminal if needed.
              "the-absolute-finale", "the-final-squash", "the-zenith-protocol",
              # Linux-only (hardcoded /home/tsann paths, konsole, wmctrl); hidden 2026-11-19.
              "master-gui-launcher",
              "xenn-master-suite-patcher",
              # Stale copy of github-tool-auto-sync's script (still `git push --force`es the
              # Intel vault); the "Github Tool Auto Sync" tile runs the fixed copy. Hidden 2026-11-19.
              "sovereign-nexus-apex",
              # Not GUI apps (hidden 2026-11-19): 06-build-adapters is a code generator that
              # writes into app/; the two apply-aegis-* scripts are one-shot patchers that
              # overwrite a hardcoded C:/Users/tsann/... file. Run from a terminal if needed.
              "06-build-adapters", "apply-aegis-lockfix", "apply-aegis-titan",
              # One-shot patcher with a thin PyQt6 wrapper: rewrites/restores files under a
              # hardcoded C:/Users/tsann/.../gui_apps path. Not an app; hidden 2026-11-19.
              "aegis-crash-fixer-v3",
              # main.py doesn't parse (see the commented-out registry entry). Hidden 2026-11-19.
              "PunksTactical",
              # Duplicate copies of tiled apps (hidden 2026-11-19): edm-finder is byte-identical
              # to EDM_Finder; wifi-airspace-scanner is WifiScanner minus one processEvents() line.
              "edm-finder", "wifi-airspace-scanner",
              # Tiled via launchers/*_live.sh instead (the bare script needs a subcommand).
              "sentinel-diag", "ai-content-detector-sentinel-diag-suite",
              # Duplicate of sentinel-diag (minus a copyright line) that also fails bare (needs the
              # "live" subcommand) and on Homebrew python (no PyQt5 bindings). Hidden 2026-11-19.
              "sentinel-diagnostics",
              # Acer Chromebook Plus 516 GE keyboard-RGB controller (ectool / /dev/port; Kubuntu only):
              # nothing to control on this Mac, and its __main__.py runs `apt install` and
              # `pip install keyboard --break-system-packages` on launch. Hidden 2026-11-19.
              "cb-rgb-controller",
              # CLI code patcher, not an app: reads sovereign_nexus_omega.py from its working directory and
              # writes sovereign_nexus_omega_hardened.py. Run from a terminal if needed. Hidden 2026-11-19.
              "nexus-patcher",
              # One-shot YouTube playlist downloader that cannot work as written: it needs pytube (no release
              # since 2023-05-07), filters for abr="320kbps" (YouTube audio streams are lower), and renames
              # .mp4/.webm audio to .mp3 without converting before tagging it with mutagen. Hidden 2026-11-19.
              "m3u-formatter"}
_auto = []
if os.path.isdir(_MAC_ROOT):
    for _d in sorted(os.listdir(_MAC_ROOT)):
        _dp = os.path.join(_MAC_ROOT, _d)
        # Vendored libraries are excluded here the same way the path shim
        # prunes them: their lone setup.py otherwise passes the single-.py
        # fallback below and shows up as a bogus "Pillow"/"Kivy"/... tile.
        if (not os.path.isdir(_dp) or "BACKUP" in _d.upper()
                or _d in _skip_dirs or _d in _VENDORED_DIRS
                or _d.startswith(".")):
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
        if _entry and os.path.realpath(_entry).lower() not in _claimed:
            _title = _d.replace("-", " ").replace("_", " ").title()
            _auto.append((_title, [_entry]))

MASTER_REGISTRY = sorted(MASTER_REGISTRY + _auto, key=lambda t: t[0].lower())
print(f"[HUB] auto-discovered {len(_auto)} additional projects "
      f"({len(MASTER_REGISTRY)} tiles total)", file=sys.stderr)
# ---------------------------------------------------------------------------

# --- Sync with the GUI App Dashboard (auto-added) ----------------------------
# Adds a tile for every app the dashboard lists (minus its Ignore list, vendored
# library demos and apps already tiled above). Reads a cache for an instant open;
# a detached background process refreshes the cache when it gets old.
#   Force a refresh now:  python3 aegis_master_hub.py --sync-dashboard
import json as _json
import ast as _ast
import shutil as _shutil
import importlib.util as _ilu

_DASH_CACHE = os.path.expanduser("~/.gui_dashboard/hub_apps.json")
_DASH_CACHE_MAX_AGE = 6 * 3600          # seconds before a background refresh
_DASH_CANDIDATES = [
    "~/Downloads/gui_dashboard.py",
    "~/Scripts/gui_dashboard.py",
    "~/Projects/gui_dashboard/gui_dashboard.py",
    "~/gui_dashboard.py",
]
# Path fragments to leave out (vendored libraries, demos, the HUD's own files).
_DASH_SKIP_PARTS = (
    "/PyQt-Fluent-Widgets/", "/kivy/kivy/", "/CustomTkinter/customtkinter/",
    "/PySimpleGUI/PySimpleGUI/", "/mpv/TOOLS/",
    "/PunksTactical/",   # hidden 2026-11-19 (main.py doesn't parse)
    "/edm-finder/", "/wifi-airspace-scanner/",   # duplicate copies, hidden 2026-11-19
    # Tiled via launchers/*_live.sh (bare script exits without the "live" subcommand):
    "/Aegis-Core/sentinel_diagnostics.py", "/sentinel-diag/", "/ai-content-detector-sentinel-diag-suite/",
    "/sentinel-diagnostics/",   # duplicate of sentinel-diag, hidden 2026-11-19 (not -gui)
    # Duplicate-copy cluster (CLAUDE.md): its 15 dashboard tiles were stale copies -- 6 template wrappers
    # for /home/tsann backends that don't exist here, Linux-only tools, apt installers, and copies of
    # apps that live in real projects (AI Water Tracker, PricePulse re-pointed above). 2026-11-19.
    "/wayland_tripwire/",
)
_DASH_SKIP_FILES = {"aegis_master_hub.py", "aegis_engine_macos.py", "gui_dashboard.py"}
_DASH_GENERIC = {"main", "app", "gui", "run", "start", "launcher", "window", "ui", "index"}
_PY_FOR = {}


def _pyfor_key(path):
    """Resolved, case-folded path (APFS is case-insensitive) for _PY_FOR lookups."""
    return os.path.realpath(os.path.expanduser(path)).lower()


# --- Explicit interpreter overrides (2026-11-19) ---------------------------
# Tiles that otherwise fall back to bare "python3" (= /usr/bin/python3 3.9
# under launchd, no PyQt/psutil). Each was verified: every third-party module
# the script imports is importable by the interpreter given here, and the tile
# was test-launched and stayed up. Checked before _PY_FOR in _launch_app.
_BREW_PY = "/opt/homebrew/bin/python3"
INTERPRETER_OVERRIDES = {
    "~/Projects/mac-gui-suite/Aegis-Contextual-HUD/ai_terminal.py": _BREW_PY,  # AI Terminal (tkinter)
    "~/Projects/mac-gui-suite/aegis-osiris-wizard/aegis_osiris_wizard.py": _BREW_PY,  # Aegis Osiris Wizard (tkinter)
    "~/Projects/mac-gui-suite/claude_check/aegis_osiris_wizard.py": _BREW_PY,  # Claude Check (tkinter)
    "~/Projects/mac-gui-suite/clean-room/CleanRoomGUI.py": _BREW_PY,  # Clean Room (PyQt6)
    "~/Projects/mac-gui-suite/cleanroomgui/CleanRoomGUI.py": _BREW_PY,  # Cleanroomgui (PyQt6)
    "~/Projects/mac-gui-suite/EDM_Finder/edm_finder.py": _BREW_PY,  # Edm Finder (customtkinter)
    "~/Projects/mac-gui-suite/food-roulette/food_roulette.py": _BREW_PY,  # Food Roulette (PyQt6)
    "~/Projects/mac-gui-suite/nasdrivegui/NASDriveGUI.py": _BREW_PY,  # NAS Drive GUI (PyQt6)
    "~/Projects/mac-gui-suite/netsec/NetSecDeployer.py": _BREW_PY,  # Netsec (PyQt6)
    "~/Projects/mac-gui-suite/netsecdeployer/NetSecDeployer.py": _BREW_PY,  # Netsecdeployer (PyQt6)
    "~/Projects/mac-gui-suite/omnisurgeon-pro/omnisurgeon.py": _BREW_PY,  # OmniSurgeon Pro (PyQt6)
    "~/Projects/mac-gui-suite/Osiris-GUI-Suite/network_gui.py": _BREW_PY,  # Network GUI (PyQt6)
    "~/Projects/mac-gui-suite/Osiris-GUI-Suite/pyfixer.py": _BREW_PY,  # PyFixer Utility (tkinter)
    "~/Projects/mac-gui-suite/Osiris-GUI-Suite/scrape_gui.py": _BREW_PY,  # Scrape GUI (PyQt6)
    "~/Projects/mac-gui-suite/Osiris-GUI-Suite/system_monitor.py": _BREW_PY,  # System Monitor (tkinter)
    "~/Projects/mac-gui-suite/Osiris-GUI-Suite/tubemaster_pro.py": _BREW_PY,  # TubeMaster Pro Elite (PyQt6)
    "~/Projects/mac-gui-suite/swiss-army-knife/swiss_army_knife.py": _BREW_PY,  # Swiss Army Knife (tkinter)
    # Per-project venvs (<project>/.venv, gitignored), pinned deps installed 2026-11-19.
    "~/Projects/mac-gui-suite/aegis-fire-map/aegis_fire_map.py": "~/Projects/mac-gui-suite/aegis-fire-map/.venv/bin/python",
    "~/Projects/mac-gui-suite/css-server-browser2/css_server_browser2.py": "~/Projects/mac-gui-suite/css-server-browser2/.venv/bin/python",
    "~/Projects/mac-gui-suite/github-tool-auto-sync/sovereign_nexus_apex-PUBLIC.py": "~/Projects/mac-gui-suite/github-tool-auto-sync/.venv/bin/python",
    "~/Projects/mac-gui-suite/network-guardian-gui/network_guardian_gui.py": "~/Projects/mac-gui-suite/network-guardian-gui/.venv/bin/python",
    "~/Projects/mac-gui-suite/punksadminconsole-enterprise/punksadminconsole_enterprise.py": "~/Projects/mac-gui-suite/punksadminconsole-enterprise/.venv/bin/python",
    "~/Projects/mac-gui-suite/ssoc/ssoc.py": "~/Projects/mac-gui-suite/ssoc/.venv/bin/python",
    "~/Projects/mac-gui-suite/tubemaster-pro/tubemaster_pro.py": "~/Projects/mac-gui-suite/tubemaster-pro/.venv/bin/python",
    "~/Projects/mac-gui-suite/datacentertracker/main.py": "~/Projects/mac-gui-suite/datacentertracker/.venv/bin/python",
    "~/Projects/mac-gui-suite/xenn-engagement-auditor/xenn_engagement_auditor.py": "~/Projects/mac-gui-suite/xenn-engagement-auditor/.venv/bin/python",
    # Import-checked only (2026-11-19, every third-party import resolves); NOT test-launched.
    "~/Projects/mac-gui-suite/meme-sync-gui/meme_sync_gui.py": _BREW_PY,  # Meme Sync Pro (PyQt6, PIL)
    # Per-project venvs created 2026-11-19 (wheels only, hash-pinned, no .pth files). Import-checked;
    # NOT test-launched. PyQt5 is not usable in Homebrew python (only Qt5 libs + sip installed).
    "~/Projects/mac-gui-suite/Aegis-Core/ai_watcher_enterprise.py": "~/Projects/mac-gui-suite/Aegis-Core/.venv/bin/python",  # Aegis Core AI Watcher (PyQt5, mss)
    "~/Projects/mac-gui-suite/ai-watcher-enterprise/ai_watcher_enterprise.py": "~/Projects/mac-gui-suite/ai-watcher-enterprise/.venv/bin/python",  # Ai Watcher Enterprise (PyQt5, mss, numpy)
    "~/Projects/mac-gui-suite/SP-Locator/sp_locator_v3.py": "~/Projects/mac-gui-suite/sentinel-diag/.venv/bin/python",  # Sp Locator (PyQt5; shares sentinel-diag .venv)
    # The 3 sentinel_diagnostics.py tiles now run launchers/*_live.sh, which exec their
    # project .venv python directly (.sh tiles don't consult these overrides).
    "~/Projects/mac-gui-suite/ICE-Watch/ice_watch.py": "~/Projects/mac-gui-suite/ICE-Watch/.venv/bin/python",  # ICE Watch (Kivy 2.3.1, Python 3.12)
    # Homebrew python: PyQt6 from Homebrew site-packages, psutil from the per-user site
    # (~/Library/Python/3.14). Import-checked without -I, as the hub launches; NOT test-launched.
    "~/Projects/mac-gui-suite/storage-gui/storage_gui.py": _BREW_PY,  # Storage Gui (PyQt6, psutil)
    # The 4 variant tiles added 2026-11-19 (static-checked, NOT test-launched):
    "~/Projects/mac-gui-suite/ICEDetentionGUI/main.py": _BREW_PY,  # ICE DRI Tracker (PyQt6; groq optional)
    "~/Projects/mac-gui-suite/UnifiedTracker/main.py": _BREW_PY,  # OSIRIS Unified Tracker Hub (PyQt6)
    "~/Projects/mac-gui-suite/aether-singularity/aether_singularity.py": _BREW_PY,  # Aether Singularity (original) (PyQt6, psutil, requests)
    "~/Projects/mac-gui-suite/xenn/xenn_engagement_auditor.py": _BREW_PY,  # XENN Engagement Auditor (xenn) (PyQt6)
    # Own .venv (2026-11-19; wheels only, hash-pinned, 14-day rule, no .pth): PyQt6 6.12.0,
    # PyQt6-WebEngine 6.140.0, groq 1.7.0. Import-checked; NOT test-launched.
    "~/Projects/mac-gui-suite/ai-datacenter-tracker/main.py": "~/Projects/mac-gui-suite/ai-datacenter-tracker/.venv/bin/python",  # AI Datacenter Tracker (USA)
    "~/Projects/mac-gui-suite/Osiris-GUI-Suite/ai_water_tracker.py": _BREW_PY,  # AI Water Tracker (tkinter, stdlib only)
    # PricePulse runs launchers/pricepulse_ui.sh, which execs Homebrew python3 itself.
    "~/Projects/github-staging/enterprisecomm/EnterpriseComm.py": _BREW_PY,  # EnterpriseComm (PyQt6, stdlib only)
    "~/Projects/mac-gui-suite/Aegis-Contextual-HUD/scripts/substrate_os_overlay.py": _BREW_PY,  # Substrate OS Overlay (variant) (tkinter; psutil from the per-user site)
}
_INTERP_OVERRIDE = {_pyfor_key(k): os.path.expanduser(v) for k, v in INTERPRETER_OVERRIDES.items()}


def _dash_key(path):
    p = os.path.abspath(os.path.expanduser(path))
    stem = re.sub(r"[^a-z0-9]", "", os.path.splitext(os.path.basename(p))[0].lower())
    if stem in _DASH_GENERIC:
        stem = re.sub(r"[^a-z0-9]", "", os.path.basename(os.path.dirname(p)).lower()) + stem
    return stem


def _dash_imports(path):
    """Top-level module names a script imports (minus sibling/local modules)."""
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            tree = _ast.parse(f.read())
    except Exception:
        return set()
    names = set()
    for n in _ast.walk(tree):
        if isinstance(n, _ast.Import):
            names.update(a.name.split(".")[0] for a in n.names)
        elif isinstance(n, _ast.ImportFrom) and n.level == 0 and n.module:
            names.add(n.module.split(".")[0])
    local, cur = set(), os.path.dirname(path)
    for _ in range(3):
        try:
            for e in os.listdir(cur):
                local.add(e[:-3] if e.endswith(".py") else e)
        except OSError:
            pass
        cur = os.path.dirname(cur)
    return {m for m in names if m not in local and m != "__main__"}


_DASH_PROBE = (
    "import importlib.util as u, sys, json\n"
    "bad = []\n"
    "for m in sys.argv[1:]:\n"
    "    try:\n"
    "        if u.find_spec(m) is None: bad.append(m)\n"
    "    except Exception:\n"
    "        bad.append(m)\n"
    "print(json.dumps(bad))\n"
)


def _dash_pick_pythons(items):
    """items: [(path, preferred_python)] -> {path: interpreter that can import the most}.
    The dashboard's venv guess stays first, so it still wins ties; but a venv that
    lacks a module the script imports loses to one that has it (e.g. Homebrew)."""
    extras = []
    for c in (sys.executable, _shutil.which("python3"),
              "/opt/homebrew/bin/python3", "/usr/local/bin/python3"):
        if c and os.path.exists(c) and c not in extras:
            extras.append(c)
    mods = {p: _dash_imports(p) for p, _ in items}
    cands, want = {}, {}
    for p, pref in items:
        cl = [x for x in [pref] + [e for e in extras if e != pref] if x and os.path.exists(x)]
        cands[p] = cl
        for py in cl:
            want.setdefault(py, set()).update(mods[p])
    missing = {}
    for py, wanted in want.items():
        try:
            r = subprocess.run([py, "-c", _DASH_PROBE] + sorted(wanted), cwd="/",
                               capture_output=True, text=True, timeout=60)
            missing[py] = set(_json.loads(r.stdout.strip().splitlines()[-1])) if r.returncode == 0 else None
        except Exception:
            missing[py] = None
    best = {}
    for p, cl in cands.items():
        scored = [(len(mods[p] & missing[py]), i, py)
                  for i, py in enumerate(cl) if missing.get(py) is not None]
        best[p] = min(scored)[2] if scored else (cl[0] if cl else sys.executable)
    return best


_DASH_SRC_MEMO = os.path.expanduser("~/.gui_dashboard/hub_src.txt")


def _dash_find_source():
    """Locate gui_dashboard.py: env var, remembered path, known spots, then a shallow search."""
    cands = [os.environ.get("AEGIS_DASHBOARD", "")]
    try:
        cands.append(open(_DASH_SRC_MEMO).read().strip())
    except OSError:
        pass
    cands += [os.path.expanduser(c) for c in _DASH_CANDIDATES]
    found = next((c for c in cands if c and os.path.isfile(c)), None)
    if not found:
        skip = {"venv", ".venv", "env", "site-packages", "node_modules", "Library",
                ".Trash", ".git", "__pycache__"}
        home = os.path.expanduser("~")
        for root in ("~/Downloads", "~/Scripts", "~/Projects", "~/Developer", "~/Desktop", "~"):
            base = os.path.expanduser(root)
            depth0 = base.rstrip(os.sep).count(os.sep)
            for dp, dns, fns in os.walk(base):
                dns[:] = [d for d in dns if d not in skip and not d.startswith(".")]
                if dp.count(os.sep) - depth0 >= (1 if base == home else 4):
                    dns[:] = []
                if "gui_dashboard.py" in fns:
                    found = os.path.join(dp, "gui_dashboard.py")
                    break
            if found:
                break
    if found:
        try:
            os.makedirs(os.path.dirname(_DASH_SRC_MEMO), exist_ok=True)
            with open(_DASH_SRC_MEMO, "w") as f:
                f.write(found)
        except OSError:
            pass
    return found


def _dash_write_cache():
    """Run the dashboard's own scan and store the result. Returns the app list."""
    src = _dash_find_source()
    if not src:
        print("[HUB] gui_dashboard.py not found anywhere under ~/Downloads, ~/Scripts, "
              "~/Projects, ~/Developer or ~; dashboard sync skipped (cache left unchanged)",
              file=sys.stderr)
        return None
    spec = _ilu.spec_from_file_location("gui_dashboard_mod", src)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cfg = mod.load_config()
    apps, _copies, _hidden = mod.discover(cfg)
    ignored = set(cfg.get("ignored", []))
    keep = [p for p in sorted(apps)
            if not (p in ignored or os.path.basename(p) in _DASH_SKIP_FILES
                    or any(part in p for part in _DASH_SKIP_PARTS))]
    pys = _dash_pick_pythons([(p, mod.python_for(p)) for p in keep])
    out = [[mod.display_name(p), p, pys[p]] for p in keep]
    os.makedirs(os.path.dirname(_DASH_CACHE), exist_ok=True)
    tmp = _DASH_CACHE + ".tmp"
    with open(tmp, "w") as f:
        _json.dump({"generated": time.time(), "apps": out}, f, indent=1)
    os.replace(tmp, _DASH_CACHE)
    return out


if "--sync-dashboard" in sys.argv:
    _res = _dash_write_cache()
    if _res is not None:
        print(f"[HUB] dashboard sync wrote {len(_res)} apps to {_DASH_CACHE}", file=sys.stderr)
    sys.exit(0 if _res is not None else 1)

_dash_apps = None
try:
    with open(_DASH_CACHE) as _f:
        _blob = _json.load(_f)
    _dash_apps = _blob.get("apps", [])
    if time.time() - _blob.get("generated", 0) > _DASH_CACHE_MAX_AGE:
        os.utime(_DASH_CACHE, None)     # avoid several hubs refreshing at once
        subprocess.Popen([sys.executable, os.path.abspath(__file__), "--sync-dashboard"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
except Exception:
    try:                                # first run: build the cache once, now
        _dash_apps = _dash_write_cache() or []
    except Exception as _exc:
        print(f"[HUB] dashboard sync failed: {_exc}", file=sys.stderr)
        _dash_apps = []

_PY_DIR_PICKS = {}
_have_keys = {_dash_key(p) for _, ps in MASTER_REGISTRY for p in ps}
_have_titles = {n.lower() for n, _ in MASTER_REGISTRY}
_dash_new = []
for _title, _path, _py in (_dash_apps or []):
    if not os.path.exists(_path):
        continue
    # Apply the skip list to cached entries too (it was only applied when the cache is
    # rebuilt, so a newly skipped app stayed tiled until the next refresh).
    if any(_part in _path for _part in _DASH_SKIP_PARTS):
        continue
    # Remember the dashboard's interpreter pick even for apps already tiled
    # above (registry/auto-discovered), keyed by resolved path: otherwise
    # those tiles fall back to bare "python3" (/usr/bin/python3 3.9 under
    # launchd, no PyQt6) and a symlinked/moved app loses its venv. (2026-11-18)
    _PY_FOR.setdefault(_pyfor_key(_path), _py)
    # Collect per-folder picks for the same-folder fallback below.
    _PY_DIR_PICKS.setdefault(os.path.dirname(_pyfor_key(_path)), set()).add(_py)
    _k = _dash_key(_path)
    if _k in _have_keys or _title.lower() in _have_titles:
        continue
    _have_keys.add(_k)
    _have_titles.add(_title.lower())
    _PY_FOR[_path] = _py
    _dash_new.append((_title, [_path]))

# Same-folder fallback (e.g. an auto-discovered main.py whose sibling gui.py is
# what the dashboard listed) -- only where every listed sibling in that folder
# agrees on one interpreter. Mixed folders (Osiris-GUI-Suite: tkinter scripts on
# the HUD venv, PyQt6 scripts on Homebrew) get no fallback.
for _d, _pys in _PY_DIR_PICKS.items():
    if len(_pys) == 1:
        _PY_FOR.setdefault("dir:" + _d, next(iter(_pys)))

MASTER_REGISTRY = sorted(MASTER_REGISTRY + _dash_new, key=lambda t: t[0].lower())
print(f"[HUB] dashboard sync added {len(_dash_new)} tiles "
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
            elif exp.endswith(".app"):
                subprocess.Popen(["open", exp], stdout=subprocess.DEVNULL, stderr=err_out, start_new_session=True)
            else:
                interp = ("bash" if exp.endswith(".sh") else
                          _INTERP_OVERRIDE.get(_pyfor_key(exp))
                          or _PY_FOR.get(exp) or _PY_FOR.get(_pyfor_key(exp))
                          or _PY_FOR.get("dir:" + os.path.dirname(_pyfor_key(exp)))
                          or "python3")
                subprocess.Popen([interp, exp], cwd=os.path.dirname(exp), stdout=subprocess.DEVNULL, stderr=err_out, start_new_session=True)

        if "TubeMaster" not in name: close_callback()
    except: pass

_ACCESSORY_HOOKED = False


def _pre_tk_accessory():
    """macOS: keep the hub out of the Dock for the *whole* Tk startup.

    Calling setActivationPolicy_(Accessory) after tk.Tk() returns is too
    late: Tk() itself takes 1-4s, and during it the process is Foreground
    (Dock icon visible) twice over -- Python.app checks in as a regular app,
    and Tk's init explicitly calls [NSApp setActivationPolicy:Regular].
    NSApplication can't be created before Tk (Tk needs its own TKApplication
    subclass as NSApp; a plain NSApp crashes Tk_GetColor), so instead:
      1. mark the main bundle LSUIElement in-memory, so check-in is UIElement;
      2. coerce Tk's Regular policy request to Accessory via a category.
    Neither instantiates NSApplication. Process-wide, so standalone only.
    """
    global _ACCESSORY_HOOKED
    if _ACCESSORY_HOOKED:
        return
    try:
        import objc
        from Foundation import NSBundle
        from AppKit import (NSApplication,
                            NSApplicationActivationPolicyAccessory,
                            NSApplicationActivationPolicyRegular)
        info = NSBundle.mainBundle().infoDictionary()
        if info is not None:
            info["LSUIElement"] = "1"
        _orig_set_policy = NSApplication.instanceMethodForSelector_(
            b"setActivationPolicy:")

        # PyObjC requires the category class to carry the class's own name.
        class NSApplication(objc.Category(NSApplication)):  # noqa: F811
            def setActivationPolicy_(self, policy):
                if policy == NSApplicationActivationPolicyRegular:
                    policy = NSApplicationActivationPolicyAccessory
                return _orig_set_policy(self, policy)

        _ACCESSORY_HOOKED = True
        print("[HUB] pre-Tk accessory hook installed", file=sys.stderr)
    except Exception as exc:
        print(f"[HUB] pre-Tk accessory hook failed: {exc}", file=sys.stderr)


def launch_master_hub(parent_root=None):
    global _hub_ref
    if _hub_ref:
        try: _hub_ref.destroy()
        except: pass

    # Must precede tk.Tk(): see _pre_tk_accessory(). Only for a standalone
    # root -- a Toplevel shares its parent's NSApp and Dock presence.
    if sys.platform == "darwin" and not parent_root:
        _pre_tk_accessory()

    hub = tk.Tk() if not parent_root else tk.Toplevel(parent_root)
    _hub_ref = hub

    # macOS: belt-and-braces re-assert of the accessory policy now that the
    # Tk root exists (no-op when the pre-Tk hook worked; the fallback if it
    # didn't). Accessory apps have no Dock icon or menu bar but can still
    # own key windows -- they just are never auto-activated, so
    # _activate_app() below does that explicitly.
    def _activate_app():
        if sys.platform != "darwin":
            return
        try:
            from AppKit import NSApplication
            NSApplication.sharedApplication().activateIgnoringOtherApps_(True)
        except Exception as exc:
            print(f"[HUB] activate: {exc}", file=sys.stderr)

    if sys.platform == "darwin" and not parent_root:
        try:
            from AppKit import (NSApplication,
                                NSApplicationActivationPolicyAccessory)
            NSApplication.sharedApplication().setActivationPolicy_(
                NSApplicationActivationPolicyAccessory)
            print("[HUB] activation policy: accessory (no Dock icon)",
                  file=sys.stderr)
        except Exception as exc:
            print(f"[HUB] accessory policy failed: {exc}", file=sys.stderr)

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
    _left_at = [None]
    HUB_LINGER_SECS = 5   # how long the menu stays up after the pointer leaves

    def _monitor_pointer():
        if not hub.winfo_exists(): return
        try:
            x, y = hub.winfo_pointerxy()
            rx, ry = hub.winfo_rootx(), hub.winfo_rooty()
            inside = rx <= x <= rx + w and ry <= y <= ry + h
            if inside:
                _mouse_entered[0] = True
                _left_at[0] = None          # back inside: cancel the countdown
            elif _mouse_entered[0]:
                if _left_at[0] is None:
                    _left_at[0] = time.time()
                elif time.time() - _left_at[0] >= HUB_LINGER_SECS:
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
                _activate_app()
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
            _activate_app()
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
    subtitle_var = tk.StringVar(value="Enterprise Application Matrix")
    tk.Label(title_frame, textvariable=subtitle_var, bg=SURFACE, fg=MUTED,
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
    _cwin = canvas.create_window((0, 0), window=grid, anchor="nw", width=w-30)
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(_cwin, width=e.width))

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
        _scroll_acc = [0.0]

        # This handler runs inside Tk's own Tcl_DoOneEvent (AppKit dispatch)
        # via PyObjC, NOT as a Tk callback -- so it must not touch Tk at all.
        # Any tkinter call here clears _tkinter's saved thread state, and the
        # next Python Tk callback fired in the same event iteration (e.g. the
        # one a real scroll triggers) aborts the process with "Fatal Python
        # error: PyEval_RestoreThread ... GIL is released". So only record
        # the delta here (AppKit-side hit test) and let _drain_scroll, a
        # normal Tk timer, apply it.
        def _ns_scroll(event):
            try:
                win = event.window()
                if win is not None and str(win.title()) == "AEGIS_MASTER_HUB":
                    dy = event.scrollingDeltaY()
                    if dy:
                        _scroll_acc[0] += dy
                    return None  # consumed
            except Exception as exc:
                print(f"[HUB] ns-scroll: {exc}", file=sys.stderr)
            return event

        def _drain_scroll():
            units = int(-_scroll_acc[0])     # keep sub-unit trackpad remainder
            if units:
                _scroll_acc[0] += units
                canvas.yview_scroll(units, "units")
            hub.after(16, _drain_scroll)

        hub.after(16, _drain_scroll)

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
    for _c in range(5):
        grid.columnconfigure(_c, weight=1, uniform="tile", minsize=0)
    _TILE_FONT_PT = 10                       # tile text size; raise if too small
    _WRAP = max(120, (w - 30) // 5 - 44)     # text wraps inside the tile
    def _tile_label(n):
        # Full name always shown: underscores become spaces so long names can
        # wrap at word boundaries instead of being cut off.
        return "▸ " + n.upper().replace("_", " ")

    apps_found = []
    for name, p_list in MASTER_REGISTRY:
        res = _smart_resolve(name, p_list)
        if res: apps_found.append((name, res))
    apps_found.sort(key=lambda x: x[0].lower())
    subtitle_var.set(f"Enterprise Application Matrix · {len(apps_found)} apps")

    _btn_frames = {}
    for i, (name, path) in enumerate(apps_found):
        c = ACCENT_COLORS[i % len(ACCENT_COLORS)]
        b = tk.Frame(grid, bg=BORDER, padx=1, pady=1)
        b.grid(row=i//5, column=i%5, padx=3, pady=2, sticky="nsew")
        btn = tk.Button(b, text=_tile_label(name), width=1, wraplength=_WRAP, justify="left", bg=SURFACE, fg=c, activebackground=S2, activeforeground=c, relief="flat", anchor="w", font=("Inter", _TILE_FONT_PT, "bold"), command=lambda n=name, p=path: _launch_app(n, p, close))
        btn.pack(fill=tk.BOTH, expand=True, ipady=2, ipadx=6)
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
        if q:
            subtitle_var.set(f"Enterprise Application Matrix · {vis_idx} / {len(apps_found)} apps")
        else:
            subtitle_var.set(f"Enterprise Application Matrix · {len(apps_found)} apps")
        canvas.yview_moveto(0)
        _update_scroll()

    s_var.trace_add("write", _search)

    hub.bind("<Escape>", lambda e: close())
    hub.after(20, lambda: [_activate_app(), hub.focus_force(), s_entry.focus_set(), _monitor_pointer()])

    if not parent_root: hub.mainloop()
    return hub

if __name__ == "__main__":
    launch_master_hub()
