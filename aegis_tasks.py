#!/usr/bin/env python3
"""
AEGIS Task Panel v3.0
Two-tab panel: PERSONAL TASKS (priority queue, persist to JSON) and LIVE PROCESSES.
"""
import tkinter as tk
import psutil
import threading
import time
import json
import os
import subprocess

_panel_ref = None
TASKS_FILE = os.path.expanduser("~/.aegis_tasks.json")

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
ORANGE  = "#fb923c"

PRIORITY_ORDER  = ["HIGH", "MED", "LOW"]
PRIORITY_COLORS = {"HIGH": RED, "MED": YELLOW, "LOW": GREEN}



def _load_tasks() -> list:
    try:
        if os.path.exists(TASKS_FILE):
            return json.loads(open(TASKS_FILE).read())
    except Exception:
        pass
    return []


def _save_tasks(tasks: list) -> None:
    try:
        with open(TASKS_FILE, "w") as f:
            json.dump(tasks, f, indent=2)
    except Exception:
        pass



def launch_tasks_panel(parent_root: tk.Tk) -> None:
    global _panel_ref
    if _panel_ref is not None and _panel_ref.winfo_exists():
        return

    sw = parent_root.winfo_screenwidth()
    sh = parent_root.winfo_screenheight()

    panel = tk.Toplevel(parent_root)
    _panel_ref = panel
    panel.overrideredirect(True)
    panel.attributes("-topmost", True)
    panel.configure(bg=BG, highlightthickness=1, highlightbackground=ORANGE)

    w = 660
    h = min(sh - 100, 800)
    x = sw - w - 20
    y = 44
    panel.geometry(f"{w}x{h}+{x}+{y}")

    _dead = [False]
    _tab  = [0]

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

    threading.Thread(target=_watch, daemon=True).start()

    # ── Header ────────────────────────────────────────────────────────────────
    hdr = tk.Frame(panel, bg=SURFACE)
    hdr.pack(fill=tk.X)
    tk.Label(hdr, text="⊕ AEGIS TASK CENTER",
             bg=SURFACE, fg=ORANGE,
             font=("JetBrains Mono", 11, "bold")).pack(side=tk.LEFT, padx=14, pady=10)
    tk.Button(hdr, text="✕", bg=SURFACE, fg=RED,
              relief="flat", font=("JetBrains Mono", 11), cursor="hand2",
              command=close).pack(side=tk.RIGHT, padx=10, pady=8)

    # ── Tab bar ───────────────────────────────────────────────────────────────
    tab_bar = tk.Frame(panel, bg=S2)
    tab_bar.pack(fill=tk.X)

    content = tk.Frame(panel, bg=BG)
    content.pack(fill=tk.BOTH, expand=True)

    def show_tab(t: int):
        _tab[0] = t
        for child in content.winfo_children():
            child.destroy()
        if t == 0:
            btn_tasks.config(bg=ORANGE, fg=BG)
            btn_procs.config(bg=S2, fg=MUTED)
            _build_tasks(content)
        else:
            btn_tasks.config(bg=S2, fg=MUTED)
            btn_procs.config(bg=PURPLE, fg=BG)
            _build_procs(content)

    btn_tasks = tk.Button(tab_bar, text="PERSONAL TASKS", bg=ORANGE, fg=BG,
                          relief="flat", font=("Inter", 8, "bold"), cursor="hand2",
                          command=lambda: show_tab(0))
    btn_tasks.pack(side=tk.LEFT, padx=4, pady=4, ipadx=10, ipady=3)

    btn_procs = tk.Button(tab_bar, text="LIVE PROCESSES", bg=S2, fg=MUTED,
                          relief="flat", font=("Inter", 8, "bold"), cursor="hand2",
                          command=lambda: show_tab(1))
    btn_procs.pack(side=tk.LEFT, padx=4, pady=4, ipadx=10, ipady=3)

    # ── Tasks tab ─────────────────────────────────────────────────────────────

    def _build_tasks(parent: tk.Frame):
        tasks = _load_tasks()

        # Add task bar
        add_row = tk.Frame(parent, bg=SURFACE)
        add_row.pack(fill=tk.X, padx=10, pady=8)

        entry = tk.Entry(add_row, bg=S2, fg=TEXT, font=("JetBrains Mono", 9),
                         relief="flat", insertbackground=ORANGE)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 6))

        placeholder = "New task description…"
        entry.insert(0, placeholder)
        entry.config(fg=MUTED)

        def _focus_in(e):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=TEXT)

        def _focus_out(e):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg=MUTED)

        entry.bind("<FocusIn>",  _focus_in)
        entry.bind("<FocusOut>", _focus_out)

        prio_var = tk.StringVar(value="MED")
        for p in PRIORITY_ORDER:
            tk.Radiobutton(add_row, text=p, variable=prio_var, value=p,
                           bg=SURFACE, fg=PRIORITY_COLORS[p],
                           selectcolor=SURFACE, activebackground=SURFACE,
                           font=("Inter", 7, "bold")).pack(side=tk.LEFT, padx=2)

        def _add():
            text = entry.get().strip()
            if not text or text == placeholder:
                return
            tasks.append({
                "text":     text,
                "priority": prio_var.get(),
                "done":     False,
                "ts":       time.strftime("%H:%M"),
                "date":     time.strftime("%Y-%m-%d"),
            })
            _save_tasks(tasks)
            entry.delete(0, tk.END)
            _refresh(task_list, tasks)

        entry.bind("<Return>", lambda e: _add())
        tk.Button(add_row, text="ADD", bg=ORANGE, fg=BG,
                  relief="flat", font=("Inter", 8, "bold"), cursor="hand2",
                  command=_add).pack(side=tk.LEFT, padx=4, ipady=6, ipadx=8)

        # Stats row
        pending = sum(1 for t in tasks if not t.get("done"))
        done_ct = len(tasks) - pending
        stats = tk.Frame(parent, bg=BG)
        stats.pack(fill=tk.X, padx=12)
        tk.Label(stats, text=f"{pending} pending  ·  {done_ct} done",
                 bg=BG, fg=MUTED, font=("JetBrains Mono", 7)).pack(side=tk.LEFT)

        if tasks:
            tk.Button(stats, text="CLEAR DONE", bg=BG, fg=MUTED,
                      relief="flat", font=("Inter", 7), cursor="hand2",
                      command=lambda: _clear_done(tasks, task_list)).pack(
                          side=tk.RIGHT, padx=4)

        # Scrollable list
        outer = tk.Frame(parent, bg=BG)
        outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=(4, 10))

        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        sb     = tk.Scrollbar(outer, orient="vertical", command=canvas.yview,
                               bg=S2, troughcolor=BG, width=8)
        task_list = tk.Frame(canvas, bg=BG)

        task_list.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=task_list, anchor="nw", width=w - 50)
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        def _sc(e):
            canvas.yview_scroll(-1 if e.num == 4 else 1, "units")
        canvas.bind("<Button-4>", _sc)
        canvas.bind("<Button-5>", _sc)

        _refresh(task_list, tasks)

    def _clear_done(tasks: list, container):
        tasks[:] = [t for t in tasks if not t.get("done")]
        _save_tasks(tasks)
        _refresh(container, tasks)

    def _refresh(container: tk.Frame, tasks: list):
        for child in container.winfo_children():
            child.destroy()

        pending  = [t for t in tasks if not t.get("done")]
        done_lst = [t for t in tasks if t.get("done")]

        pending.sort(key=lambda t: PRIORITY_ORDER.index(t.get("priority", "MED")))

        for task in pending:
            _task_row(container, task, tasks)

        if done_lst:
            tk.Label(container, text="── COMPLETED ──",
                     bg=BG, fg=MUTED, font=("JetBrains Mono", 7)).pack(pady=(10, 3))
            for task in done_lst[-10:]:
                _task_row(container, task, tasks)

    def _task_row(parent: tk.Frame, task: dict, all_tasks: list):
        p    = task.get("priority", "MED")
        c    = PRIORITY_COLORS[p]
        done = task.get("done", False)
        bg   = S2 if done else SURFACE

        row = tk.Frame(parent, bg=bg, highlightthickness=1,
                       highlightbackground=c if not done else MUTED)
        row.pack(fill=tk.X, pady=2)

        def _toggle():
            task["done"] = not task["done"]
            _save_tasks(all_tasks)
            show_tab(0)

        def _delete():
            all_tasks.remove(task)
            _save_tasks(all_tasks)
            show_tab(0)

        tk.Label(row, text=f"[{p}]", bg=bg, fg=c if not done else MUTED,
                 font=("JetBrains Mono", 7, "bold"), width=6).pack(
                     side=tk.LEFT, padx=(6, 2), pady=7)

        tk.Label(row, text=task.get("text", ""),
                 bg=bg, fg=MUTED if done else TEXT,
                 font=("Inter", 9, "overstrike" if done else "normal"),
                 anchor="w", wraplength=400, justify=tk.LEFT).pack(
                     side=tk.LEFT, fill=tk.X, expand=True, pady=7)

        tk.Label(row, text=task.get("ts", ""), bg=bg, fg=MUTED,
                 font=("JetBrains Mono", 7)).pack(side=tk.LEFT, padx=4)

        tk.Button(row, text="✓" if not done else "↩", bg=bg,
                  fg=GREEN if not done else MUTED,
                  relief="flat", font=("Inter", 9), cursor="hand2",
                  command=_toggle).pack(side=tk.LEFT, padx=3, pady=5)

        tk.Button(row, text="✕", bg=bg, fg=RED,
                  relief="flat", font=("Inter", 9), cursor="hand2",
                  command=_delete).pack(side=tk.LEFT, padx=(0, 6), pady=5)

    # ── Processes tab ─────────────────────────────────────────────────────────

    def _build_procs(parent: tk.Frame):
        outer = tk.Frame(parent, bg=BG)
        outer.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        sb     = tk.Scrollbar(outer, orient="vertical", command=canvas.yview,
                               bg=S2, troughcolor=BG, width=8)
        inner  = tk.Frame(canvas, bg=BG)

        inner.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw", width=w - 40)
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        def _sc(e):
            canvas.yview_scroll(-1 if e.num == 4 else 1, "units")
        canvas.bind("<Button-4>", _sc)
        canvas.bind("<Button-5>", _sc)

        # Sort selector
        ctrl = tk.Frame(inner, bg=BG)
        ctrl.pack(fill=tk.X, pady=(0, 4))
        sort_var = tk.StringVar(value="cpu")
        tk.Label(ctrl, text="Sort:", bg=BG, fg=MUTED,
                 font=("JetBrains Mono", 7)).pack(side=tk.LEFT, padx=4)
        for label, val in [("CPU%", "cpu"), ("RAM%", "ram"), ("Name", "name")]:
            tk.Radiobutton(ctrl, text=label, variable=sort_var, value=val,
                           bg=BG, fg=MUTED, selectcolor=BG, activebackground=BG,
                           font=("Inter", 7, "bold"),
                           command=lambda: _fill_procs(proc_frame, sort_var.get())
                           ).pack(side=tk.LEFT, padx=2)

        # Header row
        hdr_row = tk.Frame(inner, bg=S2)
        hdr_row.pack(fill=tk.X, pady=(2, 1))
        for col, cw in [("PID", 6), ("NAME", 22), ("CPU%", 6),
                         ("RAM%", 6), ("THR", 5), ("STATUS", 10)]:
            tk.Label(hdr_row, text=col, bg=S2, fg=MUTED,
                     font=("JetBrains Mono", 7, "bold"),
                     width=cw, anchor="w").pack(side=tk.LEFT, padx=2, pady=3)

        proc_frame = tk.Frame(inner, bg=BG)
        proc_frame.pack(fill=tk.X)

        def _color(pct):
            if pct >= 50: return RED
            if pct >= 20: return YELLOW
            return TEXT

        def _fill_procs(container: tk.Frame, sort_by: str):
            for child in container.winfo_children():
                child.destroy()

            procs = []
            for p in psutil.process_iter(["pid", "name", "cpu_percent",
                                            "memory_percent", "num_threads", "status"]):
                try:
                    procs.append(p.info)
                except Exception:
                    pass

            key_fn = {
                "cpu":  lambda x: x.get("cpu_percent") or 0,
                "ram":  lambda x: x.get("memory_percent") or 0,
                "name": lambda x: (x.get("name") or "").lower(),
            }.get(sort_by, lambda x: x.get("cpu_percent") or 0)

            procs.sort(key=key_fn, reverse=(sort_by != "name"))

            for proc in procs[:40]:
                cpu_p = proc.get("cpu_percent") or 0
                ram_p = proc.get("memory_percent") or 0
                row   = tk.Frame(container, bg=BG)
                row.pack(fill=tk.X, pady=1)

                for txt, cw in [
                    (str(proc.get("pid", "")),         6),
                    (str(proc.get("name", ""))[:22],   22),
                    (f"{cpu_p:.1f}",                   6),
                    (f"{ram_p:.1f}",                   6),
                    (str(proc.get("num_threads", "?")),5),
                    (str(proc.get("status", ""))[:10], 10),
                ]:
                    tk.Label(row, text=txt, bg=BG,
                             fg=_color(cpu_p) if "." in txt else TEXT,
                             font=("JetBrains Mono", 7), width=cw,
                             anchor="w").pack(side=tk.LEFT, padx=2)

                def _kill(pid=proc.get("pid")):
                    try:
                        subprocess.call(["kill", "-9", str(pid)])
                    except Exception:
                        pass
                    panel.after(100, lambda: show_tab(1))

                tk.Button(row, text="KILL", bg="#450a0a", fg=RED,
                          font=("Inter", 6, "bold"), relief="flat",
                          cursor="hand2", command=_kill).pack(side=tk.LEFT, padx=3)

        _fill_procs(proc_frame, "cpu")

    show_tab(0)
