import os
import subprocess
import difflib
import pickle
import json
import dateparser
import numpy as np
import sys
import time
import ctypes
import webbrowser
from urllib.parse import quote_plus
import psutil
import pygetwindow as gw
import pyautogui
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
import comtypes
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc
from docx import Document
import pyttsx3

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SCOPES = ["https://www.googleapis.com/auth/calendar"]
HISTORY_FILE = "atlas_memory.json"
def speak(text):
    print("Atlas:", text)
    engine = pyttsx3.init()
    engine.setProperty("rate", 175)
    engine.say(text)
    engine.runAndWait()
    engine.stop()

def open_notepad():
    subprocess.Popen(["notepad.exe"])
    return "opening notepad"

def type_in_notepad(text):
    subprocess.Popen(["notepad.exe"])
    time.sleep(1)
    windows = [w for w in gw.getAllTitles() if "notepad" in w.lower()]
    if not windows:
        return "couldnt focus notepad, didnt type anything"
    win = gw.getWindowsWithTitle(windows[0])[0]
    if win.isMinimized:
        win.restore()
    win.activate()
    time.sleep(1)
    active = gw.getActiveWindow()
    if not active or "notepad" not in active.title.lower():
        return "couldnt focus notepad, didnt type anything"
    pyautogui.write(text, interval=0.02)
    return f"typed in notepad: {text}"

def type_in_discord(text):
    windows = [w for w in gw.getAllTitles() if "discord" in w.lower()]
    if not windows:
        return "discord isnt open"
    win = gw.getWindowsWithTitle(windows[0])[0]
    if win.isMinimized:
        win.restore()
    win.activate()
    time.sleep(1)
    active = gw.getActiveWindow()
    if not active or "discord" not in active.title.lower():
        return "couldnt focus discord, didnt type anything"
    pyautogui.write(text, interval=0.02)
    pyautogui.press("enter")
    return f"sent to discord: {text}"

def open_camera():
    os.startfile("microsoft.windows.camera:")
    return "opening camera"

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


recent_files = []

def track_recent(filepath):
    recent_files.append(filepath)
    if len(recent_files) > 5:
        recent_files.pop(0)

def open_last_file():
    if not recent_files:
        return "i dont have a record of a recently opened file"
    last = recent_files[-1]
    os.startfile(last)
    return f"reopening {os.path.basename(last)}"


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
        return "no files to search"

    names = [n for n, p in files]
    match = difflib.get_close_matches(query, names, n=1, cutoff=0.45)
    if not match:
        return f"couldnt find anything matching '{query}'"

    for n, p in files:
        if n == match[0]:
            os.startfile(p)
            track_recent(p)
            return f"opening {n}"


def find_and_open_app(query):
    query = query.lower()
    if "spotify" in query:
        os.startfile("spotify:")
        return "opening spotify"
    if "camera" in query:
        return open_camera()

    start_menu_dirs = [
        os.path.join(os.environ["ProgramData"], "Microsoft", "Windows", "Start Menu", "Programs"),
        os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs"),
    ]

    shortcuts = []
    for d in start_menu_dirs:
        for root, dirs, files in os.walk(d):
            for f in files:
                if f.lower().endswith(".lnk"):
                    shortcuts.append((f[:-4], os.path.join(root, f)))

    if not shortcuts:
        return "cant find any installed apps"

    for n, p in shortcuts:
        if query in n.lower():
            os.startfile(p)
            return f"opening {n}"

    names = [n for n, p in shortcuts]
    match = difflib.get_close_matches(query, names, n=3, cutoff=0.5)
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

    clean = [r[:-4] if r.lower().endswith(".exe") else r for r in running]

    for orig, c in zip(running, clean):
        if query.lower() in c.lower():
            subprocess.run(["taskkill", "/IM", orig, "/F"], capture_output=True)
            return f"closed {orig}"

    match = difflib.get_close_matches(query.lower(), [c.lower() for c in clean], n=1, cutoff=0.6)
    if not match:
        return f"couldnt find a running app matching '{query}'"

    for orig, c in zip(running, clean):
        if c.lower() == match[0]:
            subprocess.run(["taskkill", "/IM", orig, "/F"], capture_output=True)
            return f"closed {orig}"


def google_search(query):
    url = f"https://www.google.com/search?q={quote_plus(query)}"
    webbrowser.open(url)
    return f"searching google for {query}"


def draft_document(topic):
    res = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=f"write the following, just the content, no preamble: {topic}"
    )
    content = res.text.strip()

    drafts_folder = os.path.join(os.path.expanduser("~"), "Documents", "atlas drafts")
    os.makedirs(drafts_folder, exist_ok=True)

    safe_name = "".join(c for c in topic if c.isalnum() or c == " ").strip()[:40]
    filepath = os.path.join(drafts_folder, f"{safe_name}.docx")

    doc = Document()
    for line in content.split("\n"):
        doc.add_paragraph(line)
    doc.save(filepath)

    os.startfile(filepath)
    track_recent(filepath)
    return f"drafted and saved: {safe_name}.docx"


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
        start = datetime.now() + timedelta(hours=1)  # couldnt parse it, just default

    end = start + timedelta(hours=1)

    event = {
        "summary": title,
        "start": {"dateTime": start.isoformat(), "timeZone": "Asia/Singapore"},
        "end": {"dateTime": end.isoformat(), "timeZone": "Asia/Singapore"},
    }

    created = service.events().insert(calendarId="primary", body=event).execute()
    return f"scheduled '{title}' for {start.strftime('%d %b, %I:%M %p')}, {created.get('htmlLink')}"


def get_volume_interface():
    comtypes.CoInitialize()  # needed or pycaw throws sometimes
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))

def set_volume(level):
    level = max(0, min(100, int(level)))
    vol = get_volume_interface()
    vol.SetMasterVolumeLevelScalar(level / 100, None)
    return f"volume set to {level}%"

def mute_toggle():
    vol = get_volume_interface()
    current = vol.GetMute()
    vol.SetMute(not current, None)
    return "muted" if not current else "unmuted"

def set_brightness(level):
    level = max(0, min(100, int(level)))
    sbc.set_brightness(level)
    return f"brightness set to {level}%"

def lock_screen():
    subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"])
    return "locking screen"


# windows media key codes, works for spotify/yt/vlc/etc, anything that
# hooks into the system media session
def media_key(key_name):
    keys = {
        "play_pause": 0xB3,
        "next": 0xB0,
        "prev": 0xB1,
        "stop": 0xB2,
    }
    if key_name not in keys:
        return "dont know that media action"

    vk = keys[key_name]
    ctypes.windll.user32.keybd_event(vk, 0, 0, 0)  # key down
    ctypes.windll.user32.keybd_event(vk, 0, 2, 0)  # key up
    return f"sent {key_name}"

def skip_song():
    return media_key("next")

def previous_song():
    return media_key("prev")

def play_pause():
    return media_key("play_pause")


# per-app keyboard shortcuts, since not everything has a media key equivalent.
# add more here as you think of ones you actually use
app_shortcuts = {
    "vscode": {
        "save": ["ctrl", "s"],
        "new file": ["ctrl", "n"],
        "close tab": ["ctrl", "w"],
        "terminal": ["ctrl", "`"],
    },
    "chrome": {
        "new tab": ["ctrl", "t"],
        "close tab": ["ctrl", "w"],
        "reopen tab": ["ctrl", "shift", "t"],
        "refresh": ["f5"],
    },
    "discord": {
        "mute mic": ["ctrl", "shift", "m"],
        "deafen": ["ctrl", "shift", "d"],
    },
}

def send_app_shortcut(app_name, action):
    app_name = app_name.lower()
    action = action.lower()

    if app_name not in app_shortcuts:
        return f"dont have shortcuts set up for {app_name}"
    if action not in app_shortcuts[app_name]:
        return f"dont know a '{action}' shortcut for {app_name}"

    windows = [w for w in gw.getAllTitles() if app_name in w.lower()]
    if not windows:
        return f"{app_name} isnt open"
    win = gw.getWindowsWithTitle(windows[0])[0]
    if win.isMinimized:
        win.restore()
    win.activate()
    time.sleep(0.5)

    pyautogui.hotkey(*app_shortcuts[app_name][action])
    return f"sent {action} in {app_name}"


# tool declarations, telling gemini what it can call and what info each needs
tools = [
    {"name": "open_app", "description": "opens an app by name eg chrome, spotify, discord",
     "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},

    {"name": "close_app", "description": "closes a running app by name",
     "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},

    {"name": "find_and_open_file", "description": "searches desktop/documents/downloads for a file and opens it",
     "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},

    {"name": "open_last_file", "description": "reopens the most recently opened file, use when user refers to 'the file i just closed' or similar",
     "parameters": {"type": "object", "properties": {}}},

    {"name": "schedule_meeting", "description": "makes a google calendar event",
     "parameters": {"type": "object", "properties": {
         "when_text": {"type": "string"}, "title": {"type": "string"}}, "required": ["when_text", "title"]}},

    {"name": "google_search", "description": "opens a google search, use for weather/news/real time stuff",
     "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},

    {"name": "set_volume", "description": "sets volume 0-100",
     "parameters": {"type": "object", "properties": {"level": {"type": "integer"}}, "required": ["level"]}},

    {"name": "set_brightness", "description": "sets brightness 0-100",
     "parameters": {"type": "object", "properties": {"level": {"type": "integer"}}, "required": ["level"]}},

    {"name": "mute_toggle", "description": "mutes/unmutes audio", "parameters": {"type": "object", "properties": {}}},
    {"name": "lock_screen", "description": "locks the pc", "parameters": {"type": "object", "properties": {}}},

    {"name": "draft_document", "description": "writes something (email/essay/letter) and saves as docx",
     "parameters": {"type": "object", "properties": {"topic": {"type": "string"}}, "required": ["topic"]}},

    {"name": "type_in_notepad", "description": "types into an already open notepad",
     "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}},

    {"name": "type_in_discord", "description": "types + sends msg in whatever discord chat is open",
     "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}},

    {"name": "open_downloads", "description": "opens downloads folder", "parameters": {"type": "object", "properties": {}}},
    {"name": "open_explorer", "description": "opens file explorer", "parameters": {"type": "object", "properties": {}}},

    {"name": "skip_song", "description": "skips to next track in whatever music app is playing (spotify, youtube, etc)",
     "parameters": {"type": "object", "properties": {}}},
    {"name": "previous_song", "description": "goes back to previous track",
     "parameters": {"type": "object", "properties": {}}},
    {"name": "play_pause", "description": "toggles play/pause on whatever music is playing",
     "parameters": {"type": "object", "properties": {}}},

    {"name": "send_app_shortcut", "description": "sends a known keyboard shortcut to a specific app, eg save in vscode, new tab in chrome, mute mic in discord",
     "parameters": {"type": "object", "properties": {
         "app_name": {"type": "string"}, "action": {"type": "string"}}, "required": ["app_name", "action"]}},
]

tool_functions = {
    "open_app": lambda query: find_and_open_app(query),
    "close_app": lambda query: close_app(query),
    "find_and_open_file": lambda query: find_and_open_file(query),
    "open_last_file": lambda: open_last_file(),
    "schedule_meeting": lambda when_text, title: schedule_meeting(when_text, title),
    "google_search": lambda query: google_search(query),
    "set_volume": lambda level: set_volume(level),
    "set_brightness": lambda level: set_brightness(level),
    "mute_toggle": lambda: mute_toggle(),
    "lock_screen": lambda: lock_screen(),
    "draft_document": lambda topic: draft_document(topic),
    "type_in_notepad": lambda text: type_in_notepad(text),
    "type_in_discord": lambda text: type_in_discord(text),
    "open_downloads": lambda: open_downloads(),
    "open_explorer": lambda: open_explorer(),
    "skip_song": lambda: skip_song(),
    "previous_song": lambda: previous_song(),
    "play_pause": lambda: play_pause(),
    "send_app_shortcut": lambda app_name, action: send_app_shortcut(app_name, action),
}


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history():
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(chat_history, f)
    except Exception as e:
        print(f"atlas: couldnt save memory ({e})")


chat_history = load_history()

# basically its personality, told to gemini once instead of stuffing it in every message
system_msg = ("you are atlas, the users desktop assistant on windows. talk casually, not robotic. "
              "only use a tool if they actually want something done on the pc, otherwise just reply normally. "
              "remember stuff from earlier in the convo, including past sessions, so you can handle follow ups "
              "like 'time it' or 'do that again' or 'what did i say about x'. "
              "keep it short, 1-3 sentences, this basically gets read out loud")

def talk_to_atlas(user_text):
    chat_history.append({"role": "user", "parts": [{"text": user_text}]})

    res = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=chat_history,
        config={"tools": [{"function_declarations": tools}], "system_instruction": system_msg},
    )

    parts = res.candidates[0].content.parts
    reply = ""
    did_stuff = []

    for p in parts:
        call = getattr(p, "function_call", None)
        if call:
            fn = call.name
            args = dict(call.args) if call.args else {}
            if fn in tool_functions:
                try:
                    r = tool_functions[fn](**args)
                except Exception as e:
                    r = f"that broke: {e}"
                did_stuff.append(f"{fn} -> {r}")

        if getattr(p, "text", None):
            reply += p.text

    chat_history.append({"role": "model", "parts": [{"text": reply or " ; ".join(did_stuff) or "ok"}]})

    if len(chat_history) > 60:
        del chat_history[:2]  # dont let this grow forever

    save_history()

    if reply:
        return reply
    if did_stuff:
        return " and ".join(x.split(" -> ", 1)[1] for x in did_stuff)
    return "done"


def talk_to_atlas_safe(user_text):
    for attempt in range(3):
        try:
            return talk_to_atlas(user_text)
        except Exception as e:
            print(f"atlas: gemini's being slow, retrying... ({e})")
            time.sleep(10)
    return "cant reach gemini rn, try again in a bit"


oww_model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")
recognizer = sr.Recognizer()
recognizer.pause_threshold = 1.8

def listen_for_wakeword():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000,
                         input=True, frames_per_buffer=1280)

    print("listening for 'hey jarvis'...")

    for _ in range(5):
        stream.read(1280)  # mic spikes on startup, throw these away

    hits = 0
    try:
        while True:
            chunk = np.frombuffer(stream.read(1280), dtype=np.int16)
            pred = oww_model.predict(chunk)
            best = max(pred.values(), default=0)

            if best > 0.9:
                hits += 1
                if hits >= 3:
                    return
            else:
                hits = 0
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()


def listen_for_command():
    with sr.Microphone() as source:
        print("listening for command...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=20)
        except sr.WaitTimeoutError:
            print("atlas: didnt hear anything, going back to sleep")
            return None

    try:
        text = recognizer.recognize_google(audio)
        print(f"heard: {text}")
        return text
    except sr.UnknownValueError:
        print("atlas: didnt catch that")
        return None
    except sr.WaitTimeoutError:
        print("atlas: didnt hear anything, going back to sleep")
        return None


def main():
    print("atlas is online (voice mode)")
    while True:
        try:
            listen_for_wakeword()
            cmd = listen_for_command()
        except KeyboardInterrupt:
            print("shutting down")
            save_history()
            break
        except Exception as e:
            print(f"atlas: listening broke ({e}), trying again")
            time.sleep(2)
            continue

        if not cmd:
            continue

        if cmd.strip().lower() == "exit":
            print("shutting down")
            save_history()
            break

        reply = talk_to_atlas_safe(cmd)
        speak(reply)


if __name__ == "__main__":
    main()