import pyaudiowpatch as pyaudio
import numpy as np
from openwakeword.model import Model

# loads the built in models, hey jarvis is one of them
oww_model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")
