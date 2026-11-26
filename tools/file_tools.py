# stuff for opening/closing apps and files. moved out of main.py so its not
# all in one giant file

import os
import subprocess
import difflib
import time
import pygetwindow as gw
import pyautogui
import psutil

from src import config

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


# tracks files atlas has opened so "open the file i just closed" kinda works.
# only knows about stuff opened through atlas, not files you opened yourself
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
    match = difflib.get_close_matches(query, names, n=1, cutoff=config.file_match_cutoff)
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

    # substring check first, way more reliable than fuzzy for app names
    for n, p in shortcuts:
        if query in n.lower():
            os.startfile(p)
            return f"opening {n}"

    names = [n for n, p in shortcuts]
    match = difflib.get_close_matches(query, names, n=3, cutoff=config.app_open_cutoff)
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

    match = difflib.get_close_matches(query.lower(), [c.lower() for c in clean], n=1, cutoff=config.app_close_cutoff)
    if not match:
        return f"couldnt find a running app matching '{query}'"

    for orig, c in zip(running, clean):
        if c.lower() == match[0]:
            subprocess.run(["taskkill", "/IM", orig, "/F"], capture_output=True)
            return f"closed {orig}"