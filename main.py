import os
import subprocess
import difflib
import pickle
import dateparser
import numpy as np
import sys
import webbrowser
import psutil
import pyaudiowpatch as pyaudio
sys.modules["pyaudio"] = pyaudio
import speech_recognition as sr
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google import genai
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from openwakeword.model import Model
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc
from docx import Document

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

def open_cmd():
    subprocess.Popen(["cmd.exe"])
    return "opening cmd"

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


def find_and_open_app(query):
    if "spotify" in query:
        os.startfile("spotify:")
        return "opening spotify"

    start_menu_dirs = [
        os.path.join(os.environ["ProgramData"], "Microsoft", "Windows", "Start Menu", "Programs"),
        os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs"),
    ]

    shortcuts = []
    for d in start_menu_dirs:
        for root, dirs, files in os.walk(d):
            for f in files:
                if f.lower().endswith(".lnk"):
                    name = f[:-4]
                    shortcuts.append((name, os.path.join(root, f)))

    if not shortcuts:
        return "couldnt find any installed apps"

    for n, p in shortcuts:
        if query in n.lower():
            os.startfile(p)
            return f"opening {n}"

    names = [n for n, p in shortcuts]
    match = difflib.get_close_matches(query, names, n=3, cutoff=0.6)

    if not match:
        return f"couldnt find an app matching '{query}'"

    best = match[0]
    for n, p in shortcuts:
        if n == best:
            os.startfile(p)
            return f"opening {n}"


def close_app(query):
    running = []
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            running.append(proc.info["name"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    running_clean = [r[:-4] if r.lower().endswith(".exe") else r for r in running]

    for original, clean in zip(running, running_clean):
        if query in clean.lower():
            subprocess.run(["taskkill", "/IM", original, "/F"], capture_output=True)
            return f"closed {original}"

    match = difflib.get_close_matches(query, [c.lower() for c in running_clean], n=1, cutoff=0.6)
    if not match:
        return f"couldnt find a running app matching '{query}'"

    for original, clean in zip(running, running_clean):
        if clean.lower() == match[0]:
            subprocess.run(["taskkill", "/IM", original, "/F"], capture_output=True)
            return f"closed {original}"


def google_search(query):
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"searching google for {query}"


def ask_gemini_general(query):
    res = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=f"answer briefly and conversationally, 1-2 sentences max: {query}"
    )
    return res.text.strip()


def draft_document(topic):
    res = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=f"write the following, just the content, no preamble or explanation: {topic}"
    )
    content = res.text.strip()

    drafts_folder = os.path.join(os.path.expanduser("~"), "Documents", "atlas drafts")
    os.makedirs(drafts_folder, exist_ok=True)

    safe_name = "".join(c for c in topic if c.isalnum() or c == " ").strip()[:40]
    filename = f"{safe_name}.docx"
    filepath = os.path.join(drafts_folder, filename)

    doc = Document()
    for line in content.split("\n"):
        doc.add_paragraph(line)
    doc.save(filepath)

    os.startfile(filepath)
    return f"drafted and saved: {filename}"


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
        start = datetime.now() + timedelta(hours=1)

    end = start + timedelta(hours=1)

    event = {
        "summary": title,
        "start": {"dateTime": start.isoformat(), "timeZone": "Asia/Singapore"},
        "end": {"dateTime": end.isoformat(), "timeZone": "Asia/Singapore"},
    }

    created = service.events().insert(calendarId="primary", body=event).execute()
    return f"scheduled '{title}' for {start.strftime('%d %b, %I:%M %p')}, check calendar: {created.get('htmlLink')}"


def get_volume_interface():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))

def set_volume(level):
    vol = get_volume_interface()
    vol.SetMasterVolumeLevelScalar(level / 100, None)
    return f"volume set to {level}%"

def mute_toggle():
    vol = get_volume_interface()
    current = vol.GetMute()
    vol.SetMute(not current, None)
    return "muted" if not current else "unmuted"

def set_brightness(level):
    sbc.set_brightness(level)
    return f"brightness set to {level}%"

def lock_screen():
    subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"])
    return "locking screen"


actions = {
    "notepad": open_notepad,
    "downloads": open_downloads,
    "cmd": open_cmd,
    "explorer": open_explorer,
    "lock_screen": lock_screen,
    "mute": mute_toggle,
}

exact = {
    "open notepad": "notepad",
    "open downloads": "downloads",
    "open cmd": "cmd",
    "open explorer": "explorer",
    "lock my screen": "lock_screen",
    "mute": "mute",
}


def ask_gemini(text):
    opts = "\n".join(actions.keys())
    prompt = f"""you are a command parser for atlas.
if user wants one of these specific things, reply with ONLY one word from this list:

{opts}
open_file
open_app
close_app
schedule_meeting
set_volume
set_brightness
unknown

if its open_file, reply like this instead:
open_file: <short search term for the file>

if its open_app, reply like this instead:
open_app: <name of the app>

if its closing/killing an app, reply like this:
close_app: <name of the app>

if its schedule_meeting, reply like this instead:
schedule_meeting: <when they said, eg "tomorrow at 3pm">|<short title for the meeting>

if its a web search request, or asking about something real-time/current
(weather, news, prices, scores, "whats the time in X" etc), reply like this:
search: <search term>

if its a general knowledge question you can just answer directly
(not needing live info, not an app command), reply like this:
answer: <the original question>

if its setting volume, reply like this:
set_volume: <number 0-100>

if its setting brightness, reply like this:
set_brightness: <number 0-100>

if user wants something written/drafted (email, essay, message, letter, etc), reply like this:
draft: <what they want written, keep their original request/topic intact>

message: "{text}"
"""
    res = client.models.generate_content(model="gemini-3.1-flash-lite", contents=prompt)
    return res.text.strip().lower()


oww_model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")
recognizer = sr.Recognizer()

def listen_for_wakeword():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000,
                         input=True, frames_per_buffer=1280)

    print("listening for 'hey jarvis'...")

    for _ in range(5):
        stream.read(1280)

    while True:
        chunk = np.frombuffer(stream.read(1280), dtype=np.int16)
        prediction = oww_model.predict(chunk)

        for wakeword, score in prediction.items():
            if score > 0.7:
                stream.stop_stream()
                stream.close()
                audio.terminate()
                return


def listen_for_command():
    with sr.Microphone() as source:
        print("listening for command...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)

    try:
        text = recognizer.recognize_google(audio)
        print(f"heard: {text}")
        return text.lower()
    except sr.UnknownValueError:
        print("atlas: didnt catch that")
        return None
    except sr.WaitTimeoutError:
        print("atlas: no command heard, going back to sleep")
        return None


def main():
    print("atlas is online (voice mode)")
    while True:
        listen_for_wakeword()
        cmd = listen_for_command()

        if not cmd:
            continue

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
        elif action.startswith("open_app:"):
            query = action.split(":", 1)[1].strip()
            print("Atlas:", find_and_open_app(query))
        elif action.startswith("close_app:"):
            query = action.split(":", 1)[1].strip()
            print("Atlas:", close_app(query))
        elif action.startswith("schedule_meeting:"):
            details = action.split(":", 1)[1].strip()
            when_text, title = details.split("|", 1)
            print("Atlas:", schedule_meeting(when_text.strip(), title.strip()))
        elif action.startswith("search:"):
            query = action.split(":", 1)[1].strip()
            print("Atlas:", google_search(query))
        elif action.startswith("answer:"):
            query = action.split(":", 1)[1].strip()
            print("Atlas:", ask_gemini_general(query))
        elif action.startswith("set_volume:"):
            level = int(action.split(":", 1)[1].strip())
            print("Atlas:", set_volume(level))
        elif action.startswith("set_brightness:"):
            level = int(action.split(":", 1)[1].strip())
            print("Atlas:", set_brightness(level))
        elif action.startswith("draft:"):
            topic = action.split(":", 1)[1].strip()
            print("Atlas:", draft_document(topic))
        elif action in actions:
            print("Atlas:", actions[action]())
        else:
            print("Atlas: idk that command yet")


main()