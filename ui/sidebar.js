const Sidebar = {
  root: null,
  onOpen: null,
  init(onOpen) {
    this.onOpen = onOpen;
    this.tree = document.getElementById("filetree");
    this.name = document.getElementById("folder-name");
    document.getElementById("open-folder").onclick = () => this.pickFolder();
    document.getElementById("sidebar").addEventListener("click", (e) => e.stopPropagation());
  },
  async pickFolder() {
    const res = await API.dialogOpenFolder("Open Folder");
    if (res.ok && res.path) return this.load(res.path);
    if (!res.ok) {                          // tkinter missing → fallback
      const p = prompt("Folder path:");
      if (p) await this.load(p);
    }
  },
  async load(path) {
    this.root = path;
    this.name.textContent = path.split(/[\\/]/).pop() || path;
    this.tree.innerHTML = "";
    await this._addDir(path, this.tree, 0);
  },
  async _addDir(path, parent, depth) {
    const res = await API.list(path);
    if (!res.entries) return;
    for (const e of res.entries) {
      const li = document.createElement("li");
      li.textContent = e.name;
      li.style.paddingLeft = (12 + depth * 14) + "px";
      if (e.dir) {
        li.classList.add("dir");
        li.addEventListener("click", async (ev) => {
          ev.stopPropagation();
          if (li.classList.contains("open")) {
            li.classList.remove("open");
            while (li.nextSibling && li.nextSibling.dataset.depth > depth) {
              li.parentNode.removeChild(li.nextSibling);
            }
          } else {
            li.classList.add("open");
            await this._addDir(e.path, li.parentNode, depth + 1);
          }
        });
      } else {
        li.dataset.depth = depth;
        li.addEventListener("click", () => this.onOpen(e.path));
      }
      li.dataset.depth = depth;
      parent.appendChild(li);
    }
  },
};