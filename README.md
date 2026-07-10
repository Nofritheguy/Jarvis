# JARVIS — Lokalny Asystent AI

Lokalnie działający asystent głosowy wzorowany na Jarvisie z Iron Mana. Wake word **"Jarvis"** budzi asystenta, który odpowiada głosem (po polsku) i wyświetla rozmowy w panelu.

## Stack

| Warstwa | Technologia |
|---|---|
| Backend | Python, FastAPI, WebSocket |
| AI | Claude Sonnet 4.6 (Anthropic) + tool use |
| STT | OpenAI Whisper (`small`, offline) |
| Wake word | Porcupine (`pvporcupine`) |
| TTS | edge-tts (`pl-PL-MarekNeural`) |
| DB | SQLite + SQLAlchemy |
| Frontend | Next.js 15, TypeScript, Tailwind CSS |
| 3D | Three.js + React Three Fiber |
| Integracje | Google Calendar, Spotify, GPW (stooq.pl), Messenger (Playwright) |

## Szybki start

### 1. Klonowanie i instalacja

```bash
git clone https://github.com/Nofritheguy/Jarvis.git
cd Jarvis
chmod +x scripts/install.sh
./scripts/install.sh
```

### 2. Konfiguracja `.env`

```bash
cp .env.example .env
# Uzupełnij klucze:
# - ANTHROPIC_API_KEY (console.anthropic.com)
# - PORCUPINE_ACCESS_KEY (console.picovoice.ai) + plik .ppn z keyword "Jarvis"
# - SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET (developer.spotify.com)
# - GOOGLE_CREDENTIALS_PATH → plik z Google Cloud Console (Calendar API)
```

### 3. Uruchomienie

**Backend:**
```bash
cd /ścieżka/do/Jarvis
backend/.venv/bin/python -m uvicorn backend.main:app --port 8000
```

**Frontend (dev):**
```bash
cd frontend && npm run dev
# → http://localhost:3000
```

## Architektura

```
jarvis/
├── backend/
│   ├── main.py              # FastAPI + WebSocket
│   ├── config.py            # Konfiguracja z .env
│   ├── core/
│   │   ├── listener.py      # Wake word (Porcupine) + nagrywanie
│   │   ├── transcriber.py   # Whisper STT
│   │   ├── brain.py         # Claude API + tool use loop
│   │   ├── speaker.py       # edge-tts + odtwarzanie
│   │   └── memory.py        # SQLite historia rozmów
│   ├── tools/               # Narzędzia dla Claude
│   └── integrations/        # OAuth + sesje
├── frontend/
│   └── src/
│       ├── app/page.tsx     # Główny panel
│       ├── app/integrations/ # Panel integracji
│       └── components/
│           ├── NeuralOrb.tsx        # 3D animacja (R3F)
│           ├── ConversationFeed.tsx
│           ├── IntegrationCard.tsx
│           └── StatusBar.tsx
└── scripts/
    ├── install.sh
    └── com.jarvis.assistant.plist   # macOS LaunchAgent
```

## WebSocket events

| Event | Opis |
|---|---|
| `state_change` | `idle \| listening \| thinking \| speaking` |
| `audio_level` | Amplituda mikrofonu (0-1), ~50ms |
| `transcript` | Rozpoznany tekst użytkownika |
| `tool_call` | Wywołanie narzędzia przez Claude |
| `tool_result` | Wynik narzędzia |
| `response` | Odpowiedź tekstowa Jarvisa |
| `integration_status` | Zmiana statusu integracji |

## Integracje — wymagania

### Google Calendar
1. Utwórz projekt w [Google Cloud Console](https://console.cloud.google.com)
2. Włącz **Google Calendar API**
3. Utwórz OAuth 2.0 credentials → pobierz `credentials.json`
4. Ustaw `GOOGLE_CREDENTIALS_PATH` w `.env`

### Spotify
1. Zarejestruj aplikację na [developer.spotify.com](https://developer.spotify.com)
2. Dodaj redirect URI: `http://localhost:8888/callback`
3. Ustaw `SPOTIFY_CLIENT_ID` i `SPOTIFY_CLIENT_SECRET`

### Porcupine (wake word)
1. Załóż darmowe konto na [console.picovoice.ai](https://console.picovoice.ai)
2. Wygeneruj keyword model dla słowa **"Jarvis"** (Mac)
3. Pobierz plik `.ppn` → ustaw `PORCUPINE_KEYWORD_PATH`

### Messenger ⚠️
- Używa Playwright do scrapingu messenger.com
- Narusza ToS Facebooka — używaj ostrożnie, tylko do odczytu
- Przy pierwszym połączeniu → ręczne logowanie w oknie przeglądarki

## Autostart (macOS)

`scripts/install.sh` instaluje LaunchAgent który startuje backend przy logowaniu.

```bash
# Ręczne zarządzanie:
launchctl load ~/Library/LaunchAgents/com.jarvis.assistant.plist
launchctl unload ~/Library/LaunchAgents/com.jarvis.assistant.plist
```

Logi: `logs/jarvis.log` i `logs/jarvis.err`
