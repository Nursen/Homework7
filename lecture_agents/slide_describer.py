"""Agent that processes slide images sequentially, building context-aware descriptions."""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from config.slide_schema import SlideDescription, SlideDescriptions

load_dotenv()
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

SYSTEM_PROMPT = """\
You are an expert at analyzing lecture slides and producing rich, structured \
descriptions that will later be used to generate spoken narration.

You will receive:
1. An image of the CURRENT slide
2. Descriptions of ALL PREVIOUS slides (so you understand the lecture arc so far)

Your job is to describe the current slide thoroughly and in context. Think like \
a teaching assistant preparing notes for a substitute lecturer who has never \
seen this deck before.

Guidelines:
- Read ALL text on the slide carefully and reproduce it faithfully.
- Identify the slide type (title, content, diagram, code, comparison, etc.).
- Describe visual elements: layout, diagrams, charts, images, color coding, arrows.
- Infer the pedagogical purpose: why does this slide exist in this position?
- Connect to previous slides: is this continuing a thread, introducing something \
  new, providing an example of what was just explained, or summarizing?
- Suggest realistic talking points: what would the instructor actually SAY here? \
  Think about what needs verbal explanation beyond what's written on the slide.
- Capture the speaker's likely intent: what should the audience walk away knowing \
  after this slide?

Be precise and thorough — the narration generator will rely entirely on your \
description to know what's on each slide.\
"""


def _build_model() -> GoogleModel:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY or GOOGLE_API_KEY in .env")
    provider = GoogleProvider(api_key=api_key)
    return GoogleModel(DEFAULT_MODEL, provider=provider)


slide_agent = Agent(
    model=_build_model(),
    system_prompt=SYSTEM_PROMPT,
    output_type=SlideDescription,
)


def _build_context_block(previous: list[SlideDescription]) -> str:
    """Format previous slide descriptions as context for the model."""
    if not previous:
        return "This is the FIRST slide in the deck. There are no previous slides."

    lines = [f"=== Previous slides (1–{len(previous)}) ===\n"]
    for desc in previous:
        lines.append(
            f"--- Slide {desc.slide_number} ({desc.slide_type}) ---\n"
            f"Headline: {desc.headline}\n"
            f"Key points: {'; '.join(desc.key_points)}\n"
            f"Purpose: {desc.pedagogical_purpose}\n"
        )
    return "\n".join(lines)


def describe_slides(project_dir: str | Path) -> SlideDescriptions:
    """Process all slide images in a project and write slide_description.json."""
    project_dir = Path(project_dir)
    images_dir = project_dir / "slide_images"

    if not images_dir.exists():
        raise FileNotFoundError(f"No slide_images/ directory in {project_dir}")

    slide_files = sorted(images_dir.glob("slide_*.png"))
    if not slide_files:
        raise FileNotFoundError(f"No slide_*.png files in {images_dir}")

    total = len(slide_files)
    print(f"Processing {total} slides from {images_dir}/")

    descriptions: list[SlideDescription] = []

    for i, slide_path in enumerate(slide_files, start=1):
        print(f"  Slide {i}/{total}: {slide_path.name} …", end=" ", flush=True)

        image_data = slide_path.read_bytes()
        context = _build_context_block(descriptions)

        user_prompt = [
            f"Slide {i} of {total}.\n\n{context}\n\n"
            f"Describe slide {i} shown in the attached image.",
            BinaryContent(data=image_data, media_type="image/png"),
        ]

        result = slide_agent.run_sync(user_prompt)
        desc = result.output
        # Ensure slide_number is correct regardless of model output
        desc.slide_number = i
        descriptions.append(desc)
        print(f"done ({desc.slide_type})")

    # Infer lecture title from the first slide
    lecture_title = descriptions[0].headline if descriptions else ""

    output = SlideDescriptions(
        lecture_title=lecture_title,
        total_slides=total,
        slides=descriptions,
    )

    output_path = project_dir / "slide_description.json"
    output_path.write_text(
        json.dumps(output.model_dump(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Wrote {output_path}")

    return output


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Describe lecture slides sequentially")
    parser.add_argument("project", help="Project directory (e.g. projects/lecture_17)")
    args = parser.parse_args()

    describe_slides(args.project)


if __name__ == "__main__":
    main()
