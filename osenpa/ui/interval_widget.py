import tkinter as tk
from tkinter import ttk
from ui.theme import T

# (label, saniye cinsinden çarpan)
UNITS = [
    ("MS",  0.001),
    ("SEC", 1.0),
    ("MIN", 60.0),
    ("HR",  3600.0),
]


def make_interval_widget(parent, bg=None, default_ms=100, dark=False):
    bg_color = bg or T("SURFACE")

    frame = tk.Frame(parent, bg=bg_color)

    entry_bg = T("FOOTER_BG") if dark else T("ENTRY_BG")
    entry_fg = T("FOOTER_FG") if dark else T("FG")
    border   = T("FOOTER_BORDER") if dark else T("BORDER")
    hi_color = T("FOOTER_FG") if dark else T("BORDER_STRONG")

    val_entry = tk.Entry(
        frame, width=7,
        bg=entry_bg, fg=entry_fg,
        relief="solid", bd=1,
        highlightthickness=1,
        highlightbackground=border,
        highlightcolor=hi_color,
        font=("Segoe UI", 9),
        justify="center",
        insertbackground=entry_fg
    )
    val_entry.insert(0, str(default_ms))
    val_entry.pack(side="left", padx=(0, 4))

    val_entry.bind("<FocusIn>",
        lambda e: val_entry.config(
            highlightbackground=hi_color,
            highlightthickness=2))
    val_entry.bind("<FocusOut>",
        lambda e: val_entry.config(
            highlightbackground=border,
            highlightthickness=1))

    unit_var = tk.StringVar(value="MS")
    unit_cb  = ttk.Combobox(
        frame,
        textvariable=unit_var,
        values=[u[0] for u in UNITS],
        state="readonly",
        width=5,
        font=("Segoe UI", 9)
    )
    unit_cb.pack(side="left")

    def get_seconds():
        try:
            raw = val_entry.get().strip()
            val = float(raw) if raw else float(default_ms)
        except ValueError:
            val = float(default_ms)

        unit_label = unit_var.get()
        mult = next(
            (u[1] for u in UNITS if u[0] == unit_label),
            0.001  # fallback: MS
        )
        result = val * mult
        return max(0.001, result)   # minimum 1ms

    def set_state(s):
        val_entry.config(state=s)
        unit_cb.config(
            state="readonly" if s == "normal" else "disabled")

    frame.get_seconds = get_seconds
    frame.set_state   = set_state
    return frame