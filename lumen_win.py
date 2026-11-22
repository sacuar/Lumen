"""Native window with a private per-instance local HTTP service."""
import os,sys,threading
from http.server import ThreadingHTTPServer
from lumen import server,__version__
def main():
    if "--smoke-test" in sys.argv:
        from lumen import preview,runtime
        assert os.path.isfile(os.path.join(server.UI_DIR,"index.html"))
        import webview,PIL,pypdfium2,docx
        return
    import webview
    if sys.platform=="win32":
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("sacuar.Lumen.Editor")
    if len(sys.argv)>1 and os.path.exists(sys.argv[1]):server.INITIAL_PATH=os.path.abspath(sys.argv[1])
    httpd=ThreadingHTTPServer((server.HOST,0),server.Handler)
    threading.Thread(target=httpd.serve_forever,daemon=True).start()
    window=webview.create_window("Lumen",f"http://127.0.0.1:{httpd.server_port}",width=1280,height=800,min_size=(800,500),confirm_close=True)
    try:webview.start(gui="edgechromium" if sys.platform=="win32" else None)
    finally:httpd.shutdown();httpd.server_close()
if __name__=="__main__":main()
