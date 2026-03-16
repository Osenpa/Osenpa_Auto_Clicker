"""
state.py — Osenpa Auto Clicker merkezi durum yönetimi.

Tüm paylaşılan durum alanları thread-safe bir AppState nesnesi üzerinden
erişilir. Birden fazla thread (automation, color_detector, image_detector)
aynı alanları okuyup yazdığı için Lock ile koruma zorunludur.

Geriye dönük uyumluluk: mevcut kod `state.running` gibi erişimleri
değiştirmeden kullanmaya devam edebilir.
"""

import threading

_lock = threading.Lock()


class _AppState:
    """Thread-safe uygulama durumu."""

    def __init__(self):
        self._lock = _lock

        self.stop_event = threading.Event()
        self.stop_event.set() # default to stopped

        # Adım listesi — sadece ana thread değiştirir, lock gerekmez
        self.steps: list = []

        # Hotkey'ler
        self._hotkey            = "f7"
        self._macro_hotkey      = "f8"
        self._color_hotkey      = "f9"
        self._image_hotkey      = "f10"
        self._kb_hotkey         = "f5"
        self._kb_key_hotkey     = "f11"  # f11: avoids alt+f4 conflict
        self._kb_combo_hotkey   = "f3"
        self._mouse_hotkey      = "f6"

        # Hotkey değiştirme bayrakları
        self._changing_hotkey           = False
        self._changing_macro_hotkey     = False
        self._changing_color_hotkey     = False
        self._changing_image_hotkey     = False
        self._changing_kb_hotkey        = False
        self._changing_kb_key_hotkey    = False
        self._changing_kb_combo_hotkey  = False
        self._changing_mouse_hotkey     = False

        # Çalışma durumları
        self._running           = False
        self._macro_recording   = False
        self._color_scanning    = False
        self._image_scanning    = False
        self._kb_running        = False
        self._kb_key_running    = False
        self._kb_combo_running  = False
        self._mouse_running     = False

        # Sayaçlar
        self._action_count = 0
        self._click_count  = 0

        # Gelişmiş Özellikler
        self._humanize = False
        self._total_lifetime_clicks = 0

    # Hotkey property'leri
    @property
    def hotkey(self):
        with self._lock: return self._hotkey
    @hotkey.setter
    def hotkey(self, v):
        with self._lock: self._hotkey = v

    @property
    def macro_hotkey(self):
        with self._lock: return self._macro_hotkey
    @macro_hotkey.setter
    def macro_hotkey(self, v):
        with self._lock: self._macro_hotkey = v

    @property
    def color_hotkey(self):
        with self._lock: return self._color_hotkey
    @color_hotkey.setter
    def color_hotkey(self, v):
        with self._lock: self._color_hotkey = v

    @property
    def image_hotkey(self):
        with self._lock: return self._image_hotkey
    @image_hotkey.setter
    def image_hotkey(self, v):
        with self._lock: self._image_hotkey = v

    @property
    def kb_hotkey(self):
        with self._lock: return self._kb_hotkey
    @kb_hotkey.setter
    def kb_hotkey(self, v):
        with self._lock: self._kb_hotkey = v

    @property
    def kb_key_hotkey(self):
        with self._lock: return self._kb_key_hotkey
    @kb_key_hotkey.setter
    def kb_key_hotkey(self, v):
        with self._lock: self._kb_key_hotkey = v

    @property
    def kb_combo_hotkey(self):
        with self._lock: return self._kb_combo_hotkey
    @kb_combo_hotkey.setter
    def kb_combo_hotkey(self, v):
        with self._lock: self._kb_combo_hotkey = v

    @property
    def mouse_hotkey(self):
        with self._lock: return self._mouse_hotkey
    @mouse_hotkey.setter
    def mouse_hotkey(self, v):
        with self._lock: self._mouse_hotkey = v

    # Changing bayrakları
    @property
    def changing_hotkey(self):
        with self._lock: return self._changing_hotkey
    @changing_hotkey.setter
    def changing_hotkey(self, v):
        with self._lock: self._changing_hotkey = v

    @property
    def changing_macro_hotkey(self):
        with self._lock: return self._changing_macro_hotkey
    @changing_macro_hotkey.setter
    def changing_macro_hotkey(self, v):
        with self._lock: self._changing_macro_hotkey = v

    @property
    def changing_color_hotkey(self):
        with self._lock: return self._changing_color_hotkey
    @changing_color_hotkey.setter
    def changing_color_hotkey(self, v):
        with self._lock: self._changing_color_hotkey = v

    @property
    def changing_image_hotkey(self):
        with self._lock: return self._changing_image_hotkey
    @changing_image_hotkey.setter
    def changing_image_hotkey(self, v):
        with self._lock: self._changing_image_hotkey = v

    @property
    def changing_kb_hotkey(self):
        with self._lock: return self._changing_kb_hotkey
    @changing_kb_hotkey.setter
    def changing_kb_hotkey(self, v):
        with self._lock: self._changing_kb_hotkey = v

    @property
    def changing_kb_key_hotkey(self):
        with self._lock: return self._changing_kb_key_hotkey
    @changing_kb_key_hotkey.setter
    def changing_kb_key_hotkey(self, v):
        with self._lock: self._changing_kb_key_hotkey = v

    @property
    def changing_kb_combo_hotkey(self):
        with self._lock: return self._changing_kb_combo_hotkey
    @changing_kb_combo_hotkey.setter
    def changing_kb_combo_hotkey(self, v):
        with self._lock: self._changing_kb_combo_hotkey = v

    @property
    def changing_mouse_hotkey(self):
        with self._lock: return self._changing_mouse_hotkey
    @changing_mouse_hotkey.setter
    def changing_mouse_hotkey(self, v):
        with self._lock: self._changing_mouse_hotkey = v

    # Çalışma durumları
    @property
    def running(self):
        with self._lock: return self._running
    @running.setter
    def running(self, v):
        with self._lock:
            self._running = v
            if v:
                self.stop_event.clear()
            else:
                self.stop_event.set()

    @property
    def macro_recording(self):
        with self._lock: return self._macro_recording
    @macro_recording.setter
    def macro_recording(self, v):
        with self._lock: self._macro_recording = v

    @property
    def color_scanning(self):
        with self._lock: return self._color_scanning
    @color_scanning.setter
    def color_scanning(self, v):
        with self._lock: self._color_scanning = v

    @property
    def image_scanning(self):
        with self._lock: return self._image_scanning
    @image_scanning.setter
    def image_scanning(self, v):
        with self._lock: self._image_scanning = v

    @property
    def kb_running(self):
        with self._lock: return self._kb_running
    @kb_running.setter
    def kb_running(self, v):
        with self._lock: self._kb_running = v

    @property
    def kb_key_running(self):
        with self._lock: return self._kb_key_running
    @kb_key_running.setter
    def kb_key_running(self, v):
        with self._lock: self._kb_key_running = v

    @property
    def kb_combo_running(self):
        with self._lock: return self._kb_combo_running
    @kb_combo_running.setter
    def kb_combo_running(self, v):
        with self._lock: self._kb_combo_running = v

    @property
    def mouse_running(self):
        with self._lock: return self._mouse_running
    @mouse_running.setter
    def mouse_running(self, v):
        with self._lock: self._mouse_running = v

    # Sayaçlar
    @property
    def action_count(self):
        with self._lock: return self._action_count
    @action_count.setter
    def action_count(self, v):
        with self._lock: self._action_count = v

    @property
    def click_count(self):
        with self._lock: return self._click_count
    @click_count.setter
    def click_count(self, v):
        with self._lock: self._click_count = v

    def increment_action(self) -> int:
        """action_count ve click_count'u atomik olarak artırır, yeni değeri döndürür."""
        with self._lock:
            self._action_count += 1
            self._click_count = self._action_count
            self._total_lifetime_clicks += 1
            return self._action_count

    def increment_click(self) -> int:
        """Yalnızca click_count'u atomik olarak artırır (color/image detector için).
        Yeni click_count değerini döndürür."""
        with self._lock:
            self._click_count += 1
            self._total_lifetime_clicks += 1
            return self._click_count

    def reset_counts(self):
        """Sayaçları sıfırlar."""
        with self._lock:
            self._action_count = 0
            self._click_count  = 0

    @property
    def humanize(self):
        with self._lock: return self._humanize
    @humanize.setter
    def humanize(self, v):
        with self._lock: self._humanize = v

    @property
    def total_lifetime_clicks(self):
        with self._lock: return self._total_lifetime_clicks
    @total_lifetime_clicks.setter
    def total_lifetime_clicks(self, v):
        with self._lock: self._total_lifetime_clicks = v


# Modül seviyesinde tekil nesne
_app_state = _AppState()

# steps listesini doğrudan modül üzerinden erişilebilir kıl
steps = _app_state.steps

# Proxy: `state.running` gibi erişimler _app_state üzerinden çalışır
import sys as _sys

class _StateModule(_sys.modules[__name__].__class__):
    def __getattr__(self, name):
        return getattr(_app_state, name)

    def __setattr__(self, name, value):
        if name.startswith("_") or name in ("steps",):
            super().__setattr__(name, value)
        else:
            try:
                setattr(_app_state, name, value)
            except AttributeError:
                super().__setattr__(name, value)

_sys.modules[__name__].__class__ = _StateModule
