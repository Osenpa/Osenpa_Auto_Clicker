"""
Step Edit Dialog — Osenpa Auto Clicker
Seçili adımı düzenlemek için popup dialog.
Her step tipine göre dinamik form alanları gösterir.
"""
import tkinter as tk
from tkinter import ttk
from ui.theme import T, make_btn, make_entry
from utils.i18n import tr

# interval units
UNITS = [("MS", 0.001), ("SEC", 1.0), ("MIN", 60.0), ("HR", 3600.0)]


def _seconds_to_display(seconds: float) -> tuple[str, str]:
    """Saniyeyi en uygun birim+değer çiftine çevirir."""
    ms = seconds * 1000
    if ms < 1000:
        return str(int(round(ms))), "MS"
    if seconds < 60:
        return f"{seconds:.2f}".rstrip("0").rstrip("."), "SEC"
    if seconds < 3600:
        return f"{seconds / 60:.2f}".rstrip("0").rstrip("."), "MIN"
    return f"{seconds / 3600:.2f}".rstrip("0").rstrip("."), "HR"


def _get_seconds(val_str: str, unit: str) -> float:
    try:
        val = float(val_str)
    except Exception:
        val = 100
    mult = next((u[1] for u in UNITS if u[0] == unit), 0.001)
    return max(0.001, val * mult)


# ── Her tip için field tanımları ─────────────────────────────────────────────
# Her field: (key, label, type, default, options?)
# type: "entry" | "int_entry" | "float_entry" | "radio" | "check" | "interval"

FIELDS = {
    "key": [
        ("key",      "KEY",        "entry",    "a"),
        ("repeat",   "REPEAT",     "int_entry","1"),
        ("interval", "INTERVAL",   "interval", 0.1),
    ],
    "hotkey": [
        ("keys",     "HOTKEY COMBO","entry",    "ctrl+c"),
        ("repeat",   "REPEAT",     "int_entry","1"),
        ("interval", "INTERVAL",   "interval", 0.1),
    ],
    "click": [
        ("use_cursor","USE CURSOR POSITION", "check", False),
        ("x",        "X",          "int_entry","0"),
        ("y",        "Y",          "int_entry","0"),
        ("button",   "BUTTON",     "radio",    "left",
         [("left","LEFT"),("right","RIGHT"),("middle","MIDDLE")]),
        ("repeat",   "REPEAT",     "int_entry","1"),
        ("interval", "INTERVAL",   "interval", 0.1),
    ],
    "scroll": [
        ("x",        "X",          "int_entry","0"),
        ("y",        "Y",          "int_entry","0"),
        ("dy",       "SCROLL AMOUNT (+ up / - down)", "int_entry", "3"),
        ("repeat",   "REPEAT",     "int_entry","1"),
        ("interval", "INTERVAL",   "interval", 0.1),
    ],
    "color": [
        ("rgb",      "RGB COLOR",  "rgb",      [255,0,0]),
        ("tolerance","TOLERANCE",  "int_entry","15"),
        ("button",   "BUTTON",     "radio",    "left",
         [("left","LEFT"),("right","RIGHT"),("middle","MIDDLE")]),
        ("scan_interval","SCAN INTERVAL","interval",0.5),
        ("timeout",  "TIMEOUT  (0 = wait forever)",  "int_entry","0"),
        ("repeat",   "REPEAT",     "int_entry","1"),
        ("interval", "INTERVAL",   "interval", 0.1),
    ],
    "image": [
        ("image_path","IMAGE PATH","entry",    ""),
        ("confidence","CONFIDENCE (0.0 – 1.0)","float_entry","0.8"),
        ("button",   "BUTTON",     "radio",    "left",
         [("left","LEFT"),("right","RIGHT"),("middle","MIDDLE")]),
        ("scan_interval","SCAN INTERVAL","interval",0.5),
        ("timeout",  "TIMEOUT  (0 = wait forever)",  "int_entry","0"),
        ("repeat",   "REPEAT",     "int_entry","1"),
        ("interval", "INTERVAL",   "interval", 0.1),
    ],
}

TYPE_COLORS = {
    "key":      "#4A90D9",
    "hotkey":   "#7B68EE",
    "click":    "#50C878",
    "scroll":   "#FF8C00",
    "color":    "#E74C3C",
    "image":    "#F39C12",
    "delay":    "#6C757D",
    "if_color": "#C0392B",
    "if_image": "#D35400",
}

TYPE_LABELS = {
    "key":      "KEY PRESS",
    "hotkey":   "HOTKEY COMBO",
    "click":    "MOUSE CLICK",
    "scroll":   "SCROLL",
    "color":    "COLOR DETECTION",
    "image":    "IMAGE DETECTION",
    "delay":    "DELAY / WAIT",
    "if_color": "IF COLOR → THEN / ELSE",
    "if_image": "IF IMAGE → THEN / ELSE",
}


class StepEditDialog:
    def __init__(self, parent, step: dict, on_save):
        """
        parent  : Tk widget (ana pencere veya herhangi bir widget)
        step    : Düzenlenecek adım dict'i (kopyası alınır, orijinal değişmez)
        on_save : on_save(updated_step) — OK'a basılınca çağrılır
        """
        self._step    = dict(step)
        self._on_save = on_save
        self._widgets = {}   # key → widget veya (val_entry, unit_cb) tuple
        self._cursor_var = None

        self._win = tk.Toplevel(parent)
        self._win.title(tr("Edit Step"))
        self._win.configure(bg=T("SURFACE"))
        self._win.grab_set()
        self._win.focus_set()

        stype = step.get("type", "key")
        # if_color / if_image: yeniden boyutlandırılabilir + scroll
        if stype in ("if_color", "if_image"):
            self._win.resizable(True, True)
        else:
            self._win.resizable(False, False)

        self._build()
        self._center(parent)

    # ── Build ────────────────────────────────────────────────────────────────

    def _build(self):
        stype = self._step.get("type", "key")
        color = TYPE_COLORS.get(stype, T("PRIMARY_BG"))
        label = tr(TYPE_LABELS.get(stype, stype.upper()))

        # ── Başlık šeridi (scroll dışında, her zaman sabit) ──
        header = tk.Frame(self._win, bg=color)
        header.pack(fill="x", side="top")

        # Koşul adımları için başlıǧa ekstra bilgi ekle
        if stype == "if_color":
            rgb  = self._step.get("rgb", [255, 0, 0])
            hex_c = "#{:02X}{:02X}{:02X}".format(*rgb)
            # Renk swatchi
            swatch = tk.Label(header, text="  ", bg=hex_c, width=3,
                               relief="flat")
            swatch.pack(side="left", padx=(10, 0), ipady=10)
            tk.Label(header,
                      text=tr("  EDIT STEP  —  {}  ·  {}").format(label, hex_c),
                      bg=color, fg="#FFFFFF",
                      font=("Segoe UI", 11, "bold"),
                      pady=14).pack(side="left")
        elif stype == "if_image":
            img_list = self._step.get("image_list", [])
            count = len(img_list) if img_list else 1
            noun = tr("template") if count == 1 else tr("templates")
            tk.Label(header,
                      text=tr("  EDIT STEP  —  {}  ·  {} {}").format(label, count, noun),
                      bg=color, fg="#FFFFFF",
                      font=("Segoe UI", 11, "bold"),
                      pady=14).pack(side="left")
        else:
            tk.Label(header, text=tr("  EDIT STEP  —  {}").format(label),
                      bg=color, fg="#FFFFFF",
                      font=("Segoe UI", 11, "bold"),
                      pady=14).pack(side="left")

        # ── Butonlar (scroll dışında, altta sabit) ────────────
        btn_bar = tk.Frame(self._win, bg=T("SURFACE"))
        btn_bar.pack(fill="x", side="bottom", padx=28, pady=(12, 20))
        make_btn(btn_bar, tr("SAVE CHANGES"), self._save,
                  primary=True).pack(side="left", padx=(0, 10))
        make_btn(btn_bar, tr("CANCEL"), self._win.destroy).pack(side="left")

        self._win.bind("<Return>", lambda e: self._save())
        self._win.bind("<Escape>", lambda e: self._win.destroy())

        if stype in ("if_color", "if_image"):
            # ── Scroll canvas ─────────────────────────────────
            canvas_frame = tk.Frame(self._win, bg=T("SURFACE"))
            canvas_frame.pack(fill="both", expand=True)

            canvas = tk.Canvas(
                canvas_frame,
                bg=T("SURFACE"),
                bd=0, highlightthickness=0,
                relief="flat"
            )
            scrollbar = tk.Scrollbar(
                canvas_frame, orient="vertical",
                command=canvas.yview
            )
            canvas.configure(yscrollcommand=scrollbar.set)

            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)

            # İçerik frame canvas üzerinde
            body = tk.Frame(canvas, bg=T("SURFACE"))
            body_id = canvas.create_window((0, 0), window=body, anchor="nw")

            def _on_body_configure(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
                # Canvas genişliği kadar body'yi genişlet
                canvas.itemconfig(body_id, width=canvas.winfo_width())

            def _on_canvas_configure(event):
                canvas.itemconfig(body_id, width=event.width)

            body.bind("<Configure>", _on_body_configure)
            canvas.bind("<Configure>", _on_canvas_configure)

            # Mouse wheel desteği
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            def _on_mousewheel_linux(event):
                if event.num == 4:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.yview_scroll(1, "units")

            canvas.bind_all("<MouseWheel>",     _on_mousewheel)
            canvas.bind_all("<Button-4>",       _on_mousewheel_linux)
            canvas.bind_all("<Button-5>",       _on_mousewheel_linux)

            # Dialog kapanınca global bind temizle
            def _cleanup(event=None):
                try:
                    canvas.unbind_all("<MouseWheel>")
                    canvas.unbind_all("<Button-4>")
                    canvas.unbind_all("<Button-5>")
                except Exception:
                    pass
            self._win.bind("<Destroy>", _cleanup)

            # İçerik paddingli wrapper
            inner = tk.Frame(body, bg=T("SURFACE"))
            inner.pack(fill="both", expand=True, padx=28, pady=(20, 12))
            self._build_if_body(inner, stype)

        else:
            # ── Normal (scroll yok) ───────────────────────────
            body = tk.Frame(self._win, bg=T("SURFACE"))
            body.pack(fill="both", expand=True, padx=28, pady=(20, 0))
            fields = FIELDS.get(stype, [])
            for field in fields:
                self._add_field(body, field)
            # ── Evrensel Not alanı ────────────────────────────
            self._build_note_field(body)

    def _build_if_body(self, body, stype):
        """IF/THEN/ELSE step için özel form."""
        # ── Koşul bilgisi (sadece gösterim) ──────────────────
        tk.Label(body, text=tr("CONDITION"),
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 4))

        cond_frame = tk.Frame(body, bg=T("SURFACE2"),
                               relief="solid", bd=1,
                               highlightthickness=1,
                               highlightbackground=T("BORDER"))
        cond_frame.pack(fill="x", pady=(0, 4))
        cond_inner = tk.Frame(cond_frame, bg=T("SURFACE2"))
        cond_inner.pack(fill="x", padx=12, pady=8)

        if stype == "if_color":
            rgb = self._step.get("rgb", [255, 0, 0])
            hex_c = "#{:02X}{:02X}{:02X}".format(*rgb)
            swatch = tk.Label(cond_inner, width=3, bg=hex_c,
                               relief="solid", bd=1)
            swatch.pack(side="left", padx=(0, 10), ipady=8)
            info = tk.Frame(cond_inner, bg=T("SURFACE2"))
            info.pack(side="left")
            tk.Label(info, text=f"RGB({rgb[0]}, {rgb[1]}, {rgb[2]})",
                      bg=T("SURFACE2"), fg=T("FG"),
                      font=("Segoe UI", 9, "bold")).pack(anchor="w")
            tc = self._step.get("target_colors", [])
            if len(tc) > 1:
                tk.Label(info, text=tr("+ {} more color(s)").format(len(tc)-1),
                          bg=T("SURFACE2"), fg=T("FG2"),
                          font=("Segoe UI", 8)).pack(anchor="w")
            tol = self._step.get("tolerance", 15)
            tk.Label(info, text=tr("Tolerance: {}").format(tol),
                      bg=T("SURFACE2"), fg=T("FG3"),
                      font=("Segoe UI", 8)).pack(anchor="w")
        else:  # if_image
            img_list = self._step.get("image_list", [])
            count = len(img_list) if img_list else 1
            noun = tr("image") if count == 1 else tr("images")
            tk.Label(cond_inner, text=tr("🖼  {} template {}").format(count, noun),
                      bg=T("SURFACE2"), fg=T("FG"),
                      font=("Segoe UI", 9, "bold")).pack(anchor="w")
            conf = self._step.get("confidence", 0.8)
            tk.Label(cond_inner, text=tr("Confidence: {:.2f}").format(conf),
                      bg=T("SURFACE2"), fg=T("FG3"),
                      font=("Segoe UI", 8)).pack(anchor="w")

        tk.Label(body, text=tr("Re-add step from the panel to change condition targets."),
                  bg=T("SURFACE"), fg=T("FG3"),
                  font=("Segoe UI", 7, "italic")).pack(anchor="w", pady=(2, 12))

        # ── Max Wait ──────────────────────────────────────────
        mw_row = tk.Frame(body, bg=T("SURFACE"))
        mw_row.pack(fill="x", pady=(0, 4))
        tk.Label(mw_row, text=tr("MAX WAIT (scan timeout — 0 = single scan)"),
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 4))
        irow = tk.Frame(mw_row, bg=T("SURFACE"))
        irow.pack(anchor="w")

        mw_secs = float(self._step.get("max_wait", 0.0))
        val_str, unit_str = _seconds_to_display(mw_secs) if mw_secs > 0 else ("0", "SEC")

        mw_val = tk.Entry(irow, width=8,
                           bg=T("ENTRY_BG"), fg=T("FG"),
                           relief="solid", bd=1,
                           highlightthickness=1,
                           highlightbackground=T("BORDER"),
                           highlightcolor=T("BORDER_STRONG"),
                           font=("Segoe UI", 9), justify="center",
                           insertbackground=T("FG"))
        mw_val.insert(0, val_str)
        mw_val.pack(side="left", padx=(0, 6))
        mw_val.bind("<FocusIn>",  lambda e: mw_val.config(highlightthickness=2))
        mw_val.bind("<FocusOut>", lambda e: mw_val.config(highlightthickness=1))

        mw_unit = tk.StringVar(value=unit_str)
        mw_cb = ttk.Combobox(irow, textvariable=mw_unit,
                              values=[u[0] for u in UNITS],
                              state="readonly", width=5,
                              font=("Segoe UI", 9))
        mw_cb.pack(side="left")
        self._widgets["max_wait"] = (mw_val, mw_unit)

        # ── Divider ───────────────────────────────────────────
        tk.Frame(body, bg=T("BORDER"), height=1).pack(fill="x", pady=(8, 14))

        # ── THEN branch ───────────────────────────────────────
        self._build_branch(body, "then_action",
                            tr("✓  IF FOUND — THEN"),
                            "#27AE60",
                            click_found_label=tr("Click at found position"),
                            stype=stype)

        tk.Frame(body, bg=T("BORDER"), height=1).pack(fill="x", pady=(4, 14))

        # ── ELSE branch ───────────────────────────────────────
        self._build_branch(body, "else_action",
                            tr("✗  IF NOT FOUND — ELSE"),
                            "#E74C3C",
                            click_found_label=None,
                            stype=stype)

        # ── Evrensel Not alanı ────────────────────────────────
        tk.Frame(body, bg=T("BORDER"), height=1).pack(fill="x", pady=(12, 14))
        self._build_note_field(body)

    def _build_branch(self, parent, branch_key, title, accent_color,
                      click_found_label, stype):
        """THEN veya ELSE için aksiyon seçici."""
        # Başlık
        hdr = tk.Frame(parent, bg=accent_color)
        hdr.pack(fill="x", pady=(0, 10))
        tk.Label(hdr, text=f"  {title}",
                  bg=accent_color, fg="#FFFFFF",
                  font=("Segoe UI", 9, "bold"),
                  pady=6).pack(side="left")

        branch_data   = self._step.get(branch_key, {})
        # THEN dalı için varsayılan aksiyon "click_found", ELSE için "none"
        fallback      = "click_found" if (branch_key == "then_action" and click_found_label) else "none"
        atype_default = branch_data.get("type", fallback)

        # Aksiyon tipi seçimi
        atype_row = tk.Frame(parent, bg=T("SURFACE"))
        atype_row.pack(fill="x", pady=(0, 8))

        tk.Label(atype_row, text=tr("ACTION TYPE"),
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 4))

        atype_var = tk.StringVar(value=atype_default)

        # Mevcut aksiyon tipleri
        action_options = []
        if click_found_label:
            action_options.append(("click_found", click_found_label))
        action_options += [
            ("click",   "Click at coordinates"),
            ("key",     "Press a key"),
            ("hotkey",  "Press hotkey combo"),
            ("delay",   "Wait (delay)"),
            ("go_to",   "Go to step N"),
            ("stop",    "Stop automation"),
            ("none",    "Do nothing (skip)"),
        ]

        radio_frame = tk.Frame(atype_row, bg=T("SURFACE"))
        radio_frame.pack(anchor="w")

        for val, lbl in action_options:
            tk.Radiobutton(
                radio_frame, text=tr(lbl),
                variable=atype_var, value=val,
                bg=T("SURFACE"), fg=T("FG"),
                selectcolor=T("CHECK_BG"),
                activebackground=T("SURFACE"),
                activeforeground=T("FG"),
                font=("Segoe UI", 9),
                command=lambda bk=branch_key: self._refresh_branch_detail(bk)
            ).pack(anchor="w", pady=1)

        # Detail frame (aksiyon detayları dinamik)
        detail_frame = tk.Frame(parent, bg=T("SURFACE2"),
                                 relief="solid", bd=1,
                                 highlightthickness=1,
                                 highlightbackground=T("BORDER"))
        detail_frame.pack(fill="x", pady=(4, 0))

        # Widget referansları bu branch için sakla
        branch_widgets = {
            "atype_var":    atype_var,
            "detail_frame": detail_frame,
            "data":         dict(branch_data),
        }
        self._widgets[branch_key] = branch_widgets

        self._refresh_branch_detail(branch_key)

    def _refresh_branch_detail(self, branch_key):
        """Seçilen aksiyon tipine göre detail_frame içeriğini yenile."""
        bw = self._widgets.get(branch_key, {})
        if not isinstance(bw, dict):
            return

        atype_var    = bw.get("atype_var")
        detail_frame = bw.get("detail_frame")
        data         = bw.get("data", {})
        if not atype_var or not detail_frame:
            return

        # Mevcut içeriği temizle
        for w in detail_frame.winfo_children():
            w.destroy()
        bw.pop("detail_widgets", None)

        atype = atype_var.get()
        inner = tk.Frame(detail_frame, bg=T("SURFACE2"))
        inner.pack(fill="x", padx=12, pady=8)
        detail_widgets = {}

        if atype == "click_found":
            tk.Label(inner,
                      text=tr("→ Will click exactly where the match was found."),
                      bg=T("SURFACE2"), fg=T("FG2"),
                      font=("Segoe UI", 8, "italic")).pack(anchor="w")

        elif atype == "click":
            xy_row = tk.Frame(inner, bg=T("SURFACE2"))
            xy_row.pack(anchor="w", pady=(0, 6))

            for lbl, key, default in [("X", "x", "0"), ("Y", "y", "0")]:
                col = tk.Frame(xy_row, bg=T("SURFACE2"))
                col.pack(side="left", padx=(0, 12))
                tk.Label(col, text=tr(lbl),
                          bg=T("SURFACE2"), fg=T("FG2"),
                          font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 3))
                e = tk.Entry(col, width=7,
                              bg=T("ENTRY_BG"), fg=T("FG"),
                              relief="solid", bd=1,
                              highlightthickness=1,
                              highlightbackground=T("BORDER"),
                              highlightcolor=T("BORDER_STRONG"),
                              font=("Segoe UI", 9), justify="center",
                              insertbackground=T("FG"))
                e.insert(0, str(data.get(key, default)))
                e.pack()
                e.bind("<FocusIn>",  lambda ev, w=e: w.config(highlightthickness=2))
                e.bind("<FocusOut>", lambda ev, w=e: w.config(highlightthickness=1))
                detail_widgets[key] = e

            btn_key_var = tk.StringVar(value=data.get("button", "left"))
            btn_row = tk.Frame(inner, bg=T("SURFACE2"))
            btn_row.pack(anchor="w")
            tk.Label(btn_row, text=tr("BUTTON"),
                      bg=T("SURFACE2"), fg=T("FG2"),
                      font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 3))
            rb_row = tk.Frame(btn_row, bg=T("SURFACE2"))
            rb_row.pack(anchor="w")
            for val, lbl in [("left", "LEFT"), ("right", "RIGHT"), ("middle", "MIDDLE")]:
                tk.Radiobutton(rb_row, text=tr(lbl),
                                variable=btn_key_var, value=val,
                                bg=T("SURFACE2"), fg=T("FG"),
                                selectcolor=T("SURFACE"),
                                activebackground=T("SURFACE2"),
                                activeforeground=T("FG"),
                                font=("Segoe UI", 8)).pack(side="left", padx=(0, 10))
            detail_widgets["button"] = btn_key_var

        elif atype == "key":
            tk.Label(inner, text=tr("KEY"),
                      bg=T("SURFACE2"), fg=T("FG2"),
                      font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 3))
            e = tk.Entry(inner, width=18,
                          bg=T("ENTRY_BG"), fg=T("FG"),
                          relief="solid", bd=1,
                          highlightthickness=1,
                          highlightbackground=T("BORDER"),
                          highlightcolor=T("BORDER_STRONG"),
                          font=("Segoe UI", 9),
                          insertbackground=T("FG"))
            e.insert(0, data.get("key", ""))
            e.pack(anchor="w")
            e.bind("<FocusIn>",  lambda ev: e.config(highlightthickness=2))
            e.bind("<FocusOut>", lambda ev: e.config(highlightthickness=1))
            detail_widgets["key"] = e

        elif atype == "hotkey":
            tk.Label(inner, text=tr("HOTKEY  (e.g. ctrl+c, alt+f4)"),
                      bg=T("SURFACE2"), fg=T("FG2"),
                      font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 3))
            e = tk.Entry(inner, width=18,
                          bg=T("ENTRY_BG"), fg=T("FG"),
                          relief="solid", bd=1,
                          highlightthickness=1,
                          highlightbackground=T("BORDER"),
                          highlightcolor=T("BORDER_STRONG"),
                          font=("Segoe UI", 9),
                          insertbackground=T("FG"))
            e.insert(0, data.get("keys", "ctrl+c"))
            e.pack(anchor="w")
            e.bind("<FocusIn>",  lambda ev: e.config(highlightthickness=2))
            e.bind("<FocusOut>", lambda ev: e.config(highlightthickness=1))
            detail_widgets["keys"] = e

        elif atype == "delay":
            tk.Label(inner, text=tr("WAIT (seconds)"),
                      bg=T("SURFACE2"), fg=T("FG2"),
                      font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 3))
            e = tk.Entry(inner, width=10,
                          bg=T("ENTRY_BG"), fg=T("FG"),
                          relief="solid", bd=1,
                          highlightthickness=1,
                          highlightbackground=T("BORDER"),
                          highlightcolor=T("BORDER_STRONG"),
                          font=("Segoe UI", 9), justify="center",
                          insertbackground=T("FG"))
            e.insert(0, str(data.get("duration", "1.0")))
            e.pack(anchor="w")
            e.bind("<FocusIn>",  lambda ev, w=e: w.config(highlightthickness=2))
            e.bind("<FocusOut>", lambda ev, w=e: w.config(highlightthickness=1))
            detail_widgets["duration"] = e

        elif atype == "go_to":
            tk.Label(inner, text=tr("GO TO STEP  (1-based index)"),
                      bg=T("SURFACE2"), fg=T("FG2"),
                      font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 3))
            e = tk.Entry(inner, width=7,
                          bg=T("ENTRY_BG"), fg=T("FG"),
                          relief="solid", bd=1,
                          highlightthickness=1,
                          highlightbackground=T("BORDER"),
                          highlightcolor=T("BORDER_STRONG"),
                          font=("Segoe UI", 9), justify="center",
                          insertbackground=T("FG"))
            e.insert(0, str(data.get("step_index", 1)))
            e.pack(anchor="w")
            e.bind("<FocusIn>",  lambda ev, w=e: w.config(highlightthickness=2))
            e.bind("<FocusOut>", lambda ev, w=e: w.config(highlightthickness=1))
            detail_widgets["step_index"] = e
            tk.Label(inner, text=tr("Step 1 = first step in the list."),
                      bg=T("SURFACE2"), fg=T("FG3"),
                      font=("Segoe UI", 7, "italic")).pack(anchor="w", pady=(4, 0))

        elif atype == "stop":
            tk.Label(inner,
                      text=tr("→ Will stop the automation sequence."),
                      bg=T("SURFACE2"), fg=T("FG2"),
                      font=("Segoe UI", 8, "italic")).pack(anchor="w")

        else:  # none / skip
            tk.Label(inner,
                      text=tr("→ No action — step will be skipped."),
                      bg=T("SURFACE2"), fg=T("FG3"),
                      font=("Segoe UI", 8, "italic")).pack(anchor="w")

        bw["detail_widgets"] = detail_widgets

    def _add_field(self, parent, field_def):
        key   = field_def[0]
        label = tr(field_def[1])
        ftype = field_def[2]
        default = field_def[3]
        opts  = field_def[4] if len(field_def) > 4 else None

        current = self._step.get(key, default)

        row = tk.Frame(parent, bg=T("SURFACE"))
        row.pack(fill="x", pady=(0, 14))

        if ftype == "check":
            # ── Checkbox ──────────────────────────────────
            var = tk.BooleanVar(value=bool(current))
            cb  = tk.Checkbutton(
                row, text=label,
                variable=var,
                bg=T("SURFACE"), fg=T("FG"),
                selectcolor=T("CHECK_BG"),
                activebackground=T("SURFACE"),
                activeforeground=T("FG"),
                font=("Segoe UI", 9)
            )
            cb.pack(anchor="w")
            self._widgets[key] = var
            # click tipinde cursor checkbox → x/y alanlarını disable eder
            if key == "use_cursor":
                self._cursor_var = var
                var.trace_add("write", self._toggle_cursor_fields)

        elif ftype == "radio":
            # ── Radio group ───────────────────────────────
            tk.Label(row, text=label,
                      bg=T("SURFACE"), fg=T("FG2"),
                      font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 4))
            var = tk.StringVar(value=str(current))
            radio_row = tk.Frame(row, bg=T("SURFACE"))
            radio_row.pack(anchor="w")
            for val, lbl in (opts or []):
                tk.Radiobutton(
                    radio_row, text=tr(lbl), variable=var, value=val,
                    bg=T("SURFACE"), fg=T("FG"),
                    selectcolor=T("CHECK_BG"),
                    activebackground=T("SURFACE"),
                    activeforeground=T("FG"),
                    font=("Segoe UI", 9)
                ).pack(side="left", padx=(0, 16))
            self._widgets[key] = var

        elif ftype == "rgb":
            # ── RGB gösterge (sadece okuma, renk seçimi yok) ──
            tk.Label(row, text=label,
                      bg=T("SURFACE"), fg=T("FG2"),
                      font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 4))
            rgb_row = tk.Frame(row, bg=T("SURFACE"))
            rgb_row.pack(anchor="w")
            if isinstance(current, (list, tuple)) and len(current) == 3:
                r, g, b = current
                hex_c = "#{:02X}{:02X}{:02X}".format(r, g, b)
            else:
                r, g, b = 255, 0, 0
                hex_c = "#FF0000"
            swatch = tk.Label(
                rgb_row, width=4, bg=hex_c,
                relief="solid", bd=1)
            swatch.pack(side="left", padx=(0, 8), ipady=6)
            tk.Label(rgb_row, text=f"RGB({r}, {g}, {b})",
                      bg=T("SURFACE"), fg=T("FG"),
                      font=("Segoe UI", 9, "bold")).pack(side="left")
            tk.Label(rgb_row,
                      text=tr("  (Re-add step to change color)"),
                      bg=T("SURFACE"), fg=T("FG3"),
                      font=("Segoe UI", 8)).pack(side="left")
            # RGB sadece gösterim, kaydederken orijinal değer kullanılır
            self._widgets[key] = None

        elif ftype == "interval":
            # ── Interval widget ───────────────────────────
            tk.Label(row, text=label,
                      bg=T("SURFACE"), fg=T("FG2"),
                      font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 4))
            irow = tk.Frame(row, bg=T("SURFACE"))
            irow.pack(anchor="w")

            val_str, unit_str = _seconds_to_display(
                float(current) if not isinstance(current, (list, tuple)) else 0.1)

            val_e = tk.Entry(
                irow, width=8,
                bg=T("ENTRY_BG"), fg=T("FG"),
                relief="solid", bd=1,
                highlightthickness=1,
                highlightbackground=T("BORDER"),
                highlightcolor=T("BORDER_STRONG"),
                font=("Segoe UI", 9), justify="center",
                insertbackground=T("FG")
            )
            val_e.insert(0, val_str)
            val_e.pack(side="left", padx=(0, 6))
            val_e.bind("<FocusIn>",
                lambda e, w=val_e: w.config(highlightthickness=2))
            val_e.bind("<FocusOut>",
                lambda e, w=val_e: w.config(highlightthickness=1))

            unit_var = tk.StringVar(value=unit_str)
            unit_cb  = ttk.Combobox(
                irow, textvariable=unit_var,
                values=[u[0] for u in UNITS],
                state="readonly", width=5,
                font=("Segoe UI", 9)
            )
            unit_cb.pack(side="left")
            self._widgets[key] = (val_e, unit_var)

        else:
            # ── Text / int / float entry ──────────────────
            tk.Label(row, text=label,
                      bg=T("SURFACE"), fg=T("FG2"),
                      font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 4))
            entry = tk.Entry(
                row, width=24,
                bg=T("ENTRY_BG"), fg=T("FG"),
                relief="solid", bd=1,
                highlightthickness=1,
                highlightbackground=T("BORDER"),
                highlightcolor=T("BORDER_STRONG"),
                font=("Segoe UI", 9),
                insertbackground=T("FG")
            )
            entry.insert(0, str(current))
            entry.pack(anchor="w")
            entry.bind("<FocusIn>",
                lambda e, w=entry: w.config(highlightthickness=2))
            entry.bind("<FocusOut>",
                lambda e, w=entry: w.config(highlightthickness=1))
            self._widgets[key] = entry

            # x/y entry referanslarını sakla → cursor toggle için
            if key == "x":
                self._x_entry = entry
            elif key == "y":
                self._y_entry = entry

        # İlk kurulumda cursor durumunu uygula
        if key == "use_cursor":
            self._toggle_cursor_fields()

    def _build_note_field(self, parent):
        """Her adıma ait kullanıcı notu için metin alanı — tüm tipler için."""
        note_frame = tk.Frame(parent, bg=T("SURFACE"))
        note_frame.pack(fill="x", pady=(12, 4))

        hdr = tk.Frame(note_frame, bg=T("SURFACE"))
        hdr.pack(fill="x", pady=(0, 4))
        tk.Label(hdr, text=tr("📝  NOTE"),
                 bg=T("SURFACE"), fg=T("FG2"),
                 font=("Segoe UI", 8, "bold")).pack(side="left")
        tk.Label(hdr, text=tr("  (optional — briefly describe what this step does)"),
                 bg=T("SURFACE"), fg=T("FG3"),
                 font=("Segoe UI", 7, "italic")).pack(side="left")

        note_entry = tk.Entry(
            note_frame, width=42,
            bg=T("ENTRY_BG"), fg=T("FG"),
            relief="solid", bd=1,
            highlightthickness=1,
            highlightbackground=T("BORDER"),
            highlightcolor=T("BORDER_STRONG"),
            font=("Segoe UI", 9),
            insertbackground=T("FG")
        )
        note_entry.insert(0, self._step.get("note", ""))
        note_entry.pack(fill="x", anchor="w")
        note_entry.bind("<FocusIn>",  lambda e: note_entry.config(highlightthickness=2))
        note_entry.bind("<FocusOut>", lambda e: note_entry.config(highlightthickness=1))
        self._widgets["note"] = note_entry

    def _toggle_cursor_fields(self, *_):
        """use_cursor aktifse x/y giriş alanlarını devre dışı bırak."""
        if self._cursor_var is None:
            return
        use = self._cursor_var.get()
        state = "disabled" if use else "normal"
        for attr in ("_x_entry", "_y_entry"):
            w = getattr(self, attr, None)
            if w:
                w.config(state=state)

    # ── Save ─────────────────────────────────────────────────────────────────

    def _save(self):
        updated = dict(self._step)  # orijinali koru, üzerine yaz
        stype   = updated.get("type", "key")

        if stype in ("if_color", "if_image"):
            # max_wait
            mw = self._widgets.get("max_wait")
            if mw:
                val_e, unit_var = mw
                updated["max_wait"] = _get_seconds(val_e.get().strip(), unit_var.get())

            # THEN / ELSE branches
            for branch_key in ("then_action", "else_action"):
                bw = self._widgets.get(branch_key)
                if not isinstance(bw, dict):
                    continue
                atype_var = bw.get("atype_var")
                dw        = bw.get("detail_widgets", {})
                if not atype_var:
                    continue
                atype = atype_var.get()
                action = {"type": atype}

                if atype == "click":
                    try:
                        action["x"] = int(dw["x"].get()) if dw.get("x") else 0
                        action["y"] = int(dw["y"].get()) if dw.get("y") else 0
                    except Exception:
                        action["x"] = 0
                        action["y"] = 0
                    btn_var = dw.get("button")
                    action["button"] = btn_var.get() if btn_var else "left"
                elif atype == "key":
                    key_w = dw.get("key")
                    action["key"] = key_w.get().strip() if key_w else ""
                elif atype == "hotkey":
                    keys_w = dw.get("keys")
                    action["keys"] = keys_w.get().strip() if keys_w else "ctrl+c"
                elif atype == "delay":
                    dur_w = dw.get("duration")
                    try:
                        action["duration"] = float(dur_w.get()) if dur_w else 1.0
                    except ValueError:
                        action["duration"] = 1.0
                elif atype == "go_to":
                    idx_w = dw.get("step_index")
                    try:
                        action["step_index"] = max(1, int(idx_w.get())) if idx_w else 1
                    except ValueError:
                        action["step_index"] = 1

                updated[branch_key] = action

        else:
            fields = FIELDS.get(stype, [])
            for field_def in fields:
                key   = field_def[0]
                ftype = field_def[2]
                w     = self._widgets.get(key)

                if w is None:
                    continue  # rgb gibi sadece gösterim alanları

                try:
                    if ftype == "check":
                        updated[key] = w.get()

                    elif ftype == "radio":
                        updated[key] = w.get()

                    elif ftype == "interval":
                        val_e, unit_var = w
                        updated[key] = _get_seconds(
                            val_e.get().strip(), unit_var.get())

                    elif ftype == "int_entry":
                        raw = w.get().strip()
                        updated[key] = int(raw) if raw else 0

                    elif ftype == "float_entry":
                        raw = w.get().strip()
                        updated[key] = float(raw) if raw else 0.0

                    else:  # plain entry
                        updated[key] = w.get().strip()

                except Exception as e:
                    print(f"[StepEditDialog] save field '{key}' error: {e}")

        # Not alanını her tip için kaydet
        note_w = self._widgets.get("note")
        if note_w is not None:
            try:
                updated["note"] = note_w.get().strip()
            except Exception:
                pass

        self._on_save(updated)
        self._win.destroy()

    # ── Center ───────────────────────────────────────────────────────────────

    def _center(self, parent):
        self._win.update_idletasks()
        stype = self._step.get("type", "key")

        try:
            rx = parent.winfo_rootx()
            ry = parent.winfo_rooty()
            rw = parent.winfo_width()
            rh = parent.winfo_height()
        except Exception:
            rx, ry, rw, rh = 200, 100, 800, 600

        if stype in ("if_color", "if_image"):
            try:
                screen_h = self._win.winfo_screenheight()
                screen_w = self._win.winfo_screenwidth()
            except Exception:
                screen_h, screen_w = 900, 1440

            min_w   = 520
            min_h   = 400
            max_h   = int(screen_h * 0.85)
            nat_w   = self._win.winfo_reqwidth()
            nat_h   = self._win.winfo_reqheight()
            final_w = max(min_w, min(nat_w, int(screen_w * 0.50)))
            final_h = max(min_h, min(nat_h, max_h))
            self._win.minsize(min_w, min_h)

            # Konumu hesapla
            sx = max(0, rx + rw // 2 - final_w // 2)
            sy = max(0, ry + rh // 2 - final_h // 2)
            self._win.geometry(f"{final_w}x{final_h}+{sx}+{sy}")
        else:
            pw = self._win.winfo_reqwidth()
            ph = self._win.winfo_reqheight()
            sx = max(0, rx + rw // 2 - pw // 2)
            sy = max(0, ry + rh // 2 - ph // 2)
            self._win.geometry(f"+{sx}+{sy}")
