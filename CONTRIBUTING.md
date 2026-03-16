# Contributing

## Scope

Contributions are welcome for bug fixes, UI improvements, localization updates, documentation, packaging, and test coverage.

## Before Opening a Pull Request

1. Keep changes focused and easy to review.
2. Do not commit generated cache files, local profiles, or machine-specific settings.
3. Update documentation when behavior or setup changes.
4. Verify the application still launches on Windows after your changes.

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python osenpa/main.py
```

## Build Check

If your change affects packaging, verify the executable still builds:

```bash
pip install pyinstaller
python build.py
```

## Pull Request Notes

- Describe the user-visible change clearly.
- Mention any dependency updates.
- Include screenshots when the UI changes.
- Keep unrelated cleanup out of the same pull request.
