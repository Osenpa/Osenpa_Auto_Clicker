# Osenpa Auto Clicker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/Platform-Windows-blue.svg)](https://www.microsoft.com/windows)
[![Release](https://img.shields.io/github/v/release/Osenpa/Osenpa_Auto_Clicker)](https://github.com/Osenpa/Osenpa_Auto_Clicker/releases)

**Osenpa Auto Clicker** is a free, open-source, Python-based automation tool with a modern GUI. It combines a fully-featured auto clicker, macro recorder, image/color detection bot, keyboard automator, and scheduler — all in one application.

> **Platform:** Windows (primary). Linux/macOS may work with limited functionality.

---

## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Step Types](#step-types)
  - [Default Hotkeys](#default-hotkeys)
- [Build to Executable](#build-to-executable)
- [Contributing](#contributing)
- [Changelog](#changelog)
- [License](#license)
- [Contact](#contact)

---

## Features

| Category | Details |
|---|---|
| 🖱️ **Mouse Automation** | Auto-click at fixed coordinates or current cursor position; drag support; left, right, and middle buttons |
| ⌨️ **Keyboard Automation** | Single key presses, hotkey combos (e.g. `Ctrl+C`), configurable repeat and interval |
| 🔍 **Image Detection** | Click when a template image appears on screen; multi-image support; confidence threshold; scan area restriction |
| 🎨 **Color Detection** | Click when a target color (with tolerance) appears on screen; multi-color support; scan area restriction |
| 🔀 **Conditional Logic** | IF COLOR / IF IMAGE steps with THEN/ELSE branches — click, press a key, jump to step, or stop |
| 📋 **Step Builder** | Build, reorder, duplicate, and edit individual automation steps; unlimited steps per session |
| 🔁 **Loop Control** | Run steps a fixed number of times or infinitely; per-step repeat counts |
| ⏱️ **Scheduler** | Start automation once at a specific time of day, or repeatedly at a configurable interval |
| 🎙️ **Macro Recorder** | Record real mouse clicks, drags, scrolls, and keystrokes and replay them as steps |
| 💾 **Profiles** | Save and load named configuration profiles for each panel; instant profile switching |
| 🔄 **Auto-Save / Undo-Redo** | Session auto-saved on exit; full undo/redo history for the step list |
| 🎨 **Dark / Light Theme** | One-click theme toggle; persists between sessions |
| 🌐 **12 Languages** | Arabic, Chinese, German, English, Spanish, French, Indonesian, Japanese, Korean, Portuguese, Russian, Turkish |
| 🔑 **Custom Hotkeys** | Every panel has an independently configurable hotkey; duplicate-hotkey detection prevents conflicts |
| 🖼️ **Overlay Indicator** | Floating overlay shows the active task, action count, and scan count while automation runs |
| 🤖 **Anti-Bot Jitter** | Optional "Humanize" mode adds random micro-variations to coordinates and timings |

---

## Screenshots

> Screenshots and demo GIFs coming soon. Star the repo to stay notified of updates!

---

## Prerequisites

- **Python 3.8 or higher**
- **Windows** (primary platform; Linux/macOS may have limited support)
- The dependencies listed in `requirements.txt`

---

## Installation

1. **Clone or download** the repository:

   ```bash
   git clone https://github.com/Osenpa/Osenpa_Auto_Clicker.git
   cd Osenpa_Auto_Clicker
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**

   ```bash
   python osenpa/main.py
   ```

---

## Usage

### Quick Start

1. Open the application.
2. Choose a panel from the left sidebar (**Mouse**, **Keyboard**, **Color**, **Image**, **Macro**, etc.).
3. Configure your action(s) and click **Add Step** to add them to the step list on the right.
4. Press **RUN STEPS** in the footer (or use the hotkey `F7`) to start automation.
5. Press **STOP** or the hotkey again to stop.

### Step Types

| Step Type | Description |
|---|---|
| `click` | Click a fixed screen coordinate or the current cursor position |
| `key` | Press a single keyboard key (supports non-Latin characters) |
| `hotkey` | Press a key combination such as `Ctrl+C` or `Alt+F4` |
| `scroll` | Scroll the mouse wheel at a given position |
| `delay` | Wait for a specified duration before the next step |
| `color` | Scan the screen (or a region) and click when a target color is found |
| `image` | Scan the screen (or a region) and click when a template image is found |
| `if_color` | Conditional: evaluate a color scan, then run a THEN or ELSE action |
| `if_image` | Conditional: evaluate an image scan, then run a THEN or ELSE action |

### Default Hotkeys

| Action | Default Key |
|---|---|
| Run / Stop Steps | `F7` |
| Record Macro | `F8` |
| Color Detection | `F9` |
| Image Detection | `F10` |
| Keyboard — Single Key | `F11` |
| Keyboard — Combo | `F3` |
| Mouse Panel | `F6` |

> All hotkeys can be changed from **Settings → Hotkeys** or the individual panel's **CHANGE** button.

---

## Build to Executable

A `build.py` script is included for creating a standalone Windows `.exe` with [PyInstaller](https://pyinstaller.org/):

1. **Install PyInstaller:**

   ```bash
   pip install pyinstaller
   ```

2. **Run the build script:**

   ```bash
   python build.py
   ```

This produces `dist/Osenpa Auto Clicker.exe` with all required assets bundled — no Python installation needed on the target machine.

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request or opening an issue.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full version history.

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## Contact

- **Email:** osenpacom@gmail.com
- **GitHub:** [https://github.com/Osenpa](https://github.com/Osenpa)
- **Issues / Feature Requests:** [GitHub Issues](https://github.com/Osenpa/Osenpa_Auto_Clicker/issues)
