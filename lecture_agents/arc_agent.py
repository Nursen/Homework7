"""Agent that reads the premise and slide descriptions to produce a structured lecture arc."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from config.arc_schema import LectureArc

load_dotenv()
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

SYSTEM_PROMPT = """\
You are an expert lecture architect and performance director. You are given:
1. A PREMISE document — the lecture's identity (thesis, scope, concepts, audience)
2. The complete SLIDE DESCRIPTIONS — what every slide contains

Your job is to produce the lecture ARC — the temporal blueprint of HOW this \
lecture unfolds. The premise tells you WHAT the lecture is. You must now determine \
HOW it flows.

Think like a theatre director blocking a performance:

PHASES / ACTS:
- Break the lecture into major phases (typically 3-6). Each phase is a sustained \
  section with a unified purpose — not just a topic change, but a shift in what \
  the lecture is DOING (motivating, explaining, proving, applying, synthesizing).
- For each phase: what slides does it span? What's the energy? What does it build \
  on and set up? What demos happen here?

FLOW DYNAMICS:
- Map the TRANSITIONS — how does the lecturer move between phases? Is it a \
  rhetorical question? A callback? A provocative claim?
- Track EMOTIONAL BEATS — where does the energy shift? Where's the humor? The \
  gravity? The empowerment?
- Describe the TENSION ARC — where are questions raised and where answered?
- Note PACING — which phases move fast, which linger?

IDEA PROGRESSION:
- What's the build order? How does each idea scaffold the next?
- What threads recur across phases — examples, metaphors, or themes that create \
  cohesion?
- Where is the CLIMAX — the peak intellectual moment?
- How does the lecture RESOLVE after the climax?

FRAMEWORKS:
- Identify structural or pedagogical patterns: problem-solution, concrete-to-abstract, \
  scaffolded complexity, hero's journey, compare-and-contrast, etc.

Be specific. Cite slide numbers. Ground everything in the actual content. \
Your arc should be detailed enough that a speaker could use it as a performance \
script alongside the slides.\
"""


def _build_model() -> GoogleModel:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY or GOOGLE_API_KEY in .env")
    provider = GoogleProvider(api_key=api_key)
    return GoogleModel(DEFAULT_MODEL, provider=provider)


arc_agent = Agent(
    model=_build_model(),
    system_prompt=SYSTEM_PROMPT,
    output_type=LectureArc,
)


def generate_arc(project_dir: str | Path) -> LectureArc:
    """Read premise.json and slide_description.json, produce arc.json."""
    project_dir = Path(project_dir)

    premise_path = project_dir / "premise.json"
    descriptions_path = project_dir / "slide_description.json"

    if not premise_path.exists():
        raise FileNotFoundError(f"No premise.json in {project_dir}. Run 'premise' first.")
    if not descriptions_path.exists():
        raise FileNotFoundError(f"No slide_description.json in {project_dir}. Run 'describe' first.")

    premise = json.loads(premise_path.read_text(encoding="utf-8"))
    descriptions = json.loads(descriptions_path.read_text(encoding="utf-8"))

    # Format the premise as context
    premise_block = json.dumps(premise, indent=2)

    # Format slide descriptions
    slide_blocks = []
    for s in descriptions["slides"]:
        slide_blocks.append(
            f"=== Slide {s['slide_number']} ({s['slide_type']}) ===\n"
            f"Headline: {s['headline']}\n"
            f"Key points: {'; '.join(s['key_points'])}\n"
            f"Text on slide: {s['text_on_slide']}\n"
            f"Visuals: {s['visual_elements']}\n"
            f"Purpose: {s['pedagogical_purpose']}\n"
            f"Context: {s['narrative_context']}\n"
        )

    user_prompt = (
        "=== LECTURE PREMISE ===\n"
        f"{premise_block}\n\n"
        f"=== SLIDE DESCRIPTIONS ({descriptions.get('total_slides', len(descriptions['slides']))} slides) ===\n"
        + "\n".join(slide_blocks)
        + "\n\nProduce the complete lecture arc from this premise and these slides."
    )

    print(f"Generating arc for: {premise.get('title', 'Unknown')}")
    result = arc_agent.run_sync(user_prompt)
    arc = result.output

    output_path = project_dir / "arc.json"
    output_path.write_text(
        json.dumps(arc.model_dump(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Wrote {output_path}")

    return arc


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate a lecture arc from premise + slide descriptions")
    parser.add_argument("project", help="Project directory (e.g. projects/lecture_17)")
    args = parser.parse_args()

    generate_arc(args.project)


if __name__ == "__main__":
    main()
