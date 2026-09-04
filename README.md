# Atlas Client

Atlas is a Windows voice desktop assistant. Say **Hey Jarvis**, speak a command, and Atlas can open applications, control system settings, search Google, use Google Calendar, type into Notepad or Discord, control media, draft Word documents, and answer general questions with Gemini.

## Requirements

- Windows 10 or Windows 11
- Python 3.10 or newer
- A working microphone and speakers
- A Gemini API key
- Google Calendar OAuth credentials if calendar commands are used

The assistant uses Windows-specific packages and will not run unchanged on macOS or Linux.

## Setup

Open PowerShell in this folder and create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
pip install google-genai python-dotenv numpy psutil pygetwindow pyautogui pyaudiowpatch SpeechRecognition dateparser google-auth-oauthlib google-api-python-client openwakeword onnxruntime pycaw comtypes screen-brightness-control python-docx pyttsx3
```

If PowerShell blocks activation, run this once in an administrator PowerShell window or use the virtual environment's Python directly:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### Gemini API key

Create a file named `.env` beside `main.py`:

```text
GEMINI_API_KEY=your_gemini_api_key
```

Keep this file private. Do not commit API keys to Git.

### Google Calendar

1. Create or select a project in Google Cloud.
2. Enable the Google Calendar API.
3. Create an OAuth desktop-app client and download its JSON file.
4. Save it as `credentials.json` beside `main.py`.
5. On the first calendar command, complete the browser authorization flow.

Atlas stores the resulting authorization token in `token.pickle`. Keep both credential files private.

## Run Atlas

```powershell
python main.py
```

The program waits quietly for the wakeword. After detecting **Hey Jarvis**, it listens for one command for up to 20 seconds. Say `exit` after the wakeword to stop the program.

To test wakeword detection without running the assistant actions:

```powershell
python wake_test.py
```

## Example commands

### Applications and files

- “Open Notepad”
- “Open Camera”
- “Open Spotify”
- “Close Discord”
- “Open the budget spreadsheet”
- “Open my Downloads folder”

### Typing

- “Type in Notepad saying the first point is …”
- “The second point is …” to append to the existing Notepad document
- “Type hello in Discord”

Atlas checks that the target window is focused before typing. Discord must already be open and have a chat ready; Atlas does not choose a server or channel.

### Search and questions

- “Search Google for weather in Singapore”
- “Open WhatsApp on Google”
- “What time is it?”
- “Explain photosynthesis briefly”

### System controls

- “Put my volume to 100”
- “Set brightness to 60”
- “Mute”
- “Lock my screen”

### Calendar and documents

- “Schedule a meeting tomorrow at 3 PM called project review”
- “Draft an email asking for a project update”

Drafts are saved as `.docx` files in `Documents\atlas drafts`.

### Media and shortcuts

- “Skip the song”
- “Play pause”
- “Save in VS Code”
- “Open a new tab in Chrome”
- “Mute my mic in Discord”

Shortcuts are limited to the applications and actions configured in `main.py`.

## How it works

1. `openwakeword` continuously monitors the microphone for **Hey Jarvis**.
2. SpeechRecognition records the command and sends it to Google Speech Recognition.
3. Gemini selects a tool or produces a conversational answer.
4. Atlas runs the Windows action and reads the result aloud with `pyttsx3`.
5. Conversation history is saved locally in `atlas_memory.json` and reused for follow-up questions.

Transient Gemini failures are retried three times. Listening and action errors are reported and the assistant returns to its wakeword loop instead of exiting.

## Troubleshooting

### Atlas does not hear the wakeword

- Check that Windows has granted microphone access to Python or VS Code.
- Confirm the intended microphone is the Windows default input device.
- Run `wake_test.py` to check wakeword detection separately.
- Speak clearly and wait for Atlas to finish saying it is listening.

### Long commands are cut off

The current recording limit is 20 seconds. Long pauses are allowed up to the recognizer's configured pause threshold. For commands longer than that, split the text into multiple Notepad points.

### Typing goes to the wrong application

Atlas activates the matching window and verifies its title before typing. Make sure the target app is open and visible. For Discord, keep the desired chat selected before speaking.

### Volume or brightness commands fail

These controls depend on Windows hardware and drivers. Run Atlas from a normal desktop session, confirm Windows itself can change the setting, and check that all packages installed in the active virtual environment.

### Gemini credits or quota are exhausted

Atlas retries temporary API failures and then returns to listening. Retries cannot bypass an exhausted quota; wait for the quota window to reset or use an API project with available billing/quota.

## Project files

| File | Purpose |
| --- | --- |
| `main.py` | Assistant, voice loop, Gemini tools, and Windows actions |
| `wake_test.py` | Standalone wakeword detector test |
| `.env` | Local Gemini API key; keep private |
| `credentials.json` | Google Calendar OAuth client; keep private |
| `token.pickle` | Cached Google Calendar authorization; keep private |
| `atlas_memory.json` | Local conversation history |
