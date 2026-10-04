import streamlit as st
import json
import os
from datetime import datetime
import random
from openai import OpenAI

st.set_page_config(
    page_title="Pip AI Studio",
    page_icon="🦊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        min-height: 3rem;
        font-size: 1.1rem;
        border-radius: 12px;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    code {
        white-space: pre-wrap !important;
        word-break: break-word !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

DATA_FILE = "pip_data.json"

CHARACTER_BIBLE = """Pip is a tiny adorable teal-blue fox with:
- Oversized expressive amber-gold eyes
- Small rounded ears
- Tiny dark nose
- Short legs and rounded paws
- Fluffy oversized tail with cream-colored tip
- Bright yellow scarf (always present, never changes)
- Soft rounded / plush-like proportions
- Curious, kind, expressive personality
- Completely original design – must NEVER resemble any existing copyrighted cartoon character"""

STYLE_LOCK = """High-quality polished 3D children's animation, warm cinematic lighting, soft rounded shapes, colorful natural environments, expressive faces, detailed but appealing, 9:16 vertical, action centered for mobile viewing, ages 4–9."""

SYSTEM_PROMPT = f"""You are the expert creative director for an original children's YouTube Shorts series starring Pip the teal-blue fox.

CHARACTER BIBLE (follow 100%):
{CHARACTER_BIBLE}

VISUAL STYLE:
{STYLE_LOCK}

STRICT STORY RULES:
- 25–35 seconds spoken length
- Structure (non-negotiable for retention):
  0–2s: Immediate visual hook (something already happening)
  2–7s: Pip reacts and chases/investigates
  7–14s: Escalation + gentle funny obstacle/near-miss
  14–22s: Pip succeeds + notices someone/something needing kindness
  22–28s: Pip chooses to share or help
  28–34s: Happy payoff + small visual gag (leaf, butterfly, confused look, etc.)
- Family-friendly, understandable without sound
- Completely original – zero copying of existing characters or stories
- Warm, curious, kind, gently funny tone

OUTPUT ONLY valid JSON with these exact keys:
{{
  "title": "catchy short title",
  "story_summary": "2-4 sentences",
  "narration": "short punchy sentences, ~28 seconds",
  "shot_plan": [
    {{"shot": 1, "duration": "4-5s", "description": "...", "camera": "...", "expression": "...", "prompt_addition": "specific visual details for this shot"}},
    ... exactly 7 shots
  ],
  "captions": ["max 6 words each"],
  "youtube_description": "ready to paste",
  "hashtags": "#PipTheFox ...",
  "thumbnail_concept": "short visual description for thumbnail",
  "why_it_works": "1-2 sentences on retention/hook strength"
}}
"""

THEME_BANK = [
    "runaway object that needs sharing",
    "helping a tiny animal in trouble",
    "discovering something shiny",
    "funny weather surprise",
    "making a new tiny friend",
    "lost item that leads to kindness",
    "gentle race with a silly obstacle",
    "sharing food with someone hungrier",
    "a magical-looking leaf or flower",
    "helping build a tiny home",
    "a sleepy creature that needs rest",
    "chasing a floating feather or balloon"
]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "episodes": [],
        "next_episode_number": 1,
        "character_bible": CHARACTER_BIBLE.strip(),
        "style_lock": STYLE_LOCK.strip(),
        "api_provider": "groq",
        "api_key": "",
        "model": "llama-3.3-70b-versatile",
        "onboarded": False
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_client(provider, api_key):
    if not api_key:
        return None
    base_urls = {
        "groq": "https://api.groq.com/openai/v1",
        "openrouter": "https://openrouter.ai/api/v1",
        "xai": "https://api.x.ai/v1",
        "openai": "https://api.openai.com/v1",
        "together": "https://api.together.xyz/v1",
    }
    return OpenAI(api_key=api_key, base_url=base_urls.get(provider.lower(), base_urls["groq"]))

def generate_with_llm(client, model, theme_hint=None, past_titles=None):
    user_msg = "Generate a brand new original Pip the Fox YouTube Short production package."
    if theme_hint and theme_hint.strip():
        user_msg += f"\nTheme direction: {theme_hint.strip()}"
    if past_titles:
        user_msg += f"\nAvoid repeating these recent titles: {', '.join(past_titles[-8:])}"
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg}
        ],
        temperature=0.88,
        max_tokens=3000,
        response_format={"type": "json_object"}
    )
    package = json.loads(response.choices[0].message.content)
    required = ["title", "story_summary", "narration", "shot_plan", "captions", "youtube_description", "hashtags"]
    for k in required:
        if k not in package:
            raise ValueError(f"Missing key: {k}")
    return package

def generate_fallback(theme_hint=None):
    theme = theme_hint if theme_hint else random.choice(THEME_BANK)
    return {
        "title": f"Pip & the {theme.title()}",
        "story_summary": f"Pip notices something related to '{theme}'. He reacts with curiosity and energy, faces a small gentle obstacle, then discovers a chance to be kind. He helps or shares and ends with a funny visual gag.",
        "narration": "Whoa—look at that!\nPip sees it right away!\nRun, Pip, run!\nAlmost… oh no!\nHe keeps going!\nGot it!\nBut wait… who needs help?\nPip shares!\nHappy ending!\nHuh… what’s on my head?",
        "shot_plan": [
            {"shot": 1, "duration": "4-5s", "description": "Immediate visual hook – something already happening. Pip reacts.", "camera": "dynamic low angle", "expression": "surprised", "prompt_addition": "bright object already in motion"},
            {"shot": 2, "duration": "4-5s", "description": "Pip races or investigates with energy.", "camera": "side tracking", "expression": "determined", "prompt_addition": "scarf and tail flowing"},
            {"shot": 3, "duration": "4-5s", "description": "Gentle funny near-miss or obstacle.", "camera": "slight dip and recover", "expression": "surprised then determined", "prompt_addition": "soft comedic slip"},
            {"shot": 4, "duration": "4-5s", "description": "Pip succeeds.", "camera": "push-in", "expression": "proud", "prompt_addition": "happy sparkling eyes"},
            {"shot": 5, "duration": "4-5s", "description": "Pip notices someone needing kindness.", "camera": "gentle reveal", "expression": "kind", "prompt_addition": "tiny creature or object in need"},
            {"shot": 6, "duration": "4-5s", "description": "Pip shares or helps. Happy payoff.", "camera": "soft orbit", "expression": "happy", "prompt_addition": "warm glowing light"},
            {"shot": 7, "duration": "3-4s", "description": "Small visual gag. Hold ending.", "camera": "subtle push-in", "expression": "confused", "prompt_addition": "leaf or butterfly lands on head"}
        ],
        "captions": ["Whoa—look at that!", "Pip sees it!", "Run, Pip, run!", "Almost… oh no!", "Got it!", "Who needs help?", "Pip shares!", "Happy!", "Huh… a leaf?"],
        "youtube_description": f"Pip is back!\n\nPip & the {theme.title()}\n\nA short original story about kindness and curiosity.\n\nNew Pip Shorts every week!\n\n#PipTheFox #KidsShorts",
        "hashtags": "#PipTheFox #KidsAnimation #ChildrensShorts #CartoonShorts #PipAndFriends #SharingIsCaring #YouTubeKids",
        "thumbnail_concept": "Close-up of Pip’s big amber eyes looking surprised, bright object in foreground, warm lighting, big readable title text",
        "why_it_works": "Strong immediate hook + clear escalation + satisfying kindness payoff + replayable gag."
    }

def make_full_prompts(package):
    base = package.get("prompt_base", "")
    prompts = []
    for shot in package.get("shot_plan", []):
        addition = shot.get("prompt_addition", shot.get("description", ""))
        full = f"{base}\n\nSHOT {shot['shot']} ({shot.get('duration','')}):\n{shot['description']}\nCamera: {shot.get('camera','')}\nExpression: {shot.get('expression','')}\nExtra details: {addition}"
        prompts.append(full)
    return prompts

def package_to_markdown(package):
    md = f"""# {package.get('title', 'Untitled')}
**Episode #{package.get('episode_number')}** • {package.get('created_at')} • Source: {package.get('generation_source')}

## Story Summary
{package.get('story_summary')}

## Narration
{package.get(‘narration’)}
## Shot Plan
"""
    for s in package.get("shot_plan", []):
        md += f"- **Shot {s['shot']}** ({s.get('duration')}): {s['description']} | Camera: {s.get('camera','')} | Expression: {s.get('expression','')}\n"
    
    md += f"""
## Captions
{chr(10).join(package.get('captions', []))}

## YouTube Description
{package.get(‘youtube_description’)}
  ## Hashtags
{package.get('hashtags')}

## Thumbnail Concept
{package.get('thumbnail_concept', '')}

## Why it works
{package.get('why_it_works', '')}

## Base Prompt Lock
{package.get(‘prompt_base’, ‘’)}
  """
    return md

data = load_data()

with st.sidebar:
    st.title("🦊 Pip AI Studio")
    st.caption("v0.3 • Mobile Ready")
    
    st.header("🔑 AI Connection")
    provider = st.selectbox("Provider", ["groq", "openrouter", "xai", "openai", "together"],
                            index=["groq","openrouter","xai","openai","together"].index(data.get("api_provider","groq")))
    api_key = st.text_input("API Key", value=data.get("api_key",""), type="password")
    model = st.text_input("Model", value=data.get("model", "llama-3.3-70b-versatile"))
    
    if st.button("💾 Save Connection", use_container_width=True):
        data["api_provider"] = provider
        data["api_key"] = api_key
        data["model"] = model
        save_data(data)
        st.success("Saved!")
    
    connected = bool(data.get("api_key"))
    if connected:
        st.success("✅ AI Connected")
    else:
        st.warning("⚠️ Using template mode\nAdd API key for real AI stories")
    
    st.divider()
    st.header("Character Lock")
    st.text_area("Pip Bible", value=data["character_bible"], height=160, disabled=True)
    
    st.metric("Next Episode", data["next_episode_number"])
    if st.button("Reset Counter", use_container_width=True):
        data["next_episode_number"] = 1
        save_data(data)
        st.rerun()

st.title("🦊 Pip AI Studio")
st.caption("Create original YouTube Shorts with consistent characters • Works on iPhone")

if not data.get("onboarded"):
    with st.expander("👋 First time? Tap here for quick start", expanded=True):
        st.markdown("""
        **3 steps to your first Short:**
        1. (Optional) Add a free API key in the sidebar for real AI stories (Groq is easiest)
        2. Tap **Generate New Episode** below
        3. Copy the prompts and use them in Grok / Kling / CapCut
        
        Everything stays locked to Pip’s design so he never changes.
        """)
        if st.button("Got it – start creating!", use_container_width=True):
            data["onboarded"] = True
            save_data(data)
            st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(["🎬 Create", "📚 Library", "🖼️ Prompts", "📱 Help"])

with tab1:
    st.subheader("Generate New Episode")
    
    theme_hint = st.text_input("Theme idea (optional)", placeholder="e.g. runaway balloon, helping a baby bird, rainy day...")
    
    colA, colB = st.columns(2)
    with colA:
        use_ai = st.toggle("Use Real AI", value=bool(data.get("api_key")), help="Requires API key in sidebar")
    with colB:
        st.write("")
    
    if st.button("🚀 Generate Next Episode", type="primary", use_container_width=True):
        ep_num = data["next_episode_number"]
        past_titles = [e.get("title","") for e in data["episodes"]]
        
        with st.spinner("Creating original story..."):
            try:
                client = get_client(data.get("api_provider","groq"), data.get("api_key",""))
                if use_ai and client and data.get("api_key"):
                    package = generate_with_llm(client, data.get("model","llama-3.3-70b-versatile"), theme_hint, past_titles)
                    source = "Real AI"
                else:
                    package = generate_fallback(theme_hint)
                    source = "Smart Template"
                
                package["episode_number"] = ep_num
                package["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                package["generation_source"] = source
                package["prompt_base"] = f"""High-quality polished 3D children’s animation, warm cinematic lighting, soft rounded plush-like proportions, colorful natural environment. Consistent original character: tiny adorable teal-blue fox named Pip, oversized expressive amber-gold eyes, small rounded ears, tiny dark nose, short legs and rounded paws, fluffy oversized tail with cream-colored tip, bright yellow scarf, soft rounded body. Keep face, eyes, fur color, scarf, body proportions, ears, paws and tail identical. No redesign, no extra accessories, no morphing. 9:16 vertical, action centered, smooth natural motion."""
                
                data["episodes"].insert(0, package)
                data["next_episode_number"] = ep_num + 1
                save_data(data)
                
                st.success(f"✅ Episode {ep_num} ready! ({source})")
                if source == "Real AI":
                    st.balloons()
                
                st.markdown(f"### {package['title']}")
                st.caption(f"Episode #{ep_num} • {package['created_at']} • {source}")
                
                st.markdown("**Story Summary**")
                st.info(package["story_summary"])
                
                st.markdown("**Narration** (copy this)")
                st.code(package["narration"], language=None)
                
                with st.expander("Full Shot Plan"):
                    for s in package["shot_plan"]:
                        st.markdown(f"**Shot {s['shot']}** ({s.get('duration')}) – {s['description']}  
Camera: {s.get('camera')} | Expression: {s.get('expression')}")
                
                st.markdown("**Captions**")
                st.code("\n".join(package["captions"]), language=None)
                
                st.markdown("**YouTube Description**")
                st.code(package["youtube_description"], language=None)
                
                st.markdown("**Hashtags**")
                st.code(package["hashtags"], language=None)
                
                if package.get("thumbnail_concept"):
                    st.markdown("**Thumbnail Idea**")
                    st.write(package["thumbnail_concept"])
                
                md_content = package_to_markdown(package)
                st.download_button(
                    label="📥 Download Full Package (.md)",
                    data=md_content,
                    file_name=f"Pip_Episode_{ep_num}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"Error: {e}")
                st.info("Try again or switch to template mode.")

with tab2:
    st.subheader("Episode Library")
    
    if not data["episodes"]:
        st.info("No episodes yet. Go to the Create tab!")
    else:
        st.write(f"Total episodes: **{len(data['episodes'])}**")
        
        search = st.text_input("Search titles or themes", "")
        
        for ep in data["episodes"]:
            if search and search.lower() not in ep.get("title","").lower() and search.lower() not in ep.get("story_summary","").lower():
                continue
            
            with st.expander(f"#{ep['episode_number']}  {ep['title']}  •  {ep.get('created_at','')}"):
                st.caption(f"Source: {ep.get('generation_source','—')}")
                st.write(ep.get("story_summary",""))
                
                st.markdown("**Narration**")
                st.code(ep.get("narration",""), language=None)
                
                col1, col2 = st.columns(2)
                with col1:
                    md = package_to_markdown(ep)
                    st.download_button("📥 Download", data=md, file_name=f"Pip_Ep{ep['episode_number']}.md",
                                       mime="text/markdown", key=f"dl_{ep['episode_number']}")
                with col2:
                    if st.button("🗑️ Delete", key=f"del_{ep['episode_number']}"):
                        data["episodes"] = [e for e in data["episodes"] if e["episode_number"] != ep["episode_number"]]
                        save_data(data)
                        st.rerun()

with tab3:
    st.subheader("Ready-to-Use Video Prompts")
    st.caption("Pick an episode → get detailed prompts for every shot")
    
    if not data["episodes"]:
        st.info("Generate an episode first.")
    else:
        titles = [f"#{e['episode_number']} – {e['title']}" for e in data["episodes"]]
        choice = st.selectbox("Choose episode", titles)
        idx = titles.index(choice)
        selected = data["episodes"][idx]
        
        st.markdown(f"### {selected['title']}")
        
        st.markdown("**1. Base Character Lock** (paste this first)")
        st.code(selected.get("prompt_base", ""), language=None)
        
        st.markdown("**2. Individual Shot Prompts**")
        full_prompts = make_full_prompts(selected)
        for i, p in enumerate(full_prompts):
            with st.expander(f"Shot {i+1} Prompt"):
                st.code(p, language=None)

with tab4:
    st.subheader("How to use on iPhone")
    
    st.markdown("""
    ### Open on iPhone
    1. After the app is running, open the link in **Safari**
    2. Tap Share → **Add to Home Screen**
    3. Name it “Pip AI”
    
    ### Free AI keys
    - Groq: console.groq.com → model `llama-3.3-70b-versatile`
    - OpenRouter: openrouter.ai
    
    ### Workflow
    1. Generate episode here
    2. Copy Base Prompt + Shot prompts
    3. Create stills in Grok Imagine
    4. Animate in free Kling
    5. Assemble in CapCut
    6. Upload
    """)
    
    st.divider()
    st.markdown("**Theme ideas**")
    st.write(", ".join(THEME_BANK))

st.divider()
st.caption("Pip AI Studio v0.3 • Works on iPhone • Keep Pip consistent")
