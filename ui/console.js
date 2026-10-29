const Console = {
  init() {
    this.el = document.getElementById("console");
    this.out = document.getElementById("console-output");
    document.getElementById("console-close").onclick = () => this.hide();
  },
  show() { this.el.classList.remove("hidden"); },
  hide() { this.el.classList.add("hidden"); },
  toggle() { this.el.classList.toggle("hidden"); },
  log(...parts) {
    this.out.textContent += parts.join(" ") + "\n";
    this.out.scrollTop = this.out.scrollHeight;
  },
  clear() { this.out.textContent = ""; },
};