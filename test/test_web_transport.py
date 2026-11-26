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
