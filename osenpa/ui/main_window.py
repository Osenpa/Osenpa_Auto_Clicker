import ctypes
import os
import sys
import tkinter as tk
from ui.theme import apply_styles, T
from ui.keyboard_panel import KeyboardPanel
from ui.mouse_panel import MousePanel
from ui.macro_panel import MacroPanel
from ui.steps_panel import StepsPanel
from ui.footer import Footer
from ui.color_panel import ColorPanel
from ui.image_panel import ImagePanel
from ui.settings_panel import SettingsPanel
from ui.help_panel import HelpPanel
from ui.donate_panel import DonatePanel
from ui.overlay_indicator import OverlayIndicator
from ui.sidebar import Sidebar
from ui.profiles_panel import ProfilesPanel

from core import state, automation, macro_recorder, hotkey_listener
from core.color_detector import ColorDetector
from core.image_detector import ImageDetector
from utils import file_manager
from utils.autosave import save_session, load_session, has_session
from utils.i18n import tr


class MainWindow:
    def __init__(self):
        self._set_windows_app_id()
        self.window = tk.Tk()
        self.window.title(tr("Osenpa Auto Clicker: Free Macro Recorder & Image Detection Bot"))
        self.window.geometry("1280x740")
        self.window.minsize(1340, 780)   # prevent element clipping on resize
        self.window.resizable(True, True)
        self.window.configure(bg=T("BG"))

        self._set_app_icon()
        if sys.platform == "win32":
            self.window.bind("<Map>", self._on_window_map, add="+")

        self.color_detector    = ColorDetector()
        self.image_detector    = ImageDetector()
        self._border_win       = None
        self._image_border_win = None
        self.settings = {
            "show_indicator":   True,
            "show_scan_border": True,
            "has_prompted_donation": False,
            "on_change":        self._on_settings_change,
            "on_language_change": self._on_language_change,
            "on_reset_hotkeys": self._on_all_hotkeys_reset,
        }
        self.indicator   = OverlayIndicator(self.window)
        self._tab_frames = {}
        self._active_tab = "keyboard"

        self._run_from_idx = 0   # "Run From Step N" için
        apply_styles()
        self._build()
        self._register_hotkeys()

    def _set_windows_app_id(self):
        if sys.platform != "win32":
            return
        try:
            # A stable AppUserModelID helps Windows show the intended taskbar icon.
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.osenpa.autoclicker")
        except Exception:
            pass

    def _resolve_icon_path(self):
        base = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
        candidates = [os.path.join(base, "osenpa_release.ico")]

        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(os.path.join(meipass, "osenpa", "osenpa_release.ico"))
            candidates.append(os.path.join(meipass, "osenpa_release.ico"))

        for path in candidates:
            if os.path.exists(path):
                return path
        return candidates[0]

    def _set_app_icon(self):
        icon_path = self._resolve_icon_path()
        icon_path_fwd = icon_path.replace("\\", "/")

        self._app_icons = []

        try:
            # On Windows, .ico is still the most reliable source for title/taskbar icon slots.
            self.window.iconbitmap(icon_path_fwd)
            self.window.iconbitmap(default=icon_path_fwd)
        except Exception:
            pass

        # On Windows, use native HICON assignment only. Tk iconphoto may cause
        # taskbar/title mismatches depending on shell scaling and cache state.
        if sys.platform == "win32":
            try:
                self.window.update_idletasks()
            except Exception:
                pass
            self._apply_native_window_icon(icon_path)
            return

        try:
            from PIL import Image as pil_image
            from PIL import ImageTk as image_tk

            with pil_image.open(icon_path) as img:
                rgba = img.convert("RGBA")
                for size in [16, 20, 24, 32, 40, 48, 64, 96, 128, 256]:
                    self._app_icons.append(
                        image_tk.PhotoImage(rgba.resize((size, size), pil_image.LANCZOS))
                    )
            if self._app_icons:
                self.window.iconphoto(True, *self._app_icons)
        except Exception:
            pass

    def _apply_native_window_icon(self, icon_path):
        if sys.platform != "win32":
            return
        try:
            user32 = ctypes.windll.user32
            # Use pointer-sized types so icon handles are not truncated on 64-bit Windows.
            user32.LoadImageW.restype = ctypes.c_void_p
            user32.LoadImageW.argtypes = [
                ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint,
                ctypes.c_int, ctypes.c_int, ctypes.c_uint
            ]
            user32.SendMessageW.restype = ctypes.c_void_p
            user32.SendMessageW.argtypes = [
                ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p
            ]
            if hasattr(user32, "SetClassLongPtrW"):
                user32.SetClassLongPtrW.restype = ctypes.c_void_p
                user32.SetClassLongPtrW.argtypes = [
                    ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p
                ]

            image_icon = 1
            lr_loadfromfile = 0x0010
            wm_seticon = 0x0080
            icon_small = 0
            icon_big = 1
            sm_cxicon = 11
            sm_cyicon = 12
            sm_cxsmicon = 49
            sm_cysmicon = 50
            gclp_hicon = -14
            gclp_hiconsm = -34

            small_w = user32.GetSystemMetrics(sm_cxsmicon)
            small_h = user32.GetSystemMetrics(sm_cysmicon)
            big_w = user32.GetSystemMetrics(sm_cxicon)
            big_h = user32.GetSystemMetrics(sm_cyicon)

            hicon_small = user32.LoadImageW(None, icon_path, image_icon, small_w, small_h, lr_loadfromfile)
            hicon_big = user32.LoadImageW(None, icon_path, image_icon, big_w, big_h, lr_loadfromfile)
            hwnds = self._get_icon_hwnds()

            for hwnd in hwnds:
                if hicon_small:
                    user32.SendMessageW(hwnd, wm_seticon, icon_small, hicon_small)
                if hicon_big:
                    user32.SendMessageW(hwnd, wm_seticon, icon_big, hicon_big)

                if hasattr(user32, "SetClassLongPtrW"):
                    if hicon_big:
                        user32.SetClassLongPtrW(hwnd, gclp_hicon, hicon_big)
                    if hicon_small:
                        user32.SetClassLongPtrW(hwnd, gclp_hiconsm, hicon_small)
                else:
                    if hicon_big:
                        user32.SetClassLongW(hwnd, gclp_hicon, hicon_big)
                    if hicon_small:
                        user32.SetClassLongW(hwnd, gclp_hiconsm, hicon_small)

            self._native_hicon_small = hicon_small
            self._native_hicon_big = hicon_big
            self._icon_hwnds = hwnds

            # Re-apply after initial map; some Windows shells overwrite first assignment.
            self.window.after(120, self._reapply_icons)
            self.window.after(450, self._reapply_icons)
            self.window.after(900, self._reapply_icons)
        except Exception:
            pass

    def _get_icon_hwnds(self):
        hwnds = set()
        try:
            hwnds.add(int(self.window.winfo_id()))
        except Exception:
            pass

        try:
            # Tk's real top-level frame handle (the one taskbar tracks).
            frame = self.window.tk.call("wm", "frame", self.window._w)
            if isinstance(frame, str) and frame.startswith("0x"):
                hwnds.add(int(frame, 16))
            elif frame:
                hwnds.add(int(frame))
        except Exception:
            pass

        try:
            user32 = ctypes.windll.user32
            for hwnd in list(hwnds):
                parent = user32.GetParent(hwnd)
                if parent:
                    hwnds.add(int(parent))
        except Exception:
            pass

        return [h for h in hwnds if h]

    def _reapply_icons(self, _event=None):
        if sys.platform != "win32":
            return
        try:
            user32 = ctypes.windll.user32
            wm_seticon = 0x0080
            icon_small = 0
            icon_big = 1
            for hwnd in getattr(self, "_icon_hwnds", []) or self._get_icon_hwnds():
                if getattr(self, "_native_hicon_small", None):
                    user32.SendMessageW(hwnd, wm_seticon, icon_small, self._native_hicon_small)
                if getattr(self, "_native_hicon_big", None):
                    user32.SendMessageW(hwnd, wm_seticon, icon_big, self._native_hicon_big)
        except Exception:
            pass

    def _on_window_map(self, _event=None):
        # On some systems taskbar icon is decided at map time; re-apply once mapped.
        # Prevent recursive/frequent calls during window drag which causes crashes
        if getattr(self, "_has_mapped_icon", False):
            return
        self._has_mapped_icon = True
        try:
            self._apply_native_window_icon(self._resolve_icon_path())
        except Exception:
            pass

    def _build(self):
        for w in self.window.winfo_children():
            w.destroy()
        self.window.configure(bg=T("BG"))
        self.window.title(tr("Osenpa Auto Clicker: Free Macro Recorder & Image Detection Bot"))

        self._tab_frames = {}
        self.indicator   = OverlayIndicator(self.window)

        # Footer sabit altta kalacak ÅŸekilde Ã¶nce pack et
        self._footer_frame = tk.Frame(self.window, bg=T("BG"))
        self._footer_frame.pack(side="bottom", fill="x")

        self._body_frame = tk.Frame(self.window, bg=T("BG"))
        self._body_frame.pack(side="top", fill="both", expand=True)

        self._build_body()
        self._build_footer()

    def _on_theme_change(self):
        apply_styles()
        self._rebuild_ui()

    def _on_language_change(self):
        self._rebuild_ui()

    def _rebuild_ui(self):
        tab = self._active_tab
        self._pending_tab = tab
        self._build()
        self._show_tab(tab)
        if hasattr(self, "sidebar"):
            self.sidebar.active_tab = tab
            self.sidebar._set_active_style(tab)
            self.sidebar._update_theme_btns()

    def _build_body(self):
        body = tk.Frame(self._body_frame, bg=T("BG"))
        body.pack(fill="both", expand=True)

        self.sidebar = Sidebar(
            body,
            on_tab_change=self._on_tab_change,
            on_theme_change=self._on_theme_change,
            initial_tab=getattr(self, "_pending_tab", self._active_tab)
        )
        from ui.theme import is_dark
        self.sidebar._dark_var.set(is_dark())
        self.sidebar._update_theme_btns()

        work_area = tk.Frame(body, bg=T("BG"))
        work_area.pack(side="left", fill="both", expand=True)

        work_area.columnconfigure(0, weight=3, minsize=500)
        work_area.columnconfigure(1, weight=0)
        work_area.columnconfigure(2, weight=1, minsize=360)
        work_area.rowconfigure(0, weight=1)

        self._workspace = tk.Frame(work_area, bg=T("SURFACE"))
        self._workspace.grid(row=0, column=0, sticky="nsew")

        tk.Frame(work_area, bg=T("BORDER"), width=1).grid(
            row=0, column=1, sticky="ns")

        self._steps_outer = tk.Frame(work_area, bg=T("SURFACE"))
        self._steps_outer.grid(row=0, column=2, sticky="nsew")

        self.steps_panel = StepsPanel(
            self._steps_outer, state.steps,
            on_export=self._export,
            on_import=self._import,
            on_add_step=self._add_step,
            on_run_from=self._run_from_step
        )

        self._build_tabs()
        self._show_tab(self._active_tab)

    def _make_plain(self, parent):
        frame = tk.Frame(parent, bg=T("SURFACE"))
        frame.pack(fill="both", expand=True)
        return frame

    def _build_tabs(self):
        builders = {
            "profiles":   self._build_profiles_tab,
            "keyboard":   self._build_keyboard_tab,
            "mouse":      self._build_mouse_tab,
            "macro":      self._build_macro_tab,
            "color":      self._build_color_tab,
            "image":      self._build_image_tab,

            "settings":   self._build_settings_tab,
            "help":        self._build_help_tab,
            "donate":      self._build_donate_tab,
        }
        for key, builder in builders.items():
            frame = tk.Frame(self._workspace, bg=T("SURFACE"))
            self._tab_frames[key] = frame
            builder(frame)

    def _build_profiles_tab(self, parent):
        inner = self._make_plain(parent)
        self.profiles_panel = ProfilesPanel(
            inner,
            on_save_request=self._profile_collect,
            on_load_request=self._profile_apply,
            on_tab_change=self._on_tab_change_from_profile
        )

    def _on_tab_change_from_profile(self, tab_key):
        """Profil yÃ¼klenince ilgili sekmeye geÃ§ ve sidebar'Ä± gÃ¼ncelle."""
        self._active_tab = tab_key
        self._show_tab(tab_key)
        self.sidebar.active_tab = tab_key
        # TÃ¼m butonlarÄ± inactive yap, sonra aktifi set et
        for k in self.sidebar._tab_btns:
            self.sidebar._set_inactive_style(k)
        self.sidebar._set_active_style(tab_key)

    def _build_keyboard_tab(self, parent):
        inner = self._make_plain(parent)
        self.kb_panel = KeyboardPanel(inner, self._add_step)
        self.kb_panel.set_indicator_callbacks(
            self._show_indicator, self.indicator.hide,
            self.indicator.update_count,
            self._minimize_if_visible)
        self.kb_panel._on_busy_check = self._any_task_running

    def _build_mouse_tab(self, parent):
        inner = self._make_plain(parent)
        self.ms_panel = MousePanel(
            inner, self._add_step, self._pick_target)
        self.ms_panel.set_indicator_callbacks(
            self._show_indicator, self.indicator.hide,
            self._minimize_if_visible)
        self.ms_panel._on_update_count = self.indicator.update_count
        self.ms_panel._on_busy_check = self._any_task_running

    def _build_macro_tab(self, parent):
        inner = self._make_plain(parent)
        self.macro_panel = MacroPanel(
            inner,
            on_start_recording=self._start_macro,
            on_stop_recording=self._stop_macro,
            on_change_hotkey=self._change_macro_hotkey
        )

    def _build_color_tab(self, parent):
        inner = self._make_plain(parent)
        self.color_panel = ColorPanel(
            inner,
            on_start=self._start_color_scan,
            on_stop=self._stop_color_scan,
            on_pick_screen=self._pick_color_from_screen,
            on_pick_area=self._pick_area,
            on_change_hotkey=self._change_color_hotkey,
            on_add_step=self._add_step
        )
        self.color_panel._on_busy_check = self._any_task_running

    def _build_image_tab(self, parent):
        inner = self._make_plain(parent)
        self.image_panel = ImagePanel(
            inner,
            on_start=self._start_image_scan,
            on_stop=self._stop_image_scan,
            on_pick_area=self._pick_area,
            on_change_hotkey=self._change_image_hotkey,
            on_add_step=self._add_step
        )
        self.image_panel._on_busy_check = self._any_task_running

    def _build_settings_tab(self, parent):
        inner = self._make_plain(parent)
        self.settings_panel_ui = SettingsPanel(inner, self.settings)

    def _build_help_tab(self, parent):
        inner = self._make_plain(parent)
        self.help_panel = HelpPanel(inner)

    def _build_donate_tab(self, parent):
        inner = self._make_plain(parent)
        self.donate_panel = DonatePanel(inner)

    def _show_tab(self, key):
        for f in self._tab_frames.values():
            f.pack_forget()
        frame = self._tab_frames.get(key)
        if frame:
            frame.pack(fill="both", expand=True)

    def _on_tab_change(self, key):
        self._active_tab = key
        self._show_tab(key)

    def _build_footer(self):
        self.footer = Footer(
            self._footer_frame,
            on_start=self._start_automation,
            on_stop=self._stop_automation,
            on_change_hotkey=self._change_hotkey
        )

    def _on_settings_change(self):
        if not self.settings["show_indicator"]:
            self.indicator.hide()
        if not self.settings["show_scan_border"]:
            self._hide_area_border()
            self._hide_image_border()

    # â”€â”€ Profile system â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _profile_collect(self, scope: str) -> dict:
        """
        TÃ¼m panellerden (veya belirli bir panelden) ayarlarÄ± toplayÄ±p
        tek bir sÃ¶zlÃ¼k olarak dÃ¶ndÃ¼rÃ¼r. scope='all' veya tab adÄ±.
        """
        data = {}
        panels = {
            "keyboard": (self.kb_panel,    "keyboard"),
            "mouse":    (self.ms_panel,     "mouse"),
            "color":    (self.color_panel,  "color"),
            "image":    (self.image_panel,  "image"),
        }
        for key, (panel, _) in panels.items():
            if scope == "all" or scope == key:
                try:
                    data[key] = panel.get_profile_data()
                except Exception as e:
                    print(f"[Profile] collect {key} error: {e}")
        # Steps'i de ekle
        if scope == "all":
            try:
                import json as _json
                data["steps"] = _json.loads(_json.dumps(state.steps))
            except Exception:
                data["steps"] = []
        return data

    def _profile_apply(self, data: dict):
        """
        Profil verisini ilgili panellere uygular.
        data None ise (load baÅŸarÄ±sÄ±z) sessizce Ã§Ä±kar.
        """
        if data is None:
            # load_profile zaten kullanÄ±cÄ±ya messagebox gÃ¶sterdi
            return
        panel_map = {
            "keyboard": self.kb_panel,
            "mouse":    self.ms_panel,
            "color":    self.color_panel,
            "image":    self.image_panel,
        }
        errors = []
        for key, panel in panel_map.items():
            if key in data:
                try:
                    panel.load_profile_data(data[key])
                except Exception as e:
                    errors.append(f"  â€¢ {key}: {e}")
                    print(f"[Profile] apply {key} error: {e}")
        # Steps
        if "steps" in data:
            try:
                state.steps.clear()
                state.steps.extend(data["steps"])
                self.steps_panel.refresh()
            except Exception as e:
                errors.append(f"  â€¢ steps: {e}")
                print(f"[Profile] apply steps error: {e}")
        if errors:
            from tkinter import messagebox as _mb
            _mb.showwarning(
                tr("Profile Load Warning"),
                tr("Some sections could not be applied:\n") + "\n".join(errors)
            )

    # â”€â”€ Window minimize helper â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _minimize_if_visible(self):
        """Pencere gÃ¶rÃ¼nÃ¼yorsa minimize et; kÄ±sayolla Ã§aÄŸrÄ±ldÄ±ÄŸÄ±nda dokunma."""
        try:
            if self.window.state() == "normal":
                self.window.iconify()
        except Exception:
            pass

    # â”€â”€ Single-task guard â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _any_task_running(self):
        """Steps dÄ±ÅŸÄ±nda herhangi bir gÃ¶rev Ã§alÄ±ÅŸÄ±yor mu?"""
        return (state.mouse_running or state.kb_key_running or
                state.kb_combo_running or state.color_scanning or
                state.image_scanning)

    def _show_busy_warning(self):
        self.footer.set_status(
            tr("STOP THE ACTIVE TASK FIRST."), color="#E74C3C")
        self.window.after(3000, lambda: self.footer.set_status(tr("READY")))

    # â”€â”€ Automation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _start_automation(self):
        if not state.steps:
            self.footer.set_status(tr("NO STEPS TO RUN."))
            return
        infinite, count = self.footer.get_loop_settings()
        interval = self.footer.get_interval_seconds()
        total    = len(state.steps)
        state.reset_counts()

        start_from = getattr(self, "_run_from_idx", 0)
        self._run_from_idx = 0  # SÄ±fÄ±rla â€” tek kullanÄ±mlÄ±k

        automation.start(
            on_done=lambda n: self.window.after(
                0, self._on_automation_done),
            on_no_steps=lambda: self.window.after(0, lambda: (
                self.footer.set_status(tr("NO STEPS TO RUN.")),
                self._set_all_states("normal"),
                self.footer.set_running(False)
            )),
            loop_infinite=infinite,
            loop_count=count,
            global_interval=interval,
            on_click=lambda c: self.window.after(0, lambda: (
                self.footer.set_status(
                    tr("RUNNING  —  ACTION {} / {}").format(c, total)),
                self.footer.set_progress(c, total),
                self.indicator.update_count(c)
            )),
            on_condition_result=lambda branch, atype: self.window.after(
                0, lambda b=branch, a=atype: self.indicator.update_condition(b, a)
            ),
            start_from=start_from,
            on_step_change=lambda idx: self.window.after(
                0, lambda i=idx: self._on_step_change(i))
        )
        self._set_all_states("disabled")
        self.footer.set_running(True)
        self.footer.set_status(tr("RUNNING..."))
        self._show_indicator(tr("AUTOMATION RUNNING"),
                             hotkey=state.hotkey, count=0)
        self._minimize_if_visible()

    def _stop_automation(self):
        automation.stop()

    def _on_automation_done(self):
        self._set_all_states("normal")
        self.footer.set_running(False)
        self.footer.set_status(
            f"{tr('DONE.  TOTAL ACTIONS:')} {state.action_count}")
        self.footer.set_active_step(-1)       # Highlight kaldır
        self.steps_panel.set_active_step(-1)  # Liste highlight kaldÄ±r
        self.indicator.hide()
        try:
            if self.window.state() == "iconic":
                self.window.deiconify()
        except Exception:
            pass

    # â”€â”€ Color scan â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _start_color_scan(self, target_rgb,
                           scan_interval, click_button,
                           area=None, repeat=0, infinite=True,
                           tolerance=15, step_interval=0,
                           target_colors=None, tolerances=None, **kw):
        if self._any_task_running():
            self._show_busy_warning()
            self.color_panel.start_btn.config(state="normal")
            self.color_panel.stop_btn.config(state="disabled")
            self.color_panel.status_lbl.config(text=tr("STOP THE ACTIVE TASK FIRST."))
            return
        state.reset_counts()
        self.color_detector.start(
            target_rgb=target_rgb,
            scan_interval=scan_interval,
            click_button=click_button,
            on_found=self._on_color_found,
            on_status=None,
            area=area,
            on_area_highlight=self._on_area_highlight,
            tolerance=tolerance,
            step_interval=step_interval,
            on_scan=self._on_color_scan,
            target_colors=target_colors,
            tolerances=tolerances
        )
        color_count = len(target_colors) if target_colors else 1
        noun = tr("COLOR") if color_count == 1 else f"{color_count} {tr('COLORS')}"
        self._show_indicator(f"{tr('SCANNING')} {noun}",
                             hotkey=state.color_hotkey, count=0,
                             show_scan=True)
        self._minimize_if_visible()

    def _stop_color_scan(self):
        self.color_detector.stop()
        self.indicator.hide()
        self.color_panel.update_status(
            f"{tr('STOPPED.  TOTAL:')} {state.action_count}", T("FG2"))

    def _on_color_found(self, x, y, count, matched_rgb=None):
        state.action_count = count
        if matched_rgb:
            r, g, b = matched_rgb
            hex_c = "#{:02X}{:02X}{:02X}".format(r, g, b)
            msg = f"{tr('CLICKED')} ({x}, {y})  [{hex_c}]  —  {tr('TOTAL:')} {count}"
        else:
            msg = f"{tr('CLICKED')} ({x}, {y})  —  {tr('TOTAL:')} {count}"
        self.window.after(0, lambda: self.color_panel.update_status(
            msg, T("FG")))
        self.window.after(0, lambda: self.indicator.update_count(count))

    def _on_color_scan(self, scan_count):
        self.window.after(0, lambda: self.indicator.update_scan(scan_count))

    # â”€â”€ Image scan â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _start_image_scan(self, image_path, clipboard_image,
                           confidence, scan_interval,
                           click_button, area=None, step_interval=0,
                           image_list=None, **kw):
        if self._any_task_running():
            self._show_busy_warning()
            self.image_panel.start_btn.config(state="normal")
            self.image_panel.stop_btn.config(state="disabled")
            self.image_panel.status_lbl.config(text=tr("STOP THE ACTIVE TASK FIRST."))
            return

        # Çoklu görsel listesi varsa önce tümünü yükle
        if image_list and len(image_list) > 0:
            loaded = self.image_detector.load_templates_from_list(image_list)
            if loaded == 0:
                self.image_panel.update_status(tr("FAILED TO LOAD IMAGES."), T("FG2"))
                self.image_panel._stop()
                return
        else:
            # Eski tekli gÃ¶rsel yÃ¼kleme
            if clipboard_image is not None:
                import numpy as np
                ok = self.image_detector.load_from_array(np.array(clipboard_image))
            else:
                ok = self.image_detector.load_template(image_path)
            if not ok:
                self.image_panel.update_status(tr("FAILED TO LOAD IMAGE."), T("FG2"))
                self.image_panel._stop()
                return

        state.reset_counts()
        started = self.image_detector.start(
            confidence=confidence,
            scan_interval=scan_interval,
            click_button=click_button,
            on_found=self._on_image_found,
            area=area,
            on_area_highlight=self._on_image_area_highlight,
            step_interval=step_interval,
            on_scan=self._on_image_scan
        )
        if not started:
            self.image_panel.update_status(tr("COULD NOT START."), T("FG2"))
            self.image_panel._stop()
            return
        img_count = len(image_list) if image_list else 1
        noun = tr("IMAGE") if img_count == 1 else f"{img_count} {tr('IMAGES')}"
        self._show_indicator(f"{tr('SCANNING')} {noun}",
                             hotkey=state.image_hotkey, count=0,
                             show_scan=True)
        self._minimize_if_visible()

    def _stop_image_scan(self):
        self.image_detector.stop()
        self.indicator.hide()
        self.image_panel.update_status(
            f"{tr('STOPPED.  TOTAL:')} {state.action_count}", T("FG2"))

    def _on_image_found(self, x, y, count, matched_label=None):
        state.action_count = count
        if matched_label:
            import os as _os
            name = _os.path.basename(matched_label) if (_os.sep in matched_label or "/" in matched_label) else matched_label
            msg = f"{tr('CLICKED')} ({x}, {y})  [{name}]  —  {tr('TOTAL:')} {count}"
        else:
            msg = f"{tr('CLICKED')} ({x}, {y})  —  {tr('TOTAL:')} {count}"
        self.window.after(0, lambda: self.image_panel.update_status(msg, T("FG")))
        self.window.after(0, lambda: self.indicator.update_count(count))

    def _on_image_scan(self, scan_count):
        self.window.after(0, lambda: self.indicator.update_scan(scan_count))

    # â”€â”€ Area borders â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _on_area_highlight(self, area, show):
        if not self.settings.get("show_scan_border"):
            return
        if show:
            self.window.after(0, lambda: self._show_area_border(area))
        else:
            self.window.after(0, self._hide_area_border)

    def _on_image_area_highlight(self, area, show):
        if not self.settings.get("show_scan_border"):
            return
        if show:
            self.window.after(
                0, lambda: self._show_image_border(area))
        else:
            self.window.after(0, self._hide_image_border)

    def _show_area_border(self, area):
        self._hide_area_border()
        x1, y1, x2, y2 = area
        self._border_win = tk.Toplevel(self.window)
        self._border_win.overrideredirect(True)
        self._border_win.attributes("-topmost", True)
        self._border_win.attributes("-transparentcolor", "white")
        self._border_win.geometry(f"{x2-x1}x{y2-y1}+{x1}+{y1}")
        c = tk.Canvas(self._border_win,
                      bg="white", highlightthickness=0)
        c.pack(fill="both", expand=True)
        b = 3
        c.create_rectangle(b, b, x2-x1-b, y2-y1-b,
                             outline=T("PRIMARY_BG"), width=b, fill="")

    def _hide_area_border(self):
        try:
            if self._border_win:
                self._border_win.destroy()
                self._border_win = None
        except Exception:
            pass

    def _show_image_border(self, area):
        self._hide_image_border()
        x1, y1, x2, y2 = area
        self._image_border_win = tk.Toplevel(self.window)
        self._image_border_win.overrideredirect(True)
        self._image_border_win.attributes("-topmost", True)
        self._image_border_win.attributes("-transparentcolor", "white")
        self._image_border_win.geometry(f"{x2-x1}x{y2-y1}+{x1}+{y1}")
        c = tk.Canvas(self._image_border_win,
                      bg="white", highlightthickness=0)
        c.pack(fill="both", expand=True)
        b = 3
        c.create_rectangle(b, b, x2-x1-b, y2-y1-b,
                             outline=T("FG2"), width=b, fill="")

    def _hide_image_border(self):
        try:
            if self._image_border_win:
                self._image_border_win.destroy()
                self._image_border_win = None
        except Exception:
            pass

    def _show_indicator(self, text, hotkey=None, count=None, show_scan=False):
        if self.settings.get("show_indicator"):
            self.indicator.show(text, hotkey=hotkey, count=count,
                                show_scan=show_scan)

    # â”€â”€ Pickers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _pick_color_from_screen(self, callback):
        self.window.iconify()
        overlay = tk.Toplevel()
        overlay.attributes("-fullscreen", True)
        overlay.attributes("-alpha", 0.01)
        overlay.attributes("-topmost", True)
        overlay.config(cursor="crosshair")

        def on_click(event):
            import pyautogui
            screenshot = pyautogui.screenshot()
            r, g, b = screenshot.getpixel(
                (event.x_root, event.y_root))
            hex_c = "#{:02x}{:02x}{:02x}".format(r, g, b)
            overlay.destroy()
            self.window.deiconify()
            callback((r, g, b), hex_c)

        overlay.bind("<Button-1>", on_click)
        overlay.focus_force()

    def _pick_area(self, callback):
        self.window.iconify()
        overlay = tk.Toplevel()
        overlay.attributes("-fullscreen", True)
        overlay.attributes("-alpha", 0.15)
        overlay.attributes("-topmost", True)
        overlay.configure(bg="gray")
        overlay.config(cursor="crosshair")
        start_x = start_y = 0
        rect    = None
        canvas  = tk.Canvas(overlay, cursor="crosshair",
                             bg="gray", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        def on_press(e):
            nonlocal start_x, start_y, rect
            start_x, start_y = e.x_root, e.y_root
            if rect:
                canvas.delete(rect)

        def on_drag(e):
            nonlocal rect
            if rect:
                canvas.delete(rect)
            rect = canvas.create_rectangle(
                start_x, start_y, e.x_root, e.y_root,
                outline=T("PRIMARY_BG"), width=2, fill="")

        def on_release(e):
            x1 = min(start_x, e.x_root)
            y1 = min(start_y, e.y_root)
            x2 = max(start_x, e.x_root)
            y2 = max(start_y, e.y_root)
            overlay.destroy()
            self.window.deiconify()
            callback(x1, y1, x2, y2)

        canvas.bind("<ButtonPress-1>",   on_press)
        canvas.bind("<B1-Motion>",       on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        overlay.focus_force()

    def _pick_target(self, x_entry, y_entry):
        self.window.iconify()
        self.footer.set_status(tr("CLICK ANYWHERE TO PICK TARGET..."))
        overlay = tk.Toplevel()
        overlay.attributes("-fullscreen", True)
        overlay.attributes("-alpha", 0.01)
        overlay.attributes("-topmost", True)
        overlay.config(cursor="crosshair")

        def on_click(event):
            x_entry.delete(0, tk.END)
            x_entry.insert(0, str(event.x_root))
            y_entry.delete(0, tk.END)
            y_entry.insert(0, str(event.y_root))
            overlay.destroy()
            self.window.deiconify()
            self.footer.set_status(tr("READY"))

        overlay.bind("<Button-1>", on_click)
        overlay.focus_force()

    # â”€â”€ Macro â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _start_macro(self):
        macro_recorder.start(on_stop_callback=self._on_macro_stop)
        self.footer.set_status(tr("RECORDING MACRO..."))
        self.window.iconify()
        self._show_indicator(tr("MACRO RECORDING"),
                             hotkey=state.macro_hotkey)

    def _stop_macro(self):
        macro_recorder.stop()
        self.macro_panel.set_recording(False)
        self.indicator.hide()

    def _on_macro_hotkey_stop(self):
        macro_recorder.stop()
        self.macro_panel.set_recording(False)
        self.indicator.hide()

    def _on_macro_stop(self, events):
        new_steps = macro_recorder.convert_to_steps(events)
        state.steps.extend(new_steps)
        self.window.after(0, self._after_macro_stop, len(new_steps))

    def _after_macro_stop(self, count):
        self.window.deiconify()
        self.steps_panel.refresh()
        self.footer.set_status(
            f"{tr('MACRO RECORDED')}  —  {count} {tr('STEPS ADDED.')}")
        self.indicator.hide()

    # â”€â”€ Steps â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _add_step(self, step):
        # add_step_from_panel default not ekler ve undo history'e kaydeder
        self.steps_panel.add_step_from_panel(step)

    def _run_from_step(self, idx: int):
        """StepsPanel'deki 'Run From Here' butonundan Ã§aÄŸrÄ±lÄ±r."""
        self._run_from_idx = idx
        self._start_automation()

    def _on_step_change(self, idx: int):
        """Otomasyon motoru adÄ±m deÄŸiÅŸtirince Ã§aÄŸrÄ±lÄ±r."""
        # Footer'da aktif adÄ±m gÃ¶stergesi
        if idx >= 0 and idx < len(state.steps):
            step = state.steps[idx]
            from ui.steps_panel import TYPE_LABELS
            lbl = TYPE_LABELS.get(step.get("type", ""), "")
            self.footer.set_active_step(idx, lbl)
        else:
            self.footer.set_active_step(-1)
        # Steps listesinde highlight
        self.steps_panel.set_active_step(idx)

    def _export(self):
        ok = file_manager.export_steps(state.steps)
        if ok:
            self.footer.set_status(tr("STEPS EXPORTED."))

    def _import(self):
        data = file_manager.import_steps()
        if data is not None:
            state.steps.clear()
            state.steps.extend(data)
            self.steps_panel.refresh()
            self.footer.set_status(f"{tr('STEPS IMPORTED.')}  ({len(data)} {tr('STEPS')})")
        else:
            # import_steps() returned None â€” either user cancelled or error shown
            pass

    # â”€â”€ Hotkeys â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _register_hotkeys(self):
        rl = hotkey_listener.register
        rl("automation_start",
           lambda: self.window.after(0, self._start_automation))
        rl("automation_stop",
           lambda: self.window.after(0, self._stop_automation))
        rl("macro_start",
           lambda: self.window.after(0, self._start_macro))
        rl("macro_stop",
           lambda: self.window.after(0, self._on_macro_hotkey_stop))
        rl("color_start",
           lambda: self.window.after(
               0, lambda: self.color_panel._start()))
        rl("color_stop",
           lambda: self.window.after(
               0, lambda: self.color_panel._stop()))
        rl("image_start",
           lambda: self.window.after(
               0, lambda: self.image_panel._start()))
        rl("image_stop",
           lambda: self.window.after(
               0, lambda: self.image_panel._stop()))
        rl("kb_key_start",
           lambda: self.window.after(
               0, lambda: self.kb_panel.start_independent()))
        rl("kb_key_stop",
           lambda: self.window.after(
               0, lambda: self.kb_panel._stop_key()))
        rl("kb_combo_start",
           lambda: self.window.after(
               0, lambda: self.kb_panel.start_combo_independent()))
        rl("kb_combo_stop",
           lambda: self.window.after(
               0, lambda: self.kb_panel._stop_combo()))
        rl("kb_key_hotkey_changed",   self._on_kb_key_hotkey_changed)
        rl("kb_combo_hotkey_changed", self._on_kb_combo_hotkey_changed)
        rl("mouse_start",
           lambda: self.window.after(
               0, lambda: self.ms_panel._start()))
        rl("mouse_stop",
           lambda: self.window.after(
               0, lambda: self.ms_panel._stop()))
        rl("hotkey_changed",       self._on_hotkey_changed)
        rl("macro_hotkey_changed", self._on_macro_hotkey_changed)
        rl("color_hotkey_changed", self._on_color_hotkey_changed)
        rl("image_hotkey_changed", self._on_image_hotkey_changed)
        rl("kb_hotkey_changed",    self._on_kb_hotkey_changed)
        rl("mouse_hotkey_changed", self._on_mouse_hotkey_changed)
        rl("hotkey_duplicate",
           lambda k: self.window.after(0, lambda: self.footer.set_status(
               tr("'{}' IS ALREADY ASSIGNED.").format(k.upper()))))
        hotkey_listener.start()

    def _change_hotkey(self):
        state.changing_hotkey = True
        self.footer.set_status(tr("PRESS ANY KEY FOR START/STOP HOTKEY..."))

    def _change_macro_hotkey(self):
        state.changing_macro_hotkey = True
        self.footer.set_status(tr("PRESS ANY KEY FOR MACRO HOTKEY..."))

    def _change_color_hotkey(self):
        state.changing_color_hotkey = True
        self.footer.set_status(tr("PRESS ANY KEY FOR COLOR SCAN HOTKEY..."))

    def _change_image_hotkey(self):
        state.changing_image_hotkey = True
        self.footer.set_status(tr("PRESS ANY KEY FOR IMAGE SCAN HOTKEY..."))

    def _on_hotkey_changed(self, key_name):
        self.window.after(0, lambda: (
            self.footer.update_hotkey_display(key_name),
            self.footer.set_status(tr("READY"))
        ))

    def _on_macro_hotkey_changed(self, key_name):
        self.window.after(0, lambda: (
            self.macro_panel.update_hotkey_display(key_name),
            self.footer.set_status(tr("READY"))
        ))

    def _on_color_hotkey_changed(self, key_name):
        self.window.after(
            0, lambda: self.color_panel.update_hotkey_display(key_name))

    def _on_image_hotkey_changed(self, key_name):
        self.window.after(
            0, lambda: self.image_panel.update_hotkey_display(key_name))

    def _on_kb_hotkey_changed(self, key_name):
        self.window.after(
            0, lambda: self.kb_panel.update_hotkey_display(key_name, "key"))

    def _on_kb_key_hotkey_changed(self, key_name):
        self.window.after(
            0, lambda: self.kb_panel.update_hotkey_display(key_name, "key"))

    def _on_kb_combo_hotkey_changed(self, key_name):
        self.window.after(
            0, lambda: self.kb_panel.update_hotkey_display(key_name, "combo"))

    def _on_mouse_hotkey_changed(self, key_name):
        self.window.after(
            0, lambda: self.ms_panel.update_hotkey_display(key_name))

    def _on_all_hotkeys_reset(self):
        """Called by settings when RESET HOTKEYS is pressed â€” update all panel displays."""
        from core import state as _s
        from core import hotkey_listener
        def _update():
            try:
                self.footer.update_hotkey_display(_s.hotkey)
                self.macro_panel.update_hotkey_display(_s.macro_hotkey)
                self.color_panel.update_hotkey_display(_s.color_hotkey)
                self.image_panel.update_hotkey_display(_s.image_hotkey)
                self.kb_panel.update_hotkey_display(_s.kb_hotkey, "key")
                self.kb_panel.update_hotkey_display(_s.kb_combo_hotkey, "combo")
                self.ms_panel.update_hotkey_display(_s.mouse_hotkey)
            except Exception:
                pass

        self.window.after(0, _update)

    def _set_all_states(self, s):
        self.kb_panel.set_state(s)
        self.ms_panel.set_state(s)
        self.macro_panel.set_state(s)
        self.steps_panel.set_state(s)
        self.footer.set_state(s)

    def run(self):
        # Autosave: kapanÄ±ÅŸta kaydet
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        # Ã–nceki oturumu geri yÃ¼kle
        self._restore_session()
        self.window.mainloop()

    def _restore_session(self):
        """Önceki oturumda kaydedilen adımları geri yükle."""
        if not has_session():
            return
        session = load_session()
        if not session:
            return
        
        # Load user runtime settings
        loaded_sets = session.get("settings", {})
        self.settings["show_indicator"] = loaded_sets.get("show_indicator", self.settings.get("show_indicator", True))
        self.settings["show_scan_border"] = loaded_sets.get("show_scan_border", self.settings.get("show_scan_border", True))
        self.settings["has_prompted_donation"] = loaded_sets.get("has_prompted_donation", False)
        
        # Increment session count
        self.settings["total_sessions"] = loaded_sets.get("total_sessions", 0) + 1
        
        state.humanize = loaded_sets.get("humanize", False)
        state.total_lifetime_clicks = loaded_sets.get("total_lifetime_clicks", 0)

        # Check for milestone prompt
        self.window.after(3000, self._check_milestone_prompt)

        steps = session.get("steps", [])
        if not steps:
            return
        from tkinter import messagebox as _mb
        answer = _mb.askyesno(
            tr("Restore Session"),
            tr("Found {} step(s) from your last session.\n\nWould you like to restore them?").format(len(steps)),
            default="yes"
        )
        if answer:
            state.steps.clear()
            state.steps.extend(steps)
            self.steps_panel.refresh()
            self.footer.set_status(
                tr("SESSION RESTORED  —  {} STEPS").format(len(steps)))

    def _check_milestone_prompt(self):
        sessions = self.settings.get("total_sessions", 1)
        prompted = self.settings.get("has_prompted_donation", False)
        
        if sessions >= 20 and not prompted:
            self.settings["has_prompted_donation"] = True
            msg = tr("We see Osenpa has saved you a lot of time...\nWould you like to buy us a coffee?")
            # Override translation manually for the required text if not in dictionary yet
            # Since the user requested exact Turkish string (it will be translated if in dict)
            msg = tr("Osenpa'nın size çok zaman kazandırdığını görüyoruz... Bize bir kahve ısmarlamak ister misiniz?")
            self._show_toast(msg)

    def _show_toast(self, message):
        toast = tk.Toplevel(self.window)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        toast.configure(bg=T("PRIMARY_BG"))
        
        lbl = tk.Label(toast, text=message, bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
                       font=("Segoe UI", 10, "bold"), justify="left", padx=20, pady=15)
        lbl.pack(side="left")
        
        btn = tk.Button(toast, text="X", bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
                        font=("Segoe UI", 12, "bold"), relief="flat", activebackground=T("PRIMARY_BG"),
                        command=toast.destroy, cursor="hand2")
        btn.pack(side="right", padx=10)
        
        # Position in bottom right corner of the window
        self.window.update_idletasks()
        x = self.window.winfo_rootx() + self.window.winfo_width() - toast.winfo_reqwidth() - 30
        y = self.window.winfo_rooty() + self.window.winfo_height() - toast.winfo_reqheight() - 30
        toast.geometry(f"+{x}+{y}")
        
        # Auto hide after 15 seconds
        self.window.after(15000, lambda: [toast.destroy() if toast.winfo_exists() else None])

    def _on_close(self):
        """Uygulama kapanmadan önce oturumu kaydet."""
        try:

            # Store memory state to dict
            self.settings["humanize"] = getattr(state, "humanize", False)
            self.settings["total_lifetime_clicks"] = getattr(state, "total_lifetime_clicks", 0)
            
            # Exclude runtime callbacks
            save_dict = {k: v for k, v in self.settings.items() if not callable(v)}
            save_session(list(state.steps), save_dict)
        except Exception as e:
            print(f"[AutoSave] on_close error: {e}")
        finally:
            self.window.destroy()
