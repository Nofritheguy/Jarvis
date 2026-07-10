import asyncio
import tempfile
import os
import edge_tts
import sounddevice as sd
import soundfile as sf
from backend.config import TTS_VOICE


async def synthesize(text: str) -> bytes:
    """Convert text to MP3 bytes via edge-tts."""
    communicate = edge_tts.Communicate(text, TTS_VOICE)
    buf = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buf += chunk["data"]
    return buf


async def speak(text: str) -> None:
    """Synthesize and play audio blocking until done."""
    mp3_bytes = await synthesize(text)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(mp3_bytes)
        tmp_path = f.name
    try:
        data, samplerate = sf.read(tmp_path, dtype="float32")
        sd.play(data, samplerate)
        sd.wait()
    finally:
        os.unlink(tmp_path)


def speak_sync(text: str) -> None:
    asyncio.run(speak(text))
