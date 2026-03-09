"""
language.py — AutoClicker Pro language registry (legacy compatibility layer).

The main string system is now utils/strings.py (S() function).
This file is kept for backward compatibility with any code still using T().
All languages are English-only for now; additional languages can be added
to utils/strings.py LANGUAGES dict.
"""

from utils.strings import S, set_language, get_language, available_languages

# Legacy T() shim — maps old keys to strings.py keys or falls back to key itself
_KEY_MAP = {
    "title":              "app_title",
    "start":              "btn_start",
    "stop":               "btn_stop_task",
    "add_step":           "btn_add_to_steps",
    "pick_target":        "ms_pick_target",
    "export":             "btn_export",
    "import":             "btn_import",
    "clear_all":          "btn_clear_all",
    "no_steps":           "steps_empty",
    "status_running":     "kb_running",
    "status_done":        "kb_done",
    "status_picking":     "ms_no_coords",
    "macro_record":       "mac_start_rec",
    "macro_recording":    "mac_recording",
    "macro_stopped":      "mac_done",
}

def T(key: str) -> str:
    """Legacy string lookup — prefers strings.py, falls back to English dict."""
    mapped = _KEY_MAP.get(key)
    if mapped:
        return S(mapped)
    return S(key) if key in _get_all_keys() else key

def _get_all_keys():
    from utils.strings import LANGUAGES, _current
    return set(LANGUAGES.get(_current, {}).keys())
