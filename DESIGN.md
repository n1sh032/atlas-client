# Atlas Client - Design notes

## Architecture history (why it looks the way it does)

Started as a simple text loop -> if/elif command matching -> dict-based command router
(action name -> function) -> added an LLM as a fallback classifier that returned strings
like `open_file: resume` which got parsed with `.startswith()` -> eventually this got
messy (every new feature needed a new prompt section + a new parsing branch, and it had
no real memory of the conversation) -> rebuilt the core around actual LLM tool calling.

The current architecture is NOT the text-classification one. Don't reintroduce
`action.startswith("something:")` style parsing - that pattern is intentionally retired.

## Current flow