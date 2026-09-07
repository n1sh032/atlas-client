# Atlas Client

Voice-controlled desktop assistant for Windows, inspired by JARVIS. Say "hey jarvis" to
wake it up, then talk to it normally — it can hold a conversation, remember context,
and take actions on the PC when asked.

## Stack
- Python 3.14
- Gemini API (`gemini-2.5-flash` currently, swap models if rate limited) for conversation + tool calling
- `openwakeword` for the wake word ("hey jarvis" built-in model, onnx runtime)
- `SpeechRecognition` + Google's free STT for voice-to-text
- `pyttsx3` for text-to-speech (reinit engine per call, see note below)
- Google Calendar API for scheduling
- `pycaw`, `screen_brightness_control`, `psutil`, `pygetwindow`, `pyautogui` for system control

## How it works
1. `listen_for_wakeword()` blocks until "hey jarvis" is heard (3 consecutive high-confidence hits)
2. `listen_for_command()` records and transcribes what you say next
3. `talk_to_atlas()` sends the text + full chat history to Gemini with a list of `tools`
   (function declarations) — Gemini decides whether to reply in plain text, call a function,
   or both
4. Whatever Gemini calls gets run via `tool_functions`, a dict mapping tool name -> real
   python function
5. Conversation history is saved to `atlas_memory.json` after every exchange, so it persists
   across restarts (not just within one session)

## Known gotchas
- `pyaudio` fails to build on Windows without a C++ compiler — use `pyaudiowpatch` instead,
  and shim it into `sys.modules["pyaudio"]` before importing `speech_recognition`, since that
  library hardcodes `import pyaudio`
- `pyttsx3`'s SAPI5 driver on Windows breaks after the first `runAndWait()` if you reuse one
  engine instance — `speak()` creates a fresh engine every call to work around this
- Gemini model names get deprecated fast (already been through 2.0-flash, 2.5-flash-lite,
  gemini-3.1-flash, gemini-3-flash-preview in this project's lifetime) — if you get a 404
  NOT_FOUND, check current available models before assuming the code is broken
- Free tier rate limits vary a lot by model, sometimes as low as 20 requests/day — check
  https://ai.dev/rate-limit if things start throwing 429 errors
- `token.pickle`, `credentials.json`, `.env`, and `atlas_memory.json` must never be committed
  — check `.gitignore` before every push if working on anything auth/memory related

## Adding a new capability
1. Write a normal python function that does the thing, return a short string describing
   what happened
2. Add a matching entry to the `tools` list (name, description, parameters) so Gemini knows
   it exists and when to use it
3. Add a matching entry to `tool_functions` mapping the tool name to the actual function
4. That's it — no prompt engineering needed beyond the tool description, Gemini handles
   routing itself now (this replaced an earlier text-classification approach, see design.md)