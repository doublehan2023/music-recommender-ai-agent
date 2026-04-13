"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs


def main() -> None:
    """Load songs, run the recommender, and print a formatted results table."""
    songs = load_songs("data/songs.csv") 

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    recommendations = recommend_songs(user_prefs, songs, k=5)

    width = 52
    print("\n" + "=" * width)
    print(" TOP RECOMMENDATIONS")
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


if __name__ == "__main__":
    main()
