"""
sidebar.py â€” Osenpa Auto Clicker
Navigasyon Ã§ubuÄŸu. THEME bÃ¶lÃ¼mÃ¼ her zaman gÃ¶rÃ¼nÃ¼r kalÄ±r (scrollable nav).
"""
import tkinter as tk
from ui.theme import T, set_dark, apply_styles, is_dark
from utils.i18n import tr

MENU_ITEMS = [
    ("profiles",    "Profiles"),
    ("keyboard",    "Keyboard"),
    ("mouse",       "Mouse"),
    ("macro",       "Record Actions"),
    ("color",       "Color Detection"),
    ("image",       "Image Detection"),
    ("settings",    "Settings"),
    ("help",        "Help & Guide"),
    ("donate",      "Support & Donate"),
]


class Sidebar:
    def __init__(self, parent, on_tab_change, on_theme_change=None,
                 initial_tab="keyboard"):
        self.on_tab_change   = on_tab_change
        self.on_theme_change = on_theme_change
        self.active_tab      = initial_tab
        self._tab_btns       = {}
        self._dark_var       = tk.BooleanVar(value=False)
        self._build(parent)

    def _build(self, parent):
        # Ana sidebar frame â€” sabit geniÅŸlik
        self.frame = tk.Frame(parent, bg=T("SIDEBAR_BG"), width=210)
        self.frame.pack(side="left", fill="y")
        self.frame.pack_propagate(False)

        # SaÄŸ kenar Ã§izgisi
        tk.Frame(self.frame, bg=T("BORDER"), width=1).pack(side="right", fill="y")

        # â”€â”€ Ãœst bÃ¶lÃ¼m: Brand (sabit yÃ¼kseklik) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        top_frame = tk.Frame(self.frame, bg=T("SIDEBAR_BG"))
        top_frame.pack(side="top", fill="x")

        brand = tk.Frame(top_frame, bg=T("SIDEBAR_BG"))
        brand.pack(fill="x", padx=20, pady=(20, 14))

        # OSENPA â€” bÃ¼yÃ¼k, belirgin marka adÄ±
        tk.Label(brand, text=tr("OSENPA"),
                  bg=T("SIDEBAR_BG"), fg=T("SIDEBAR_FG"),
                  font=("Segoe UI", 17, "bold")).pack(anchor="w")

        # AUTO CLICKER â€” aynÄ± boyut, tek satÄ±r, yan yana
        tk.Label(brand, text=tr("AUTO CLICKER"),
                  bg=T("SIDEBAR_BG"), fg=T("SIDEBAR_FG2"),
                  font=("Segoe UI", 17, "bold")).pack(anchor="w")

        tk.Frame(top_frame, bg=T("SIDEBAR_HOV"), height=1).pack(fill="x", padx=24)

        # â”€â”€ Alt bÃ¶lÃ¼m: THEME (sabit, her zaman gÃ¶rÃ¼nÃ¼r) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        bottom_frame = tk.Frame(self.frame, bg=T("SIDEBAR_BG"))
        bottom_frame.pack(side="bottom", fill="x")

        tk.Frame(bottom_frame, bg=T("SIDEBAR_HOV"), height=1).pack(
            fill="x", padx=24)

        theme_row = tk.Frame(bottom_frame, bg=T("SIDEBAR_BG"))
        theme_row.pack(fill="x", padx=24, pady=(12, 16))

        tk.Label(theme_row, text=tr("THEME"),
                  bg=T("SIDEBAR_BG"), fg=T("SIDEBAR_FG2"),
                  font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 8))

        toggle_frame = tk.Frame(theme_row, bg=T("SIDEBAR_BG"))
        toggle_frame.pack(anchor="w")

        self._light_btn = tk.Button(
            toggle_frame, text=tr("LIGHT"),
            command=lambda: self._set_theme(False),
            bg=T("SIDEBAR_BG"), fg=T("SIDEBAR_FG"),
            font=("Segoe UI", 9, "bold"),
            relief="solid", bd=1, highlightthickness=0,
            padx=10, pady=4, cursor="hand2",
            activebackground=T("SIDEBAR_FG"),
            activeforeground=T("SIDEBAR_BG")
        )
        self._light_btn.pack(side="left", padx=(0, 4))

        self._dark_btn = tk.Button(
            toggle_frame, text=tr("DARK"),
            command=lambda: self._set_theme(True),
            bg=T("SIDEBAR_BG"), fg=T("SIDEBAR_FG"),
            font=("Segoe UI", 9),
            relief="solid", bd=1, highlightthickness=0,
            padx=10, pady=4, cursor="hand2",
            activebackground=T("SIDEBAR_FG"),
            activeforeground=T("SIDEBAR_BG")
        )
        self._dark_btn.pack(side="left")

        # â”€â”€ Orta bÃ¶lÃ¼m: Nav â€” Canvas ile scrollable â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        mid_frame = tk.Frame(self.frame, bg=T("SIDEBAR_BG"))
        mid_frame.pack(side="top", fill="both", expand=True)

        self._nav_canvas = tk.Canvas(
            mid_frame, bg=T("SIDEBAR_BG"),
            highlightthickness=0, width=210
        )
        self._nav_canvas.pack(side="left", fill="both", expand=True)

        self._nav_sb = tk.Scrollbar(
            mid_frame, orient="vertical",
            command=self._nav_canvas.yview,
            bg=T("SCROLL_BG"), troughcolor=T("SCROLL_BG"),
            activebackground=T("SCROLL_ACTIVE"),
            relief="flat", bd=0, width=6
        )
        self._nav_canvas.configure(yscrollcommand=self._nav_sb_set)

        nav_inner = tk.Frame(self._nav_canvas, bg=T("SIDEBAR_BG"))
        self._nav_win = self._nav_canvas.create_window(
            (0, 0), window=nav_inner, anchor="nw"
        )

        tk.Label(nav_inner, text=tr("NAVIGATION"),
                  bg=T("SIDEBAR_BG"), fg=T("SIDEBAR_FG2"),
                  font=("Segoe UI", 8, "bold")).pack(
            anchor="w", padx=24, pady=(16, 8))

        for key, label in MENU_ITEMS:
            self._make_tab(nav_inner, key, tr(label))

        def _on_nav_cfg(e):
            self._nav_canvas.configure(
                scrollregion=self._nav_canvas.bbox("all"))
            self._nav_canvas.itemconfig(self._nav_win, width=e.width)

        def _on_canvas_cfg(e):
            bb = self._nav_canvas.bbox("all")
            if bb:
                if (bb[3] - bb[1]) > e.height:
                    self._nav_sb.pack(side="right", fill="y",
                                      before=self._nav_canvas)
                else:
                    self._nav_sb.pack_forget()
            self._nav_canvas.itemconfig(self._nav_win, width=e.width)

        nav_inner.bind("<Configure>", _on_nav_cfg)
        self._nav_canvas.bind("<Configure>", _on_canvas_cfg)

        self._nav_canvas.bind("<Enter>",
            lambda e: self._nav_canvas.bind_all("<MouseWheel>",
                lambda ev: self._nav_canvas.yview_scroll(
                    int(-1*(ev.delta/120)), "units")))
        self._nav_canvas.bind("<Leave>",
            lambda e: self._nav_canvas.unbind_all("<MouseWheel>"))

        self._update_theme_btns()
        self._set_active_style(self.active_tab)

    def _nav_sb_set(self, *args):
        self._nav_sb.set(*args)

    def _set_theme(self, dark: bool):
        self._dark_var.set(dark)
        set_dark(dark)
        apply_styles()
        if self.on_theme_change:
            self.on_theme_change()

    def _update_theme_btns(self):
        dark = self._dark_var.get()
        if not dark:
            self._light_btn.config(
                bg=T("SIDEBAR_FG"), fg=T("SIDEBAR_BG"),
                font=("Segoe UI", 9, "bold"))
            self._dark_btn.config(
                bg=T("SIDEBAR_BG"), fg=T("SIDEBAR_FG2"),
                font=("Segoe UI", 9))
        else:
            self._dark_btn.config(
                bg=T("SIDEBAR_FG"), fg=T("SIDEBAR_BG"),
                font=("Segoe UI", 9, "bold"))
            self._light_btn.config(
                bg=T("SIDEBAR_BG"), fg=T("SIDEBAR_FG2"),
                font=("Segoe UI", 9))

    def _make_tab(self, parent, key, label):
        btn = tk.Button(
            parent, text=label,
            command=lambda k=key: self._on_tab_click(k),
            bg=T("SIDEBAR_BG"), fg=T("SIDEBAR_FG2"),
            font=("Segoe UI", 10),
            relief="flat",
            padx=24, pady=10,
            cursor="hand2", anchor="w",
            bd=0,
            activebackground=T("SIDEBAR_HOV"),
            activeforeground=T("SIDEBAR_FG"),
        )
        btn.pack(fill="x")
        btn.bind("<Enter>", lambda e, b=btn, k=key: (
            b.config(bg=T("SIDEBAR_HOV"), fg=T("SIDEBAR_FG"))
            if k != self.active_tab else None))
        btn.bind("<Leave>", lambda e, b=btn, k=key: (
            b.config(bg=T("SIDEBAR_BG"), fg=T("SIDEBAR_FG2"))
            if k != self.active_tab else None))
        self._tab_btns[key] = btn

    def _on_tab_click(self, key):
        if key == self.active_tab:
            return
        old = self.active_tab
        self.active_tab = key
        self._set_active_style(key)
        self._set_inactive_style(old)
        self.on_tab_change(key)

    def _set_active_style(self, key):
        btn = self._tab_btns.get(key)
        if btn:
            btn.config(
                bg=T("SIDEBAR_ACT"),
                fg=T("SIDEBAR_ACT_FG"),
                font=("Segoe UI", 10, "bold"),
                activebackground=T("SIDEBAR_ACT"),
                activeforeground=T("SIDEBAR_ACT_FG")
            )

    def _set_inactive_style(self, key):
        btn = self._tab_btns.get(key)
        if btn:
            btn.config(
                bg=T("SIDEBAR_BG"),
                fg=T("SIDEBAR_FG2"),
                font=("Segoe UI", 10),
                activebackground=T("SIDEBAR_HOV"),
                activeforeground=T("SIDEBAR_FG")
            )

