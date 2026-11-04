import os
import sys
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

WORKSPACE_ROOT = Path("C:/Users/ACER/Documents/Codex/revenue-copilot-international-phase0")
VIBE_FRONTEND_DIST = Path("C:/Users/ACER/AppData/Local/MaiVibeTrading/Vibe-Trading/frontend/dist")

class FastWorkspaceHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WORKSPACE_ROOT), **kwargs)

    def log_message(self, format, *args):
        pass

class FastVibeDistHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def __init__(self, *args, **kwargs):
        target_dir = str(VIBE_FRONTEND_DIST if VIBE_FRONTEND_DIST.exists() else WORKSPACE_ROOT)
        super().__init__(*args, directory=target_dir, **kwargs)

    def log_message(self, format, *args):
        pass

def run_hub(port, handler_cls, name):
    try:
        server = ThreadingHTTPServer(("127.0.0.1", port), handler_cls)
        server.daemon_threads = True
        print(f"[{name}] Listening on http://127.0.0.1:{port}")
        server.serve_forever()
    except Exception as e:
        print(f"[{name}] Bind error on port {port}: {e}")

if __name__ == "__main__":
    t1 = threading.Thread(target=run_hub, args=(8000, FastWorkspaceHandler, "CodexHub"), daemon=True)
    t2 = threading.Thread(target=run_hub, args=(8899, FastVibeDistHandler, "VibeTradingUI"), daemon=True)
    
    t1.start()
    t2.start()
    print("Dual Threading HTTP Servers live on 8000 & 8899")
    
    t1.join()
    t2.join()
