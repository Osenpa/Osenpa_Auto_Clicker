import os
import json
import sys

def _get_base_path():
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # In our build.py, locales are added to "osenpa/locales"
        return os.path.join(sys._MEIPASS, "osenpa")
    except Exception:
        return os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))

# Better to save language.json in standard AppData or user profile folder
# so we avoid permission issues that happen if we try to write to cwd of the .exe
_appdata = os.path.join(os.path.expanduser("~"), ".osenpa")
if not os.path.exists(_appdata):
    try:
        os.makedirs(_appdata)
    except Exception:
        pass
_SETTINGS_FILE = os.path.join(_appdata, "language.json")

# Locales are static assets bundled with the app
_LOCALES_DIR = os.path.join(_get_base_path(), "locales")


LANGUAGES = {
    "en": "English",
    "de": "Deutsch",
    "id": "Bahasa Indonesia",
    "ru": "Русский",
    "ja": "日本語",
    "ko": "한국어",
    "fr": "Français",
    "ar": "العربية",
    "es": "Español",
    "pt": "Português",
    "zh": "中文",
    "tr": "Türkçe"
}

_current_language = "en"
_translations = {}

def _load_translations(lang: str):
    global _translations
    file_path = os.path.join(_LOCALES_DIR, f"{lang}.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                _translations = json.load(f)
        except Exception as e:
            print(f"Error loading translation for {lang}: {e}")
            _translations = {}
    else:
        _translations = {}

def load_language():
    """Initializes the language based on saved settings."""
    global _current_language
    if os.path.exists(_SETTINGS_FILE):
        try:
            with open(_SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                saved_lang = data.get("language", "en")
                if saved_lang in LANGUAGES:
                    _current_language = saved_lang
        except Exception:
            pass
    _load_translations(_current_language)

def get_language() -> str:
    return _current_language

def set_language(lang_code: str):
    global _current_language
    if lang_code in LANGUAGES:
        _current_language = lang_code
        _load_translations(lang_code)
        try:
            with open(_SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump({"language": _current_language}, f)
        except Exception:
            pass
        # also notify state or just return
        return True
    return False

def tr(key: str) -> str:
    """Returns the translated string for the given key in the current language."""
    if not key:
        return ""
    return _translations.get(key, key)

# Load existing lang on import
load_language()
