#!/bin/bash
set -e

JARVIS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_NAME="com.jarvis.assistant"
PLIST_SRC="$JARVIS_DIR/scripts/$PLIST_NAME.plist"
PLIST_DST="$HOME/Library/LaunchAgents/$PLIST_NAME.plist"

echo "=== Jarvis Install Script ==="
echo "Katalog projektu: $JARVIS_DIR"

# 1. Python venv
if [ ! -d "$JARVIS_DIR/backend/.venv" ]; then
  echo "[1/5] Tworzenie środowiska Python..."
  python3 -m venv "$JARVIS_DIR/backend/.venv"
fi

echo "[2/5] Instalowanie zależności Python..."
"$JARVIS_DIR/backend/.venv/bin/pip" install -q --upgrade pip
"$JARVIS_DIR/backend/.venv/bin/pip" install -q -r "$JARVIS_DIR/backend/requirements.txt"

# Playwright browsers
"$JARVIS_DIR/backend/.venv/bin/playwright" install chromium 2>/dev/null || true

# 2. Node / frontend
echo "[3/5] Instalowanie zależności frontend..."
cd "$JARVIS_DIR/frontend" && npm install --silent

# 3. .env
if [ ! -f "$JARVIS_DIR/.env" ]; then
  echo "[4/5] Kopiowanie .env.example → .env (uzupełnij klucze!)"
  cp "$JARVIS_DIR/.env.example" "$JARVIS_DIR/.env"
else
  echo "[4/5] Plik .env już istnieje."
fi

# 4. LaunchAgent
echo "[5/5] Instalowanie LaunchAgent..."
sed "s|JARVIS_PATH|$JARVIS_DIR|g" "$PLIST_SRC" > "$PLIST_DST"
launchctl unload "$PLIST_DST" 2>/dev/null || true
launchctl load "$PLIST_DST"

echo ""
echo "Instalacja zakończona!"
echo "Backend uruchomi się automatycznie przy logowaniu."
echo "Ręczne uruchomienie backendu: cd backend && ../.venv/bin/python -m uvicorn backend.main:app --port 8000"
echo "Frontend dev server: cd frontend && npm run dev"
echo ""
echo "Pamiętaj o uzupełnieniu .env kluczami API!"
