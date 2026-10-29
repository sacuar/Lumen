"""Sublime Text `sublime` module shim for Lumen.

Bootstrap (called once, before loading any plugin):

    import sublime_shim
    sublime_shim.install()          # registers `sublime` + `sublime_plugin`

Then plugin code can do:

    import sublime
    import sublime_plugin
"""
import os
import sys
import threading

PLATFORM = "windows" if sys.platform.startswith("win") else \
           "linux"   if sys.platform.startswith("linux") else "osx"
VERSION  = "4000"

_HOME         = os.path.join(os.path.expanduser("~"), ".lumen")
_cache_path   = os.path.join(_HOME, "cache")
_packages_dir = os.path.join(_HOME, "packages")
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in (_cache_path, _packages_dir):
    os.makedirs(_d, exist_ok=True)


# ---- top-level functions -------------------------------------------------

def cache_path():              return _cache_path
def packages_path():           return _packages_dir
def installed_packages_path(): return _packages_dir
def platform():                return PLATFORM
def version():                 return VERSION
def arch():                    return "x64"
def executable_path():         return sys.executable

def status_message(msg):       _emit("status", msg)
def error_message(msg):        _emit("error", msg)
def message_dialog(msg):       _emit("dialog", msg)
def ok_cancel_dialog(msg, ok_title=""):
    _emit("dialog", msg); return True

def set_timeout(cb, delay):         return _timer(cb, delay)
def set_timeout_async(cb, delay=0): return _timer(cb, delay)

def _timer(cb, delay):
    t = threading.Timer(delay / 1000.0, cb); t.daemon = True; t.start(); return t

def _emit(kind, payload):
    try:
        from lumen.plugin_loader import PluginManager
        PluginManager._push_ui_event(kind, payload)
    except Exception:
        pass

def load_resource(name):
    p = os.path.join(_PROJECT_ROOT, name)
    if os.path.isfile(p):
        with open(p, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def find_resources(pattern): return []

def load_settings(name):  return Settings()
def save_settings(name):  pass

def expand_variables(value, variables):
    if isinstance(value, str):
        for k, v in variables.items():
            value = value.replace("${%s}" % k, str(v)).replace("$%s" % k, str(v))
        return value
    if isinstance(value, list):  return [expand_variables(v, variables) for v in value]
    if isinstance(value, dict):  return {k: expand_variables(v, variables) for k, v in value.items()}
    return value


# ---- data types ----------------------------------------------------------

class Region:
    def __init__(self, a, b=None):
        self.a = a
        self.b = a if b is None else b
    def begin(self): return min(self.a, self.b)
    def end(self):   return max(self.a, self.b)
    def size(self):  return self.end() - self.begin()
    def empty(self): return self.a == self.b

class Edit:
    def __init__(self): self._changes = []

class Settings:
    def __init__(self): self._d = {}
    def get(self, key, default=None): return self._d.get(key, default)
    def set(self, key, value):        self._d[key] = value
    def has(self, key):               return key in self._d
    def erase(self, key):             self._d.pop(key, None)
    def add_on_change(self, key, cb): pass
    def clear_on_change(self, key):   pass

class View:
    def __init__(self, view_id=0, buffer=""):
        self.id        = view_id
        self._buffer   = buffer
        self._settings = Settings()
        self._sel      = [Region(0)]

    def substr(self, r):       return self._buffer[r.begin():r.end()]
    def size(self):            return len(self._buffer)
    def sel(self):             return list(self._sel)
    def settings(self):        return self._settings
    def file_name(self):       return self._settings.get("filename", "")
    def is_dirty(self):        return False
    def set_scratch(self, f):  pass
    def set_syntax_file(self, name): self._settings.set("syntax", name)
    def find_all(self, pattern, flags=0): return [Region(0, 0)]
    def window(self):          return Window()

    def insert(self, edit, pt, string):
        self._buffer = self._buffer[:pt] + string + self._buffer[pt:]
        _emit("view_edit", {"view": self.id, "ops": [["insert", pt, string]]})

    def erase(self, edit, region):
        self._buffer = self._buffer[:region.begin()] + self._buffer[region.end():]
        _emit("view_edit", {"view": self.id,
                            "ops": [["erase", region.begin(), region.end()]]})

    def run_command(self, name, args=None):
        _emit("run_view_command", {"name": name, "args": args or {}, "view": self.id})

class Window:
    def __init__(self, win_id=0): self.id = win_id
    def active_view(self):         return View()
    def views(self):               return [View()]
    def run_command(self, name, args=None):
        _emit("run_window_command", {"name": name, "args": args or {}})
    def show_quick_panel(self, items, on_done, *a, **k):
        _emit("quick_panel", {"items": [str(i) for i in items]})

def active_window(): return Window()
def windows():       return [Window()]


# ---- bootstrap -----------------------------------------------------------

def install():
    """Register `sublime` and `sublime_plugin` in sys.modules. Idempotent."""
    if sys.modules.get("sublime") is sys.modules[__name__]:
        return sys.modules[__name__]
    sys.modules["sublime"] = sys.modules[__name__]   # must be set first
    from . import sublime_plugin as _sp              # this does `import sublime`
    sys.modules["sublime_plugin"] = _sp
    return sys.modules[__name__]