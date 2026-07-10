import io
import numpy as np
import whisper
import soundfile as sf
from backend.config import WHISPER_MODEL, SAMPLE_RATE

_model: whisper.Whisper | None = None


def _get_model() -> whisper.Whisper:
    global _model
    if _model is None:
        _model = whisper.load_model(WHISPER_MODEL)
    return _model


def transcribe(audio_data: np.ndarray) -> str:
    """Transcribe numpy audio array (float32, mono, 16kHz) to text."""
    model = _get_model()
    audio = audio_data.astype(np.float32)
    if audio.max() > 1.0:
        audio = audio / 32768.0
    result = model.transcribe(audio, language="pl", fp16=False)
    return result["text"].strip()


def transcribe_bytes(audio_bytes: bytes) -> str:
    """Transcribe raw WAV bytes to text."""
    buf = io.BytesIO(audio_bytes)
    audio, _ = sf.read(buf, dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    return transcribe(audio)
