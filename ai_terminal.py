#!/usr/bin/env python3
"""
AEGIS AI TERMINAL v3.0
Multi-context AI terminal backed by Groq (llama-3.3-70b).
Supports streaming, per-context system prompts, runnable CMD blocks,
persistent conversation history, and geometry save/restore.

API key: ~/.groq_api_key  or  $GROQ_API_KEY
"""

import sys
import os
import subprocess
import threading
import time
import re
import json
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import font as tkfont

AEGIS_DIR     = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE  = os.path.expanduser("~/.aegis_ai_history.json")
GEOMETRY_FILE = os.path.expanduser("~/.aegis_ai_geometry.json")
API_KEY_FILE  = os.path.expanduser("~/.groq_api_key")

C = {
    "bg":      "#020617",
    "surface": "#0f172a",
    "s2":      "#1e293b",
    "border":  "#334155",
    "text":    "#e2e8f0",
    "muted":   "#64748b",
    "user":    "#38bdf8",
    "ai":      "#a78bfa",
    "system":  "#10b981",
    "cmd_bg":  "#0c2a3e",
    "cmd_fg":  "#7dd3fc",
    "code_bg": "#0a1a0a",
    "code_fg": "#86efac",
    "error":   "#ef4444",
    "amber":   "#f59e0b",
}

CONTEXTS: dict[str, dict] = {
    "GLOBAL": {
        "color": "#64748b",
        "icon":  "◈",
        "system": (
            "You are AEGIS, an elite AI assistant embedded in a Linux tactical HUD. "
            "Help with system administration, coding, research, and any task. "
            "Wrap terminal commands in <CMD>command here</CMD> tags for one-click execution. "
            "Be direct, precise, and enterprise-grade."
        ),
    },
    "TERMINAL": {
        "color": "#38bdf8",
        "icon":  "▶",
        "system": (
            "You are a doctorate-level Linux systems architect embedded in a tactical HUD "
            "on KDE Plasma/Kubuntu. Give concise, production-ready bash commands and scripts. "
            "Wrap each runnable command in <CMD>command</CMD> tags for one-click execution. "
            "Be precise, no hand-holding. Output complete, runnable scripts when asked."
        ),
    },
    "CODING": {
        "color": "#f97316",
        "icon":  "⌥",
        "system": (
            "You are an elite software engineer. Provide surgical code fixes, refactors, "
            "and optimizations. Wrap runnable commands in <CMD>command</CMD> tags. "
            "Output only what is needed: working code on the first try. "
            "Identify edge cases and handle them proactively."
        ),
    },
    "AI WORKSPACE": {
        "color": "#a78bfa",
        "icon":  "⟡",
        "system": (
            "You are a prompt engineering specialist and AI workflow optimizer. "
            "Help craft better prompts, chain AI tasks, evaluate model outputs, "
            "and maximize output quality. Be strategic, precise, and meta-analytical."
        ),
    },
    "E-COMMERCE": {
        "color": "#10b981",
        "icon":  "⊕",
        "system": (
            "You are an e-commerce strategy specialist. Help with product listings, "
            "pricing strategy, supplier communication, and TikTok Shop optimization. "
            "Be tactical and conversion-focused. Provide A/B test variants when relevant."
        ),
    },
    "YOUTUBE": {
        "color": "#ef4444",
        "icon":  "▷",
        "system": (
            "You are a content strategy expert specializing in YouTube growth. "
            "Help analyze content, suggest high-CTR titles, descriptions, tags, "
            "and engagement strategies. Ground advice in platform algorithm mechanics."
        ),
    },
}

QUICK_PROMPTS = [
    ("F1 Explain",  "Explain what this does and how I could improve it:\n"),
    ("F2 Fix",      "Find and fix all bugs in this code, explain each fix:\n"),
    ("F3 Script",   "Write a production-ready bash script that does the following:\n"),
    ("F4 Optimize", "Identify redundancies and optimize this for maximum efficiency:\n"),
]



def _load_api_key() -> str:
    if os.path.exists(API_KEY_FILE):
        key = open(API_KEY_FILE).read().strip()
        if key:
            return key
    return os.environ.get("GROQ_API_KEY", "")


def _save_api_key(key: str) -> None:
    with open(API_KEY_FILE, "w") as f:
        f.write(key)
    os.chmod(API_KEY_FILE, 0o600)



class AITerminal:

    def __init__(self, context: str = "GLOBAL"):
        self.context       = context if context in CONTEXTS else "GLOBAL"
        self.conversation: list[dict] = []
        self.input_history: list[str] = []
        self.history_idx   = -1
        self.last_reply    = ""
        self.streaming     = False
        self.api_key       = _load_api_key()

        self.root = tk.Tk()
        self.root.title("AEGIS AI TERMINAL v3")
        self.root.configure(bg=C["bg"])
        #self.root.attributes("-topmost", True)
        #self.root.wm_attributes("-type", "dialog")
        self.root.resizable(True, True)
        self.root.minsize(640, 400)

        w, h, x, y = self._load_geometry()
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        self._build_ui()
        if sys.platform != "darwin":
            try:
                pass
            except: pass
        self._load_history()
        self._bind_keys()
        # self._start_focus_watcher()
        self.root.protocol("WM_DELETE_WINDOW", self._quit)

    # ── Geometry ──────────────────────────────────────────────────────────────

    def _load_geometry(self) -> tuple:
        try:
            d = json.loads(open(GEOMETRY_FILE).read())
            return d["w"], d["h"], d["x"], d["y"]
        except Exception:
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            return 960, 700, (sw - 960) // 2, (sh - 700) // 2

    def _save_geometry(self) -> None:
        try:
            m = re.match(r"(\d+)x(\d+)\+(-?\d+)\+(-?\d+)", self.root.geometry())
            if m:
                w, h, x, y = map(int, m.groups())
                open(GEOMETRY_FILE, "w").write(json.dumps({"w": w, "h": h, "x": x, "y": y}))
        except Exception:
            pass

    # ── History ───────────────────────────────────────────────────────────────

    def _load_history(self) -> None:
        try:
            if not os.path.exists(HISTORY_FILE):
                return
            data = json.loads(open(HISTORY_FILE).read())
            self.conversation  = data.get("conversation", [])[-30:]
            self.input_history = data.get("input_history", [])[-200:]
            for msg in self.conversation:
                role = msg["role"]
                if role == "user":
                    self._append_bubble("YOU", msg["content"], C["user"])
                else:
                    self._append_bubble("AEGIS", msg["content"], C["ai"])
                    self.last_reply = msg["content"]
        except Exception:
            pass

    def _save_history(self) -> None:
        try:
            open(HISTORY_FILE, "w").write(json.dumps({
                "conversation":  self.conversation[-50:],
                "input_history": self.input_history[-200:],
            }))
        except Exception:
            pass

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self._build_titlebar()
        if not self.api_key:
            self._build_keybar()
        self._build_context_bar()
        self._build_chat()
        self._build_quick_prompts()
        self._build_inputbar()

    def _build_titlebar(self) -> None:
        bar = tk.Frame(self.root, bg=C["surface"], height=38)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        ctx = CONTEXTS[self.context]
        self.ctx_badge = tk.Label(
            bar,
            text=f" {ctx['icon']} {self.context} ",
            bg=ctx["color"], fg=C["bg"],
            font=("JetBrains Mono", 8, "bold"))
        self.ctx_badge.pack(side=tk.LEFT, padx=(10, 0), pady=6)

        tk.Label(bar, text="AEGIS AI TERMINAL",
                 bg=C["surface"], fg=C["text"],
                 font=("JetBrains Mono", 10, "bold")).pack(side=tk.LEFT, padx=10)

        # Right controls
        for text, fg, cmd in [
            ("×",        C["error"],  self._quit),
            ("CLR",      C["muted"],  self._clear_chat),
            ("COPY LAST",C["ai"],     self._copy_last),
            ("NEW CHAT", C["system"], self._new_chat),
        ]:
            tk.Button(bar, text=text, bg=C["surface"], fg=fg,
                      relief="flat", font=("JetBrains Mono", 9, "bold"),
                      cursor="hand2", activebackground=C["s2"],
                      command=cmd).pack(side=tk.RIGHT, padx=5, pady=6)

    def _build_keybar(self) -> None:
        f = tk.Frame(self.root, bg="#1c0800",
                     highlightthickness=1, highlightbackground=C["amber"])
        f.pack(fill=tk.X)
        tk.Label(f, text=" ⚠ Groq API key required: ",
                 bg="#1c0800", fg=C["amber"],
                 font=("JetBrains Mono", 8, "bold")).pack(side=tk.LEFT, pady=5)
        self.key_entry = tk.Entry(f, bg=C["s2"], fg=C["text"], show="•",
                                   font=("JetBrains Mono", 9), relief="flat",
                                   width=50, insertbackground=C["amber"])
        self.key_entry.pack(side=tk.LEFT, padx=4, ipady=4)
        self.key_entry.bind("<Return>", lambda e: self._save_key())
        tk.Button(f, text="SAVE", bg="#431407", fg=C["amber"],
                  relief="flat", font=("Inter", 8, "bold"), cursor="hand2",
                  command=self._save_key).pack(side=tk.LEFT, padx=6, ipady=4, ipadx=6)

    def _build_context_bar(self) -> None:
        bar = tk.Frame(self.root, bg=C["s2"], height=32)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        tk.Label(bar, text="CONTEXT:", bg=C["s2"], fg=C["muted"],
                 font=("JetBrains Mono", 7, "bold")).pack(side=tk.LEFT, padx=(10, 4), pady=6)

        for name, data in CONTEXTS.items():
            is_active = (name == self.context)
            btn = tk.Button(
                bar, text=f"{data['icon']} {name}",
                bg=data["color"] if is_active else C["s2"],
                fg=C["bg"] if is_active else C["muted"],
                relief="flat", font=("Inter", 7, "bold"), cursor="hand2",
                command=lambda n=name: self._switch_context(n))
            btn.pack(side=tk.LEFT, padx=2, pady=4, ipady=2, ipadx=6)

    def _build_chat(self) -> None:
        outer = tk.Frame(self.root, bg=C["bg"])
        outer.pack(fill=tk.BOTH, expand=True)

        self.chat_canvas = tk.Canvas(outer, bg=C["bg"], highlightthickness=0,
                                      bd=0)
        sb = tk.Scrollbar(outer, orient="vertical", command=self.chat_canvas.yview,
                          bg=C["s2"], troughcolor=C["bg"], width=8)
        self.chat_frame = tk.Frame(self.chat_canvas, bg=C["bg"])

        self.chat_frame.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(
                scrollregion=self.chat_canvas.bbox("all")))

        self.chat_canvas.create_window((0, 0), window=self.chat_frame,
                                        anchor="nw", tags="inner")
        self.chat_canvas.configure(yscrollcommand=sb.set)

        self.chat_canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.chat_canvas.bind("<Configure>",
            lambda e: self.chat_canvas.itemconfig("inner", width=e.width))

        def _scroll(e):
            self.chat_canvas.yview_scroll(-1 if e.num == 4 else 1, "units")
        self.chat_canvas.bind("<Button-4>", _scroll)
        self.chat_canvas.bind("<Button-5>", _scroll)
        self.chat_frame.bind("<Button-4>", _scroll)
        self.chat_frame.bind("<Button-5>", _scroll)

    def _build_quick_prompts(self) -> None:
        bar = tk.Frame(self.root, bg=C["s2"])
        bar.pack(fill=tk.X)
        tk.Label(bar, text="QUICK:", bg=C["s2"], fg=C["muted"],
                 font=("JetBrains Mono", 7)).pack(side=tk.LEFT, padx=(10, 4), pady=4)
        for label, prefix in QUICK_PROMPTS:
            tk.Button(bar, text=label, bg=C["s2"], fg=C["muted"],
                      relief="flat", font=("Inter", 7), cursor="hand2",
                      command=lambda p=prefix: self._inject_prefix(p)).pack(
                          side=tk.LEFT, padx=3, pady=3, ipady=2, ipadx=4)

    def _build_inputbar(self) -> None:
        bottom = tk.Frame(self.root, bg=C["surface"],
                          highlightthickness=1, highlightbackground=C["border"])
        bottom.pack(fill=tk.X, side=tk.BOTTOM)

        self.input_box = tk.Text(
            bottom, height=3, bg=C["s2"], fg=C["text"],
            font=("JetBrains Mono", 10), relief="flat", wrap=tk.WORD,
            insertbackground=CONTEXTS[self.context]["color"],
            padx=10, pady=8, highlightthickness=0)
        self.input_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                             padx=(10, 6), pady=8)
        self.input_box.focus_set()

        send_col = CONTEXTS[self.context]["color"]
        self.send_btn = tk.Button(
            bottom, text="SEND\n↵",
            bg=send_col, fg=C["bg"],
            font=("Inter", 9, "bold"), relief="flat", cursor="hand2",
            width=7, command=self._send)
        self.send_btn.pack(side=tk.RIGHT, padx=(0, 10), pady=8, ipady=6)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(bottom, textvariable=self.status_var,
                 bg=C["surface"], fg=C["muted"],
                 font=("JetBrains Mono", 7)).pack(side=tk.BOTTOM, padx=10, pady=(0, 4))

    # ── Chat rendering ────────────────────────────────────────────────────────

    def _append_bubble(self, sender: str, content: str, color: str) -> None:
        """Add a styled message bubble to the chat frame."""
        wrapper = tk.Frame(self.chat_frame, bg=C["bg"], pady=4)
        wrapper.pack(fill=tk.X, padx=8)

        # Header row
        hdr = tk.Frame(wrapper, bg=C["bg"])
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text=f"  {sender}", bg=C["bg"], fg=color,
                 font=("JetBrains Mono", 8, "bold")).pack(side=tk.LEFT)
        ts = time.strftime("%H:%M:%S")
        tk.Label(hdr, text=ts, bg=C["bg"], fg=C["muted"],
                 font=("JetBrains Mono", 7)).pack(side=tk.LEFT, padx=6)

        # Bubble frame
        bubble_bg = C["surface"] if sender != "YOU" else C["s2"]
        bubble = tk.Frame(wrapper, bg=bubble_bg, padx=10, pady=6,
                          highlightthickness=1,
                          highlightbackground=color if sender != "YOU" else C["border"])
        bubble.pack(fill=tk.X, padx=2, pady=(2, 0))

        self._render_content(bubble, content)
        self._scroll_bottom()

    def _append_system(self, msg: str) -> None:
        wrapper = tk.Frame(self.chat_frame, bg=C["bg"], pady=2)
        wrapper.pack(fill=tk.X, padx=12)
        tk.Label(wrapper, text=msg, bg=C["bg"], fg=C["system"],
                 font=("JetBrains Mono", 8), anchor="w",
                 wraplength=800, justify=tk.LEFT).pack(fill=tk.X)
        self._scroll_bottom()

    # ── Content parser / renderer ─────────────────────────────────────────────

    _SEGMENT_RE = re.compile(
        r"<CMD>(.*?)</CMD>|```(?:\w+\n)?(.*?)```",
        re.DOTALL)

    def _parse_segments(self, content: str) -> list[tuple[str, str]]:
        segments = []
        last = 0
        for m in self._SEGMENT_RE.finditer(content):
            if m.start() > last:
                segments.append(("text", content[last:m.start()]))
            if m.group(1) is not None:
                segments.append(("cmd", m.group(1).strip()))
            else:
                segments.append(("code", m.group(2) or ""))
            last = m.end()
        if last < len(content):
            segments.append(("text", content[last:]))
        return segments

    def _render_content(self, parent: tk.Frame, content: str) -> None:
        scroll_cb = lambda e: self.chat_canvas.yview_scroll(
            -1 if e.num == 4 else 1, "units")
        for kind, text in self._parse_segments(content):
            text = text.strip()
            if not text:
                continue
            if kind == "cmd":
                self._render_cmd(parent, text)
            elif kind == "code":
                self._render_code(parent, text, scroll_cb)
            else:
                self._render_text(parent, text, scroll_cb)

    def _render_text(self, parent, text: str, scroll_cb) -> None:
        lines = min(text.count("\n") + 1, 40)
        t = tk.Text(parent, bg=parent["bg"], fg=C["text"],
                    font=("JetBrains Mono", 9), relief="flat",
                    wrap=tk.WORD, height=lines, bd=0, highlightthickness=0)
        t.insert("1.0", text)
        t.config(state=tk.DISABLED)
        t.pack(fill=tk.X, pady=1)
        t.bind("<Button-4>", scroll_cb)
        t.bind("<Button-5>", scroll_cb)

    def _render_code(self, parent, code: str, scroll_cb) -> None:
        lines = min(code.count("\n") + 1, 35)
        f = tk.Frame(parent, bg=C["code_bg"],
                     highlightthickness=1, highlightbackground="#1f4f1f",
                     padx=8, pady=4)
        f.pack(fill=tk.X, pady=3)

        ctrl = tk.Frame(f, bg=C["code_bg"])
        ctrl.pack(fill=tk.X)
        tk.Label(ctrl, text="CODE", bg=C["code_bg"], fg=C["muted"],
                 font=("JetBrains Mono", 7)).pack(side=tk.LEFT)

        def _copy():
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            self.status_var.set("Code copied to clipboard.")

        tk.Button(ctrl, text="COPY", bg=C["code_bg"], fg=C["muted"],
                  font=("Inter", 7), relief="flat", cursor="hand2",
                  command=_copy).pack(side=tk.RIGHT)

        t = tk.Text(f, bg=C["code_bg"], fg=C["code_fg"],
                    font=("JetBrains Mono", 9), relief="flat",
                    wrap=tk.NONE, height=lines, bd=0, highlightthickness=0)
        t.insert("1.0", code)
        t.config(state=tk.DISABLED)
        t.pack(fill=tk.X)
        t.bind("<Button-4>", scroll_cb)
        t.bind("<Button-5>", scroll_cb)

    def _render_cmd(self, parent, cmd: str) -> None:
        f = tk.Frame(parent, bg=C["cmd_bg"],
                     highlightthickness=1, highlightbackground=C["cmd_fg"],
                     padx=8, pady=5)
        f.pack(fill=tk.X, pady=3)

        tk.Label(f, text=f"$ {cmd}", bg=C["cmd_bg"], fg=C["cmd_fg"],
                 font=("JetBrains Mono", 9), anchor="w",
                 wraplength=700, justify=tk.LEFT).pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(f, text="COPY", bg=C["cmd_bg"], fg=C["muted"],
                  font=("Inter", 7), relief="flat", cursor="hand2",
                  command=lambda c=cmd: self._copy_cmd(c)).pack(side=tk.RIGHT, padx=2)
        tk.Button(f, text="RUN ▶", bg="#1a3a5c", fg=C["cmd_fg"],
                  font=("Inter", 8, "bold"), relief="flat", cursor="hand2",
                  command=lambda c=cmd: self._run_command(c)).pack(side=tk.RIGHT, padx=4)

    # ── Actions ───────────────────────────────────────────────────────────────

    def _run_command(self, cmd: str) -> None:
        self._append_system(f"▶ {cmd}")

        def _exec():
            try:
                t0 = time.time()
                res = subprocess.run(cmd, shell=True, capture_output=True,
                                     text=True, timeout=45)
                elapsed = time.time() - t0
                out = (res.stdout or res.stderr or "(no output)").strip()
                out = f"{out[:4000]}\n[exit {res.returncode} | {elapsed:.1f}s]"
                self.root.after(0, lambda: self._append_system(out))
            except subprocess.TimeoutExpired:
                self.root.after(0, lambda: self._append_system("✗ Timed out (45s)."))
            except Exception as exc:
                self.root.after(0, lambda e=str(exc): self._append_system(f"✗ Error: {e}"))

        threading.Thread(target=_exec, daemon=True).start()

    def _copy_cmd(self, cmd: str) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(cmd)
        self.status_var.set(f"Copied: {cmd[:80]}")

    def _copy_last(self) -> None:
        if self.last_reply:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.last_reply)
            self.status_var.set("Last reply copied.")

    def _clear_chat(self) -> None:
        for w in self.chat_frame.winfo_children():
            w.destroy()
        self.status_var.set("Chat cleared.")

    def _new_chat(self) -> None:
        self.conversation.clear()
        self._clear_chat()
        self._append_system(f"New session started — context: {self.context}")

    def _switch_context(self, name: str) -> None:
        self.context = name
        # Rebuild context bar with updated active state
        ctx = CONTEXTS[name]
        self.ctx_badge.config(text=f" {ctx['icon']} {name} ",
                               bg=ctx["color"])
        self.input_box.config(insertbackground=ctx["color"])
        self.send_btn.config(bg=ctx["color"])
        self._append_system(f"Context switched to {name}")

    def _inject_prefix(self, prefix: str) -> None:
        self.input_box.delete("1.0", tk.END)
        self.input_box.insert("1.0", prefix)
        self.input_box.focus_set()

    def _scroll_bottom(self) -> None:
        self.root.after(80, lambda: self.chat_canvas.yview_moveto(1.0))

    # ── API ───────────────────────────────────────────────────────────────────

    def _send(self) -> None:
        text = self.input_box.get("1.0", tk.END).strip()
        if not text or self.streaming:
            return
        self.input_box.delete("1.0", tk.END)
        self.history_idx = -1
        if not self.input_history or self.input_history[-1] != text:
            self.input_history.append(text)
        self._append_bubble("YOU", text, C["user"])
        self.conversation.append({"role": "user", "content": text})
        threading.Thread(target=self._call_api, daemon=True).start()

    def _call_api(self) -> None:
        if not self.api_key:
            self.root.after(0, lambda: self._append_system(
                "✗ No Groq API key. Enter it in the bar above and click SAVE."))
            return

        self.streaming = True
        t0 = time.time()
        ctx_name  = self.context
        ctx_color = CONTEXTS[ctx_name]["color"]
        self.root.after(0, lambda: self.status_var.set(
            f"Thinking… [{ctx_name}] · Groq · llama-3.3-70b"))
        self.root.after(0, lambda: self.send_btn.config(
            state=tk.DISABLED, text="…"))

        system_prompt = CONTEXTS[ctx_name]["system"]
        messages = [{"role": "system", "content": system_prompt}]
        for msg in self.conversation[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        payload = json.dumps({
            "model":       "llama-3.3-70b-versatile",
            "max_tokens":  2048,
            "temperature": 0.65,
            "messages":    messages,
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type":  "application/json",
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                },
                method="POST")
            with urllib.request.urlopen(req, timeout=90) as resp:
                data    = json.loads(resp.read().decode("utf-8"))
                reply   = data["choices"][0]["message"]["content"]
                usage   = data.get("usage", {})
                elapsed = time.time() - t0

                self.last_reply = reply
                self.conversation.append({"role": "assistant", "content": reply})
                self._save_history()

                status = (f"Ready  ·  "
                          f"{usage.get('prompt_tokens',0)} prompt  "
                          f"{usage.get('completion_tokens',0)} completion  ·  "
                          f"{elapsed:.1f}s")

                self.root.after(0, lambda r=reply:
                    self._append_bubble("AEGIS", r, C["ai"]))
                self.root.after(0, lambda s=status: self.status_var.set(s))

        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            self.root.after(0, lambda c=exc.code, b=body: self._append_system(f"✗ Groq HTTP {c}: {b[:400]}"))
        except Exception as exc:
            self.root.after(0, lambda e=str(exc): self._append_system(f"✗ Connection error: {e}"))
        finally:
            self.streaming = False
            self.root.after(0, lambda: self.send_btn.config(
                state=tk.NORMAL, text="SEND\n↵"))

    # ── Keybinds ──────────────────────────────────────────────────────────────

    def _bind_keys(self) -> None:
        self.root.bind("<Control-Return>", lambda e: self._send())
        self.root.bind("<Escape>",         lambda e: self._quit())
        self.root.bind("<Alt-c>",          lambda e: self._clear_chat())
        self.root.bind("<Alt-n>",          lambda e: self._new_chat())
        self.input_box.bind("<Return>",    self._on_return)
        self.input_box.bind("<Up>",        self._history_prev)
        self.input_box.bind("<Down>",      self._history_next)

        fkeys = [("F1", 0), ("F2", 1), ("F3", 2), ("F4", 3)]
        for key, idx in fkeys:
            if idx < len(QUICK_PROMPTS):
                self.root.bind(f"<{key}>",
                    lambda e, i=idx: self._inject_prefix(QUICK_PROMPTS[i][1]))

    def _on_return(self, event) -> str:
        if event.state & 0x4:   # Ctrl+Enter → send
            self._send()
            return "break"
        return ""               # plain Enter → newline

    def _history_prev(self, event) -> str:
        if not self.input_history:
            return ""
        self.history_idx = max(0, self.history_idx - 1
                               if self.history_idx >= 0
                               else len(self.input_history) - 1)
        self.input_box.delete("1.0", tk.END)
        self.input_box.insert("1.0", self.input_history[self.history_idx])
        return "break"

    def _history_next(self, event) -> str:
        if not self.input_history or self.history_idx < 0:
            return ""
        if self.history_idx >= len(self.input_history) - 1:
            self.history_idx = -1
            self.input_box.delete("1.0", tk.END)
        else:
            self.history_idx += 1
            self.input_box.delete("1.0", tk.END)
            self.input_box.insert("1.0", self.input_history[self.history_idx])
        return "break"

    # ── Focus watcher / quit ──────────────────────────────────────────────────

    def _start_focus_watcher(self) -> None:
        our_pid = str(os.getpid())

        def _watch():
            time.sleep(1.0)
            while True:
                time.sleep(1.5)
                try:
                    pid = subprocess.check_output(
                        ["xdotool", "getactivewindow", "getwindowpid"],
                        stderr=subprocess.DEVNULL).decode().strip()
                    if pid and pid != our_pid:
                        self.root.after(0, self._quit)
                        return
                except Exception:
                    pass

        threading.Thread(target=_watch, daemon=True).start()

    def _save_key(self) -> None:
        key = self.key_entry.get().strip()
        if key:
            self.api_key = key
            _save_api_key(key)
            self._append_system("✓ Groq API key saved securely.")

    def _quit(self) -> None:
        self._save_geometry()
        self._save_history()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()



if __name__ == "__main__":
    ctx = sys.argv[1].upper() if len(sys.argv) > 1 else "GLOBAL"
    term = AITerminal(ctx)
    term.run()
