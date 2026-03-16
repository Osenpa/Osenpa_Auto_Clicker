import os
import subprocess
from pathlib import Path

APP_NAME = "Osenpa Auto Clicker"
ROOT = Path(__file__).resolve().parent
ICON_PATH = ROOT / "osenpa" / "osenpa_release.ico"
EXE_ICON_PATH = ROOT / "osenpa" / "osenpa_exe.ico"
FALLBACK_PNG = ROOT / "osenpa" / "osenpa_icon_64.png"
MASTER_PNG = ROOT / "osenpa" / "icon_master.png"
ICON_SIZES = [16, 20, 24, 32, 40, 48, 64, 96, 128, 256]


def _add_data_arg(src: str, dst: str) -> str:
    sep = ";" if os.name == "nt" else ":"
    return f"{src}{sep}{dst}"


def ensure_multi_size_icon():
    source = MASTER_PNG if MASTER_PNG.exists() else (ICON_PATH if ICON_PATH.exists() else FALLBACK_PNG)
    if not source.exists():
        raise FileNotFoundError(
            f"Icon source not found. Looked for: {MASTER_PNG}, {ICON_PATH}, {FALLBACK_PNG}"
        )

    from PIL import Image

    with Image.open(source) as img:
        rgba = img.convert("RGBA")
        rgba.save(ICON_PATH, format="ICO", sizes=[(s, s) for s in ICON_SIZES])

    print(f"Generated multi-size icon: {ICON_PATH}")
    if source == MASTER_PNG:
        print("Source: osenpa/icon_master.png")
    elif source == ICON_PATH:
        print("Source: existing osenpa/osenpa_release.ico")
    else:
        print("Source: fallback osenpa/osenpa_icon_64.png")


def ensure_exe_icon_variant():
    # Explorer icon can be tuned independently from runtime window/taskbar icon.
    from PIL import Image, ImageFilter

    with Image.open(ICON_PATH) as img:
        base = img.convert("RGBA")

    w, h = base.size
    scale = 1.10  # slightly larger visual footprint for folder/exe listing icon
    sw, sh = int(w * scale), int(h * scale)

    scaled = base.resize((sw, sh), Image.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.paste(scaled, ((w - sw) // 2, (h - sh) // 2), scaled)

    # Light edge-thickening helps thin glyphs read better in Explorer small icons.
    alpha = canvas.split()[-1].filter(ImageFilter.MaxFilter(3))
    canvas.putalpha(alpha)

    canvas.save(EXE_ICON_PATH, format="ICO", sizes=[(s, s) for s in ICON_SIZES])
    print(f"Generated Explorer exe icon: {EXE_ICON_PATH}")


def build():
    print("Preparing icon assets...")
    ensure_multi_size_icon()
    ensure_exe_icon_variant()

    print("Building Osenpa Auto Clicker executable...")
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name",
        APP_NAME,
        "--icon",
        str(EXE_ICON_PATH),
        "--add-data",
        _add_data_arg("osenpa/language.json", "osenpa"),
        "--add-data",
        _add_data_arg("osenpa/locales", "osenpa/locales"),
        "--add-data",
        _add_data_arg("osenpa/osenpa_icon_64.png", "osenpa"),
        "--add-data",
        _add_data_arg("osenpa/osenpa_release.ico", "osenpa"),
        "--add-data",
        _add_data_arg("osenpa/ui/assets", "osenpa/ui/assets"),
        "--add-data",
        _add_data_arg("osenpa/ui/assets", "ui/assets"),
        "osenpa/main.py",
    ]
    subprocess.run(cmd, check=True)
    print("Build complete!")


if __name__ == "__main__":
    build()
