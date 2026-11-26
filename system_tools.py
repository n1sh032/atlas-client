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
