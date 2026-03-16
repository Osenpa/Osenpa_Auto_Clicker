import tkinter as tk
from tkinter import ttk

_LIGHT = {
    "BG":            "#F8F9FA",
    "BG2":           "#F1F3F5",
    "FG":            "#212529",
    "FG2":           "#6C757D",
    "FG3":           "#ADB5BD",
    "BORDER":        "#DEE2E6",
    "BORDER_STRONG": "#212529",
    "SURFACE":       "#FFFFFF",
    "SURFACE2":      "#F8F9FA",
    "ENTRY_BG":      "#FFFFFF",
    "PRIMARY_BG":    "#212529",
    "PRIMARY_FG":    "#FFFFFF",
    "PRIMARY_H_BG":  "#FFFFFF",
    "PRIMARY_H_FG":  "#212529",
    "DANGER":        "#C0392B",
    "DANGER_BG":     "#FDEDED",
    "COND_TRUE":     "#27AE60",
    "COND_FALSE":    "#E74C3C",
    "SIDEBAR_BG":    "#212529",
    "SIDEBAR_FG":    "#E9ECEF",
    "SIDEBAR_FG2":   "#6C757D",
    "SIDEBAR_ACT":   "#F8F9FA",
    "SIDEBAR_ACT_FG":"#212529",
    "SIDEBAR_HOV":   "#2C3034",
    "FOOTER_BG":     "#212529",
    "FOOTER_FG":     "#F8F9FA",
    "FOOTER_FG2":    "#6C757D",
    "FOOTER_BORDER": "#2C3034",
    "BADGE_BG":      "#212529",
    "BADGE_FG":      "#F8F9FA",
    "STOP_BG":       "#2C3034",
    "STOP_FG":       "#F8F9FA",
    "STOP_BORDER":   "#495057",
    "SCROLL_BG":     "#F1F3F5",
    "SCROLL_THUMB":  "#ADB5BD",
    "SCROLL_ACTIVE": "#6C757D",
    "CHECK_BG":      "#FFFFFF",
    "CHECK_FG":      "#212529",
}

_DARK = {
    "BG":            "#121212",
    "BG2":           "#1A1A1A",
    "FG":            "#E0E0E0",
    "FG2":           "#9E9E9E",
    "FG3":           "#616161",
    "BORDER":        "#2C2C2C",
    "BORDER_STRONG": "#E0E0E0",
    "SURFACE":       "#1E1E1E",
    "SURFACE2":      "#121212",
    "ENTRY_BG":      "#1E1E1E",
    "PRIMARY_BG":    "#E0E0E0",
    "PRIMARY_FG":    "#121212",
    "PRIMARY_H_BG":  "#1E1E1E",
    "PRIMARY_H_FG":  "#E0E0E0",
    "DANGER":        "#E74C3C",
    "DANGER_BG":     "#2D1515",
    "COND_TRUE":     "#2ECC71",
    "COND_FALSE":    "#E74C3C",
    "SIDEBAR_BG":    "#0D0D0D",
    "SIDEBAR_FG":    "#E0E0E0",
    "SIDEBAR_FG2":   "#616161",
    "SIDEBAR_ACT":   "#E0E0E0",
    "SIDEBAR_ACT_FG":"#121212",
    "SIDEBAR_HOV":   "#1A1A1A",
    "FOOTER_BG":     "#0D0D0D",
    "FOOTER_FG":     "#E0E0E0",
    "FOOTER_FG2":    "#616161",
    "FOOTER_BORDER": "#1A1A1A",
    "BADGE_BG":      "#E0E0E0",
    "BADGE_FG":      "#121212",
    "STOP_BG":       "#1A1A1A",
    "STOP_FG":       "#E0E0E0",
    "STOP_BORDER":   "#2C2C2C",
    "SCROLL_BG":     "#1A1A1A",
    "SCROLL_THUMB":  "#3C3C3C",
    "SCROLL_ACTIVE": "#5C5C5C",
    "CHECK_BG":      "#3C3C3C",
    "CHECK_FG":      "#E0E0E0",
}

_current = _LIGHT
_is_dark  = False


def is_dark() -> bool:
    return _is_dark


def set_dark(dark: bool):
    global _current, _is_dark
    _is_dark  = dark
    _current  = _DARK if dark else _LIGHT


def T(key: str) -> str:
    return _current.get(key, "#000000")


def apply_styles():
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure("TRadiobutton",
                    background=T("SURFACE"),
                    foreground=T("FG"),
                    font=("Segoe UI", 9))
    style.configure("TCheckbutton",
                    background=T("SURFACE"),
                    foreground=T("FG"),
                    font=("Segoe UI", 9))
    style.configure("Vertical.TScrollbar",
                    background=T("SCROLL_THUMB"),
                    troughcolor=T("SCROLL_BG"),
                    bordercolor=T("BORDER"),
                    arrowcolor=T("FG2"),
                    relief="flat",
                    darkcolor=T("SCROLL_THUMB"),
                    lightcolor=T("SCROLL_THUMB"))
    style.map("Vertical.TScrollbar",
              background=[("active", T("SCROLL_ACTIVE")),
                          ("pressed", T("SCROLL_ACTIVE"))])
    style.configure("TCombobox",
                    fieldbackground=T("ENTRY_BG"),
                    background=T("SURFACE2"),
                    foreground=T("FG"),
                    selectbackground=T("PRIMARY_BG"),
                    selectforeground=T("PRIMARY_FG"),
                    relief="flat")
    style.map("TCombobox",
              fieldbackground=[("readonly", T("ENTRY_BG"))],
              foreground=[("readonly", T("FG"))],
              background=[("readonly", T("SURFACE2"))])
    style.configure("TScale",
                    background=T("SURFACE"),
                    troughcolor=T("BORDER"),
                    sliderthickness=14,
                    sliderrelief="flat")
    style.configure("Horizontal.TProgressbar",
                    background=T("PRIMARY_BG"),
                    troughcolor=T("BORDER"),
                    bordercolor=T("BG"),
                    lightcolor=T("PRIMARY_BG"),
                    darkcolor=T("PRIMARY_BG"))


def make_entry(parent, width=10, default="",
               bg=None, center=False, font_size=9):
    e = tk.Entry(
        parent,
        width=width,
        bg=bg or T("ENTRY_BG"),
        fg=T("FG"),
        relief="solid", bd=1,
        highlightthickness=1,
        highlightbackground=T("BORDER"),
        highlightcolor=T("BORDER_STRONG"),
        font=("Segoe UI", font_size),
        insertbackground=T("FG"),
        disabledbackground=T("SURFACE2"),
        disabledforeground=T("FG3"),
        justify="center" if center else "left",
        takefocus=1,
    )
    e.insert(0, default)
    e.bind("<FocusIn>",
           lambda ev: e.config(highlightbackground=T("BORDER_STRONG"),
                               highlightthickness=2))
    e.bind("<FocusOut>",
           lambda ev: e.config(highlightbackground=T("BORDER"),
                               highlightthickness=1))
    return e


def make_capture_entry(parent, width=22, placeholder="PRESS A KEY COMBINATION..."):
    e = tk.Entry(
        parent,
        width=width,
        bg=T("SURFACE2"),
        fg=T("FG2"),
        relief="solid", bd=1,
        highlightthickness=1,
        highlightbackground=T("BORDER"),
        highlightcolor=T("BORDER_STRONG"),
        font=("Segoe UI", 9),
        insertbackground=T("FG"),
        justify="center",
        takefocus=1,
    )
    e._placeholder = placeholder
    e.insert(0, placeholder)

    def on_fi(ev):
        if e.get() == e._placeholder:
            e.delete(0, tk.END)
            e.config(fg=T("FG"))
        e.config(highlightbackground=T("BORDER_STRONG"),
                 highlightthickness=2)

    def on_fo(ev):
        if e.get().strip() == "":
            e.insert(0, e._placeholder)
            e.config(fg=T("FG2"))
        e.config(highlightbackground=T("BORDER"),
                 highlightthickness=1)

    e.bind("<FocusIn>",  on_fi)
    e.bind("<FocusOut>", on_fo)
    return e


def make_btn(parent, text, cmd, width=None,
             primary=False, danger=False,
             small=False, stop=False):
    TEXT = text.upper()

    if primary or stop:
        b = tk.Button(
            parent, text=TEXT, command=cmd,
            bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
            activebackground=T("PRIMARY_H_BG"),
            activeforeground=T("PRIMARY_H_FG"),
            font=("Segoe UI", 9, "bold"),
            relief="flat", bd=0,
            highlightthickness=2,
            highlightbackground=T("PRIMARY_BG"),
            padx=16, pady=7, cursor="hand2",
            takefocus=1
        )
        b.bind("<Enter>", lambda e: b.config(
            bg=T("PRIMARY_H_BG"), fg=T("PRIMARY_H_FG"),
            highlightbackground=T("BORDER_STRONG")))
        b.bind("<Leave>", lambda e: b.config(
            bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
            highlightbackground=T("PRIMARY_BG")))
        b.bind("<Return>", lambda e: cmd())

    elif danger:
        b = tk.Button(
            parent, text=TEXT, command=cmd,
            bg=T("SURFACE"), fg=T("FG"),
            activebackground=T("SURFACE2"),
            activeforeground=T("FG"),
            font=("Segoe UI", 9),
            relief="solid", bd=1,
            highlightthickness=1,
            highlightbackground=T("BORDER"),
            padx=10, pady=4, cursor="hand2",
            takefocus=1
        )
        b.bind("<Enter>", lambda e: b.config(
            bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
            highlightbackground=T("PRIMARY_BG")))
        b.bind("<Leave>", lambda e: b.config(
            bg=T("SURFACE"), fg=T("FG"),
            highlightbackground=T("BORDER")))
        b.bind("<Return>", lambda e: cmd())

    elif small:
        b = tk.Button(
            parent, text=TEXT, command=cmd,
            bg=T("SURFACE"), fg=T("FG"),
            activebackground=T("SURFACE2"),
            activeforeground=T("FG"),
            font=("Segoe UI", 8),
            relief="solid", bd=1,
            highlightthickness=1,
            highlightbackground=T("BORDER"),
            padx=8, pady=3, cursor="hand2",
            takefocus=1
        )
        b.bind("<Enter>", lambda e: b.config(
            bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
            highlightbackground=T("PRIMARY_BG")))
        b.bind("<Leave>", lambda e: b.config(
            bg=T("SURFACE"), fg=T("FG"),
            highlightbackground=T("BORDER")))
        b.bind("<Return>", lambda e: cmd())

    else:
        b = tk.Button(
            parent, text=TEXT, command=cmd,
            bg=T("SURFACE"), fg=T("FG"),
            activebackground=T("SURFACE2"),
            activeforeground=T("FG"),
            font=("Segoe UI", 9),
            relief="solid", bd=1,
            highlightthickness=1,
            highlightbackground=T("BORDER"),
            padx=12, pady=5, cursor="hand2",
            takefocus=1
        )
        b.bind("<Enter>", lambda e: b.config(
            bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
            highlightbackground=T("PRIMARY_BG")))
        b.bind("<Leave>", lambda e: b.config(
            bg=T("SURFACE"), fg=T("FG"),
            highlightbackground=T("BORDER")))
        b.bind("<Return>", lambda e: cmd())

    if width:
        b.config(width=width)
    return b


def make_icon_btn(parent, icon, cmd, danger=False):
    b = tk.Button(
        parent, text=icon, command=cmd,
        bg=T("SURFACE"), fg=T("FG"),
        activebackground=T("PRIMARY_BG"),
        activeforeground=T("PRIMARY_FG"),
        font=("Segoe UI", 9),
        relief="solid", bd=1,
        highlightthickness=1,
        highlightbackground=T("BORDER"),
        padx=8, pady=4,
        cursor="hand2",
        takefocus=1
    )
    b.bind("<Enter>", lambda e: b.config(
        bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
        highlightbackground=T("PRIMARY_BG")))
    b.bind("<Leave>", lambda e: b.config(
        bg=T("SURFACE"), fg=T("FG"),
        highlightbackground=T("BORDER")))
    b.bind("<Return>", lambda e: cmd())
    return b


def make_slider(parent, from_, to, default, bg=None):
    bg  = bg or T("SURFACE")
    row = tk.Frame(parent, bg=bg)
    var = tk.DoubleVar(value=default)

    val_lbl = tk.Label(
        row, text=str(default),
        bg=T("SURFACE2"), fg=T("FG"),
        font=("Segoe UI", 9, "bold"),
        width=5, relief="solid", bd=1,
        pady=2, padx=4
    )
    val_lbl.pack(side="right", padx=(8, 0))

    def on_change(v):
        rounded = round(float(v), 2)
        var.set(rounded)
        val_lbl.config(text=str(rounded))

    slider = ttk.Scale(
        row, from_=from_, to=to,
        orient="horizontal",
        variable=var,
        command=on_change,
        length=200
    )
    slider.pack(side="left", fill="x", expand=True)
    row.get_val = lambda: round(var.get(), 2)
    row.set_val = lambda v: (var.set(float(v)), on_change(float(v)))
    row.var     = var
    return row


def section_title(parent, text, bg=None):
    bg = bg or T("SURFACE")
    tk.Label(
        parent, text=text,
        bg=bg, fg=T("FG3"),
        font=("Segoe UI", 7, "bold"),
    ).pack(anchor="w", pady=(0, 8))


def divider(parent, padx=0, pady=8, color=None):
    tk.Frame(parent, bg=color or T("BORDER"), height=1).pack(
        fill="x", padx=padx, pady=pady)


def field_label(parent, text, bg=None):
    return tk.Label(
        parent, text=text.upper(),
        bg=bg or T("SURFACE"),
        fg=T("FG2"),
        font=("Segoe UI", 8)
    )