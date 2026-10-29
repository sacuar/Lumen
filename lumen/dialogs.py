"""Native OS file/folder dialogs via tkinter.

Called from HTTP handler threads. Returns "" if the user cancels.
Raises RuntimeError if tkinter is unavailable (headless server).

On Windows, tkinter can create+destroy Tk() from a worker thread.
On macOS you'd need to marshal this to the main thread; not handled
here because Lumen's primary target is Windows.
"""
import threading

_lock = threading.Lock()


def _root():
    import tkinter as tk
    r = tk.Tk()
    r.withdraw()
    try:
        r.attributes("-topmost", True)
    except Exception:
        pass
    return r


def _convert(filetypes):
    """[{name, pattern}] -> tkinter's [(name, "*.py *.txt")]."""
    if not filetypes:
        return [("All files", "*.*")]
    out = []
    for ft in filetypes:
        name = ft.get("name", "Files")
        pat = ft.get("pattern", "*.*")
        if isinstance(pat, list):
            pat = " ".join(pat)
        out.append((name, pat))
    return out


def open_file(title="Open File", filetypes=None):
    with _lock:
        root = _root()
        try:
            from tkinter import filedialog
            return filedialog.askopenfilename(
                parent=root, title=title, filetypes=_convert(filetypes))
        finally:
            root.destroy()


def save_file(title="Save As", defaultextension="", filetypes=None):
    with _lock:
        root = _root()
        try:
            from tkinter import filedialog
            return filedialog.asksaveasfilename(
                parent=root, title=title, defaultextension=defaultextension,
                filetypes=_convert(filetypes))
        finally:
            root.destroy()


def open_folder(title="Open Folder"):
    with _lock:
        root = _root()
        try:
            from tkinter import filedialog
            return filedialog.askdirectory(parent=root, title=title)
        finally:
            root.destroy()