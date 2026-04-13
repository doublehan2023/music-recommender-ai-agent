# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias

Where the system struggles or behaves unfairly.

### Features the system ignores

Three song attributes — tempo (BPM), valence, and danceability — are loaded from the dataset but never used in scoring. A user who loves fast danceable songs and a user who prefers slow ballads could receive identical recommendations if their genre, mood, and energy preferences are similar. The system also has no concept of artist familiarity, release date, or listening history, so it cannot surface new artists or avoid recommending the same song repeatedly.

### Exact-match bias on genre and mood

Genre and mood are compared as exact text strings. "indie pop" is treated as completely different from "pop", and "chill" has nothing in common with "relaxed" as far as the scorer is concerned. A user who prefers indie pop receives zero genre points against every pop song in the catalog, even though those songs are closely related. Users whose preferred genre or mood label happens to match the catalog's exact wording are rewarded; users with synonyms or sub-genres are not.

### Underrepresented catalog entries

If the catalog contains very few songs in a given genre or mood, users with those preferences will rarely see a genre or mood match in their top results. Their rankings fall back entirely on energy and acousticness proximity, which means two users with completely different taste profiles could receive the same list if their energy targets are similar.

### The calm-music blind spot (energy = 0.0)

Due to how Python evaluates zero as false, a user who sets their target energy to exactly 0.0 — meaning they want the calmest possible songs — has their energy preference silently ignored. The system behaves as if they expressed no energy preference at all. This disproportionately affects users who explicitly want quiet or ambient music.

### Hard thresholds on acousticness create a dead zone

The acousticness bonus is awarded only if a song scores 0.6 or above (for users who like acoustic) or 0.4 or below (for users who do not). A song at 0.59 receives nothing; a song at 0.60 receives the full bonus. Songs with no acousticness data default to 0.5, which falls in neither bucket — these songs are permanently invisible to the acousticness signal regardless of the user's preference.

### Tie-breaking favors catalog order

When two songs score identically — which happens often when energy and acousticness are not specified — the system returns whichever song appears earlier in the CSV file. There is no random shuffling or secondary ranking criterion. Songs near the top of the dataset are systematically over-represented in results for users with loosely specified preferences.

### Energy dominance after reweighting

With energy weighted at 2.0 (double the original), a user with a precise energy target can surface songs with no genre or mood match ahead of songs that match both. This is intentional for energy-focused users, but it means a user who casually includes an energy value without strong feelings about it will still have that value dominate their recommendations in ways they may not expect.

---

## 7. Evaluation

How you checked whether the recommender behaved as expected.

### Profiles tested

Four adversarial user profiles were designed to probe specific weaknesses in the scoring logic rather than typical happy-path usage:

1. **Calm Seeker** — target energy of 0.0, genre pop, mood happy. Designed to trigger the silent energy-skip bug.
2. **Hyper Fan** — target energy of 1.5, genre pop, mood happy. Designed to test what happens when energy is out of the valid 0–1 range.
3. **Unknown Taste** — genre "baroque", mood "nostalgic". Neither label exists in the catalog, so genre and mood scoring always returns zero.
4. **Energy Purist** — genre pop, mood happy, energy 0.95. Used specifically to verify that doubling the energy weight changed rankings in a predictable, math-confirmed way.

### What we looked for

For each profile we checked whether the top results made intuitive sense given the stated preferences, whether scores could be hand-calculated from the formula, and whether any songs ranked surprisingly high or low compared to expectations.

### What the results showed

**Calm Seeker** returned the same results as if no energy preference had been given at all. Songs were ranked by genre and mood matches only, meaning a high-energy pop song scored identically to a low-energy one. This confirmed the `energy = 0.0` silent-skip bug.

**Hyper Fan** produced a case where the energy contribution went negative for songs far from 1.5. A song with energy 0.0 received an energy penalty of −1.0, pulling its total score below what a song with no match at all would receive. The ranking was technically sorted correctly, but the scores no longer had the expected 0–3.5 range.

**Unknown Taste** confirmed that when neither genre nor mood matches anything in the catalog, the entire top-5 is decided by energy distance to 0.5. Two stylistically unrelated songs — say a rock track and a lofi track — ranked back-to-back purely because their energy values were similar, with no other signal distinguishing them.

### Verifying the reweight with math

After doubling the energy weight and halving the genre weight, we manually computed expected scores for five songs under both the old and new formulas and compared them to the actual output. The rankings shifted in three measurable ways:

- **Gym Hero** dropped from rank 2 to rank 4. It matched the genre label but had weaker energy (0.93 vs target 0.95). Halving the genre bonus from 1.0 to 0.5 was not enough to compensate for the energy gap against songs that skipped the genre bonus entirely.
- **Bass Drop Friday** rose from rank 3 to rank 2. It matched neither the genre nor the artist style, but its energy (0.86) was close enough to the target that doubling the energy contribution pushed it above Gym Hero.
- **Thunder Circuit** entered the top 5 with a score of exactly 2.00 — zero genre points, zero mood points, purely on a perfect energy match of 0.95. Under the original weights it would have scored 1.0 and ranked outside the top 5 entirely.

All three shifts matched the hand-calculated predictions before running the code, which confirmed the weight changes were applied correctly and were producing the intended effect.

### What was surprising

The most unexpected finding was how drastically a single out-of-range energy value (1.5) corrupted rankings. A negative energy contribution is not an obvious failure — the list still returns five songs in sorted order and looks correct on the surface. Without checking the raw scores, this bug would be easy to miss in production. It highlighted that the scoring function assumes inputs are bounded between 0 and 1 but does nothing to enforce that assumption.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection

Building this system taught me that a recommender is not just a ranking algorithm — it is a set of assumptions about what users want, encoded as numbers. Every weight I chose (genre worth this much, energy worth that much) reflects a judgment call about whose taste the system is optimized for. When I doubled the energy weight, songs with no genre or mood match suddenly appeared in the top 5. That was not a bug; it was the system faithfully following the new assumption. It made me realize that in a real product, those weight decisions are often made by engineers or product managers, not users, and the people most affected by them rarely know the choices exist.

The most surprising discovery was how invisible some failures are. The `energy = 0.0` bug does not crash anything — the program runs, the output looks reasonable, and a user asking for calm music would have no idea their preference was silently ignored. The out-of-range energy bug was similar: the rankings still appeared sorted and plausible on the surface. Both failures were only visible when I checked the raw scores by hand. That changed how I think about testing: a system that returns output without errors is not the same as a system that is working correctly.

Before this project I thought of apps like Spotify or Apple Music as systems that "know" my taste. Now I see them differently — as weighted scorers that match features of songs against features of a user profile, with all the same blind spots this simulation has, just with more data and more features. The labels and moods in their catalogs are assigned by humans or classifiers, exact-match bias exists in any system that uses discrete categories, and someone decided how much energy matters relative to genre. The gap between a simple class project and a production recommender is scale and engineering polish, not a fundamentally different kind of logic.  
