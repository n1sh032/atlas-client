# Agent instructions for Atlas Client

If you're an AI agent (Claude Code, Cursor, Copilot, etc) working in this repo, some rules:

## Code style
- Casual, not textbook. lowercase variable names, minimal docstrings, comments that sound
  like a person's actual reasoning ("this breaks if X" not "this function handles X").
  This is a personal/student project, not a library — don't over-formalize it.
- Don't add type hints, docstrings-on-every-function, or heavy abstraction unless asked.
  Keep functions short and readable over "clean architecture."

## Before making changes
- Read CLAUDE.md first for project context and known gotchas
- Check .gitignore includes .env, token.pickle, credentials.json, atlas_memory.json before
  touching anything related to auth or memory — these have leaked before, be paranoid about it
- If changing the model name, check it's actually available first (search, don't assume) —
  Gemini model names get deprecated often, this project has hit 404s from this multiple times

## When adding a new tool/action
- Follow the pattern in main.py: plain function -> entry in `tools` list -> entry in
  `tool_functions` dict. Don't reintroduce text-based command parsing (action.startswith(...))
  — that was the old architecture before the tool-calling rebuild, it's intentionally gone.
- Functions should return a short string describing what happened, not print directly —
  the caller (talk_to_atlas / speak) handles output

## Never do
- Never add a generic "run this shell command" or "execute arbitrary code" tool. Every tool
  should be a specific, bounded action (open app, set volume, etc), not a general execution
  primitive. This is a deliberate security boundary, not an oversight — don't remove it even
  if asked to add flexibility.
- Never commit secrets. If a push gets blocked by GitHub secret scanning, fix it by removing
  the secret from history (amend if it's the last commit) — don't force-push over it blindly.
- Don't silently swap pyaudio back to the plain `pyaudio` package — it doesn't build on this
  machine, pyaudiowpatch is intentional.