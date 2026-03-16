"""
Profiles Panel — Osenpa Auto Clicker
Save, load, delete, rename panel configurations.
"""
import tkinter as tk
from tkinter import messagebox
import time
from ui.theme import (make_btn, section_title, divider, T)
from utils.profile_manager import (
    list_profiles, save_profile, load_profile,
    delete_profile, rename_profile
)
from utils.i18n import tr

TAB_LABELS = {
    "keyboard": tr("Keyboard"),
    "mouse":    tr("Mouse"),
    "color":    tr("Color Detection"),
    "image":    tr("Image Detection"),
    "macro":    tr("Record Actions"),
}


class ProfilesPanel:
    def __init__(self, parent,
                 on_save_request,
                 on_load_request,
                 on_tab_change):
        self.on_save_request = on_save_request
        self.on_load_request = on_load_request
        self.on_tab_change   = on_tab_change
        self._profiles          = []
        self._filtered_profiles = []
        self._selected_path     = None

        self.box = tk.Frame(parent, bg=T("SURFACE"))
        self.box.pack(fill="both", expand=True)
        self._build()
        self._refresh_list()

    def _build(self):
        box = self.box

        # Title
        title_bar = tk.Frame(box, bg=T("SURFACE"))
        title_bar.pack(fill="x", padx=32, pady=(28, 6))
        tk.Label(title_bar, text=tr("PROFILES"),
                  bg=T("SURFACE"), fg=T("FG"),
                  font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(title_bar,
                  text=tr("Save and load your panel configurations"),
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 0))

        divider(box, padx=32, pady=(14, 0))

        # ── Two-column layout with PanedWindow for responsive resize ──
        # Use grid so both columns resize predictably
        content = tk.Frame(box, bg=T("SURFACE"))
        content.pack(fill="both", expand=True, padx=32, pady=(20, 20))
        content.columnconfigure(0, weight=3, minsize=180)
        content.columnconfigure(1, weight=0, minsize=200)
        content.rowconfigure(0, weight=1)

        # Left: list (expands)
        left = tk.Frame(content, bg=T("SURFACE"))
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        # Right: detail panel — scrollable so it never clips
        right_outer = tk.Frame(content, bg=T("SURFACE"), width=220)
        right_outer.grid(row=0, column=1, sticky="nsew")
        right_outer.grid_propagate(False)

        # Scrollable right column
        r_canvas = tk.Canvas(right_outer, bg=T("SURFACE"),
                              highlightthickness=0, width=220)
        r_sb = tk.Scrollbar(right_outer, orient="vertical",
                             command=r_canvas.yview,
                             bg=T("SCROLL_BG"), troughcolor=T("SCROLL_BG"),
                             activebackground=T("SCROLL_ACTIVE"),
                             relief="flat", bd=0, width=8)
        r_canvas.configure(yscrollcommand=r_sb.set)
        r_canvas.pack(side="left", fill="both", expand=True)

        right = tk.Frame(r_canvas, bg=T("SURFACE"))
        r_win = r_canvas.create_window((0, 0), window=right, anchor="nw")

        def _r_cfg(e):
            r_canvas.configure(scrollregion=r_canvas.bbox("all"))
            # Show scrollbar only when needed
            bb = r_canvas.bbox("all")
            if bb and (bb[3] - bb[1]) > r_canvas.winfo_height():
                if not r_sb.winfo_ismapped():
                    r_sb.pack(side="right", fill="y", before=r_canvas)
            else:
                r_sb.pack_forget()

        def _r_cwidth(e):
            r_canvas.itemconfig(r_win, width=e.width)

        right.bind("<Configure>", _r_cfg)
        r_canvas.bind("<Configure>", _r_cwidth)
        r_canvas.bind("<Enter>",
            lambda e: r_canvas.bind_all("<MouseWheel>",
                lambda ev: r_canvas.yview_scroll(int(-1*(ev.delta/120)), "units")))
        r_canvas.bind("<Leave>",
            lambda e: r_canvas.unbind_all("<MouseWheel>"))

        self._build_list(left)
        self._build_detail(right)

    def _build_list(self, parent):
        section_title(parent, tr("SAVED PROFILES"), bg=T("SURFACE"))

        # Search
        search_outer = tk.Frame(parent, bg=T("ENTRY_BG"),
                                relief="solid", bd=1,
                                highlightthickness=1,
                                highlightbackground=T("BORDER"))
        search_outer.pack(fill="x", pady=(0, 6))

        self._profile_search = tk.Entry(
            search_outer,
            bg=T("ENTRY_BG"), fg=T("FG2"),
            relief="flat", bd=0, highlightthickness=0,
            font=("Segoe UI", 9),
            insertbackground=T("FG")
        )
        self._profile_search.pack(fill="x", expand=True, pady=4, padx=8)
        self._profile_search.insert(0, tr("Search profiles..."))

        def _sf_in(e):
            if self._profile_search.get() == tr("Search profiles..."):
                self._profile_search.delete(0, "end")
                self._profile_search.config(fg=T("FG"))
            search_outer.config(highlightbackground=T("BORDER_STRONG"),
                                highlightthickness=2)
        def _sf_out(e):
            if self._profile_search.get().strip() == "":
                self._profile_search.insert(0, tr("Search profiles..."))
                self._profile_search.config(fg=T("FG2"))
            search_outer.config(highlightbackground=T("BORDER"),
                                highlightthickness=1)

        self._profile_search.bind("<FocusIn>",   _sf_in)
        self._profile_search.bind("<FocusOut>",  _sf_out)
        self._profile_search.bind("<KeyRelease>", lambda e: self._apply_filter())

        # List frame
        list_frame = tk.Frame(
            parent,
            bg=T("ENTRY_BG"),
            relief="solid", bd=1,
            highlightthickness=1,
            highlightbackground=T("BORDER")
        )
        list_frame.pack(fill="both", expand=True)

        sb = tk.Scrollbar(list_frame, orient="vertical",
                           bg=T("SCROLL_BG"),
                           troughcolor=T("SCROLL_BG"),
                           activebackground=T("SCROLL_ACTIVE"))
        sb.pack(side="right", fill="y")

        self._listbox = tk.Listbox(
            list_frame,
            yscrollcommand=sb.set,
            bg=T("ENTRY_BG"), fg=T("FG"),
            selectbackground=T("PRIMARY_BG"),
            selectforeground=T("PRIMARY_FG"),
            font=("Segoe UI", 10),
            relief="flat", bd=0,
            highlightthickness=0,
            activestyle="none",
            cursor="hand2"
        )
        self._listbox.pack(side="left", fill="both", expand=True,
                           padx=2, pady=2)
        sb.config(command=self._listbox.yview)
        self._listbox.bind("<<ListboxSelect>>", self._on_select)
        self._listbox.bind("<Double-Button-1>", lambda e: self._load())

        # Empty state — a dedicated full-size frame inside the list_frame
        # so the label never overflows the list border
        self._empty_frame = tk.Frame(list_frame, bg=T("ENTRY_BG"))
        self._empty_lbl = tk.Label(
            self._empty_frame,
            text=tr("No saved profiles yet.\nClick  SAVE CURRENT  to create one."),
            bg=T("ENTRY_BG"), fg=T("FG3"),
            font=("Segoe UI", 9), justify="center",
            wraplength=160
        )
        self._empty_lbl.place(relx=0.5, rely=0.5, anchor="center")
        # Keep wraplength 40px narrower than the container
        def _update_empty_wrap(e):
            w = max(80, e.width - 40)
            self._empty_lbl.config(wraplength=w)
        self._empty_frame.bind("<Configure>", _update_empty_wrap)

        # Refresh button
        refresh_row = tk.Frame(parent, bg=T("SURFACE"))
        refresh_row.pack(fill="x", pady=(8, 0))
        make_btn(refresh_row, tr("↺  REFRESH"),
                  self._refresh_list, small=True).pack(side="left")

    def _build_detail(self, parent):
        section_title(parent, tr("SAVE CURRENT SETTINGS"), bg=T("SURFACE"))

        tk.Label(parent, text=tr("PROFILE NAME"),
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 4))

        self._name_entry = tk.Entry(
            parent, width=22,
            bg=T("ENTRY_BG"), fg=T("FG"),
            relief="solid", bd=1,
            highlightthickness=1,
            highlightbackground=T("BORDER"),
            highlightcolor=T("BORDER_STRONG"),
            font=("Segoe UI", 9),
            insertbackground=T("FG")
        )
        self._name_entry.pack(fill="x", pady=(0, 4))
        self._name_entry.bind("<FocusIn>",
            lambda e: self._name_entry.config(highlightthickness=2))
        self._name_entry.bind("<FocusOut>",
            lambda e: self._name_entry.config(highlightthickness=1))
        self._name_entry.bind("<Return>", lambda e: self._save())

        tk.Label(parent, text=tr("SAVE SETTINGS FROM"),
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", pady=(8, 4))

        self._scope_options = [
            (tr("All panels"),       "all"),
            (tr("Keyboard"),         "keyboard"),
            (tr("Mouse"),            "mouse"),
            (tr("Color Detection"),  "color"),
            (tr("Image Detection"),  "image"),
        ]
        self._tab_var = tk.StringVar(value=tr("All panels"))

        scope_menu = tk.OptionMenu(
            parent, self._tab_var,
            *[label for label, _ in self._scope_options]
        )
        scope_menu.config(
            bg=T("ENTRY_BG"), fg=T("FG"),
            font=("Segoe UI", 9),
            relief="solid", bd=1,
            highlightthickness=0,
            activebackground=T("SURFACE2"),
            activeforeground=T("FG"),
            cursor="hand2"
        )
        scope_menu["menu"].config(
            bg=T("ENTRY_BG"), fg=T("FG"),
            font=("Segoe UI", 9))
        scope_menu.pack(fill="x", pady=(0, 10))

        self._save_btn = make_btn(
            parent, tr("💾  SAVE CURRENT"), self._save, primary=True)
        self._save_btn.pack(fill="x", pady=(0, 2))

        self._save_status = tk.Label(
            parent, text="",
            bg=T("SURFACE"), fg=T("FG2"),
            font=("Segoe UI", 8), wraplength=200)
        self._save_status.pack(anchor="w", pady=(2, 0))

        divider(parent, pady=(16, 16))

        section_title(parent, tr("SELECTED PROFILE"), bg=T("SURFACE"))

        self._sel_lbl = tk.Label(
            parent, text=tr("— none selected —"),
            bg=T("SURFACE"), fg=T("FG3"),
            font=("Segoe UI", 9, "italic"), wraplength=200, justify="left")
        self._sel_lbl.pack(anchor="w", pady=(0, 10))

        self._meta_lbl = tk.Label(
            parent, text="",
            bg=T("SURFACE"), fg=T("FG3"),
            font=("Segoe UI", 7), wraplength=200, justify="left")
        self._meta_lbl.pack(anchor="w", pady=(0, 10))

        self._load_btn = make_btn(
            parent, tr("▶  LOAD PROFILE"), self._load, primary=True)
        self._load_btn.config(state="disabled")
        self._load_btn.pack(fill="x", pady=(0, 6))

        self._rename_btn = make_btn(
            parent, tr("✏  RENAME"), self._rename)
        self._rename_btn.config(state="disabled")
        self._rename_btn.pack(fill="x", pady=(0, 6))

        self._delete_btn = make_btn(
            parent, tr("✕  DELETE"), self._delete)
        self._delete_btn.config(state="disabled")
        self._delete_btn.pack(fill="x")

        self._action_status = tk.Label(
            parent, text="",
            bg=T("SURFACE"), fg=T("FG2"),
            font=("Segoe UI", 8), wraplength=200)
        self._action_status.pack(anchor="w", pady=(8, 16))

    # ── List management ─────────────────────────────────────────

    def _refresh_list(self):
        self._profiles = list_profiles()
        self._apply_filter()
        self._selected_path = None
        self._update_detail(None)

    def _apply_filter(self):
        """Filter profile list by search box content."""
        raw = getattr(self, "_profile_search", None)
        flt = ""
        if raw:
            v = raw.get()
            flt = "" if v == tr("Search profiles...") else v.lower().strip()

        self._listbox.delete(0, "end")
        self._filtered_profiles = [
            p for p in self._profiles
            if not flt or flt in p["name"].lower()
        ]
        if self._filtered_profiles:
            self._empty_frame.place_forget()
            for p in self._filtered_profiles:
                self._listbox.insert("end", f"  {p['name']}")
        else:
            if not self._profiles:
                # Fill list_frame exactly — label won't overflow
                self._empty_frame.place(x=0, y=0, relwidth=1.0, relheight=1.0)
            else:
                self._listbox.insert("end", f"  {tr('(no matches)')}")

    def _on_select(self, event=None):
        sel = self._listbox.curselection()
        if not sel:
            self._selected_path = None
            self._update_detail(None)
            return
        idx = sel[0]
        filtered = getattr(self, "_filtered_profiles", self._profiles)
        if idx < len(filtered):
            p = filtered[idx]
            self._selected_path = p["path"]
            self._update_detail(p)

    def _update_detail(self, p):
        if p is None:
            self._sel_lbl.config(text=tr("— none selected —"),
                                  fg=T("FG3"),
                                  font=("Segoe UI", 9, "italic"))
            self._meta_lbl.config(text="")
            for btn in [self._load_btn, self._rename_btn, self._delete_btn]:
                btn.config(state="disabled")
        else:
            self._sel_lbl.config(
                text=p["name"], fg=T("FG"),
                font=("Segoe UI", 9, "bold"))
            mod = time.strftime("%d %b %Y  %H:%M",
                                 time.localtime(p["modified"]))
            tab_name = TAB_LABELS.get(p.get("tab", ""), tr("All panels"))
            self._meta_lbl.config(
                text=f"{tr('Saved:')} {mod}\n{tr('Scope:')} {tab_name}")
            for btn in [self._load_btn, self._rename_btn, self._delete_btn]:
                btn.config(state="normal")

    # ── Actions ─────────────────────────────────────────────────

    def _save(self):
        name = self._name_entry.get().strip()
        if not name:
            self._set_save_status(tr("⚠  Enter a profile name first."), T("FG2"))
            self._name_entry.focus_set()
            return
        selected_label = self._tab_var.get()
        tab_scope = next(
            (key for label, key in self._scope_options
             if label == selected_label),
            "all"
        )
        try:
            data = self.on_save_request(tab_scope)
            data["tab"] = tab_scope
            save_profile(name, data)
            self._set_save_status(f'{tr("✓  Saved as")} "{name}"', T("FG"))
            self._name_entry.delete(0, "end")
            self._refresh_list()
        except Exception as e:
            self._set_save_status(f"{tr('✗  Error:')} {e}", T("FG2"))

    def _load(self):
        if not self._selected_path:
            return
        data = load_profile(self._selected_path)
        if not data:
            self._set_action_status(tr("✗  Could not load profile."), T("FG2"))
            return
        try:
            self.on_load_request(data)
            tab = data.get("tab", "keyboard")
            if tab != "all":
                self.on_tab_change(tab)
            self._set_action_status(tr("✓  Profile loaded."), T("FG"))
        except Exception as e:
            self._set_action_status(f"{tr('✗  Error:')} {e}", T("FG2"))

    def _rename(self):
        if not self._selected_path:
            return
        dialog = tk.Toplevel(self.box)
        dialog.title(tr("Rename Profile"))
        dialog.resizable(False, False)
        dialog.configure(bg=T("SURFACE"))
        dialog.grab_set()

        tk.Label(dialog, text=tr("NEW NAME"),
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 8)).pack(anchor="w", padx=20, pady=(16, 4))

        entry = tk.Entry(
            dialog, width=28,
            bg=T("ENTRY_BG"), fg=T("FG"),
            relief="solid", bd=1,
            font=("Segoe UI", 9),
            insertbackground=T("FG")
        )
        entry.pack(padx=20, pady=(0, 12))
        current = next((p["name"] for p in self._profiles
                         if p["path"] == self._selected_path), "")
        entry.insert(0, current)
        entry.select_range(0, "end")
        entry.focus_set()

        btn_row = tk.Frame(dialog, bg=T("SURFACE"))
        btn_row.pack(fill="x", padx=20, pady=(0, 16))

        def do_rename():
            new_name = entry.get().strip()
            if not new_name:
                return
            new_path = rename_profile(self._selected_path, new_name)
            self._selected_path = new_path
            dialog.destroy()
            self._refresh_list()
            self._set_action_status(f'{tr("✓  Renamed to")} "{new_name}"', T("FG"))

        make_btn(btn_row, tr("RENAME"), do_rename, primary=True).pack(
            side="left", padx=(0, 8))
        make_btn(btn_row, tr("CANCEL"), dialog.destroy).pack(side="left")
        entry.bind("<Return>", lambda e: do_rename())
        entry.bind("<Escape>", lambda e: dialog.destroy())

        dialog.update_idletasks()
        pw = dialog.winfo_reqwidth()
        ph = dialog.winfo_reqheight()
        sx = self.box.winfo_rootx() + self.box.winfo_width() // 2 - pw // 2
        sy = self.box.winfo_rooty() + self.box.winfo_height() // 2 - ph // 2
        dialog.geometry(f"+{sx}+{sy}")

    def _delete(self):
        if not self._selected_path:
            return
        name = next((p["name"] for p in self._profiles
                      if p["path"] == self._selected_path), tr("this profile"))
        if messagebox.askyesno(
                tr("Delete Profile"),
                f"{tr('Delete')} \"{name}\"?\n\n{tr('This cannot be undone.')}",
                icon="warning"):
            if delete_profile(self._selected_path):
                self._selected_path = None
                self._refresh_list()
                self._set_action_status(tr("✓  Profile deleted."), T("FG2"))
            else:
                self._set_action_status(tr("✗  Could not delete."), T("FG2"))

    # ── Status helpers ──────────────────────────────────────────

    def _set_save_status(self, msg, color=None):
        self._save_status.config(text=msg, fg=color or T("FG2"))
        self.box.after(4000, lambda: self._save_status.config(text=""))

    def _set_action_status(self, msg, color=None):
        self._action_status.config(text=msg, fg=color or T("FG2"))
        self.box.after(4000, lambda: self._action_status.config(text=""))

    def refresh_labels(self):
        pass
