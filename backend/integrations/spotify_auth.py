import os
import json
from typing import Optional
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from backend.config import (
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URI,
    SPOTIFY_TOKEN_PATH,
)

SCOPE = (
    "user-read-playback-state user-modify-playback-state user-read-currently-playing"
)

_client: Optional[spotipy.Spotify] = None


def get_spotify_client() -> spotipy.Spotify:
    global _client
    if _client:
        return _client

    auth_manager = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPE,
        cache_path=SPOTIFY_TOKEN_PATH,
        open_browser=True,
    )
    _client = spotipy.Spotify(auth_manager=auth_manager)
    return _client


def is_connected() -> bool:
    try:
        get_spotify_client().current_user()
        return True
    except Exception:
        return False


def disconnect():
    global _client
    _client = None
    if os.path.exists(SPOTIFY_TOKEN_PATH):
        os.remove(SPOTIFY_TOKEN_PATH)
