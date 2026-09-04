import os
import subprocess
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def open_notepad():
    subprocess.Popen(["notepad.exe"])
    return "opening notepad"

def open_downloads():
    dl_path = os.path.join(os.path.expanduser("~"), "Downloads")
    os.startfile(dl_path)
    return "opening downloads folder"

def open_chrome():
    subprocess.Popen([r"C:\Program Files\Google\Chrome\Application\chrome.exe"])
    return "opening chrome"

def open_cmd():
    subprocess.Popen(["cmd.exe"])
    return "opening cmd"

def open_spotify():
    os.startfile("spotify:")
    return "opening spotify"

def open_vscode():
    subprocess.Popen(["code"])
    return "opening vscode"

def open_explorer():
    os.startfile(os.path.expanduser("~"))
    return "opening file explorer"


# action name -> function
actions = {
    "notepad": open_notepad,
    "downloads": open_downloads,
    "chrome": open_chrome,
    "cmd": open_cmd,
    "spotify": open_spotify,
    "vscode": open_vscode,
    "explorer": open_explorer,
}

# exact phrases so it doesnt need to call gemini every time
exact = {
    "open notepad": "notepad",
    "open downloads": "downloads",
    "open chrome": "chrome",
    "open cmd": "cmd",
    "open spotify": "spotify",
    "open vscode": "vscode",
    "open explorer": "explorer",
}


def ask_gemini(text):
    opts = "\n".join(actions.keys())
    prompt = f"""you are a command parser for atlas.
reply with ONLY one word from this list, nothing else:

{opts}
unknown

message: "{text}"
"""
    res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return res.text.strip().lower()


def main():
    print("atlas is online. type exit to quit")
    while True:
        cmd = input("You: ").strip().lower()

        if cmd == "exit":
            print("shutting down")
            break

        if cmd in exact:
            action = exact[cmd]
        else:
            action = ask_gemini(cmd)

        if action in actions:
            print("Atlas:", actions[action]())
        else:
            print("Atlas: idk that command yet")


main()