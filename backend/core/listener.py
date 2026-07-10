import struct
import threading
import time
import numpy as np
import pyaudio
import pvporcupine
from typing import Callable
from backend.config import (
    PORCUPINE_ACCESS_KEY,
    PORCUPINE_KEYWORD_PATH,
    SAMPLE_RATE,
    SILENCE_THRESHOLD,
    SILENCE_SECONDS,
    MAX_RECORDING_SECONDS,
)


class Listener:
    """
    Wake-word listener using Porcupine + PyAudio.
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

    def _emit_state(self, state: str):
        self.on_state(state)

    def start(self):
        self._running = True
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()

    def stop(self):
        self._running = False

    def _loop(self):
        porcupine = pvporcupine.create(
            access_key=PORCUPINE_ACCESS_KEY,
            keyword_paths=[PORCUPINE_KEYWORD_PATH],
        )
        pa = pyaudio.PyAudio()
        stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length,
        )
        self._emit_state("idle")
        try:
            while self._running:
                pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
                pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm)
                keyword_index = porcupine.process(pcm_unpacked)
                if keyword_index >= 0:
                    self._emit_state("listening")
                    audio = self._record(stream, pa)
                    self._emit_state("thinking")
                    self.on_audio(audio)
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()
            porcupine.delete()

    def _record(self, stream, pa) -> np.ndarray:
        frames = []
        silence_frames = 0
        frames_per_50ms = int(SAMPLE_RATE * 0.05 / 512)
        max_frames = int(MAX_RECORDING_SECONDS * SAMPLE_RATE / 512)
        silence_limit = int(SILENCE_SECONDS * SAMPLE_RATE / 512)

        while len(frames) < max_frames:
            pcm = stream.read(512, exception_on_overflow=False)
            frames.append(pcm)
            arr = np.frombuffer(pcm, dtype=np.int16)
            level = float(np.abs(arr).mean()) / 32768.0
            self.on_audio_level(level)

            if np.abs(arr).mean() < SILENCE_THRESHOLD:
                silence_frames += 1
            else:
                silence_frames = 0

            if silence_frames >= silence_limit:
                break

        raw = b"".join(frames)
        return np.frombuffer(raw, dtype=np.int16).astype(np.float32)
