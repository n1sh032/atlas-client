# everything to do with actually hearing and talking. wake word detection,
# speech to text, text to speech

import sys
import numpy as np
import pyaudiowpatch as pyaudio
sys.modules["pyaudio"] = pyaudio  # speech_recognition hardcodes "import pyaudio"
                                   # so this tricks it into using the patched version
import speech_recognition as sr
import pyttsx3
from openwakeword.model import Model

from src import config

oww_model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")
recognizer = sr.Recognizer()
recognizer.pause_threshold = config.mic_pause_threshold

# opening the mic stream ONCE here instead of every time listen_for_wakeword runs.
# opening/closing it constantly was making the laptop chirp every loop
_audio = pyaudio.PyAudio()
_wake_stream = _audio.open(format=pyaudio.paInt16, channels=1, rate=16000,
                            input=True, frames_per_buffer=1280)

# throw away the first few reads once at startup, mic spikes when it first opens
for _ in range(5):
    _wake_stream.read(1280)


def listen_for_wakeword():
    print("listening for 'hey jarvis'...")

    hits = 0
    while True:
        chunk = np.frombuffer(_wake_stream.read(1280), dtype=np.int16)
        pred = oww_model.predict(chunk)
        best = max(pred.values(), default=0)

        if best > config.wake_threshold:
            hits += 1
            if hits >= config.wake_hits_needed:
                return
        else:
            hits = 0

