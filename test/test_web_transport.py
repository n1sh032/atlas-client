import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def test_local_transport_validates_origin_and_serializes_actions():
    root = Path(__file__).resolve().parents[1]
    code = """
from pathlib import Path
from src.web_runtime import serve
import time
class App:
    actions = {"echo"}
    def describe(self): return {"name": "test"}
    def execute(self, action, payload):
        time.sleep(0.3)
        return payload
serve(App(), Path("web"), "test", 0)
"""
    process = subprocess.Popen(
        [sys.executable, "-u", "-c", code], cwd=root, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, text=True,
    )
    try:
        address = process.stdout.readline().strip().removeprefix("Open ")
        port = address.rsplit(":", 1)[1]
        host = "test.localhost:" + port
        base = "http://127.0.0.1:" + port

        def request(path, body=None, origin=None):
            headers = {"Host": host}
            if origin:
                headers["Origin"] = origin
            data = None if body is None else json.dumps(body).encode()
            req = Request(base + path, data=data, headers=headers)
            try:
                response = urlopen(req, timeout=5)
            except HTTPError as exc:
                response = exc
            with response:
                return response.status, response.read()

        assert request("/")[0] == 200
        action = {"action": "echo", "payload": {"message": "checked"}}
        assert request("/api/actions", action, "http://other.example")[0] == 403
        assert request("/api/actions", {"action": "unknown"}, address)[0] == 400
        assert request("/api/actions", action, address)[0] == 202
        assert request("/api/actions", action, address)[0] == 409
        for _ in range(30):
            state = json.loads(request("/api/state")[1])
            if not state["busy"]:
                break
            time.sleep(0.05)
        assert state["result"] == {"message": "checked"}
    finally:
        process.terminate()
        process.communicate(timeout=5)
