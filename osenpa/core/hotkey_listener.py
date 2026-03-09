from pynput import keyboard as pynput_keyboard
from core import state

_callbacks = {}
_listener  = None

ALL_HOTKEY_FIELDS = [
    "hotkey", "macro_hotkey", "color_hotkey",
    "image_hotkey", "kb_hotkey", "kb_key_hotkey",
    "kb_combo_hotkey", "mouse_hotkey"
]


def is_duplicate(new_key, current_field):
    for field in ALL_HOTKEY_FIELDS:
        if field == current_field:
            continue
        if getattr(state, field, None) == new_key:
            return True
    return False


def register(event_name, callback):
    _callbacks[event_name] = callback


def _on_press(key):
    try:
        key_name = key.name
    except AttributeError:
        try:
            key_name = key.char
        except Exception:
            return

    # ── Hotkey değiştirme modları ────────────────────────────
    changing_map = [
        ("changing_hotkey",           "hotkey",           "hotkey_changed"),
        ("changing_macro_hotkey",     "macro_hotkey",     "macro_hotkey_changed"),
        ("changing_color_hotkey",     "color_hotkey",     "color_hotkey_changed"),
        ("changing_image_hotkey",     "image_hotkey",     "image_hotkey_changed"),
        ("changing_kb_hotkey",        "kb_hotkey",        "kb_hotkey_changed"),
        ("changing_kb_key_hotkey",    "kb_key_hotkey",    "kb_key_hotkey_changed"),
        ("changing_kb_combo_hotkey",  "kb_combo_hotkey",  "kb_combo_hotkey_changed"),
        ("changing_mouse_hotkey",     "mouse_hotkey",     "mouse_hotkey_changed"),
    ]
    for flag, field, event in changing_map:
        if getattr(state, flag, False):
            if is_duplicate(key_name, field):
                if "hotkey_duplicate" in _callbacks:
                    _callbacks["hotkey_duplicate"](key_name)
                setattr(state, flag, False)
                return
            setattr(state, field, key_name)
            setattr(state, flag, False)
            if event in _callbacks:
                _callbacks[event](key_name)
            return

    # ── Tetikleyiciler ────────────────────────────────────────
    if key_name == state.hotkey:
        if state.running:
            _fire("automation_stop")
        else:
            _fire("automation_start")
        return

    if key_name == state.macro_hotkey:
        if state.macro_recording:
            _fire("macro_stop")
        else:
            _fire("macro_start")
        return

    if key_name == state.color_hotkey:
        if state.color_scanning:
            _fire("color_stop")
        else:
            _fire("color_start")
        return

    if key_name == state.image_hotkey:
        if state.image_scanning:
            _fire("image_stop")
        else:
            _fire("image_start")
        return

    if key_name == getattr(state, "kb_key_hotkey", "f11"):   # default: f11 (avoids alt+f4 conflict)
        if getattr(state, "kb_key_running", False):
            _fire("kb_key_stop")
        else:
            _fire("kb_key_start")
        return

    if key_name == getattr(state, "kb_combo_hotkey", "f3"):  # default: f3 (state.py ile tutarlı)
        if getattr(state, "kb_combo_running", False):
            _fire("kb_combo_stop")
        else:
            _fire("kb_combo_start")
        return

    if key_name == getattr(state, "mouse_hotkey", "f6"):
        if getattr(state, "mouse_running", False):
            _fire("mouse_stop")
        else:
            _fire("mouse_start")
        return


def _fire(event):
    if event in _callbacks:
        _callbacks[event]()


def start():
    global _listener
    _listener = pynput_keyboard.Listener(on_press=_on_press)
    _listener.daemon = True
    _listener.start()