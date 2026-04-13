"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs


ADVERSARIAL_PROFILES = [
    # Profile 1: energy=0.0 — triggers the falsy `or` bug on line 95 of
    # recommender.py, silently skipping energy scoring entirely.
    {
        "name": "Calm Seeker (energy=0.0 bug)",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 0.0},
    },
    # Profile 2: energy=1.5 — out-of-range value produces negative energy
    # scores, which can lower a genre+mood-matched song below a no-match song.
    {
        "name": "Hyper Fan (energy=1.5 out-of-range)",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 1.5},
    },
    # Profile 3: genre and mood absent from catalog — every song scores 0 on
    # both text fields, so the top-k is decided by energy proximity alone.
    {
        "name": "Unknown Taste (genre/mood not in catalog)",
        "prefs": {"genre": "baroque", "mood": "nostalgic", "energy": 0.5},
    },
    # Profile 4: verifies the reweighted scorer (genre 0.5, energy up to 2.0).
    # A perfect-energy song (energy=0.95, wrong genre) should outscore a
    # genre-match song with mediocre energy (energy=0.4). Math:
    #   perfect-energy / wrong-genre: 0 + 2.0*(1-|0.95-0.95|) = 2.0
    #   genre-match   / bad-energy:   0.5 + 2.0*(1-|0.4-0.95|) = 0.5 + 0.9 = 1.4
    # So energy proximity should dominate genre label when the gap is large.
    {
        "name": "Energy Purist (reweight check: energy=0.95, genre=pop)",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 0.95},
    },
]


def print_recommendations(label: str, recommendations) -> None:
    width = 52
    print("\n" + "=" * width)
    print(f" PROFILE: {label}")
    print("=" * width)

    for rank, (song, score, reasons) in enumerate(recommendations, start=1):
        print(f"\n#{rank}  {song['title']}")
        print(f"    Artist : {song['artist']}")
        print(f"    Genre  : {song['genre']}  |  Mood: {song['mood']}")
        print(f"    Score  : {score:.2f}")
        print("    " + "-" * (width - 4))
        if reasons:
            for reason in reasons:
                print(f"    • {reason}")
        else:
            print("    • No strong matches found")

    print("\n" + "=" * width + "\n")


def main() -> None:
    """Load songs, run the recommender for each adversarial profile, and print results."""
    songs = load_songs("data/songs.csv")

    for profile in ADVERSARIAL_PROFILES:
        recommendations = recommend_songs(profile["prefs"], songs, k=5)
        print_recommendations(profile["name"], recommendations)


if __name__ == "__main__":
    main()
