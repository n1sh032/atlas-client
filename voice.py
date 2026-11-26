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

import config

oww_model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")
recognizer = sr.Recognizer()
recognizer.pause_threshold = config.mic_pause_threshold

