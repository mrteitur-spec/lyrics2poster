from __future__ import annotations

from .models import ArtBrief
from .safety import clean_lyrics, validate_metadata
from .styles import STYLE_PRESETS

MOOD_SIGNALS = {
    "hopeful": {"light", "hope", "rise", "sun", "begin", "home", "shine", "새벽", "빛", "희망"},
    "melancholic": {"rain", "tears", "empty", "gone", "miss", "alone", "night", "비", "눈물", "그리움"},
    "energetic": {"run", "dance", "fire", "wild", "loud", "heart", "burn", "춤", "불꽃", "달려"},
    "dreamlike": {"dream", "sky", "moon", "float", "cloud", "stars", "잠", "꿈", "달", "하늘"},
}


def _infer_mood(lyrics: str) -> str:
    tokens = set(lyrics.lower().replace("\n", " ").split())
    scores = {mood: len(tokens.intersection(words)) for mood, words in MOOD_SIGNALS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else "introspective"


def create_demo_brief(*, title: str, artist: str, lyrics: str, style: str) -> ArtBrief:
    """Create a lyric-free art direction using deterministic local rules.

    This is a no-key demo substitute, not an LLM call. Lyrics are never placed in
    the returned object; callers should discard the input immediately afterward.
    """
    title, artist = validate_metadata(title, artist)
    text = clean_lyrics(lyrics)
    if not title or not artist:
        raise ValueError("A title and artist are required.")
    if not text:
        raise ValueError("Please enter some lyrics.")
    if style not in STYLE_PRESETS:
        style = "Aurora"

    preset = STYLE_PRESETS[style]
    mood = _infer_mood(text)
    motifs = list(preset["motifs"])
    concept = f"{mood.title()} {style.lower()}"
    description = (
        f"An abstract, text-free visual scene with a {mood} atmosphere. "
        f"Use {', '.join(motifs[:2])} and a {preset['finish']} finish. "
        "Avoid depicting identifiable people, logos, or recognizable existing artwork."
    )
    return ArtBrief(
        concept=concept,
        description=description,
        mood=mood,
        visual_elements=motifs,
        palette=list(preset["palette"]),
        style=style,
    )
