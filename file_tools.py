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
