import tkinter as tk
from tkinter import filedialog
from PIL import ImageGrab, Image
import numpy as np
import os
from ui.theme import (make_entry, make_btn, make_slider,
                       section_title, divider, T)
from ui.interval_widget import make_interval_widget
from core import state
from utils.i18n import tr
from utils.tooltip import add_tooltip


# ── Tek görsel satır widget'ı ─────────────────────────────────────────────────

class _ImageRow:
    """Single row in image list: thumbnail + name + remove button."""

    MAX_THUMB = 48

    def __init__(self, parent, label, path, array, confidence, on_remove, index):
        self.label      = label
        self.path       = path
        self.array      = array
        self.index      = index
        self._confidence = confidence   # store global conf at add time
        self._thumb_img = None

        self.frame = tk.Frame(parent, bg=T("SURFACE2"),
                              relief="solid", bd=1,
                              highlightthickness=1,
                              highlightbackground=T("BORDER"))
        self.frame.pack(fill="x", pady=(0, 6))

        inner = tk.Frame(self.frame, bg=T("SURFACE2"))
        inner.pack(fill="x", padx=10, pady=8)

        # Left: thumbnail
        thumb_frame = tk.Frame(inner, bg=T("BORDER"),
                               width=self.MAX_THUMB + 2,
                               height=self.MAX_THUMB + 2)
        thumb_frame.pack(side="left", padx=(0, 10))
        thumb_frame.pack_propagate(False)

        self._thumb_lbl = tk.Label(thumb_frame, bg=T("SURFACE2"),
                                    text="", relief="flat")
        self._thumb_lbl.place(relx=0.5, rely=0.5, anchor="center")
        self._load_thumbnail()

        # Middle: name + source
        mid = tk.Frame(inner, bg=T("SURFACE2"))
        mid.pack(side="left", fill="both", expand=True)

        disp_name = os.path.basename(label) if os.sep in label or "/" in label else label
        self._name_lbl = tk.Label(
            mid,
            text=disp_name.upper() if len(disp_name) <= 28 else disp_name[:25].upper() + "...",
            bg=T("SURFACE2"), fg=T("FG"),
            font=("Segoe UI", 9, "bold"),
            anchor="w"
        )
        self._name_lbl.pack(anchor="w")

        src_text = tr("CLIPBOARD") if path is None else os.path.basename(path)
        self._src_lbl = tk.Label(
            mid,
            text=src_text,
            bg=T("SURFACE2"), fg=T("FG2"),
            font=("Segoe UI", 7),
            anchor="w"
        )
        self._src_lbl.pack(anchor="w", pady=(1, 4))

        # Right: remove button
        right = tk.Frame(inner, bg=T("SURFACE2"))
        right.pack(side="right", anchor="center")

        del_btn = tk.Button(
            right, text="✕",
            command=lambda: on_remove(self),
            bg=T("SURFACE2"), fg=T("FG3"),
            activebackground=T("PRIMARY_BG"),
            activeforeground=T("PRIMARY_FG"),
            font=("Segoe UI", 10),
            relief="flat", bd=0,
            padx=6, pady=2,
            cursor="hand2"
        )
        del_btn.pack()
        del_btn.bind("<Enter>", lambda e: del_btn.config(fg=T("FG"), bg=T("BORDER")))
        del_btn.bind("<Leave>", lambda e: del_btn.config(fg=T("FG3"), bg=T("SURFACE2")))

    def _load_thumbnail(self):
        """Görselden küçük önizleme oluştur."""
        try:
            if self.array is not None:
                pil_img = Image.fromarray(self.array.astype(np.uint8))
            elif self.path and os.path.isfile(self.path):
                pil_img = Image.open(self.path).convert("RGB")
            else:
                self._thumb_lbl.config(
                    text="?", fg=T("FG3"),
                    font=("Segoe UI", 14), bg=T("SURFACE2"))
                return

            # Orantılı küçültme
            w, h = pil_img.size
            scale = self.MAX_THUMB / max(w, h)
            nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
            pil_img = pil_img.resize((nw, nh), Image.LANCZOS)

            # Tkinter PhotoImage olarak sakla
            self._thumb_img = tk.PhotoImage(data=self._pil_to_png_bytes(pil_img))
            self._thumb_lbl.config(image=self._thumb_img,
                                   bg=T("SURFACE2"), text="")
        except Exception as e:
            print(f"[ImageRow] thumbnail error: {e}")
            self._thumb_lbl.config(
                text=tr("IMG"), fg=T("FG3"),
                font=("Segoe UI", 7, "bold"), bg=T("SURFACE2"))

    @staticmethod
    def _pil_to_png_bytes(pil_img):
        """PIL Image'ı base64-free PhotoImage data'sına çevirir."""
        import io, base64
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue())

    def get_confidence(self):
        return round(self._confidence, 2)

    def destroy(self):
        self.frame.destroy()


# ── ImagePanel ana sınıfı ──────────────────────────────────────────────────────

class ImagePanel:
    def __init__(self, parent, on_start, on_stop, on_pick_area,
                 on_change_hotkey, on_add_step):
        self.on_start         = on_start
        self.on_stop          = on_stop
        self.on_pick_area     = on_pick_area
        self.on_change_hotkey = on_change_hotkey
        self.on_add_step      = on_add_step

        # Eski tekli görsel (uyumluluk)
        self.image_path      = None
        self.clipboard_image = None

        # Çoklu görsel listesi
        self._image_rows = []

        self.area = None
        self.box  = tk.Frame(parent, bg=T("SURFACE"))
        self.box.pack(fill="both", expand=True)
        self._build()

    # ── Scroll yardımcıları ───────────────────────────────────────

    def _make_scrollbar_handler(self, canvas, sb):
        def handler(first, last):
            sb.set(first, last)
            self._update_scrollbar_visibility(canvas, sb)
        return handler

    def _update_scrollbar_visibility(self, canvas, sb):
        try:
            region = canvas.bbox("all")
            if not region:
                sb.pack_forget()
                return
            content_h = region[3] - region[1]
            canvas_h  = canvas.winfo_height()
            if content_h > canvas_h:
                if not sb.winfo_ismapped():
                    sb.pack(side="right", fill="y", before=canvas)
            else:
                sb.pack_forget()
                canvas.yview_moveto(0)
        except Exception:
            pass

    def _build(self):
        box = self.box

        canvas = tk.Canvas(box, bg=T("SURFACE"), highlightthickness=0)
        sb = tk.Scrollbar(box, orient="vertical", command=canvas.yview,
                          bg=T("SCROLL_BG"), troughcolor=T("SCROLL_BG"),
                          activebackground=T("SCROLL_ACTIVE"),
                          relief="flat", bd=0, width=10)
        canvas.configure(yscrollcommand=self._make_scrollbar_handler(canvas, sb))
        canvas.pack(side="left", fill="both", expand=True)
        wrap = tk.Frame(canvas, bg=T("SURFACE"))
        win  = canvas.create_window((0, 0), window=wrap, anchor="nw")
        self._img_canvas = canvas
        self._img_sb     = sb

        def on_fc(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            self._update_scrollbar_visibility(canvas, sb)
        def on_cc(e):
            canvas.itemconfig(win, width=e.width)
            self._update_scrollbar_visibility(canvas, sb)
        wrap.bind("<Configure>", on_fc)
        canvas.bind("<Configure>", on_cc)
        canvas.bind("<Enter>",
            lambda e: canvas.bind_all("<MouseWheel>",
                lambda ev: canvas.yview_scroll(int(-1*(ev.delta/120)), "units")))
        canvas.bind("<Leave>",
            lambda e: canvas.unbind_all("<MouseWheel>"))

        # ── Başlık ────────────────────────────────────────────────
        title_bar = tk.Frame(wrap, bg=T("SURFACE"))
        title_bar.pack(fill="x", padx=32, pady=(28, 6))
        tk.Label(title_bar, text=tr("IMAGE DETECTION"),
                  bg=T("SURFACE"), fg=T("FG"),
                  font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(title_bar,
                  text=tr("Click when any of the defined template images appears on screen"),
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 0))

        # ── Hotkey badge ──────────────────────────────────────────
        hk_row = tk.Frame(wrap, bg=T("SURFACE"))
        hk_row.pack(fill="x", padx=32, pady=(6, 0))
        tk.Label(hk_row, text=tr("PANEL HOTKEY"),
                  bg=T("SURFACE"), fg=T("FG3"),
                  font=("Segoe UI", 7, "bold")).pack(side="left", padx=(0, 8))
        self.hotkey_display = tk.Label(
            hk_row, text=state.image_hotkey.upper(),
            bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
            font=("Segoe UI", 8, "bold"), padx=8, pady=2)
        self.hotkey_display.pack(side="left", padx=(0, 8))
        make_btn(hk_row, tr("CHANGE"),
                  self._change_hotkey_btn, small=True).pack(side="left")

        divider(wrap, padx=32, pady=(14, 0))

        body = tk.Frame(wrap, bg=T("SURFACE"))
        body.pack(fill="x", padx=32, pady=(20, 0))

        # ── Görsel Listesi Bölümü ─────────────────────────────────
        section_title(body, tr("TARGET IMAGES"), bg=T("SURFACE"))

        tk.Label(body,
                  text=tr("Click when ANY of these template images is detected on screen"),
                  bg=T("SURFACE"), fg=T("FG3"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 10))

        # Ekleme butonları
        add_btn_row = tk.Frame(body, bg=T("SURFACE"))
        add_btn_row.pack(fill="x", pady=(0, 10))
        make_btn(add_btn_row, tr("＋ LOAD IMAGE"),
                  self._add_from_file).pack(side="left", padx=(0, 8))
        make_btn(add_btn_row, tr("＋ PASTE CLIPBOARD"),
                  self._add_from_clipboard).pack(side="left")

        # Görsel listesi kapsayıcısı
        self._list_outer = tk.Frame(body, bg=T("SURFACE"))
        self._list_outer.pack(fill="x", pady=(0, 4))

        self._list_frame = tk.Frame(self._list_outer, bg=T("SURFACE"))
        self._list_frame.pack(fill="x")

        # Boş durum etiketi
        self._empty_lbl = tk.Label(
            self._list_frame,
            text=tr("No images added yet. Use the buttons above to add template images."),
            bg=T("SURFACE"), fg=T("FG3"),
            font=("Segoe UI", 9), wraplength=380, justify="left"
        )
        self._empty_lbl.pack(anchor="w", pady=(4, 8))

        # Sayaç + Temizle
        counter_row = tk.Frame(body, bg=T("SURFACE"))
        counter_row.pack(fill="x", pady=(0, 4))
        self._count_lbl = tk.Label(
            counter_row, text=f"0 {tr('images defined')}",
            bg=T("SURFACE"), fg=T("FG2"),
            font=("Segoe UI", 8)
        )
        self._count_lbl.pack(side="left")
        make_btn(counter_row, tr("CLEAR ALL"),
                  self._clear_all_images, small=True).pack(side="right")

        divider(body, pady=(12, 16))

        # ── SETTINGS (Repeat/Infinite) ────────────────────────────
        section_title(body, tr("SETTINGS"), bg=T("SURFACE"))
        
        rep_row = tk.Frame(body, bg=T("SURFACE"))
        rep_row.pack(fill="x", pady=(0, 14))

        rr1 = tk.Frame(rep_row, bg=T("SURFACE"))
        rr1.pack(side="left", padx=(0, 20))
        tk.Label(rr1, text=tr("REPEAT"), bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 5))
        self.repeat_entry = make_entry(rr1, width=6, default="1", center=True)
        self.repeat_entry.pack(anchor="w")

        rr2 = tk.Frame(rep_row, bg=T("SURFACE"))
        rr2.pack(side="left", padx=(0, 20))
        tk.Label(rr2, text=tr("INFINITE"), bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 5))
        self.infinite_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            rr2, variable=self.infinite_var,
            bg=T("SURFACE"), fg=T("FG"),
            activebackground=T("SURFACE"),
            activeforeground=T("FG"),
            selectcolor=T("CHECK_BG"), relief="flat",
            command=self._toggle_infinite
        ).pack(anchor="w")

        # ── Varsayılan Confidence ─────────────────────────────────
        section_title(body, tr("DEFAULT CONFIDENCE"), bg=T("SURFACE"))

        conf_title_row = tk.Frame(body, bg=T("SURFACE"))
        conf_title_row.pack(fill="x", pady=(0, 6))

        tk.Label(conf_title_row, text=tr("Applied to new images — each image can be fine-tuned above"),
                  bg=T("SURFACE"), fg=T("FG3"),
                  font=("Segoe UI", 8)).pack(side="left")

        help_icon = tk.Label(conf_title_row, text="[?]", bg=T("SURFACE"), fg=T("PRIMARY_BG"), font=("Segoe UI", 8, "bold"), cursor="hand2")
        help_icon.pack(side="left", padx=(4, 0))
        add_tooltip(help_icon, tr("Confidence controls how identical the image on screen needs to be.\n1.0 = exact pixel match.\n0.8 = usually ignores slight color depth/rendering differences."))
        tk.Label(body, text=tr("Higher value = stricter match (0.70–0.85 recommended)"),
                  bg=T("SURFACE"), fg=T("FG3"),
                  font=("Segoe UI", 7)).pack(anchor="w", pady=(0, 5))
        self.conf_slider = make_slider(body, 0, 1, 0.8, bg=T("SURFACE"))
        self.conf_slider.pack(fill="x", pady=(0, 4))
        tk.Label(body,
                  text=tr("⚠  Values above 0.90 may fail on slightly different screens"),
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 7)).pack(anchor="w", pady=(0, 12))

        divider(body, pady=(4, 16))

        # Scan interval
        iv_row = tk.Frame(body, bg=T("SURFACE"))
        iv_row.pack(fill="x", pady=(0, 14))
        tk.Label(iv_row, text=tr("SCAN INTERVAL"),
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 2))
        tk.Label(iv_row,
                  text=tr("How often the screen is scanned for images"),
                  bg=T("SURFACE"), fg=T("FG3"),
                  font=("Segoe UI", 7)).pack(anchor="w", pady=(0, 5))
        self.scan_interval_widget = make_interval_widget(
            iv_row, bg=T("SURFACE"), default_ms=500)
        self.scan_interval_widget.pack(anchor="w")

        divider(body, pady=(4, 16))

        # ── Click Settings ────────────────────────────────────────
        section_title(body, tr("CLICK SETTINGS"), bg=T("SURFACE"))

        tk.Label(body, text=tr("BUTTON"),
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 5))
        btn_row = tk.Frame(body, bg=T("SURFACE"))
        btn_row.pack(anchor="w", pady=(0, 14))
        self.click_var = tk.StringVar(value="left")
        for val, lbl in [("left", tr("LEFT")), ("right", tr("RIGHT")),
                          ("middle", tr("MIDDLE"))]:
            tk.Radiobutton(
                btn_row, text=lbl,
                variable=self.click_var, value=val,
                bg=T("SURFACE"), fg=T("FG"),
                selectcolor=T("CHECK_BG"),
                activebackground=T("SURFACE"),
                activeforeground=T("FG"),
                font=("Segoe UI", 9)
            ).pack(side="left", padx=(0, 16))

        divider(body, pady=(4, 16))

        # ── Scan Area ─────────────────────────────────────────────
        section_title(body, tr("SCAN AREA"), bg=T("SURFACE"))

        tk.Label(body, text=tr("Limit scanning to a specific region (optional)"),
                  bg=T("SURFACE"), fg=T("FG3"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 10))

        area_btn_row = tk.Frame(body, bg=T("SURFACE"))
        area_btn_row.pack(fill="x", pady=(0, 8))
        make_btn(area_btn_row, tr("PICK AREA"),
                  self._pick_area_btn).pack(side="left", padx=(0, 8))
        make_btn(area_btn_row, tr("FULL SCREEN"),
                  self._set_fullscreen).pack(side="left", padx=(0, 8))
        make_btn(area_btn_row, tr("CLEAR"),
                  self._clear_area).pack(side="left")

        coord_row = tk.Frame(body, bg=T("SURFACE"))
        coord_row.pack(fill="x", pady=(0, 6))
        for label, attr in [(tr("X1"), "x1"), (tr("Y1"), "y1"),
                              (tr("X2"), "x2"), (tr("Y2"), "y2")]:
            col = tk.Frame(coord_row, bg=T("SURFACE"))
            col.pack(side="left", padx=(0, 12))
            tk.Label(col, text=label, bg=T("SURFACE"), fg=T("FG2"),
                      font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 4))
            e = make_entry(col, width=6)
            e.pack(anchor="w")
            setattr(self, f"{attr}_entry", e)

        self.area_label = tk.Label(
            body, text=tr("Full screen (default)"),
            bg=T("SURFACE"), fg=T("FG2"), font=("Segoe UI", 9)
        )
        self.area_label.pack(anchor="w", pady=(4, 0))

        divider(body, pady=(16, 16))

        # ── Step Interval ─────────────────────────────────────────
        section_title(body, tr("STEP INTERVAL"), bg=T("SURFACE"))

        tk.Label(body,
                  text=tr("⏱  Wait AFTER click, before scanning again"),
                  bg=T("SURFACE"), fg=T("FG3"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 8))

        step_iv_row = tk.Frame(body, bg=T("SURFACE"))
        step_iv_row.pack(fill="x", pady=(0, 14))
        self.step_interval_widget = make_interval_widget(
            step_iv_row, bg=T("SURFACE"), default_ms=500)
        self.step_interval_widget.pack(anchor="w")

        divider(body, pady=(4, 16))

        # ── IF IMAGE → THEN / ELSE ────────────────────────────────
        self._build_condition_section(body)

        divider(body, pady=(4, 16))

        # ── Actions ───────────────────────────────────────────────
        section_title(body, tr("ACTIONS"), bg=T("SURFACE"))

        action_row = tk.Frame(body, bg=T("SURFACE"))
        action_row.pack(fill="x", pady=(0, 8))

        self.start_btn = make_btn(
            action_row, tr("START"), self._start, primary=True)
        self.start_btn.pack(side="left", padx=(0, 8))

        self.stop_btn = make_btn(action_row, tr("STOP"), self._stop)
        self.stop_btn.config(state="disabled")
        self.stop_btn.pack(side="left", padx=(0, 8))

        make_btn(action_row, tr("ADD TO STEPS"),
                  self._add_step).pack(side="left")

        self.status_lbl = tk.Label(
            body, text="", bg=T("SURFACE"), fg=T("FG2"),
            font=("Segoe UI", 9))
        self.status_lbl.pack(anchor="w", pady=(10, 24))

    # ── Görsel listesi yönetimi ───────────────────────────────────

    def _add_image_to_list(self, label, path, array, confidence=None):
        """Yeni görseli listeye ekle."""
        if confidence is None:
            confidence = self.conf_slider.get_val()
        # Aynı path'ten zaten eklendiyse atla
        if path is not None:
            for row in self._image_rows:
                if row.path == path:
                    self.status_lbl.config(
                        text=f"{tr('ALREADY IN LIST: ')}{os.path.basename(path).upper()}",
                        fg=T("FG2"))
                    return
        row = _ImageRow(
            self._list_frame, label, path, array, confidence,
            on_remove=self._remove_image_row,
            index=len(self._image_rows)
        )
        self._image_rows.append(row)

        # Eski tekli uyumluluk
        if self.image_path is None and self.clipboard_image is None:
            self.image_path      = path
            self.clipboard_image = array

        self._refresh_list_ui()

    def _remove_image_row(self, row):
        if row in self._image_rows:
            self._image_rows.remove(row)
        row.destroy()
        # Eski tekli imleci güncelle
        if self._image_rows:
            self.image_path      = self._image_rows[0].path
            self.clipboard_image = self._image_rows[0].array
        else:
            self.image_path      = None
            self.clipboard_image = None
        self._refresh_list_ui()

    def _clear_all_images(self):
        for row in list(self._image_rows):
            row.destroy()
        self._image_rows.clear()
        self.image_path      = None
        self.clipboard_image = None
        self._refresh_list_ui()

    def _refresh_list_ui(self):
        count = len(self._image_rows)
        if count == 0:
            self._empty_lbl.pack(anchor="w", pady=(4, 8))
        else:
            self._empty_lbl.pack_forget()
        noun = tr("image") if count == 1 else tr("images")
        self._count_lbl.config(
            text=f"{count} {noun} defined",
            fg=T("FG") if count > 0 else T("FG2")
        )

    def get_image_list(self):
        """[{"path": ..., "array": ..., "confidence": ..., "label": ...}, ...] döndürür."""
        result = []
        for row in self._image_rows:
            result.append({
                "path":       row.path,
                "array":      row.array,
                "confidence": row.get_confidence(),
                "label":      row.label,
            })
        return result

    # ── Görsel yükleme ────────────────────────────────────────────

    def _add_from_file(self):
        paths = filedialog.askopenfilenames(
            title=tr("Select Template Image(s)"),
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff"),
                       ("All files", "*.*")]
        )
        for path in paths:
            label = os.path.basename(path)
            self._add_image_to_list(label, path, None)

    def _add_from_clipboard(self):
        try:
            img = ImageGrab.grabclipboard()
            if img is None:
                self.status_lbl.config(
                    text=tr("NO IMAGE IN CLIPBOARD."), fg=T("FG2"))
                return
            arr   = np.array(img.convert("RGB"))
            count = sum(1 for r in self._image_rows if r.path is None)
            label = f"{tr('Clipboard')} {count + 1}" if count > 0 else tr("Clipboard")
            self._add_image_to_list(label, None, arr)
            self.status_lbl.config(text="")
        except Exception as e:
            self.status_lbl.config(text=f"{tr('PASTE FAILED: ')}{e}", fg=T("FG2"))

    def _has_images(self):
        return len(self._image_rows) > 0

    # ── Hotkey ────────────────────────────────────────────────────

    def _change_hotkey_btn(self):
        self.on_change_hotkey()
        self.hotkey_display.config(
            text=tr("PRESS ANY KEY..."),
            bg=T("SURFACE2"), fg=T("FG2"))

    def update_hotkey_display(self, key_name):
        self.hotkey_display.config(
            text=key_name.upper(),
            bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"))

    # ── Infinite ──────────────────────────────────────────────────

    def _toggle_infinite(self):
        self.repeat_entry.config(
            state="disabled" if self.infinite_var.get() else "normal")

    # ── Alan seçimi ───────────────────────────────────────────────

    def _pick_area_btn(self):
        self.on_pick_area(self._apply_area)

    def _set_fullscreen(self):
        self._clear_area()
        self.area_label.config(text=tr("Full screen (selected)"), fg=T("FG"))

    def _clear_area(self):
        self.area = None
        for attr in ["x1", "y1", "x2", "y2"]:
            getattr(self, f"{attr}_entry").delete(0, tk.END)
        self.area_label.config(text=tr("Full screen (default)"), fg=T("FG2"))

    def _apply_area(self, x1, y1, x2, y2):
        self.area = (x1, y1, x2, y2)
        for attr, val in [("x1", x1), ("y1", y1), ("x2", x2), ("y2", y2)]:
            e = getattr(self, f"{attr}_entry")
            e.delete(0, tk.END)
            e.insert(0, str(val))
        self.area_label.config(
            text=f"({x1}, {y1}) → ({x2}, {y2})", fg=T("FG"))

    def get_area(self):
        try:
            return (int(self.x1_entry.get()), int(self.y1_entry.get()),
                    int(self.x2_entry.get()), int(self.y2_entry.get()))
        except Exception:
            return None

    # ── Start / Stop ──────────────────────────────────────────────

    def _start(self):
        if not self._has_images():
            self.status_lbl.config(
                text=tr("PLEASE ADD AT LEAST ONE IMAGE."), fg=T("FG2"))
            return
        if getattr(self, "_on_busy_check", None) and self._on_busy_check():
            self.status_lbl.config(
                text=tr("STOP THE ACTIVE TASK FIRST."), fg=T("FG2"))
            return
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_lbl.config(text=tr("SCANNING..."))

        img_list = self.get_image_list()
        # Eski API uyumluluğu: ilk görseli tekli parametreler olarak da gönder
        first = img_list[0]
        self.on_start(
            image_path=first["path"],
            clipboard_image=first["array"],
            confidence=first["confidence"],
            scan_interval=self.scan_interval_widget.get_seconds(),
            click_button=self.click_var.get(),
            area=self.get_area(),
            step_interval=self.step_interval_widget.get_seconds(),
            image_list=img_list      # çoklu liste
        )

    def _stop(self):
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_lbl.config(text=tr("STOPPED."))
        self.on_stop()

    def _add_step(self):
        if not self._has_images():
            self.status_lbl.config(
                text=tr("PLEASE ADD AT LEAST ONE IMAGE."), fg=T("FG2"))
            return
        infinite = self.infinite_var.get()
        try:
            repeat = 1 if infinite else int(self.repeat_entry.get())
        except Exception:
            repeat = 1

        img_list = self.get_image_list()
        first    = img_list[0]

        base = {
            "type":          "image",
            "confidence":    first["confidence"],
            "scan_interval": self.scan_interval_widget.get_seconds(),
            "button":        self.click_var.get(),
            "area":          list(self.area) if self.area else None,
            "interval":      0.1,
            "repeat":        repeat,
            "infinite":      infinite,
            "image_path":    first["path"],
            "clipboard_image": first["array"].tolist() if first["array"] is not None else None,
            # Çoklu görsel listesi (serileştirilebilir)
            "image_list": [
                {
                    "path":       item["path"],
                    "array":      item["array"].tolist() if item["array"] is not None else None,
                    "confidence": item["confidence"],
                    "label":      item["label"],
                }
                for item in img_list
            ],
        }
        self.on_add_step(base)
        count = len(img_list)
        noun  = tr("image") if count == 1 else tr("images")
        self.status_lbl.config(
            text=f"{tr('STEP ADDED: ')}{count} {noun.upper()}", fg=T("FG"))

    # ─────────────────────────────────────────────────────────────────────────
    # IF / THEN / ELSE  —  CONDITION STEP
    # Genişletilmiş: AND/OR, wait_until_found, goto, drag, scroll, type_text
    # ─────────────────────────────────────────────────────────────────────────

    def _build_condition_section(self, body):
        """IF IMAGE → THEN / ELSE koşul bölümünü oluştur (genişletilmiş)."""
        from ui.theme import section_title as _st
        _st(body, tr("IF / THEN / ELSE  —  CONDITION STEP"), bg=T("SURFACE"))

        tk.Label(body,
                 text=tr("Use the images above as a conditional trigger. Set what happens when found (THEN) and when not found (ELSE)."),
                 bg=T("SURFACE"), fg=T("FG2"),
                 font=("Segoe UI", 8), wraplength=400, justify="left"
                 ).pack(anchor="w", pady=(0, 12))

        # ── Multi-image match mode (AND / OR) ─────────────────────
        cmode_frame = tk.Frame(body, bg=T("SURFACE2"),
                               relief="solid", bd=1,
                               highlightthickness=1,
                               highlightbackground=T("BORDER"))
        cmode_frame.pack(fill="x", pady=(0, 10))
        cmode_inner = tk.Frame(cmode_frame, bg=T("SURFACE2"))
        cmode_inner.pack(fill="x", padx=12, pady=8)

        tk.Label(cmode_inner, text=tr("MULTI-IMAGE MATCH MODE"),
                 bg=T("SURFACE2"), fg=T("FG2"),
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 6))

        self._cond_mode_var = tk.StringVar(value="OR")
        cm_row = tk.Frame(cmode_inner, bg=T("SURFACE2"))
        cm_row.pack(anchor="w")
        for val, lbl, desc in [
            ("OR",  tr("OR"),  tr("Triggers if ANY image is found")),
            ("AND", tr("AND"), tr("Triggers only if ALL images are found")),
        ]:
            col = tk.Frame(cm_row, bg=T("SURFACE2"))
            col.pack(side="left", padx=(0, 20))
            tk.Radiobutton(col, text=lbl, variable=self._cond_mode_var, value=val,
                           bg=T("SURFACE2"), fg=T("FG"),
                           selectcolor=T("CHECK_BG"),
                           activebackground=T("SURFACE2"),
                           activeforeground=T("FG"),
                           font=("Segoe UI", 9, "bold")).pack(anchor="w")
            tk.Label(col, text=desc,
                     bg=T("SURFACE2"), fg=T("FG3"),
                     font=("Segoe UI", 7)).pack(anchor="w")

        # ── Wait Mode ─────────────────────────────────────────────
        wm_frame = tk.Frame(body, bg=T("SURFACE2"),
                            relief="solid", bd=1,
                            highlightthickness=1,
                            highlightbackground=T("BORDER"))
        wm_frame.pack(fill="x", pady=(0, 10))
        wm_inner = tk.Frame(wm_frame, bg=T("SURFACE2"))
        wm_inner.pack(fill="x", padx=12, pady=8)

        tk.Label(wm_inner, text=tr("SCAN WAIT MODE"),
                 bg=T("SURFACE2"), fg=T("FG2"),
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 6))

        self._cond_wait_mode_var = tk.StringVar(value="wait_then_continue")
        wm_row = tk.Frame(wm_inner, bg=T("SURFACE2"))
        wm_row.pack(anchor="w")
        for val, lbl, desc in [
            ("wait_then_continue", tr("Timeout"),        tr("Scan for MAX WAIT, then go to ELSE")),
            ("wait_until_found",   tr("Wait until found"), tr("Keep scanning forever until found")),
        ]:
            col = tk.Frame(wm_row, bg=T("SURFACE2"))
            col.pack(side="left", padx=(0, 20))
            tk.Radiobutton(col, text=lbl,
                           variable=self._cond_wait_mode_var, value=val,
                           bg=T("SURFACE2"), fg=T("FG"),
                           selectcolor=T("CHECK_BG"),
                           activebackground=T("SURFACE2"),
                           activeforeground=T("FG"),
                           font=("Segoe UI", 9),
                           command=self._refresh_cond_maxwait).pack(anchor="w")
            tk.Label(col, text=desc,
                     bg=T("SURFACE2"), fg=T("FG3"),
                     font=("Segoe UI", 7)).pack(anchor="w")

        # Max wait satırı
        self._mw_holder = tk.Frame(body, bg=T("SURFACE"))
        self._mw_holder.pack(fill="x", pady=(0, 4))
        self._build_maxwait_row(self._mw_holder)

        # ── THEN block ────────────────────────────────────────────
        then_outer = tk.Frame(body, bg=T("SURFACE"))
        then_outer.pack(fill="x", pady=(6, 0))
        then_hdr = tk.Frame(then_outer, bg="#27AE60")
        then_hdr.pack(fill="x")
        tk.Label(then_hdr, text=tr("  ✓  IF FOUND — THEN"),
                 bg="#27AE60", fg="#FFFFFF",
                 font=("Segoe UI", 9, "bold"), pady=5).pack(side="left")
        then_body = tk.Frame(then_outer, bg=T("SURFACE2"),
                             relief="solid", bd=1,
                             highlightthickness=1,
                             highlightbackground=T("BORDER"))
        then_body.pack(fill="x")
        then_inner = tk.Frame(then_body, bg=T("SURFACE2"))
        then_inner.pack(fill="x", padx=14, pady=10)
        self._cond_then_var    = tk.StringVar(value="click_found")
        self._cond_then_detail = {}
        self._build_action_picker(then_inner, self._cond_then_var,
                                  self._cond_then_detail,
                                  include_click_found=True, branch="then")

        # ── ELSE block ────────────────────────────────────────────
        else_outer = tk.Frame(body, bg=T("SURFACE"))
        else_outer.pack(fill="x", pady=(8, 0))
        else_hdr = tk.Frame(else_outer, bg="#D35400")
        else_hdr.pack(fill="x")
        tk.Label(else_hdr, text=tr("  ✗  IF NOT FOUND — ELSE"),
                 bg="#D35400", fg="#FFFFFF",
                 font=("Segoe UI", 9, "bold"), pady=5).pack(side="left")
        else_body = tk.Frame(else_outer, bg=T("SURFACE2"),
                             relief="solid", bd=1,
                             highlightthickness=1,
                             highlightbackground=T("BORDER"))
        else_body.pack(fill="x")
        else_inner = tk.Frame(else_body, bg=T("SURFACE2"))
        else_inner.pack(fill="x", padx=14, pady=10)
        self._cond_else_var    = tk.StringVar(value="none")
        self._cond_else_detail = {}
        self._build_action_picker(else_inner, self._cond_else_var,
                                  self._cond_else_detail,
                                  include_click_found=False, branch="else")

        # ── ADD CONDITION STEP ────────────────────────────────────
        add_row = tk.Frame(body, bg=T("SURFACE"))
        add_row.pack(fill="x", pady=(12, 0))
        make_btn(add_row, tr("ADD CONDITION STEP"),
                 self._add_step_condition, primary=True).pack(side="left")

    def _build_maxwait_row(self, parent):
        row = tk.Frame(parent, bg=T("SURFACE"))
        row.pack(fill="x")
        tk.Label(row, text=tr("SCAN TIMEOUT  (0 = single scan)"),
                 bg=T("SURFACE"), fg=T("FG2"),
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 4))
        irow = tk.Frame(row, bg=T("SURFACE"))
        irow.pack(anchor="w")
        self._cond_maxwait_widget = make_interval_widget(
            irow, bg=T("SURFACE"), default_ms=0)
        ch = self._cond_maxwait_widget.winfo_children()
        if ch:
            ch[0].delete(0, tk.END)
            ch[0].insert(0, "0")
        self._cond_maxwait_widget.pack(side="left")
        self._cond_mw_hint = tk.Label(
            irow, text=tr("→ single scan"),
            bg=T("SURFACE"), fg=T("FG3"),
            font=("Segoe UI", 7, "italic"))
        self._cond_mw_hint.pack(side="left", padx=(8, 0))

        def _upd(*_):
            try:
                s = self._cond_maxwait_widget.get_seconds()
                if s <= 0.001:   h = tr("→ single scan")
                elif s < 1.0:    h = f"{tr('→ scan for')} {int(s*1000)} {tr('ms')}"
                elif s < 60:     h = f"{tr('→ scan for')} {s:.1f}{tr('s')}"
                else:            h = f"{tr('→ scan for')} {int(s//60)}{tr('m')} {int(s%60)}{tr('s')}"
                self._cond_mw_hint.config(text=h)
            except Exception:
                pass

        if ch:
            ch[0].bind("<KeyRelease>", lambda e: _upd())
        for w in irow.winfo_children():
            if hasattr(w, "bind"):
                w.bind("<<ComboboxSelected>>", lambda e: _upd())
        self._mw_row = row

    def _refresh_cond_maxwait(self):
        mode = self._cond_wait_mode_var.get()
        if mode == "wait_until_found":
            self._mw_row.pack_forget()
        else:
            self._mw_row.pack(fill="x")

    def _build_action_picker(self, parent, var, store,
                              include_click_found, branch):
        from tkinter import ttk as _ttk

        options_found = [
            ("click_found", tr("Click at found position")),
            ("click",       tr("Click at coordinates")),
            ("drag_to",     tr("Drag to coordinates")),
            ("scroll",      tr("Scroll")),
            ("type_text",   tr("Type text")),
            ("key",         tr("Press a key")),
            ("hotkey",      tr("Hotkey combo")),
            ("goto_step",   tr("Go to step N")),
            ("stop",        tr("Stop automation")),
            ("none",        tr("Do nothing")),
        ]
        options_notfound = [o for o in options_found if o[0] != "click_found"]
        opts    = options_found if include_click_found else options_notfound
        default = "click_found" if include_click_found else "none"
        var.set(default)

        vals    = [v for v, _ in opts]
        lbls    = [l for _, l in opts]

        cb_var = tk.StringVar(value=lbls[0])
        store["_cb_var"]   = cb_var
        store["_opt_vals"] = vals
        store["_opt_lbls"] = lbls
        store["_var"]      = var

        cb = _ttk.Combobox(parent, textvariable=cb_var, values=lbls,
                           state="readonly", font=("Segoe UI", 9), width=28)
        cb.current(0)
        cb.pack(anchor="w", pady=(0, 8), fill="x")

        detail_frame = tk.Frame(parent, bg=T("SURFACE2"))
        detail_frame.pack(fill="x")
        store["_frame"] = detail_frame

        def on_sel(e=None):
            sel = cb_var.get()
            try:
                idx = lbls.index(sel)
                var.set(vals[idx])
            except ValueError:
                var.set("none")
            self._refresh_cond_detail(branch)

        cb.bind("<<ComboboxSelected>>", on_sel)
        self._refresh_cond_detail(branch)

    def _refresh_cond_detail(self, branch):
        if branch == "then":
            var, store = self._cond_then_var, self._cond_then_detail
        else:
            var, store = self._cond_else_var, self._cond_else_detail

        frame = store.get("_frame")
        if not frame:
            return
        for w in frame.winfo_children():
            w.destroy()
        for k in list(store.keys()):
            if not k.startswith("_"):
                del store[k]

        atype = var.get()
        inner = tk.Frame(frame, bg=T("SURFACE2"))
        inner.pack(fill="x", padx=2, pady=4)

        if atype == "click_found":
            tk.Label(inner, text=tr("→ Clicks exactly where the image was found."),
                     bg=T("SURFACE2"), fg=T("FG2"),
                     font=("Segoe UI", 8, "italic")).pack(anchor="w")

        elif atype == "click":
            self._detail_xy(inner, store)

        elif atype == "drag_to":
            tk.Label(inner, text=tr("DRAG  FROM → TO"),
                     bg=T("SURFACE2"), fg=T("FG2"),
                     font=("Segoe UI", 7, "bold")).pack(anchor="w", pady=(0, 4))
            fr = tk.Frame(inner, bg=T("SURFACE2"))
            fr.pack(anchor="w")
            for lbl, k in [(tr("From X"), "from_x"), (tr("From Y"), "from_y"),
                            (tr("To X"),   "to_x"),   (tr("To Y"),   "to_y")]:
                c = tk.Frame(fr, bg=T("SURFACE2"))
                c.pack(side="left", padx=(0, 8))
                tk.Label(c, text=lbl, bg=T("SURFACE2"), fg=T("FG3"),
                         font=("Segoe UI", 7)).pack(anchor="w")
                e = self._small_entry(c, "0")
                store[k] = e

        elif atype == "scroll":
            pos_row = tk.Frame(inner, bg=T("SURFACE2"))
            pos_row.pack(anchor="w", pady=(0, 4))
            for lbl, k in [(tr("X"), "x"), (tr("Y"), "y")]:
                c = tk.Frame(pos_row, bg=T("SURFACE2"))
                c.pack(side="left", padx=(0, 8))
                tk.Label(c, text=lbl, bg=T("SURFACE2"), fg=T("FG3"),
                         font=("Segoe UI", 7)).pack(anchor="w")
                e = self._small_entry(c, "0")
                store[k] = e
            dy_row = tk.Frame(inner, bg=T("SURFACE2"))
            dy_row.pack(anchor="w")
            tk.Label(dy_row, text=tr("Amount (+ up / - down)"),
                     bg=T("SURFACE2"), fg=T("FG2"),
                     font=("Segoe UI", 8)).pack(side="left", padx=(0, 8))
            e = self._small_entry(dy_row, "3", w=5)
            store["dy"] = e

        elif atype == "type_text":
            tk.Label(inner, text=tr("TEXT TO TYPE"),
                     bg=T("SURFACE2"), fg=T("FG2"),
                     font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 3))
            e = tk.Entry(inner, width=26,
                         bg=T("ENTRY_BG"), fg=T("FG"),
                         relief="solid", bd=1,
                         highlightthickness=1,
                         highlightbackground=T("BORDER"),
                         highlightcolor=T("BORDER_STRONG"),
                         font=("Segoe UI", 9),
                         insertbackground=T("FG"))
            e.pack(anchor="w", fill="x")
            store["text"] = e

        elif atype == "key":
            tk.Label(inner, text=tr("KEY"),
                     bg=T("SURFACE2"), fg=T("FG2"),
                     font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 3))
            e = tk.Entry(inner, width=16,
                         bg=T("ENTRY_BG"), fg=T("FG"),
                         relief="solid", bd=1,
                         highlightthickness=1,
                         highlightbackground=T("BORDER"),
                         highlightcolor=T("BORDER_STRONG"),
                         font=("Segoe UI", 9),
                         insertbackground=T("FG"))
            e.pack(anchor="w")
            store["key"] = e

        elif atype == "hotkey":
            tk.Label(inner, text=tr("HOTKEY  (e.g. ctrl+c)"),
                     bg=T("SURFACE2"), fg=T("FG2"),
                     font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 3))
            e = tk.Entry(inner, width=16,
                         bg=T("ENTRY_BG"), fg=T("FG"),
                         relief="solid", bd=1,
                         highlightthickness=1,
                         highlightbackground=T("BORDER"),
                         highlightcolor=T("BORDER_STRONG"),
                         font=("Segoe UI", 9),
                         insertbackground=T("FG"))
            e.insert(0, "ctrl+c")
            e.pack(anchor="w")
            store["keys"] = e

        elif atype == "goto_step":
            row = tk.Frame(inner, bg=T("SURFACE2"))
            row.pack(anchor="w")
            tk.Label(row, text=tr("Go to step"),
                     bg=T("SURFACE2"), fg=T("FG2"),
                     font=("Segoe UI", 8)).pack(side="left", padx=(0, 8))
            e = tk.Entry(row, width=5,
                         bg=T("ENTRY_BG"), fg=T("FG"),
                         relief="solid", bd=1,
                         highlightthickness=1,
                         highlightbackground=T("BORDER"),
                         font=("Segoe UI", 10, "bold"), justify="center",
                         insertbackground=T("FG"))
            e.insert(0, "1")
            e.pack(side="left")
            tk.Label(row, text=tr("(1 = first step)"),
                     bg=T("SURFACE2"), fg=T("FG3"),
                     font=("Segoe UI", 7, "italic")).pack(side="left", padx=(8, 0))
            store["step_number"] = e

        elif atype == "stop":
            tk.Label(inner, text=tr("→ Stops the automation."),
                     bg=T("SURFACE2"), fg=T("FG2"),
                     font=("Segoe UI", 8, "italic")).pack(anchor="w")
        else:
            tk.Label(inner, text=tr("→ No action — skipped."),
                     bg=T("SURFACE2"), fg=T("FG3"),
                     font=("Segoe UI", 8, "italic")).pack(anchor="w")

    def _detail_xy(self, parent, store):
        row = tk.Frame(parent, bg=T("SURFACE2"))
        row.pack(anchor="w", pady=(0, 4))
        for lbl, k in [(tr("X"), "x"), (tr("Y"), "y")]:
            c = tk.Frame(row, bg=T("SURFACE2"))
            c.pack(side="left", padx=(0, 10))
            tk.Label(c, text=lbl, bg=T("SURFACE2"), fg=T("FG2"),
                     font=("Segoe UI", 7)).pack(anchor="w")
            e = self._small_entry(c, "0", w=7)
            store[k] = e
        btn_var = tk.StringVar(value="left")
        btn_row = tk.Frame(parent, bg=T("SURFACE2"))
        btn_row.pack(anchor="w")
        for val, lbl in [("left",tr("L")), ("right",tr("R")), ("middle",tr("M"))]:
            tk.Radiobutton(btn_row, text=lbl, variable=btn_var, value=val,
                           bg=T("SURFACE2"), fg=T("FG"),
                           selectcolor=T("SURFACE"),
                           activebackground=T("SURFACE2"),
                           activeforeground=T("FG"),
                           font=("Segoe UI", 8)).pack(side="left", padx=(0, 8))
        store["button"] = btn_var

    def _small_entry(self, parent, default, w=7):
        e = tk.Entry(parent, width=w,
                     bg=T("ENTRY_BG"), fg=T("FG"),
                     relief="solid", bd=1,
                     highlightthickness=1,
                     highlightbackground=T("BORDER"),
                     highlightcolor=T("BORDER_STRONG"),
                     font=("Segoe UI", 9), justify="center",
                     insertbackground=T("FG"))
        e.insert(0, default)
        e.pack()
        e.bind("<FocusIn>",  lambda ev, w=e: w.config(highlightthickness=2))
        e.bind("<FocusOut>", lambda ev, w=e: w.config(highlightthickness=1))
        return e

    def _get_condition_action(self, var, store):
        atype  = var.get()
        action = {"type": atype}
        if atype == "click":
            try: action["x"] = int(store["x"].get())
            except Exception: action["x"] = 0
            try: action["y"] = int(store["y"].get())
            except Exception: action["y"] = 0
            btn_v = store.get("button")
            action["button"] = btn_v.get() if btn_v else "left"
        elif atype == "drag_to":
            for k in ("from_x", "from_y", "to_x", "to_y"):
                try: action[k] = int(store[k].get())
                except Exception: action[k] = 0
        elif atype == "scroll":
            for k in ("x", "y"):
                try: action[k] = int(store[k].get())
                except Exception: action[k] = 0
            try: action["dy"] = int(store["dy"].get())
            except Exception: action["dy"] = 3
        elif atype == "type_text":
            w = store.get("text")
            action["text"] = w.get() if w else ""
        elif atype == "key":
            w = store.get("key")
            action["key"] = w.get().strip() if w else ""
        elif atype == "hotkey":
            w = store.get("keys")
            action["keys"] = w.get().strip() if w else "ctrl+c"
        elif atype == "goto_step":
            w = store.get("step_number")
            try: action["step_number"] = int(w.get()) if w else 1
            except Exception: action["step_number"] = 1
        return action

    def _add_step_condition(self):
        """IF IMAGE step oluştur ve steps listesine ekle."""
        if not self._has_images():
            self.status_lbl.config(
                text=tr("PLEASE ADD AT LEAST ONE IMAGE."), fg=T("FG2"))
            return

        wait_mode = getattr(self, "_cond_wait_mode_var",
                            tk.StringVar(value="wait_then_continue")).get()
        max_wait  = 0.0
        if wait_mode == "wait_then_continue" and hasattr(self, "_cond_maxwait_widget"):
            mw = self._cond_maxwait_widget.get_seconds()
            max_wait = 0.0 if mw <= 0.001 else mw

        cmode          = getattr(self, "_cond_mode_var", None)
        condition_mode = cmode.get() if cmode else "OR"

        img_list    = self.get_image_list()
        first       = img_list[0]
        then_action = self._get_condition_action(
            self._cond_then_var, self._cond_then_detail)
        else_action = self._get_condition_action(
            self._cond_else_var, self._cond_else_detail)

        step = {
            "type":           "if_image",
            "confidence":     first["confidence"],
            "scan_interval":  self.scan_interval_widget.get_seconds(),
            "button":         self.click_var.get(),
            "area":           list(self.area) if self.area else None,
            "max_wait":       max_wait,
            "wait_mode":      wait_mode,
            "condition_mode": condition_mode,
            "image_path":     first["path"],
            "clipboard_image": first["array"].tolist() if first["array"] is not None else None,
            "image_list": [
                {
                    "path":       item["path"],
                    "array":      item["array"].tolist() if item["array"] is not None else None,
                    "confidence": item["confidence"],
                    "label":      item["label"],
                }
                for item in img_list
            ],
            "then_action":    then_action,
            "else_action":    else_action,
            "interval":       0.1,
            "repeat":         1,
        }
        self.on_add_step(step)
        then_t = then_action.get("type", "none").upper()
        else_t = else_action.get("type", "none").upper()
        self.status_lbl.config(
            text=f"{tr('CONDITION STEP ADDED')}  ✓ {then_t}  ✗ {else_t}",
            fg=T("FG"))

    def _load_condition_data(self, d: dict):
        """Profil dict'inden koşul ayarlarını geri yükle."""
        wm = d.get("cond_wait_mode", "wait_then_continue")
        if hasattr(self, "_cond_wait_mode_var"):
            self._cond_wait_mode_var.set(wm)
            self._refresh_cond_maxwait()

        cm = d.get("cond_condition_mode", "OR")
        if hasattr(self, "_cond_mode_var"):
            self._cond_mode_var.set(cm)

        mw_val  = d.get("cond_maxwait_val",  "0")
        mw_unit = d.get("cond_maxwait_unit", "MS")
        if hasattr(self, "_cond_maxwait_widget"):
            ch = self._cond_maxwait_widget.winfo_children()
            if ch:
                ch[0].delete(0, tk.END)
                ch[0].insert(0, str(mw_val))
            if len(ch) > 1:
                ch[1].set(mw_unit)

        then_data = d.get("cond_then_action", {})
        if then_data and hasattr(self, "_cond_then_var"):
            self._load_branch_action(then_data, self._cond_then_var,
                                     self._cond_then_detail, "then")
        else_data = d.get("cond_else_action", {})
        if else_data and hasattr(self, "_cond_else_var"):
            self._load_branch_action(else_data, self._cond_else_var,
                                     self._cond_else_detail, "else")

    def _load_branch_action(self, action_data: dict, var, store, branch: str):
        atype      = action_data.get("type", "none")
        store_lbls = store.get("_opt_lbls", [])
        store_vals = store.get("_opt_vals", [])
        cb_var     = store.get("_cb_var")
        try:
            idx = store_vals.index(atype)
            if cb_var:
                cb_var.set(store_lbls[idx])
        except (ValueError, IndexError):
            pass
        var.set(atype)
        self._refresh_cond_detail(branch)
        if atype == "click":
            for k in ("x", "y"):
                w = store.get(k)
                if w:
                    w.delete(0, tk.END)
                    w.insert(0, str(action_data.get(k, 0)))
            bv = store.get("button")
            if bv:
                bv.set(action_data.get("button", "left"))
        elif atype == "drag_to":
            for k in ("from_x", "from_y", "to_x", "to_y"):
                w = store.get(k)
                if w:
                    w.delete(0, tk.END)
                    w.insert(0, str(action_data.get(k, 0)))
        elif atype == "scroll":
            for k in ("x", "y", "dy"):
                w = store.get(k)
                if w:
                    w.delete(0, tk.END)
                    w.insert(0, str(action_data.get(k, 0 if k != "dy" else 3)))
        elif atype == "type_text":
            w = store.get("text")
            if w:
                w.delete(0, tk.END)
                w.insert(0, action_data.get("text", ""))
        elif atype == "key":
            w = store.get("key")
            if w:
                w.delete(0, tk.END)
                w.insert(0, action_data.get("key", ""))
        elif atype == "hotkey":
            w = store.get("keys")
            if w:
                w.delete(0, tk.END)
                w.insert(0, action_data.get("keys", "ctrl+c"))
        elif atype == "goto_step":
            w = store.get("step_number")
            if w:
                w.delete(0, tk.END)
                w.insert(0, str(action_data.get("step_number", 1)))

    def update_status(self, text, color=None):
        self.status_lbl.config(
            text=text.upper(), fg=color or T("FG2"))

    def set_state(self, s):
        try:
            self.start_btn.config(state=s)
        except Exception:
            pass
        self.scan_interval_widget.set_state(s)

    def refresh_labels(self):
        pass

    # ── Profile support ───────────────────────────────────────────

    def _iw_vals(self, widget):
        ch = widget.winfo_children()
        return (ch[0].get() if ch else "500",
                ch[1].get() if len(ch) > 1 else "MS")

    def _iw_load(self, widget, val, unit):
        ch = widget.winfo_children()
        if ch:
            ch[0].delete(0, "end")
            ch[0].insert(0, str(val))
        if len(ch) > 1:
            ch[1].set(unit)

    def get_profile_data(self) -> dict:
        siv, siu = self._iw_vals(self.scan_interval_widget)
        stv, stu = self._iw_vals(self.step_interval_widget)
        img_list = self.get_image_list()

        # Koşul ayarları — widget henüz oluşturulmamışsa güvenli fallback
        then_action  = {}
        else_action  = {}
        cond_mw_val  = "0"
        cond_mw_unit = "MS"
        if hasattr(self, "_cond_then_var"):
            then_action = self._get_condition_action(
                self._cond_then_var, self._cond_then_detail)
        if hasattr(self, "_cond_else_var"):
            else_action = self._get_condition_action(
                self._cond_else_var, self._cond_else_detail)
        if hasattr(self, "_cond_maxwait_widget"):
            cond_mw_val, cond_mw_unit = self._iw_vals(self._cond_maxwait_widget)

        return {
            "image_path":         self.image_path,
            "confidence":         self.conf_slider.get_val(),
            "repeat":             self.repeat_entry.get(),
            "infinite":           self.infinite_var.get(),
            "scan_interval_val":  siv,
            "scan_interval_unit": siu,
            "step_interval_val":  stv,
            "step_interval_unit": stu,
            "button":             self.click_var.get(),
            "image_list": [
                {
                    "path":       item["path"],
                    "array":      item["array"].tolist() if item["array"] is not None else None,
                    "confidence": item["confidence"],
                    "label":      item["label"],
                }
                for item in img_list
            ],
            # Koşul adımı ayarları
            "cond_then_action":   then_action,
            "cond_else_action":   else_action,
            "cond_maxwait_val":   cond_mw_val,
            "cond_maxwait_unit":  cond_mw_unit,
        }

    def load_profile_data(self, d: dict):
        if not d:
            return
        try:
            self._clear_all_images()
            img_list = d.get("image_list", [])
            if img_list:
                for item in img_list:
                    path  = item.get("path")
                    raw   = item.get("array")
                    conf  = item.get("confidence", 0.8)
                    label = item.get("label", "")
                    arr   = np.array(raw, dtype=np.uint8) if raw is not None else None
                    if path and not os.path.isfile(path):
                        path = None
                    if path is not None or arr is not None:
                        self.conf_slider.set_val(conf)
                        self._add_image_to_list(label or (os.path.basename(path) if path else "Clipboard"), path, arr, conf)
            elif d.get("image_path") and os.path.isfile(d["image_path"]):
                path  = d["image_path"]
                label = os.path.basename(path)
                self._add_image_to_list(label, path, None, float(d.get("confidence", 0.8)))

            self.conf_slider.set_val(float(d.get("confidence", 0.8)))
            self.repeat_entry.delete(0, "end")
            self.repeat_entry.insert(0, str(d.get("repeat", "1")))
            self.infinite_var.set(d.get("infinite", False))
            self._toggle_infinite()
            self._iw_load(self.scan_interval_widget,
                          d.get("scan_interval_val", "500"),
                          d.get("scan_interval_unit", "MS"))
            self._iw_load(self.step_interval_widget,
                          d.get("step_interval_val", "0"),
                          d.get("step_interval_unit", "MS"))
            self.click_var.set(d.get("button", "left"))

            # ── Koşul ayarlarını yükle ────────────────────────────
            self._load_condition_data(d)

        except Exception as e:
            print(f"[ImagePanel] load_profile_data error: {e}")

    def _load_condition_data(self, d: dict):
        """Profil dict'inden koşul (IF/THEN/ELSE) ayarlarını geri yükle."""
        mw_val  = d.get("cond_maxwait_val",  "0")
        mw_unit = d.get("cond_maxwait_unit", "MS")
        if hasattr(self, "_cond_maxwait_widget"):
            self._iw_load(self._cond_maxwait_widget, mw_val, mw_unit)

        then_data = d.get("cond_then_action", {})
        if then_data and hasattr(self, "_cond_then_var"):
            self._load_branch_action(
                then_data, self._cond_then_var,
                self._cond_then_detail, "then")

        else_data = d.get("cond_else_action", {})
        if else_data and hasattr(self, "_cond_else_var"):
            self._load_branch_action(
                else_data, self._cond_else_var,
                self._cond_else_detail, "else")

    def _load_branch_action(self, action_data: dict, var, store, branch: str):
        """Tek bir THEN/ELSE dalını action_data dict'inden yükle."""
        atype = action_data.get("type", "none")
        var.set(atype)
        self._refresh_cond_detail(branch)
        if atype == "click":
            xe = store.get("x")
            ye = store.get("y")
            if xe:
                xe.delete(0, tk.END)
                xe.insert(0, str(action_data.get("x", 0)))
            if ye:
                ye.delete(0, tk.END)
                ye.insert(0, str(action_data.get("y", 0)))
            btn_v = store.get("button")
            if btn_v:
                btn_v.set(action_data.get("button", "left"))
        elif atype == "key":
            ke = store.get("key")
            if ke:
                ke.delete(0, tk.END)
                ke.insert(0, action_data.get("key", ""))
        elif atype == "hotkey":
            he = store.get("keys")
            if he:
                he.delete(0, tk.END)
                he.insert(0, action_data.get("keys", "ctrl+c"))
