import tkinter as tk
from ui.theme import T, divider, section_title, make_btn
from core import state
from utils.i18n import tr, LANGUAGES, get_language, set_language


_DEFAULT_HOTKEYS = {
    "hotkey":           "f7",
    "macro_hotkey":     "f8",
    "color_hotkey":     "f9",
    "image_hotkey":     "f10",
    "kb_hotkey":        "f5",
    "kb_key_hotkey":    "f11",
    "kb_combo_hotkey":  "f3",
    "mouse_hotkey":     "f6",
}


class SettingsPanel:
    def __init__(self, parent, settings):
        self.settings = settings
        self._hotkey_labels = {}
        self.box = tk.Frame(parent, bg=T("SURFACE"))
        self.box.pack(fill="both", expand=True)
        self._build()
        self._poll_hotkeys()

    def _poll_hotkeys(self):
        """Periodically sync hotkey badge labels from state."""
        try:
            for field, lbl in self._hotkey_labels.items():
                cur = getattr(state, field, "—").upper()
                if lbl.cget("text") != cur:
                    lbl.config(text=cur, bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"))
        except Exception:
            pass
        self.box.after(500, self._poll_hotkeys)

    def update_hotkey_display(self, field, key_name):
        """Called externally when a hotkey changes."""
        if field in self._hotkey_labels:
            self._hotkey_labels[field].config(
                text=key_name.upper(),
                bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"))

    def _build(self):
        box = self.box
        canvas = tk.Canvas(box, bg=T("SURFACE"), highlightthickness=0)
        sb = tk.Scrollbar(box, orient="vertical", command=canvas.yview,
                          bg=T("SCROLL_BG"), troughcolor=T("SCROLL_BG"),
                          activebackground=T("SCROLL_ACTIVE"),
                          relief="flat", bd=0, width=10)
        canvas.configure(yscrollcommand=self._make_sb_handler(canvas, sb))
        canvas.pack(side="left", fill="both", expand=True)
        wrap = tk.Frame(canvas, bg=T("SURFACE"))
        win  = canvas.create_window((0, 0), window=wrap, anchor="nw")

        def on_fc(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            self._update_sb_visibility(canvas, sb)
        def on_cc(e):
            canvas.itemconfig(win, width=e.width)
            self._update_sb_visibility(canvas, sb)
        wrap.bind("<Configure>", on_fc)
        canvas.bind("<Configure>", on_cc)
        canvas.bind("<Enter>",
            lambda e: canvas.bind_all("<MouseWheel>",
                lambda ev: canvas.yview_scroll(int(-1*(ev.delta/120)), "units")))
        canvas.bind("<Leave>",
            lambda e: canvas.unbind_all("<MouseWheel>"))

        title_bar = tk.Frame(wrap, bg=T("SURFACE"))
        title_bar.pack(fill="x", padx=32, pady=(28, 6))
        tk.Label(title_bar, text=tr("SETTINGS"),
                  bg=T("SURFACE"), fg=T("FG"),
                  font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(title_bar, text=tr("Application preferences"),
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 0))

        divider(wrap, padx=32, pady=(16, 0))

        body = tk.Frame(wrap, bg=T("SURFACE"))
        body.pack(fill="x", padx=32, pady=(20, 0))

        # ── Language ──────────────────────────────────────
        section_title(body, tr("LANGUAGE"), bg=T("SURFACE"))
        lang_row = tk.Frame(body, bg=T("SURFACE"))
        lang_row.pack(fill="x", pady=6)
        tk.Label(lang_row, text=tr("Select your preferred language."),
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 9)).pack(side="left")

        from tkinter import ttk as _ttk
        self._lang_var = tk.StringVar(value=LANGUAGES.get(get_language(), "English"))
        lang_cb = _ttk.Combobox(
            lang_row, textvariable=self._lang_var,
            values=list(LANGUAGES.values()),
            state="readonly", width=20,
            font=("Segoe UI", 9)
        )
        lang_cb.pack(side="right")

        def on_lang_sel(event):
            selected_name = self._lang_var.get()
            selected_code = "en"
            for code, name in LANGUAGES.items():
                if name == selected_name:
                    selected_code = code
                    break
            set_language(selected_code)
            if self.settings.get("on_language_change"):
                self.settings["on_language_change"]()

        lang_cb.bind("<<ComboboxSelected>>", on_lang_sel)
        divider(body, pady=(20, 10))

        # ── Display ───────────────────────────────────────
        section_title(body, tr("DISPLAY"), bg=T("SURFACE"))

        self.indicator_var = tk.BooleanVar(
            value=self.settings.get("show_indicator", True))
        self._make_toggle(
            body, self.indicator_var,
            tr("SHOW ACTIVE TASK INDICATOR"),
            tr("Overlay shown in bottom-right corner during automation")
        )
        divider(body, pady=10)

        self.border_var = tk.BooleanVar(
            value=self.settings.get("show_scan_border", True))
        self._make_toggle(
            body, self.border_var,
            tr("SHOW SCAN AREA BORDER"),
            tr("Highlight border around scan region during color/image detection")
        )
        divider(body, pady=(20, 10))

        # ── Logic ───────────────────────────────────────
        section_title(body, tr("LOGIC & PERFORMANCE"), bg=T("SURFACE"))

        self.humanize_var = tk.BooleanVar(
            value=getattr(state, "humanize", False))
        self._make_toggle(
            body, self.humanize_var,
            tr("HUMANIZE (ANTI-BOT JITTER)"),
            tr("Add random variations to click coordinates and wait times to evade detection")
        )
        divider(body, pady=(20, 10))

        # ── Hotkeys ───────────────────────────────────────
        section_title(body, tr("HOTKEYS"), bg=T("SURFACE"))
        tk.Label(body,
                  text=tr("Current hotkey assignments. Change them from each panel."),
                  bg=T("SURFACE"), fg=T("FG3"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 10))

        hotkey_rows = [
            ("hotkey",          "Run / Stop Steps"),
            ("macro_hotkey",    "Record Actions"),
            ("color_hotkey",    "Color Detection"),
            ("image_hotkey",    "Image Detection"),
            ("kb_key_hotkey",   "Keyboard — Single Key"),
            ("kb_combo_hotkey", "Keyboard — Combo"),
            ("mouse_hotkey",    "Mouse Panel"),
        ]

        for field, label in hotkey_rows:
            row = tk.Frame(body, bg=T("SURFACE"))
            row.pack(fill="x", pady=3)
            tk.Label(row, text=tr(label).upper(),
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8),
                  width=26, anchor="w").pack(side="left")
            lbl = tk.Label(
                row,
                text=getattr(state, field, "—").upper(),
                bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
                font=("Segoe UI", 8, "bold"),
                padx=8, pady=2
            )
            lbl.pack(side="left")
            self._hotkey_labels[field] = lbl

        divider(body, pady=(16, 10))

        reset_row = tk.Frame(body, bg=T("SURFACE"))
        reset_row.pack(fill="x", pady=(0, 8))
        tk.Label(reset_row,
                  text=tr("Reset all hotkeys to their factory defaults"),
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 9)).pack(side="left", padx=(0, 16))
        make_btn(reset_row, tr("RESET HOTKEYS"),
                  self._reset_hotkeys, danger=True).pack(side="left")

        self._reset_status = tk.Label(
            body, text="",
            bg=T("SURFACE"), fg=T("FG2"),
            font=("Segoe UI", 8))
        self._reset_status.pack(anchor="w", pady=(4, 0))

        divider(body, pady=(20, 10))

        # ── Auto-Close Timer ───────────────────────────────────
        section_title(body, tr("AUTO-CLOSE TIMER"), bg=T("SURFACE"))

        tk.Label(body,
                  text=tr("Set a duration and press START TIMER to close the app automatically."),
                  bg=T("SURFACE"), fg=T("FG3"),
                  font=("Segoe UI", 8),
                  wraplength=300, justify="left").pack(anchor="w", pady=(0, 12))

        dur_row = tk.Frame(body, bg=T("SURFACE"))
        dur_row.pack(anchor="w", pady=(0, 10))

        tk.Label(dur_row, text=tr("CLOSE AFTER"),
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(side="left", padx=(0, 8))

        self._ac_val_entry = tk.Entry(
            dur_row, width=7,
            bg=T("ENTRY_BG"), fg=T("FG"),
            relief="solid", bd=1,
            highlightthickness=1, highlightbackground=T("BORDER"),
            highlightcolor=T("BORDER_STRONG"),
            font=("Segoe UI", 10, "bold"), justify="center",
            insertbackground=T("FG")
        )
        self._ac_val_entry.insert(0, "60")
        self._ac_val_entry.pack(side="left", padx=(0, 6))
        self._ac_val_entry.bind("<FocusIn>",
            lambda e: self._ac_val_entry.config(highlightthickness=2))
        self._ac_val_entry.bind("<FocusOut>",
            lambda e: self._ac_val_entry.config(highlightthickness=1))

        # Uses _ttk imported earlier for language dropdown
        self._ac_unit_var = tk.StringVar(value=tr("minutes"))
        ac_unit_cb = _ttk.Combobox(
            dur_row, textvariable=self._ac_unit_var,
            values=[tr("seconds"), tr("minutes"), tr("hours")],
            state="readonly", width=8,
            font=("Segoe UI", 9)
        )
        ac_unit_cb.pack(side="left")

        ac_btn_row = tk.Frame(body, bg=T("SURFACE"))
        ac_btn_row.pack(anchor="w", fill="x", pady=(0, 4))

        make_btn(ac_btn_row, tr("▶  START TIMER"),
                 self._ac_start, primary=True).pack(side="left", padx=(0, 8))
        make_btn(ac_btn_row, tr("✕  CANCEL"),
                 self._ac_cancel).pack(side="left", padx=(0, 12))

        # Inline countdown — updates next to the buttons
        self._ac_countdown_lbl = tk.Label(
            ac_btn_row, text="",
            bg=T("SURFACE"), fg=T("FG"),
            font=("Segoe UI", 12, "bold"))
        self._ac_countdown_lbl.pack(side="left")

        self._ac_status = tk.Label(
            body, text="",
            bg=T("SURFACE"), fg=T("FG3"),
            font=("Segoe UI", 8))
        self._ac_status.pack(anchor="w", pady=(2, 0))

        # Internal timer state
        self._ac_remaining = 0
        self._ac_tick_job  = None

        divider(body, pady=(20, 10))

        # ── Reset All ─────────────────────────────────────
        section_title(body, tr("RESET"), bg=T("SURFACE"))

        reset_all_row = tk.Frame(body, bg=T("SURFACE"))
        reset_all_row.pack(fill="x", pady=(0, 8))

        reset_all_info = tk.Frame(reset_all_row, bg=T("SURFACE"))
        reset_all_info.pack(side="left", fill="x", expand=True)
        tk.Label(reset_all_info,
                  text=tr("RESET ALL SETTINGS"),
                  bg=T("SURFACE"), fg=T("FG"),
                  font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(reset_all_info,
                  text=tr("Clear steps, hotkeys and session data. Saved profiles are kept."),
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8),
                  wraplength=300, justify="left").pack(anchor="w", pady=(2, 0))

        make_btn(reset_all_row, tr("RESET ALL"),
                  self._reset_all, danger=True).pack(side="right", anchor="n")

        self._reset_all_status = tk.Label(
            body, text="",
            bg=T("SURFACE"), fg=T("FG2"),
            font=("Segoe UI", 8))
        self._reset_all_status.pack(anchor="w", pady=(4, 16))

    def _make_sb_handler(self, canvas, sb):
        def handler(first, last):
            sb.set(first, last)
            self._update_sb_visibility(canvas, sb)
        return handler

    def _update_sb_visibility(self, canvas, sb):
        try:
            region = canvas.bbox("all")
            if not region:
                sb.pack_forget()
                return
            if region[3] - region[1] > canvas.winfo_height():
                if not sb.winfo_ismapped():
                    sb.pack(side="right", fill="y", before=canvas)
            else:
                sb.pack_forget()
                canvas.yview_moveto(0)
        except Exception:
            pass

    def _make_toggle(self, parent, var, title, desc):
        row = tk.Frame(parent, bg=T("SURFACE"))
        row.pack(fill="x", pady=6)
        text_col = tk.Frame(row, bg=T("SURFACE"))
        text_col.pack(side="left", fill="x", expand=True)
        tk.Label(text_col, text=title,
                  bg=T("SURFACE"), fg=T("FG"),
                  font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(text_col, text=desc,
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8),
                  wraplength=300, justify="left").pack(anchor="w")
        tk.Checkbutton(
            row, variable=var,
            command=self._on_change,
            bg=T("SURFACE"), fg=T("FG"),
            selectcolor=T("CHECK_BG"),
            activebackground=T("SURFACE"),
            activeforeground=T("FG"),
            relief="flat", bd=0
        ).pack(side="right")

    def _ac_start(self):
        """Start auto-close countdown."""
        try:
            val = float(self._ac_val_entry.get())
        except ValueError:
            self._ac_status.config(text=tr("Enter a valid number."))
            return
        unit_text = self._ac_unit_var.get()
        # the unit variable is now translated, so map by checking the translated words
        unit = "seconds"
        if unit_text == tr("minutes"): unit = "minutes"
        elif unit_text == tr("hours"): unit = "hours"

        mult = {"seconds": 1, "minutes": 60, "hours": 3600}.get(unit, 60)
        total_secs = max(1, int(val * mult))
        # Cancel FIRST (resets tick job only, not remaining), then set remaining
        if self._ac_tick_job:
            try:
                self.box.after_cancel(self._ac_tick_job)
            except Exception:
                pass
            self._ac_tick_job = None
        self._ac_remaining = total_secs
        self._ac_tick()

    def _ac_tick(self):
        """Update countdown label every second."""
        if self._ac_remaining <= 0:
            self._ac_countdown_lbl.config(text="")
            self._ac_status.config(text="")
            try:
                self.box.winfo_toplevel().destroy()
            except Exception:
                pass
            return
        h  = self._ac_remaining // 3600
        m  = (self._ac_remaining % 3600) // 60
        s  = self._ac_remaining % 60
        if h:
            disp = f"{tr('Closing in  ')}{h:02d}:{m:02d}:{s:02d}"
        elif m:
            disp = f"{tr('Closing in  ')}{m:02d}:{s:02d}"
        else:
            disp = f"{tr('Closing in  ')}{s}{tr('s')}"
        self._ac_countdown_lbl.config(text=disp)
        self._ac_status.config(text=tr("Timer active — close app when countdown reaches 0."), fg=T("FG3"))
        self._ac_remaining -= 1
        self._ac_tick_job = self.box.after(1000, self._ac_tick)

    def _ac_cancel(self):
        """Cancel auto-close timer."""
        if self._ac_tick_job:
            try:
                self.box.after_cancel(self._ac_tick_job)
            except Exception:
                pass
            self._ac_tick_job = None
        self._ac_remaining = 0
        try:
            self._ac_countdown_lbl.config(text="")
        except Exception:
            pass
        self._ac_status.config(text="")

    def _on_change(self):
        self.settings["show_indicator"]   = self.indicator_var.get()
        self.settings["show_scan_border"] = self.border_var.get()
        self.settings["humanize"]         = self.humanize_var.get()
        state.humanize                    = self.humanize_var.get()
        if self.settings.get("on_change"):
            self.settings["on_change"]()

    def _reset_hotkeys(self):
        for field, default in _DEFAULT_HOTKEYS.items():
            setattr(state, field, default)
            if field in self._hotkey_labels:
                self._hotkey_labels[field].config(
                    text=default.upper(),
                    bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"))
        # Notify all panels via callback so their hotkey displays update
        cb = self.settings.get("on_reset_hotkeys")
        if cb:
            cb()
        self._reset_status.config(text=tr("ALL HOTKEYS RESET TO DEFAULTS."))
        self.box.after(3000, lambda: self._reset_status.config(text=""))

    def _reset_all(self):
        """Reset all settings. Profiles are kept."""
        import tkinter.messagebox as mb
        ok = mb.askyesno(
            tr("Reset All Settings"),
            tr("All steps, hotkeys and session data will be cleared.\nSaved profiles will NOT be deleted.\n\nContinue?"),
            icon="warning"
        )
        if not ok:
            return

        from core import state as _state
        _state.steps.clear()

        for field, default in _DEFAULT_HOTKEYS.items():
            setattr(_state, field, default)
            if field in self._hotkey_labels:
                self._hotkey_labels[field].config(
                    text=default.upper(),
                    bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"))

        _state.running          = False
        _state.macro_recording  = False
        _state.color_scanning   = False
        _state.image_scanning   = False
        _state.kb_running       = False
        _state.kb_key_running   = False
        _state.kb_combo_running = False
        _state.mouse_running    = False
        _state.action_count     = 0
        _state.click_count      = 0

        from ui.theme import set_dark, apply_styles
        set_dark(False)

        try:
            from utils.autosave import clear_session
            clear_session()
        except Exception:
            pass

        self._reset_all_status.config(text=tr("SETTINGS RESET. Restarting..."))

        import sys, subprocess
        try:
            python = sys.executable
            script = sys.argv[0]
            self.box.after(600, lambda: (
                subprocess.Popen([python, script]),
                self.box.winfo_toplevel().destroy()
            ))
        except Exception as e:
            self._reset_all_status.config(text=tr("RESTART FAILED: ") + str(e))
