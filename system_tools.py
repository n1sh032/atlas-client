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