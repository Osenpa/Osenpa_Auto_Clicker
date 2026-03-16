# Osenpa Auto Clicker

Osenpa Auto Clicker is a Windows auto clicker, macro recorder, and desktop automation tool built with Python and Tkinter. It provides configurable mouse and keyboard automation, profile management, image detection, color detection, and multi-language support in a packaged GUI application.

Website: [osenpa.com](https://osenpa.com)

## Highlights

- Adjustable click, delay, and hotkey automation flows
- Profile save/load support
- Macro recording support
- Image and color detection based triggers
- Multi-language interface
- Windows-ready packaged executable
- Packaged Windows executable included in [`dist/`](dist/)

## Keywords

Osenpa Auto Clicker, Windows auto clicker, macro recorder, image detection bot, color detection bot, desktop automation tool, Python auto clicker, Tkinter automation app.

## Project Status

This repository is prepared for public source release.

- Source code is included.
- License is MIT.
- The prebuilt Windows executable is kept in `dist/`.
- Generated Python cache files are excluded from version control.

## Requirements

- Windows 10 or Windows 11
- Python 3.14 or newer for running from source
- `pip` for dependency installation

## Quick Start

### Run from source

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python osenpa/main.py
```

### Run the packaged executable

Launch [`dist/OsenpaAutoClicker.exe`](dist/OsenpaAutoClicker.exe) on Windows.

## Build a New Executable

```bash
pip install -r requirements.txt
pip install pyinstaller
python build.py
```

The build script regenerates icon assets and creates a one-file Windows executable in `dist/`.

## Repository Layout

```text
osenpa/
  core/        Automation and detection logic
  ui/          Tkinter UI panels and shared theme code
  utils/       Persistence, localization, and helper utilities
dist/          Prebuilt Windows executable
build.py       PyInstaller build entry point
```

## Data Storage

The application stores user-generated runtime data outside the repository:

- Language settings: `%USERPROFILE%\.osenpa\language.json`
- Profiles: `%APPDATA%\AutoClickerPro\profiles\`

These paths should not be committed to the repository.

## Responsible Use

Use this software only in environments and applications where automation is allowed. You are responsible for complying with the terms of service, security rules, and local regulations that apply to your use case.

## Links

- Website: [osenpa.com](https://osenpa.com)
- Donate: [osenpa.com/donate](https://osenpa.com/donate)
- Source code: [Codeberg repository](https://codeberg.org/Osenpa/osenpa-auto-clicker)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution and pull request expectations.

## Security

See [SECURITY.md](SECURITY.md) for how to report vulnerabilities.

## Contact

- Website: [osenpa.com](https://osenpa.com)
- Email: `osenpacom@gmail.com`
- Donate: [osenpa.com/donate](https://osenpa.com/donate)
- Codeberg: [Osenpa Auto Clicker](https://codeberg.org/Osenpa/osenpa-auto-clicker)
