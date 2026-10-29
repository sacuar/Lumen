"""Launch Lumen as a native desktop window (no browser chrome)."""
import os
import sys
import threading
import time
import urllib.request
from urllib.parse import quote

from lumen.server import run_server, HOST, PORT

try:
    import webview
except ImportError:
    print("pywebview not installed. Run: pip install pywebview")
    sys.exit(1)

URL = f"http://{HOST}:{PORT}"


def _start():
    run_server(HOST, PORT)


def _wait():
    for _ in range(60):
        try:
            urllib.request.urlopen(URL, timeout=0.2)
            return True
        except Exception:
            time.sleep(0.1)
    return False


def main():
    initial_file = sys.argv[1] if len(sys.argv) > 1 else ""
    if initial_file and not os.path.isfile(initial_file):
        initial_file = ""

    t = threading.Thread(target=_start, daemon=True)
    t.start()
    if not _wait():
        print("server failed to start")
        sys.exit(1)

    start_url = f"{URL}/?open={quote(initial_file)}" if initial_file else URL

    webview.create_window(
        "Lumen", start_url, width=1280, height=800, min_size=(800, 500),
    )
    webview.start()


if __name__ == "__main__":
    main()