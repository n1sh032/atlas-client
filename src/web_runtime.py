"""Loopback web transport. Application operations run on one worker."""

import json
import logging
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock

logger = logging.getLogger(__name__)
ASSETS = {
    "/": ("index.html", "text/html"),
    "/app.js": ("app.js", "text/javascript"),
    "/style.css": ("style.css", "text/css"),
}


def serve(application, assets, name, port):
    worker = ThreadPoolExecutor(max_workers=1)
    lock = Lock()
    state = {"busy": False, "result": None, "error": None, "revision": 0}
    allowed = {f"{name}.localhost:{port}", f"127.0.0.1:{port}"}

    def run(action, payload):
        try:
            result = application.execute(action, payload)
            with lock:
                state.update(result=result, error=None)
        except (ValueError, OSError) as exc:
            with lock:
                state.update(error=str(exc))
        except Exception:
            logger.exception("Application operation failed")
            with lock:
                state.update(error="Operation failed. Check the terminal for details.")
        finally:
            with lock:
                state["busy"] = False
                state["revision"] += 1

    class Handler(BaseHTTPRequestHandler):
        def reply(self, status, value):
            body = json.dumps(value).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def valid_host(self):
            return self.headers.get("Host") in allowed

        def do_GET(self):
            if not self.valid_host():
                self.reply(403, {"error": "Use the address printed by the app."})
                return
            if self.path == "/api/state":
                with lock:
                    value = dict(state)
                value["application"] = application.describe()
                self.reply(200, value)
                return
            asset = ASSETS.get(self.path)
            if asset is None:
                self.reply(404, {"error": "Page not found"})
                return
            filename, kind = asset
            body = (assets / filename).read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", kind + "; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            self.connection.settimeout(10)
            if not self.valid_host() or self.headers.get(
                "Origin"
            ) != "http://" + self.headers.get("Host", ""):
                self.reply(403, {"error": "Requests must come from this app."})
