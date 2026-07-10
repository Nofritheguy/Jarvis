from backend.tools.base import BaseTool
from backend.integrations.spotify_auth import get_spotify_client


class GetCurrentTrackTool(BaseTool):
    name = "get_current_track"
    description = "Zwraca aktualnie odtwarzany utwór na Spotify."
    input_schema = {"type": "object", "properties": {}, "required": []}

    def run(self, **_):
        try:
            sp = get_spotify_client()
            current = sp.current_playback()
            if not current or not current.get("item"):
                return "Nic nie gra."
            item = current["item"]
            artists = ", ".join(a["name"] for a in item["artists"])
            return f"{artists} — {item['name']}"
        except Exception as ex:
            return f"Błąd Spotify: {ex}"


class PlayPauseTool(BaseTool):
    name = "play_pause"
    description = "Przełącza odtwarzanie/pauzę na Spotify."
    input_schema = {"type": "object", "properties": {}, "required": []}

    def run(self, **_):
        try:
            sp = get_spotify_client()
            current = sp.current_playback()
            if current and current.get("is_playing"):
                sp.pause_playback()
                return "Spotify zapauzowane."
            else:
                sp.start_playback()
                return "Spotify wznowione."
        except Exception as ex:
            return f"Błąd Spotify: {ex}"


class NextTrackTool(BaseTool):
    name = "next_track"
    description = "Przeskakuje do następnego utworu na Spotify."
    input_schema = {"type": "object", "properties": {}, "required": []}

    def run(self, **_):
        try:
            get_spotify_client().next_track()
            return "Następny utwór."
        except Exception as ex:
            return f"Błąd Spotify: {ex}"


class PreviousTrackTool(BaseTool):
    name = "previous_track"
    description = "Wraca do poprzedniego utworu na Spotify."
    input_schema = {"type": "object", "properties": {}, "required": []}

    def run(self, **_):
        try:
            get_spotify_client().previous_track()
            return "Poprzedni utwór."
        except Exception as ex:
            return f"Błąd Spotify: {ex}"


class SearchAndPlayTool(BaseTool):
    name = "search_and_play"
    description = "Wyszukuje utwór/artystę/playlistę na Spotify i odtwarza."
    input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Zapytanie, np. 'Billie Eilish Bad Guy'"}
        },
        "required": ["query"],
    }

    def run(self, query: str, **_):
        try:
            sp = get_spotify_client()
            results = sp.search(q=query, limit=1, type="track")
            tracks = results["tracks"]["items"]
            if not tracks:
                return f"Nie znaleziono: {query}"
            track = tracks[0]
            sp.start_playback(uris=[track["uri"]])
            artists = ", ".join(a["name"] for a in track["artists"])
            return f"Odtwarzam: {artists} — {track['name']}"
        except Exception as ex:
            return f"Błąd Spotify: {ex}"


class SetSpotifyVolumeTool(BaseTool):
    name = "set_spotify_volume"
    description = "Ustawia głośność Spotify (0-100)."
    input_schema = {
        "type": "object",
        "properties": {
            "level": {"type": "integer", "description": "Głośność 0-100"}
        },
        "required": ["level"],
    }

    def run(self, level: int, **_):
        try:
            get_spotify_client().volume(max(0, min(100, level)))
            return f"Głośność Spotify: {level}%."
        except Exception as ex:
            return f"Błąd Spotify: {ex}"
