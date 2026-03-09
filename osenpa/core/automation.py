import threading
import time
import pyautogui
import numpy as np
import cv2
import random
import logging
from pynput.keyboard import Controller as KbController, KeyCode
from core import state

logging.basicConfig(level=logging.ERROR,
                    format="%(asctime)s [%(levelname)s] %(message)s")

# FAILSAFE ACTIVE TO PREVENT GETTING STUCK
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.0

_kb_controller = KbController()

def _press_key(key):
    """Her karakteri pynput ile doğrudan bas — Türkçe dahil."""
    if not key or not key.strip():          # ← boş string / sadece boşluk koruması
        return
    key = key.strip()
    if len(key) == 1:
        try:
            _kb_controller.press(KeyCode.from_char(key))
            time.sleep(random.uniform(0.02, 0.06) if state.humanize else 0.01)
            _kb_controller.release(KeyCode.from_char(key))
            return
        except Exception as e:
            logging.error(f"Pynput key press error '{key}': {e}")
    try:
        pyautogui.press(key)
    except Exception as e:
        logging.error(f"PyAutoGUI key press error '{key}': {e}")


def _press_hotkey(keys_str):
    """'+' ile ayrılmış hotkey combo'yu güvenle bas."""
    if not keys_str or not keys_str.strip():   # ← boş string koruması
        return
    km     = {"ctrl": "ctrl", "shift": "shift", "alt": "alt", "cmd": "win"}
    parts  = [k.strip() for k in keys_str.split("+") if k.strip()]
    if not parts:
        return
    mapped = [km.get(p, p) for p in parts]
    try:
        pyautogui.hotkey(*mapped)
    except Exception as e:
        logging.error(f"Hotkey press error '{keys_str}': {e}")


def _scan_color(target_rgb, tolerance, area=None):
    if area:
        x1, y1, x2, y2 = area
        w, h = x2 - x1, y2 - y1
        if w <= 0 or h <= 0:
            return None
        screenshot = pyautogui.screenshot(region=(x1, y1, w, h))
        offset_x, offset_y = x1, y1
    else:
        screenshot = pyautogui.screenshot()
        offset_x, offset_y = 0, 0
    
    img = np.array(screenshot)
    r, g, b = target_rgb
    
    lower_bound = np.array([max(0, r - tolerance), max(0, g - tolerance), max(0, b - tolerance)])
    upper_bound = np.array([min(255, r + tolerance), min(255, g + tolerance), min(255, b + tolerance)])
    
    mask = cv2.inRange(img, lower_bound, upper_bound)
    coords = cv2.findNonZero(mask)

    if coords is not None and len(coords) > 0:
        x, y = coords[0][0]
        return int(x) + offset_x, int(y) + offset_y
    return None


def _scan_image(image_path, confidence, area=None,
                clipboard_img=None):
    try:
        if clipboard_img is not None:
            template = cv2.cvtColor(
                np.array(clipboard_img), cv2.COLOR_RGB2BGR)
        else:
            template = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if template is None:
            return None
        if area:
            x1, y1, x2, y2 = area
            w, h = x2 - x1, y2 - y1
            if w <= 0 or h <= 0:
                return None
            screenshot = pyautogui.screenshot(region=(x1, y1, w, h))
            offset_x, offset_y = x1, y1
        else:
            screenshot = pyautogui.screenshot()
            offset_x, offset_y = 0, 0
        screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        th, tw = template.shape[:2]
        sh, sw = screen.shape[:2]
        if th > sh or tw > sw:
            return None
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val >= confidence:
            cx = max_loc[0] + tw // 2 + offset_x
            cy = max_loc[1] + th // 2 + offset_y
            return cx, cy
    except Exception:
        pass
    return None


def run_step(step, global_interval=None, on_action=None, on_condition_result=None):
    """Tek bir adımı çalıştır. on_action(count) her aksiyonda çağrılır."""
    stype = step.get("type", "")

    # ── if_color / if_image → repeat kavramı ANLAMSIZ, döngü DIŞINDA çalışır ──
    if stype in ("if_color", "if_image"):
        if not state.running:
            return
        _run_condition_step(step, on_action, on_condition_result)
        # Koşul adımı kendi interval'ını tüketir (genellikle 0.1s)
        interval = step.get("interval", global_interval if global_interval is not None else 0.1)
        _interruptible_sleep(interval)
        return

    # ── Diğer tüm tipler: repeat döngüsüyle çalışır ───────────────────────────
    for _ in range(step.get("repeat", 1)):
        if not state.running:
            return
        stype = step.get("type", "")

        if stype == "key":
            _press_key(step["key"])
            _count = state.increment_action()
            if on_action:
                on_action(_count)

        elif stype == "hotkey":
            _press_hotkey(step.get("keys", ""))
            _count = state.increment_action()
            if on_action:
                on_action(_count)

        elif stype == "click":
            use_cursor = step.get("use_cursor", False)
            if use_cursor:
                x, y = pyautogui.position()
            else:
                x, y = step["x"], step["y"]
                if state.humanize:
                    x += random.randint(-3, 3)
                    y += random.randint(-3, 3)

            if "drag_to" in step:
                dx, dy = step["drag_to"][0], step["drag_to"][1]
                if state.humanize:
                    dx += random.randint(-4, 4)
                    dy += random.randint(-4, 4)
                btn = step.get("button", "left")
                pyautogui.moveTo(x, y, duration=random.uniform(0.1, 0.3) if state.humanize else 0.05)
                pyautogui.mouseDown(button=btn)
                time.sleep(random.uniform(0.05, 0.1) if state.humanize else 0.05)
                pyautogui.moveTo(dx, dy, duration=random.uniform(0.2, 0.5) if state.humanize else 0.2)
                time.sleep(random.uniform(0.05, 0.1) if state.humanize else 0.05)
                pyautogui.mouseUp(button=btn)
            else:
                pyautogui.click(x, y, button=step["button"])
                if state.humanize:
                    time.sleep(random.uniform(0.02, 0.08))

            _count = state.increment_action()
            if on_action:
                on_action(_count)

        elif stype == "scroll":
            x  = step.get("x", 0)
            y  = step.get("y", 0)
            dy = step.get("dy", 0)
            dx = step.get("dx", 0)
            clicks = int(dy) if dy != 0 else int(dx)
            pyautogui.scroll(clicks, x=x, y=y)
            _count = state.increment_action()
            if on_action:
                on_action(_count)

        elif stype == "color":
            raw_colors = step.get("target_colors")
            raw_tols   = step.get("tolerances", [])
            if raw_colors and len(raw_colors) > 0:
                color_list = [
                    (tuple(c), raw_tols[i] if i < len(raw_tols) else step.get("tolerance", 0))
                    for i, c in enumerate(raw_colors)
                ]
            else:
                color_list = [(tuple(step["rgb"]), step.get("tolerance", 0))]
            area          = step.get("area")
            button        = step.get("button", "left")
            scan_interval = step.get("scan_interval", 0.5)
            timeout       = step.get("timeout", 0.0)   # 0 = sınırsız
            _deadline     = (time.time() + timeout) if timeout > 0 else None
            while state.running:
                if _deadline and time.time() >= _deadline:
                    break  # Timeout: renk bulunamadı, sonraki adıma geç
                result = None
                for rgb, tol in color_list:
                    result = _scan_color(rgb, tol, area)
                    if result:
                        break
                if result:
                    pyautogui.click(result[0], result[1], button=button)
                    _count = state.increment_action()
                    if on_action:
                        on_action(_count)
                    break
                _interruptible_sleep(scan_interval)

        elif stype == "image":
            raw_image_list = step.get("image_list")
            confidence     = step.get("confidence", 0.8)
            area           = step.get("area")
            button         = step.get("button", "left")
            scan_interval  = step.get("scan_interval", 0.5)
            timeout        = step.get("timeout", 0.0)   # 0 = sınırsız
            _deadline      = (time.time() + timeout) if timeout > 0 else None
            if raw_image_list and len(raw_image_list) > 0:
                img_entries = [
                    (
                        item.get("path"),
                        (np.array(item["array"], dtype=np.uint8) if item.get("array") is not None else None),
                        item.get("confidence", confidence),
                    )
                    for item in raw_image_list
                ]
            else:
                clip = step.get("clipboard_image")
                clip_arr = np.array(clip, dtype=np.uint8) if clip is not None else None
                img_entries = [(step.get("image_path"), clip_arr, confidence)]
            while state.running:
                if _deadline and time.time() >= _deadline:
                    break  # Timeout: görsel bulunamadı, sonraki adıma geç
                result = None
                for img_path, clip_arr, conf in img_entries:
                    result = _scan_image(img_path, conf, area, clip_arr)
                    if result:
                        break
                if result:
                    pyautogui.click(result[0], result[1], button=button)
                    _count = state.increment_action()
                    if on_action:
                        on_action(_count)
                    break
                _interruptible_sleep(scan_interval)

        elif stype == "delay":
            duration = step.get("duration", 1.0)
            if state.humanize:
                duration += random.uniform(-0.05, 0.1)
            _interruptible_sleep(max(0.0, duration))

        # Adımın kendi interval'ı önceliklidir.
        interval = step.get("interval", global_interval if global_interval is not None else 0.1)
        if state.humanize:
            interval += random.uniform(0, 0.05)
        _interruptible_sleep(interval)


def _run_condition_step(step, on_action, on_condition_result=None):
    """
    if_color / if_image adımını çalıştır.
    repeat döngüsünden BAĞIMSIZ — koşul adımı her zaman TEK KEZ değerlendirilir.
    """
    stype = step.get("type", "")

    # ── Koşulu değerlendir ────────────────────────────────────────────────────
    found_pos     = None
    area          = step.get("area")
    scan_interval = step.get("scan_interval", 0.5)
    max_wait      = step.get("max_wait", 0.0)   # 0 = tek tarama
    button        = step.get("button", "left")

    if stype == "if_color":
        raw_colors = step.get("target_colors")
        raw_tols   = step.get("tolerances", [])
        if raw_colors and len(raw_colors) > 0:
            color_list = [
                (tuple(c), raw_tols[i] if i < len(raw_tols) else step.get("tolerance", 15))
                for i, c in enumerate(raw_colors)
            ]
        else:
            rgb = step.get("rgb", [255, 0, 0])
            color_list = [(tuple(rgb), step.get("tolerance", 15))]

        deadline = time.time() + max_wait
        while state.running:
            for rgb, tol in color_list:
                found_pos = _scan_color(rgb, tol, area)
                if found_pos:
                    break
            if found_pos:
                break
            if max_wait <= 0 or time.time() >= deadline:
                break
            _interruptible_sleep(scan_interval)

    else:  # if_image
        raw_image_list = step.get("image_list")
        confidence     = step.get("confidence", 0.8)
        if raw_image_list and len(raw_image_list) > 0:
            img_entries = [
                (
                    item.get("path"),
                    (np.array(item["array"], dtype=np.uint8) if item.get("array") is not None else None),
                    item.get("confidence", confidence),
                )
                for item in raw_image_list
            ]
        else:
            clip     = step.get("clipboard_image")
            clip_arr = np.array(clip, dtype=np.uint8) if clip is not None else None
            img_entries = [(step.get("image_path"), clip_arr, confidence)]

        deadline = time.time() + max_wait
        while state.running:
            for img_path, clip_arr, conf in img_entries:
                found_pos = _scan_image(img_path, conf, area, clip_arr)
                if found_pos:
                    break
            if found_pos:
                break
            if max_wait <= 0 or time.time() >= deadline:
                break
            _interruptible_sleep(scan_interval)

    # ── Dalı seç ve aksiyonu çalıştır ────────────────────────────────────────
    branch_key = "then_action" if found_pos else "else_action"
    action     = step.get(branch_key) or {}
    atype      = action.get("type", "none")
    branch_label = "THEN" if found_pos else "ELSE"

    # Overlay'e hangi dalın tetiklendiğini bildir
    if on_condition_result:
        on_condition_result(branch_label, atype)

    if atype == "click_found" and found_pos:
        pyautogui.click(found_pos[0], found_pos[1], button=button)
        _count = state.increment_action()
        if on_action:
            on_action(_count)

    elif atype == "click":
        x   = action.get("x", 0)
        y   = action.get("y", 0)
        btn = action.get("button", button)
        if state.humanize:
            x += random.randint(-3, 3)
            y += random.randint(-3, 3)
        pyautogui.click(x, y, button=btn)
        _count = state.increment_action()
        if on_action:
            on_action(_count)

    elif atype == "key":
        key_val = action.get("key", "").strip()
        if key_val:                          # ← boş key koruması
            _press_key(key_val)
            _count = state.increment_action()
            if on_action:
                on_action(_count)

    elif atype == "hotkey":
        keys_val = action.get("keys", "").strip()
        if keys_val:                         # ← boş hotkey koruması
            _press_hotkey(keys_val)
            _count = state.increment_action()
            if on_action:
                on_action(_count)

    elif atype == "delay":
        duration = action.get("duration", 1.0)
        if state.humanize:
            duration += random.uniform(-0.05, 0.1)
        _interruptible_sleep(max(0.0, float(duration)))

    elif atype == "go_to":
        return {"go_to": action.get("step_index", 1)}

    elif atype == "stop":
        state.running = False

    else:
        _count = state.increment_action()
        if on_action:
            on_action(_count)


def _interruptible_sleep(seconds):
    """Event.wait ile 0 CPU kullanımı sunan optimize uyku."""
    if seconds > 0 and state.running:
        state.stop_event.wait(timeout=seconds)


def automation_loop(on_done, on_no_steps, loop_infinite,
                    loop_count, global_interval, on_action,
                    on_condition_result=None, start_from=0,
                    on_step_change=None):
    """
    global_interval = Footer'daki STEP INTERVAL.
    start_from      = Başlanacak adım indeksi (0-tabanlı).
    on_step_change  = (step_index) -> None  — aktif adım değiştiğinde çağrılır.
    """
    if not state.steps:
        state.running = False
        on_no_steps()
        return
    total_loops = -1 if loop_infinite else loop_count
    loop_num    = 0
    start_idx   = max(0, min(start_from, len(state.steps) - 1))
    jump_count  = 0
    MAX_JUMPS_PER_LOOP = 1000  # Sonsuz döngü kilitlenmesini önleyen limit

    while state.running:
        steps_slice = state.steps[start_idx:] if loop_num == 0 else state.steps
        i = 0
        while i < len(steps_slice):
            if not state.running:
                break
            step  = steps_slice[i]
            abs_i = (start_idx + i) if loop_num == 0 else i
            if on_step_change:
                on_step_change(abs_i)

            try:
                result = run_step(step, global_interval, on_action, on_condition_result)
            except Exception as e:
                logging.error(f"Error running step {abs_i}: {e}")
                result = None

            if isinstance(result, dict) and "go_to" in result:
                jump_count += 1
                if jump_count > MAX_JUMPS_PER_LOOP:
                    logging.warning(f"Max jumps ({MAX_JUMPS_PER_LOOP}) exceeded! Breaking loop to prevent freeze.")
                    state.running = False
                    break

                target_1based = result["go_to"]
                target_0based = max(0, target_1based - 1)
                if loop_num == 0:
                    abs_target = min(target_0based, len(state.steps) - 1)
                    slice_start = start_idx
                    new_rel = abs_target - slice_start
                    if new_rel >= 0:
                        i = new_rel
                    else:
                        i += 1
                else:
                    i = min(target_0based, len(steps_slice) - 1)
                continue
            
            i += 1
        
        loop_num += 1
        jump_count = 0  # Yeni döngüde jump sayacını sıfırla

        if not loop_infinite and loop_num >= total_loops:
            break
        if state.running and global_interval and global_interval > 0:
            _interruptible_sleep(global_interval)
    state.running = False
    if on_step_change:
        on_step_change(-1)   # Bitti — highlight kaldır
    on_done(loop_num)


def start(on_done, on_no_steps, loop_infinite, loop_count,
          global_interval=None, on_click=None, on_condition_result=None,
          start_from=0, on_step_change=None):
    if state.running:
        return
    state.running = True
    state.reset_counts()
    t = threading.Thread(
        target=automation_loop,
        args=(on_done, on_no_steps, loop_infinite,
              loop_count, global_interval, on_click),
        kwargs={"on_condition_result": on_condition_result,
                "start_from": start_from,
                "on_step_change": on_step_change},
        daemon=True
    )
    t.start()


def stop():
    state.running = False