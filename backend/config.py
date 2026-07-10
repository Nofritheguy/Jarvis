import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
JARVIS_DIR = Path.home() / ".jarvis"
TOKEN_DIR = JARVIS_DIR / "tokens"
TOKEN_DIR.mkdir(parents=True, exist_ok=True)

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4-6"

# Porcupine wake word
PORCUPINE_ACCESS_KEY = os.getenv("PORCUPINE_ACCESS_KEY", "")
PORCUPINE_KEYWORD_PATH = os.getenv("PORCUPINE_KEYWORD_PATH", "./jarvis_mac.ppn")

# Audio
SAMPLE_RATE = 16000
CHANNELS = 1
SILENCE_THRESHOLD = 500
SILENCE_SECONDS = 1.5
MAX_RECORDING_SECONDS = 30

# Whisper
WHISPER_MODEL = "small"

# TTS
TTS_VOICE = "pl-PL-MarekNeural"

# Spotify
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")
SPOTIFY_TOKEN_PATH = str(TOKEN_DIR / "spotify.json")

# Google
GOOGLE_CREDENTIALS_PATH = os.path.expanduser(
    os.getenv("GOOGLE_CREDENTIALS_PATH", str(TOKEN_DIR / "google_credentials.json"))
)
GOOGLE_TOKEN_PATH = str(TOKEN_DIR / "google.json")
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Messenger
MESSENGER_SESSION_PATH = str(TOKEN_DIR / "messenger_session.json")

# Stocks watchlist
STOCK_WATCHLIST = ["PKN", "CDR", "PKO", "LPP", "ALE"]

# FastAPI
PORT = int(os.getenv("PORT", 8000))

# System prompt
SYSTEM_PROMPT = """Jesteś Jarvis — osobisty asystent AI Patryka.
Odpowiadasz ZAWSZE po polsku, chyba że Patryk mówi po angielsku.
Jesteś zwięzły i konkretny — maksymalnie 2-3 zdania na odpowiedź głosową.
Nie używasz "Oczywiście!", "Świetnie!" — przechodzisz od razu do rzeczy.
Masz dostęp do narzędzi: kalendarz Google, Spotify, kursy GPW, Messenger.
Używaj narzędzi proaktywnie gdy pytanie tego wymaga.
Znasz projekty Patryka: Suprizely (suprizely.pl), QWS (quickws.ovh), sports prediction engine.
Gdy używasz narzędzia, powiedz krótko co robisz: "Sprawdzam kalendarz...\""""
