# Changelog

All notable changes to Osenpa Auto Clicker will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Pull request template
- Improved README with full feature table, step types table, default hotkeys reference, and badges
- Expanded CONTRIBUTING guide with project structure map, commit conventions, and localization walkthrough
- Improved bug report and feature request issue templates

---

## [1.0.0] - 2026-03-09

### Added
- Initial public release
- Mouse click automation with configurable interval, button, and repeat count
- Keyboard step support (single key and hotkey combos)
- Color detection: click on screen when a specific color appears
- Image detection: click on screen when a template image is found
- Conditional steps: IF COLOR / IF IMAGE with THEN/ELSE branches
- Macro recorder: record mouse and keyboard actions and replay them as steps
- Profile save/load for all panel settings
- Dark and light mode UI theme
- Multi-language support (Arabic, German, English, Spanish, French, Indonesian, Japanese, Korean, Portuguese, Russian, Turkish, Chinese)
- Overlay indicator showing active automation task
- Auto-save and undo/redo for the step list
- Scheduler: run once at a specific time or repeatedly at a set interval
- Anti-bot jitter (Humanize mode) for randomized timing and coordinates
- `build.py` script for packaging to a Windows executable with PyInstaller

[Unreleased]: https://github.com/Osenpa/Osenpa_Auto_Clicker/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Osenpa/Osenpa_Auto_Clicker/releases/tag/v1.0.0
