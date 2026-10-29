"""Build systems."""
import os
import subprocess
import sys

BUILDS = {
    "Python": {
        "cmd": [sys.executable, "-u", "{file}"],
        "extensions": [".py", ".pyw"],
    },
    "Node": {
        "cmd": ["node", "{file}"],
        "extensions": [".js", ".mjs"],
    },
    "Make": {
        "cmd": ["make"],
        "extensions": [".c", ".cpp", ".h"],
    },
}

def list_builds():
    return [{"name": k, "extensions": v["extensions"]} for k, v in BUILDS.items()]

def guess(path):
    ext = os.path.splitext(path)[1].lower()
    for name, b in BUILDS.items():
        if ext in b["extensions"]:
            return name
    return None

def run(path, content, name=None):
    path = path or ""
    name = name or guess(path)
    if not name:
        return {"ok": False, "output": "No build system for this file type.", "code": -1}
    b = BUILDS[name]
    # write to a temp file if path is empty
    tmp = None
    if not path:
        import tempfile
        fd, tmp = tempfile.mkstemp(suffix=".py")
        os.close(fd)
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(content)
        path = tmp
    try:
        proc = subprocess.run(
            [c.replace("{file}", path) for c in b["cmd"]],
            cwd=os.path.dirname(os.path.abspath(path)) or None,
            capture_output=True, text=True, timeout=60,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        return {"ok": proc.returncode == 0, "output": out, "code": proc.returncode, "build": name}
    except FileNotFoundError:
        return {"ok": False, "output": f"Build command not found: {b['cmd'][0]}", "code": -1}
    except subprocess.TimeoutExpired:
        return {"ok": False, "output": "Build timed out.", "code": -1}
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)