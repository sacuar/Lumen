"""Sublime Text `sublime_plugin` module shim.

Depends on `sublime_shim.install()` having run first — which it always
does, because `sublime_shim/__init__.py` sets `sys.modules["sublime"]`
before importing this module.
"""
import sublime  # noqa: F401  (resolves via sys.modules)


class TextCommand:
    def __init__(self, view=None): self.view = view
    def name(self):                return type(self).__name__
    def run(self, edit, **kw):     pass
    def is_enabled(self, **kw):    return True
    def is_visible(self, **kw):    return True
    def description(self, **kw):   return None


class WindowCommand:
    def __init__(self, window=None): self.window = window
    def name(self):                  return type(self).__name__
    def run(self, **kw):             pass
    def is_enabled(self, **kw):      return True
    def is_visible(self, **kw):      return True
    def description(self, **kw):     return None


class ApplicationCommand:
    def name(self):              return type(self).__name__
    def run(self, **kw):         pass
    def is_enabled(self, **kw):  return True
    def is_visible(self, **kw):  return True
    def description(self, **kw): return None


class EventListener:      pass


class ViewEventListener:
    def __init__(self, view): self.view = view
    @classmethod
    def is_applicable(cls, settings): return True


class TextInputHandler:
    def name(self):                return type(self).__name__
    def description(self, text):   return text
    def placeholder(self):         return ""


class ListInputHandler:
    def name(self):                     return type(self).__name__
    def description(self, value, text): return text
    def list_items(self):               return []


class CommandInputHandler:
    def name(self): return type(self).__name__


__all__ = [
    "TextCommand", "WindowCommand", "ApplicationCommand",
    "EventListener", "ViewEventListener",
    "TextInputHandler", "ListInputHandler", "CommandInputHandler",
]