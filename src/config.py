import os
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).resolve().parents[1]
load_dotenv(project_root / ".env")
gemini_model = os.getenv("ATLAS_GEMINI_MODEL", "gemini-3.6-flash")
draft_model = "gemini-3.1-flash-lite"   # used just for draft_document, dont need tool calling for that

timezone = "Asia/Singapore"

# wake word stuff
wake_threshold = 0.9      # how confident it needs to be to count as a hit
wake_hits_needed = 3      # needs this many hits in a row or it kept false triggering on noise

# mic stuff
mic_pause_threshold = 1.8   # bumped this up bc it kept cutting me off mid sentence
mic_timeout = 5             # how long it waits for you to start talking
mic_phrase_limit = 20       # max length of one command

# fuzzy match cutoffs, tuned these by just testing till they stopped being dumb
file_match_cutoff = 0.45
app_open_cutoff = 0.5
app_close_cutoff = 0.6   # higher bc closing the wrong app is way more annoying than opening one

# tts
tts_rate = 175
tts_voice_index = None   # set this after checking voices, see readme

chat_history_cap = 60
memory_file = str(project_root / "atlas_memory.json")

drafts_folder = "atlas drafts"
