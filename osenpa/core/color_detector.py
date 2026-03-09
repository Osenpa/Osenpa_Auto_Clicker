import threading
import time
import numpy as np
import pyautogui
from core import state

# FailSafe devre dışı — köşeye gidilince crash olmaz
pyautogui.FAILSAFE = False


class ColorDetector:
    def __init__(self):
        self.running = False
        self.target_rgb = None        # tekli renk (eski uyumluluk)
        self.target_colors = []       # çoklu renk listesi: [(r,g,b), ...]
        self.tolerances = []          # her renge ait tolerans listesi
        self.tolerance = 15
        self.scan_interval = 0.5
        self.step_interval = 0
        self.click_button = "left"
        self.area = None
        self.on_found = None
        self.on_area_highlight = None
        self._thread = None

    def start(self, target_rgb, scan_interval,
              click_button, on_found, on_status=None, area=None,
              on_area_highlight=None, tolerance=15, step_interval=0,
              on_scan=None, target_colors=None, tolerances=None,
              repeat=0, infinite=True):
        if self.running:
            return

        # Çoklu renk desteği
        if target_colors and len(target_colors) > 0:
            self.target_colors = list(target_colors)
            self.tolerances = (list(tolerances)
                               if tolerances and len(tolerances) == len(target_colors)
                               else [tolerance] * len(target_colors))
        elif target_rgb:
            self.target_colors = [target_rgb]
            self.tolerances = [max(tolerance, 0)]
        else:
            self.target_colors = []
            self.tolerances = []

        self.target_rgb = target_rgb
        self.tolerance = max(tolerance, 0)
        self.scan_interval = scan_interval
        self.step_interval = step_interval
        self.click_button = click_button
        self.area = area
        self.on_found = on_found
        self.on_scan = on_scan
        self.on_area_highlight = on_area_highlight
        # repeat=0 means infinite
        self._repeat = 0 if infinite else max(1, repeat)
        self._infinite = infinite
        self.running = True
        state.color_scanning = True
        if on_area_highlight and area:
            on_area_highlight(area, True)
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False
        state.color_scanning = False
        if self.on_area_highlight and self.area:
            self.on_area_highlight(self.area, False)

    def _loop(self):
        scan_count = 0
        click_count = 0
        while self.running:
            try:
                scan_count += 1
                if self.on_scan:
                    self.on_scan(scan_count)
                result = self._scan()
                if result and self.running:
                    x, y, matched_rgb = result
                    pyautogui.click(x, y, button=self.click_button)
                    _cnt = state.increment_click()
                    click_count += 1
                    if self.on_found:
                        self.on_found(x, y, _cnt, matched_rgb)
                    if self.step_interval and self.step_interval > 0:
                        end = time.time() + self.step_interval
                        while self.running and time.time() < end:
                            time.sleep(min(0.05, end - time.time()))
                    # Stop if not infinite and repeat count reached
                    if not self._infinite and click_count >= self._repeat:
                        self.stop()
                        return
            except Exception as e:
                print(f"[ColorDetector] loop error: {e}")
            end = time.time() + max(0.05, self.scan_interval)
            while self.running and time.time() < end:
                time.sleep(min(0.05, end - time.time()))

    def _scan(self):
        if not self.target_colors:
            return None
        try:
            if self.area:
                x1, y1, x2, y2 = self.area
                w, h = x2 - x1, y2 - y1
                if w <= 0 or h <= 0:
                    return None
                screenshot = pyautogui.screenshot(region=(x1, y1, w, h))
                offset_x, offset_y = x1, y1
            else:
                screenshot = pyautogui.screenshot()
                offset_x, offset_y = 0, 0

            img = np.array(screenshot.convert("RGB"))

            # Tüm renkleri sırayla tara — ilk eşleşeni döndür
            for idx, (r, g, b) in enumerate(self.target_colors):
                tol = (self.tolerances[idx]
                       if idx < len(self.tolerances)
                       else self.tolerance)

                mask = (
                    (np.abs(img[:, :, 0].astype(np.int16) - r) <= tol) &
                    (np.abs(img[:, :, 1].astype(np.int16) - g) <= tol) &
                    (np.abs(img[:, :, 2].astype(np.int16) - b) <= tol)
                )
                coords = np.argwhere(mask)
                if len(coords) > 0:
                    mid = len(coords) // 2
                    py, px = coords[mid]
                    return int(px) + offset_x, int(py) + offset_y, (r, g, b)

        except Exception as e:
            print(f"[ColorDetector] scan error: {e}")
        return None
