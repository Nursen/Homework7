"""Agentic Video Lecture Pipeline - Entry Point"""

import argparse
import sys
from pathlib import Path

from lecture_agents.arc_agent import generate_arc
from lecture_agents.audio_agent import generate_audio
from lecture_agents.narration_agent import generate_narrations
from lecture_agents.premise_agent import generate_premise
from lecture_agents.slide_describer import describe_slides
from lecture_agents.style_analyzer import analyze_style
from utils.assemble_video import assemble_video
from utils.rasterize_slides import rasterize


def main():
    parser = argparse.ArgumentParser(description="Agentic Video Lecture Pipeline")
    subparsers = parser.add_subparsers(dest="command", help="Pipeline step to run")

    # --- style command ---
    style_parser = subparsers.add_parser(
        "style", help="Analyze a transcript and produce style.json"
    )
    style_parser.add_argument("transcript", type=str, help="Path to the transcript file")
    style_parser.add_argument(
        "-o", "--output", type=str, default="style.json",
        help="Output path for the style profile (default: style.json)",
    )

    # --- premise command ---
    premise_parser = subparsers.add_parser(
        "premise", help="Generate a lecture premise from slide descriptions"
    )
    premise_parser.add_argument("project", type=str, help="Project directory (e.g. projects/lecture_17)")

    # --- arc command ---
    arc_parser = subparsers.add_parser(
        "arc", help="Generate a lecture arc from premise + slide descriptions"
    )
    arc_parser.add_argument("project", type=str, help="Project directory (e.g. projects/lecture_17)")

    # --- narrate command ---
    narrate_parser = subparsers.add_parser(
        "narrate", help="Generate slide narrations in the instructor's voice"
    )
    narrate_parser.add_argument("project", type=str, help="Project directory (e.g. projects/lecture_17)")
    narrate_parser.add_argument(
        "--style", type=str, default="style.json",
        help="Path to style.json (default: style.json in repo root)",
    )

    # --- audio command ---
    audio_parser = subparsers.add_parser(
        "audio", help="Synthesize slide narrations into MP3 audio"
    )
    audio_parser.add_argument("project", type=str, help="Project directory (e.g. projects/lecture_17)")
    audio_parser.add_argument("--style", type=str, default="style.json", help="Path to style.json")
    audio_parser.add_argument("--provider", choices=["elevenlabs", "gemini"], default="elevenlabs",
                              help="TTS provider (default: elevenlabs)")
    audio_parser.add_argument("--voice-id", type=str, default=None,
                              help="ElevenLabs voice ID (auto-selected from style if omitted)")

    # --- video command ---
    video_parser = subparsers.add_parser(
        "video", help="Assemble slide PNGs + MP3 audio into a lecture video"
    )
    video_parser.add_argument("project", type=str, help="Project directory (e.g. projects/lecture_17)")
    video_parser.add_argument("--pdf-name", type=str, default=None,
                              help="Original PDF filename for output naming (e.g. Lecture_17_AI_screenplays.pdf)")

    # --- describe command ---
    describe_parser = subparsers.add_parser(
        "describe", help="Generate descriptions for each slide image"
    )
    describe_parser.add_argument("project", type=str, help="Project directory (e.g. projects/lecture_17)")

    # --- slides command ---
    slides_parser = subparsers.add_parser(
        "slides", help="Rasterize a slide PDF into PNGs"
    )
    slides_parser.add_argument("pdf", type=str, help="Path to the slide deck PDF")
    slides_parser.add_argument("project", type=str, help="Project directory (e.g. projects/lecture_17)")
    slides_parser.add_argument("--dpi", type=int, default=200, help="Resolution (default: 200)")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "style":
        transcript = Path(args.transcript)
        print(f"Analyzing transcript: {transcript.name}")
        profile = analyze_style(transcript, args.output)
        print(f"Style profile written to {args.output}")
        print(f"Instructor: {profile.instructor_name}")
        print(f"Course: {profile.course_context}")

    elif args.command == "premise":
        generate_premise(args.project)

    elif args.command == "arc":
        generate_arc(args.project)

    elif args.command == "narrate":
        generate_narrations(args.project, args.style)

    elif args.command == "audio":
        generate_audio(args.project, args.style, args.provider, args.voice_id)

    elif args.command == "video":
        assemble_video(args.project, args.pdf_name)

    elif args.command == "describe":
        describe_slides(args.project)

    elif args.command == "slides":
        rasterize(args.pdf, args.project, args.dpi)


if __name__ == "__main__":
    main()
