import threading
import time
import numpy as np
import cv2
import logging
import pyautogui
from PIL import ImageGrab
from core import state

# FAILSAFE ACTIVE TO PREVENT GETTING STUCK
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.0


class ImageDetector:
    def __init__(self):
        self.running = False
        # Tekli şablon (eski uyumluluk)
        self.template      = None
        self.template_path = None
        # Çoklu şablon listesi: [{"template": nparray, "path": str, "confidence": float, "label": str}, ...]
        self.templates     = []
        self.confidence    = 0.8
        self.scan_interval = 0.5
        self.step_interval = 0
        self.click_button  = "left"
        self.area          = None
        self.on_found      = None
        self.on_area_highlight = None
        self._thread       = None

    # ── Tekli yükleme (eski API) ─────────────────────────────────

    def load_template(self, path):
        try:
            with open(path, "rb") as f:
                data = np.frombuffer(f.read(), dtype=np.uint8)
            img = cv2.imdecode(data, cv2.IMREAD_COLOR)
            if img is None:
                return False
            self.template      = img
            self.template_path = path
            
            return True
        except Exception as e:
            print(f"[ImageDetector] load_template error: {e}")
            return False

    def load_from_array(self, img_array):
        try:
            arr = np.array(img_array)
            if arr.ndim == 2:
                img = cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
            elif arr.shape[2] == 4:
                img = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
            else:
                img = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            self.template      = img
            self.template_path = "clipboard"
            
            return True
        except Exception as e:
            print(f"[ImageDetector] load_from_array error: {e}")
            return False

    # ── Çoklu şablon yönetimi ─────────────────────────────────────

    def load_templates_from_list(self, items):
        """
        items: [{"path": str|None, "array": ndarray|None,
                 "confidence": float, "label": str}, ...]
        Başarıyla yüklenen şablon sayısını döndürür.
        """
        self.templates = []
        loaded = 0
        for item in items:
            try:
                path  = item.get("path")
                arr   = item.get("array")
                conf  = item.get("confidence", 0.8)
                label = item.get("label", "")
                img   = None

                if arr is not None:
                    a = np.array(arr)
                    if a.ndim == 2:
                        img = cv2.cvtColor(a, cv2.COLOR_GRAY2BGR)
                    elif a.shape[2] == 4:
                        img = cv2.cvtColor(a, cv2.COLOR_RGBA2BGR)
                    else:
                        img = cv2.cvtColor(a, cv2.COLOR_RGB2BGR)
                elif path:
                    with open(path, "rb") as f:
                        data = np.frombuffer(f.read(), dtype=np.uint8)
                    img = cv2.imdecode(data, cv2.IMREAD_COLOR)

                if img is not None:
                    self.templates.append({
                        "template":   img,
                        "path":       path,
                        "confidence": conf,
                        "label":      label,
                    })
                    loaded += 1
                    
            except Exception as e:
                print(f"[ImageDetector] load_templates_from_list item error: {e}")
        # Geriye uyumluluk: ilk şablonu tekli olarak da ayarla
        if self.templates:
            self.template      = self.templates[0]["template"]
            self.template_path = self.templates[0]["path"]
        return loaded

    # ── Başlatma / Durdurma ───────────────────────────────────────

    def start(self, confidence, scan_interval, click_button,
              on_found, area=None, on_area_highlight=None, step_interval=0,
              on_scan=None):
        # Çoklu liste boşsa tekli template'den liste oluştur
        if not self.templates and self.template is not None:
            self.templates = [{
                "template":   self.template,
                "path":       self.template_path,
                "confidence": confidence,
                "label":      (self.template_path or "clipboard"),
            }]
        if self.running or not self.templates:
            return False

        self.confidence    = confidence
        self.scan_interval = scan_interval
        self.step_interval = step_interval
        self.click_button  = click_button
        self.area          = area
        self.on_found      = on_found
        self.on_scan       = on_scan
        self.on_area_highlight = on_area_highlight
        self.running       = True
        state.image_scanning = True
        if on_area_highlight and area:
            on_area_highlight(area, True)
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        return True

    def stop(self):
        self.running = False
        state.image_scanning = False
        if self.on_area_highlight and self.area:
            self.on_area_highlight(self.area, False)

    # ── Ana döngü ─────────────────────────────────────────────────

    def _loop(self):
        scan_count = 0
        while self.running:
            try:
                scan_count += 1
                if self.on_scan:
                    self.on_scan(scan_count)
                result = self._scan()
                if result and self.running:
                    x, y, matched_label = result
                    pyautogui.click(x, y, button=self.click_button)
                    _cnt = state.increment_click()
                    if self.on_found:
                        self.on_found(x, y, _cnt, matched_label)
                    si = self.step_interval or 0
                    if si > 0:
                        end = time.time() + si
                        while self.running and time.time() < end:
                            time.sleep(min(0.02, end - time.time()))
            except Exception as e:
                logging.error(f"[ImageDetector] loop error: {e}")
            end = time.time() + max(0.01, self.scan_interval)
            if self.scan_interval > 0 and self.running:
                state.stop_event.wait(timeout=max(0.01, end - time.time()))

    # ── Ekran yakalama ────────────────────────────────────────────

    def _grab_screen(self):
        try:
            if self.area:
                x1, y1, x2, y2 = self.area
                if x2 - x1 <= 0 or y2 - y1 <= 0:
                    return None, 0, 0
                img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                screen = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)
                return screen, x1, y1
            else:
                img = ImageGrab.grab()
                screen = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)
                return screen, 0, 0
        except Exception as e:
            print(f"[ImageDetector] grab error: {e}")
            return None, 0, 0

    # ── Tarama ────────────────────────────────────────────────────

    def _scan(self):
        """Tüm şablonları sırayla tara, multi-scale eşleştirme ile ilk iyi eşleşeni döndür."""
        if not self.templates:
            return None
        try:
            screen, offset_x, offset_y = self._grab_screen()
            if screen is None:
                return None
            sh, sw = screen.shape[:2]

            for item in self.templates:
                tmpl  = item["template"]
                conf  = item["confidence"]
                label = item.get("label", "")
                
                # Multi-scale matching
                scales = [1.0, 0.8, 1.2]
                best_val = -1
                best_loc = None
                best_tw = 0
                best_th = 0

                for scale in scales:
                    if scale != 1.0:
                        scaled_w = int(tmpl.shape[1] * scale)
                        scaled_h = int(tmpl.shape[0] * scale)
                        if scaled_w <= 0 or scaled_h <= 0: continue
                        scaled_tmpl = cv2.resize(tmpl, (scaled_w, scaled_h))
                    else:
                        scaled_tmpl = tmpl
                        
                    th, tw = scaled_tmpl.shape[:2]

                    if th > sh or tw > sw:
                        continue

                    result = cv2.matchTemplate(screen, scaled_tmpl, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, max_loc = cv2.minMaxLoc(result)
                    
                    if max_val > best_val:
                        best_val = max_val
                        best_loc = max_loc
                        best_tw = tw
                        best_th = th

                if best_val >= conf:
                    cx = best_loc[0] + best_tw // 2 + offset_x
                    cy = best_loc[1] + best_th // 2 + offset_y
                    return cx, cy, label

        except Exception as e:
            logging.error(f"[ImageDetector] scan error: {e}")
        return None
