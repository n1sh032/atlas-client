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
