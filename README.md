# Atlas Client

Atlas is a Windows voice assistant. Say **Hey Jarvis**, then give it one command. It can open apps, type into Notepad or Discord, control media and some Windows settings, create Word drafts, schedule calendar events, and answer questions with Gemini.

## Requirements

- Windows desktop session with a microphone and speakers.
- Python 3.14, the version documented for this project. The pinned dependency set includes Windows-specific packages.
- Internet access for Google Speech Recognition and Gemini, and a Gemini API key with access to the model configured in [src/config.py](src/config.py).
- Google Calendar OAuth credentials if you want to use calendar commands.

## Setup

From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create a private `.env` file in the repository root:

```text
GEMINI_API_KEY=your_gemini_api_key
```

For calendar commands, enable the Google Calendar API in your Google Cloud project and create an OAuth **Desktop app** client. Save its downloaded client file as `credentials.json` in the repository root. The first calendar command prompts you to authorize access and saves it in `token.pickle`. Keep both credential files, `.env`, and `atlas_memory.json` private.

## Run and try it

```powershell
.\.venv\Scripts\python.exe -m src.main
```

Say **Hey Jarvis**, wait for Atlas to listen, then try **“Open Notepad”** or **“What time is it?”** The recording limit is 20 seconds once you start speaking. Say **“exit”** after the wakeword or press Ctrl+C to quit.

Other examples:

- **“Type in Notepad saying the first point is …”** Atlas checks the target window before typing. Discord needs an open chat.
- **“Close Notepad”** uses the exact process name and requests a graceful close of a single visible window. You may see a save prompt.
- **“Set brightness to 60”** depends on the display and Windows drivers.
- **“Draft an email asking for a project update”** saves a Word file in `Documents\atlas drafts`.
- **“Schedule a meeting tomorrow at 3 PM called project review”** creates an event after Calendar has been authorized.

## How it works

openWakeWord listens for the wakeword. After a trigger, Google Speech Recognition transcribes the command. Gemini selects an available action or replies in text. Atlas reports the actual tool outcome when it runs an action and speaks it with `pyttsx3`. Conversation history stays in a local JSON file and is reused as context for Gemini requests. A transient Gemini error can retry the model call before the desktop action runs.

## Working proof and troubleshooting

The assistant regression test passed with simulated Gemini and desktop actions. It checks that a transient retry produces one command in history, invokes the action once, and reports the actual action result. Python compilation also passed. The test does not exercise a physical microphone, live Gemini, or Windows UI actions.

```powershell
.\.venv\Scripts\python.exe -m pip install pytest
.\.venv\Scripts\python.exe -m pytest -q test/test_assistant.py
.\.venv\Scripts\python.exe -m compileall -q src tools
```

If Atlas misses the wakeword, check the default microphone and Windows microphone permissions, then run `.\.venv\Scripts\python.exe -m test.wake_test` from the root. If speech works but Gemini fails, check the API key, model access, and quota. If an action fails, try it directly in Windows to check that your desktop session and device support it.

See [design notes](docs/DESIGN.md) for the module layout.
