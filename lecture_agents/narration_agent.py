"""Agent that generates slide-by-slide narration using style, premise, arc, and slide descriptions."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from config.narration_schema import SlideNarration, SlideNarrations
from config.slide_schema import SlideDescription

load_dotenv()
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


class NarrationOutput(BaseModel):
    """Single narration output from the model."""
    narration: str = Field(description="The spoken narration for this slide")


SYSTEM_PROMPT = """\
You are a lecture narrator. You will be given an instructor's detailed speaking-style \
profile and asked to generate narration for lecture slides AS THAT INSTRUCTOR.

Your narration must:

VOICE & STYLE:
- Sound EXACTLY like the instructor described in the style profile. Match their \
  fillers, verbal tics, slang, humor style, energy, sentence patterns, and vocabulary.
- Use their signature phrases, their rhythm, their way of building to a point.
- Match their profanity level, their directness, their warmth.
- If they trail off, you trail off. If they say "yo" and "bro", you say "yo" and "bro".

CONTENT & PEDAGOGY:
- Cover the key points on the slide thoroughly — don't skip content.
- Follow the lecture arc: know where you are in the overall flow, what just happened, \
  and what's coming next.
- Use the pedagogical approach from the style profile: their analogy style, their \
  example types, how they handle jargon, how they scaffold ideas.
- Hit the emotional beats appropriate for this point in the lecture.

PERFORMANCE TEXTURE — this is what separates a robotic reading from a live lecture:

1. TANGENTS & ASIDES: The instructor goes off-script. For at least some slides, \
   include a brief tangent — a relevant news story, an industry aside, a personal \
   anecdote, a career warning — that connects to the slide content but isn't ON \
   the slide. Use the tangent_and_aside_style from the profile. Get back on track \
   the way the instructor does (e.g. "Anyways…", "But yeah…").

2. SPONTANEOUS INTERACTION: Simulate real-time audience moments. Reference the \
   chat, react to an imagined student comment, ask a student to confirm something. \
   Use the spontaneous_interaction patterns from the profile.

3. MESSY SPEECH — this is CRITICAL: Real speech is grammatically broken. You MUST:
   - Leave some sentences genuinely unfinished. Trail off with "so…" or just pivot.
   - Change direction mid-sentence. Start saying one thing, switch to another.
   - Include moments of real confusion or forgetting: wrong numbers corrected, \
     blanking on a name, second-guessing yourself. Use the messy_speech_patterns \
     from the profile as templates.
   - When numbers come up, work through them out loud, imprecisely: "that's like, \
     what, 10,000 times 6, so… 60,000? Yeah, 60,000 files."
   - Say something slightly wrong, then catch it: "all the 6 books… wait, 7. \
     Seven books."

4. COMIC TIMING: Deliver some punchlines as STANDALONE BEATS — short lines that \
   hang in the air with nothing before or after. Not buried in paragraphs. \
   Invent irreverent nicknames for technical terms the way the instructor does. \
   Use the comic_timing patterns from the profile.

5. SENTENCE FRAGMENTATION: Many "sentences" should be fragments. Short. Punchy. \
   Incomplete. Mixed with longer flowing explanations. The rhythm should feel like \
   real speech cadence, not written prose.

NATURALISM:
- Sound like a TRANSCRIPT of someone talking, NOT like someone writing. \
  If you read it back and it sounds like an essay, you've failed.
- The test: could this plausibly be an auto-generated caption file? It should \
  have that raw, unedited, thinking-out-loud quality.

LENGTH:
- Generate enough narration to naturally cover the slide content. A content-heavy \
  slide needs more narration than a simple transition slide.
- Don't pad with filler, but don't rush through complex ideas either.

EXPRESSIVENESS FOR TEXT-TO-SPEECH:
This narration will be read aloud by a TTS engine. The engine does NOT understand \
stage directions like (laughing) or (excited) — it reads them literally. Instead, \
you must write the emotion INTO the words themselves so the TTS voice naturally \
picks up the energy. Rules:

NEVER USE parenthetical stage directions like (pause), (laughing), (excited), etc. \
The TTS will say them out loud. Instead:

- For LAUGHTER: Write it out. "Ha!" or "Heh heh." or "Man, that's funny." \
  The TTS will vocalize these naturally.
- For PAUSES: Use "..." (ellipsis). The TTS pauses on these. Or write \
  "So... yeah." or "Right... okay." or just a short sentence by itself.
- For EXCITEMENT: Use exclamation marks and energetic word choice. \
  "Oh MAN, check this out!" not "(excited) Check this out."
- For GRAVITY: Use slower, shorter sentences. "And that... that's the real \
  problem here." Let the words carry the weight.
- For EMPHASIS: Use ALL CAPS on ONE word sparingly. "This is the WHOLE point." \
  The TTS stresses capitalized words.
- For THINKING: Write it as thinking out loud. "Hmm... let me think... so \
  if you take that and..." with ellipses and hedging words.
- For ASIDES: Drop to a conspiratorial tone through word choice. "And between \
  you and me... that job's probably not gonna exist in two years. Just saying."

The key principle: if you read the text yourself with zero acting, would the \
emotion come through from the WORDS ALONE? If not, rewrite until it does.

You are writing a performance script. Every word should sound like it came from \
this specific instructor's mouth — including the tangents, the mistakes, and the \
messy humanity.\
"""


def _build_model() -> GoogleModel:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY or GOOGLE_API_KEY in .env")
    provider = GoogleProvider(api_key=api_key)
    return GoogleModel(DEFAULT_MODEL, provider=provider)


narration_agent = Agent(
    model=_build_model(),
    system_prompt=SYSTEM_PROMPT,
    output_type=NarrationOutput,
)


def _format_prior_narrations(prior: list[SlideNarration]) -> str:
    """Format previous narrations as context."""
    if not prior:
        return ""

    lines = [f"\n=== PRIOR NARRATIONS (slides 1–{len(prior)}) ===\n"]
    for sn in prior:
        lines.append(
            f"--- Slide {sn.slide_number} ---\n"
            f"{sn.narration}\n"
        )
    return "\n".join(lines)


def _format_slide_description(s: dict) -> str:
    """Format a single slide description for the prompt."""
    return (
        f"Slide type: {s['slide_type']}\n"
        f"Headline: {s['headline']}\n"
        f"Key points: {'; '.join(s['key_points'])}\n"
        f"Text on slide: {s['text_on_slide']}\n"
        f"Visuals: {s['visual_elements']}\n"
        f"Pedagogical purpose: {s['pedagogical_purpose']}\n"
        f"Narrative context: {s['narrative_context']}\n"
        f"Suggested talking points: {'; '.join(s['suggested_talking_points'])}\n"
        f"Speaker notes hint: {s['speaker_notes_hint']}\n"
    )


def _find_current_phase(arc: dict, slide_num: int) -> dict | None:
    """Find which phase of the arc the current slide belongs to."""
    for phase in arc.get("phases", []):
        slide_range = phase.get("slides", "")
        if "-" in slide_range:
            start, end = slide_range.split("-")
            if int(start) <= slide_num <= int(end):
                return phase
        elif slide_range.isdigit() and int(slide_range) == slide_num:
            return phase
    return None


def generate_narrations(
    project_dir: str | Path,
    style_path: str | Path = "style.json",
) -> SlideNarrations:
    """Generate narration for each slide and write slide_description_narration.json."""
    project_dir = Path(project_dir)
    style_path = Path(style_path)

    # Load all inputs
    for path, name in [
        (style_path, "style.json"),
        (project_dir / "premise.json", "premise.json"),
        (project_dir / "arc.json", "arc.json"),
        (project_dir / "slide_description.json", "slide_description.json"),
    ]:
        if not path.exists():
            raise FileNotFoundError(f"Missing {name} at {path}. Run prior pipeline steps first.")

    style = json.loads(style_path.read_text(encoding="utf-8"))
    premise = json.loads((project_dir / "premise.json").read_text(encoding="utf-8"))
    arc = json.loads((project_dir / "arc.json").read_text(encoding="utf-8"))
    descriptions = json.loads((project_dir / "slide_description.json").read_text(encoding="utf-8"))

    # Build static context blocks
    style_block = json.dumps(style, indent=2)
    premise_block = json.dumps(premise, indent=2)
    arc_summary = (
        f"Hook: {arc.get('hook', '')}\n"
        f"Opening energy: {arc.get('opening_energy', '')}\n"
        f"Closing move: {arc.get('closing_move', '')}\n"
        f"Tension arc: {arc.get('tension_arc', '')}\n"
        f"Climax: {arc.get('climax', '')}\n"
        f"Resolution: {arc.get('resolution', '')}\n"
        f"Idea build order: {'; '.join(arc.get('idea_build_order', []))}\n"
        f"Recurring threads: {'; '.join(arc.get('recurring_threads', []))}\n"
        f"Pacing notes: {arc.get('pacing_notes', '')}\n"
    )

    images_dir = project_dir / "slide_images"
    if not images_dir.exists():
        raise FileNotFoundError(f"No slide_images/ in {project_dir}. Run 'slides' first.")

    instructor_name = style.get("instructor_name", "the instructor")
    lecture_title = descriptions.get("lecture_title", premise.get("title", "Unknown"))
    total = len(descriptions["slides"])

    print(f"Generating narrations for {total} slides as {instructor_name}")

    narrations: list[SlideNarration] = []

    for i, slide_data in enumerate(descriptions["slides"], start=1):
        print(f"  Slide {i}/{total}: {slide_data['headline']} …", end=" ", flush=True)

        # Find current phase context
        phase = _find_current_phase(arc, i)
        phase_block = ""
        if phase:
            phase_block = (
                f"\n=== CURRENT PHASE: {phase['name']} ===\n"
                f"Purpose: {phase['purpose']}\n"
                f"Energy: {phase['energy_level']}\n"
                f"Builds on: {phase['builds_on']}\n"
                f"Sets up: {phase['sets_up']}\n"
            )

        # Title slide gets special instructions
        title_instruction = ""
        if i == 1:
            title_instruction = (
                f"\n** IMPORTANT: This is the TITLE SLIDE. The instructor should:\n"
                f"1. Introduce themselves by name ({instructor_name})\n"
                f"2. Give a short, engaging summary of what this lecture is about\n"
                f"3. Set the tone and energy for the rest of the lecture\n"
                f"Use the premise thesis and the hook from the arc to guide the intro. **\n"
            )

        prior_context = _format_prior_narrations(narrations)

        # Load the current slide image
        slide_image_path = images_dir / f"slide_{i:03d}.png"
        slide_image_data = slide_image_path.read_bytes()

        text_prompt = (
            f"=== INSTRUCTOR STYLE PROFILE ===\n{style_block}\n\n"
            f"=== LECTURE PREMISE ===\n{premise_block}\n\n"
            f"=== LECTURE ARC ===\n{arc_summary}\n"
            f"{phase_block}\n"
            f"=== CURRENT SLIDE ({i} of {total}) ===\n"
            f"{_format_slide_description(slide_data)}\n"
            f"{title_instruction}"
            f"{prior_context}\n"
            f"The slide image is attached. Generate the narration for slide {i}. "
            f"Speak as {instructor_name}."
        )

        user_prompt = [
            text_prompt,
            BinaryContent(data=slide_image_data, media_type="image/png"),
        ]

        result = narration_agent.run_sync(user_prompt)

        slide_desc = SlideDescription(**slide_data)
        narration_entry = SlideNarration(
            slide_number=i,
            narration=result.output.narration,
            slide_description=slide_desc,
        )
        narrations.append(narration_entry)
        print("done")

    output = SlideNarrations(
        lecture_title=lecture_title,
        instructor_name=instructor_name,
        total_slides=total,
        narrations=narrations,
    )

    output_path = project_dir / "slide_description_narration.json"
    output_path.write_text(
        json.dumps(output.model_dump(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Wrote {output_path}")

    return output


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate slide narrations in the instructor's voice")
    parser.add_argument("project", help="Project directory (e.g. projects/lecture_17)")
    parser.add_argument(
        "--style", type=str, default="style.json",
        help="Path to style.json (default: style.json in repo root)",
    )
    args = parser.parse_args()

    generate_narrations(args.project, args.style)


if __name__ == "__main__":
    main()
