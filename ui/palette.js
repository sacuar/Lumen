const Palette = {
  items: [],
  filtered: [],
  active: 0,
  dispatch: null,

  init(dispatch) {
    this.dispatch = dispatch;
    this.el = document.getElementById("palette");
    this.input = document.getElementById("palette-input");
    this.list = document.getElementById("palette-list");
    this.input.addEventListener("input", () => this._filter());
    this.input.addEventListener("keydown", (e) => this._key(e));
    this.el.addEventListener("click", (e) => e.stopPropagation());
  },

  register(items) { this.items = items; },

  open() {
    this.el.classList.remove("hidden");
    this.input.value = "";
    this._filter();
    this.input.focus();
  },
  close() { this.el.classList.add("hidden"); },

  _filter() {
    const q = this.input.value.toLowerCase();
    this.filtered = this.items.filter(i => i.label.toLowerCase().includes(q));
    this.active = 0;
    this._render();
  },
  _render() {
    this.list.innerHTML = "";
    this.filtered.slice(0, 50).forEach((item, i) => {
      const li = document.createElement("li");
      li.textContent = item.label;
      if (i === this.active) li.classList.add("active");
      li.addEventListener("click", () => this._choose(i));
      this.list.appendChild(li);
    });
  },
  _key(e) {
    if (e.key === "Escape") return this.close();
    if (e.key === "ArrowDown") { this.active = Math.min(this.active + 1, this.filtered.length - 1); this._render(); e.preventDefault(); }
    if (e.key === "ArrowUp") { this.active = Math.max(this.active - 1, 0); this._render(); e.preventDefault(); }
    if (e.key === "Enter") { this._choose(this.active); e.preventDefault(); }
  },
  _choose(i) {
    const item = this.filtered[i];
    if (!item) return;
    this.close();
    this.dispatch(item.command, item.args || {});
  },
};