import argparse
import os
from pathlib import Path

from src.web_runtime import serve


class AtlasApplication:
    actions = {"chat", "listen"}

    def describe(self):
        from dotenv import load_dotenv

        load_dotenv()
        return {
            "name": "Atlas",
            "configured": bool(os.getenv("GEMINI_API_KEY")),
            "platform": os.name,
        }

    def execute(self, action, payload):
        if action == "listen":
            from src.voice import listen_for_command

