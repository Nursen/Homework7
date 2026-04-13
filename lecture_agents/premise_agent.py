"""Agent that reads slide descriptions and produces a structured lecture premise."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from config.premise_schema import LecturePremise

load_dotenv()
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

SYSTEM_PROMPT = """\
You are an expert curriculum designer. You are given the complete slide-by-slide \
descriptions of a lecture deck. Your job is to reverse-engineer the lecture PREMISE — \
the identity card of what this lecture IS.

The premise captures WHAT, not HOW. Do NOT describe the lecture's flow, pacing, \
emotional beats, or temporal structure — that belongs in a separate arc document. \
Focus exclusively on:

THESIS & ARGUMENT:
- What is the single core argument? What is it pushing back against (the antithesis)?
- Unpack the thesis — what exactly is being claimed and why it matters?

SCOPE:
- What does this lecture explicitly cover? What does it intentionally leave out and why?

AUDIENCE:
- Who are these people? What do they already know? What pain points do they walk in with?

LEARNING OBJECTIVES:
- What should students be able to DO or UNDERSTAND after this lecture?
- Tag each with a Bloom's taxonomy level.

CONCEPTS & DEPENDENCIES:
- What are the core concepts? Define each concisely.
- Map the dependency graph — which concepts require understanding others first?
- Describe the relationships between concepts explicitly.

MISCONCEPTIONS:
- What does the audience likely believe coming in that this lecture corrects?

BRIDGES:
- What prior knowledge does this lecture build on?
- What does it set up for next?

TAKEAWAY:
- The one thing to remember if everything else is forgotten.

Be specific and grounded in the slide content. Infer intelligently but don't invent.\
"""


def _build_model() -> GoogleModel:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY or GOOGLE_API_KEY in .env")
    provider = GoogleProvider(api_key=api_key)
    return GoogleModel(DEFAULT_MODEL, provider=provider)


premise_agent = Agent(
    model=_build_model(),
    system_prompt=SYSTEM_PROMPT,
    output_type=LecturePremise,
)


def generate_premise(project_dir: str | Path) -> LecturePremise:
    """Read slide_description.json from a project and produce premise.json."""
    project_dir = Path(project_dir)
    descriptions_path = project_dir / "slide_description.json"

    if not descriptions_path.exists():
        raise FileNotFoundError(
            f"No slide_description.json in {project_dir}. Run 'describe' first."
        )

    descriptions = json.loads(descriptions_path.read_text(encoding="utf-8"))

    # Build a concise but complete summary of the deck for the model
    slide_summaries = []
    for s in descriptions["slides"]:
        slide_summaries.append(
            f"=== Slide {s['slide_number']} ({s['slide_type']}) ===\n"
            f"Headline: {s['headline']}\n"
            f"Key points: {'; '.join(s['key_points'])}\n"
            f"Text on slide: {s['text_on_slide']}\n"
            f"Visuals: {s['visual_elements']}\n"
            f"Purpose: {s['pedagogical_purpose']}\n"
            f"Context: {s['narrative_context']}\n"
            f"Talking points: {'; '.join(s['suggested_talking_points'])}\n"
        )

    user_prompt = (
        f"Lecture: {descriptions.get('lecture_title', 'Unknown')}\n"
        f"Total slides: {descriptions.get('total_slides', len(descriptions['slides']))}\n\n"
        + "\n".join(slide_summaries)
        + "\n\nProduce the complete lecture premise from these slide descriptions."
    )

    print(f"Generating premise for: {descriptions.get('lecture_title', 'Unknown')}")
    result = premise_agent.run_sync(user_prompt)
    premise = result.output

    output_path = project_dir / "premise.json"
    output_path.write_text(
        json.dumps(premise.model_dump(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Wrote {output_path}")

    return premise


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate a lecture premise from slide descriptions")
    parser.add_argument("project", help="Project directory (e.g. projects/lecture_17)")
    args = parser.parse_args()

    generate_premise(args.project)


if __name__ == "__main__":
    main()
