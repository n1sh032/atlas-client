# Atlas Client - PRD

## What this is
A JARVIS-style voice assistant for a personal Windows laptop. Wake word activated,
holds a real conversation, and can take actions on the PC on request.

## Who it's for
Just me, on my own laptop. Not a product, not multi-user, no auth/permissions system
needed beyond what's already there (Google OAuth for calendar).

## Goals (in rough order of how they got built)
1. Text-based command loop that maps typed input to actions - DONE
2. Fuzzy understanding of casual phrasing via an LLM instead of exact string matching - DONE
3. Fuzzy file search (open files without knowing exact filename/location) - DONE
4. Calendar scheduling with natural language time parsing ("tomorrow at 3pm") - DONE
5. Voice input via wake word ("hey jarvis") + speech-to-text - DONE
6. System control: volume, brightness, mute, lock screen - DONE
7. Close running apps by name - DONE
8. Web search fallback for real-time info (weather, news, etc) - DONE
9. Draft documents (emails, essays) and save as docx - DONE
10. Discord messaging via UI automation (types into whatever chat is open) - DONE
11. Multi-step commands in one sentence ("open notepad and search google for X") - DONE
12. Real conversational memory - not just command classification, actual back-and-forth
    with context retained across turns, and across restarts - DONE (rebuilt core around
    gemini tool-calling instead of text classification to achieve this)
13. Media key shortcuts (skip/pause/prev, works across spotify/youtube/etc) - DONE
14. Per-app keyboard shortcuts (save in vscode, new tab in chrome, etc) - DONE
15. Text-to-speech so it talks back instead of just printing - DONE

## Non-goals
- Not trying to support multiple users or accounts
- Not trying to be secure against adversarial input from strangers - this only ever
  receives input from me, via my own mic, on my own machine
- Not trying to browse the web autonomously or read arbitrary files/pages and act on
  their content - every tool is a specific bounded action, not general-purpose execution
- Not building a mobile app or anything cross-device, this is laptop-only

## Open ideas / not yet built
- Custom "Atlas" wake word (currently using built-in "hey jarvis" model)
- Image generation
- Screenshot + describe what's on screen
- Reading a file's contents back / summarizing it aloud
- A lighter GUI instead of a raw terminal window

## Known constraints
- Gemini free tier rate limits are small and inconsistent across models (seen anywhere
  from 20/day to much higher depending on model) - this is the main practical limitation
  on how much testing/usage this can handle without hitting quota
- Speech recognition needs internet (uses Google's free STT, not offline)
- UI-automation features (discord messaging, app shortcuts) are inherently fragile -
  they depend on window titles and focus state, will break if those change