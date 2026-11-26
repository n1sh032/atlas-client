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


