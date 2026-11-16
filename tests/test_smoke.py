"""Dependency-light checks for Lumen's core editor metadata."""
from pathlib import Path
import unittest

from lumen import syntax, keymaps

ROOT = Path(__file__).resolve().parents[1]


class SyntaxSmokeTests(unittest.TestCase):
    def test_extension_detection(self):
        for filename, expected in (
            ("main.py", "Python"),
            ("script.JS", "JavaScript"),
            ("index.html", "HTML"),
            ("styles.css", "CSS"),
            ("data.json", "JSON"),
            ("README.md", "Markdown"),
            ("unknown.xyz", "Plain"),
        ):
            with self.subTest(filename=filename):
                self.assertEqual(syntax.guess(filename), expected)

    def test_empty_and_plain_have_no_highlight_spans(self):
        self.assertEqual(syntax.guess(""), "Plain")
        self.assertEqual(syntax.tokenize("hello", "Plain"), [])

    def test_highlighting_spans_are_in_bounds(self):
        data = "def greet(name):\n    return name\n"
        spans = syntax.tokenize(data, "Python")
        self.assertTrue(spans)
        for start, end, kind in spans:
            self.assertGreaterEqual(start, 0)
            self.assertLess(start, end)
            self.assertLessEqual(end, len(data))
            self.assertTrue(kind)

    def test_keymaps_include_essential_editor_commands(self):
        commands = {item["command"] for item in keymaps.KEYMAPS}
        for cmd in ("open_file", "save", "find", "replace", "command_palette"):
            self.assertIn(cmd, commands)


class UiSmokeTests(unittest.TestCase):
    def test_frontend_files_referenced_in_index_exist(self):
        page = (ROOT / "ui" / "index.html").read_text(encoding="utf-8")
        for filename in ("api.js", "editor.js", "menus.js", "palette.js", "find.js",
                         "sidebar.js", "console.js", "app.js", "style.css"):
            self.assertTrue((ROOT / "ui" / filename).is_file(), filename)
            self.assertIn(filename, page)


if __name__ == "__main__":
    unittest.main()
