const API = {
  async post(path, data) {
    const r = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data || {}),
    });
    return r.json();
  },
  boot: () => API.post("/api/boot"),
  read: (path) => API.post("/api/fs/read", { path }),
  write: (path, content) => API.post("/api/fs/write", { path, content }),
  list: (path) => API.post("/api/fs/list", { path }),
  build: (path, content) => API.post("/api/build", { path, content }),
  installPlugin: (path) => API.post("/api/plugin/install", { path }),
  installPluginSource: (name, content) =>
    API.post("/api/plugin/install", { name, content }),
  listPlugins: () => API.post("/api/plugin/list"),
  command: (name, args) => API.post("/api/command", { name, args }),

  // ---- native OS dialogs (open on the machine running the Lumen server) ----
  dialogOpenFile:   (title, types) =>
    API.post("/api/dialog/open_file",   { title, types }),
  dialogSaveFile:   (title, ext, types) =>
    API.post("/api/dialog/save_file",   { title, ext, types }),
  dialogOpenFolder: (title) =>
    API.post("/api/dialog/open_folder", { title }),
};