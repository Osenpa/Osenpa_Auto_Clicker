import tkinter as tk
import threading
import time
import pyautogui
from ui.theme import make_entry, make_btn, section_title, divider, T
from ui.interval_widget import make_interval_widget
from core import state
from utils.i18n import tr


class MousePanel:
    def __init__(self, parent, on_add_step, on_pick_target):
        self.on_add_step         = on_add_step
        self.on_pick_target      = on_pick_target
        self._running            = False
        self._toast_after        = None
        self._on_show_indicator  = None
        self._on_hide_indicator  = None
        self._on_minimize        = None
        self.box = tk.Frame(parent, bg=T("SURFACE"))
        self.box.pack(fill="both", expand=True)
        self._build()

    def set_indicator_callbacks(self, on_show, on_hide, on_minimize=None):
        self._on_show_indicator = on_show
        self._on_hide_indicator = on_hide
        self._on_minimize       = on_minimize
        # on_update_count: OverlayIndicator.update_count bağlanacak
        self._on_update_count   = None

    def _update_count(self, count):
        if self._on_update_count:
            self._on_update_count(count)

    def _build(self):
        box = self.box

        title_bar = tk.Frame(box, bg=T("SURFACE"))
        title_bar.pack(fill="x", padx=32, pady=(28, 6))
        tk.Label(title_bar, text=tr("MOUSE CONFIGURATION"),
                  bg=T("SURFACE"), fg=T("FG"),
                  font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(title_bar,
                  text=tr("Simulate mouse clicks at specific or current coordinates"),
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 0))

        # Hotkey badge
        hk_row = tk.Frame(box, bg=T("SURFACE"))
        hk_row.pack(fill="x", padx=32, pady=(6, 0))
        tk.Label(hk_row, text=tr("PANEL HOTKEY"),
                  bg=T("SURFACE"), fg=T("FG3"),
                  font=("Segoe UI", 7, "bold")).pack(
            side="left", padx=(0, 8))
        self.hotkey_lbl = tk.Label(
            hk_row, text=state.mouse_hotkey.upper(),
            bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
            font=("Segoe UI", 8, "bold"), padx=8, pady=2)
        self.hotkey_lbl.pack(side="left", padx=(0, 8))
        make_btn(hk_row, tr("CHANGE"),
                  self._change_hotkey, small=True).pack(side="left")

        divider(box, padx=32, pady=(14, 0))

        body = tk.Frame(box, bg=T("SURFACE"))
        body.pack(fill="x", padx=32, pady=(20, 0))

        # ── Konum modu ──────────────────────────────────────
        section_title(body, tr("POSITION MODE"), bg=T("SURFACE"))

        self.use_cursor_var = tk.BooleanVar(value=False)
        mode_row = tk.Frame(body, bg=T("SURFACE"))
        mode_row.pack(fill="x", pady=(0, 16))

        for val, lbl in [(False, tr("FIXED COORDINATES")),
                          (True, tr("CURRENT CURSOR POSITION"))]:
            tk.Radiobutton(
                mode_row, text=lbl,
                variable=self.use_cursor_var, value=val,
                bg=T("SURFACE"), fg=T("FG"),
                selectcolor=T("CHECK_BG"),
                activebackground=T("SURFACE"),
                activeforeground=T("FG"),
                font=("Segoe UI", 9),
                command=self._toggle_mode
            ).pack(side="left", padx=(0, 20))

        # ── Koordinatlar ────────────────────────────────────
        self.coord_frame = tk.Frame(body, bg=T("SURFACE"))
        self.coord_frame.pack(fill="x")

        section_title(self.coord_frame, tr("COORDINATES"),
                       bg=T("SURFACE"))
        coord_row = tk.Frame(self.coord_frame, bg=T("SURFACE"))
        coord_row.pack(fill="x", pady=(0, 16))

        cx = tk.Frame(coord_row, bg=T("SURFACE"))
        cx.pack(side="left", padx=(0, 20))
        tk.Label(cx, text=tr("X"), bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 5))
        self.x_entry = make_entry(cx, width=8, default="500",
                                   center=True)
        self.x_entry.pack(anchor="w")

        cy_ = tk.Frame(coord_row, bg=T("SURFACE"))
        cy_.pack(side="left", padx=(0, 20))
        tk.Label(cy_, text=tr("Y"), bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 5))
        self.y_entry = make_entry(cy_, width=8, default="300",
                                   center=True)
        self.y_entry.pack(anchor="w")

        pick_col = tk.Frame(coord_row, bg=T("SURFACE"))
        pick_col.pack(side="left", anchor="s", pady=(0, 2))
        self.pick_btn = make_btn(pick_col, tr("PICK TARGET"), self._pick)
        self.pick_btn.pack()

        divider(body, pady=(0, 16))

        # ── Ayarlar ─────────────────────────────────────────
        section_title(body, tr("CLICK SETTINGS"), bg=T("SURFACE"))

        settings_row = tk.Frame(body, bg=T("SURFACE"))
        settings_row.pack(fill="x", pady=(0, 12))

        sr = tk.Frame(settings_row, bg=T("SURFACE"))
        sr.pack(side="left", padx=(0, 20))
        tk.Label(sr, text=tr("REPEAT"), bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 5))
        self.repeat_entry = make_entry(sr, width=6, default="1",
                                        center=True)
        self.repeat_entry.pack(anchor="w")

        sr2 = tk.Frame(settings_row, bg=T("SURFACE"))
        sr2.pack(side="left", padx=(0, 20))
        tk.Label(sr2, text=tr("INFINITE"), bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 5))
        self.infinite_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            sr2, variable=self.infinite_var,
            bg=T("SURFACE"), fg=T("FG"),
            activebackground=T("SURFACE"),
            activeforeground=T("FG"),
            selectcolor=T("CHECK_BG"), relief="flat",
            command=self._toggle_infinite
        ).pack(anchor="w")

        si = tk.Frame(settings_row, bg=T("SURFACE"))
        si.pack(side="left")
        tk.Label(si, text=tr("INTERVAL"), bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 2))
        tk.Label(si, text=tr("Wait between each click"),
                  bg=T("SURFACE"), fg=T("FG3"),
                  font=("Segoe UI", 7)).pack(anchor="w", pady=(0, 3))
        self.interval_widget = make_interval_widget(si, bg=T("SURFACE"))
        self.interval_widget.pack(anchor="w")

        divider(body, pady=(4, 12))

        section_title(body, tr("BUTTON"), bg=T("SURFACE"))
        btn_type_row = tk.Frame(body, bg=T("SURFACE"))
        btn_type_row.pack(anchor="w", pady=(0, 16))
        self.click_var = tk.StringVar(value="left")
        for val, lbl in [("left", tr("LEFT")),
                          ("right", tr("RIGHT")),
                          ("middle", tr("MIDDLE"))]:
            tk.Radiobutton(
                btn_type_row, text=lbl,
                variable=self.click_var, value=val,
                bg=T("SURFACE"), fg=T("FG"),
                selectcolor=T("CHECK_BG"),
                activebackground=T("SURFACE"),
                activeforeground=T("FG"),
                font=("Segoe UI", 9)
            ).pack(side="left", padx=(0, 16))

        divider(body, pady=(0, 16))

        action_row = tk.Frame(body, bg=T("SURFACE"))
        action_row.pack(fill="x", pady=(0, 8))

        self.start_btn = make_btn(
            action_row, tr("START"), self._start, primary=True)
        self.start_btn.pack(side="left", padx=(0, 8))

        self.stop_btn = make_btn(action_row, tr("STOP"), self._stop)
        self.stop_btn.config(state="disabled")
        self.stop_btn.pack(side="left", padx=(0, 8))

        make_btn(action_row, tr("ADD TO STEPS"),
                  self._add).pack(side="left")

        self.status_lbl = tk.Label(
            body, text="",
            bg=T("SURFACE"), fg=T("FG2"),
            font=("Segoe UI", 9))
        self.status_lbl.pack(anchor="w", pady=(10, 0))

        self._toast = tk.Label(
            box, text="",
            bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
            font=("Segoe UI", 9, "bold"),
            padx=16, pady=10
        )

    def _toggle_mode(self):
        use = self.use_cursor_var.get()
        s   = "disabled" if use else "normal"
        for w in [self.x_entry, self.y_entry, self.pick_btn]:
            w.config(state=s)

    def _toggle_infinite(self):
        self.repeat_entry.config(
            state="disabled" if self.infinite_var.get() else "normal")

    def _pick(self):
        self.on_pick_target(self.x_entry, self.y_entry)

    def _get_params(self):
        use_cursor = self.use_cursor_var.get()
        if use_cursor:
            x, y = 0, 0
        else:
            try:
                x = int(self.x_entry.get())
                y = int(self.y_entry.get())
            except Exception:
                return None
        infinite = self.infinite_var.get()
        try:
            repeat   = 0 if infinite else int(self.repeat_entry.get())
            interval = self.interval_widget.get_seconds()
        except Exception:
            return None
        return (x, y, repeat, interval,
                self.click_var.get(), use_cursor, infinite)

    def _start(self):
        # Başka aktif görev kontrolü
        if getattr(self, "_on_busy_check", None) and self._on_busy_check():
            self.status_lbl.config(text=tr("STOP THE ACTIVE TASK FIRST."))
            return
        params = self._get_params()
        if params is None:
            self.status_lbl.config(text=tr("INVALID VALUES."))
            return
        x, y, repeat, interval, button, use_cursor, infinite = params
        self._running       = True
        state.mouse_running = True
        state.action_count  = 0   # reset per-session counter
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        pos_str = tr("CURSOR") if use_cursor else f"({x},{y})"
        self.status_lbl.config(text=tr("RUNNING..."))

        if self._on_show_indicator:
            self._on_show_indicator(
                f"{tr('MOUSE ACTIVE')}\n{pos_str} {tr(button.upper())}",
                hotkey=state.mouse_hotkey, count=0)
        if self._on_minimize:
            self._on_minimize()

        def loop():
            count = 0  # increment_action() döndürdüğü global değeri tutar
            done  = 0
            while self._running and (infinite or done < repeat):
                cx, cy = pyautogui.position() if use_cursor else (x, y)
                pyautogui.click(cx, cy, button=button)
                count = state.increment_action()
                done  += 1
                self.box.after(0, lambda c=count:
                    self.status_lbl.config(
                        text=f"{tr('RUNNING  —  ACTIONS:')} {c}"))
                self.box.after(0, lambda c=count: self._update_count(c))
                _isleep(interval, self)
            self.box.after(0, self._on_done, count)

        threading.Thread(target=loop, daemon=True).start()

    def _stop(self):
        self._running       = False
        state.mouse_running = False

    def _on_done(self, count):
        self._running       = False
        state.mouse_running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_lbl.config(text=f"{tr('DONE.  TOTAL:')} {count}")
        if self._on_hide_indicator:
            self._on_hide_indicator()

    def _add(self):
        params = self._get_params()
        if params is None:
            self._show_toast(tr("INVALID VALUES."))
            return
        x, y, repeat, interval, button, use_cursor, infinite = params
        if infinite:
            self._show_toast(tr("Infinite mode not supported in steps. Set a repeat count."))
            return
        self.on_add_step({
            "type": "click",
            "x": x, "y": y,
            "button": button,
            "interval": interval,
            "repeat": repeat,
            "use_cursor": use_cursor
        })
        pos = tr("CURSOR") if use_cursor else f"({x},{y})"
        self._show_toast(f"{tr('STEP ADDED:')} {pos} {tr(button.upper())}")

    def _show_toast(self, msg):
        if self._toast_after:
            self.box.after_cancel(self._toast_after)
        self._toast.config(text=msg)
        self._toast.place(relx=1.0, rely=1.0,
                           anchor="se", x=-16, y=-16)
        self._toast_after = self.box.after(3000, self._hide_toast)

    def _hide_toast(self):
        self._toast.place_forget()
        self._toast_after = None

    def _change_hotkey(self):
        state.changing_mouse_hotkey = True
        self.hotkey_lbl.config(
            text=tr("PRESS ANY KEY..."),
            bg=T("SURFACE2"), fg=T("FG2"))

    def update_hotkey_display(self, key_name):
        self.hotkey_lbl.config(
            text=key_name.upper(),
            bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"))

    def set_state(self, s):
        for w in [self.x_entry, self.y_entry,
                  self.repeat_entry, self.pick_btn]:
            try:
                w.config(state=s)
            except Exception:
                pass
        self.interval_widget.set_state(s)

    def refresh_labels(self):
        pass

    # ── Profile support ─────────────────────────────────────────

    def get_profile_data(self) -> dict:
        """Mevcut panel ayarlarını sözlük olarak döndürür."""
        return {
            "use_cursor":    self.use_cursor_var.get(),
            "x":             self.x_entry.get(),
            "y":             self.y_entry.get(),
            "repeat":        self.repeat_entry.get(),
            "infinite":      self.infinite_var.get(),
            "interval_val":  self.interval_widget.winfo_children()[0].get()
                             if self.interval_widget.winfo_children() else "100",
            "interval_unit": self.interval_widget.winfo_children()[1].get()
                             if len(self.interval_widget.winfo_children()) > 1 else "MS",
            "button":        self.click_var.get(),
        }

    def load_profile_data(self, d: dict):
        """Sözlükten panel ayarlarını geri yükler."""
        if not d:
            return
        try:
            self.use_cursor_var.set(d.get("use_cursor", False))
            self._toggle_mode()
            self.x_entry.delete(0, "end")
            self.x_entry.insert(0, str(d.get("x", "500")))
            self.y_entry.delete(0, "end")
            self.y_entry.insert(0, str(d.get("y", "300")))
            self.repeat_entry.delete(0, "end")
            self.repeat_entry.insert(0, str(d.get("repeat", "1")))
            self.infinite_var.set(d.get("infinite", False))
            self._toggle_infinite()
            children = self.interval_widget.winfo_children()
            if children:
                children[0].delete(0, "end")
                children[0].insert(0, str(d.get("interval_val", "100")))
            if len(children) > 1:
                children[1].set(d.get("interval_unit", "MS"))
            self.click_var.set(d.get("button", "left"))
        except Exception as e:
            print(f"[MousePanel] load_profile_data error: {e}")


def _isleep(seconds, panel):
    end = time.time() + seconds
    while panel._running and time.time() < end:
        time.sleep(min(0.05, end - time.time()))