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
