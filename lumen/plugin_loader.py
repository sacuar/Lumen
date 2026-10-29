"""Loads Sublime-style plugins, provides sublime_plugin shim, and runs commands."""
import os
import sys
import threading
import traceback
import types

import sublime_shim
sublime_shim.install()          # registers `sublime` and `sublime_plugin`

PLUGIN_DIR = sublime_shim.packages_path()
os.makedirs(PLUGIN_DIR, exist_ok=True)


class PluginManager:
    _ui_queue = []
    _lock = threading.Lock()

    def __init__(self):
        self.plugins = {}          # name -> module
        self.commands = {}         # class name -> (class, kind)
        self.listeners = []        # instantiated listeners
        self._loaded = False

    # ---- install / load ---------------------------------------------------
    def load_all(self):
        if self._loaded:
            return
        for name in sorted(os.listdir(PLUGIN_DIR)):
            if name.endswith(".py"):
                self.install_from_file(
                    os.path.join(PLUGIN_DIR, name), record_name=name[:-3])
        self._loaded = True

    def install_from_file(self, path, record_name=None):
        try:
            with open(path, "r", encoding="utf-8") as f:
                src = f.read()
        except Exception as e:
            return False, f"read failed: {e}"
        name = record_name or os.path.splitext(os.path.basename(path))[0]
        return self.install_from_source(name, src)

    def install_from_source(self, name, source):
        modname = f"lumen_plugin_{name}"
        mod = types.ModuleType(modname)
        mod.__dict__["__file__"] = os.path.join(PLUGIN_DIR, name + ".py")
        try:
            code = compile(source, mod.__dict__["__file__"], "exec")
            exec(code, mod.__dict__)
        except Exception:
            tb = traceback.format_exc()
            return False, "compile/exec failed:\n" + tb

        self.plugins[name] = mod
        import sublime_plugin
        for attr in dir(mod):
            obj = getattr(mod, attr)
            if isinstance(obj, type):
                if issubclass(obj, sublime_plugin.TextCommand):
                    self.commands[attr] = (obj, "text")
                elif issubclass(obj, sublime_plugin.WindowCommand):
                    self.commands[attr] = (obj, "window")
                elif issubclass(obj, sublime_plugin.ApplicationCommand):
                    self.commands[attr] = (obj, "app")
                elif issubclass(obj, sublime_plugin.EventListener):
                    try:
                        self.listeners.append(obj())
                    except Exception:
                        pass
                elif issubclass(obj, sublime_plugin.ViewEventListener):
                    try:
                        self.listeners.append(obj(None))
                    except Exception:
                        pass

        try:
            dst = os.path.join(PLUGIN_DIR, name + ".py")
            with open(dst, "w", encoding="utf-8") as f:
                f.write(source)
        except Exception:
            pass
        return True, f"installed {name}"

    # ---- listing ----------------------------------------------------------
    def list(self):
        return [{"name": n, "commands": [c for c in self.commands
                if c in dir(m)]} for n, m in self.plugins.items()]

    # ---- command execution ------------------------------------------------
    def run_command(self, class_name, args):
        entry = self.commands.get(class_name)
        if not entry:
            for k, v in self.commands.items():
                if k.lower() == class_name.lower():
                    entry = v
                    break
        if not entry:
            return {"ok": False, "error": f"no such command: {class_name}"}
        cls, kind = entry
        try:
            if kind == "text":
                cmd = cls(sublime_shim.View())
                cmd.run(sublime_shim.Edit(), **args)
            elif kind == "window":
                cmd = cls(sublime_shim.Window())
                cmd.run(**args)
            else:
                cmd = cls()
                cmd.run(**args)
            return {"ok": True}
        except Exception as e:
            return {"ok": False,
                    "error": f"{type(e).__name__}: {e}\n{traceback.format_exc()}"}

    # ---- events -----------------------------------------------------------
    def broadcast(self, event, *args):
        for l in self.listeners:
            fn = getattr(l, event, None)
            if fn:
                try:
                    fn(*args)
                except Exception:
                    traceback.print_exc()

    # ---- UI bridge --------------------------------------------------------
    @classmethod
    def _push_ui_event(cls, kind, payload):
        with cls._lock:
            cls._ui_queue.append({"kind": kind, "payload": payload})

    @classmethod
    def drain_ui_events(cls):
        with cls._lock:
            out = cls._ui_queue[:]
            cls._ui_queue.clear()
        return out