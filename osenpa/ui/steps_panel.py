"""
steps_panel.py — Osenpa Auto Clicker step list panel.

Yeni özellikler (v2):
  • Sürükle-bırak sıralama (drag-and-drop)
  • Çoklu seçim: Ctrl+Click / Shift+Click + toplu SİL / KOPYALA
  • Adım kopyalama (DUPLICATE)
  • Tam Undo/Redo geçmişi (Ctrl+Z / Ctrl+Y / Ctrl+Shift+Z)
  • Active step highlight — shows which step is running during automation
  • Start step selection — "Run From Step N"
  • Timeout field for color/image steps (via step_edit_dialog)
  • Tooltip desteği — her buton ve label için açıklama
  • Step notes — user-defined note for each step
"""

import tkinter as tk
import copy
from ui.theme import make_btn, make_icon_btn, T
from ui.step_edit_dialog import StepEditDialog
from utils.i18n import tr


# ── Format yardımcısı ─────────────────────────────────────────────────────────

def _branch_label(action: dict) -> str:
    """Short readable label for a THEN/ELSE action."""
    t = action.get("type", "none")
    if t == "go_to":
        n = action.get("step_index", "?")
        return f"GOTO#{n}"
    if t == "delay":
        d = action.get("duration", 1.0)
        return f"WAIT{d}s"
    return t.upper()

def _fmt(seconds):
    ms = int(round(seconds * 1000))
    if ms < 1000:  return f"{ms}MS"
    if ms < 60000: return f"{seconds:.1f}S"
    m = int(seconds // 60)
    return f"{m}M{int(seconds % 60)}S"


TYPE_LABELS = {
    "key":      "KEY",
    "hotkey":   "HOTKEY",
    "click":    "CLICK",
    "drag":     "DRAG",
    "scroll":   "SCROLL",
    "color":    "COLOR",
    "image":    "IMAGE",
    "delay":    "DELAY",
    "if_color": "IF COLOR",
    "if_image": "IF IMAGE",
}

# Short default note for each step type
_DEFAULT_NOTES = {
    "key":      "Press a key (e.g. Enter or A).",
    "hotkey":   "Press multiple keys at once (e.g. Ctrl+C to copy).",
    "click":    "Click the mouse at a position.",
    "drag":     "Drag the mouse from one position to another.",
    "scroll":   "Scroll the mouse wheel up or down.",
    "color":    "Scan for a color on screen and click when found.",
    "image":    "Scan for an image on screen and click when found.",
    "delay":    "Wait before moving to the next step.",
    "if_color": "Check if a color is present; do different things based on result.",
    "if_image": "Check if an image is present; do different things based on result.",
}


# ── Tooltip ───────────────────────────────────────────────────────────────────

class _Tooltip:
    """Shows a short tooltip when hovering over the widget."""

    _DELAY = 600   # ms — ne kadar bekledikten sonra çıksın

    def __init__(self, widget, text: str):
        self._widget = widget
        self._text   = text
        self._tip    = None
        self._job    = None
        widget.bind("<Enter>",  self._on_enter, add="+")
        widget.bind("<Leave>",  self._on_leave, add="+")
        widget.bind("<Destroy>", self._on_leave, add="+")

    def _on_enter(self, e=None):
        self._job = self._widget.after(self._DELAY, self._show)

    def _on_leave(self, e=None):
        if self._job:
            self._widget.after_cancel(self._job)
            self._job = None
        if self._tip:
            try:
                self._tip.destroy()
            except Exception:
                pass
            self._tip = None

    def _show(self):
        if not self._text:
            return
        try:
            x = self._widget.winfo_rootx() + self._widget.winfo_width() // 2
            y = self._widget.winfo_rooty() + self._widget.winfo_height() + 4
            self._tip = tk.Toplevel(self._widget)
            self._tip.wm_overrideredirect(True)
            self._tip.wm_geometry(f"+{x}+{y}")
            self._tip.attributes("-topmost", True)
            frame = tk.Frame(self._tip,
                             bg=T("PRIMARY_BG"),
                             relief="solid", bd=1,
                             highlightthickness=1,
                             highlightbackground=T("BORDER"))
            frame.pack()
            tk.Label(frame,
                     text=self._text,
                     bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
                     font=("Segoe UI", 8),
                     padx=8, pady=4,
                     wraplength=280, justify="left"
                     ).pack()
        except Exception:
            pass


def _tip(widget, text: str) -> _Tooltip:
    """Kısa yardımcı — widget'a tooltip ekle."""
    return _Tooltip(widget, text)


# ── Undo/Redo geçmiş kaydı ────────────────────────────────────────────────────

class _HistoryEntry:
    """Tek bir geri alınabilir eylem."""
    __slots__ = ("label", "before", "after")

    def __init__(self, label: str, before: list, after: list):
        self.label  = label
        self.before = before   # deep copy of steps list before action
        self.after  = after    # deep copy after


# ── StepsPanel ────────────────────────────────────────────────────────────────

class StepsPanel:
    _HISTORY_LIMIT = 50   # Maksimum undo geçmişi derinliği
    _UNDO_LIMIT    = 20   # Eski slot uyumluluğu (clear için)

    def __init__(self, parent, steps, on_export, on_import,
                 on_add_step=None, on_run_from=None):
        self.steps       = steps
        self.on_export   = on_export
        self.on_import   = on_import
        self.on_add_step = on_add_step
        self.on_run_from = on_run_from   # (start_index) -> None

        # Undo/Redo stacks
        self._undo_history: list[_HistoryEntry] = []
        self._redo_history: list[_HistoryEntry] = []

        # Active step highlight (during automation)
        self._active_step_idx: int = -1

        # Sürükle-bırak durumu
        self._drag_start_idx: int = -1

        # Filtre-steps index mapping (refresh() tarafından doldurulur)
        self._visible_indices: list[int] = []

        # Undo bar job
        self._undo_job = None

        # Seçim modu (normal/multi)
        self._multi_sel: list[int] = []

        self._build(parent)

    # ── UI inşası ─────────────────────────────────────────────────────────────

    def _build(self, parent):
        self._parent = parent
        outer = tk.Frame(parent, bg=T("SURFACE"))
        outer.pack(fill="both", expand=True)
        self._outer = outer

        # ── Header ──────────────────────────────────────────────
        header = tk.Frame(outer, bg=T("SURFACE"))
        header.pack(fill="x", padx=16, pady=(16, 8))

        left_h = tk.Frame(header, bg=T("SURFACE"))
        left_h.pack(side="left", fill="x", expand=True)

        tk.Label(left_h, text=tr("AUTOMATION STEPS"),
                 bg=T("SURFACE"), fg=T("FG"),
                 font=("Segoe UI", 10, "bold")).pack(side="left")

        self.count_lbl = tk.Label(
            left_h, text=" 0 ",
            bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
            font=("Segoe UI", 8, "bold"),
            padx=4, pady=1
        )
        self.count_lbl.pack(side="left", padx=(8, 0))
        _tip(self.count_lbl, tr("Total step count"))

        right_h = tk.Frame(header, bg=T("SURFACE"))
        right_h.pack(side="right")

        exp_btn = make_btn(right_h, tr("EXPORT"), self.on_export, small=True)
        exp_btn.pack(side="left", padx=(0, 4))
        _tip(exp_btn, tr("Export steps to file (JSON / CSV / TXT)"))

        imp_btn = make_btn(right_h, tr("IMPORT"), self.on_import, small=True)
        imp_btn.pack(side="left", padx=(0, 8))
        _tip(imp_btn, tr("Import previously saved steps"))

        clr_btn = make_btn(right_h, tr("CLEAR ALL"), self._clear, danger=True)
        clr_btn.pack(side="left")
        _tip(clr_btn, tr("Clear all steps (asks for confirmation)"))

        # ── Kontroller ───────────────────────────────────────────
        ctrl_row = tk.Frame(outer, bg=T("SURFACE"))
        ctrl_row.pack(fill="x", padx=16, pady=(0, 4))

        self.up_btn   = make_icon_btn(ctrl_row, "▲", self._move_up)
        self.down_btn = make_icon_btn(ctrl_row, "▼", self._move_down)
        self.edit_btn = make_icon_btn(ctrl_row, tr("EDIT"),   self._edit)
        self.dup_btn  = make_icon_btn(ctrl_row, tr("COPY"),   self._duplicate)
        self.del_btn  = make_icon_btn(ctrl_row, tr("REMOVE"), self._delete)

        for btn, tip_text in [
            (self.up_btn,   tr("Move step up  (or drag and drop)")),
            (self.down_btn, tr("Move step down")),
            (self.edit_btn, tr("Edit selected step")),
            (self.dup_btn,  tr("Duplicate selected step")),
            (self.del_btn,  tr("Delete selected step  (Ctrl+Z to undo)")),
        ]:
            btn.pack(side="left", padx=(0, 4))
            _tip(btn, tip_text)

        # Undo/Redo butonları
        sep = tk.Frame(ctrl_row, bg=T("BORDER"), width=1)
        sep.pack(side="left", fill="y", padx=(4, 8), pady=2)

        self._undo_btn = make_icon_btn(ctrl_row, tr("↩ UNDO"), self._undo)
        self._redo_btn = make_icon_btn(ctrl_row, tr("↪ REDO"), self._redo)
        self._undo_btn.pack(side="left", padx=(0, 4))
        self._redo_btn.pack(side="left", padx=(0, 4))
        _tip(self._undo_btn, tr("Undo last change  (Ctrl+Z)"))
        _tip(self._redo_btn, tr("Redo the last undone change  (Ctrl+Y)"))

        # Run From Step — in its own frame on the right, never shrinks
        right_ctrl = tk.Frame(ctrl_row, bg=T("SURFACE"))
        right_ctrl.pack(side="right", fill="y")

        tk.Frame(right_ctrl, bg=T("BORDER"), width=1).pack(
            side="left", fill="y", padx=(4, 8), pady=2)

        self._run_from_btn = make_btn(
            right_ctrl, tr("▶  FROM HERE"), self._run_from_selected, small=True)
        self._run_from_btn.pack(side="left", pady=2)
        _tip(self._run_from_btn,
             tr("Run automation from this step\n") +
             tr("(to run from the middle, not the beginning)"))

        # ── Quick Delay Add ──────────────────────────────────────
        delay_row = tk.Frame(outer, bg=T("SURFACE"))
        delay_row.pack(fill="x", padx=16, pady=(0, 6))

        delay_lbl = tk.Label(delay_row, text=tr("QUICK ADD"),
                             bg=T("SURFACE"), fg=T("FG3"),
                             font=("Segoe UI", 7, "bold"))
        delay_lbl.pack(side="left", padx=(0, 8))
        _tip(delay_lbl, tr("Add a quick delay step"))

        for dur_label, dur_sec in [("0.5s", 0.5), ("1s", 1.0), ("2s", 2.0), ("5s", 5.0)]:
            b = make_btn(delay_row, f"⏱ {dur_label}",
                         lambda s=dur_sec: self._add_delay_quick(s),
                         small=True)
            b.pack(side="left", padx=(0, 4))
            # We can construct the translated tip directly
            _tip(b, tr("Add a {}s delay step").format(dur_sec))

        cust = make_btn(delay_row, tr("CUSTOM DELAY"), self._add_delay_custom, small=True)
        cust.pack(side="left", padx=(4, 0))
        _tip(cust, tr("Add a custom delay step"))

        # ── Arama ────────────────────────────────────────────────
        search_frame = tk.Frame(outer, bg=T("SURFACE"))
        search_frame.pack(fill="x", padx=16, pady=(0, 0))

        tk.Label(search_frame, text=tr("SEARCH"),
                 bg=T("SURFACE"), fg=T("FG3"),
                 font=("Segoe UI", 7, "bold")).pack(anchor="w", pady=(0, 4))

        search_inner = tk.Frame(
            search_frame,
            bg=T("ENTRY_BG"),
            relief="solid", bd=1,
            highlightthickness=1,
            highlightbackground=T("BORDER"),
        )
        search_inner.pack(fill="x")

        self._search_entry = tk.Entry(
            search_inner,
            bg=T("ENTRY_BG"), fg=T("FG2"),
            relief="flat", bd=0,
            highlightthickness=0,
            font=("Segoe UI", 9),
            insertbackground=T("FG")
        )
        self._search_entry.pack(fill="x", expand=True, pady=5, padx=8)
        self._search_entry.insert(0, tr("Search steps..."))
        _tip(self._search_entry, tr("Filter step list — searches by type, detail or note"))

        def on_fi(e):
            if self._search_entry.get() == tr("Search steps..."):
                self._search_entry.delete(0, tk.END)
                self._search_entry.config(fg=T("FG"))
            search_inner.config(highlightbackground=T("BORDER_STRONG"), highlightthickness=2)

        def on_fo(e):
            if self._search_entry.get() == "":
                self._search_entry.insert(0, tr("Search steps..."))
                self._search_entry.config(fg=T("FG2"))
            search_inner.config(highlightbackground=T("BORDER"), highlightthickness=1)

        self._search_entry.bind("<FocusIn>",  on_fi)
        self._search_entry.bind("<FocusOut>", on_fo)
        self._search_entry.bind("<KeyRelease>", lambda e: self.refresh())

        tk.Frame(outer, bg=T("BORDER"), height=1).pack(fill="x", pady=(10, 0))

        # ── Liste ─────────────────────────────────────────────────
        self._list_frame = tk.Frame(outer, bg=T("SURFACE"))
        self._list_frame.pack(fill="both", expand=True)

        # Empty state
        self._empty_frame = tk.Frame(self._list_frame, bg=T("SURFACE"))

        tk.Label(self._empty_frame, text=tr("NO STEPS"),
                 bg=T("SURFACE"), fg=T("FG"),
                 font=("Segoe UI", 14, "bold")).pack(pady=(0, 6))

        tk.Label(self._empty_frame,
                 text=tr("Select a tool and click\nADD TO STEPS to begin."),
                 bg=T("SURFACE"), fg=T("FG2"),
                 font=("Segoe UI", 9), justify="center").pack(pady=(0, 16))

        make_btn(self._empty_frame, tr("LOAD EXAMPLE TEMPLATE"),
                 self._load_example, small=True).pack()

        # Listbox + Scrollbar
        lb_outer = tk.Frame(self._list_frame, bg=T("SURFACE"))
        lb_outer.pack(fill="both", expand=True)

        sb = tk.Scrollbar(lb_outer, orient="vertical",
                          bg=T("SCROLL_BG"), troughcolor=T("SCROLL_BG"),
                          activebackground=T("SCROLL_ACTIVE"),
                          relief="flat", bd=0, width=10)
        self._steps_sb = sb

        self.listbox = tk.Listbox(
            lb_outer,
            font=("Segoe UI", 9),
            bg=T("SURFACE"), fg=T("FG"),
            selectbackground=T("PRIMARY_BG"),
            selectforeground=T("PRIMARY_FG"),
            relief="flat", bd=0,
            yscrollcommand=self._steps_scroll_handler,
            activestyle="none",
            highlightthickness=0,
            selectmode=tk.EXTENDED   # Ctrl+Click / Shift+Click çoklu seçim
        )
        sb.config(command=self.listbox.yview)
        self.listbox.pack(fill="both", expand=True, padx=8, pady=4)

        # Çift tıklama → düzenle
        self.listbox.bind("<Double-Button-1>", lambda e: self._edit())

        # Sürükle-bırak
        self.listbox.bind("<ButtonPress-1>",   self._on_drag_start)
        self.listbox.bind("<B1-Motion>",       self._on_drag_motion)
        self.listbox.bind("<ButtonRelease-1>", self._on_drag_release)

        # Klavye kısayolları
        self.listbox.bind("<Delete>",         lambda e: self._delete())
        self.listbox.bind("<Control-z>",      lambda e: self._undo())
        self.listbox.bind("<Control-y>",      lambda e: self._redo())
        self.listbox.bind("<Control-Z>",      lambda e: self._redo())   # Shift+Z
        self.listbox.bind("<Control-d>",      lambda e: self._duplicate())
        self.listbox.bind("<Control-a>",      lambda e: self._select_all())

        # Undo bar (mevcut tasarımla uyumlu, turuncu / uyarı rengi)
        self._undo_bar = tk.Frame(outer, bg="#E67E22")
        undo_inner = tk.Frame(self._undo_bar, bg="#E67E22")
        undo_inner.pack(fill="x", padx=16, pady=8)
        self._undo_lbl = tk.Label(
            undo_inner, text="",
            bg="#E67E22", fg="#FFFFFF",
            font=("Segoe UI", 9)
        )
        self._undo_lbl.pack(side="left")
        tk.Button(
            undo_inner, text="UNDO  ↩",
            command=self._undo,
            bg="#FFFFFF", fg="#E67E22",
            font=("Segoe UI", 9, "bold"),
            relief="flat", padx=10, pady=2,
            cursor="hand2"
        ).pack(side="right", padx=(8, 0))
        tk.Button(
            undo_inner, text="✕",
            command=self._hide_undo_bar,
            bg="#E67E22", fg="#FFFFFF",
            font=("Segoe UI", 9),
            relief="flat", padx=4, pady=2,
            cursor="hand2"
        ).pack(side="right")

        self.refresh()
        self._bind_global_shortcuts(parent)

    def _bind_global_shortcuts(self, parent):
        """Ana pencereye Ctrl+Z/Y kısayollarını bağla."""
        try:
            root = parent.winfo_toplevel()
            root.bind("<Control-z>", lambda e: self._undo(), add="+")
            root.bind("<Control-y>", lambda e: self._redo(), add="+")
            root.bind("<Control-Z>", lambda e: self._redo(), add="+")
        except Exception:
            pass

    # ── Scrollbar ─────────────────────────────────────────────────────────────

    def _steps_scroll_handler(self, first, last):
        self._steps_sb.set(first, last)
        try:
            if float(first) <= 0.0 and float(last) >= 1.0:
                self._steps_sb.pack_forget()
            else:
                if not self._steps_sb.winfo_ismapped():
                    self._steps_sb.pack(side="right", fill="y", before=self.listbox)
        except Exception:
            pass

    # ── Sürükle-bırak ─────────────────────────────────────────────────────────

    def _on_drag_start(self, event):
        lb_idx = self.listbox.nearest(event.y)
        vis = getattr(self, "_visible_indices", None)
        if vis and 0 <= lb_idx < len(vis):
            self._drag_start_idx = vis[lb_idx]
        elif 0 <= lb_idx < len(self.steps):
            self._drag_start_idx = lb_idx
        else:
            self._drag_start_idx = -1

    def _on_drag_motion(self, event):
        if self._drag_start_idx < 0:
            return
        # Hedef satırı göster — renk değiştirerek
        cur = self.listbox.nearest(event.y)
        if 0 <= cur < self.listbox.size():
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(cur)

    def _on_drag_release(self, event):
        if self._drag_start_idx < 0:
            return
        lb_target = self.listbox.nearest(event.y)
        src       = self._drag_start_idx
        self._drag_start_idx = -1

        vis = getattr(self, "_visible_indices", None)
        if vis and 0 <= lb_target < len(vis):
            target = vis[lb_target]
        else:
            target = lb_target

        if target < 0 or target >= len(self.steps) or target == src:
            return
        self._snapshot("Move step")
        step = self.steps.pop(src)
        self.steps.insert(target, step)
        self.refresh()
        # Yeni listbox indexini bul
        new_vis = getattr(self, "_visible_indices", None)
        if new_vis and target in new_vis:
            new_lb = new_vis.index(target)
        else:
            new_lb = target
        self.listbox.selection_set(new_lb)
        self.listbox.see(new_lb)

    # ── Örnek veri ────────────────────────────────────────────────────────────

    def _load_example(self):
        self._snapshot("Load example")
        self.steps.extend([
            {"type": "hotkey", "keys": "ctrl+c",
             "interval": 0.1, "repeat": 1,
             "note": "Seçili metni kopyalar (Ctrl+C)"},
            {"type": "click", "x": 500, "y": 300,
             "button": "left", "interval": 0.5, "repeat": 1,
             "note": "Click the center of the screen"},
            {"type": "hotkey", "keys": "ctrl+v",
             "interval": 0.1, "repeat": 1,
             "note": "Paste copied content (Ctrl+V)"},
        ])
        self.refresh()

    # ── Filtre ────────────────────────────────────────────────────────────────

    def _get_filter(self):
        raw = self._search_entry.get()
        return "" if raw == tr("Search steps...") else raw.lower().strip()

    # ── Refresh ───────────────────────────────────────────────────────────────

    def refresh(self):
        self.listbox.delete(0, tk.END)
        self._visible_indices = []   # listbox_index → real steps_index mapping
        flt   = self._get_filter()
        count = len(self.steps)

        for i, step in enumerate(self.steps):
            stype  = step.get("type", "")
            iv     = _fmt(step.get("interval", 0.1))
            rep    = step.get("repeat", 1)
            lbl    = tr(TYPE_LABELS.get(stype, stype.upper()))
            note   = step.get("note", "").strip()

            if stype == "key":
                detail = step.get("key", "").upper()
            elif stype == "hotkey":
                detail = step.get("keys", "").upper()
            elif stype == "click":
                pos = "CURSOR" if step.get("use_cursor") else \
                    f"X:{step.get('x',0)} Y:{step.get('y',0)}"
                detail = f"{pos} {step.get('button','').upper()}"
            elif stype == "color":
                rgb = step.get("rgb", [0, 0, 0])
                to  = step.get("timeout", 0)
                detail = f"RGB({rgb[0]},{rgb[1]},{rgb[2]})" + (f" ⏱{to}s" if to else "")
            elif stype == "image":
                p = step.get("image_path") or "CLIPBOARD"
                to = step.get("timeout", 0)
                detail = p.split("/")[-1].split("\\")[-1].upper() + (f" ⏱{to}s" if to else "")
            elif stype == "if_color":
                rgb = step.get("rgb", [0, 0, 0])
                then_a = step.get("then_action", {})
                else_a = step.get("else_action", {})
                then_t = _branch_label(then_a)
                else_t = _branch_label(else_a)
                detail = f"RGB({rgb[0]},{rgb[1]},{rgb[2]}) → {then_t}/{else_t}"
            elif stype == "if_image":
                img_list  = step.get("image_list", [])
                img_count = len(img_list) if img_list else 1
                then_a = step.get("then_action", {})
                else_a = step.get("else_action", {})
                then_t = _branch_label(then_a)
                else_t = _branch_label(else_a)
                noun = "IMG" if img_count == 1 else f"{img_count}IMGS"
                detail = f"{noun} → {then_t}/{else_t}"
            elif stype == "delay":
                dur = step.get("duration", 1.0)
                lbl = step.get("label", "").strip()
                detail = (f"{lbl}  " if lbl else "") + _fmt(dur)
            elif stype == "scroll":
                dy = step.get("dy", 0)
                detail = f"{'↑' if dy > 0 else '↓'}{abs(dy)} @ ({step.get('x',0)},{step.get('y',0)})"
            else:
                detail = stype.upper()

            # Not göstergesi
            note_icon = " 📝" if note else ""

            if stype == "delay":
                row = f"  {i+1:02d}.  {lbl:<8}  {detail}{note_icon}"
            elif stype in ("if_color", "if_image"):
                row = f"  {i+1:02d}.  ❯ {tr(TYPE_LABELS.get(stype,'IF')):<10}  {detail}{note_icon}"
            else:
                row = (f"  {i+1:02d}.  {tr(TYPE_LABELS.get(stype,stype.upper())):<8}  {detail:<20}"
                       f"  x{rep}  {iv}{note_icon}")

            if flt and flt not in row.lower() and flt not in note.lower():
                continue

            self._visible_indices.append(i)
            self.listbox.insert(tk.END, row)

            # Renk kodlaması
            if i == self._active_step_idx:
                # Active (running) step — highlighted
                self.listbox.itemconfig(
                    tk.END,
                    bg=T("COND_TRUE"), fg="#FFFFFF",
                    selectbackground=T("COND_TRUE"),
                    selectforeground="#FFFFFF"
                )
            elif stype in ("if_color", "if_image"):
                self.listbox.itemconfig(
                    tk.END,
                    bg=T("SURFACE2"), fg=T("FG"),
                    selectbackground=T("PRIMARY_BG"),
                    selectforeground=T("PRIMARY_FG")
                )
            elif stype == "delay":
                self.listbox.itemconfig(
                    tk.END,
                    bg=T("SURFACE"), fg=T("FG2"),
                    selectbackground=T("PRIMARY_BG"),
                    selectforeground=T("PRIMARY_FG")
                )

        # Badge
        self.count_lbl.config(text=f" {count} ")
        # Undo/Redo buton durumu
        self._update_undo_redo_state()

        if count == 0:
            self._empty_frame.place(relx=0.5, rely=0.42, anchor="center")
            self.listbox.pack_forget()
        else:
            self._empty_frame.place_forget()
            if not self.listbox.winfo_ismapped():
                self.listbox.pack(fill="both", expand=True, padx=8, pady=4)

    # ── Active step highlight (during automation) ────────────────────────────

    def set_active_step(self, idx: int):
        """Called by the automation engine — marks which step is running."""
        old = self._active_step_idx
        self._active_step_idx = idx
        if old != idx:
            try:
                self._parent.after(0, self._do_highlight, idx)
            except Exception:
                pass

    def _do_highlight(self, idx):
        self.refresh()
        # idx = steps index; listbox index'e çevir
        vis = getattr(self, "_visible_indices", None)
        if vis and idx in vis:
            lb_idx = vis.index(idx)
            self.listbox.see(lb_idx)
        elif 0 <= idx < self.listbox.size():
            self.listbox.see(idx)

    # ── Çoklu seçim yardımcıları ──────────────────────────────────────────────

    def _get_selection(self) -> list[int]:
        """Seçili listbox indekslerini gerçek steps index'e çevirir."""
        vis = getattr(self, "_visible_indices", None)
        sel = list(self.listbox.curselection())
        if vis is None:
            return sel
        return [vis[lb_i] for lb_i in sel if lb_i < len(vis)]

    def _select_all(self):
        self.listbox.selection_set(0, tk.END)

    # ── Undo/Redo ─────────────────────────────────────────────────────────────

    def _snapshot(self, label: str):
        """Snapshot the current step list — call BEFORE the operation."""
        entry = _HistoryEntry(
            label=label,
            before=copy.deepcopy(self.steps),
            after=[]   # after işlemden sonra doldurulur
        )
        self._undo_history.append(entry)
        if len(self._undo_history) > self._HISTORY_LIMIT:
            self._undo_history.pop(0)
        # Yeni eylem → redo geçmişini temizle
        self._redo_history.clear()

    def _commit(self):
        """Son snapshot'ın 'after' alanını doldur."""
        if self._undo_history:
            self._undo_history[-1].after = copy.deepcopy(self.steps)

    def _undo(self):
        if not self._undo_history:
            return
        entry = self._undo_history.pop()
        # Redo'ya ekle
        entry_redo = _HistoryEntry(entry.label, entry.after or copy.deepcopy(self.steps), entry.before)
        self._redo_history.append(entry_redo)
        # Geri yükle
        self.steps.clear()
        self.steps.extend(copy.deepcopy(entry.before))
        self.refresh()
        self._show_undo_bar(tr("↩  Undone: {}").format(tr(entry.label)))

    def _redo(self):
        if not self._redo_history:
            return
        entry = self._redo_history.pop()
        undo_entry = _HistoryEntry(entry.label, entry.after or copy.deepcopy(self.steps), entry.before)
        self._undo_history.append(undo_entry)
        self.steps.clear()
        self.steps.extend(copy.deepcopy(entry.before))
        self.refresh()
        self._show_undo_bar(tr("↪  Redone: {}").format(tr(entry.label)))

    def _update_undo_redo_state(self):
        try:
            self._undo_btn.config(state="normal" if self._undo_history else "disabled")
            self._redo_btn.config(state="normal" if self._redo_history else "disabled")
        except Exception:
            pass

    def _show_undo_bar(self, msg: str = ""):
        if self._undo_job:
            self._parent.after_cancel(self._undo_job)
        try:
            self._undo_lbl.config(text=msg or tr("Change made."))
            self._undo_bar.pack(fill="x", side="bottom")
            self._undo_job = self._parent.after(6000, self._hide_undo_bar)
        except Exception:
            pass

    def _hide_undo_bar(self):
        try:
            self._undo_bar.pack_forget()
        except Exception:
            pass
        self._undo_job = None

    # ── Adım işlemleri ────────────────────────────────────────────────────────

    def _edit(self):
        sel = self._get_selection()
        if not sel:
            return
        i    = sel[0]
        step = self.steps[i]

        def on_save(updated):
            self._snapshot("Edit step")
            self.steps[i] = updated
            self._commit()
            self.refresh()
            vis = getattr(self, "_visible_indices", None)
            lb = vis.index(i) if vis and i in vis else i
            self.listbox.selection_set(lb)

        StepEditDialog(self._parent, step, on_save)

    def _move_up(self):
        sel = self._get_selection()
        if not sel or sel[0] == 0:
            return
        i = sel[0]
        self._snapshot("Move up")
        self.steps[i], self.steps[i-1] = self.steps[i-1], self.steps[i]
        self._commit()
        self.refresh()
        vis = getattr(self, "_visible_indices", None)
        lb = vis.index(i-1) if vis and (i-1) in vis else i-1
        self.listbox.selection_set(lb)

    def _move_down(self):
        sel = self._get_selection()
        if not sel or sel[0] == len(self.steps) - 1:
            return
        i = sel[0]
        self._snapshot("Move down")
        self.steps[i], self.steps[i+1] = self.steps[i+1], self.steps[i]
        self._commit()
        self.refresh()
        vis = getattr(self, "_visible_indices", None)
        lb = vis.index(i+1) if vis and (i+1) in vis else i+1
        self.listbox.selection_set(lb)

    def _duplicate(self):
        sel = self._get_selection()
        if not sel:
            return
        self._snapshot("Duplicate")
        # Çoklu seçim varsa hepsini kopyala (ters sırayla ekle ki indexler bozulmasın)
        for i in reversed(sel):
            new_step = copy.deepcopy(self.steps[i])
            note = new_step.get("note", "")
            if note:
                new_step["note"] = f"(Copy) {note}"
            self.steps.insert(i + 1, new_step)
        self._commit()
        self.refresh()
        # Son kopyaya git (steps index → listbox index)
        last_steps_idx = sel[-1] + len(sel)
        vis = getattr(self, "_visible_indices", None)
        last_lb = vis.index(last_steps_idx) if vis and last_steps_idx in vis else last_steps_idx
        self.listbox.selection_set(last_lb)
        self.listbox.see(last_lb)
        self._show_undo_bar(tr("📋  {} step(s) copied  (Ctrl+Z to undo)").format(len(sel)))

    def _delete(self):
        sel = self._get_selection()
        if not sel:
            return
        self._snapshot("Delete")
        # Yüksek indeksten başlayarak sil — index kayması olmasın
        for i in sorted(sel, reverse=True):
            if 0 <= i < len(self.steps):
                self.steps.pop(i)
        self._commit()
        self.refresh()
        n = len(sel)
        self._show_undo_bar(tr("🗑  {} step(s) removed  (Ctrl+Z to undo)").format(n))

    def _clear(self):
        if not self.steps:
            return
        from tkinter import messagebox
        answer = messagebox.askyesno(
            tr("Clear All Steps"),
            tr("All {} step(s) will be removed.\nThis can be undone with Ctrl+Z.\n\nContinue?").format(len(self.steps)),
            icon="warning",
            default="no"
        )
        if not answer:
            return
        self._snapshot("Clear all")
        self.steps.clear()
        self._commit()
        self.refresh()
        self._show_undo_bar(tr("🗑  All steps cleared  (Ctrl+Z to undo)"))

    def _run_from_selected(self):
        """Run automation starting from the selected step."""
        sel = self._get_selection()
        idx = sel[0] if sel else 0
        if self.on_run_from:
            self.on_run_from(idx)

    # ── Delay yardımcıları ────────────────────────────────────────────────────

    def _add_delay_quick(self, duration):
        self._snapshot("Add delay")
        step = {"type": "delay", "duration": duration, "label": "",
                "interval": 0.0, "note": f"Wait {duration}s"}
        self.steps.append(step)
        self._commit()
        self.refresh()
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(tk.END)
        self.listbox.see(tk.END)

    def _add_delay_custom(self):
        _DelayDialog(self._parent, self._on_delay_dialog_save)

    def _on_delay_dialog_save(self, duration, label):
        self._snapshot("Add custom delay")
        step = {"type": "delay", "duration": duration, "label": label,
                "interval": 0.0, "note": f"{label or 'Delay'}: {duration:.1f}s"}
        self.steps.append(step)
        self._commit()
        self.refresh()
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(tk.END)
        self.listbox.see(tk.END)

    # ── External step addition ─────────────────────────────────────────────────

    def add_step_from_panel(self, step: dict):
        """Called by other panels — appends a step with a default note."""
        stype = step.get("type", "")
        if "note" not in step or not step["note"]:
            step["note"] = tr(_DEFAULT_NOTES.get(stype, ""))
        self._snapshot(tr("Add {} step").format(stype))
        self.steps.append(step)
        self._commit()
        self.refresh()
        self.scroll_to_last()

    # ── Genel yardımcılar ─────────────────────────────────────────────────────

    def set_state(self, s):
        for w in [self.up_btn, self.down_btn, self.edit_btn,
                  self.del_btn, self.dup_btn]:
            try:
                w.config(state=s)
            except Exception:
                pass

    def scroll_to_last(self):
        try:
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(tk.END)
            self.listbox.see(tk.END)
        except Exception:
            pass

    def refresh_labels(self):
        self.refresh()


# ── Özel Delay Dialog ─────────────────────────────────────────────────────────

_DELAY_UNITS = [("MS", 0.001), ("SEC", 1.0), ("MIN", 60.0), ("HR", 3600.0)]


def _delay_to_display(seconds: float):
    ms = seconds * 1000
    if ms < 1000:
        return str(int(round(ms))), "MS"
    if seconds < 60:
        v = f"{seconds:.2f}".rstrip("0").rstrip(".")
        return v, "SEC"
    if seconds < 3600:
        v = f"{seconds / 60:.2f}".rstrip("0").rstrip(".")
        return v, "MIN"
    v = f"{seconds / 3600:.2f}".rstrip("0").rstrip(".")
    return v, "HR"


def _delay_get_seconds(val_str: str, unit: str) -> float:
    try:
        val = float(val_str)
    except Exception:
        val = 1.0
    mult = next((u[1] for u in _DELAY_UNITS if u[0] == unit), 1.0)
    return max(0.001, val * mult)


class _DelayDialog:
    """Compact dialog for entering a custom delay duration and optional label."""

    def __init__(self, parent, on_save):
        self._on_save = on_save
        from tkinter import ttk as _ttk
        self._ttk = _ttk

        self._win = tk.Toplevel(parent)
        self._win.title(tr("Add Delay Step"))
        self._win.resizable(False, False)
        self._win.configure(bg=T("SURFACE"))
        self._win.grab_set()
        self._win.focus_set()
        self._build()
        self._center(parent)

    def _build(self):
        header = tk.Frame(self._win, bg=T("PRIMARY_BG"))
        header.pack(fill="x")
        tk.Label(header, text=tr("  ⏱  ADD DELAY STEP"),
                 bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
                 font=("Segoe UI", 11, "bold"),
                 pady=14).pack(side="left")

        body = tk.Frame(self._win, bg=T("SURFACE"))
        body.pack(fill="both", expand=True, padx=28, pady=(20, 0))

        tk.Label(body, text=tr("WAIT DURATION"),
                 bg=T("SURFACE"), fg=T("FG2"),
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 4))

        preset_row = tk.Frame(body, bg=T("SURFACE"))
        preset_row.pack(anchor="w", pady=(0, 8))

        presets = [("0.5s", 0.5), ("1s", 1.0), ("2s", 2.0),
                   ("3s", 3.0), ("5s", 5.0), ("10s", 10.0), ("30s", 30.0)]
        for label, secs in presets:
            b = tk.Button(
                preset_row, text=label,
                command=lambda s=secs: self._apply_preset(s),
                bg=T("SURFACE"), fg=T("FG"),
                activebackground=T("PRIMARY_BG"),
                activeforeground=T("PRIMARY_FG"),
                font=("Segoe UI", 8),
                relief="solid", bd=1,
                highlightthickness=1,
                highlightbackground=T("BORDER"),
                padx=7, pady=3, cursor="hand2"
            )
            b.pack(side="left", padx=(0, 4))
            b.bind("<Enter>", lambda e, w=b: w.config(
                bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
                highlightbackground=T("PRIMARY_BG")))
            b.bind("<Leave>", lambda e, w=b: w.config(
                bg=T("SURFACE"), fg=T("FG"),
                highlightbackground=T("BORDER")))

        manual_row = tk.Frame(body, bg=T("SURFACE"))
        manual_row.pack(anchor="w", pady=(0, 4))

        self._val_entry = tk.Entry(
            manual_row, width=9,
            bg=T("ENTRY_BG"), fg=T("FG"),
            relief="solid", bd=1,
            highlightthickness=1, highlightbackground=T("BORDER"),
            highlightcolor=T("BORDER_STRONG"),
            font=("Segoe UI", 11, "bold"), justify="center",
            insertbackground=T("FG")
        )
        self._val_entry.insert(0, "1")
        self._val_entry.pack(side="left", padx=(0, 8))
        self._val_entry.bind("<FocusIn>",  lambda e: self._val_entry.config(highlightthickness=2))
        self._val_entry.bind("<FocusOut>", lambda e: self._val_entry.config(highlightthickness=1))

        self._unit_var = tk.StringVar(value="SEC")
        unit_cb = self._ttk.Combobox(
            manual_row, textvariable=self._unit_var,
            values=[u[0] for u in _DELAY_UNITS],
            state="readonly", width=5,
            font=("Segoe UI", 9)
        )
        unit_cb.pack(side="left")

        self._preview_lbl = tk.Label(
            body, text=tr("= 1.00 seconds"),
            bg=T("SURFACE"), fg=T("FG3"),
            font=("Segoe UI", 8, "italic")
        )
        self._preview_lbl.pack(anchor="w", pady=(2, 12))

        self._val_entry.bind("<KeyRelease>", lambda e: self._update_preview())
        self._unit_var.trace_add("write", lambda *_: self._update_preview())

        tk.Frame(body, bg=T("BORDER"), height=1).pack(fill="x", pady=(0, 14))

        tk.Label(body, text=tr("LABEL  (optional — shown in steps list)"),
                 bg=T("SURFACE"), fg=T("FG2"),
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 4))

        self._label_entry = tk.Entry(
            body, width=32,
            bg=T("ENTRY_BG"), fg=T("FG"),
            relief="solid", bd=1,
            highlightthickness=1, highlightbackground=T("BORDER"),
            highlightcolor=T("BORDER_STRONG"),
            font=("Segoe UI", 9),
            insertbackground=T("FG")
        )
        self._label_entry.pack(anchor="w")
        self._label_entry.bind("<FocusIn>",  lambda e: self._label_entry.config(highlightthickness=2))
        self._label_entry.bind("<FocusOut>", lambda e: self._label_entry.config(highlightthickness=1))

        btn_row = tk.Frame(self._win, bg=T("SURFACE"))
        btn_row.pack(fill="x", padx=28, pady=(20, 24))

        ok_btn = tk.Button(
            btn_row, text=tr("ADD DELAY"),
            command=self._save,
            bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
            activebackground=T("PRIMARY_H_BG"),
            activeforeground=T("PRIMARY_H_FG"),
            font=("Segoe UI", 9, "bold"),
            relief="flat", bd=0,
            highlightthickness=0,
            padx=16, pady=7, cursor="hand2"
        )
        ok_btn.pack(side="left", padx=(0, 10))

        cancel_btn = tk.Button(
            btn_row, text=tr("CANCEL"),
            command=self._win.destroy,
            bg=T("SURFACE"), fg=T("FG"),
            activebackground=T("SURFACE2"),
            activeforeground=T("FG"),
            font=("Segoe UI", 9),
            relief="solid", bd=1,
            highlightthickness=1,
            highlightbackground=T("BORDER"),
            padx=12, pady=5, cursor="hand2"
        )
        cancel_btn.pack(side="left")

        self._win.bind("<Return>", lambda e: self._save())
        self._win.bind("<Escape>", lambda e: self._win.destroy())
        self._val_entry.focus_set()
        self._val_entry.select_range(0, tk.END)

    def _apply_preset(self, seconds):
        val_str, unit = _delay_to_display(seconds)
        self._val_entry.delete(0, tk.END)
        self._val_entry.insert(0, val_str)
        self._unit_var.set(unit)
        self._update_preview()

    def _update_preview(self):
        try:
            secs = _delay_get_seconds(self._val_entry.get(), self._unit_var.get())
            if secs < 1.0:
                txt = tr("= {} ms").format(int(secs * 1000))
            elif secs < 60:
                txt = tr("= {:.2f} seconds").format(secs)
            elif secs < 3600:
                txt = tr("= {:.2f} minutes").format(secs / 60)
            else:
                txt = tr("= {:.2f} hours").format(secs / 3600)
            self._preview_lbl.config(text=txt, fg=T("FG3"))
        except Exception:
            self._preview_lbl.config(text=tr("= invalid value"), fg="#E74C3C")

    def _save(self):
        duration = _delay_get_seconds(self._val_entry.get(), self._unit_var.get())
        label    = self._label_entry.get().strip()
        self._on_save(duration, label)
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
            sx, sy = 400, 200
        self._win.geometry(f"+{max(0,sx)}+{max(0,sy)}")
