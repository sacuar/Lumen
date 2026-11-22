"""Lumen HTTP server. Stdlib only."""
import json
import secrets, hmac
from pathlib import Path
from lumen import __version__, preview, release
import os
import sys
import threading
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from lumen import menus, keymaps, syntax, builds, api
from lumen.plugin_loader import PluginManager

HOST = "127.0.0.1"
PORT = 8765

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_DIR = os.path.join(ROOT, "ui")

PLUGINS = PluginManager()
BUILD_LOCK = threading.Lock()
SESSION_TOKEN = secrets.token_urlsafe(32)
INITIAL_PATH = ''


class Handler(BaseHTTPRequestHandler):
    server_version = "Lumen/"+__version__

    def log_message(self, fmt, *args):
        pass

    # ---------- helpers ----------
    def _json(self, obj, code=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _err(self, msg, code=400):
        self._json({"error": msg}, code)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw or b"{}")
        except Exception:
            return {}

    def _serve_file(self, path, content_type):
        if not os.path.isfile(path):
            self._err("not found", 404)
            return
        with open(path, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ---------- GET ----------
    def do_GET(self):
        p = urlparse(self.path).path
        if p in ("/", "/index.html"):
            if self.headers.get("Host") != f"127.0.0.1:{self.server.server_port}":return self._err("Invalid host",403)
            body=Path(UI_DIR,"index.html").read_text(encoding="utf-8").replace("__LUMEN_SESSION__",SESSION_TOKEN).encode()
            self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8");self.send_header("Cache-Control","no-store");self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body);return
        static = os.path.realpath(os.path.join(UI_DIR, p.lstrip("/")))
        if os.path.commonpath([os.path.realpath(UI_DIR),static])!=os.path.realpath(UI_DIR):return self._err("not found",404)
        if os.path.isfile(static):
            ctype = "text/css" if p.endswith(".css") else \
                    "application/javascript" if p.endswith(".js") else \
                    "application/octet-stream"
            return self._serve_file(static, ctype)
        self._err("not found", 404)

    # ---------- POST ----------
    def do_POST(self):
        p = urlparse(self.path).path
        if self.headers.get("Host") != f"127.0.0.1:{self.server.server_port}" or not hmac.compare_digest(self.headers.get("X-Lumen-Session",""),SESSION_TOKEN):return self._err("Forbidden",403)
        if self.headers.get("Origin") not in (None,f"http://127.0.0.1:{self.server.server_port}"):return self._err("Forbidden",403)
        if int(self.headers.get("Content-Length","0"))>24*1024*1024:return self._err("Request too large",413)
        routes = {
            "/api/preview": self.preview_file,
            "/api/update": self.update_check,
            "/api/boot": self.boot,
            "/api/fs/read": self.fs_read,
            "/api/fs/write": self.fs_write,
            "/api/fs/list": self.fs_list,
            "/api/build": self.build,
            "/api/plugin/install": self.plugin_install,
            "/api/plugin/list": self.plugin_list,
            "/api/command": self.command,
            "/api/dialog/open_file": self.dlg_open_file,
            "/api/dialog/save_file": self.dlg_save_file,
            "/api/dialog/open_folder": self.dlg_open_folder,
        }
        fn = routes.get(p)
        if not fn:
            return self._err("unknown endpoint", 404)
        try:
            fn(self._read_json())
        except Exception as e:
            traceback.print_exc()
            self._err(f"{type(e).__name__}: {e}", 500)

    # ---------- endpoints ----------
    def boot(self, _):
        self._json({
            "version": __version__, "initial_path": INITIAL_PATH, "initial_dir": os.path.isdir(INITIAL_PATH),
            "menus": menus.MENUS,
            "keymaps": keymaps.KEYMAPS,
            "syntaxes": syntax.list_syntaxes(),
            "builds": builds.list_builds(),
            "plugins": PLUGINS.list(),
            "cwd": os.getcwd(),
        })

    def fs_read(self, data):
        path = data.get("path")
        if not path or not os.path.isfile(path):
            return self._err("no such file")
        if preview.supports(path):return self._json({"preview":True})
        if os.path.getsize(path)>16*1024*1024:return self._err("Text file exceeds 16 MB")
        raw=Path(path).read_bytes()
        if b"\x00" in raw and not raw.startswith((b"\xff\xfe",b"\xfe\xff")):return self._err("Binary file cannot be edited")
        encoding="utf-16" if raw.startswith((b"\xff\xfe",b"\xfe\xff")) else "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
        try:content=raw.decode(encoding)
        except UnicodeError:return self._err("Unsupported text encoding; file not modified")
        self._json({"path": path, "content": content,
                    "syntax": syntax.guess(path),"encoding":encoding,"eol":"\r\n" if "\r\n" in content else "\n"})

    def fs_write(self, data):
        path = data.get("path")
        content = data.get("content", "")
        if not path:
            return self._err("no path")
        if preview.supports(path):return self._err("Preview files are read-only")
        target=Path(path)
        if target.exists():
            raw=target.read_bytes()
            if b"\x00" in raw and not raw.startswith((b"\xff\xfe",b"\xfe\xff")):return self._err("Refusing to overwrite binary file")
            try:raw.decode("utf-16" if raw.startswith((b"\xff\xfe",b"\xfe\xff")) else "utf-8-sig")
            except UnicodeError:return self._err("Refusing to overwrite unsupported encoding")
        encoding=data.get("encoding","utf-8")
        if encoding not in ("utf-8","utf-8-sig","utf-16"):return self._err("Unsupported encoding")
        eol=data.get("eol","\n")
        if eol not in ("\n","\r\n"):return self._err("Invalid newline")
        target.write_bytes(content.replace("\r\n","\n").replace("\n",eol).encode(encoding))
        self._json({"ok": True, "path": path})

    def fs_list(self, data):
        path = data.get("path") or os.getcwd()
        if not os.path.isdir(path):
            return self._err("not a directory")
        entries = []
        try:
            for name in sorted(os.listdir(path)):
                if name.startswith("."):
                    continue
                full = os.path.join(path, name)
                entries.append({
                    "name": name,
                    "path": full,
                    "dir": os.path.isdir(full),
                })
        except PermissionError:
            pass
        self._json({"path": path, "entries": entries})

    def build(self, data):
        path = data.get("path") or ""
        content = data.get("content", "")
        with BUILD_LOCK:result = builds.run(path, content, data.get("name"), data.get("python","Auto"))
        PLUGINS.broadcast("on_build_finished", result)
        self._json(result)

    def preview_file(self,data):
        self._json(preview.render(data.get("path",""),data.get("page",0)))

    def update_check(self,data):
        self._json(release.check())

    def plugin_install(self, data):
        content = data.get("content")
        name = data.get("name")
        if content and name:
            ok, msg = PLUGINS.install_from_source(name, content)
        else:
            src = data.get("path")
            if not src or not os.path.isfile(src):
                return self._err("no plugin source")
            ok, msg = PLUGINS.install_from_file(src)
        self._json({"ok": ok, "message": msg, "plugins": PLUGINS.list()})

    def plugin_list(self, _):
        self._json({"plugins": PLUGINS.list()})

    def command(self, data):
        name = data.get("name")
        args = data.get("args", {})
        result = PLUGINS.run_command(name, args)
        self._json({"ok": True, "result": result})

    # ---------- native dialogs ----------
    def _run_dialog(self, fn):
        try:
            from lumen import dialogs
            path = fn(dialogs)
            self._json({"ok": True, "path": path or ""})
        except Exception as e:
            self._json({"ok": False, "path": "",
                        "error": f"{type(e).__name__}: {e}"})

    def dlg_open_file(self, data):
        self._run_dialog(lambda d: d.open_file(
            title=data.get("title", "Open File"),
            filetypes=data.get("types")))

    def dlg_save_file(self, data):
        self._run_dialog(lambda d: d.save_file(
            title=data.get("title", "Save As"),
            defaultextension=data.get("ext", ""),
            filetypes=data.get("types")))

    def dlg_open_folder(self, data):
        self._run_dialog(lambda d: d.open_folder(
            title=data.get("title", "Open Folder")))


def run_server(host=HOST, port=PORT):
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"Lumen running at http://{host}:{port}")
    httpd.serve_forever()


def main():
    port = int(os.environ.get("LUMEN_PORT", PORT))
    if os.environ.get("LUMEN_OPEN_BROWSER", "1") == "1":
        threading.Timer(0.8, lambda: webbrowser.open(f"http://{HOST}:{port}")).start()
    run_server(port=port)


if __name__ == "__main__":
    main()