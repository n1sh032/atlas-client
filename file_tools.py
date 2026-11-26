# stuff for opening/closing apps and files. moved out of main.py so its not
# all in one giant file

import os
import subprocess
import difflib
import time
import pygetwindow as gw
import pyautogui
import psutil

import config


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
