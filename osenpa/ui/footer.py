import tkinter as tk
from tkinter import ttk
from ui.theme import make_entry, make_btn, T
from ui.interval_widget import make_interval_widget
from core import state
from utils.i18n import tr


class Footer:
    def __init__(self, parent, on_start, on_stop, on_change_hotkey):
        self.on_start          = on_start
        self.on_stop           = on_stop
        self.on_change_hotkey  = on_change_hotkey
        self._progress_val     = tk.DoubleVar(value=0)
        # Scheduler state
        self._scheduler_job    = None
        self._scheduler_active = False
        self._build(parent)

    def _build(self, parent):
        self._prog_bar = ttk.Progressbar(
            parent,
            variable=self._progress_val,
            maximum=100,
            mode="determinate",
            style="Horizontal.TProgressbar"
        )

        self._frame = tk.Frame(parent, bg=T("FOOTER_BG"))
        self._frame.pack(fill="x")

        tk.Frame(self._frame, bg=T("FOOTER_BORDER"), height=1).pack(fill="x")

        inner = tk.Frame(self._frame, bg=T("FOOTER_BG"))
        inner.pack(fill="x", padx=24, pady=14)

        # ── Sol — RUN STEPS / STOP ─────────────────────────
        left = tk.Frame(inner, bg=T("FOOTER_BG"))
        left.pack(side="left", fill="y")

        self.start_btn = tk.Button(
            left, text=tr("RUN STEPS"),
            command=self.on_start,
            bg=T("FOOTER_FG"), fg=T("FOOTER_BG"),
            font=("Segoe UI", 12, "bold"),
            relief="flat", bd=0,
            highlightthickness=2,
            highlightbackground=T("FOOTER_FG"),
            padx=24, pady=10, cursor="hand2",
            activebackground=T("FOOTER_BG"),
            activeforeground=T("FOOTER_FG")
        )
        self.start_btn.pack(side="left", padx=(0, 10))
        self.start_btn.bind("<Enter>", lambda e: self.start_btn.config(
            bg=T("FOOTER_BG"), fg=T("FOOTER_FG"),
            highlightbackground=T("FOOTER_FG")))
        self.start_btn.bind("<Leave>", lambda e: self.start_btn.config(
            bg=T("FOOTER_FG"), fg=T("FOOTER_BG"),
            highlightbackground=T("FOOTER_FG")))

        self.stop_btn = tk.Button(
            left, text=tr("STOP"),
            command=self.on_stop,
            bg=T("FOOTER_BG"), fg=T("FOOTER_FG"),
            font=("Segoe UI", 10, "bold"),
            relief="solid", bd=1,
            highlightthickness=1,
            highlightbackground=T("FOOTER_BORDER"),
            padx=18, pady=10, cursor="hand2", state="disabled",
            activebackground=T("FOOTER_FG"),
            activeforeground=T("FOOTER_BG")
        )
        self.stop_btn.pack(side="left")
        self.stop_btn.bind("<Enter>", lambda e:
            self.stop_btn.config(bg=T("FOOTER_FG"), fg=T("FOOTER_BG"))
            if str(self.stop_btn["state"]) == "normal" else None)
        self.stop_btn.bind("<Leave>", lambda e:
            self.stop_btn.config(bg=T("FOOTER_BG"), fg=T("FOOTER_FG"))
            if str(self.stop_btn["state"]) == "normal" else None)

        # Dikey çizgi
        tk.Frame(inner, bg=T("FOOTER_BORDER"), width=1).pack(
            side="left", fill="y", padx=24, pady=4)

        # ── Orta — Loop + Interval ─────────────────────────
        mid = tk.Frame(inner, bg=T("FOOTER_BG"))
        mid.pack(side="left", fill="y")

        loop_grp = tk.Frame(mid, bg=T("FOOTER_BG"))
        loop_grp.pack(side="left", padx=(0, 20))

        tk.Label(loop_grp, text=tr("LOOP"),
                  bg=T("FOOTER_BG"), fg=T("FOOTER_FG2"),
                  font=("Segoe UI", 8, "bold")).pack(
            anchor="w", pady=(0, 6))

        loop_inner = tk.Frame(loop_grp, bg=T("FOOTER_BG"))
        loop_inner.pack(anchor="w")

        self.loop_infinite_var = tk.BooleanVar(value=False)
        self.loop_cb = tk.Checkbutton(
            loop_inner, text=tr("Infinite"),
            variable=self.loop_infinite_var,
            bg=T("FOOTER_BG"), fg=T("FOOTER_FG"),
            selectcolor=T("FOOTER_BG"),
            activebackground=T("FOOTER_BG"),
            activeforeground=T("FOOTER_FG"),
            font=("Segoe UI", 9),
            relief="flat"
        )
        self.loop_cb.pack(side="left", padx=(0, 12))

        tk.Label(loop_inner, text=tr("Count"),
                  bg=T("FOOTER_BG"), fg=T("FOOTER_FG2"),
                  font=("Segoe UI", 8)).pack(side="left", padx=(0, 4))

        self.loop_count_entry = tk.Entry(
            loop_inner, width=5,
            bg=T("FOOTER_BG"), fg=T("FOOTER_FG"),
            relief="solid", bd=1,
            highlightthickness=1,
            highlightbackground=T("FOOTER_BORDER"),
            highlightcolor=T("FOOTER_FG"),
            font=("Segoe UI", 9),
            insertbackground=T("FOOTER_FG"),
            justify="center"
        )
        self.loop_count_entry.insert(0, "1")
        self.loop_count_entry.pack(side="left")

        # Dikey çizgi
        tk.Frame(mid, bg=T("FOOTER_BORDER"), width=1).pack(
            side="left", fill="y", padx=20, pady=4)

        iv_grp = tk.Frame(mid, bg=T("FOOTER_BG"))
        iv_grp.pack(side="left")

        tk.Label(iv_grp, text=tr("STEP INTERVAL"),
                  bg=T("FOOTER_BG"), fg=T("FOOTER_FG2"),
                  font=("Segoe UI", 8, "bold")).pack(
            anchor="w", pady=(0, 2))
        tk.Label(iv_grp,
                  text=tr("Wait after all steps finish, before repeating"),
                  bg=T("FOOTER_BG"), fg=T("FOOTER_FG2"),
                  font=("Segoe UI", 7)).pack(anchor="w", pady=(0, 4))

        self.interval_widget = make_interval_widget(
            iv_grp, bg=T("FOOTER_BG"), default_ms=100,
            dark=True)
        self.interval_widget.pack(anchor="w")

        # Support Us Mini Button aligned to the right inside mid
        support_grp = tk.Frame(mid, bg=T("FOOTER_BG"))
        support_grp.pack(side="right", padx=10)

        def open_donate():
            from tkinter import messagebox
            messagebox.showinfo(tr("Support Us"), tr("Thank you! Please visit the Support & Donate tab on the sidebar to buy us a coffee."))

        self.support_btn = tk.Button(
            support_grp, text="♥ " + tr("SUPPORT US"),
            command=open_donate,
            bg=T("FOOTER_BG"), fg=T("DANGER"),
            font=("Segoe UI", 8, "bold"),
            relief="solid", bd=1,
            highlightthickness=1,
            highlightbackground=T("FOOTER_BORDER"),
            padx=10, pady=3, cursor="hand2",
            activebackground=T("DANGER"),
            activeforeground=T("FOOTER_FG")
        )
        self.support_btn.pack()
        self.support_btn.bind("<Enter>", lambda e: self.support_btn.config(
            bg=T("DANGER"), fg=T("FOOTER_FG")))
        self.support_btn.bind("<Leave>", lambda e: self.support_btn.config(
            bg=T("FOOTER_BG"), fg=T("DANGER")))

        # Dikey çizgi
        tk.Frame(inner, bg=T("FOOTER_BORDER"), width=1).pack(
            side="right", fill="y", padx=24, pady=4)

        # ── Sağ — Status + Hotkey ─────────────────────────
        right = tk.Frame(inner, bg=T("FOOTER_BG"))
        right.pack(side="right", fill="y")

        status_row = tk.Frame(right, bg=T("FOOTER_BG"))
        status_row.pack(anchor="e", pady=(0, 8))

        tk.Label(status_row, text=tr("STATUS"),
                  bg=T("FOOTER_BG"), fg=T("FOOTER_FG2"),
                  font=("Segoe UI", 8, "bold")).pack(
            side="left", padx=(0, 8))

        self.status_label = tk.Label(
            status_row, text=tr("Ready"),
            bg=T("FOOTER_BG"), fg=T("FOOTER_FG"),
            font=("Segoe UI", 10)
        )
        self.status_label.pack(side="left")

        # Aktif adım göstergesi — otomasyon sırasında hangi adım çalışıyor
        self._active_step_row = tk.Frame(right, bg=T("FOOTER_BG"))
        self._active_step_row.pack(anchor="e", pady=(2, 0))
        tk.Label(self._active_step_row, text=tr("STEP"),
                 bg=T("FOOTER_BG"), fg=T("FOOTER_FG2"),
                 font=("Segoe UI", 7, "bold")).pack(side="left", padx=(0, 6))
        self._active_step_lbl = tk.Label(
            self._active_step_row, text="—",
            bg=T("FOOTER_BG"), fg=T("FOOTER_FG"),
            font=("Segoe UI", 9, "bold")
        )
        self._active_step_lbl.pack(side="left")
        self._active_step_row.pack_forget()   # başlangıçta gizli

        # Scheduler satırı
        sched_row = tk.Frame(right, bg=T("FOOTER_BG"))
        sched_row.pack(anchor="e", pady=(4, 0))
        self._sched_btn = tk.Button(
            sched_row, text=tr("⏰ SCHEDULE"),
            command=self._open_scheduler,
            bg=T("FOOTER_BG"), fg=T("FOOTER_FG"),
            font=("Segoe UI", 8),
            relief="solid", bd=1,
            highlightthickness=1,
            highlightbackground=T("FOOTER_BORDER"),
            padx=8, pady=2, cursor="hand2",
            activebackground=T("FOOTER_FG"),
            activeforeground=T("FOOTER_BG")
        )
        self._sched_btn.pack(side="left", padx=(0, 6))
        self._sched_btn.bind("<Enter>", lambda e: self._sched_btn.config(
            bg=T("FOOTER_FG"), fg=T("FOOTER_BG")))
        self._sched_btn.bind("<Leave>", lambda e: self._sched_btn.config(
            bg=T("FOOTER_BG"), fg=T("FOOTER_FG")))
        self._sched_status = tk.Label(
            sched_row, text="",
            bg=T("FOOTER_BG"), fg=T("FOOTER_FG2"),
            font=("Segoe UI", 7)
        )
        self._sched_status.pack(side="left")

        hk_row = tk.Frame(right, bg=T("FOOTER_BG"))
        hk_row.pack(anchor="e")

        tk.Label(hk_row, text=tr("HOTKEY"),
                  bg=T("FOOTER_BG"), fg=T("FOOTER_FG2"),
                  font=("Segoe UI", 8, "bold")).pack(
            side="left", padx=(0, 8))

        self.hotkey_display = tk.Label(
            hk_row, text=state.hotkey.upper(),
            bg=T("BADGE_BG"), fg=T("BADGE_FG"),
            font=("Segoe UI", 9, "bold"),
            relief="solid", bd=1,
            padx=10, pady=3
        )
        self.hotkey_display.pack(side="left", padx=(0, 8))

        self.hotkey_btn = tk.Button(
            hk_row, text=tr("CHANGE"),
            command=self.on_change_hotkey,
            bg=T("FOOTER_BG"), fg=T("FOOTER_FG"),
            font=("Segoe UI", 8),
            relief="solid", bd=1,
            highlightthickness=1,
            highlightbackground=T("FOOTER_BORDER"),
            padx=8, pady=3, cursor="hand2",
            activebackground=T("FOOTER_FG"),
            activeforeground=T("FOOTER_BG")
        )
        self.hotkey_btn.pack(side="left")
        self.hotkey_btn.bind("<Enter>", lambda e: self.hotkey_btn.config(
            bg=T("FOOTER_FG"), fg=T("FOOTER_BG")))
        self.hotkey_btn.bind("<Leave>", lambda e: self.hotkey_btn.config(
            bg=T("FOOTER_BG"), fg=T("FOOTER_FG")))

    def get_interval_seconds(self):
        return self.interval_widget.get_seconds()

    def set_running(self, is_running):
        if is_running:
            self.start_btn.config(state="disabled",
                                  bg=T("FOOTER_BORDER"),
                                  fg=T("FOOTER_FG2"))
            self.stop_btn.config(state="normal")
            self._prog_bar.pack(fill="x", side="bottom",
                                before=self._frame)
        else:
            self.start_btn.config(state="normal",
                                  bg=T("FOOTER_FG"),
                                  fg=T("FOOTER_BG"))
            self.stop_btn.config(state="disabled")
            self._progress_val.set(0)
            self._prog_bar.pack_forget()

    def set_progress(self, current, total):
        if total > 0:
            self._progress_val.set((current / total) * 100)

    def set_status(self, text, color=None):
        self.status_label.config(
            text=text, fg=color or T("FOOTER_FG"))

    def update_hotkey_display(self, key_name):
        self.hotkey_display.config(text=key_name.upper())

    def get_loop_settings(self):
        infinite = self.loop_infinite_var.get()
        try:
            count = int(self.loop_count_entry.get())
        except:
            count = 1
        return infinite, count

    def set_state(self, s):
        for w in [self.loop_cb, self.loop_count_entry, self.hotkey_btn]:
            try:
                w.config(state=s)
            except:
                pass
        self.interval_widget.set_state(s)

    def refresh_labels(self):
        pass

    def set_active_step(self, idx: int, label: str = ""):
        """Otomasyon sırasında hangi adımın çalıştığını göster."""
        try:
            if idx < 0:
                self._active_step_row.pack_forget()
            else:
                step_text = f"#{idx+1}" + (f"  {label}" if label else "")
                self._active_step_lbl.config(text=step_text)
                if not self._active_step_row.winfo_ismapped():
                    self._active_step_row.pack(anchor="e", pady=(2, 0))
        except Exception:
            pass

    def _open_scheduler(self):
        """Zamanlayıcı ayarları dialog'unu aç."""
        _SchedulerDialog(self._frame, self._on_scheduler_set)

    def _on_scheduler_set(self, mode: str, hour: int, minute: int, interval_min: int):
        """
        mode: "once" | "repeat" | "off"
        hour, minute: hedef saat (once için)
        interval_min: tekrar aralığı dakika (repeat için)
        """
        if self._scheduler_job:
            try:
                self._frame.after_cancel(self._scheduler_job)
            except Exception:
                pass
            self._scheduler_job = None

        if mode == "off":
            self._scheduler_active = False
            self._sched_status.config(text="")
            return

        self._scheduler_active = True
        if mode == "once":
            self._sched_status.config(text=f"⏰ {hour:02d}:{minute:02d}")
            self._schedule_once(hour, minute)
        elif mode == "repeat":
            self._sched_status.config(text=f"↻ {tr('every')} {interval_min}{tr('min')}")
            self._schedule_repeat(interval_min * 60)

    def _schedule_once(self, hour: int, minute: int):
        import datetime
        now = datetime.datetime.now()
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target += datetime.timedelta(days=1)
        delay_ms = int((target - now).total_seconds() * 1000)
        self._scheduler_job = self._frame.after(
            delay_ms, self._fire_scheduled)

    def _schedule_repeat(self, interval_secs: float):
        delay_ms = int(interval_secs * 1000)
        def _tick():
            self._fire_scheduled()
            if self._scheduler_active:
                self._scheduler_job = self._frame.after(delay_ms, _tick)
        self._scheduler_job = self._frame.after(delay_ms, _tick)

    def _fire_scheduled(self):
        """Zamanlayıcı tetiklendi — RUN STEPS simüle et."""
        if self.on_start:
            self.on_start()


# ── Scheduler Dialog ─────────────────────────────────────────────────────────

class _SchedulerDialog:
    """Zamanlayıcı ayarları — belirli saatte veya aralıkla çalıştır."""

    def __init__(self, parent, on_set):
        self._on_set = on_set
        self._win = tk.Toplevel(parent)
        self._win.title("Scheduler")
        self._win.resizable(False, False)
        self._win.configure(bg=T("SURFACE"))
        self._win.grab_set()
        self._win.focus_set()
        self._build()
        self._center(parent)

    def _build(self):
        from tkinter import ttk as _ttk

        # Header
        hdr = tk.Frame(self._win, bg=T("PRIMARY_BG"))
        hdr.pack(fill="x")
        tk.Label(hdr, text=tr("  ⏰  SCHEDULER"),
                 bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
                 font=("Segoe UI", 11, "bold"),
                 pady=14).pack(side="left")

        body = tk.Frame(self._win, bg=T("SURFACE"))
        body.pack(fill="both", expand=True, padx=24, pady=(16, 0))

        # Mod seçimi
        tk.Label(body, text=tr("MODE"),
                 bg=T("SURFACE"), fg=T("FG2"),
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 6))

        self._mode_var = tk.StringVar(value="once")
        mode_row = tk.Frame(body, bg=T("SURFACE"))
        mode_row.pack(fill="x", pady=(0, 16))

        for val, lbl in [("once",   tr("Run once at time")),
                          ("repeat", tr("Repeat every N minutes")),
                          ("off",    tr("Off"))]:
            tk.Radiobutton(
                mode_row, text=lbl, variable=self._mode_var, value=val,
                bg=T("SURFACE"), fg=T("FG"),
                selectcolor=T("CHECK_BG"),
                activebackground=T("SURFACE"),
                activeforeground=T("FG"),
                font=("Segoe UI", 9),
                command=self._on_mode_change
            ).pack(anchor="w", pady=2)

        # "Once" ayarları
        self._once_frame = tk.Frame(body, bg=T("SURFACE"))
        self._once_frame.pack(fill="x", pady=(0, 8))
        tk.Label(self._once_frame, text=tr("RUN AT"),
                 bg=T("SURFACE"), fg=T("FG2"),
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 4))
        time_row = tk.Frame(self._once_frame, bg=T("SURFACE"))
        time_row.pack(anchor="w")

        self._hour_var = tk.StringVar(value="09")
        self._min_var  = tk.StringVar(value="00")

        hour_cb = _ttk.Combobox(time_row, textvariable=self._hour_var,
                                values=[f"{h:02d}" for h in range(24)],
                                state="readonly", width=4,
                                font=("Segoe UI", 10))
        hour_cb.pack(side="left")
        tk.Label(time_row, text=" : ",
                 bg=T("SURFACE"), fg=T("FG"),
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        min_cb = _ttk.Combobox(time_row, textvariable=self._min_var,
                               values=[f"{m:02d}" for m in range(0, 60, 5)],
                               state="readonly", width=4,
                               font=("Segoe UI", 10))
        min_cb.pack(side="left")

        # "Repeat" ayarları
        self._repeat_frame = tk.Frame(body, bg=T("SURFACE"))
        self._repeat_frame.pack(fill="x", pady=(0, 8))
        tk.Label(self._repeat_frame, text=tr("INTERVAL (minutes)"),
                 bg=T("SURFACE"), fg=T("FG2"),
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 4))
        self._interval_entry = tk.Entry(
            self._repeat_frame, width=8,
            bg=T("ENTRY_BG"), fg=T("FG"),
            relief="solid", bd=1,
            highlightthickness=1,
            highlightbackground=T("BORDER"),
            font=("Segoe UI", 10), justify="center",
            insertbackground=T("FG")
        )
        self._interval_entry.insert(0, "30")
        self._interval_entry.pack(anchor="w")

        self._on_mode_change()

        # Önizleme
        self._preview_lbl = tk.Label(
            body, text="",
            bg=T("SURFACE"), fg=T("FG2"),
            font=("Segoe UI", 8, "italic"), wraplength=260)
        self._preview_lbl.pack(anchor="w", pady=(4, 0))

        # Butonlar
        btn_row = tk.Frame(self._win, bg=T("SURFACE"))
        btn_row.pack(fill="x", padx=24, pady=(12, 20))

        ok_btn = tk.Button(
            btn_row, text=tr("SET SCHEDULE"),
            command=self._save,
            bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
            font=("Segoe UI", 9, "bold"),
            relief="flat", bd=0, padx=16, pady=7, cursor="hand2",
            activebackground=T("PRIMARY_H_BG"),
            activeforeground=T("PRIMARY_H_FG")
        )
        ok_btn.pack(side="left", padx=(0, 10))

        cancel_btn = tk.Button(
            btn_row, text=tr("CANCEL"),
            command=self._win.destroy,
            bg=T("SURFACE"), fg=T("FG"),
            font=("Segoe UI", 9),
            relief="solid", bd=1, padx=12, pady=5, cursor="hand2",
            highlightthickness=1,
            highlightbackground=T("BORDER"),
            activebackground=T("SURFACE2"),
            activeforeground=T("FG")
        )
        cancel_btn.pack(side="left")

        self._win.bind("<Return>", lambda e: self._save())
        self._win.bind("<Escape>", lambda e: self._win.destroy())

    def _on_mode_change(self):
        mode = self._mode_var.get()
        # Sadece ilgili alt-formu göster
        if mode == "once":
            self._once_frame.pack(fill="x", pady=(0, 8))
            self._repeat_frame.pack_forget()
        elif mode == "repeat":
            self._once_frame.pack_forget()
            self._repeat_frame.pack(fill="x", pady=(0, 8))
        else:
            self._once_frame.pack_forget()
            self._repeat_frame.pack_forget()

    def _save(self):
        mode = self._mode_var.get()
        try:
            hour = int(self._hour_var.get())
            minute = int(self._min_var.get())
        except Exception:
            hour, minute = 9, 0
        try:
            interval = max(1, int(self._interval_entry.get()))
        except Exception:
            interval = 30
        self._on_set(mode, hour, minute, interval)
        self._win.destroy()

    def _center(self, parent):
        self._win.update_idletasks()
        pw = self._win.winfo_reqwidth()
        ph = self._win.winfo_reqheight()
        try:
            rx = parent.winfo_rootx()
            ry = parent.winfo_rooty()
            rw = parent.winfo_width()
            rh = parent.winfo_height()
            sx = rx + rw // 2 - pw // 2
            sy = ry + rh // 2 - ph // 2
        except Exception:
            sx, sy = 300, 200
        self._win.geometry(f"+{max(0,sx)}+{max(0,sy)}")