# Original Project - Music Recommener Stimulation

## Project Summary

This project is a rule-based music recommender simulation that suggests songs from a small 18-track catalog based on a user's preferred genre, mood, and energy level. Each song is scored using a weighted formula that rewards genre and mood matches and penalizes energy distance, then the top results are returned with plain-language explanations. It was built to explore how recommender systems turn structured data into ranked predictions, and to surface the tradeoffs and biases that emerge even in simple scoring logic.

---

# Agentic Music Recommender

## Summary

This project extends the original rule-based simulation into a fully agentic music recommender powered by Claude and the Spotify API. Users describe what they want to listen to in natural language, and a Claude agent iteratively searches Spotify, scores and ranks candidates using audio features, and returns personalized picks with explanations — all through a Streamlit chat interface. Unlike the original fixed pipeline, the agent decides how many searches to run and how to refine its query based on intermediate results, making the recommendation process dynamic and conversational.

# Architecture Overview

![System Architecture](assets/mermaid.png)

# Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/doublehan2023/music-recommender-ai-agent.git
cd music-recommender-ai-agent
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # Mac / Linux
.venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up API keys

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=your_anthropic_api_key
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

- Get your Anthropic API key at [console.anthropic.com](https://console.anthropic.com)
- Get your Spotify credentials at [developer.spotify.com](https://developer.spotify.com/dashboard)

### 5. Run the original CLI simulation

```bash
python -m src.main
```

### 6. Run the Streamlit app

```bash
streamlit run app.py
```

### 7. Run tests

```bash
pytest
```
---

# Sample Interactions

## Example 1 — Chill study music

**Input:** *"something chill for studying late at night"*

**Output:**
> Here are 5 chill picks perfect for a late-night study session — all low-energy, mellow, and easy to keep on in the background without breaking your focus:
>
> 1. **"Late Night Study" — The LoFi Bear** — Title says it all — gentle lofi with low energy (~0.25) and a warm acoustic feel that won't pull your attention from the page.
> 2. **"Study Time" — Chilled Cat** — Soft, steady, and unobtrusive — a classic chill-lofi groove tailor-made for deep reading or note-taking.
> 3. **"Chill Work Music" — Ambient Desk Music Co.** — The most ambient of the bunch — very high acousticness (~0.78) and slow tempo for a quiet, late-hour focus zone.
> 4. **"Lofi Music" — Lofi Sleep Chill & Study** — A balanced lofi loop — calm enough to relax you, with just enough rhythmic pulse to keep you awake at 1 AM.
> 5. **"Late Night Beats" — Lofi Sleep Chill & Study** — Slightly more groove (energy ~0.30) for when you need a small momentum boost without losing the chill vibe.

---

## Example 2 — High energy workout, no lyrics

**Input:** *"high energy workout music, no lyrics preferred"*

**Output:**
> Here are 5 high-energy, instrumental workout tracks — all packed with driving beats and zero vocals to keep you locked in:
>
> 1. **"Hard Electronic Workout" — Fitness & Workout Hits 2019** — Maxed-out energy (~0.95) with a punchy 140 BPM and almost no acoustic softness — pure electronic adrenaline for heavy lifts.
> 2. **"Dubstep Workout" — Fitness & Workout Hits 2019** — The most intense pick at ~0.96 energy and 145 BPM — heavy bass drops to push you through the toughest sets.
> 3. **"Heavy EDM Gym Banger" — Motivational Music** — Pure EDM banger energy (~0.94) at 140 BPM — great for pushing tempo on the treadmill or bike.
> 4. **"Super Duper Stonk" — EDM Machine** — Hard-hitting instrumental EDM at 138 BPM — lyric-free intensity that keeps your focus on the rep, not the words.
> 5. **"Drum and Bass Running Music" — Workout Music** — A blistering 174 BPM DnB track — perfect for sprint intervals or cranking cadence on a run.

---

## Example 3 — Sad indie, rainy day

**Input:** *"sad indie songs for a rainy day"*

**Output:**
> Here are 5 sad indie songs perfect for a rainy day — all low-energy, acoustic-leaning, and melancholic:
>
> 1. **"Out To Pasture" — Good Morning** — Mellow Aussie indie with hushed vocals and a quiet, contemplative pace that pairs beautifully with grey skies.
> 2. **"Only One" — The Neighborly** — Tender bedroom-pop loneliness with a warm acoustic foundation — perfect for staring out a foggy window.
> 3. **"The Trembling Waltz" — Novelley** — Highly acoustic and gently somber — its waltzing rhythm feels like raindrops tapping the glass.
> 4. **"Goodbye" — Pete McCredie** — A wistful indie-folk farewell with soft strums and aching emotion to soundtrack quiet reflection.
> 5. **"novocaine (sad song) (with rain)" — moody** — Comes with literal rain sounds baked in — a numb, slow-burning track tailor-made for this exact mood.

---

# Design Decisions

## Claude as the orchestrator, not just the output layer

The agent uses Claude (claude-opus-4-7) to decide *how* to search — which queries to run, how many, and when to stop — rather than following a fixed pipeline. This means the system can adapt: if a first search for "sad indie" yields weak results, the agent refines the query on its own. The trade-off is cost and latency. Each request involves multiple API roundtrips, making it slower and more expensive than a traditional recommender. For a production system this would matter, but for a conversational tool where quality is the priority it's the right call.

## Tool use over a single prompt

Recommendation is split into four discrete tools (`search_tracks`, `get_audio_features`, `score_and_rank`, `explain_recommendation`) rather than asking Claude to do everything in one prompt. This keeps each step inspectable and debuggable — you can see in `agent.log` exactly what the agent searched for, what scores came back, and where it failed. The alternative (one big prompt) is simpler but produces a black box where it's impossible to tell whether a bad recommendation came from a bad search or bad scoring.

## Rule-based scoring alongside Claude

The `score_and_rank` tool uses a deterministic formula (energy distance, genre/mood match, acoustic preference) rather than asking Claude to rank tracks directly. This makes scoring consistent and testable — the 11 unit tests in `tests/` verify exact behavior. The downside is the scoring is simple and misses nuance that Claude would catch (e.g. cultural associations with a genre). In practice, the search step does most of the heavy lifting and scoring refines from there.

## Graceful degradation for deprecated APIs

Spotify deprecated their `/audio-features` endpoint in November 2024. Rather than hard-failing, `get_audio_features` catches the exception and returns an empty list, and the agent falls back to ranking by search relevance and track metadata alone. This keeps the app functional at the cost of less precise scoring. The agent also transparently tells the user when features were unavailable, so outputs are honest about their confidence.

---

# Testing Summary

## What worked

**The agentic search loop** performed better than expected. Claude consistently chose useful query refinements — when "sad indie" returned tracks that felt too upbeat, it would follow up with "melancholic indie folk acoustic" without being told to. This kind of iterative behavior is hard to get from a fixed pipeline and was the biggest win of the agentic approach.

**Unit tests caught real bugs.** Writing tests for `score_song` immediately surfaced two `KeyError` crashes — one where `None == None` triggered a genre match on songs with no genre field, and one where the energy reason string used `song['energy']` directly instead of the default-safe value already computed. Both would have been silent failures in production.

**Graceful degradation worked cleanly.** After Spotify deprecated `/audio-features`, wrapping it in a try/except kept the app fully functional. Claude adapted by leaning on track titles, artist names, and search relevance to make recommendations — and was transparent with the user when numeric features weren't available.

## What didn't work

**Scoring is mostly decorative.** Because Spotify's audio features endpoint is deprecated, `score_and_rank` runs on default values (0.5 for everything) for most tracks, so it rarely changes the ordering that search already returned. The scoring infrastructure is sound but needs a data source to feed it.

**Search limit restrictions.** Spotify's Development Mode apps return a 400 error for limits above 10, and required an explicit `market` parameter that isn't documented prominently. This cost time to debug and silently broke the app until the limit was clamped and the parameter added.

**The `Recommender` class is a stub.** The original OOP `Recommender` and `explain_recommendation` methods in `src/recommender.py` still have placeholder implementations. They pass tests only because the tests don't assert on the correctness of the output, just its type.

## What I learned

Building an agentic system exposed a class of bugs that unit tests alone don't catch — the agent would occasionally call tools in an unexpected order or pass slightly wrong input shapes, and those failures only showed up at runtime. Structured logging (`agent.log`) was essential for diagnosing them: seeing the exact tool inputs and outputs per request made it possible to trace exactly where the agent went off course. For any future agentic project, logging tool calls from the start is worth doing on day one.

---

# Reflection

The biggest shift this project caused in how I think about AI was moving from "what does the model output?" to "what decisions does the model make?" In the original rule-based recommender, every step was explicit — I wrote the scoring formula, I chose the weights, I decided what counted as a match. The agentic version delegates those decisions to Claude: which search query to run, when to retry, how to explain a pick. That's a fundamentally different relationship with the code. You're no longer the author of the logic, you're the author of the constraints around it.

That was uncomfortable at first. When a recommendation came out wrong, it wasn't obvious whether the problem was the system prompt, the tool design, the search query Claude chose, or the scoring formula — there were too many moving parts. This is where structured logging became essential, not as an afterthought but as the primary debugging tool. Reading `agent.log` line by line and tracing a bad result back to a specific tool call was the only reliable way to understand what happened.

I also learned that external APIs are a bigger reliability risk than the AI itself. The Spotify `/audio-features` deprecation broke a core assumption of the system mid-build, and there was no warning — it just started returning errors. Building in graceful fallbacks and not over-relying on any single data source became a design principle I'd apply from the start next time.

The broader lesson: AI doesn't reduce the need for good engineering; it raises the stakes for it. A poorly structured prompt or a missing try/except doesn't just produce a bug, it produces a confident-sounding wrong answer, which is harder to catch and more damaging to trust.