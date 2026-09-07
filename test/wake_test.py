import pyaudiowpatch as pyaudio
import numpy as np
from openwakeword.model import Model

# loads the built in models, hey jarvis is one of them
oww_model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")

audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000,
                     input=True, frames_per_buffer=1280)

print("listening for 'hey jarvis'... ctrl+c to stop")

while True:
    audio_chunk = np.frombuffer(stream.read(1280), dtype=np.int16)
    prediction = oww_model.predict(audio_chunk)

    for wakeword, score in prediction.items():
        if score > 0.5:
            print(f"detected: {wakeword} (confidence: {score:.2f})")