import tkinter as tk
import threading
import time
import pyautogui
from pynput.keyboard import Controller as KbController, KeyCode
from ui.theme import (make_entry, make_btn, make_capture_entry,
                       section_title, divider, T)
from ui.interval_widget import make_interval_widget
from core import state
from utils.i18n import tr

_kb_controller = KbController()

def _press_key(key):
    """Her karakteri pynput ile doğrudan bas — Türkçe dahil."""
    if len(key) == 1:
        try:
            _kb_controller.press(KeyCode.from_char(key))
            _kb_controller.release(KeyCode.from_char(key))
            return
        except Exception:
            pass
    try:
        pyautogui.press(key)
    except Exception:
        pass


class KeyboardPanel:
    def __init__(self, parent, on_add_step):
        self.on_add_step    = on_add_step
        self._running_key   = False
        self._running_combo = False
        self._on_show_indicator = None
        self._on_hide_indicator = None
        self._on_update_count   = None
        self._on_minimize       = None
        self.box = tk.Frame(parent, bg=T("SURFACE"))
        self.box.pack(fill="both", expand=True)
        self._build()

    def set_indicator_callbacks(self, on_show, on_hide, on_update_count=None, on_minimize=None):
        self._on_show_indicator  = on_show
        self._on_hide_indicator  = on_hide
        self._on_update_count    = on_update_count
        self._on_minimize        = on_minimize

    def _update_overlay_count(self, count):
        if self._on_update_count:
            self._on_update_count(count)

    def _build(self):
        box = self.box

        title_bar = tk.Frame(box, bg=T("SURFACE"))
        title_bar.pack(fill="x", padx=32, pady=(28, 6))
        tk.Label(title_bar, text=tr("KEYBOARD CONFIGURATION"),
                  bg=T("SURFACE"), fg=T("FG"),
                  font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(title_bar,
                  text=tr("Send keystrokes and hotkey combinations"),
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 0))

        # Hotkey badge — seksiyon bazlı badge'ler aşağıda tanımlı
        # Hotkey badge — tek panel hotkey'i kaldır, aşağıda seksiyon bazlı ekle

        # Hotkey badge — tek panel hotkey'i kaldır, aşağıda seksiyon bazlı ekle
        divider(box, padx=32, pady=(14, 0))

        # ── Single Key ──────────────────────────────────────
        sec1 = tk.Frame(box, bg=T("SURFACE"))
        sec1.pack(fill="x", padx=32, pady=(20, 0))

        section_title(sec1, tr("SINGLE KEY"), bg=T("SURFACE"))

        # Single Key hotkey badge
        sk_hk_row = tk.Frame(sec1, bg=T("SURFACE"))
        sk_hk_row.pack(fill="x", pady=(0, 10))
        tk.Label(sk_hk_row, text=tr("HOTKEY"),
                  bg=T("SURFACE"), fg=T("FG3"),
                  font=("Segoe UI", 7, "bold")).pack(side="left", padx=(0, 8))
        self.key_hotkey_lbl = tk.Label(
            sk_hk_row, text=state.kb_key_hotkey.upper(),
            bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
            font=("Segoe UI", 8, "bold"), padx=8, pady=2)
        self.key_hotkey_lbl.pack(side="left", padx=(0, 8))
        make_btn(sk_hk_row, tr("CHANGE"),
                  self._change_key_hotkey, small=True).pack(side="left")

        row1 = tk.Frame(sec1, bg=T("SURFACE"))
        row1.pack(fill="x", pady=(0, 12))

        c1 = tk.Frame(row1, bg=T("SURFACE"))
        c1.pack(side="left", padx=(0, 20))
        tk.Label(c1, text=tr("KEY"), bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 5))
        self.key_capture = make_capture_entry(c1, width=22)
        self.key_capture.pack(anchor="w")

        c2 = tk.Frame(row1, bg=T("SURFACE"))
        c2.pack(side="left", padx=(0, 20))
        tk.Label(c2, text=tr("REPEAT"), bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 5))
        self.key_repeat = make_entry(c2, width=6, default="1",
                                      center=True)
        self.key_repeat.pack(anchor="w")

        # Infinite checkbox
        c2b = tk.Frame(row1, bg=T("SURFACE"))
        c2b.pack(side="left", padx=(0, 20))
        tk.Label(c2b, text=tr("INFINITE"), bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 5))
        self.key_infinite_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            c2b, variable=self.key_infinite_var,
            bg=T("SURFACE"), fg=T("FG"),
            activebackground=T("SURFACE"),
            activeforeground=T("FG"),
            selectcolor=T("CHECK_BG"), relief="flat",
            command=self._toggle_key_infinite
        ).pack(anchor="w")

        c3 = tk.Frame(row1, bg=T("SURFACE"))
        c3.pack(side="left")
        tk.Label(c3, text=tr("INTERVAL"), bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 2))
        tk.Label(c3, text=tr("Wait between each keypress"),
                  bg=T("SURFACE"), fg=T("FG3"),
                  font=("Segoe UI", 7)).pack(anchor="w", pady=(0, 3))
        self.key_interval = make_interval_widget(c3, bg=T("SURFACE"))
        self.key_interval.pack(anchor="w")

        btn_row1 = tk.Frame(sec1, bg=T("SURFACE"))
        btn_row1.pack(fill="x", pady=(0, 4))
        self.key_start_btn = make_btn(
            btn_row1, tr("START"), self._start_key, primary=True)
        self.key_start_btn.pack(side="left", padx=(0, 8))
        self.key_stop_btn = make_btn(
            btn_row1, tr("STOP"), self._stop_key)
        self.key_stop_btn.config(state="disabled")
        self.key_stop_btn.pack(side="left", padx=(0, 8))
        make_btn(btn_row1, tr("ADD TO STEPS"),
                  self._add_key).pack(side="left")

        self.key_status = tk.Label(
            sec1, text="", bg=T("SURFACE"), fg=T("FG2"),
            font=("Segoe UI", 8))
        self.key_status.pack(anchor="w", pady=(5, 0))

        divider(box, padx=32, pady=(20, 0))

        # ── Hotkey Combination ──────────────────────────────
        sec2 = tk.Frame(box, bg=T("SURFACE"))
        sec2.pack(fill="x", padx=32, pady=(20, 0))

        section_title(sec2, tr("HOTKEY COMBINATION"), bg=T("SURFACE"))

        # Combo hotkey badge
        cb_hk_row = tk.Frame(sec2, bg=T("SURFACE"))
        cb_hk_row.pack(fill="x", pady=(0, 10))
        tk.Label(cb_hk_row, text=tr("HOTKEY"),
                  bg=T("SURFACE"), fg=T("FG3"),
                  font=("Segoe UI", 7, "bold")).pack(side="left", padx=(0, 8))
        self.combo_hotkey_lbl = tk.Label(
            cb_hk_row, text=state.kb_combo_hotkey.upper(),
            bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
            font=("Segoe UI", 8, "bold"), padx=8, pady=2)
        self.combo_hotkey_lbl.pack(side="left", padx=(0, 8))
        make_btn(cb_hk_row, tr("CHANGE"),
                  self._change_combo_hotkey, small=True).pack(side="left")

        tk.Label(sec2,
                  text=tr("FORMAT: ctrl+z  /  ctrl+shift+s  /  alt+f4"),
                  bg=T("SURFACE"), fg=T("FG3"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 10))

        row2 = tk.Frame(sec2, bg=T("SURFACE"))
        row2.pack(fill="x", pady=(0, 12))

        d1 = tk.Frame(row2, bg=T("SURFACE"))
        d1.pack(side="left", padx=(0, 20))
        tk.Label(d1, text=tr("KEYS"), bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 5))
        self.combo_entry = make_entry(d1, width=16)
        self.combo_entry.pack(anchor="w")
        # Placeholder
        self.combo_entry.insert(0, tr("e.g. ctrl+z"))
        self.combo_entry.config(fg=T("FG3"))

        def _on_combo_fi(e):
            if self.combo_entry.get() == tr("e.g. ctrl+z"):
                self.combo_entry.delete(0, tk.END)
                self.combo_entry.config(fg=T("FG"))
        def _on_combo_fo(e):
            if self.combo_entry.get().strip() == "":
                self.combo_entry.insert(0, tr("e.g. ctrl+z"))
                self.combo_entry.config(fg=T("FG3"))
        self.combo_entry.bind("<FocusIn>",  _on_combo_fi)
        self.combo_entry.bind("<FocusOut>", _on_combo_fo)

        d2 = tk.Frame(row2, bg=T("SURFACE"))
        d2.pack(side="left", padx=(0, 20))
        tk.Label(d2, text=tr("REPEAT"), bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 5))
        self.combo_repeat = make_entry(d2, width=6, default="1",
                                        center=True)
        self.combo_repeat.pack(anchor="w")

        d2b = tk.Frame(row2, bg=T("SURFACE"))
        d2b.pack(side="left", padx=(0, 20))
        tk.Label(d2b, text=tr("INFINITE"), bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 5))
        self.combo_infinite_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            d2b, variable=self.combo_infinite_var,
            bg=T("SURFACE"), fg=T("FG"),
            activebackground=T("SURFACE"),
            activeforeground=T("FG"),
            selectcolor=T("CHECK_BG"), relief="flat",
            command=self._toggle_combo_infinite
        ).pack(anchor="w")

        d3 = tk.Frame(row2, bg=T("SURFACE"))
        d3.pack(side="left")
        tk.Label(d3, text=tr("INTERVAL"), bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 2))
        tk.Label(d3, text=tr("Wait between each combo press"),
                  bg=T("SURFACE"), fg=T("FG3"),
                  font=("Segoe UI", 7)).pack(anchor="w", pady=(0, 3))
        self.combo_interval = make_interval_widget(d3, bg=T("SURFACE"))
        self.combo_interval.pack(anchor="w")

        btn_row2 = tk.Frame(sec2, bg=T("SURFACE"))
        btn_row2.pack(fill="x", pady=(0, 4))
        self.combo_start_btn = make_btn(
            btn_row2, tr("START"), self._start_combo, primary=True)
        self.combo_start_btn.pack(side="left", padx=(0, 8))
        self.combo_stop_btn = make_btn(
            btn_row2, tr("STOP"), self._stop_combo)
        self.combo_stop_btn.config(state="disabled")
        self.combo_stop_btn.pack(side="left", padx=(0, 8))
        make_btn(btn_row2, tr("ADD TO STEPS"),
                  self._add_hotkey).pack(side="left")

        self.combo_status = tk.Label(
            sec2, text="", bg=T("SURFACE"), fg=T("FG2"),
            font=("Segoe UI", 8))
        self.combo_status.pack(anchor="w", pady=(5, 0))

    def _toggle_key_infinite(self):
        inf = self.key_infinite_var.get()
        self.key_repeat.config(
            state="disabled" if inf else "normal")

    def _toggle_combo_infinite(self):
        inf = self.combo_infinite_var.get()
        self.combo_repeat.config(
            state="disabled" if inf else "normal")

    # ── Bağımsız çalıştırma ─────────────────────────────────

    def start_independent(self):
        self._start_key()

    def start_combo_independent(self):
        self._start_combo()

    def stop_independent(self):
        self._stop_key()
        self._stop_combo()

    def _start_key(self):
        # Başka aktif görev kontrolü
        if getattr(self, "_on_busy_check", None) and self._on_busy_check():
            self.key_status.config(text=tr("STOP THE ACTIVE TASK FIRST."))
            return
        key = self.key_capture.get().strip()
        if not key or key == tr("PRESS ANY KEY..."):
            self.key_status.config(text=tr("NO KEY SPECIFIED."))
            return
        infinite = self.key_infinite_var.get()
        try:
            repeat   = 0 if infinite else int(self.key_repeat.get())
            interval = self.key_interval.get_seconds()
        except Exception:
            return
        state.reset_counts()
        self._running_key = True
        state.kb_running      = True
        state.kb_key_running  = True
        self.key_start_btn.config(state="disabled")
        self.key_stop_btn.config(state="normal")
        self.key_status.config(text=tr("RUNNING..."))
        if self._on_show_indicator:
            self._on_show_indicator(
                f"{tr('KEYBOARD ACTIVE')}\n{tr('KEY')}: {key.upper()}",
                hotkey=state.kb_key_hotkey, count=0)
        if self._on_minimize:
            self._on_minimize()

        def loop():
            count = 0  # increment_action() döndürdüğü global değeri tutar
            inf   = (repeat == 0)
            done  = 0
            while self._running_key and (inf or done < repeat):
                _press_key(key)
                count = state.increment_action()
                done  += 1
                self.box.after(0, lambda c=count:
                    self.key_status.config(
                        text=f"{tr('RUNNING  —  ACTIONS:')} {c}"))
                if self._on_show_indicator:
                    self.box.after(0, lambda c=count:
                        self._update_overlay_count(c))
                _isleep(interval, self, "_running_key")
            self.box.after(0, self._on_key_done, count)

        threading.Thread(target=loop, daemon=True).start()

    def _stop_key(self):
        self._running_key     = False
        state.kb_running      = False
        state.kb_key_running  = False
        if self._on_hide_indicator:
            self._on_hide_indicator()

    def _on_key_done(self, count):
        self._running_key     = False
        state.kb_running      = False
        state.kb_key_running  = False
        self.key_start_btn.config(state="normal")
        self.key_stop_btn.config(state="disabled")
        self.key_status.config(text=f"{tr('DONE.  TOTAL:')} {count}")
        if self._on_hide_indicator:
            self._on_hide_indicator()

    def _start_combo(self):
        # Başka aktif görev kontrolü
        if getattr(self, "_on_busy_check", None) and self._on_busy_check():
            self.combo_status.config(text=tr("STOP THE ACTIVE TASK FIRST."))
            return
        combo = self.combo_entry.get().strip()
        if not combo or combo == tr("e.g. ctrl+z"):
            self.combo_status.config(text=tr("NO KEYS SPECIFIED."))
            return
        infinite = self.combo_infinite_var.get()
        try:
            repeat   = 0 if infinite else int(self.combo_repeat.get())
            interval = self.combo_interval.get_seconds()
        except Exception:
            return
        state.reset_counts()
        self._running_combo  = True
        state.kb_running     = True
        state.kb_combo_running = True
        self.combo_start_btn.config(state="disabled")
        self.combo_stop_btn.config(state="normal")
        self.combo_status.config(text=tr("RUNNING..."))
        if self._on_show_indicator:
            self._on_show_indicator(
                f"{tr('KEYBOARD ACTIVE')}\n{tr('HOTKEY')}: {combo.upper()}",
                hotkey=state.kb_combo_hotkey, count=0)
        if self._on_minimize:
            self._on_minimize()

        def loop():
            count = 0  # increment_action() döndürdüğü global değeri tutar
            inf   = (repeat == 0)
            done  = 0
            while self._running_combo and (inf or done < repeat):
                pyautogui.hotkey(*combo.split("+"))
                count = state.increment_action()
                done  += 1
                self.box.after(0, lambda c=count:
                    self.combo_status.config(
                        text=f"{tr('RUNNING  —  ACTIONS:')} {c}"))
                if self._on_show_indicator:
                    self.box.after(0, lambda c=count:
                        self._update_overlay_count(c))
                _isleep(interval, self, "_running_combo")
            self.box.after(0, self._on_combo_done, count)

        threading.Thread(target=loop, daemon=True).start()

    def _stop_combo(self):
        self._running_combo    = False
        state.kb_running       = False
        state.kb_combo_running = False
        if self._on_hide_indicator:
            self._on_hide_indicator()

    def _on_combo_done(self, count):
        self._running_combo    = False
        state.kb_running       = False
        state.kb_combo_running = False
        self.combo_start_btn.config(state="normal")
        self.combo_stop_btn.config(state="disabled")
        self.combo_status.config(text=f"{tr('DONE.  TOTAL:')} {count}")
        if self._on_hide_indicator:
            self._on_hide_indicator()

    def _change_key_hotkey(self):
        state.changing_kb_key_hotkey = True
        self.key_hotkey_lbl.config(
            text=tr("PRESS ANY KEY..."),
            bg=T("SURFACE2"), fg=T("FG2"))

    def _change_combo_hotkey(self):
        state.changing_kb_combo_hotkey = True
        self.combo_hotkey_lbl.config(
            text=tr("PRESS ANY KEY..."),
            bg=T("SURFACE2"), fg=T("FG2"))

    def _change_hotkey(self):
        self._change_key_hotkey()

    def update_hotkey_display(self, key_name, target="key"):
        """target: 'key' veya 'combo'"""
        if target == "combo":
            self.combo_hotkey_lbl.config(
                text=key_name.upper(),
                bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"))
        else:
            self.key_hotkey_lbl.config(
                text=key_name.upper(),
                bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"))

    def _add_key(self):
        key = self.key_capture.get().strip()
        if not key or key == tr("PRESS ANY KEY..."):
            return
        infinite = self.key_infinite_var.get()
        if infinite:
            self.key_status.config(
                text=tr("Infinite mode is not supported in steps. Set a repeat count first."))
            return
        try:
            repeat = int(self.key_repeat.get())
        except Exception:
            return
        self.on_add_step({
            "type": "key", "key": key,
            "interval": self.key_interval.get_seconds(),
            "repeat": repeat
        })
        self.key_status.config(text=tr("STEP ADDED."))

    def _add_hotkey(self):
        combo = self.combo_entry.get().strip()
        if not combo or combo == tr("e.g. ctrl+z"):
            return
        infinite = self.combo_infinite_var.get()
        if infinite:
            self.combo_status.config(
                text=tr("Infinite mode is not supported in steps. Set a repeat count first."))
            return
        try:
            repeat = int(self.combo_repeat.get())
        except Exception:
            return
        self.on_add_step({
            "type": "hotkey", "keys": combo,
            "interval": self.combo_interval.get_seconds(),
            "repeat": repeat
        })
        self.combo_status.config(text=tr("STEP ADDED."))

    def set_state(self, s):
        for w in [self.key_capture, self.key_repeat,
                  self.combo_entry, self.combo_repeat]:
            try:
                w.config(state=s)
            except Exception:
                pass
        self.key_interval.set_state(s)
        self.combo_interval.set_state(s)

    def refresh_labels(self):
        pass

    # ── Profile support ─────────────────────────────────────────

    def _iw_vals(self, widget):
        """interval_widget içindeki entry+combobox değerlerini al."""
        ch = widget.winfo_children()
        val  = ch[0].get() if ch else "100"
        unit = ch[1].get() if len(ch) > 1 else "MS"
        return val, unit

    def _iw_load(self, widget, val, unit):
        """interval_widget'e değer yükle."""
        ch = widget.winfo_children()
        if ch:
            ch[0].delete(0, "end")
            ch[0].insert(0, str(val))
        if len(ch) > 1:
            ch[1].set(unit)

    def get_profile_data(self) -> dict:
        kiv, kiu = self._iw_vals(self.key_interval)
        civ, ciu = self._iw_vals(self.combo_interval)
        return {
            "key":               self.key_capture.get(),
            "key_repeat":        self.key_repeat.get(),
            "key_infinite":      self.key_infinite_var.get(),
            "key_interval_val":  kiv,
            "key_interval_unit": kiu,
            "combo":             self.combo_entry.get(),
            "combo_repeat":      self.combo_repeat.get(),
            "combo_infinite":    self.combo_infinite_var.get(),
            "combo_interval_val":  civ,
            "combo_interval_unit": ciu,
        }

    def load_profile_data(self, d: dict):
        if not d:
            return
        try:
            self.key_capture.config(state="normal")
            self.key_capture.delete(0, "end")
            self.key_capture.insert(0, d.get("key", ""))
            self.key_repeat.delete(0, "end")
            self.key_repeat.insert(0, str(d.get("key_repeat", "1")))
            self.key_infinite_var.set(d.get("key_infinite", False))
            self._toggle_key_infinite()
            self._iw_load(self.key_interval,
                          d.get("key_interval_val", "100"),
                          d.get("key_interval_unit", "MS"))
            combo_val = d.get("combo", "")
            self.combo_entry.delete(0, "end")
            if combo_val and combo_val != tr("e.g. ctrl+z"):
                self.combo_entry.insert(0, combo_val)
                self.combo_entry.config(fg=T("FG"))
            else:
                self.combo_entry.insert(0, tr("e.g. ctrl+z"))
                self.combo_entry.config(fg=T("FG3"))
            self.combo_repeat.delete(0, "end")
            self.combo_repeat.insert(0, str(d.get("combo_repeat", "1")))
            self.combo_infinite_var.set(d.get("combo_infinite", False))
            self._toggle_combo_infinite()
            self._iw_load(self.combo_interval,
                          d.get("combo_interval_val", "100"),
                          d.get("combo_interval_unit", "MS"))
        except Exception as e:
            print(f"[KeyboardPanel] load_profile_data error: {e}")


def _isleep(seconds, obj, attr):
    """İnterruptible sleep."""
    end = time.time() + seconds
    while getattr(obj, attr, False) and time.time() < end:
        time.sleep(min(0.05, end - time.time()))