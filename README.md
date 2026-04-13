# Agentic Video Lecture Pipeline

An AI-powered pipeline that takes a slide deck PDF and an instructor's transcript, then generates a complete narrated video lecture using autonomous agents.

## Pipeline Steps

1. **style** — Analyze a transcript to extract the instructor's speaking-style profile (`style.json`)
2. **slides** — Rasterize a slide PDF into individual PNGs (`slide_images/`)
3. **describe** — Generate context-aware descriptions for each slide (`slide_description.json`)
4. **premise** — Reverse-engineer the lecture's identity: thesis, scope, concepts (`premise.json`)
5. **arc** — Map the lecture's temporal flow: phases, transitions, emotional beats (`arc.json`)
6. **narrate** — Generate slide-by-slide narration in the instructor's voice (`slide_description_narration.json`)
7. **audio** — Synthesize narration to MP3 via ElevenLabs or Gemini TTS (`audio/`)
8. **video** — Assemble slide images + audio into a final lecture video (`.mp4`)

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
```

Required system dependencies: `ffmpeg`, `poppler` (for `pdftoppm`)

## Usage

```bash
# Run each step individually
python run_lecture_pipeline.py style sample/transcript.txt
python run_lecture_pipeline.py slides Lecture_17_AI_screenplays.pdf projects/lecture_17
python run_lecture_pipeline.py describe projects/lecture_17
python run_lecture_pipeline.py premise projects/lecture_17
python run_lecture_pipeline.py arc projects/lecture_17
python run_lecture_pipeline.py narrate projects/lecture_17
python run_lecture_pipeline.py audio projects/lecture_17
python run_lecture_pipeline.py video projects/lecture_17 --pdf-name Lecture_17_AI_screenplays.pdf
```

## Project Structure

```
├── README.md
├── style.json                        # Instructor speaking-style profile
├── Lecture_17_AI_screenplays.pdf      # Source slide deck
├── requirements.txt
├── run_lecture_pipeline.py            # CLI entrypoint
├── lecture_agents/                    # Agent code
│   ├── style_analyzer.py
│   ├── slide_describer.py
│   ├── premise_agent.py
│   ├── arc_agent.py
│   ├── narration_agent.py
│   └── audio_agent.py
├── config/                            # Pydantic schemas
│   ├── style_schema.py
│   ├── slide_schema.py
│   ├── premise_schema.py
��   ├── arc_schema.py
│   └── narration_schema.py
├── utils/                             # Utilities
│   ├── rasterize_slides.py
│   └── assemble_video.py
└── projects/
    └── lecture_17/
        ├── premise.json
        ├── arc.json
        ├���─ slide_description.json
        └── slide_description_narration.json
```

`slide_images/`, `audio/`, and the final `.mp4` are generated at runtime and excluded from git.

## Environment Variables

```
GEMINI_API_KEY=...           # Required for all LLM agents
ELEVENLABS_API_KEY=...       # Required for ElevenLabs TTS (or use --provider gemini)
```
