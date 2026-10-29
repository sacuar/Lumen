const Find = {
  editor: null,
  init(editor) {
    this.editor = editor;
    this.bar = document.getElementById("findbar");
    this.input = document.getElementById("find-input");
    this.replace = document.getElementById("replace-input");
    document.getElementById("find-close").onclick = () => this.bar.classList.add("hidden");
    document.getElementById("find-next").onclick = () => editor.findNext(this.input.value);
    document.getElementById("find-prev").onclick = () => editor.findPrev(this.input.value);
    document.getElementById("replace-one").onclick = () => {
      editor.replaceOne(this.input.value, this.replace.value);
    };
    document.getElementById("replace-all").onclick = () => {
      const n = editor.replaceAll(this.input.value, this.replace.value);
      console.log(`replaced ${n}`);
    };
    this.input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") editor.findNext(this.input.value);
    });
  },
  open(withReplace) {
    this.bar.classList.remove("hidden");
    this.replace.style.display = withReplace ? "" : "none";
    document.getElementById("replace-one").style.display = withReplace ? "" : "none";
    document.getElementById("replace-all").style.display = withReplace ? "" : "none";
    this.input.focus();
    this.input.select();
  },
};