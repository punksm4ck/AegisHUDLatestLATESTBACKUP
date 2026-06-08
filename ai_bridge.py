#!/usr/bin/env python3
"""
AEGIS AI Bridge v3.0
Expert-mode prompt injection workspace.
Select a context category and specialist tool, then copy or inject the
system prompt directly into any focused input via xdotool.
"""
import sys
import os
import subprocess
import time
import threading
import tkinter as tk

PROMPT_LIBRARY: dict[str, dict] = {
    "sysadmin": {
        "title":  "SYSADMIN AI OPERATIONS",
        "color":  "#38bdf8",
        "icon":   "▶",
        "tools": {
            "Enterprise Architect": (
                "You are a doctorate-level Linux systems architect. Analyze the following "
                "request and output purely functional, highly polished, commercially-viable "
                "bash scripts. Think iteratively and use cognitive recognition to correct "
                "all bugs before outputting. Output complete, runnable scripts only."
            ),
            "Log Forensics": (
                "Act as a forensic Linux administrator. Parse the following log output. "
                "Identify the root cause and provide the exact command-line syntax to "
                "remediate. Be precise, reference specific line numbers and error codes."
            ),
            "Security Auditor": (
                "Review the following configuration for privilege escalation vectors and "
                "vulnerabilities. Provide a hardened replacement with inline comments "
                "explaining each change. Follow CIS benchmark guidelines."
            ),
            "Cron / Systemd": (
                "You are a Linux scheduling specialist. Design a robust cron job or "
                "systemd unit for the following task. Include error handling, logging, "
                "and idempotency checks."
            ),
        },
    },
    "code": {
        "title":  "CODE SURGEON WORKSPACE",
        "color":  "#10b981",
        "icon":   "⌥",
        "tools": {
            "Memory & Race Scan": (
                "Analyze for memory leaks and race conditions. Provide a surgical "
                "solution with absolute precision. No explanations; only the enterprise "
                "fix with inline comments where logic changes."
            ),
            "Syntax Surgeon": (
                "The following code is throwing errors. Refactor it into a "
                "commercially-viable, production-ready solution that works on the first "
                "run. Preserve all existing functionality, improve nothing beyond the fix."
            ),
            "Refactor Pro": (
                "Identify redundancies and optimize this code for maximum efficiency "
                "while maintaining enterprise-grade reliability. Flag any breaking "
                "changes. Output only the refactored code with a change summary."
            ),
            "API Designer": (
                "Design a clean, RESTful API for the following specification. Include "
                "endpoint definitions, request/response schemas, error codes, and "
                "authentication flow. Follow OpenAPI 3.0 conventions."
            ),
        },
    },
    "ecommerce": {
        "title":  "E-COMMERCE STRATEGY AI",
        "color":  "#f59e0b",
        "icon":   "⊕",
        "tools": {
            "Product Descriptions": (
                "Generate high-conversion, SEO-optimized product descriptions for "
                "custom-printed apparel based on these specs. Include a headline, "
                "3-5 bullet benefits, and a closing CTA. Optimize for TikTok Shop."
            ),
            "Market Analyzer": (
                "Analyze these competitor prices and listing data. Provide a tactical "
                "pricing strategy to maximize TikTok Shop visibility and conversion rate. "
                "Include psychological pricing recommendations."
            ),
            "Supplier Liaison": (
                "Draft a professional, firm, yet empathetic response to a supplier "
                "regarding print quality discrepancies. Request remediation, set clear "
                "expectations, and preserve the supplier relationship."
            ),
            "TikTok Script": (
                "Write a viral TikTok script for the following product. Hook in the "
                "first 2 seconds. Structure: Hook → Problem → Solution → Proof → CTA. "
                "Keep total runtime under 30 seconds. Use conversational language."
            ),
        },
    },
    "research": {
        "title":  "RESEARCH & ANALYSIS",
        "color":  "#a78bfa",
        "icon":   "◈",
        "tools": {
            "Deep Analyst": (
                "Conduct a thorough analysis of the following topic. Structure your "
                "response as: Executive Summary → Key Findings → Supporting Evidence → "
                "Counterarguments → Conclusion. Cite reasoning clearly."
            ),
            "Fact Extractor": (
                "Extract all concrete, verifiable facts from the following text. "
                "Present them as a numbered list. Flag any claims that appear "
                "speculative or unverified."
            ),
            "Comparative Matrix": (
                "Compare the following options across all relevant dimensions. "
                "Present as a structured comparison with a final recommendation "
                "and rationale. Be definitive."
            ),
        },
    },
}


class AIBridge:

    def __init__(self, mode: str = "sysadmin"):
        self.mode = mode if mode in PROMPT_LIBRARY else "sysadmin"
        self.data = PROMPT_LIBRARY[self.mode]
        self._dead = [False]

        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(
            bg="#020617",
            highlightthickness=1,
            highlightbackground=self.data["color"])

        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        w, h = 860, 540
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        self._build_ui()
        self._load_tools()

        threading.Thread(target=self._watch_clicks,
                          args=(x, y, w, h), daemon=True).start()
        self.root.mainloop()

    def _build_ui(self) -> None:
        c = self.data["color"]

        # Header
        hdr = tk.Frame(self.root, bg="#0f172a")
        hdr.pack(fill=tk.X)
        tk.Label(hdr,
                 text=f"  {self.data['icon']}  {self.data['title']}",
                 bg="#0f172a", fg=c,
                 font=("JetBrains Mono", 11, "bold")).pack(side=tk.LEFT, pady=10)

        # Mode switcher
        for mode_key, mode_data in PROMPT_LIBRARY.items():
            is_active = (mode_key == self.mode)
            btn = tk.Button(hdr,
                            text=mode_data["icon"],
                            bg=mode_data["color"] if is_active else "#0f172a",
                            fg="#020617" if is_active else mode_data["color"],
                            relief="flat", font=("JetBrains Mono", 10),
                            cursor="hand2",
                            command=lambda m=mode_key: self._switch_mode(m))
            btn.pack(side=tk.RIGHT, padx=3, pady=6, ipadx=6, ipady=3)

        tk.Button(hdr, text="✕", bg="#0f172a", fg="#ef4444",
                  relief="flat", font=("JetBrains Mono", 11), cursor="hand2",
                  command=self._close).pack(side=tk.RIGHT, padx=8, pady=8)

        # Body
        body = tk.Frame(self.root, bg="#020617")
        body.pack(fill=tk.BOTH, expand=True, padx=16, pady=10)

        # Tool list
        list_frame = tk.Frame(body, bg="#0f172a",
                               highlightthickness=1, highlightbackground="#1e293b")
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        tk.Label(list_frame, text="TOOLS", bg="#0f172a", fg="#475569",
                 font=("JetBrains Mono", 7, "bold")).pack(padx=10, pady=(8, 4))

        self.listbox = tk.Listbox(
            list_frame, bg="#0f172a", fg="#94a3b8",
            font=("Inter", 9), borderwidth=0, highlightthickness=0,
            selectbackground=c, selectforeground="#020617",
            width=22, activestyle="none")
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 8))
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        # Prompt display
        right = tk.Frame(body, bg="#020617")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(right, text="SYSTEM PROMPT", bg="#020617", fg="#475569",
                 font=("JetBrains Mono", 7, "bold")).pack(anchor="w", pady=(0, 4))

        self.text_area = tk.Text(
            right, bg="#0f172a", fg="#f1f5f9",
            font=("JetBrains Mono", 9), borderwidth=0,
            highlightthickness=1, highlightbackground="#1e293b",
            padx=12, pady=10, wrap=tk.WORD, relief="flat")
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # Custom prompt note
        tk.Label(right, text="You can edit the prompt above before copying.",
                 bg="#020617", fg="#475569",
                 font=("Inter", 7)).pack(anchor="w", pady=(4, 0))

        # Footer
        foot = tk.Frame(self.root, bg="#020617")
        foot.pack(fill=tk.X, padx=16, pady=(0, 14))

        tk.Button(foot, text="COPY TO CLIPBOARD",
                  bg="#1e293b", fg=c,
                  font=("Inter", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._copy).pack(side=tk.LEFT, ipady=7, ipadx=12, padx=(0, 10))

        tk.Button(foot, text="INJECT (Ctrl+V) ▸",
                  bg=c, fg="#020617",
                  font=("Inter", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._inject).pack(side=tk.LEFT, ipady=7, ipadx=12)

        self.status_var = tk.StringVar(value="Select a tool to load its system prompt.")
        tk.Label(foot, textvariable=self.status_var,
                 bg="#020617", fg="#475569",
                 font=("JetBrains Mono", 7)).pack(side=tk.RIGHT)

    def _load_tools(self) -> None:
        self.listbox.delete(0, tk.END)
        for name in self.data["tools"]:
            self.listbox.insert(tk.END, f"  {name}")
        if self.listbox.size() > 0:
            self.listbox.selection_set(0)
            self._on_select()

    def _on_select(self, event=None) -> None:
        sel = self.listbox.curselection()
        if not sel:
            return
        name   = list(self.data["tools"].keys())[sel[0]]
        prompt = self.data["tools"][name]
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", prompt)
        self.status_var.set(f"Loaded: {name}")

    def _switch_mode(self, mode: str) -> None:
        self.mode = mode
        self.data = PROMPT_LIBRARY[mode]
        # Rebuild header color + reload tools
        self.root.configure(highlightbackground=self.data["color"])
        self._load_tools()

    def _get_prompt(self) -> str:
        return self.text_area.get("1.0", tk.END).strip()

    def _copy(self) -> None:
        text = self._get_prompt()
        if not text:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_var.set("✓ Copied to clipboard.")
        try:
            subprocess.call(["notify-send", "AEGIS BRIDGE", "Prompt copied"])
        except Exception:
            pass

    def _inject(self) -> None:
        self._copy()
        self._close()
        time.sleep(0.25)
        try:
            subprocess.call(["xdotool", "key", "ctrl+v"])
        except Exception:
            pass

    def _close(self) -> None:
        if self._dead[0]:
            return
        self._dead[0] = True
        try:
            self.root.destroy()
        except Exception:
            pass

    def _watch_clicks(self, x: int, y: int, w: int, h: int) -> None:
        try:
            from Xlib import display as Xdisplay, X
            dpy  = Xdisplay.Display()
            root = dpy.screen().root
            root.grab_button(X.AnyButton, X.AnyModifier, True,
                             X.ButtonPressMask, X.GrabModeSync,
                             X.GrabModeAsync, X.NONE, X.NONE)
            dpy.sync()
            while not self._dead[0]:
                if dpy.pending_events() > 0:
                    ev = dpy.next_event()
                    if ev.type == X.ButtonPress:
                        mx, my = ev.root_x, ev.root_y
                        inside = (x <= mx <= x + w) and (y <= my <= y + h)
                        dpy.allow_events(X.ReplayPointer, X.CurrentTime)
                        dpy.sync()
                        if not inside:
                            self.root.after(0, self._close)
                            break
                    else:
                        dpy.allow_events(X.ReplayPointer, X.CurrentTime)
                        dpy.sync()
                else:
                    time.sleep(0.05)
            root.ungrab_button(X.AnyButton, X.AnyModifier)
            dpy.sync()
            dpy.close()
        except Exception:
            pass


if __name__ == "__main__":
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "sysadmin"
    AIBridge(mode)
