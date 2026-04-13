"""Agent that analyzes a lecture transcript and produces an instructor style profile."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from config.style_schema import InstructorStyleProfile

load_dotenv()
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

SYSTEM_PROMPT = """\
You are an expert dialect coach, performance analyst, and linguistics researcher. \
Your job is to analyze a lecture transcript and produce an exhaustive speaking-style \
profile of the instructor — the kind of document a voice actor would study before \
portraying this person.

Analyze EVERY dimension of how this person speaks:

CORE VOICE:
- Their vocal mannerisms: fillers, verbal tics, self-corrections, trailing off
- Their tone and energy: register, humor, warmth, enthusiasm
- Their pacing and rhythm: sentence length, pauses, build-ups
- How they interact with the audience: direct address, rhetorical questions, chat
- Their explanatory style: analogies, examples, scaffolding, jargon handling
- Their pedagogy: persona, motivation tactics, tangent behavior, opinions
- Their language: vocabulary level, slang, profanity, code-switching, catchphrases
- Their structural patterns: openings, transitions, recaps, signposting

PERFORMANCE TEXTURE — pay CLOSE attention to these, they are what makes the \
voice feel LIVE vs. scripted:

- TANGENTS & ASIDES: How do they go off-script? What kinds of tangents — news \
  stories, personal anecdotes, career warnings, industry gossip? How do they get \
  back on track? How often do tangents happen? Quote specific examples.

- SPONTANEOUS INTERACTION: Do they call students by name? React to chat messages \
  live? Assign roles on the fly? Pull audience into examples? Quote instances.

- MESSY SPEECH: Find genuinely incomplete sentences, mid-sentence pivots, real \
  confusion or forgetting (not performed), working through math/numbers out loud \
  imprecisely, saying something wrong then correcting it. These are GOLD — quote \
  every instance you find.

- COMIC TIMING: Find standalone one-liner punchlines that hang in the air as \
  their own beat (not buried in paragraphs). Find irreverent nicknames they \
  invent for technical terms. Find deadpan moments, callbacks. Describe their \
  timing pattern.

Be SPECIFIC and CONCISE. When quoting the transcript, use SHORT snippets \
(under 15 words each) — just enough to illustrate the pattern, never full paragraphs. \
Don't say "uses humor" — say exactly WHAT KIND of humor with a brief example. \
Don't say "casual tone" — describe the precise texture of that casualness.

You are writing this so that someone who has never heard this instructor could \
read your profile and perfectly replicate their voice in writing — including the \
messy, improvised, tangent-filled texture that makes it feel REAL.\
"""


def _build_model() -> GoogleModel:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY or GOOGLE_API_KEY in .env")
    provider = GoogleProvider(api_key=api_key)
    return GoogleModel(DEFAULT_MODEL, provider=provider)


style_agent = Agent(
    model=_build_model(),
    system_prompt=SYSTEM_PROMPT,
    output_type=InstructorStyleProfile,
)


def analyze_style(transcript_path: str | Path, output_path: str | Path = "style.json") -> InstructorStyleProfile:
    """Read a transcript file, analyze it with the style agent, and write style.json."""
    transcript_path = Path(transcript_path)
    output_path = Path(output_path)

    if not transcript_path.exists():
        raise FileNotFoundError(f"Transcript not found: {transcript_path}")

    transcript = transcript_path.read_text(encoding="utf-8")

    user_prompt = (
        "Analyze the following lecture transcript and produce a complete "
        "instructor speaking-style profile.\n\n"
        f"<transcript>\n{transcript}\n</transcript>"
    )

    result = style_agent.run_sync(user_prompt)
    profile = result.output

    # Write validated output
    output_path.write_text(
        json.dumps(profile.model_dump(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return profile
