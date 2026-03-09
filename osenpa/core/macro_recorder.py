import time
from pynput import keyboard as pynput_keyboard
from pynput import mouse as pynput_mouse
from core import state

_events = []
_start_time = None
_kb_listener = None
_ms_listener = None
_on_stop_callback = None
_pressed_modifiers = set()
_drag_start = None
_mouse_down_pos = None

MODIFIER_KEYS = {
    pynput_keyboard.Key.ctrl_l: "ctrl",
    pynput_keyboard.Key.ctrl_r: "ctrl",
    pynput_keyboard.Key.shift_l: "shift",
    pynput_keyboard.Key.shift_r: "shift",
    pynput_keyboard.Key.alt_l: "alt",
    pynput_keyboard.Key.alt_r: "alt",
    pynput_keyboard.Key.cmd: "cmd",
}


def _get_key_name(key):
    name = getattr(key, "name", None)
    if name:
        return name
    char = getattr(key, "char", None)
    if char and ord(char) >= 32:
        return char
    vk = getattr(key, "vk", None)
    if vk:
        if 65 <= vk <= 90:
            return chr(vk + 32)
        if 48 <= vk <= 57:
            return chr(vk)
    return str(key)


def _on_key_press(key):
    if not state.macro_recording:
        return

    if key in MODIFIER_KEYS:
        _pressed_modifiers.add(MODIFIER_KEYS[key])
        return

    key_name = _get_key_name(key)

    if key_name == state.macro_hotkey:
        return

    t = round(time.time() - _start_time, 3)

    if _pressed_modifiers:
        combo = "+".join(sorted(_pressed_modifiers)) + "+" + key_name
        _events.append({"type": "hotkey", "keys": combo, "time": t})
    else:
        _events.append({"type": "key", "key": key_name, "time": t})


def _on_key_release(key):
    if key in MODIFIER_KEYS:
        _pressed_modifiers.discard(MODIFIER_KEYS[key])


def _on_mouse_click(x, y, button, pressed):
    if not state.macro_recording:
        return
    global _drag_start, _mouse_down_pos
    btn_name = (
        "left"   if "left"   in str(button) else
        "right"  if "right"  in str(button) else
        "middle"
    )
    t = round(time.time() - _start_time, 3)
    if pressed:
        _drag_start      = (x, y, t)
        _mouse_down_pos  = (x, y)
        # click'i şimdilik kaydetme, release'te karar ver
    else:
        if _drag_start:
            dx = abs(x - _drag_start[0])
            dy = abs(y - _drag_start[1])
            press_t = _drag_start[2]
            if dx > 5 or dy > 5:
                # Sürükleme / metin seçme: press + drag_end çifti
                _events.append({"type": "click",
                                "x": _drag_start[0], "y": _drag_start[1],
                                "button": btn_name, "time": press_t})
                _events.append({"type": "drag_end", "x": x, "y": y,
                                "button": btn_name, "time": t})
            else:
                # Normal tıklama
                _events.append({"type": "click", "x": x, "y": y,
                                "button": btn_name, "time": press_t})
        _drag_start     = None
        _mouse_down_pos = None


def _on_mouse_scroll(x, y, dx, dy):
    """Scroll olaylarını kaydet."""
    if not state.macro_recording:
        return
    t = round(time.time() - _start_time, 3)
    _events.append({
        "type":   "scroll",
        "x":      x,
        "y":      y,
        "dx":     dx,
        "dy":     dy,
        "time":   t
    })


def _on_mouse_move(x, y):
    """Drag sırasında ara pozisyonları kaydetme — sadece drag_end yeterli."""
    pass


def start(on_stop_callback):
    global _events, _start_time, _kb_listener, _ms_listener
    global _on_stop_callback, _pressed_modifiers, _drag_start, _mouse_down_pos
    if state.macro_recording:
        return
    _events          = []
    _pressed_modifiers = set()
    _drag_start      = None
    _mouse_down_pos  = None
    _start_time      = time.time()
    _on_stop_callback = on_stop_callback
    state.macro_recording = True
    _kb_listener = pynput_keyboard.Listener(
        on_press=_on_key_press,
        on_release=_on_key_release
    )
    _ms_listener = pynput_mouse.Listener(
        on_click=_on_mouse_click,
        on_scroll=_on_mouse_scroll
    )
    _kb_listener.daemon = True
    _ms_listener.daemon = True
    _kb_listener.start()
    _ms_listener.start()


def stop():
    global _kb_listener, _ms_listener
    if not state.macro_recording:
        return
    state.macro_recording = False
    if _kb_listener:
        _kb_listener.stop()
    if _ms_listener:
        _ms_listener.stop()
    if _on_stop_callback:
        _on_stop_callback(_events)


def convert_to_steps(events):
    result = []
    for i, e in enumerate(events):
        interval = (
            round(events[i+1]["time"] - e["time"], 3)
            if i + 1 < len(events) else 0.1
        )
        interval = max(0.05, interval)

        if e["type"] == "key":
            result.append({"type": "key", "key": e["key"],
                           "interval": interval, "repeat": 1})

        elif e["type"] == "hotkey":
            result.append({"type": "hotkey", "keys": e["keys"],
                           "interval": interval, "repeat": 1})

        elif e["type"] == "click":
            result.append({"type": "click", "x": e["x"], "y": e["y"],
                           "button": e["button"],
                           "interval": interval, "repeat": 1})

        elif e["type"] == "drag_end":
            # Son click adımına drag_to ekle (metin seçme / sürükleme)
            # Geriye doğru en yakın click'i bul (arada scroll olabilir)
            added = False
            for j in range(len(result) - 1, -1, -1):
                if result[j]["type"] == "click" and "drag_to" not in result[j]:
                    result[j]["drag_to"] = (e["x"], e["y"])
                    added = True
                    break
            if not added:
                result.append({"type": "click",
                               "x": e["x"], "y": e["y"],
                               "button": e["button"],
                               "interval": interval, "repeat": 1})

        elif e["type"] == "scroll":
            result.append({"type": "scroll",
                           "x":  e["x"],  "y":  e["y"],
                           "dx": e["dx"], "dy": e["dy"],
                           "interval": interval, "repeat": 1})
    return result
