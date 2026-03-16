import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys

from ui.theme import T, divider, make_btn, make_icon_btn, make_entry
from utils.i18n import tr

DONATE_DATA = [
    {
        "name": "Buy Me A Coffee",
        "address": "https://buymeacoffee.com/osenpa",
        "image": "image1.png",
        "warning": ""
    },
    {
        "name": "Bitcoin (BTC/SegWit)",
        "address": "bc1q4v6c6a0ru4nf70p66rgwp92w3z89cpvh7a445e",
        "image": "image2.jpeg",
        "warning": ""
    },
    {
        "name": "Ethereum (ERC-20)",
        "address": "0xda8de84d6e71d180705d036eaa364b5324ee6b6d",
        "image": "image3.jpeg",
        "warning": ""
    },
    {
        "name": "USDT (Tron/TRC20)",
        "address": "TEvxij9k6jKjkj19VSS62KYR9VKF8YodJg",
        "image": "image4.jpeg",
        "warning": ""
    },
    {
        "name": "USDT (Ethereum/ERC20)",
        "address": "0xda8de84d6e71d180705d036eaa364b5324ee6b6d",
        "image": "image5.jpeg",
        "warning": ""
    },
    {
        "name": "USDC (Ethereum/ERC20)",
        "address": "0xda8de84d6e71d180705d036eaa364b5324ee6b6d",
        "image": "image6.jpeg",
        "warning": ""
    },
    {
        "name": "USDC (Solana)",
        "address": "66EyabUsviRTsGZnr3xZtw2XMQ1Eyd5cEK43VqT1R4He",
        "image": "image7.jpeg",
        "warning": ""
    },
    {
        "name": "Dash",
        "address": "Xjw4Jg2rjXcYnaWvTGaBJWvDLR289yqhzR",
        "image": "image8.jpeg",
        "warning": ""
    },
    {
        "name": "BNB (BEP20)",
        "address": "0xda8de84d6e71d180705d036eaa364b5324ee6b6d",
        "image": "image9.jpeg",
        "warning": ""
    },
    {
        "name": "Bitcoin Cash (BCH)",
        "address": "14URHQqheuRis7HBUrrvw5dPh7bLeTM2zL",
        "image": "image10.jpeg",
        "warning": "ATTENTION: This address is only for Bitcoin Cash (BCH). Do not send regular Bitcoin (BTC)!"
    },
    {
        "name": "Litecoin (LTC)",
        "address": "LPECpKGpcMk9f4dLnxC1JYSvGVyv5m7GNg",
        "image": "image11.jpeg",
        "warning": ""
    },
    {
        "name": "Cardano (ADA)",
        "address": "addr1vyeaxft88ztd4yw39r3c9s623tdq23k3pg05v3aznhn7xds9pfw7x",
        "image": "image12.jpeg",
        "warning": ""
    },
    {
        "name": "Doge",
        "address": "DQj2XmPutvqEWPA7fErsyAsejHYyiGxEX4",
        "image": "image13.jpeg",
        "warning": ""
    },
    {
        "name": "Solana (SOL)",
        "address": "66EyabUsviRTsGZnr3xZtw2XMQ1Eyd5cEK43VqT1R4He",
        "image": "image14.jpeg",
        "warning": ""
    }
]

class DonatePanel:
    def __init__(self, parent):
        self.box = tk.Frame(parent, bg=T("SURFACE"))
        self.box.pack(fill="both", expand=True)
        self._intro_label = None
        self._qr_images = {}  # References to keep images alive
        self._qr_labels = {}  # References to dynamically update images on theme change
        self._warning_labels = []
        self._is_expanded = False
        self._more_btn_frame = None
        self._build()

    def _build(self):
        box = self.box

        # Scrollable canvas
        canvas = tk.Canvas(box, bg=T("SURFACE"), highlightthickness=0)
        sb = tk.Scrollbar(box, orient="vertical", command=canvas.yview,
                           bg=T("SCROLL_BG"), troughcolor=T("SCROLL_BG"),
                           activebackground=T("SCROLL_ACTIVE"),
                           relief="flat", bd=0, width=10)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        wrap = tk.Frame(canvas, bg=T("SURFACE"))
        win_id = canvas.create_window((0, 0), window=wrap, anchor="nw")

        def on_frame_resize(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_resize(e):
            canvas.itemconfig(win_id, width=e.width)
            new_wl = max(200, e.width - 80)
            if self._intro_label:
                try:
                    self._intro_label.config(wraplength=new_wl)
                except Exception:
                    pass
            for w in self._warning_labels:
                try:
                    w.config(wraplength=max(100, new_wl - 250))
                except Exception:
                    pass

        wrap.bind("<Configure>", on_frame_resize)
        canvas.bind("<Configure>", on_canvas_resize)

        canvas.bind("<Enter>",
            lambda e: canvas.bind_all("<MouseWheel>",
                lambda ev: canvas.yview_scroll(int(-1*(ev.delta/120)), "units")))
        canvas.bind("<Leave>",
            lambda e: canvas.unbind_all("<MouseWheel>"))

        # Title
        title_bar = tk.Frame(wrap, bg=T("SURFACE"))
        title_bar.pack(fill="x", padx=36, pady=(28, 6))
        tk.Label(title_bar, text=tr("SUPPORT & DONATE"),
                  bg=T("SURFACE"), fg=T("PRIMARY_BG"),
                  font=("Segoe UI", 16, "bold")).pack(anchor="w")

        # Intro text
        intro_text = tr("We hope this app is serving you well! If it’s made your job a bit easier, your support would mean the world to us. It helps us stay dedicated to building and releasing more free projects for the community.")
        self._intro_label = tk.Label(title_bar, text=intro_text,
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 10), justify="left")
        self._intro_label.pack(anchor="w", pady=(10, 0))

        divider(wrap, padx=36, pady=(14, 0))

        # Cards container
        self._cards_frame = tk.Frame(wrap, bg=T("SURFACE"))
        self._cards_frame.pack(fill="x", padx=36, pady=(0, 20))

        # We will render a limited number of cards initially to improve load time
        self._render_cards(self._cards_frame, DONATE_DATA[:3])

        if len(DONATE_DATA) > 3:
            self._more_btn_frame = tk.Frame(wrap, bg=T("SURFACE"))
            self._more_btn_frame.pack(fill="x", pady=(0, 20))
            make_btn(self._more_btn_frame, tr("SHOW ALL OPTIONS"),
                      self._show_all_cards).pack()

    def _show_all_cards(self):
        if self._more_btn_frame:
            self._more_btn_frame.pack_forget()
        self._render_cards(self._cards_frame, DONATE_DATA[3:])
        self._is_expanded = True
        self.box.after(100, lambda: self._cards_frame.event_generate("<Configure>"))

    def _render_cards(self, parent, data_list):
        assets_dir = self._resolve_assets_dir()

        for d in data_list:
            card = tk.Frame(parent, bg=T("SURFACE2"), relief="solid", bd=1)
            card.config(highlightbackground=T("BORDER"), highlightthickness=1)
            card.pack(fill="x", pady=(0, 16))

            header = tk.Frame(card, bg=T("ENTRY_BG"))
            header.pack(fill="x", padx=1, pady=1)
            tk.Label(header, text=d["name"],
                      bg=T("ENTRY_BG"), fg=T("FG"),
                      font=("Segoe UI", 11, "bold")).pack(side="left", padx=12, pady=8)

            body = tk.Frame(card, bg=T("SURFACE2"))
            body.pack(fill="x", padx=16, pady=16)

            left_col = tk.Frame(body, bg=T("SURFACE2"))
            left_col.pack(side="left", fill="both", expand=True)

            tk.Label(left_col, text=tr("ADDRESS / LINK"),
                      bg=T("SURFACE2"), fg=T("FG2"),
                      font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 4))
            
            addr_entry = make_entry(left_col, width=40)
            addr_entry.insert(0, d["address"])
            addr_entry.config(state="readonly", readonlybackground=T("ENTRY_BG"), fg=T("FG"))
            addr_entry.pack(fill="x", pady=(0, 12))

            btn_row = tk.Frame(left_col, bg=T("SURFACE2"))
            btn_row.pack(anchor="w")

            def make_copy_cmd(addr=d["address"]):
                def _c():
                    self.box.clipboard_clear()
                    self.box.clipboard_append(addr)
                    messagebox.showinfo(tr("Copied"), tr("Address copied to clipboard!"))
                return _c

            make_btn(btn_row, tr("COPY ADDRESS"),
                      make_copy_cmd(), primary=True).pack(side="left", padx=(0, 8))

            if d["name"] == "Buy Me A Coffee":
                def open_link(url=d["address"]):
                    import webbrowser
                    webbrowser.open_new(url)
                make_btn(btn_row, tr("OPEN LINK"), open_link).pack(side="left")

            if d["warning"]:
                w_lbl = tk.Label(left_col, text=d["warning"],
                                  bg=T("SURFACE2"), fg=T("DANGER"),
                                  font=("Segoe UI", 8, "bold"),
                                  justify="left")
                w_lbl.pack(anchor="w", pady=(12, 0))
                self._warning_labels.append(w_lbl)

            right_col = tk.Frame(body, bg=T("SURFACE2"))
            right_col.pack(side="right", padx=(16, 0))

            img_path = os.path.join(assets_dir, d["image"])
            if os.path.exists(img_path):
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(img_path)
                    img = img.resize((100, 100), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self._qr_images[d["name"]] = photo
                    
                    lbl = tk.Label(right_col, image=photo, bg=T("SURFACE2"))
                    lbl.pack()
                except Exception as e:
                    tk.Label(right_col, text="QR Error",
                              bg=T("SURFACE2"), fg=T("DANGER")).pack()

    def refresh_labels(self):
        pass

    def _resolve_assets_dir(self):
        # Dev/runtime path
        candidates = [os.path.join(os.path.dirname(__file__), "assets")]

        # PyInstaller runtime paths (both common layouts)
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(os.path.join(meipass, "ui", "assets"))
            candidates.append(os.path.join(meipass, "osenpa", "ui", "assets"))

        exe_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else None
        if exe_dir:
            candidates.append(os.path.join(exe_dir, "_internal", "ui", "assets"))
            candidates.append(os.path.join(exe_dir, "_internal", "osenpa", "ui", "assets"))

        for path in candidates:
            if os.path.isdir(path):
                return path

        return candidates[0]
