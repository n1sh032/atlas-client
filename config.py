# putting the stuff i keep tweaking here instead of digging through main.py every time

gemini_model = "gemini-2.5-flash"       # switch this if it starts throwing 429s
draft_model = "gemini-3.1-flash-lite"   # used just for draft_document, dont need tool calling for that

timezone = "Asia/Singapore"

# wake word stuff
wake_threshold = 0.9      # how confident it needs to be to count as a hit
wake_hits_needed = 3      # needs this many hits in a row or it kept false triggering on noise

# mic stuff
mic_pause_threshold = 1.8   # bumped this up bc it kept cutting me off mid sentence
mic_timeout = 5             # how long it waits for you to start talking
mic_phrase_limit = 20       # max length of one command
