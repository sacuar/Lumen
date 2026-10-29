// A dependency-free editor: transparent textarea over a highlighted <pre>.
class Editor {
  constructor(opts) {
    this.input = document.getElementById("input");
    this.highlight = document.getElementById("highlight").querySelector("code");
    this.gutter = document.getElementById("gutter");
    this.syntax = "Plain";
    this.onChange = opts.onChange || (() => {});
    this.onCursor = opts.onCursor || (() => {});
    this._bind();
    this._refresh();
  }

  _bind() {
    this.input.addEventListener("input", () => {
      this._refresh();
      this.onChange(this.value);
    });
    this.input.addEventListener("scroll", () => this._syncScroll());
    this.input.addEventListener("keydown", (e) => this._keydown(e));
    this.input.addEventListener("click", () => this._cursor());
    this.input.addEventListener("keyup", () => this._cursor());
    document.addEventListener("selectionchange", () => {
      if (document.activeElement === this.input) this._cursor();
    });
  }

  _keydown(e) {
    if (e.key === "Tab") {
      e.preventDefault();
      this.insertText("    ");
    }
  }

  _cursor() {
    const pos = this.input.selectionStart;
    const text = this.input.value.slice(0, pos);
    const line = text.split("\n").length;
    const col = pos - text.lastIndexOf("\n");
    this.onCursor({ line, col });
  }

  _syncScroll() {
    this.highlight.parentElement.scrollTop = this.input.scrollTop;
    this.highlight.parentElement.scrollLeft = this.input.scrollLeft;
    this.gutter.scrollTop = this.input.scrollTop;
  }

  _refresh() {
    const text = this.input.value;
    this.highlight.innerHTML = this._tokenize(text) + "\n";
    this._renderGutter(text);
    this._syncScroll();
  }

  _renderGutter(text) {
    const lines = text.split("\n").length;
    let html = "";
    for (let i = 1; i <= lines; i++) html += i + "\n";
    this.gutter.textContent = html;
  }

  _tokenize(text) {
    // Very small client-side tokenizer for the current syntax.
    const esc = (s) => s.replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
    const rules = SYNTAX_RULES[this.syntax] || [];
    if (!rules.length) return esc(text);
    const spans = [];
    for (const [pattern, kind] of rules) {
      const re = new RegExp(pattern, "gm");
      let m;
      while ((m = re.exec(text)) !== null) {
        if (m[0].length === 0) { re.lastIndex++; continue; }
        spans.push([m.index, m.index + m[0].length, kind]);
      }
    }
    spans.sort((a, b) => a[0] - b[0] || (b[1] - b[0]) - (a[1] - a[0]));
    let out = "", last = 0;
    for (const [s, e, kind] of spans) {
      if (s < last) continue;
      out += esc(text.slice(last, s));
      out += `<span class="tok-${kind}">${esc(text.slice(s, e))}</span>`;
      last = e;
    }
    out += esc(text.slice(last));
    return out;
  }

  get value() { return this.input.value; }
  set value(v) { this.input.value = v; this._refresh(); }
  setSyntax(name) { this.syntax = name; this._refresh(); }

  get selection() {
    return { start: this.input.selectionStart, end: this.input.selectionEnd };
  }
  setSelection(start, end) {
    this.input.selectionStart = start;
    this.input.selectionEnd = end === undefined ? start : end;
    this.input.focus();
  }
  insertText(t) {
    const { start, end } = this.selection;
    const v = this.input.value;
    this.input.value = v.slice(0, start) + t + v.slice(end);
    const p = start + t.length;
    this.input.selectionStart = this.input.selectionEnd = p;
    this._refresh();
    this.onChange(this.input.value);
  }
  focus() { this.input.focus(); }

  findNext(query, fromCursor = true) {
    if (!query) return false;
    const v = this.input.value;
    let start = fromCursor ? this.input.selectionEnd : 0;
    let i = v.indexOf(query, start);
    if (i === -1) i = v.indexOf(query, 0);
    if (i === -1) return false;
    this.setSelection(i, i + query.length);
    return true;
  }
  findPrev(query) {
    if (!query) return false;
    const v = this.input.value;
    let end = this.input.selectionStart;
    let i = v.lastIndexOf(query, end - 1);
    if (i === -1) i = v.lastIndexOf(query);
    if (i === -1) return false;
    this.setSelection(i, i + query.length);
    return true;
  }
  replaceOne(query, replacement) {
    const { start, end } = this.selection;
    if (this.input.value.slice(start, end) === query) {
      this.input.value = this.input.value.slice(0, start) + replacement + this.input.value.slice(end);
      this.input.selectionStart = this.input.selectionEnd = start + replacement.length;
      this._refresh();
      this.onChange(this.input.value);
      return true;
    }
    return false;
  }
  replaceAll(query, replacement) {
    if (!query) return 0;
    const parts = this.input.value.split(query);
    const n = parts.length - 1;
    this.input.value = parts.join(replacement);
    this._refresh();
    this.onChange(this.input.value);
    return n;
  }
}

const SYNTAX_RULES = {
  Python: [
    ["#[^\\n]*", "comment"],
    ["\"\"\"[\\s\\S]*?\"\"\"|'''[\\s\\S]*?'''", "string"],
    ["\"(?:\\\\.|[^\"\\\\])*\"|'(?:\\\\.|[^'\\\\])*'", "string"],
    ["\\b(?:def|class|return|if|elif|else|for|while|in|not|and|or|is|import|from|as|with|try|except|finally|raise|yield|lambda|pass|break|continue|global|nonlocal|assert|del|await|async)\\b", "keyword"],
    ["\\b(True|False|None)\\b", "constant"],
    ["\\b\\d+(?:\\.\\d+)?\\b", "number"],
  ],
  JavaScript: [
    ["//[^\\n]*|/\\*[\\s\\S]*?\\*/", "comment"],
    ["\"(?:\\\\.|[^\"\\\\])*\"|'(?:\\\\.|[^'\\\\])*'|`(?:\\\\.|[^`\\\\])*`", "string"],
    ["\\b(?:function|return|if|else|for|while|do|switch|case|break|continue|var|let|const|new|class|extends|import|export|from|as|async|await|try|catch|finally|throw|typeof|instanceof|in|of|this|super|yield|delete|void)\\b", "keyword"],
    ["\\b(true|false|null|undefined|NaN)\\b", "constant"],
    ["\\b\\d+(?:\\.\\d+)?\\b", "number"],
  ],
  HTML: [
    ["<!--[\\s\\S]*?-->", "comment"],
    ["<!DOCTYPE[^>]*>", "keyword"],
    ["</?[A-Za-z][\\w-]*", "tag"],
    ["[A-Za-z-]+=", "attribute"],
    ["\"(?:\\\\.|[^\"\\\\])*\"|'(?:\\\\.|[^'\\\\])*'", "string"],
  ],
  CSS: [
    ["/\\*[\\s\\S]*?\\*/", "comment"],
    ["\"(?:\\\\.|[^\"\\\\])*\"|'(?:\\\\.|[^'\\\\])*'", "string"],
    ["[.#]?[A-Za-z_-][\\w-]*(?=\\s*\\{)", "tag"],
    ["[A-Za-z-]+(?=\\s*:)", "attribute"],
    ["#[0-9a-fA-F]{3,8}\\b", "constant"],
    ["\\b\\d+(?:\\.\\d+)?(?:px|em|rem|%|vh|vw|s|ms|deg)?\\b", "number"],
  ],
  JSON: [
    ["\"(?:\\\\.|[^\"\\\\])*\"(?=\\s*:)", "attribute"],
    ["\"(?:\\\\.|[^\"\\\\])*\"", "string"],
    ["\\b(true|false|null)\\b", "constant"],
    ["-?\\b\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?\\b", "number"],
  ],
  Markdown: [
    ["^#{1,6} .*$", "keyword"],
    ["`[^`\\n]+`", "string"],
    ["\\*\\*[^*]+\\*\\*|__[^_]+__", "attribute"],
    ["\\*[^*]+\\*|_[^_]+_", "comment"],
    ["^\\s*[-*+] ", "tag"],
  ],
  Plain: [],
};