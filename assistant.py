# the actual "brain" of atlas. this is where gemini gets told what tools it
# has and decides whether to just talk or call one of them

import json
import os

import config
from gemini_client import client

import file_tools
import system_tools
import content_tools
import calendar_tools


# telling gemini what functions it can call and what info each needs
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

# links the tool name gemini picks back to the actual function that does the thing
tool_functions = {
    "open_app": lambda query: file_tools.find_and_open_app(query),
    "close_app": lambda query: file_tools.close_app(query),
    "find_and_open_file": lambda query: file_tools.find_and_open_file(query),
    "open_last_file": lambda: file_tools.open_last_file(),
    "schedule_meeting": lambda when_text, title: calendar_tools.schedule_meeting(when_text, title),
    "google_search": lambda query: content_tools.google_search(query),
    "set_volume": lambda level: system_tools.set_volume(level),
    "set_brightness": lambda level: system_tools.set_brightness(level),
    "mute_toggle": lambda: system_tools.mute_toggle(),
    "lock_screen": lambda: system_tools.lock_screen(),
    "draft_document": lambda topic: content_tools.draft_document(topic),
    "type_in_notepad": lambda text: file_tools.type_in_notepad(text),
    "type_in_discord": lambda text: file_tools.type_in_discord(text),
    "open_downloads": lambda: file_tools.open_downloads(),
    "open_explorer": lambda: file_tools.open_explorer(),
    "skip_song": lambda: system_tools.skip_song(),
    "previous_song": lambda: system_tools.previous_song(),
    "play_pause": lambda: system_tools.play_pause(),
    "send_app_shortcut": lambda app_name, action: system_tools.send_app_shortcut(app_name, action),
}


def load_history():
    if os.path.exists(config.memory_file):
        try:
            with open(config.memory_file, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_history():
    try:
        with open(config.memory_file, "w") as f:
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
        model=config.gemini_model,
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

    if len(chat_history) > config.chat_history_cap:
        del chat_history[:2]  # dont let this grow forever

    save_history()

    if reply:
        return reply
    if did_stuff:
        return " and ".join(x.split(" -> ", 1)[1] for x in did_stuff)
    return "done"


def talk_to_atlas_safe(user_text):
    import time
    for attempt in range(3):
        try:
            return talk_to_atlas(user_text)
        except Exception as e:
            print(f"atlas: gemini's being slow, retrying... ({e})")
            time.sleep(10)
    return "cant reach gemini rn, try again in a bit"