const Lumen = {
  boot: null,
  editor: null,
  currentPath: null,
  dirty: false,
  tabs: [],
  activeTab: 0,

  async start() {
    this.boot = await API.boot();
    this.editor = new Editor({
      onChange: (v) => {
        this.dirty = true;
        this._updateTitle();
      },
      onCursor: (c) => {
        document.getElementById("status").textContent =
          `Ln ${c.line}, Col ${c.col}   ${this.editor.syntax}`;
      },
    });
    this.editor.value = "";
    this.editor.setSyntax("Plain");

    Menus.init(this.boot, (cmd, args) => this.dispatch(cmd, args));
    Palette.init((cmd, args) => this.dispatch(cmd, args));
    Find.init(this.editor);
    Sidebar.init((path) => this.openFile(path));
    Console.init();

    this._buildPaletteItems();
    this._bindKeys();
    this._updateTitle();
    this.editor.focus();
  },

  _buildPaletteItems() {
    const items = [];
    for (const m of this.boot.menus) {
      for (const it of m.items) {
        if (it.command && it.label !== "-") items.push(it);
      }
    }
    for (const p of this.boot.plugins || []) {
      for (const c of p.commands || []) {
        items.push({
          label: `Plugin: ${c}`,
          command: "run_plugin_command",
          args: { name: c },
        });
      }
    }
    Palette.register(items);
  },

  _bindKeys() {
    document.addEventListener("keydown", (e) => {
      const mod = e.ctrlKey || e.metaKey;
      if (!mod) return;
      const k = e.key.toLowerCase();
      const map = {
        "n": "new_file", "o": "open_file", "s": "save",
        "w": "close_file", "z": "undo", "y": "redo",
        "f": "find", "h": "replace", "g": "goto_line",
        "b": "build",
      };
      if (e.shiftKey && k === "p") return this.dispatch("command_palette", {});
      if (e.shiftKey && k === "s") return this.dispatch("save_as", {});
      if (e.shiftKey && k === "b") return this.dispatch("build_with", {});
      if (k === "/") { e.preventDefault(); return this.dispatch("toggle_comment", {}); }
      if (k === "`") { e.preventDefault(); return this.dispatch("toggle_console", {}); }
      if (map[k]) { e.preventDefault(); this.dispatch(map[k], {}); }
    });
  },

  async dispatch(command, args) {
    switch (command) {
      case "new_file": return this.newFile();
      case "open_file": return this.openFileDialog();
      case "open_folder": return Sidebar.pickFolder();
      case "save": return this.save();
      case "save_as": return this.saveAs();
      case "close_file": return this.closeFile();
      case "exit": return window.close();
      case "undo": document.execCommand("undo"); return;
      case "redo": document.execCommand("redo"); return;
      case "find": return Find.open(false);
      case "replace": return Find.open(true);
      case "goto_line": return this.gotoLine();
      case "command_palette": return Palette.open();
      case "build": return this.build();
      case "build_with": return this.buildWith();
      case "toggle_comment": return this.toggleComment();
      case "toggle_console": return Console.toggle();
      case "toggle_sidebar":
        document.getElementById("sidebar").classList.toggle("collapsed");
        return;
      case "set_syntax":
        this.editor.setSyntax(args.name);
        document.getElementById("status").textContent = "Syntax: " + args.name;
        return;
      case "install_plugin": return this.installPluginDialog();
      case "list_plugins": return this.listPlugins();
      case "run_plugin_command": return this.runPluginCommand(args.name);
      case "about":
        alert("Lumen 0.3.0 — a Sublime Text alternative.");
        return;
    }
  },

  // -------- files --------
  newFile() {
    this.editor.value = "";
    this.editor.setSyntax("Plain");
    this.currentPath = null;
    this.dirty = false;
    this._updateTitle();
  },

  async openFileDialog() {
    const res = await API.dialogOpenFile("Open File", [
      { name: "Code files", pattern: "*.py *.js *.ts *.html *.css *.json *.md *.txt" },
      { name: "All files", pattern: "*.*" },
    ]);
    if (res.ok && res.path) return this.openFile(res.path);
    if (!res.ok) {                          // tkinter missing → fallback
      const p = prompt("File path:");
      if (p) await this.openFile(p);
    }
  },

  async openFile(path) {
    const res = await API.read(path);
    if (res.error) return alert(res.error);
    this.editor.value = res.content;
    this.editor.setSyntax(res.syntax || "Plain");
    this.currentPath = path;
    this.dirty = false;
    this._updateTitle();
    this._addTab(path);
  },

  async save() {
    if (!this.currentPath) return this.saveAs();
    await API.write(this.currentPath, this.editor.value);
    this.dirty = false;
    this._updateTitle();
  },

  async saveAs() {
    const res = await API.dialogSaveFile("Save As", "", [
      { name: "Code files", pattern: "*.py *.js *.ts *.html *.css *.json *.md *.txt" },
      { name: "All files", pattern: "*.*" },
    ]);
    if (res.ok && res.path) return this._doSaveAs(res.path);
    if (!res.ok) {
      const p = prompt("Save as path:", this.currentPath || "");
      if (p) await this._doSaveAs(p);
    }
  },

  async _doSaveAs(path) {
    await API.write(path, this.editor.value);
    this.currentPath = path;
    this.dirty = false;
    this._updateTitle();
    this._addTab(path);
  },

  closeFile() {
    if (this.dirty && !confirm("Discard unsaved changes?")) return;
    this.newFile();
  },

  // -------- tabs --------
  _addTab(path) {
    if (!this.tabs.includes(path)) this.tabs.push(path);
    this._renderTabs();
  },
  _renderTabs() {
    const tabs = document.getElementById("tabs");
    tabs.innerHTML = "";
    this.tabs.forEach((p, i) => {
      const el = document.createElement("div");
      el.className = "tab" + (p === this.currentPath ? " active" : "");
      el.textContent = p.split(/[\\/]/).pop();
      const close = document.createElement("span");
      close.className = "close";
      close.textContent = "✕";
      close.onclick = (e) => {
        e.stopPropagation();
        this.tabs.splice(i, 1);
        if (this.currentPath === p) this.newFile();
        this._renderTabs();
      };
      el.appendChild(close);
      el.onclick = () => this.openFile(p);
      tabs.appendChild(el);
    });
  },

  // -------- build --------
  async build() {
    Console.show();
    Console.log(`[build] ${this.currentPath || "untitled"}`);
    const res = await API.build(this.currentPath || "", this.editor.value);
    Console.log(res.output || "(no output)");
    Console.log(`[exit ${res.code}]`);
  },
  async buildWith() {
    const name = prompt("Build system (Python/Node/Make):", "Python");
    if (!name) return;
    Console.show();
    const res = await API.build(this.currentPath || "", this.editor.value);
    Console.log(res.output || "(no output)");
  },

  // -------- misc --------
  gotoLine() {
    const el = document.getElementById("goto");
    const input = document.getElementById("goto-input");
    el.classList.remove("hidden");
    input.value = "";
    input.focus();
    const done = () => {
      const n = parseInt(input.value, 10);
      if (n > 0) {
        const lines = this.editor.value.split("\n");
        let pos = 0;
        for (let i = 0; i < Math.min(n - 1, lines.length); i++) pos += lines[i].length + 1;
        this.editor.setSelection(pos);
      }
      el.classList.add("hidden");
      input.removeEventListener("keydown", onKey);
    };
    const onKey = (e) => {
      if (e.key === "Enter") done();
      if (e.key === "Escape") el.classList.add("hidden");
    };
    input.addEventListener("keydown", onKey);
  },

  toggleComment() {
    const { start, end } = this.editor.selection;
    const v = this.editor.value;
    const ls = v.lastIndexOf("\n", start - 1) + 1;
    const le = v.indexOf("\n", end) === -1 ? v.length : v.indexOf("\n", end);
    const block = v.slice(ls, le);
    const commented = block.split("\n")
      .map(l => l.startsWith("// ") ? l.slice(3) : "// " + l)
      .join("\n");
    this.editor.input.value = v.slice(0, ls) + commented + v.slice(le);
    this.editor._refresh();
  },

  async installPluginDialog() {
    const res = await API.dialogOpenFile("Install Plugin", [
      { name: "Sublime plugin", pattern: "*.py" },
      { name: "All files", pattern: "*.*" },
    ]);
    if (res.ok && res.path) return this._installPluginFromPath(res.path);
    if (!res.ok) {                          // tkinter missing → fallback
      const p = prompt("Path to plugin .py file:");
      if (p) await this._installPluginFromPath(p);
    }
  },

  async _installPluginFromPath(path) {
    const r = await API.installPlugin(path);
    Console.show();
    Console.log(r.message || JSON.stringify(r));
    const list = await API.listPlugins();
    this.boot.plugins = list.plugins;
    this._buildPaletteItems();
  },

  async listPlugins() {
    const res = await API.listPlugins();
    Console.show();
    Console.log(JSON.stringify(res.plugins, null, 2));
  },

  async runPluginCommand(name) {
    const res = await API.command(name, {});
    Console.show();
    Console.log(JSON.stringify(res, null, 2));
  },

  _updateTitle() {
    const p = this.currentPath || "untitled";
    document.getElementById("title").textContent = p + (this.dirty ? " •" : "");
  },
};

window.addEventListener("DOMContentLoaded", () => Lumen.start());