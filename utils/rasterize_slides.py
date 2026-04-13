"""Rasterize a PDF of lecture slides into individual PNG images."""

import argparse
import sys
from pathlib import Path

from pdf2image import convert_from_path


def rasterize(pdf_path: str | Path, project_dir: str | Path, dpi: int = 200) -> list[Path]:
    """Convert each page of a PDF into a PNG under <project_dir>/slide_images/."""
    pdf_path = Path(pdf_path)
    project_dir = Path(project_dir)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    output_dir = project_dir / "slide_images"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Rasterizing {pdf_path.name} at {dpi} DPI …")
    images = convert_from_path(pdf_path, dpi=dpi)

    saved: list[Path] = []
    for i, img in enumerate(images, start=1):
        out_file = output_dir / f"slide_{i:03d}.png"
        img.save(out_file, "PNG")
        saved.append(out_file)

    print(f"Saved {len(saved)} slides to {output_dir}/")
    return saved


def main():
    parser = argparse.ArgumentParser(description="Rasterize a slide PDF into PNGs")
    parser.add_argument("pdf", help="Path to the slide deck PDF")
    parser.add_argument("project", help="Project directory (e.g. projects/lecture_17)")
    parser.add_argument("--dpi", type=int, default=200, help="Resolution (default: 200)")
    args = parser.parse_args()

    rasterize(args.pdf, args.project, args.dpi)


if __name__ == "__main__":
    main()
