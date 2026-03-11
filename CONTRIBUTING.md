# Contributing to Osenpa Auto Clicker

Thank you for considering contributing! Here's how you can help.

## Reporting Bugs

- Use the [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md) issue template.
- Include your Python version, OS, and steps to reproduce.

## Suggesting Features

- Open an issue with the title prefix `[Feature Request]`.
- Describe the use case and expected behavior.

## Submitting Code

1. Fork the repository and create a new branch from `main`:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Make your changes, keeping the existing code style.
4. Test your changes by running the application:

   ```bash
   python osenpa/main.py
   ```

5. Commit with a clear message and open a Pull Request against `main`.

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code.
- Keep UI-related code in `osenpa/ui/`, core logic in `osenpa/core/`, and helpers in `osenpa/utils/`.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
