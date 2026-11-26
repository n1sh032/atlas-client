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

            return {"transcript": listen_for_command() or "", "kind": "transcript"}
        message = payload.get("message")
        if not isinstance(message, str) or not message.strip() or len(message) > 4000:
            return {
                "message": "Enter a command between 1 and 4,000 characters.",
                "kind": "error",
            }
        if os.name != "nt":
            return {
                "message": "Atlas desktop actions require Windows.",
                "kind": "error",
            }
