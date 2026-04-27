from src.recommender import score_song, recommend_songs


POP_SONG = {
    "id": "a1",
    "title": "Pop Hit",
    "artist": "Artist A",
    "genre": "pop",
    "mood": "happy",
    "energy": 0.8,
    "valence": 0.9,
    "danceability": 0.8,
    "acousticness": 0.2,
    "tempo_bpm": 120,
}

LOFI_SONG = {
    "id": "a2",
    "title": "Chill Loop",
    "artist": "Artist B",
    "genre": "lofi",
    "mood": "chill",
    "energy": 0.3,
    "valence": 0.5,
    "danceability": 0.4,
    "acousticness": 0.85,
    "tempo_bpm": 75,
}


def test_exact_genre_mood_energy_match_scores_high():
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}
    score, reasons = score_song(prefs, POP_SONG)
    assert score >= 3.5
    assert any("genre" in r.lower() for r in reasons)
    assert any("mood" in r.lower() for r in reasons)
    assert any("energy" in r.lower() for r in reasons)


def test_no_match_scores_low():
    prefs = {"genre": "metal", "mood": "angry", "energy": 1.0, "likes_acoustic": False}
    score, _ = score_song(prefs, LOFI_SONG)
    assert score < 1.5


def test_energy_penalty_for_mismatch():
    prefs = {"energy": 1.0}
    score_close, _ = score_song(prefs, {"energy": 0.9})
    score_far, _ = score_song(prefs, {"energy": 0.1})
    assert score_close > score_far


def test_acoustic_bonus_when_preferred():
    prefs = {"likes_acoustic": True}
    score_acoustic, reasons = score_song(prefs, LOFI_SONG)
    score_non_acoustic, _ = score_song(prefs, POP_SONG)
    assert score_acoustic > score_non_acoustic
    assert any("acoustic" in r.lower() for r in reasons)


def test_acoustic_bonus_when_not_preferred():
    prefs = {"likes_acoustic": False}
    score_non_acoustic, reasons = score_song(prefs, POP_SONG)
    score_acoustic, _ = score_song(prefs, LOFI_SONG)
    assert score_non_acoustic > score_acoustic
    assert any("acousticness" in r.lower() for r in reasons)


def test_recommend_songs_returns_sorted_by_score():
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    results = recommend_songs(prefs, [LOFI_SONG, POP_SONG], k=2)
    assert results[0][0]["id"] == "a1"
    assert results[0][1] > results[1][1]


def test_recommend_songs_respects_k():
    prefs = {"energy": 0.5}
    results = recommend_songs(prefs, [POP_SONG, LOFI_SONG], k=1)
    assert len(results) == 1


def test_missing_prefs_do_not_crash():
    score, reasons = score_song({}, POP_SONG)
    assert isinstance(score, float)
    assert isinstance(reasons, list)


def test_missing_song_fields_use_defaults():
    prefs = {"energy": 0.5, "likes_acoustic": True}
    score, _ = score_song(prefs, {"id": "x"})
    assert isinstance(score, float)
