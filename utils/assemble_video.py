"""Assemble slide PNGs + MP3 audio into a single lecture video.

For each slide, creates a video segment where the slide image is shown for the
exact duration of its audio track. All segments are then concatenated into one
MP4 whose basename matches the source PDF.
"""

import argparse
import subprocess
import tempfile
from pathlib import Path


def _get_audio_duration(mp3_path: Path) -> float:
    """Get the duration of an MP3 file in seconds using ffprobe."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(mp3_path),
        ],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def _make_segment(slide_path: Path, audio_path: Path, out_path: Path) -> None:
    """Create a video segment: slide image held for the duration of the audio."""
    duration = _get_audio_duration(audio_path)

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(slide_path),
            "-i", str(audio_path),
            "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "192k",
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black",
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            "-shortest",
            str(out_path),
        ],
        capture_output=True, check=True,
    )


def assemble_video(
    project_dir: str | Path,
    pdf_name: str | None = None,
) -> Path:
    """Assemble all slide segments into one MP4.

    Args:
        project_dir: Project directory containing slide_images/ and audio/
        pdf_name: Original PDF filename to derive output name. If None, uses
                  the project directory name.

    Returns:
        Path to the final MP4.
    """
    project_dir = Path(project_dir)
    images_dir = project_dir / "slide_images"
    audio_dir = project_dir / "audio"

    if not images_dir.exists():
        raise FileNotFoundError(f"No slide_images/ in {project_dir}")
    if not audio_dir.exists():
        raise FileNotFoundError(f"No audio/ in {project_dir}. Run 'audio' first.")

    slides = sorted(images_dir.glob("slide_*.png"))
    audios = sorted(audio_dir.glob("slide_*.mp3"))

    if not slides:
        raise FileNotFoundError(f"No slide_*.png in {images_dir}")
    if not audios:
        raise FileNotFoundError(f"No slide_*.mp3 in {audio_dir}")

    if len(slides) != len(audios):
        raise ValueError(
            f"Mismatch: {len(slides)} slides but {len(audios)} audio files. "
            "Ensure every slide has a matching MP3."
        )

    total = len(slides)
    print(f"Assembling {total} slide segments …")

    # Create temporary segment files
    segments_dir = project_dir / "_segments"
    segments_dir.mkdir(exist_ok=True)

    segment_paths: list[Path] = []
    for slide_path, audio_path in zip(slides, audios):
        idx = slide_path.stem  # e.g. "slide_001"
        seg_path = segments_dir / f"{idx}.mp4"

        print(f"  {idx}: {slide_path.name} + {audio_path.name} …", end=" ", flush=True)
        _make_segment(slide_path, audio_path, seg_path)

        duration = _get_audio_duration(audio_path)
        print(f"done ({duration:.1f}s)")
        segment_paths.append(seg_path)

    # Build concat file list for ffmpeg
    concat_file = segments_dir / "concat.txt"
    with open(concat_file, "w") as f:
        for seg in segment_paths:
            f.write(f"file '{seg.resolve()}'\n")

    # Derive output name from PDF or project dir
    if pdf_name:
        out_name = Path(pdf_name).stem + ".mp4"
    else:
        out_name = project_dir.name + ".mp4"

    out_path = project_dir / out_name

    print(f"Concatenating {total} segments into {out_path.name} …")
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(out_path),
        ],
        capture_output=True, check=True,
    )

    # Clean up temp segments
    for seg in segment_paths:
        seg.unlink()
    concat_file.unlink()
    segments_dir.rmdir()

    total_duration = sum(_get_audio_duration(a) for a in audios)
    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"Done! {out_path} ({size_mb:.1f} MB, {total_duration / 60:.1f} min)")

    return out_path


def main():
    parser = argparse.ArgumentParser(description="Assemble slide video from PNGs + MP3s")
    parser.add_argument("project", help="Project directory (e.g. projects/lecture_17)")
    parser.add_argument("--pdf-name", type=str, default=None,
                        help="Original PDF filename for output naming")
    args = parser.parse_args()

    assemble_video(args.project, args.pdf_name)


if __name__ == "__main__":
    main()
