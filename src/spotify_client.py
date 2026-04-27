import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

class SpotifyClient:
    def __init__(self):
        self._sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            )
        )

    def search_tracks(self, query: str, limit: int = 20) -> list[dict]:
        results = self._sp.search(q=query, type="track", limit=limit)
        tracks = []
        for item in results["tracks"]["items"]:
            tracks.append({
                "id": item["id"],
                "title": item["name"],
                "artist": item["artists"][0]["name"],
                "spotify_url": item["external_urls"]["spotify"],
                "preview_url": item["preview_url"],
            })
        return tracks

    def get_audio_features(self, track_ids: list[str]) -> list[dict]:
        features = self._sp.audio_features(track_ids)
        result = []
        for f in features:
            if f is None:
                continue
            result.append({
                "id": f["id"],
                "energy": f["energy"],
                "valence": f["valence"],
                "tempo_bpm": f["tempo"],
                "danceability": f["danceability"],
                "acousticness": f["acousticness"],
            })
        return result

    def enrich_tracks(self, tracks: list[dict]) -> list[dict]:
        ids = [t["id"] for t in tracks]
        features_map = {f["id"]: f for f in self.get_audio_features(ids)}
        enriched = []
        for track in tracks:
            f = features_map.get(track["id"], {})
            enriched.append({
                **track,
                "energy": f.get("energy", 0.5),
                "valence": f.get("valence", 0.5),
                "tempo_bpm": f.get("tempo_bpm", 120.0),
                "danceability": f.get("danceability", 0.5),
                "acousticness": f.get("acousticness", 0.5),
                "genre": "",
                "mood": "",
            })
        return enriched
