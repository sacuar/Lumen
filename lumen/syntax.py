"""Very small regex-based syntax definitions. Enough to colour real code."""
import os
import re

def _kw(words):
    return r"\b(?:" + "|".join(words) + r")\b"

PY = {
    "name": "Python",
    "extensions": [".py", ".pyw"],
    "rules": [
        (r"#[^\n]*", "comment"),
        (r'"""(?:.|\n)*?"""|\'\'\'(?:.|\n)*?\'\'\'', "string"),
        (r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', "string"),
        (_kw(["def","class","return","if","elif","else","for","while","in","not","and","or","is","import","from","as","with","try","except","finally","raise","yield","lambda","pass","break","continue","global","nonlocal","assert","del","await","async"]), "keyword"),
        (r"\b(True|False|None)\b", "constant"),
        (r"\b\d+(?:\.\d+)?\b", "number"),
        (r"\b[A-Za-z_]\w*(?=\s*\()", "function"),
    ],
}

JS = {
    "name": "JavaScript",
    "extensions": [".js", ".mjs", ".jsx", ".ts", ".tsx"],
    "rules": [
        (r"//[^\n]*|/\*(?:.|\n)*?\*/", "comment"),
        (r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`', "string"),
        (_kw(["function","return","if","else","for","while","do","switch","case","break","continue","var","let","const","new","class","extends","import","export","from","as","async","await","try","catch","finally","throw","typeof","instanceof","in","of","this","super","yield","delete","void"]), "keyword"),
        (r"\b(true|false|null|undefined|NaN)\b", "constant"),
        (r"\b\d+(?:\.\d+)?\b", "number"),
        (r"\b[A-Za-z_$]\w*(?=\s*\()", "function"),
    ],
}

HTML = {
    "name": "HTML",
    "extensions": [".html", ".htm", ".xhtml"],
    "rules": [
        (r"<!--(?:.|\n)*?-->", "comment"),
        (r"<!DOCTYPE[^>]*>", "keyword"),
        (r"</?[A-Za-z][\w-]*", "tag"),
        (r"[A-Za-z-]+=", "attribute"),
        (r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', "string"),
    ],
}

CSS = {
    "name": "CSS",
    "extensions": [".css", ".scss", ".less"],
    "rules": [
        (r"/\*(?:.|\n)*?\*/", "comment"),
        (r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', "string"),
        (r"[.#]?[A-Za-z_-][\w-]*(?=\s*\{)", "tag"),
        (r"[A-Za-z-]+(?=\s*:)", "attribute"),
        (r"#[0-9a-fA-F]{3,8}\b", "constant"),
        (r"\b\d+(?:\.\d+)?(?:px|em|rem|%|vh|vw|s|ms|deg)?\b", "number"),
    ],
}

JSON_SYN = {
    "name": "JSON",
    "extensions": [".json"],
    "rules": [
        (r'"(?:\\.|[^"\\])*"(?=\s*:)', "attribute"),
        (r'"(?:\\.|[^"\\])*"', "string"),
        (r"\b(true|false|null)\b", "constant"),
        (r"-?\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b", "number"),
    ],
}

MD = {
    "name": "Markdown",
    "extensions": [".md", ".markdown"],
    "rules": [
        (r"^#{1,6} .*$", "keyword"),
        (r"`[^`\n]+`", "string"),
        (r"\*\*[^*]+\*\*|__[^_]+__", "attribute"),
        (r"\*[^*]+\*|_[^_]+_", "comment"),
        (r"^\s*[-*+] ", "tag"),
    ],
}

SYNTAXES = [PY, JS, HTML, CSS, JSON_SYN, MD]

_EXT_MAP = {}
for s in SYNTAXES:
    for e in s["extensions"]:
        _EXT_MAP[e] = s["name"]

def list_syntaxes():
    return [{"name": s["name"], "extensions": s["extensions"]} for s in SYNTAXES]

def guess(path):
    if not path:
        return "Plain"
    ext = os.path.splitext(path)[1].lower()
    return _EXT_MAP.get(ext, "Plain")

def get(name):
    for s in SYNTAXES:
        if s["name"] == name:
            return s
    return None

def tokenize(text, syntax_name):
    """Return list of (start, end, kind) spans for highlighting."""
    s = get(syntax_name)
    if not s:
        return []
    spans = []
    for pattern, kind in s["rules"]:
        for m in re.finditer(pattern, text, re.MULTILINE):
            spans.append((m.start(), m.end(), kind))
    # sort, prefer later rules only for non-overlapping (first wins)
    spans.sort(key=lambda x: (x[0], -(x[1] - x[0])))
    out = []
    last = 0
    for start, end, kind in spans:
        if start < last:
            continue
        out.append((start, end, kind))
        last = end
    return out