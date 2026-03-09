"""
file_manager.py — Adım dışa/içe aktarma işlemleri.

Desteklenen formatlar:
  Export: JSON, CSV, TXT (okunabilir)
  Import: JSON

Hata durumunda sessiz kalmak yerine kullanıcıya messagebox ile bilgi verir.
"""

import json
import csv
import io
from tkinter import filedialog, messagebox


# ── Ortak yardımcı ────────────────────────────────────────────────────────────

def _fmt_seconds(s):
    ms = int(round(s * 1000))
    if ms < 1000:  return f"{ms}ms"
    if s < 60:     return f"{s:.1f}s"
    return f"{s/60:.1f}min"


def _step_summary(i, step) -> str:
    """Tek adımı okunabilir metne çevirir (TXT/CSV için)."""
    t = step.get("type", "?")
    num = f"{i+1:02d}"
    note = step.get("note", "").strip()

    if t == "key":
        s = f"KEY  [{step.get('key','').upper()}]  ×{step.get('repeat',1)}  delay={_fmt_seconds(step.get('interval',0.1))}"
    elif t == "hotkey":
        s = f"HOTKEY  [{step.get('keys','').upper()}]  ×{step.get('repeat',1)}  delay={_fmt_seconds(step.get('interval',0.1))}"
    elif t == "click":
        pos = "CURSOR" if step.get("use_cursor") else f"X={step.get('x',0)} Y={step.get('y',0)}"
        s = f"CLICK  {pos}  {step.get('button','left').upper()}  ×{step.get('repeat',1)}  delay={_fmt_seconds(step.get('interval',0.1))}"
    elif t == "color":
        rgb = step.get("rgb", [0,0,0])
        tol = step.get("timeout", 0)
        s = f"COLOR SCAN  RGB({rgb[0]},{rgb[1]},{rgb[2]})  timeout={'∞' if not tol else f'{tol}s'}"
    elif t == "image":
        p = step.get("image_path") or "CLIPBOARD"
        import os; name = os.path.basename(p)
        tol = step.get("timeout", 0)
        s = f"IMAGE SCAN  [{name}]  timeout={'∞' if not tol else f'{tol}s'}"
    elif t == "delay":
        lbl = step.get("label","").strip()
        s = f"DELAY  {_fmt_seconds(step.get('duration',1.0))}" + (f"  ({lbl})" if lbl else "")
    elif t == "if_color":
        rgb = step.get("rgb",[0,0,0])
        then = step.get("then_action",{}).get("type","none").upper()
        else_ = step.get("else_action",{}).get("type","none").upper()
        s = f"IF COLOR  RGB({rgb[0]},{rgb[1]},{rgb[2]})  → THEN:{then} / ELSE:{else_}"
    elif t == "if_image":
        imgs = step.get("image_list",[])
        n = len(imgs) if imgs else 1
        then = step.get("then_action",{}).get("type","none").upper()
        else_ = step.get("else_action",{}).get("type","none").upper()
        s = f"IF IMAGE  ({n} img)  → THEN:{then} / ELSE:{else_}"
    elif t == "drag":
        s = f"DRAG  from({step.get('x',0)},{step.get('y',0)}) to({step.get('dx',0)},{step.get('dy',0)})"
    else:
        s = t.upper()

    note_part = f"  # {note}" if note else ""
    return f"{num}. {s}{note_part}"


# ── JSON ──────────────────────────────────────────────────────────────────────

def export_steps(steps):
    path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[
            ("Osenpa Steps (*.json)", "*.json")
        ],
        title="Export Steps"
    )
    if not path:
        return False

    ext = path.lower().rsplit(".", 1)[-1]
    try:
        if ext == "csv":
            _export_csv(steps, path)
        elif ext == "txt":
            _export_txt(steps, path)
        else:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(steps, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        messagebox.showerror("Export Failed", f"Could not save steps:\n{e}")
        return False


def _export_csv(steps, path):
    """Adımları CSV formatında kaydeder."""
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["#", "Type", "Summary", "Repeat", "Interval", "Note"])
        for i, step in enumerate(steps):
            t = step.get("type","?")
            summary = _step_summary(i, step)
            repeat  = step.get("repeat", 1)
            interval = _fmt_seconds(step.get("interval", 0.1))
            note    = step.get("note","")
            writer.writerow([i+1, t.upper(), summary, repeat, interval, note])


def _export_txt(steps, path):
    """Adımları okunabilir metin formatında kaydeder."""
    lines = [
        "Osenpa Auto Clicker — Steps Export",
        "=" * 48,
        f"Total steps: {len(steps)}",
        "",
    ]
    for i, step in enumerate(steps):
        lines.append(_step_summary(i, step))
    lines.append("")
    lines.append("=" * 48)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ── Import ────────────────────────────────────────────────────────────────────

def import_steps():
    path = filedialog.askopenfilename(
        filetypes=[("Osenpa Steps (*.json)", "*.json")],
        title="Import Steps"
    )
    if not path:
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            messagebox.showerror(
                "Import Failed",
                "Invalid file format: expected a list of steps.\n"
                "Please select a valid Osenpa Auto Clicker steps file."
            )
            return None
        return data
    except json.JSONDecodeError as e:
        messagebox.showerror("Import Failed", f"File contains invalid JSON:\n{e}")
        return None
    except Exception as e:
        messagebox.showerror("Import Failed", f"Could not read file:\n{e}")
        return None
