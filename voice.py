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


def listen_for_wakeword():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000,
                         input=True, frames_per_buffer=1280)

    print("listening for 'hey jarvis'...")

    for _ in range(5):
        stream.read(1280)  # mic spikes on startup, throw these away

    hits = 0
    try:
        while True:
            chunk = np.frombuffer(stream.read(1280), dtype=np.int16)
            pred = oww_model.predict(chunk)
            best = max(pred.values(), default=0)

            if best > config.wake_threshold:
                hits += 1
                if hits >= config.wake_hits_needed:
                    return
            else:
                hits = 0
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()


def listen_for_command():
    with sr.Microphone() as source:
        print("listening for command...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=config.mic_timeout, phrase_time_limit=config.mic_phrase_limit)
        except sr.WaitTimeoutError:
            print("atlas: didnt hear anything, going back to sleep")
            return None

    try:
        text = recognizer.recognize_google(audio)
        print(f"heard: {text}")
        return text
    except sr.UnknownValueError:
        print("atlas: didnt catch that")
        return None
    except sr.WaitTimeoutError:
        print("atlas: didnt hear anything, going back to sleep")
        return None


def speak(text):
    print("Atlas:", text)
    # making a new engine every time instead of reusing one, since pyttsx3
    # goes silent after the first call otherwise on windows (sapi5 quirk)
    engine = pyttsx3.init()
    engine.setProperty("rate", config.tts_rate)
    if config.tts_voice_index is not None:
        voices = engine.getProperty("voices")
        engine.setProperty("voice", voices[config.tts_voice_index].id)
    engine.say(text)
    engine.runAndWait()
    engine.stop()