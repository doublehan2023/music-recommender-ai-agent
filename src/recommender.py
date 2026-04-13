from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Store the catalog of songs available for recommendation."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs ranked by how well they match the user's profile."""
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable string explaining why a song was recommended."""
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    import csv
    print(f"Loading songs from {csv_path}...")
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons = []

    # Genre match: worth 0.5 (halved from 1.0)
    if song.get("genre") == user_prefs.get("genre"):
        score += 0.5
        reasons.append(f"Matches your favorite genre ({song['genre']})")

    # Mood match: worth 1.0
    if song.get("mood") == user_prefs.get("mood"):
        score += 1.0
        reasons.append(f"Matches your preferred mood ({song['mood']})")

    # Energy similarity: worth up to 2.0 (doubled from 1.0)
    target_energy = user_prefs.get("energy") or user_prefs.get("target_energy")
    if target_energy is not None:
        energy_score = 2.0 * (1.0 - abs(song.get("energy", 0.5) - float(target_energy)))
        score += energy_score
        if energy_score >= 1.6:
            reasons.append(
                f"Energy level ({song['energy']:.2f}) closely matches your target ({float(target_energy):.2f})"
            )

    # Acousticness preference: worth 0.5 (optional key)
    likes_acoustic = user_prefs.get("likes_acoustic")
    if likes_acoustic is not None:
        acousticness = song.get("acousticness", 0.5)
        if likes_acoustic and acousticness >= 0.6:
            score += 0.5
            reasons.append(f"Strong acoustic feel ({acousticness:.2f}) suits your taste")
        elif not likes_acoustic and acousticness <= 0.4:
            score += 0.5
            reasons.append(f"Low acousticness ({acousticness:.2f}) suits your taste")

    return (score, reasons)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, List[str]]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, reasons))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
