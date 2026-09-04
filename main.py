import os
import subprocess
import difflib
import pickle
import dateparser
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google import genai
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SCOPES = ["https://www.googleapis.com/auth/calendar"]


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

def find_and_open_file(query):
    folders = [
        os.path.join(os.path.expanduser("~"), "Desktop"),
        os.path.join(os.path.expanduser("~"), "Documents"),
        os.path.join(os.path.expanduser("~"), "Downloads"),
    ]

    files = []
    for f in folders:
        if not os.path.exists(f):
            continue
        for name in os.listdir(f):
            full = os.path.join(f, name)
            if os.path.isfile(full):
                files.append((name, full))

    if not files:
        return "no files found to search"

    names = [n for n, p in files]
    match = difflib.get_close_matches(query, names, n=1, cutoff=0.3)

    if not match:
        return f"couldnt find anything matching '{query}'"

    for n, p in files:
        if n == match[0]:
            os.startfile(p)
            return f"opening {n}"


def get_calendar_service():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as f:
            pickle.dump(creds, f)

    return build("calendar", "v3", credentials=creds)


def schedule_meeting(when_text, title):
    service = get_calendar_service()

    start = dateparser.parse(when_text)
    if not start:
        # couldnt figure out the time, just default to 1hr from now
        start = datetime.now() + timedelta(hours=1)

    end = start + timedelta(hours=1)

    event = {
        "summary": title,
        "start": {"dateTime": start.isoformat(), "timeZone": "Asia/Singapore"},
        "end": {"dateTime": end.isoformat(), "timeZone": "Asia/Singapore"},
    }

    created = service.events().insert(calendarId="primary", body=event).execute()
    return f"scheduled '{title}' for {start.strftime('%d %b, %I:%M %p')}, check calendar: {created.get('htmlLink')}"


actions = {
    "notepad": open_notepad,
    "downloads": open_downloads,
    "chrome": open_chrome,
    "cmd": open_cmd,
    "spotify": open_spotify,
    "vscode": open_vscode,
    "explorer": open_explorer,
}

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
if user wants to open an app, reply with ONLY one word from this list:

{opts}
open_file
schedule_meeting
unknown

if its open_file, reply like this instead:
open_file: <short search term for the file>

if its schedule_meeting, reply like this instead:
schedule_meeting: <when they said, keep it natural, eg "tomorrow at 3pm">|<short title for the meeting>

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

        if action.startswith("open_file:"):
            query = action.split(":", 1)[1].strip()
            print("Atlas:", find_and_open_file(query))
        elif action.startswith("schedule_meeting:"):
            details = action.split(":", 1)[1].strip()
            when_text, title = details.split("|", 1)
            print("Atlas:", schedule_meeting(when_text.strip(), title.strip()))
        elif action in actions:
            print("Atlas:", actions[action]())
        else:
            print("Atlas: idk that command yet")


main()