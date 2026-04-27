import json
import os
import streamlit as st
import anthropic
from dotenv import load_dotenv
from src.agent import run_agent

load_dotenv()


def check_config() -> str | None:
    """Return an error message if required env vars are missing, else None."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        return "ANTHROPIC_API_KEY is not set. Add it to your .env file."
    if not os.getenv("SPOTIFY_CLIENT_ID"):
        return "SPOTIFY_CLIENT_ID is not set. Add it to your .env file."
    if not os.getenv("SPOTIFY_CLIENT_SECRET"):
        return "SPOTIFY_CLIENT_SECRET is not set. Add it to your .env file."
    return None

st.set_page_config(page_title="Music Recommender", page_icon="🎵", layout="wide")

st.title("🎵 Music Recommender")
st.caption("Describe what you want to listen to — I'll find the perfect tracks.")

config_error = check_config()
if config_error:
    st.error(f"**Configuration error:** {config_error}", icon="🔑")
    st.stop()

if "chat" not in st.session_state:
    st.session_state.chat = []        # display messages: {role, content, tracks?}
if "history" not in st.session_state:
    st.session_state.history = []     # agent conversation history (full message objects)


def extract_tracks(messages: list) -> list:
    """Pull the last score_and_rank result from the agent message history."""
    for msg in reversed(messages):
        if not isinstance(msg, dict):
            continue
        content = msg.get("content", [])
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_result":
                try:
                    data = json.loads(block["content"])
                    if isinstance(data, list) and data and "track" in data[0]:
                        return [item["track"] for item in data]
                except (json.JSONDecodeError, KeyError, TypeError):
                    continue
    return []


def render_song_card(track: dict):
    track_id = track.get("id", "")
    title = track.get("title", "Unknown")
    artist = track.get("artist", "Unknown")
    energy = track.get("energy", None)
    valence = track.get("valence", None)

    with st.container(border=True):
        col1, col2 = st.columns([2, 3])
        with col1:
            st.markdown(f"**{title}**")
            st.markdown(f"*{artist}*")
            if energy is not None:
                st.progress(energy, text=f"Energy: {energy:.0%}")
            if valence is not None:
                st.progress(valence, text=f"Positivity: {valence:.0%}")
        with col2:
            if track_id:
                st.components.v1.iframe(
                    f"https://open.spotify.com/embed/track/{track_id}?utm_source=generator",
                    height=80
                )
            else:
                st.markdown("_(no embed available)_")


# Render chat history
for turn in st.session_state.chat:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])
        if turn.get("tracks"):
            cols = st.columns(1)
            for track in turn["tracks"]:
                render_song_card(track)

# Handle new input
if prompt := st.chat_input("e.g. something chill for studying, energetic workout music..."):
    # Show user message
    st.session_state.chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Run agent
    with st.chat_message("assistant"):
        try:
            with st.spinner("Finding tracks..."):
                result = run_agent(prompt, history=st.session_state.history)

            response_text = result["response"]
            st.session_state.history = result["messages"]
            tracks = extract_tracks(result["messages"])

            st.markdown(response_text)
            for track in tracks:
                render_song_card(track)

            st.session_state.chat.append({
                "role": "assistant",
                "content": response_text,
                "tracks": tracks
            })

        except anthropic.AuthenticationError:
            st.error("**Invalid Anthropic API key.** Check the ANTHROPIC_API_KEY in your .env file.", icon="🔑")
        except anthropic.RateLimitError:
            st.warning("**Rate limit reached.** Wait a moment and try again.", icon="⏳")
        except anthropic.APIConnectionError:
            st.error("**Could not reach the Anthropic API.** Check your internet connection.", icon="🌐")
        except Exception as e:
            st.error(f"**Unexpected error:** {e}", icon="⚠️")
