# just the main loop now, everything else moved into its own file.
# see design.md for why its split up this way

import time

from src.voice import listen_for_wakeword, listen_for_command, speak
