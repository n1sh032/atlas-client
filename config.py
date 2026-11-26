# putting the stuff i keep tweaking here instead of digging through main.py every time

gemini_model = "gemini-2.5-flash"       # switch this if it starts throwing 429s
draft_model = "gemini-3.1-flash-lite"   # used just for draft_document, dont need tool calling for that

timezone = "Asia/Singapore"

# wake word stuff
wake_threshold = 0.9      # how confident it needs to be to count as a hit
