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
        if not self.describe()["configured"]:
            return {
                "message": "Add GEMINI_API_KEY to the local .env file, then try again.",
                "kind": "error",
            }
        from src.assistant import talk_to_atlas

        try:
            reply = talk_to_atlas(
                message.strip(), allow_actions=payload.get("allow_actions") is True
            )
        except Exception as exc:
            return {
                "message": f"Atlas could not complete the request ({type(exc).__name__}). Check model access and credentials.",
                "kind": "error",
            }
        return {"message": reply, "kind": "reply"}


def main():
    parser = argparse.ArgumentParser(description="Atlas desktop dashboard")
    parser.add_argument("--port", type=int, default=8010)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    serve(AtlasApplication(), root / "web", "atlas", args.port)


if __name__ == "__main__":
    main()
