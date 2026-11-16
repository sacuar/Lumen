# Lumen development roadmap

Lumen aims to be a lightweight, keyboard-first text editor inspired by Sublime Text. This is a **planning document**, not a list of features that already work.

## Priority 1 — reliable everyday editing

- [ ] Confirm document switching, dirty-file prompts and save-as behaviour.
- [ ] Regression tests for opening files, UTF-8 save/load and find/replace.
- [ ] Fix menu/shortcut conflicts and test a full Windows launch.
- [ ] Improve performance and responsiveness on large files.

## Priority 2 — smooth desktop experience

- [ ] Reproducible Windows package with clean startup and error reporting.
- [ ] High-DPI visual testing, theme consistency and keyboard accessibility.
- [ ] Project-wide search and navigation improvements.
- [ ] Better file-tree behaviour and saved workspace restoration.

## Priority 3 — extensibility

- [ ] Document which `sublime` and `sublime_plugin` APIs are implemented.
- [ ] Add isolated smoke tests for supported plugin commands.
- [ ] Safer, more predictable plugin error handling.
- [ ] More syntax tests and language coverage.

## Contributors wanted

Pick an item and [propose a focused issue](https://github.com/sacuar/Lumen/issues). A reproducible bug report or test is just as useful as a feature implementation. See [CONTRIBUTING.md](CONTRIBUTING.md).

Existing Windows release: [Lumen_V1.1.exe](https://github.com/sacuar/Lumen/releases/tag/smart_text_editor). That EXE has **not** been validated as part of the documentation cleanup.
