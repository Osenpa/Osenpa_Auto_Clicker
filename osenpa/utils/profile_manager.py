"""
Profile Manager — AutoClicker Pro
JSON tabanlı profil kayıt/yükleme sistemi.
Profiller: %APPDATA%/AutoClickerPro/profiles/ klasörüne kaydedilir.
"""
import os
import json
import time
from pathlib import Path


def _profiles_dir() -> Path:
    base = Path(os.environ.get("APPDATA", Path.home())) / "AutoClickerPro" / "profiles"
    base.mkdir(parents=True, exist_ok=True)
    return base


def list_profiles() -> list[dict]:
    """Kayıtlı tüm profilleri döndürür: [{name, path, created, modified}]"""
    result = []
    for p in sorted(_profiles_dir().glob("*.json")):
        try:
            stat = p.stat()
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
            result.append({
                "name":     data.get("name", p.stem),
                "path":     str(p),
                "created":  data.get("created", stat.st_ctime),
                "modified": stat.st_mtime,
                "tab":      data.get("tab", "keyboard"),
            })
        except Exception:
            pass
    return result


def save_profile(name: str, data: dict) -> str:
    """Profili kaydeder. Dosya yolunu döndürür."""
    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in name).strip()
    if not safe:
        safe = "profile"
    path = _profiles_dir() / f"{safe}.json"
    payload = {
        "name":    name,
        "created": data.get("created", time.time()),
        "saved":   time.time(),
        **data,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return str(path)


def load_profile(path: str) -> dict | None:
    """JSON dosyasından profil yükler. Başarısız olursa None döndürür ve kullanıcıya bildirir."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError(f"Expected dict, got {type(data).__name__}")
        return data
    except json.JSONDecodeError as e:
        import tkinter.messagebox as _mb
        _mb.showerror("Profile Load Failed", f"Invalid JSON in profile file:\n{e}")
        return None
    except Exception as e:
        import tkinter.messagebox as _mb
        _mb.showerror("Profile Load Failed", f"Could not load profile:\n{e}")
        return None


def delete_profile(path: str) -> bool:
    """Profil dosyasını siler."""
    try:
        os.remove(path)
        return True
    except Exception:
        return False


def rename_profile(path: str, new_name: str) -> str:
    """Profili yeniden adlandırır. Yeni dosya yolunu döndürür."""
    data = load_profile(path)
    if not data:
        return path
    data["name"] = new_name
    new_path = save_profile(new_name, data)
    if new_path != path:
        try:
            os.remove(path)
        except Exception:
            pass
    return new_path
