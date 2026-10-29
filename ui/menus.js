const Menus = {
  init(bootData, dispatch) {
    const bar = document.getElementById("menubar");
    bar.innerHTML = "";
    for (const menu of bootData.menus) {
      const el = document.createElement("div");
      el.className = "menu";
      el.textContent = menu.label;
      const dd = document.createElement("div");
      dd.className = "dropdown";
      for (const item of menu.items) {
        if (item.label === "-") {
          const sep = document.createElement("div");
          sep.className = "sep";
          dd.appendChild(sep);
          continue;
        }
        const row = document.createElement("div");
        row.className = "item";
        const label = document.createElement("span");
        label.textContent = item.label;
        row.appendChild(label);
        if (item.keys) {
          const k = document.createElement("span");
          k.className = "key";
          k.textContent = item.keys.join(", ");
          row.appendChild(k);
        }
        row.addEventListener("click", (e) => {
          e.stopPropagation();
          closeAll();
          dispatch(item.command, item.args || {});
        });
        dd.appendChild(row);
      }
      el.appendChild(dd);
      el.addEventListener("click", (e) => {
        e.stopPropagation();
        const wasOpen = el.classList.contains("open");
        closeAll();
        if (!wasOpen) el.classList.add("open");
      });
      bar.appendChild(el);
    }
    document.addEventListener("click", closeAll);
    function closeAll() {
      document.querySelectorAll("#menubar .menu.open").forEach(m => m.classList.remove("open"));
    }
  },
};