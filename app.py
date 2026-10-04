import streamlit as st
import json
import os
from datetime import datetime
import random
from openai import OpenAI

st.set_page_config(page_title="Pip AI Studio", page_icon="🦊", layout="centered")

DATA_FILE = "pip_data.json"

CHARACTER_BIBLE = """Pip is a tiny adorable teal-blue fox with oversized amber-gold eyes, small rounded ears, tiny dark nose, short legs, rounded paws, fluffy tail with cream tip, and a bright yellow scarf. Soft rounded proportions. Curious and kind. Completely original character."""

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "episodes": [],
        "next_episode_number": 1,
        "api_key": "",
        "model": "llama-3.3-70b-versatile"
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def generate_fallback():
    themes = ["runaway balloon", "helping a baby bird", "shiny lost button", "rainy day adventure", "sleepy squirrel"]
    theme = random.choice(themes)
    return {
        "title": f"Pip & the {theme.title()}",
        "summary": f"Pip notices something related to {theme}. He reacts, faces a small funny problem, then helps someone and ends with a silly gag.",
        "narration": "Whoa look at that!\nPip sees it!\nRun Pip run!\nAlmost... oh no!\nGot it!\nWho needs help?\nPip shares!\nHappy ending!\nHuh... a leaf?",
        "captions": ["Whoa look at that!", "Pip sees it!", "Run Pip run!", "Almost oh no!", "Got it!", "Who needs help?", "Pip shares!", "Happy!", "Huh a leaf?"],
        "description": f"Pip is back with a new adventure!\n\nPip & the {theme.title()}\n\nA short original story about kindness.\n\n#PipTheFox #KidsShorts",
        "hashtags": "#PipTheFox #KidsShorts #CartoonForKids #FamilyFriendly"
    }

data = load_data()

st.title("🦊 Pip AI Studio")
st.caption("Simple version for iPhone")

st.subheader("Character Lock")
st.info(CHARACTER_BIBLE)

st.subheader("API Key (optional)")
api_key = st.text_input("Groq or OpenRouter API Key", value=data.get("api_key", ""), type="password")
if st.button("Save API Key"):
    data["api_key"] = api_key
    save_data(data)
    st.success("Saved")

st.divider()

if st.button("🚀 Generate New Episode", type="primary"):
    ep_num = data["next_episode_number"]
    package = generate_fallback()
    package["episode_number"] = ep_num
    package["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    data["episodes"].insert(0, package)
    data["next_episode_number"] = ep_num + 1
    save_data(data)

    st.success(f"Episode {ep_num} created!")
    st.subheader(package["title"])
    st.write(package["summary"])
    st.markdown("**Narration**")
    st.code(package["narration"])
    st.markdown("**Captions**")
    st.code("\n".join(package["captions"]))
    st.markdown("**YouTube Description**")
    st.code(package["description"])
    st.markdown("**Hashtags**")
    st.code(package["hashtags"])

st.divider()
st.subheader("Past Episodes")

if not data["episodes"]:
    st.write("No episodes yet.")
else:
    for ep in data["episodes"]:
        with st.expander(f"#{ep['episode_number']} - {ep['title']}"):
            st.write(ep["summary"])
            st.code(ep["narration"])

st.caption("Pip AI Studio - Simple Version")
