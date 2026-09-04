import os
import subprocess
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def ask_gemini(user_text):
    prompt = f"""
You are a command parser for a desktop assistant called Atlas.
Given the user's message, respond with ONLY one of these exact words,
nothing else, no punctuation:

notepad
downloads
chrome
cmd
unknown

User message: "{user_text}"
"""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text.strip().lower()


def main():
    print("atlas is online. type exit to quit")
    while True:
        cmd = input("You: ").strip().lower()

        if cmd == "exit":
            print("shutting down")
            break

        elif cmd == "open notepad":
            subprocess.Popen(["notepad.exe"])
            print("Atlas: opening notepad")

        elif cmd == "open downloads":
            dl_path = os.path.join(os.path.expanduser("~"), "Downloads")
            os.startfile(dl_path)
            print("Atlas: opening downloads folder")

        elif cmd == "open chrome":
            subprocess.Popen([r"C:\Program Files\Google\Chrome\Application\chrome.exe"])
            print("Atlas: opening chrome")

        elif cmd == "open cmd":
            subprocess.Popen(["cmd.exe"])
            print("Atlas: opening command prompt")

        else:
            action = ask_gemini(cmd)

            if action == "notepad":
                subprocess.Popen(["notepad.exe"])
                print("Atlas: opening notepad")
            elif action == "downloads":
                dl_path = os.path.join(os.path.expanduser("~"), "Downloads")
                os.startfile(dl_path)
                print("Atlas: opening downloads folder")
            elif action == "chrome":
                subprocess.Popen([r"C:\Program Files\Google\Chrome\Application\chrome.exe"])
                print("Atlas: opening chrome")
            elif action == "cmd":
                subprocess.Popen(["cmd.exe"])
                print("Atlas: opening command prompt")
            else:
                print("Atlas: idk that command yet")


main()