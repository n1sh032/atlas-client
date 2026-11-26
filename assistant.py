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

