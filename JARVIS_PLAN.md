# JARVIS — Lokalny Asystent AI na MacBook
> Plan projektu dla Claude Code — v2

---

## Wizja projektu

Lokalnie działający asystent głosowy wzorowany na Jarvisie z Iron Mana. Wake word "Jarvis" budzi asystenta, który odpowiada głosem i wyświetla rozmowy w panelu. Centrum UI to animowana kula / sieć neuronów reagująca na głos. Panel integracji pokazuje podpięte serwisy i pozwala Jarvisowi z nich korzystać.

---

## Stack technologiczny

### Backend (Python)
- **FastAPI** — główny serwer, WebSocket do UI
- **pvporcupine** — wake word detection (offline)
- **openai-whisper** (lokalnie, model `small`) — STT offline
- **anthropic SDK** — Claude Sonnet 4.6 z tool use
- **edge-tts** — TTS (`pl-PL-MarekNeural`)
- **sounddevice + pyaudio** — mikrofon
- **SQLite + SQLAlchemy** — historia rozmów
- **LaunchAgent (plist)** — autostart przy logowaniu

### Integracje (Python)
- **Google Calendar** — `google-api-python-client` (OAuth2)
- **Spotify** — `spotipy` (OAuth2)
- **GPW / kursy akcji** — scraping `stooq.pl` (bez klucza API)
- **Messenger** — `playwright` (scraping messenger.com) ⚠️

### Frontend (Next.js)
- **Next.js 15 + TypeScript**
- **Tailwind CSS**
- **Three.js / React Three Fiber** — animacja 3D kuli/sieci neuronów
- **shadcn/ui** — komponenty panelu
- **WebSocket** — real-time stan asystenta

---

## Architektura katalogów

```
jarvis/
├── backend/
│   ├── main.py
│   ├── core/
│   │   ├── listener.py          # Wake word + nagrywanie
│   │   ├── transcriber.py       # Whisper STT
│   │   ├── brain.py             # Claude API + tool use loop
│   │   ├── speaker.py           # TTS + odtwarzanie
│   │   └── memory.py            # SQLite historia
│   ├── tools/
│   │   ├── __init__.py          # Tool registry + loader
│   │   ├── base.py              # BaseTool interface
│   │   ├── system.py            # Mac: czas, pogoda, volume, apps
│   │   ├── calendar_tool.py     # Google Calendar
│   │   ├── spotify_tool.py      # Spotify
│   │   ├── stocks_tool.py       # GPW / stooq.pl
│   │   └── messenger_tool.py    # Messenger (Playwright)
│   ├── integrations/
│   │   ├── google_auth.py       # OAuth2 flow dla Google
│   │   ├── spotify_auth.py      # OAuth2 flow dla Spotify
│   │   └── messenger_session.py # Playwright session manager
│   ├── config.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # Główny layout
│   │   │   └── integrations/
│   │   │       └── page.tsx     # Panel integracji
│   │   └── components/
│   │       ├── NeuralOrb.tsx    # 3D kula / sieć neuronów (R3F)
│   │       ├── ConversationFeed.tsx
│   │       ├── IntegrationCard.tsx
│   │       ├── IntegrationPanel.tsx
│   │       └── StatusBar.tsx
│   └── package.json
├── scripts/
│   ├── install.sh
│   └── com.jarvis.assistant.plist
└── README.md
```

---

## UI — Design "Neural Core"

### Koncepcja wizualna
Główny ekran jest podzielony na dwie strefy: lewa to żywy, trójwymiarowy obiekt 3D (kula lub sieć neuronów), prawa to panel z rozmową i integracje na dole. Tło: głęboka czerń `#05070A` z bardzo subtelnymi skanlinami. Jedynym źródłem koloru jest obiekt 3D i aktywne integracje.

### Paleta
- `#05070A` — tło (głęboka czerń, nie pure black)
- `#0D4FFF` — primary accent (elektryczny niebieski)
- `#00D4FF` — secondary (cyan, orb idle)
- `#FF3D6E` — alert / Messenger notification
- `#C8D0E0` — tekst główny (zimny biały)
- `#3A4560` — tekst drugorzędny / borders

### Typografia
- Display / nazwy sekcji: `Space Grotesk` (tech, ale nie robotic)
- Transkrypty / kod: `JetBrains Mono` (monospaced, czytelny)

### Layout
```
┌──────────────────────────────────────────────────┐
│  JARVIS  v2.0          ● ONLINE   [sesja: 14:32] │
├────────────────────┬─────────────────────────────┤
│                    │                             │
│   [NEURAL ORB]     │   CONVERSATION FEED         │
│                    │                             │
│   3D kula/sieć     │   > Hej Jarvis              │
│   animowana        │   Słucham, Patryk.          │
│   Three.js/R3F     │                             │
│                    │   > Jaki mam event dziś?    │
│   ● LISTENING      │   O 15:00 masz standup...  │
│                    │   [📅 Google Calendar]      │
│                    │                             │
├────────────────────┴─────────────────────────────┤
│  INTEGRACJE                                      │
│  [📅 Calendar ✓] [🎵 Spotify ✓] [📈 GPW ✓] [💬 Messenger ✓] │
└──────────────────────────────────────────────────┘
```

### NeuralOrb — stany animacji

Komponent Three.js / React Three Fiber. Do wyboru dwie opcje — Claude Code powinien zaimplementować **obie** i przełączać przez config:

**Opcja A — Particle Sphere (kula z cząstek)**
- ~800 punktów na sferze, połączone liniami gdy są blisko siebie
- Idle: powolna rotacja, zimny niebieski
- Listening: cząstki oscylują do centrum i z powrotem (puls), kolor zielony
- Thinking: linie między cząstkami migają losowo, szybka rotacja, fiolet
- Speaking: fale wychodzące od centrum, kolor cyan, pulsujące pierścienie

**Opcja B — Neural Network (sieć neuronów)**
- ~40 nodów połączonych krawędziami (random graph)
- Idle: pojedyncze impulsy przebiegają po losowych ścieżkach
- Listening: wszystkie krawędzie aktywne, zielone impulsy
- Thinking: chaotyczne, szybkie impulsy, chaos → porządek animacja
- Speaking: impulsy płyną od centrum na zewnątrz zsynchronizowane z TTS

**Implementacja:**
```tsx
// NeuralOrb.tsx
import { Canvas, useFrame } from '@react-three/fiber'

type OrbState = 'idle' | 'listening' | 'thinking' | 'speaking'

interface NeuralOrbProps {
  state: OrbState
  audioLevel?: number  // 0-1, amplituda mikrofonu w real-time
}
```

`audioLevel` przychodzi przez WebSocket z backendu (backend mierzy amplitudę podczas nagrywania) — dzięki temu kula reaguje na głos użytkownika w czasie rzeczywistym.

---

## Panel Integracji

### IntegrationCard — jeden kafelek
```
┌──────────────────────────┐
│  📅  Google Calendar     │
│  ● Połączono             │
│  Następny event: 15:00   │
│  [Odłącz]                │
└──────────────────────────┘
```

Stany karty: `disconnected` | `connecting` | `connected` | `error`

### Strona `/integrations`
Pełny widok z kartami wszystkich dostępnych integracji, instrukcją połączenia, statusem i ostatnią aktywnością.

### Backend — endpoints integracji
```
GET  /integrations              — lista wszystkich z statusem
POST /integrations/{name}/connect   — inicjuj OAuth lub session
POST /integrations/{name}/disconnect
GET  /integrations/{name}/status    — ping czy token ważny
```

---

## Integracje — szczegóły implementacji

### Google Calendar (`tools/calendar_tool.py`)
- OAuth2 przez `google-auth-oauthlib` — przy pierwszym połączeniu otwiera przeglądarkę
- Token zapisywany lokalnie w `~/.jarvis/tokens/google.json`
- Narzędzia dla Claude:
  - `get_todays_events()` → lista eventów na dziś
  - `get_upcoming_events(days=7)` → eventy w ciągu N dni
  - `create_event(title, date, time, duration)` → stwórz event

### Spotify (`tools/spotify_tool.py`)
- OAuth2 przez `spotipy` — token w `~/.jarvis/tokens/spotify.json`
- Narzędzia dla Claude:
  - `get_current_track()` → co teraz gra
  - `play_pause()` → pauza/wznowienie
  - `next_track()` / `previous_track()`
  - `search_and_play(query)` → "włącz Billie Eilish"
  - `set_volume(level)` → 0-100

### GPW / Akcje (`tools/stocks_tool.py`)
- Scraping `stooq.pl` — bez klucza API, dane opóźnione ~15 min
- Narzędzia dla Claude:
  - `get_stock_price(ticker)` → np. "PKN", "CDR", "PKO"
  - `get_watchlist()` → lista obserwowanych spółek (config)
  - `get_index(name)` → WIG20, mWIG40, sWIG80

Watchlist definiowana w `config.py`:
```python
STOCK_WATCHLIST = ["PKN", "CDR", "PKO", "LPP", "ALE"]
```

### Messenger (`tools/messenger_tool.py`) ⚠️

> **Ważna uwaga:** Meta nie udostępnia publicznego API do Messengera. Jedyna technicznie możliwa metoda to automatyczna przeglądarka (Playwright) logująca się na messenger.com. Działa, ale:
> - Narusza ToS Facebooka
> - Może triggerować 2FA lub captcha
> - Meta może zablokować konto przy agresywnym użyciu
> - **Rekomendacja:** używać oszczędnie, tylko do odczytu, nie do wysyłania
>
> **Alternatywa:** Telegram ma oficjalne Bot API — jeśli korzystasz z Telegrama, warto rozważyć zamianę.

**Implementacja Playwright:**
```python
# integrations/messenger_session.py
# Playwright Chromium — utrzymuje zalogowaną sesję
# Cookies zapisane w ~/.jarvis/messenger_session.json
# Przy starcie: sprawdź czy sesja ważna, jeśli nie → poproś o ręczne zalogowanie
```

Narzędzia dla Claude:
- `get_unread_count()` → liczba nieprzeczytanych
- `get_recent_conversations(n=5)` → ostatnie N konwersacji z nadawcą i ostatnią wiadomością
- `get_messages(conversation_id, limit=10)` → wiadomości z konkretnej rozmowy

**Flow pierwszego połączenia:**
1. Jarvis: "Otwórzcie okno przeglądarki, zaloguj się do Facebooka"
2. Playwright otwiera Chromium w trybie widocznym
3. Użytkownik loguje się ręcznie
4. Playwright zapisuje cookies → kolejne starty są automatyczne

---

## System prompt Jarvisa (zaktualizowany)

```
Jesteś Jarvis — osobisty asystent AI Patryka.
Odpowiadasz ZAWSZE po polsku, chyba że Patryk mówi po angielsku.
Jesteś zwięzły i konkretny — maksymalnie 2-3 zdania na odpowiedź głosową.
Nie używasz "Oczywiście!", "Świetnie!" — przechodzisz od razu do rzeczy.
Masz dostęp do narzędzi: kalendarz Google, Spotify, kursy GPW, Messenger.
Używaj narzędzi proaktywnie gdy pytanie tego wymaga.
Znasz projekty Patryka: Suprizely (suprizely.pl), QWS (quickws.ovh), sports prediction engine.
Gdy używasz narzędzia, powiedz krótko co robisz: "Sprawdzam kalendarz..."
```

---

## WebSocket — eventy (rozszerzony)

```json
{ "type": "state_change", "state": "listening" }
{ "type": "audio_level", "level": 0.73 }
{ "type": "transcript", "text": "Jaka jest pogoda?" }
{ "type": "tool_call", "tool": "get_stock_price", "args": {"ticker": "CDR"} }
{ "type": "tool_result", "tool": "get_stock_price", "result": "CDR: 89.40 PLN (+1.2%)" }
{ "type": "response", "text": "CD Projekt kosztuje teraz 89 złotych i 40 groszy." }
{ "type": "integration_status", "name": "spotify", "status": "connected" }
```

`audio_level` wysyłany co ~50ms podczas nagrywania — napędza animację orba w real-time.

---

## Requirements

**`backend/requirements.txt`**
```
fastapi
uvicorn[standard]
anthropic
openai-whisper
pvporcupine
pyaudio
sounddevice
edge-tts
sqlalchemy
psutil
python-dotenv
websockets
google-api-python-client
google-auth-oauthlib
spotipy
playwright
beautifulsoup4
httpx
```

**`frontend/package.json` (kluczowe deps)**
```json
{
  "dependencies": {
    "next": "15",
    "typescript": "^5",
    "tailwindcss": "^3",
    "@react-three/fiber": "^8",
    "@react-three/drei": "^9",
    "three": "^0.165",
    "shadcn-ui": "latest"
  }
}
```

---

## Kolejność implementacji dla Claude Code

**Etap 1 — Rdzeń audio (bez UI)**
1. `backend/config.py` + `.env.example`
2. `backend/core/memory.py`
3. `backend/core/transcriber.py`
4. `backend/core/speaker.py`
5. `backend/core/brain.py`
6. `backend/tools/base.py` + `tools/__init__.py`
7. `backend/tools/system.py`
8. `backend/core/listener.py`
9. `backend/main.py` (FastAPI + WebSocket z audio_level)

**Etap 2 — Integracje**
10. `backend/integrations/google_auth.py` + `backend/tools/calendar_tool.py`
11. `backend/integrations/spotify_auth.py` + `backend/tools/spotify_tool.py`
12. `backend/tools/stocks_tool.py`
13. `backend/integrations/messenger_session.py` + `backend/tools/messenger_tool.py`
14. `backend/main.py` — dodaj endpoints `/integrations/*`

**Etap 3 — Frontend**
15. `frontend/` — szkielet Next.js + layout
16. `frontend/components/NeuralOrb.tsx` — animacja 3D (Particle Sphere jako domyślna)
17. `frontend/components/ConversationFeed.tsx`
18. `frontend/components/IntegrationCard.tsx` + `IntegrationPanel.tsx`
19. `frontend/app/page.tsx` — złożenie wszystkiego
20. `frontend/app/integrations/page.tsx` — pełna strona integracji

**Etap 4 — Autostart**
21. `scripts/install.sh` + `com.jarvis.assistant.plist`

---

## Uwagi implementacyjne

- **Mikrofon na Mac:** `python` potrzebuje dostępu w System Settings → Privacy → Microphone
- **Porcupine:** darmowe konto na console.picovoice.ai → wygeneruj keyword "Jarvis" → pobierz `.ppn`
- **Google OAuth:** stwórz projekt w Google Cloud Console → włącz Calendar API → pobierz `credentials.json`
- **Spotify OAuth:** zarejestruj aplikację na developer.spotify.com → `Client ID` + `Client Secret`
- **Playwright Messenger:** po instalacji wymagane `playwright install chromium`
- **Three.js / R3F:** `audioLevel` z WebSocket wpina się bezpośrednio do `useFrame` — kula "oddycha" z głosem
- **Token storage:** wszystkie tokeny w `~/.jarvis/` poza repozytorium (w `.gitignore`)
