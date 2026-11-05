import threading
import json
import secrets
import urllib.request
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit

from wink_private_model import build_state, update_asset

WORKSPACE_ROOT = Path("C:/Users/ACER/Documents/Codex/revenue-copilot-international-phase0")
VIBE_FRONTEND_DIST = Path("C:/Users/ACER/AppData/Local/MaiVibeTrading/Vibe-Trading/frontend/dist")
PRIVATE_PAGE = WORKSPACE_ROOT / "tools" / "wink_private_dashboard.html"
PRIVATE_CSRF = secrets.token_urlsafe(32)
AGENT_ZERO_TASKS = Path.home() / "agent-zero" / "agent-zero" / "usr" / "scheduler" / "tasks.json"


def agent_zero_status():
    """Read-only status; no commands, prompts, tokens or private data sent to Agent Zero."""
    try:
        with urllib.request.urlopen("http://127.0.0.1:5080", timeout=1) as response:
            reachable = response.status < 500
    except Exception:
        reachable = False
    try:
        tasks = json.loads(AGENT_ZERO_TASKS.read_text(encoding="utf-8")).get("tasks", [])
        scheduled = len(tasks)
        enabled = sum(t.get("state") not in {"disabled", "paused"} for t in tasks)
    except (OSError, ValueError, TypeError):
        scheduled = enabled = None
    return {"url": "http://127.0.0.1:5080", "reachable": reachable,
            "scheduled_tasks": scheduled, "enabled_tasks": enabled,
            "note": "WINK chỉ hiển thị trạng thái và mở giao diện Agent Zero; chưa nối lệnh hay chia sẻ dữ liệu tài chính."}

class FastWorkspaceHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WORKSPACE_ROOT), **kwargs)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path in {"/dashboard", "/dashboard/", "/api/private/state"}:
            if not self._private_allowed():
                self.send_error(403)
                return
            if path in {"/dashboard", "/dashboard/"}:
                page = PRIVATE_PAGE.read_text(encoding="utf-8").replace("__CSRF_TOKEN__", PRIVATE_CSRF)
                self._reply(200, page.encode("utf-8"), "text/html; charset=utf-8")
            else:
                state = build_state()
                state["agent_zero"] = agent_zero_status()
                self._reply(200, json.dumps(state, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")
            return
        if path in {"/", "/index.html", "/legacy"}:
            page = (WORKSPACE_ROOT / "index.html").read_text(encoding="utf-8")
            old_link = '<a class="btn-venture" href="https://winkhere.com/" target="_blank" rel="noopener">Truy Cập winkhere.com &rarr;</a>'
            private_link = '<a class="btn-venture" href="/dashboard" rel="nofollow">Bảng tài sản riêng &rarr;</a> '
            if old_link in page:
                page = page.replace(old_link, private_link + old_link, 1)
            self._reply(200, page.encode("utf-8"), "text/html; charset=utf-8")
            return
        super().do_GET()

    def do_POST(self):
        if urlsplit(self.path).path != "/api/private/holdings":
            self.send_error(404)
            return
        if not self._private_allowed() or self.headers.get("Origin") not in {"http://127.0.0.1:8000", "http://localhost:8000"}:
            self.send_error(403)
            return
        if self.headers.get("X-WINK-CSRF") != PRIVATE_CSRF:
            self.send_error(403)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 2 or length > 2048:
                raise ValueError("Kích thước yêu cầu không hợp lệ")
            data = json.loads(self.rfile.read(length))
            update_asset(str(data.get("id", "")), data.get("quantity"), data.get("cost"), data.get("asof"))
            self._reply(200, b'{"ok":true}', "application/json")
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self._reply(400, json.dumps({"error": str(exc)}, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def _private_allowed(self):
        return self.client_address[0] in {"127.0.0.1", "::1"} and self.headers.get("Host") in {"127.0.0.1:8000", "localhost:8000"}

    def _reply(self, status: int, body: bytes, content_type: str):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.end_headers()
        self.wfile.write(body)

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
