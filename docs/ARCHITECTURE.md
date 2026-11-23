# Architecture and development

UI: `web/` contains the conversation and command form. Transport: `src/web_runtime.py` accepts same-origin local requests and runs one operation on a worker. Application: `src/web.py` validates commands and loads voice or assistant dependencies when needed. Domain behavior: `src/assistant.py` owns Gemini turns, `tools/` owns bounded desktop capabilities, and `src/voice.py` owns microphone and TTS access.

Run `python -m src.web` from the repository root. Open `http://atlas.localhost:8010`. Text input works without activating the wakeword loop. Use microphone captures one command into the text field, where it can be reviewed before sending. Desktop actions are disabled in the browser until explicitly allowed for a message. The original voice entry point stays `python -m src.main`. Run one Atlas interface at a time so conversation history has one writer. `ATLAS_GEMINI_MODEL` can configure model access without editing source.

## Engineering conventions

Each repository is independently runnable. Presentation calls a transport adapter, which invokes application behavior. I/O stays at explicit boundaries so tests can replace external providers. Long browser operations have one owner, reject overlapping requests, and report success or failure through the UI. Relay uses async provider requests; video and desktop work use a worker or an existing sequential CLI loop.

New behavior should validate input before touching a user's files or desktop, report partial failures accurately, and have a regression test for a concrete failure mode. Run the repository's checks before committing and document the exact manual checks separately from mocked tests.

The local apps share a request/status pattern, accessible form controls, and a responsive layout. Small standard-library transports are kept inside each repository so they do not require a sixth repository at runtime. The matching transport modules should be updated together when changing that contract.

## Local addresses

The browser resolves `.localhost` names to the loopback interface. These addresses are scoped to this computer. Start the Python process before opening the address. Chrome and Edge support this setup. A distinct port lets each project run alongside the others without an OS hosts-file change.

## Evaluation

Automated checks verify the workflows represented by their fixtures. Real model access, physical microphones and desktop focus still need environment-specific checks. CI is included under `.github/workflows/checks.yml`; its remote result must be checked after pushing.

Remaining work should be driven by observations from real use. Dataset accuracy, provider access and desktop-device behavior cannot be established by a successful test run alone.

## Verification for this change

4 tests passed. Chrome loaded the dashboard at desktop and phone widths and returned a live Gemini reply with desktop actions disabled. The physical microphone and action effects were not exercised in this pass.
