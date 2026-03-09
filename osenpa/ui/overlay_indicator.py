import tkinter as tk
from ui.theme import T
from utils.i18n import tr


class OverlayIndicator:
    def __init__(self, root):
        self.root           = root
        self._win           = None
        self._count_lbl     = None
        self._scan_lbl      = None
        self._title_lbl     = None
        self._condition_lbl = None

    def show(self, text, hotkey=None, count=None, show_scan=False):
        if self._win:
            try:
                if self._title_lbl:
                    self._title_lbl.config(text=text)
                if self._count_lbl and count is not None:
                    self._count_lbl.config(text=tr("ACTIONS: {}").format(count))
                return
            except Exception:
                pass

        self._win = tk.Toplevel(self.root)
        self._win.overrideredirect(True)
        self._win.attributes("-topmost", True)
        self._win.attributes("-alpha", 0.95)

        frame = tk.Frame(
            self._win,
            bg=T("PRIMARY_BG"),
            padx=20, pady=14
        )
        frame.pack()

        self._title_lbl = tk.Label(
            frame, text=text,
            bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
            font=("Segoe UI", 9, "bold"),
            justify="left"
        )
        self._title_lbl.pack(anchor="w")

        if count is not None:
            self._count_lbl = tk.Label(
                frame,
                text=tr("ACTIONS: {}").format(count),
                bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
                font=("Segoe UI", 9)
            )
            self._count_lbl.pack(anchor="w", pady=(2, 0))
        else:
            self._count_lbl = None

        # Scan sayacı satırı — color/image scanning için
        if show_scan:
            self._scan_lbl = tk.Label(
                frame,
                text=tr("SCANS: 0"),
                bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
                font=("Segoe UI", 9)
            )
            self._scan_lbl.pack(anchor="w", pady=(2, 0))
        else:
            self._scan_lbl = None

        # Koşul dal göstergesi (if_color / if_image adımları için)
        self._condition_lbl = tk.Label(
            frame,
            text="",
            bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
            font=("Segoe UI", 9, "bold")
        )
        self._condition_lbl.pack(anchor="w", pady=(2, 0))
        self._condition_lbl.pack_forget()  # başlangıçta gizli

        if hotkey:
            tk.Label(
                frame,
                text=tr("STOP: {}").format(hotkey.upper()),
                bg=T("PRIMARY_BG"), fg=T("FG3"),
                font=("Segoe UI", 8)
            ).pack(anchor="w", pady=(4, 0))

        self._win.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w  = self._win.winfo_width()
        h  = self._win.winfo_height()
        self._win.geometry(f"+{sw - w - 24}+{sh - h - 60}")

    def update_count(self, count):
        """Aksiyon sayacını güncelle."""
        if self._count_lbl:
            try:
                self._count_lbl.config(text=tr("ACTIONS: {}").format(count))
            except Exception:
                pass

    def update_scan(self, scan_count):
        """Tarama sayacını güncelle (color/image scanning için)."""
        if self._scan_lbl:
            try:
                self._scan_lbl.config(text=tr("SCANS: {}").format(scan_count))
            except Exception:
                pass

    def update_condition(self, branch: str, action_type: str):
        """IF adımı sonucunu overlay'de göster: THEN veya ELSE + aksiyon tipi."""
        if not self._condition_lbl:
            return
        try:
            if branch == "THEN":
                color = T("COND_TRUE")   # tema'dan — hardcoded değil
                icon  = "✓"
            else:
                color = T("COND_FALSE")  # tema'dan — hardcoded değil
                icon  = "✗"
            label = f"{icon} {tr(branch)}: {tr(action_type.upper())}"
            self._condition_lbl.config(text=label, fg=color)
            self._condition_lbl.pack(anchor="w", pady=(2, 0))
            # 2.5 saniye sonra sıfırla
            self.root.after(2500, self._clear_condition)
        except Exception:
            pass

    def _clear_condition(self):
        try:
            if self._condition_lbl:
                self._condition_lbl.config(text="")
                self._condition_lbl.pack_forget()
        except Exception:
            pass

    def hide(self):
        if self._win:
            try:
                self._win.destroy()
            except Exception:
                pass
            self._win           = None
            self._count_lbl     = None
            self._scan_lbl      = None
            self._title_lbl     = None
            self._condition_lbl = None
