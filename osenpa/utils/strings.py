"""
strings.py — Osenpa Auto Clicker UI Text Registry
All user-facing strings are defined here for easy localization.
To add a new language, add a new dict and register it in LANGUAGES.
"""

_EN = {
    # ── App / Window ────────────────────────────────────────────
    "app_title":            "Osenpa Auto Clicker",

    # ── Sidebar ─────────────────────────────────────────────────
    "nav_profiles":         "Profiles",
    "nav_keyboard":         "Keyboard",
    "nav_mouse":            "Mouse",
    "nav_macro":            "Record Actions",
    "nav_color":            "Color Detection",
    "nav_image":            "Image Detection",
    "nav_settings":         "Settings",
    "nav_label":            "NAVIGATION",
    "theme_label":          "THEME",
    "theme_light":          "LIGHT",
    "theme_dark":           "DARK",
    "brand_line1":          "AUTO CLICKER",
    "brand_line2":          "PRO",

    # ── Footer ──────────────────────────────────────────────────
    "btn_run_steps":        "RUN STEPS",
    "btn_stop":             "STOP",
    "footer_status_ready":  "READY",
    "footer_loop":          "LOOP",
    "footer_infinite":      "INFINITE",
    "footer_times":         "TIMES",
    "footer_step_interval": "STEP INTERVAL",
    "footer_hotkey":        "START / STOP HOTKEY",
    "footer_change":        "CHANGE",
    "footer_schedule":      "SCHEDULE",
    "footer_no_steps":      "NO STEPS TO RUN.",
    "footer_running":       "RUNNING...",
    "footer_done":          "DONE.  TOTAL ACTIONS: {n}",
    "footer_action_count":  "RUNNING  —  ACTION {c} / {t}",

    # ── Steps Panel ─────────────────────────────────────────────
    "steps_title":          "STEPS",
    "steps_empty":          "No steps yet.\nUse the panels on the left to add steps.",
    "steps_search":         "Search steps...",
    "btn_export":           "EXPORT",
    "btn_import":           "IMPORT",
    "btn_add_delay":        "ADD DELAY",
    "btn_move_up":          "↑",
    "btn_move_down":        "↓",
    "btn_edit":             "EDIT",
    "btn_duplicate":        "DUP",
    "btn_delete":           "DEL",
    "btn_run_from":         "RUN FROM HERE",
    "btn_clear_all":        "CLEAR ALL",
    "steps_undo_bar":       "{n} step(s) removed  (Ctrl+Z to undo)",
    "steps_copied_bar":     "{n} step(s) copied  (Ctrl+Z to undo)",
    "steps_cleared_bar":    "All steps cleared  (Ctrl+Z to undo)",
    "clear_confirm_title":  "Clear All Steps",
    "clear_confirm_msg":    "All {n} step(s) will be removed.\nThis can be undone with Ctrl+Z.\n\nContinue?",

    # ── Tooltips (Steps Panel) ───────────────────────────────────
    "tt_move_up":           "Move step up",
    "tt_move_down":         "Move step down",
    "tt_edit":              "Edit selected step",
    "tt_duplicate":         "Duplicate selected step",
    "tt_delete":            "Delete selected step(s)",
    "tt_run_from":          "Run automation starting from this step",
    "tt_export":            "Export steps to file",
    "tt_import":            "Import steps from file",
    "tt_clear":             "Clear all steps",
    "tt_add_delay":         "Add a delay step",

    # ── Step default notes ──────────────────────────────────────
    "note_key":             "Press a key (e.g. Enter or A).",
    "note_hotkey":          "Press multiple keys at once (e.g. Ctrl+C to copy).",
    "note_click":           "Click the mouse at a position.",
    "note_drag":            "Drag the mouse from one position to another.",
    "note_scroll":          "Scroll the mouse wheel up or down.",
    "note_color":           "Scan for a color on screen and click when found.",
    "note_image":           "Scan for an image on screen and click when found.",
    "note_delay":           "Wait before moving to the next step.",
    "note_if_color":        "Check if a color is present; do different things based on result.",
    "note_if_image":        "Check if an image is present; do different things based on result.",

    # ── Keyboard Panel ──────────────────────────────────────────
    "kb_title":             "KEYBOARD CONFIGURATION",
    "kb_subtitle":          "Send keystrokes and hotkey combinations",
    "kb_single_key":        "SINGLE KEY",
    "kb_hotkey_combo":      "HOTKEY COMBINATION",
    "kb_combo_format":      "FORMAT: ctrl+z  /  ctrl+shift+s  /  alt+f4",
    "kb_key_label":         "KEY",
    "kb_keys_label":        "KEYS",
    "kb_repeat":            "REPEAT",
    "kb_infinite":          "INFINITE",
    "kb_interval":          "INTERVAL",
    "kb_interval_hint":     "Wait between each keypress",
    "kb_combo_hint":        "Wait between each combo press",
    "kb_placeholder_key":   "PRESS A KEY...",
    "kb_placeholder_combo": "e.g. ctrl+z",
    "kb_infinite_warn":     "Infinite mode is not supported in steps. Set a repeat count first.",
    "kb_no_key":            "NO KEY SPECIFIED.",
    "kb_no_keys":           "NO KEYS SPECIFIED.",
    "kb_step_added":        "STEP ADDED.",
    "kb_running":           "RUNNING...",
    "kb_done":              "DONE.  TOTAL: {n}",
    "kb_running_count":     "RUNNING  —  ACTIONS: {n}",
    "kb_busy":              "STOP THE ACTIVE TASK FIRST.",
    "btn_start":            "START",
    "btn_stop_task":        "STOP",
    "btn_add_to_steps":     "ADD TO STEPS",
    "btn_change":           "CHANGE",
    "lbl_hotkey":           "HOTKEY",
    "lbl_panel_hotkey":     "PANEL HOTKEY",

    # ── Mouse Panel ─────────────────────────────────────────────
    "ms_title":             "MOUSE CONFIGURATION",
    "ms_subtitle":          "Simulate mouse clicks at specific or current coordinates",
    "ms_position_mode":     "POSITION MODE",
    "ms_fixed":             "FIXED COORDINATES",
    "ms_cursor":            "CURRENT CURSOR POSITION",
    "ms_x":                 "X",
    "ms_y":                 "Y",
    "ms_button":            "BUTTON",
    "ms_btn_left":          "LEFT",
    "ms_btn_right":         "RIGHT",
    "ms_btn_middle":        "MIDDLE",
    "ms_repeat":            "REPEAT",
    "ms_infinite":          "INFINITE",
    "ms_interval":          "INTERVAL",
    "ms_drag":              "DRAG",
    "ms_drag_to":           "DRAG TO",
    "ms_drag_hint":         "Enable drag from click position to target",
    "ms_pick_target":       "PICK TARGET",
    "ms_running":           "RUNNING...",
    "ms_done":              "DONE.  TOTAL: {n}",
    "ms_busy":              "STOP THE ACTIVE TASK FIRST.",
    "ms_no_coords":         "PLEASE ENTER COORDINATES.",

    # ── Macro Panel ─────────────────────────────────────────────
    "mac_title":            "RECORD ACTIONS",
    "mac_subtitle":         "Record keyboard and mouse actions",
    "mac_start_rec":        "START RECORDING",
    "mac_stop_rec":         "STOP RECORDING",
    "mac_recording":        "RECORDING...  Press hotkey to stop.",
    "mac_done":             "Recorded {n} step(s).",
    "mac_hotkey":           "RECORD HOTKEY",

    # ── Color Panel ─────────────────────────────────────────────
    "col_title":            "COLOR DETECTION",
    "col_subtitle":         "Click when any of the defined colors appears on screen",
    "col_target":           "TARGET COLORS",
    "col_target_hint":      "Click when ANY of these colors is detected on screen",
    "col_pick":             "＋ PICK COLOR",
    "col_pick_screen":      "＋ PICK FROM SCREEN",
    "col_empty":            "No colors added yet. Use the buttons above to add colors.",
    "col_count_one":        "1 color defined",
    "col_count_many":       "{n} colors defined",
    "col_already_in_list":  "COLOR ALREADY IN LIST: {hex}",
    "col_tolerance":        "DEFAULT TOLERANCE",
    "col_tol_applied":      "APPLIED TO NEW COLORS",
    "col_tol_hint":         "Higher = more forgiving color match",
    "col_tol_warning":      "⚠  Recommended: 15–30 for reliable detection. Very low values may miss the color.",
    "col_settings":         "SETTINGS",
    "col_repeat":           "REPEAT",
    "col_infinite":         "INFINITE",
    "col_scan_interval":    "SCAN INTERVAL",
    "col_scan_hint":        "How often the screen is scanned for colors",
    "col_click_settings":   "CLICK SETTINGS",
    "col_scan_area":        "SCAN AREA",
    "col_area_hint":        "Limit scanning to a specific region (optional)",
    "col_pick_area":        "PICK AREA",
    "col_full_screen":      "FULL SCREEN",
    "col_clear_area":       "CLEAR",
    "col_area_default":     "Full screen (default)",
    "col_area_selected":    "Full screen (selected)",
    "col_step_interval":    "STEP INTERVAL",
    "col_step_iv_hint":     "⏱  Wait AFTER click, before scanning again",
    "col_no_color":         "PLEASE ADD AT LEAST ONE COLOR.",
    "col_scanning":         "SCANNING...",
    "col_stopped":          "STOPPED.",
    "col_clicked":          "CLICKED ({x}, {y})  —  TOTAL: {n}",
    "col_clicked_hex":      "CLICKED ({x}, {y})  [{hex}]  —  TOTAL: {n}",
    "col_busy":             "STOP THE ACTIVE TASK FIRST.",
    "col_add_step":         "ADD TO STEPS",
    "col_step_added":       "STEP ADDED: {n} COLOR(S)",
    "col_cond_title":       "IF / THEN / ELSE  —  CONDITION STEP",
    "col_cond_hint":        "Use the colors above as a conditional trigger.",
    "col_cond_added":       "CONDITION STEP ADDED  ✓ {then}  ✗ {else}",

    # ── Image Panel ─────────────────────────────────────────────
    "img_title":            "IMAGE DETECTION",
    "img_subtitle":         "Click when a target image appears on screen",
    "img_target":           "TARGET IMAGES",
    "img_load_file":        "LOAD IMAGE FILE",
    "img_from_clipboard":   "FROM CLIPBOARD",
    "img_empty":            "No images loaded. Use the buttons above to add images.",
    "img_count_one":        "1 image defined",
    "img_count_many":       "{n} images defined",
    "img_confidence":       "DEFAULT CONFIDENCE",
    "img_conf_hint":        "Minimum match quality (0.0–1.0). Lower = more lenient.",
    "img_settings":         "SETTINGS",
    "img_scan_interval":    "SCAN INTERVAL",
    "img_scan_hint":        "How often the screen is scanned",
    "img_click_settings":   "CLICK SETTINGS",
    "img_scan_area":        "SCAN AREA",
    "img_area_hint":        "Limit scanning to a specific region (optional)",
    "img_step_interval":    "STEP INTERVAL",
    "img_step_iv_hint":     "⏱  Wait AFTER click, before scanning again",
    "img_no_image":         "PLEASE LOAD AT LEAST ONE IMAGE.",
    "img_load_failed":      "FAILED TO LOAD IMAGE.",
    "img_load_failed_all":  "FAILED TO LOAD IMAGES.",
    "img_could_not_start":  "COULD NOT START.",
    "img_scanning":         "SCANNING...",
    "img_stopped":          "STOPPED.",
    "img_clicked":          "CLICKED ({x}, {y})  —  TOTAL: {n}",
    "img_clicked_label":    "CLICKED ({x}, {y})  [{label}]  —  TOTAL: {n}",
    "img_busy":             "STOP THE ACTIVE TASK FIRST.",
    "img_add_step":         "ADD TO STEPS",
    "img_step_added":       "STEP ADDED: {n} IMAGE(S)",
    "img_mouse_park_hint":  "Mouse is temporarily moved after click to avoid blocking detection.",

    # ── Profiles Panel ──────────────────────────────────────────
    "pro_title":            "PROFILES",
    "pro_subtitle":         "Save and load your panel configurations",
    "pro_saved":            "SAVED PROFILES",
    "pro_search":           "Search profiles...",
    "pro_empty":            "No saved profiles yet.\nClick  SAVE CURRENT  to create one.",
    "pro_save_section":     "SAVE CURRENT SETTINGS",
    "pro_name_label":       "PROFILE NAME",
    "pro_scope_label":      "SAVE SETTINGS FROM",
    "pro_scope_all":        "All panels",
    "pro_scope_keyboard":   "Keyboard",
    "pro_scope_mouse":      "Mouse",
    "pro_scope_color":      "Color Detection",
    "pro_scope_image":      "Image Detection",
    "btn_save_current":     "💾  SAVE CURRENT",
    "pro_saved_as":         "✓  Saved as \"{name}\"",
    "pro_save_error":       "✗  Error: {e}",
    "pro_enter_name":       "⚠  Enter a profile name first.",
    "pro_selected":         "SELECTED PROFILE",
    "pro_none_selected":    "— none selected —",
    "btn_load_profile":     "▶  LOAD PROFILE",
    "btn_rename":           "✏  RENAME",
    "btn_delete_profile":   "✕  DELETE",
    "pro_load_ok":          "✓  Profile loaded.",
    "pro_load_fail":        "✗  Could not load profile.",
    "pro_load_error":       "✗  Error: {e}",
    "pro_delete_confirm":   "Delete \"{name}\"?\n\nThis cannot be undone.",
    "pro_delete_ok":        "✓  Profile deleted.",
    "pro_delete_fail":      "✗  Could not delete.",
    "pro_rename_title":     "Rename Profile",
    "pro_rename_label":     "NEW NAME",
    "btn_rename_ok":        "RENAME",
    "btn_cancel":           "CANCEL",
    "pro_renamed_ok":       "✓  Renamed to \"{name}\"",
    "btn_refresh":          "↺  REFRESH",
    "pro_scope_saved":      "Scope: {tab}",
    "pro_saved_date":       "Saved: {date}",

    # ── Settings Panel ──────────────────────────────────────────
    "set_title":            "SETTINGS",
    "set_subtitle":         "Application preferences",
    "set_display":          "DISPLAY",
    "set_show_indicator":   "SHOW ACTIVE TASK INDICATOR",
    "set_indicator_hint":   "Overlay shown in bottom-right during automation",
    "set_show_border":      "SHOW SCAN AREA BORDER",
    "set_border_hint":      "Border around scan region during detection",
    "set_hotkeys":          "HOTKEYS",
    "set_hk_run_stop":      "Run / Stop",
    "set_hk_macro":         "Record Actions",
    "set_hk_color":         "Color Detection",
    "set_hk_image":         "Image Detection",
    "set_hk_keyboard":      "Keyboard Panel",
    "set_hk_mouse":         "Mouse Panel",
    "set_reset_hotkeys":    "Reset all hotkeys to their defaults",
    "btn_reset_hotkeys":    "RESET HOTKEYS",
    "set_hotkeys_reset_ok": "ALL HOTKEYS RESET TO DEFAULTS.",
    "set_reset_section":    "RESET",
    "set_reset_all_title":  "RESET ALL SETTINGS",
    "set_reset_all_hint":   "Delete session, clear steps and hotkeys. Profiles are kept.",
    "btn_reset_all":        "RESET ALL",
    "set_reset_confirm_t":  "Reset All Settings",
    "set_reset_confirm_m":  "All steps, hotkeys and session data will be cleared.\nSaved profiles will NOT be deleted.\n\nContinue?",
    "set_reset_ok":         "SETTINGS RESET.",
    "set_restart_fail":     "RESTART FAILED: {e}",

    # ── Overlay Indicator ────────────────────────────────────────
    "ov_actions":           "ACTIONS: {n}",
    "ov_scans":             "SCANS: {n}",
    "ov_stop":              "STOP: {key}",
    "ov_automation":        "AUTOMATION RUNNING",
    "ov_macro":             "MACRO RECORDING",
    "ov_keyboard":          "KEYBOARD ACTIVE\nKEY: {key}",
    "ov_combo":             "KEYBOARD ACTIVE\nHOTKEY: {key}",
    "ov_scanning_color":    "SCANNING {n} COLOR(S)",
    "ov_scanning_image":    "SCANNING {n} IMAGE(S)",

    # ── Session Restore ──────────────────────────────────────────
    "session_restore_t":    "Restore Session",
    "session_restore_m":    "Found {n} step(s) from your last session.\n\nWould you like to restore them?",
    "session_restored":     "SESSION RESTORED  —  {n} STEPS",

    # ── Hotkey messages ──────────────────────────────────────────
    "hk_duplicate":         "'{key}' IS ALREADY ASSIGNED.",
    "hk_press_for":         "PRESS ANY KEY FOR {label} HOTKEY...",
    "hk_changed_ready":     "READY",

    # ── Busy / Error ─────────────────────────────────────────────
    "busy_stop_first":      "STOP THE ACTIVE TASK FIRST.",

    # ── Step Edit Dialog ─────────────────────────────────────────
    "edit_title":           "Edit Step",
    "edit_save":            "SAVE",
    "edit_close":           "CLOSE",

    # ── Delay Dialog ─────────────────────────────────────────────
    "delay_title":          "⏱  ADD DELAY STEP",
    "delay_duration":       "WAIT DURATION",
    "delay_label_opt":      "LABEL  (optional — shown in steps list)",
    "btn_add_delay_ok":     "ADD DELAY",
    "delay_preview_secs":   "= {n:.2f} seconds",
    "delay_preview_ms":     "= {n} ms",
    "delay_preview_min":    "= {n:.2f} minutes",
    "delay_preview_hr":     "= {n:.2f} hours",
    "delay_preview_inv":    "= invalid value",

    # ── Profile Load Warning ─────────────────────────────────────
    "pro_load_warn_t":      "Profile Load Warning",
    "pro_load_warn_m":      "Some sections could not be applied:\n{errors}",

    # ── Export / Import ──────────────────────────────────────────
    "export_ok":            "STEPS EXPORTED.",
    "import_ok":            "STEPS IMPORTED.  ({n} STEPS)",
    "export_fail_t":        "Export Failed",
    "export_fail_m":        "Could not save steps:\n{e}",
    "import_fail_t":        "Import Failed",
    "import_fail_inv":      "Invalid file format: expected a list of steps.",
    "import_fail_json":     "File contains invalid JSON:\n{e}",
    "import_fail_read":     "Could not read file:\n{e}",
}

LANGUAGES = {"English": _EN}
_current = "English"


def set_language(lang: str):
    global _current
    if lang in LANGUAGES:
        _current = lang


def get_language() -> str:
    return _current


def available_languages() -> list:
    return list(LANGUAGES.keys())


def S(key: str, **kwargs) -> str:
    """Get string by key with optional .format() substitutions."""
    text = LANGUAGES.get(_current, _EN).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text
