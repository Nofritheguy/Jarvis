import threading
import numpy as np
import pyaudio
from typing import Callable
from openwakeword.model import Model
from backend.config import (
    SAMPLE_RATE,
    WAKEWORD_MODEL,
    WAKEWORD_THRESHOLD,
    SILENCE_THRESHOLD,
    SILENCE_SECONDS,
    MAX_RECORDING_SECONDS,
)

# openwakeword requires 1280-sample chunks (80ms @ 16kHz)
CHUNK_SIZE = 1280
RECORD_CHUNK = 512


class Listener:
    """
    Wake-word listener using openwakeword + PyAudio.
    On wake word → records until silence → calls on_audio(np.ndarray).
    on_audio_level(float 0-1) is called ~every 50ms during recording.
    """

    def __init__(
        self,
        on_audio: Callable[[np.ndarray], None],
        on_state: Callable[[str], None] | None = None,
        on_audio_level: Callable[[float], None] | None = None,
    ):
        self.on_audio = on_audio
        self.on_state = on_state or (lambda s: None)
        self.on_audio_level = on_audio_level or (lambda l: None)
        self._running = False
        # Model loads (and auto-downloads) on first instantiation
        self._model = Model(wakeword_models=[WAKEWORD_MODEL], inference_framework="onnx")

    def start(self):
        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self._running = False

    def _loop(self):
        pa = pyaudio.PyAudio()
        stream = pa.open(
            rate=SAMPLE_RATE,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=CHUNK_SIZE,
        )
        self.on_state("idle")
        try:
            while self._running:
                pcm = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                arr = np.frombuffer(pcm, dtype=np.int16)
                predictions = self._model.predict(arr)
                if any(score >= WAKEWORD_THRESHOLD for score in predictions.values()):
                    self._model.reset()
                    self.on_state("listening")
                    audio = self._record(stream)
                    self.on_state("thinking")
                    self.on_audio(audio)
                    self.on_state("idle")
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()

    def _record(self, stream) -> np.ndarray:
        frames = []
        silence_frames = 0
        max_frames = int(MAX_RECORDING_SECONDS * SAMPLE_RATE / RECORD_CHUNK)
        silence_limit = int(SILENCE_SECONDS * SAMPLE_RATE / RECORD_CHUNK)

        while len(frames) < max_frames:
            pcm = stream.read(RECORD_CHUNK, exception_on_overflow=False)
            frames.append(pcm)
            arr = np.frombuffer(pcm, dtype=np.int16)
            self.on_audio_level(float(np.abs(arr).mean()) / 32768.0)

            if np.abs(arr).mean() < SILENCE_THRESHOLD:
                silence_frames += 1
            else:
                silence_frames = 0

            if silence_frames >= silence_limit:
                break

        return np.frombuffer(b"".join(frames), dtype=np.int16).astype(np.float32)
