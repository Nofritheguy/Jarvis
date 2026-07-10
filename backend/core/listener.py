import threading
import numpy as np
import pyaudio
from typing import Callable, Optional
from backend.config import (
    SAMPLE_RATE,
    USE_WAKE_WORD,
    WAKEWORD_MODEL,
    WAKEWORD_THRESHOLD,
    SILENCE_THRESHOLD,
    SILENCE_SECONDS,
    MAX_RECORDING_SECONDS,
)

WAKE_CHUNK = 1280   # 80ms @ 16kHz — required by openwakeword
RECORD_CHUNK = 512


class Listener:
    """
    Audio listener with two modes:
    - USE_WAKE_WORD=true  → openwakeword detects "hey jarvis" offline
    - USE_WAKE_WORD=false → press Enter in terminal to start recording (test mode)
    """

    def __init__(
        self,
        on_audio: Callable[[np.ndarray], None],
        on_state: Optional[Callable[[str], None]] = None,
        on_audio_level: Optional[Callable[[float], None]] = None,
    ):
        self.on_audio = on_audio
        self.on_state = on_state or (lambda s: None)
        self.on_audio_level = on_audio_level or (lambda l: None)
        self._running = False
        self._oww = None

        if USE_WAKE_WORD:
            from openwakeword.model import Model
            self._oww = Model(wakeword_models=[WAKEWORD_MODEL], inference_framework="onnx")

    def start(self):
        self._running = True
        if USE_WAKE_WORD:
            threading.Thread(target=self._loop_wakeword, daemon=True).start()
        else:
            threading.Thread(target=self._loop_manual, daemon=True).start()

    def stop(self):
        self._running = False

    # ── Wake word mode ────────────────────────────────────────────────────────

    def _loop_wakeword(self):
        pa = pyaudio.PyAudio()
        stream = pa.open(
            rate=SAMPLE_RATE, channels=1,
            format=pyaudio.paInt16, input=True,
            frames_per_buffer=WAKE_CHUNK,
        )
        self.on_state("idle")
        try:
            while self._running:
                pcm = stream.read(WAKE_CHUNK, exception_on_overflow=False)
                arr = np.frombuffer(pcm, dtype=np.int16)
                predictions = self._oww.predict(arr)
                if any(score >= WAKEWORD_THRESHOLD for score in predictions.values()):
                    self._oww.reset()
                    self.on_state("listening")
                    audio = self._record(stream)
                    self.on_state("thinking")
                    self.on_audio(audio)
                    self.on_state("idle")
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()

    # ── Manual / test mode ────────────────────────────────────────────────────

    def _loop_manual(self):
        self.on_state("idle")
        pa = pyaudio.PyAudio()
        print("\n[Jarvis] Tryb testowy — naciśnij Enter żeby nagrać, Ctrl+C żeby wyjść\n")
        while self._running:
            try:
                input()  # wait for Enter
            except EOFError:
                # Running without a TTY (e.g. as a service) — just idle
                import time; time.sleep(1); continue
            stream = pa.open(
                rate=SAMPLE_RATE, channels=1,
                format=pyaudio.paInt16, input=True,
                frames_per_buffer=RECORD_CHUNK,
            )
            self.on_state("listening")
            audio = self._record(stream)
            stream.stop_stream()
            stream.close()
            self.on_state("thinking")
            self.on_audio(audio)
            self.on_state("idle")

    # ── Shared recording ──────────────────────────────────────────────────────

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
