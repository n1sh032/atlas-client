# volume, brightness, lock screen, media keys, app specific keyboard shortcuts.
# basically anything that controls the pc itself rather than opening/closing stuff

import subprocess
import time
import ctypes
import comtypes
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc
import pygetwindow as gw
import pyautogui


