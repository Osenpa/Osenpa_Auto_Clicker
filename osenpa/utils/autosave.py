"""
autosave.py — Osenpa Auto Clicker otomatik kayıt / oturum geri yükleme.

Uygulama kapanırken mevcut adımları ve temel ayarları kaydeder.
Bir sonraki açılışta kaldığı yerden devam etmeyi sağlar.
"""

import json
import os
from pathlib import Path

_SESSION_DIR  = Path.home() / ".osenpa"
_SESSION_FILE = _SESSION_DIR / "last_session.json"

_VERSION = 1   # Format versiyonu — ileride migrasyon için


def _ensure_dir():
    _SESSION_DIR.mkdir(parents=True, exist_ok=True)


def save_session(steps: list, settings: dict | None = None) -> bool:
    """Mevcut adımları ve ayarları diske kaydeder. True = başarı."""
    try:
        _ensure_dir()
        payload = {
            "version":  _VERSION,
            "steps":    steps,
            "settings": settings or {},
        }
        tmp = _SESSION_FILE.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        # Atomik rename — yarım yazma dosyasını önle
        tmp.replace(_SESSION_FILE)
        return True
    except Exception as e:
        print(f"[AutoSave] save error: {e}")
        return False


def load_session() -> dict | None:
    """
    Son oturumu yükler.
    Döndürür: {"steps": [...], "settings": {...}} veya None.
    """
    if not _SESSION_FILE.exists():
        return None
    try:
        with open(_SESSION_FILE, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return None
        version = data.get("version", 0)
        if version != _VERSION:
            print(f"[AutoSave] version mismatch ({version} != {_VERSION}), skipping")
            return None
        steps = data.get("steps", [])
        if not isinstance(steps, list):
            steps = []
        return {"steps": steps, "settings": data.get("settings", {})}
    except Exception as e:
        print(f"[AutoSave] load error: {e}")
        return None


def has_session() -> bool:
    """Kayıtlı bir oturum var mı?"""
    return _SESSION_FILE.exists()


def clear_session():
    """Kayıtlı oturumu sil."""
    try:
        if _SESSION_FILE.exists():
            _SESSION_FILE.unlink()
    except Exception as e:
        print(f"[AutoSave] clear error: {e}")


def session_path() -> str:
    return str(_SESSION_FILE)
