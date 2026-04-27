import json
import os
from dotenv import load_dotenv
import anthropic
from src.spotify_client import SpotifyClient
from src.recommender import recommend_songs

load_dotenv()

TOOLS = [
    {
        "name": "search_tracks",
        "description": "Search Spotify for tracks matching a query. Use genre, mood, or descriptive keywords.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query, e.g. 'chill lofi beats' or 'energetic hip-hop workout'"},
                "limit": {"type": "integer", "description": "Number of results to return (max 10)", "default": 10}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_audio_features",
        "description": "Fetch audio features (energy, valence, tempo, danceability, acousticness) for a list of Spotify track IDs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "track_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of Spotify track IDs"
                }
            },
            "required": ["track_ids"]
        }
    },
    {
        "name": "score_and_rank",
        "description": "Score and rank a list of enriched tracks against user preferences. Returns top-k with scores and reasons.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tracks": {
                    "type": "array",
                    "description": "List of enriched track dicts (must have energy, valence, tempo_bpm, acousticness)"
                },
                "user_prefs": {
                    "type": "object",
                    "description": "User preference dict with optional keys: genre, mood, energy (0-1), likes_acoustic (bool)"
                },
                "k": {"type": "integer", "description": "Number of top results to return (default 5)", "default": 5}
            },
            "required": ["tracks", "user_prefs"]
        }
    },
    {
        "name": "explain_recommendation",
        "description": "Generate a short personalized explanation for why a track suits the user's request.",
        "input_schema": {
            "type": "object",
            "properties": {
                "track": {"type": "object", "description": "The track dict"},
                "user_request": {"type": "string", "description": "The original user request"},
                "score_reasons": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of scoring reasons from score_and_rank"
                }
            },
            "required": ["track", "user_request"]
        }
    }
]

SYSTEM_PROMPT = """You are an expert music recommender agent with access to the Spotify catalog.

When a user describes what they want to listen to:
1. Search Spotify with relevant queries (try different genres/moods if first results are weak)
2. Fetch audio features for the candidate tracks
3. Score and rank them against inferred user preferences
4. Explain each top pick in one sentence tied to their request

Extract user preferences from their description:
- Energy (0.0 = very calm, 1.0 = very intense)
- Mood keywords (chill, happy, intense, melancholic, focused)
- Genre hints
- Acoustic preference

Be iterative: if the first search doesn't yield good matches, refine the query and try again.
Return exactly 5 recommendations unless the user asks for a different number."""


def _execute_tool(name: str, tool_input: dict, spotify: SpotifyClient) -> str:
    if name == "search_tracks":
        tracks = spotify.search_tracks(tool_input["query"], tool_input.get("limit", 20))
        return json.dumps(tracks)

    if name == "get_audio_features":
        features = spotify.get_audio_features(tool_input["track_ids"])
        return json.dumps(features)

    if name == "score_and_rank":
        results = recommend_songs(
            tool_input["user_prefs"],
            tool_input["tracks"],
            tool_input.get("k", 5)
        )
        output = [
            {"track": song, "score": round(score, 3), "reasons": reasons}
            for song, score, reasons in results
        ]
        return json.dumps(output)

    if name == "explain_recommendation":
        track = tool_input["track"]
        request = tool_input["user_request"]
        reasons = tool_input.get("score_reasons", [])
        reason_text = "; ".join(reasons) if reasons else "audio features match your request"
        explanation = (
            f"\"{track.get('title', 'Unknown')}\" by {track.get('artist', 'Unknown')} — "
            f"fits your request for \"{request}\": {reason_text}."
        )
        return explanation

    return json.dumps({"error": f"Unknown tool: {name}"})


def run_agent(user_message: str, history: list[dict] | None = None) -> dict:
    """
    Run the music recommender agent for one turn.

    Args:
        user_message: The user's natural language request.
        history: Optional prior conversation turns for multi-turn sessions.

    Returns:
        dict with keys: 'response' (str), 'messages' (list)
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    spotify = SpotifyClient()

    messages = list(history or [])
    messages.append({"role": "user", "content": user_message})

    while True:
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            final_text = next(
                (block.text for block in response.content if block.type == "text"), ""
            )
            return {"response": final_text, "messages": messages}

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = _execute_tool(block.name, block.input, spotify)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            messages.append({"role": "user", "content": tool_results})
            continue

        break

    return {"response": "Agent stopped unexpectedly.", "messages": messages}
