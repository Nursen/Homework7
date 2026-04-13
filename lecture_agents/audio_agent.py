"""Agent that synthesizes slide narrations into MP3 audio files.

Supports ElevenLabs (primary) and Gemini TTS (fallback).
Includes intelligent voice selection based on the instructor's style profile.
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# Voice selector: uses the style profile to pick the best ElevenLabs voice
# ---------------------------------------------------------------------------

def _select_voice_elevenlabs(style: dict, client) -> str:
    """Use the style profile to intelligently search for a matching ElevenLabs voice.

    Strategy: build a search query from the instructor's character essence,
    comparable personas, tone, and energy — then pick the top result.
    If nothing matches, fall back to a sensible default.
    """
    from pydantic_ai import Agent
    from pydantic_ai.models.google import GoogleModel
    from pydantic_ai.providers.google import GoogleProvider
    from pydantic import BaseModel, Field

    # First, get available voices
    voices_resp = client.voices.get_all()
    voice_list = []
    for v in voices_resp.voices:
        labels = {}
        if hasattr(v, "labels") and v.labels:
            labels = v.labels if isinstance(v.labels, dict) else {}
        voice_list.append({
            "voice_id": v.voice_id,
            "name": v.name,
            "labels": labels,
            "description": getattr(v, "description", "") or "",
            "preview_url": getattr(v, "preview_url", "") or "",
        })

    # Use the LLM to match style profile to best voice
    class VoiceSelection(BaseModel):
        voice_id: str = Field(description="The voice_id of the best matching voice")
        voice_name: str = Field(description="The name of the selected voice")
        reasoning: str = Field(description="Why this voice matches the instructor's style")

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    provider = GoogleProvider(api_key=api_key)
    model = GoogleModel(os.getenv("GEMINI_MODEL", "gemini-2.5-flash"), provider=provider)

    selector_agent = Agent(
        model=model,
        system_prompt=(
            "You are a casting director selecting a text-to-speech voice for a lecture narrator. "
            "You will be given the instructor's style profile and a list of available voices. "
            "Pick the voice that best matches the instructor's energy, tone, warmth, age range, "
            "and overall vibe. Consider gender, accent, and personality descriptors."
        ),
        output_type=VoiceSelection,
    )

    style_summary = (
        f"Character essence: {style.get('performance_notes', {}).get('character_essence', '')}\n"
        f"Comparable personas: {style.get('performance_notes', {}).get('comparable_personas', [])}\n"
        f"Overall tone: {style.get('tone_and_energy', {}).get('overall_tone', '')}\n"
        f"Energy level: {style.get('tone_and_energy', {}).get('energy_level', '')}\n"
        f"Warmth: {style.get('tone_and_energy', {}).get('warmth', '')}\n"
        f"Humor style: {style.get('tone_and_energy', {}).get('humor_style', '')}\n"
        f"Vocabulary level: {style.get('language_and_diction', {}).get('vocabulary_level', '')}\n"
        f"Profanity level: {style.get('language_and_diction', {}).get('profanity_level', '')}\n"
        f"Instructor name: {style.get('instructor_name', 'Unknown')}\n"
    )

    voices_block = json.dumps(voice_list, indent=2)

    prompt = (
        f"=== INSTRUCTOR STYLE ===\n{style_summary}\n\n"
        f"=== AVAILABLE VOICES ===\n{voices_block}\n\n"
        "Select the best matching voice. Return the voice_id, name, and reasoning."
    )

    result = selector_agent.run_sync(prompt)
    selection = result.output

    print(f"  Voice selected: {selection.voice_name} — {selection.reasoning}")
    return selection.voice_id


# ---------------------------------------------------------------------------
# ElevenLabs TTS
# ---------------------------------------------------------------------------

def _synthesize_elevenlabs(
    narrations: list[dict],
    audio_dir: Path,
    style: dict,
    voice_id: str | None = None,
) -> list[Path]:
    """Synthesize narrations to MP3 using ElevenLabs."""
    from elevenlabs import ElevenLabs

    api_key = os.environ.get("ELEVENLABS_API_KEY") or os.environ.get("ELEVEN_LABS_API_KEY")
    if not api_key:
        raise RuntimeError("Set ELEVENLABS_API_KEY or ELEVEN_LABS_API_KEY in .env")

    client = ElevenLabs(api_key=api_key)

    # Auto-select voice if not provided
    if not voice_id:
        print("  Selecting voice from style profile...")
        voice_id = _select_voice_elevenlabs(style, client)

    saved: list[Path] = []
    total = len(narrations)

    for entry in narrations:
        i = entry["slide_number"]
        text = entry["narration"]
        out_file = audio_dir / f"slide_{i:03d}.mp3"

        print(f"  Slide {i}/{total}: synthesizing …", end=" ", flush=True)

        # ElevenLabs returns an iterator of bytes
        audio_iter = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )

        # Merge chunks into one file
        with open(out_file, "wb") as f:
            for chunk in audio_iter:
                f.write(chunk)

        size_kb = out_file.stat().st_size / 1024
        print(f"done ({size_kb:.0f} KB)")
        saved.append(out_file)

    return saved


# ---------------------------------------------------------------------------
# Gemini TTS (fallback)
# ---------------------------------------------------------------------------

def _synthesize_gemini(
    narrations: list[dict],
    audio_dir: Path,
) -> list[Path]:
    """Synthesize narrations to MP3 using Gemini's TTS."""
    from google import genai

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY or GOOGLE_API_KEY in .env")

    client = genai.Client(api_key=api_key)

    saved: list[Path] = []
    total = len(narrations)

    for entry in narrations:
        i = entry["slide_number"]
        text = entry["narration"]
        out_file = audio_dir / f"slide_{i:03d}.mp3"

        print(f"  Slide {i}/{total}: synthesizing (Gemini) …", end=" ", flush=True)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Read the following lecture narration aloud naturally:\n\n{text}",
            config=genai.types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=genai.types.SpeechConfig(
                    voice_config=genai.types.VoiceConfig(
                        prebuilt_voice_config=genai.types.PrebuiltVoiceConfig(
                            voice_name="Kore",
                        )
                    )
                ),
            ),
        )

        # Extract audio data from response
        audio_data = response.candidates[0].content.parts[0].inline_data.data

        # Gemini returns WAV — convert to MP3 if possible, otherwise save as wav
        wav_file = out_file.with_suffix(".wav")
        wav_file.write_bytes(audio_data)

        try:
            import subprocess
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(wav_file), "-codec:a", "libmp3lame",
                 "-qscale:a", "2", str(out_file)],
                capture_output=True, check=True,
            )
            wav_file.unlink()
        except (FileNotFoundError, subprocess.CalledProcessError):
            # No ffmpeg — just rename to mp3 (technically wrong but functional)
            wav_file.rename(out_file)

        size_kb = out_file.stat().st_size / 1024
        print(f"done ({size_kb:.0f} KB)")
        saved.append(out_file)

    return saved


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generate_audio(
    project_dir: str | Path,
    style_path: str | Path = "style.json",
    provider: str = "elevenlabs",
    voice_id: str | None = None,
) -> list[Path]:
    """Read slide_description_narration.json and synthesize audio for each slide."""
    project_dir = Path(project_dir)
    style_path = Path(style_path)

    narrations_path = project_dir / "slide_description_narration.json"
    if not narrations_path.exists():
        raise FileNotFoundError(
            f"No slide_description_narration.json in {project_dir}. Run 'narrate' first."
        )

    data = json.loads(narrations_path.read_text(encoding="utf-8"))
    narrations = data["narrations"]

    style = {}
    if style_path.exists():
        style = json.loads(style_path.read_text(encoding="utf-8"))

    audio_dir = project_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    print(f"Synthesizing {len(narrations)} slides to {audio_dir}/ (provider: {provider})")

    if provider == "elevenlabs":
        return _synthesize_elevenlabs(narrations, audio_dir, style, voice_id)
    elif provider == "gemini":
        return _synthesize_gemini(narrations, audio_dir)
    else:
        raise ValueError(f"Unknown provider: {provider}. Use 'elevenlabs' or 'gemini'.")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Synthesize slide narrations into audio")
    parser.add_argument("project", help="Project directory (e.g. projects/lecture_17)")
    parser.add_argument("--style", type=str, default="style.json", help="Path to style.json")
    parser.add_argument("--provider", choices=["elevenlabs", "gemini"], default="elevenlabs",
                        help="TTS provider (default: elevenlabs)")
    parser.add_argument("--voice-id", type=str, default=None,
                        help="ElevenLabs voice ID (auto-selected from style if omitted)")
    args = parser.parse_args()

    generate_audio(args.project, args.style, args.provider, args.voice_id)


if __name__ == "__main__":
    main()
