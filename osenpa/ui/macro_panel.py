import tkinter as tk
import time
from ui.theme import make_btn, section_title, divider, T
from core import state
from utils.i18n import tr


class MacroPanel:
    def __init__(self, parent, on_start_recording,
                 on_stop_recording, on_change_hotkey):
        self.on_start_recording = on_start_recording
        self.on_stop_recording  = on_stop_recording
        self.on_change_hotkey   = on_change_hotkey
        self.is_recording       = False
        self._timer_start       = None
        self._timer_job         = None
        self.box = tk.Frame(parent, bg=T("SURFACE"))
        self.box.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        box = self.box

        title_bar = tk.Frame(box, bg=T("SURFACE"))
        title_bar.pack(fill="x", padx=32, pady=(32, 8))
        tk.Label(title_bar, text=tr("Record Actions"),
                  bg=T("SURFACE"), fg=T("FG"),
                  font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(title_bar,
                  text=tr("Record keyboard and mouse actions as steps"),
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))

        divider(box, padx=32, pady=(20, 0))

        body = tk.Frame(box, bg=T("SURFACE"))
        body.pack(fill="x", padx=32, pady=(24, 0))

        section_title(body, tr("RECORD HOTKEY"), bg=T("SURFACE"))

        hk_row = tk.Frame(body, bg=T("SURFACE"))
        hk_row.pack(fill="x", pady=(0, 0))
        self.hotkey_display = tk.Label(
            hk_row, text=state.macro_hotkey.upper(),
            bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
            font=("Segoe UI", 11, "bold"),
            padx=16, pady=8
        )
        self.hotkey_display.pack(side="left", padx=(0, 12))
        self.change_btn = make_btn(
            hk_row, tr("CHANGE HOTKEY"), self.on_change_hotkey)
        self.change_btn.pack(side="left")

        divider(body, pady=24)

        section_title(body, tr("RECORDING"), bg=T("SURFACE"))

        self.record_btn = make_btn(
            body, tr("START RECORDING"), self._toggle, primary=True)
        self.record_btn.config(font=("Segoe UI", 11, "bold"),
                                padx=28, pady=12)
        self.record_btn.pack(anchor="w")

        self.timer_lbl = tk.Label(
            body, text="",
            bg=T("SURFACE"), fg=T("FG"),
            font=("Segoe UI", 28, "bold")
        )
        self.timer_lbl.pack(anchor="w", pady=(20, 0))

        self.status_lbl = tk.Label(
            body,
            text=tr("Press the button or use the hotkey to start."),
            bg=T("SURFACE"), fg=T("FG2"),
            font=("Segoe UI", 10),
            wraplength=400, justify="left"
        )
        self.status_lbl.pack(anchor="w", pady=(8, 0))

    def _toggle(self):
        if not self.is_recording:
            self._start()
        else:
            self._stop()

    def _start(self):
        self.is_recording = True
        self._timer_start = time.time()
        self.record_btn.config(text=tr("STOP RECORDING"))
        self.status_lbl.config(
            text=tr("Recording... Press button or hotkey to stop."))
        self._tick()
        self.on_start_recording()

    def _tick(self):
        if not self.is_recording:
            return
        elapsed = time.time() - self._timer_start
        m  = int(elapsed // 60)
        s  = int(elapsed  % 60)
        cs = int((elapsed % 1) * 100)
        self.timer_lbl.config(text=f"{m:02d}:{s:02d}.{cs:02d}")
        self._timer_job = self.box.after(50, self._tick)

    def _stop(self):
        self.is_recording = False
        if self._timer_job:
            self.box.after_cancel(self._timer_job)
            self._timer_job = None
        self.record_btn.config(text=tr("START RECORDING"))
        self.status_lbl.config(
            text=tr("Press the button or use the hotkey to start.")
        )
        self.on_stop_recording()

    def set_recording(self, is_rec):
        if is_rec and not self.is_recording:
            self._start()
        elif not is_rec and self.is_recording:
            self.is_recording = False
            if self._timer_job:
                self.box.after_cancel(self._timer_job)
                self._timer_job = None
            self.record_btn.config(text=tr("START RECORDING"))
            self.status_lbl.config(
                text=tr("Press the button or use the hotkey to start.")
        )

    def update_hotkey_display(self, key_name):
        self.hotkey_display.config(text=key_name.upper())

    def set_state(self, s):
        for w in [self.record_btn, self.change_btn]:
            try:
                w.config(state=s)
            except:
                pass

    def refresh_labels(self):
        pass