from __future__ import annotations

from pathlib import Path
import sys
import streamlit as st

# Find the package whether the project files are at the repository root or one
# folder below it. This avoids ModuleNotFoundError when an extracted project
# folder is accidentally uploaded as a nested directory on GitHub.
APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = None
_search_roots = [APP_DIR]
try:
    _search_roots.extend(
        item for item in APP_DIR.iterdir()
        if item.is_dir() and not item.name.startswith(".")
    )
except OSError:
    pass

for _candidate in _search_roots:
    if (_candidate / "songposter" / "__init__.py").is_file():
        PROJECT_ROOT = _candidate
        if str(_candidate) not in sys.path:
            sys.path.insert(0, str(_candidate))
        break

if PROJECT_ROOT is None:
    st.set_page_config(page_title="Song Poster Studio", page_icon="🎧")
    st.title("🎧 Song Poster Studio")
    st.error("The application package folder is missing. Please upload the complete project files to GitHub.")
    st.markdown("The repository must contain `streamlit_app.py`, `requirements.txt`, and the `songposter/` folder.")
    st.code(
        "Lyric2Poster/\n"
        "├── streamlit_app.py\n"
        "├── requirements.txt\n"
        "├── songposter/\n"
        "│   ├── __init__.py\n"
        "│   ├── art_director.py\n"
        "│   └── ...\n"
        "└── data/"
    )
    st.stop()

ROOT = PROJECT_ROOT

try:
    from songposter.art_director import create_demo_brief
    from songposter.charts import load_tracks
    from songposter.image_engine import create_demo_artwork
    from songposter.limits import BRIEF_LIMIT, POSTER_LIMIT
    from songposter.models import ArtBrief
    from songposter.overlay import add_title_overlay
except ModuleNotFoundError as exc:
    st.set_page_config(page_title="Song Poster Studio", page_icon="🎧")
    st.title("🎧 Song Poster Studio")
    st.error(f"A required application module is missing: {exc.name}")
    st.info("Check that all files inside the songposter/ folder were uploaded to the repository.")
    st.stop()

st.set_page_config(
    page_title="Song Poster Studio",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)


def initialize_state() -> None:
    defaults = {
        "brief_count": 0,
        "poster_count": 0,
        "art_brief": None,
        "poster_png": None,
        "app_error": None,
        "chart_choice": "Custom song",
        "song_title": "",
        "artist_name": "",
        "poster_style": "Aurora",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def selected_track_changed(track_map: dict[str, dict[str, str]]) -> None:
    choice = st.session_state.get("chart_choice", "Custom song")
    track = track_map.get(choice)
    if track:
        st.session_state["song_title"] = track["title"]
        st.session_state["artist_name"] = track["artist"]
    st.session_state["art_brief"] = None
    st.session_state["poster_png"] = None


def create_brief_callback() -> None:
    """Consume lyrics in this callback, retain only the lyric-free brief."""
    lyrics = st.session_state.get("lyrics_input", "")
    title = st.session_state.get("song_title", "").strip()
    artist = st.session_state.get("artist_name", "").strip()
    style = st.session_state.get("poster_style", "Aurora")

    try:
        if st.session_state.get("brief_count", 0) >= BRIEF_LIMIT:
            st.session_state["app_error"] = f"Session limit reached ({BRIEF_LIMIT} briefs)."
        elif not title or not artist:
            st.session_state["app_error"] = "Please enter both a song title and an artist."
        elif not lyrics.strip():
            st.session_state["app_error"] = "Please enter some lyrics to create an art brief."
        else:
            brief = create_demo_brief(title=title, artist=artist, lyrics=lyrics, style=style)
            st.session_state["art_brief"] = brief.to_dict()
            st.session_state["poster_png"] = None
            st.session_state["brief_count"] = st.session_state.get("brief_count", 0) + 1
            st.session_state["app_error"] = None
    except Exception as exc:  # Do not include user input in error text.
        st.session_state["app_error"] = f"Could not create the brief ({type(exc).__name__})."
    finally:
        # The lyrics widget value is removed before the next page render.
        st.session_state.pop("lyrics_input", None)


initialize_state()

st.title("🎧 Song Poster Studio")
st.caption("Turn a song's mood into an abstract poster. A local demo build with no API keys required.")

with st.sidebar:
    st.header("Studio settings")
    st.selectbox(
        "Poster style",
        ["Aurora", "Minimal", "Retro", "Noir", "Dreamscape", "Geometric"],
        key="poster_style",
        help="Choose the visual direction for your poster.",
    )
    st.divider()
    st.markdown("**Engine status**")
    st.success("Demo mode · local Pillow artwork")
    st.caption("This starter build does not call Claude, FLUX, or any external API.")
    st.divider()
    st.markdown("**Session usage**")
    st.metric("Art briefs", f"{st.session_state['brief_count']} / {BRIEF_LIMIT}")
    st.metric("Posters", f"{st.session_state['poster_count']} / {POSTER_LIMIT}")
    st.caption("Counters are held in this Streamlit session and reset with a new session.")

tracks = load_tracks(ROOT / "data" / "charts")
track_map = {f"{item['title']} — {item['artist']}": item for item in tracks}
chart_options = ["Custom song", *track_map.keys()]
if st.session_state.get("chart_choice") not in chart_options:
    st.session_state["chart_choice"] = "Custom song"

left, right = st.columns([1.05, 0.95], gap="large")
with left:
    st.subheader("1. Choose a song")
    st.selectbox(
        "Sample chart tracks",
        chart_options,
        key="chart_choice",
        on_change=selected_track_changed,
        kwargs={"track_map": track_map},
        help="The included chart CSV is fictional sample data. You can also enter your own track.",
    )
    st.text_input("Song title", key="song_title", placeholder="Enter the song title")
    st.text_input("Artist", key="artist_name", placeholder="Enter the artist name")

    st.subheader("2. Add lyrics")
    st.info("Lyrics are used only in-memory to create the art brief. This app does not write lyrics to files, logs, or a database.")
    with st.form("brief_form", clear_on_submit=True):
        st.text_area(
            "Lyrics",
            key="lyrics_input",
            height=190,
            placeholder="Paste a short excerpt you are permitted to use…",
            help="Use text you own or are authorized to process. Lyrics are removed from session state after the brief is created.",
        )
        st.form_submit_button(
            "Create art brief",
            type="primary",
            disabled=st.session_state["brief_count"] >= BRIEF_LIMIT,
            on_click=create_brief_callback,
            use_container_width=True,
        )

    if st.session_state.get("app_error"):
        st.error(st.session_state["app_error"])

with right:
    st.subheader("3. Your art direction")
    raw_brief = st.session_state.get("art_brief")
    if raw_brief:
        brief = ArtBrief.from_dict(raw_brief)
        st.markdown(f"### {brief.concept}")
        st.write(brief.description)
        st.markdown("**Mood**")
        st.write(brief.mood)
        st.markdown("**Visual elements**")
        st.write(", ".join(brief.visual_elements))
        st.markdown("**Palette**")
        palette_cols = st.columns(len(brief.palette))
        for col, color in zip(palette_cols, brief.palette):
            col.markdown(
                f"<div style='height:34px;border-radius:8px;background:{color};border:1px solid #777'></div>"
                f"<div style='text-align:center;font-size:0.75rem'>{color}</div>",
                unsafe_allow_html=True,
            )
        if st.button(
            "Generate poster",
            type="primary",
            disabled=st.session_state["poster_count"] >= POSTER_LIMIT,
            use_container_width=True,
        ):
            try:
                background = create_demo_artwork(brief, size=(900, 1350))
                poster = add_title_overlay(
                    background,
                    title=st.session_state.get("song_title", "Untitled"),
                    artist=st.session_state.get("artist_name", "Unknown artist"),
                    style=brief.style,
                )
                from io import BytesIO
                buffer = BytesIO()
                poster.save(buffer, format="PNG", optimize=True)
                st.session_state["poster_png"] = buffer.getvalue()
                st.session_state["poster_count"] = st.session_state.get("poster_count", 0) + 1
                st.success("Poster created.")
            except Exception as exc:
                st.error(f"Could not generate poster ({type(exc).__name__}).")
    else:
        st.caption("Your lyric-free art brief will appear here after you create it.")
        st.markdown(
            "<div style='min-height:260px;border:1px dashed #777;border-radius:14px;display:flex;align-items:center;justify-content:center;color:#888'>Waiting for an art brief</div>",
            unsafe_allow_html=True,
        )

poster_png = st.session_state.get("poster_png")
if poster_png:
    st.divider()
    st.subheader("4. Poster preview")
    preview_col, details_col = st.columns([0.58, 0.42], gap="large")
    with preview_col:
        st.image(poster_png, caption="Demo-generated abstract artwork", use_container_width=True)
    with details_col:
        st.markdown("### Your poster is ready")
        st.write("The title and artist are rendered as real text on top of the abstract artwork.")
        safe_name = "_".join((st.session_state.get("song_title", "poster").strip().split() or ["poster"]))
        st.download_button(
            "Download poster (PNG)",
            data=poster_png,
            file_name=f"{safe_name[:48]}_poster.png",
            mime="image/png",
            type="primary",
            use_container_width=True,
        )

st.divider()
with st.expander("Privacy and demo limitations"):
    st.markdown(
        """
        - Lyrics are not included in the art-brief data structure and are not written to disk or a database by this app.
        - The lyrics input is removed from Streamlit session state after brief creation. The hosting platform and browser still control their own transport/runtime behavior; do not paste confidential material.
        - The included art director is a deterministic demo, not Claude. The image engine draws abstract artwork locally with Pillow, not FLUX.
        - The sample chart data is fictional. No Last.fm collection, GitHub scheduled workflow, Hugging Face mirror, or remote GPU server is configured.
        """
    )

st.caption("Song Poster Studio · independent demo implementation")
