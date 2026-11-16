# Contributing to Lumen

Lumen is an early-stage text editor. Developers, designers, documentation writers and testers are welcome.

## Before contributing

- Read the [README](README.md), [roadmap](ROADMAP.md), and [open issues](https://github.com/sacuar/Lumen/issues).
- Please **discuss non-trivial changes in an issue** first. Work in small pull requests; keep the working editor intact.
- **Licensing needs clarification:** the existing `LICENSE` file is empty and the older README files described different licences. Request the maintainer's guidance before submitting original code. No licence terms are implied here.
- Python plugins and build commands execute code locally. Only install plugins you trust.

## Development setup

```bash
git clone https://github.com/sacuar/Lumen.git
cd Lumen
python -m lumen
```

The editor should be available at `http://127.0.0.1:8765`. For a desktop window, install `pywebview` and run `python lumen_win.py`. This is the existing project structure; Windows is the primary packaged target.

## Good first contributions

1. **Editor reliability:** tab switching, unsaved file warnings, undo/redo and find/replace edge cases (`ui/`).
2. **Keyboard/accessibility:** improve focus, contrast, shortcuts and menu behaviour (`ui/style.css`, `ui/app.js`).
3. **Tests:** create repeatable checks for file I/O, syntax highlighting and keymaps.
4. **Documentation:** verified screenshots and accurate installation instructions.

More challenging work: performance on large files, Windows installer packaging, richer project search and experimental Sublime-style plugin API compatibility.

## Pull request expectations

- Link an issue and describe the specific change.
- List Windows/macOS/Linux, Python version, and browser or `pywebview` host used to test.
- Include reproduction steps and screenshots for UI fixes.
- Do not commit build products, personal files, private API keys or machine-specific paths.
- Never claim complete Sublime Text compatibility unless tests support it.

Thank you for helping build Lumen.
