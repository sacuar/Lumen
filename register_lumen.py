"""Register Lumen with the Windows shell for .txt .php .html .py.

Usage (run once, no admin needed):
    python register_lumen.py "C:\\path\\to\\Lumen.exe"

After it finishes:
  - Lumen appears in "Open with" for those extensions.
  - Lumen appears in Settings -> Apps -> Default apps.
  - Pick it once with "Always use this app" to make it the default.

To unregister:
    python register_lumen.py --unregister
"""
import os
import sys
import winreg

APP_NAME   = "Lumen"
PROGID     = "Lumen.Editor"
EXTENSIONS = [".txt", ".php", ".html", ".py"]

# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def _open(root, path):
    return winreg.CreateKeyEx(root, path, 0, winreg.KEY_WRITE)

def _set(root, path, name=None, value=None, regtype=winreg.REG_SZ):
    key = _open(root, path)
    try:
        if name is None:
            winreg.SetValueEx(key, "", 0, regtype, value)
        else:
            winreg.SetValueEx(key, name, 0, regtype, value)
    finally:
        winreg.CloseKey(key)

def _delete_tree(root, path):
    """Recursively delete a key. Silently ignores missing keys."""
    try:
        key = winreg.OpenKey(root, path, 0,
                             winreg.KEY_READ | winreg.KEY_WRITE)
    except FileNotFoundError:
        return
    # walk children first
    children = []
    i = 0
    while True:
        try:
            children.append(winreg.EnumKey(key, i))
            i += 1
        except OSError:
            break
    winreg.CloseKey(key)
    for child in children:
        _delete_tree(root, f"{path}\\{child}")
    try:
        winreg.DeleteKey(root, path)
    except FileNotFoundError:
        pass

def _delete_value(root, path, name):
    try:
        key = winreg.OpenKey(root, path, 0, winreg.KEY_WRITE)
    except FileNotFoundError:
        return
    try:
        winreg.DeleteValue(key, name)
    except FileNotFoundError:
        pass
    finally:
        winreg.CloseKey(key)

# --------------------------------------------------------------------------
# register
# --------------------------------------------------------------------------
def register(exe_path):
    exe_path = os.path.abspath(exe_path)
    if not os.path.isfile(exe_path):
        sys.exit(f"Lumen.exe not found: {exe_path}")

    # 1. ProgID: friendly name, icon, open command
    base = f"Software\\Classes\\{PROGID}"
    _set(winreg.HKEY_CURRENT_USER, base, None, APP_NAME)
    _set(winreg.HKEY_CURRENT_USER, base, "FriendlyAppName", APP_NAME)
    _set(winreg.HKEY_CURRENT_USER, f"{base}\\DefaultIcon",
         None, f'"{exe_path}",0')
    _set(winreg.HKEY_CURRENT_USER, f"{base}\\shell\\open", None, "Open")
    _set(winreg.HKEY_CURRENT_USER, f"{base}\\shell\\open\\command",
         None, f'"{exe_path}" "%1"')

    # 2. Per-extension: register ProgID under OpenWithProgids
    for ext in EXTENSIONS:
        ext_key = f"Software\\Classes\\{ext}"
        _set(winreg.HKEY_CURRENT_USER,
             f"{ext_key}\\OpenWithProgids", PROGID, b"", winreg.REG_NONE)

    # 3. RegisteredApplications -> Settings > Default apps listing
    _set(winreg.HKEY_CURRENT_USER, "Software\\RegisteredApplications",
         APP_NAME, f"Software\\{APP_NAME}\\Capabilities")

    # 4. Capabilities block used by "Open with" / Default apps UI
    cap = f"Software\\{APP_NAME}\\Capabilities"
    _set(winreg.HKEY_CURRENT_USER, cap, "ApplicationName", APP_NAME)
    _set(winreg.HKEY_CURRENT_USER, cap, "ApplicationDescription",
         "Lumen — a Sublime Text alternative")
    for ext in EXTENSIONS:
        _set(winreg.HKEY_CURRENT_USER,
             f"{cap}\\FileAssociations", ext, PROGID)

    print(f"Registered {APP_NAME} -> {exe_path}")
    print(f"Extensions: {', '.join(EXTENSIONS)}")
    print()
    print("To make Lumen the default:")
    print("  Right-click a file -> Open with -> Choose another app")
    print("  -> Lumen -> tick 'Always use this app'.")
    print("Or: Settings -> Apps -> Default apps -> search 'Lumen'.")

# --------------------------------------------------------------------------
# unregister
# --------------------------------------------------------------------------
def unregister():
    _delete_tree(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{PROGID}")
    _delete_tree(winreg.HKEY_CURRENT_USER, f"Software\\{APP_NAME}")
    _delete_value(winreg.HKEY_CURRENT_USER,
                  "Software\\RegisteredApplications", APP_NAME)
    for ext in EXTENSIONS:
        _delete_value(winreg.HKEY_CURRENT_USER,
                      f"Software\\Classes\\{ext}\\OpenWithProgids", PROGID)
    print(f"Unregistered {APP_NAME}.")

# --------------------------------------------------------------------------
# entry
# --------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--unregister":
        unregister()
    else:
        default_exe = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "dist", "Lumen", "Lumen.exe")
        exe = sys.argv[1] if len(sys.argv) > 1 else default_exe
        register(exe)