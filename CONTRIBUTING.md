# Contributing to Osenpa Auto Clicker

Thank you for considering contributing! Here's how you can help.

## Table of Contents

- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)
- [Submitting Code](#submitting-code)
- [Project Structure](#project-structure)
- [Code Style](#code-style)
- [Commit Message Conventions](#commit-message-conventions)
- [Localization (Adding a Language)](#localization-adding-a-language)
- [License](#license)

---

## Reporting Bugs

- Use the [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md) issue template.
- Include your Python version, OS, and exact steps to reproduce.
- Attach any error output or log messages.
- Check existing issues first to avoid duplicates.

## Suggesting Features

- Open an issue using the [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md) template.
- Describe the use case and expected behavior.
- Check existing open issues and the [CHANGELOG](CHANGELOG.md) before posting.

---

## Submitting Code

1. **Fork** the repository and create a new branch from `main`:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. Make your changes, keeping the existing code style (see below).

4. **Test** your changes by running the application:

   ```bash
   python osenpa/main.py
   ```

5. **Commit** with a clear message following the [conventions](#commit-message-conventions) below.

6. **Open a Pull Request** against `main` using the provided PR template.

---

## Project Structure

```
Osenpa_Auto_Clicker/
├── osenpa/
│   ├── main.py               # Application entry point
│   ├── core/
│   │   ├── automation.py     # Step execution engine
│   │   ├── color_detector.py # Color scanning thread
│   │   ├── hotkey_listener.py# Global keyboard listener
│   │   ├── image_detector.py # Image template matching thread
│   │   ├── macro_recorder.py # Mouse/keyboard event recorder
│   │   └── state.py          # Thread-safe shared application state
│   ├── ui/
│   │   ├── main_window.py    # Top-level window and panel wiring
│   │   ├── sidebar.py        # Navigation sidebar
│   │   ├── footer.py         # Run/Stop bar, loop & interval controls
│   │   ├── steps_panel.py    # Step list view with undo/redo
│   │   ├── keyboard_panel.py # Keyboard automation panel
│   │   ├── mouse_panel.py    # Mouse automation panel
│   │   ├── color_panel.py    # Color detection panel
│   │   ├── image_panel.py    # Image detection panel
│   │   ├── macro_panel.py    # Macro recorder panel
│   │   ├── profiles_panel.py # Profile save/load panel
│   │   ├── settings_panel.py # Settings (hotkeys, theme, language)
│   │   ├── step_edit_dialog.py # Step editor dialog
│   │   ├── overlay_indicator.py# Floating status overlay
│   │   ├── theme.py          # Color tokens and widget factories
│   │   └── interval_widget.py# Reusable interval input widget
│   ├── utils/
│   │   ├── autosave.py       # Session auto-save / restore
│   │   ├── file_manager.py   # JSON/CSV/TXT step export & import
│   │   ├── i18n.py           # Internationalization (tr() function)
│   │   ├── profile_manager.py# Named profile save/load/delete
│   │   └── tooltip.py        # Hover tooltip helper
│   └── locales/              # Translation files (e.g. en.json, tr.json)
├── build.py                  # PyInstaller build script
├── requirements.txt
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

---

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code.
- Keep UI code in `osenpa/ui/`, core logic in `osenpa/core/`, and helpers in `osenpa/utils/`.
- Thread-safe state goes through `core/state.py` — do not access `_AppState` internals directly.
- Use `tr("KEY")` from `utils/i18n.py` for all user-visible strings so they can be translated.
- Add error handling (`try/except`) around any I/O, screenshot, or OS API calls.

---

## Commit Message Conventions

Use a short, imperative prefix to keep the history readable:

| Prefix | When to use |
|--------|-------------|
| `feat:` | A new user-visible feature |
| `fix:` | A bug fix |
| `docs:` | Documentation-only change |
| `refactor:` | Code restructure without behavior change |
| `style:` | Formatting, whitespace, no logic change |
| `chore:` | Build scripts, CI, dependencies |
| `i18n:` | Translation / localization files |

**Example:** `feat: add scroll step support to step editor`

---

## Localization (Adding a Language)

1. Copy an existing locale file, e.g.:

   ```bash
   cp osenpa/locales/en.json osenpa/locales/xx.json
   ```

2. Translate all string values (keep the **keys** unchanged).

3. Register the language in `osenpa/utils/i18n.py` by adding it to the `LANGUAGES` dict:

   ```python
   LANGUAGES = {
       ...
       "xx": "Your Language Name",
   }
   ```

4. Test by switching to the new language in **Settings → Language**.

---

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
