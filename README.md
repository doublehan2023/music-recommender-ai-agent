# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

**Song features used:**

Each `Song` in the catalog carries two kinds of attributes:

- Categorical: `genre` (e.g. lofi, pop, rock) and `mood` (e.g. chill, intense, happy)
- Numerical (all on a 0–1 scale): `energy`, `valence`, `danceability`, `acousticness`, plus `tempo_bpm`

**What the `UserProfile` stores:**

- `favorite_genre` and `favorite_mood` — the category labels the user prefers
- `target_energy` — the energy level the user wants, as a number between 0 and 1
- `likes_acoustic` — a true/false flag for whether the user prefers acoustic-sounding songs

**How a score is computed:**

For each song, the `Recommender` calls `score_song`, which adds up weighted signals:

1. **Genre match** (+0.35) — exact match between the song's genre and the user's favorite
2. **Mood match** (+0.30) — exact match between the song's mood and the user's favorite
3. **Energy proximity** (up to +0.25) — the closer the song's energy is to the user's `target_energy`, the higher this contribution; songs far from the target score low here regardless of whether they are higher or lower
4. **Acousticness proximity** (up to +0.10) — same proximity logic; `likes_acoustic=True` sets a target of ~0.8, `False` sets ~0.2

**How songs are chosen:**

Every song in the catalog is scored independently. The `Recommender` then sorts all songs by score (highest first) and returns the top *k* results (default: 5).

**Potential biases:**

- **Catalog imbalance** — genres with more songs in the catalog have a higher chance of appearing in the top-k. For example, lofi and r&b each have two entries while folk and hip-hop have only one. A folk fan will always get the same single match; the remaining slots are filled by whatever scores highest regardless of genre fit.

- **Exact-match penalty** — genre and mood scoring is all-or-nothing. Closely related genres (e.g. `"indie"` vs `"indie pop"`) score zero for a genre match. A user who writes `"indie"` gets no credit for songs tagged `"indie pop"`, even though they are sonically similar. This punishes genre labels that vary in spelling or specificity.

- **Energy dominates numerically** — energy carries the largest numerical weight (0.25) of any single feature. When genre and mood both miss, the system effectively becomes an energy-proximity ranker. Users in underrepresented genres will always see their results skewed toward songs whose energy happens to be closest, regardless of genre or mood fit.

- **`likes_acoustic` forces extremes** — the boolean is converted to a hard target of 0.8 (True) or 0.2 (False). A user indifferent to acousticness, or preferring a mid-range value like 0.5, is silently misrepresented by whichever option they pick.

- **No diversity** — the system always returns the top *k* closest matches. If several songs share a genre and similar energy, the top results can be nearly identical, offering no discovery or variety.

- **Western/English catalog assumption** — all 18 songs reflect Western genre labels (pop, rock, jazz, etc.) and English naming conventions. Users whose taste falls outside these categories have no path to a good recommendation.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

