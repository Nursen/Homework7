"""Pydantic schema for a lecture arc — the HOW of the lecture.

This captures how the lecture unfolds over time: phases, progression, emotional
beats, frameworks, demonstrations, transitions. It assumes the premise (WHAT)
already exists and builds the temporal blueprint on top of it.
"""

from pydantic import BaseModel, Field


class DemonstrationNote(BaseModel):
    description: str = Field(description="What is being demonstrated or shown")
    purpose: str = Field(description="Why this demo exists — what it proves or makes concrete")
    slide_range: str = Field(description="Which slides cover this demo (e.g. '7-9', '11')")


class EmotionalBeat(BaseModel):
    moment: str = Field(description="What happens — e.g. 'surprise reveal', 'humor break', 'cautionary warning'")
    location: str = Field(description="Where in the lecture this occurs — phase name or slide range")
    purpose: str = Field(description="Why this emotional shift matters pedagogically")


class Transition(BaseModel):
    from_phase: str = Field(description="Phase or topic being left")
    to_phase: str = Field(description="Phase or topic being entered")
    technique: str = Field(description="How the transition is accomplished — e.g. 'rhetorical question', 'callback to earlier example', 'provocative claim', 'summary then pivot'")
    slide_number: int = Field(description="Approximate slide where this transition occurs")


class Phase(BaseModel):
    """A major phase or act of the lecture — a sustained section with a unified purpose."""
    name: str = Field(description="Short name for this phase — e.g. 'The Problem', 'Architecture Deep Dive', 'Live Demo'")
    purpose: str = Field(description="What this phase accomplishes in the overall lecture — why it exists here")
    slides: str = Field(description="Slide range covered (e.g. '1-4', '5-9')")
    key_ideas: list[str] = Field(description="The main ideas or points developed during this phase, in order")
    builds_on: str = Field(description="What prior phase or concept this phase depends on or extends")
    sets_up: str = Field(description="What this phase prepares the audience for next")
    demonstrations: list[DemonstrationNote] = Field(default_factory=list, description="Any demos, code walkthroughs, or worked examples in this phase")
    energy_level: str = Field(description="The energy/intensity feel of this phase: high, building, reflective, intense, playful, etc.")


class PedagogicalFramework(BaseModel):
    framework: str = Field(description="Name of the framework or structural pattern — e.g. 'problem-solution', 'concrete-to-abstract', 'scaffolded complexity', 'hero's journey'")
    how_applied: str = Field(description="How this framework manifests in the lecture's structure")


class LectureArc(BaseModel):
    """Lecture arc — the temporal blueprint. HOW the lecture unfolds, phase by phase."""
    title: str = Field(description="Lecture title (carried from premise for reference)")
    total_slides: int = Field(description="Total number of slides")

    # Opening and closing
    hook: str = Field(description="How the lecture opens — the motivating question, story, image, or provocation that grabs attention")
    opening_energy: str = Field(description="The tone and energy of the first 1-2 minutes — sets audience expectations")
    closing_move: str = Field(description="How the lecture ends — synthesis, call to action, callback, cliffhanger, or bridge to next session")
    closing_energy: str = Field(description="The tone and energy of the final moments")

    # Structure
    phases: list[Phase] = Field(description="The major phases/acts of the lecture in order — typically 3-6 phases")
    pedagogical_frameworks: list[PedagogicalFramework] = Field(description="Structural or pedagogical frameworks the lecture employs")

    # Flow dynamics
    transitions: list[Transition] = Field(description="Key transitions between phases or topics — how the lecture moves")
    emotional_beats: list[EmotionalBeat] = Field(description="Moments where energy, tone, or stakes shift")
    tension_arc: str = Field(description="How intellectual tension builds and releases through the lecture — where are the questions raised, where are they answered?")
    pacing_notes: str = Field(description="Observations about pacing — which phases move fast, which linger, where does the lecture breathe?")

    # Idea progression
    idea_build_order: list[str] = Field(description="The sequence in which ideas are introduced and layered — the conceptual scaffold from first to last")
    recurring_threads: list[str] = Field(description="Ideas, examples, or metaphors that appear multiple times across phases — threads that tie the lecture together")
    climax: str = Field(description="The key 'aha' moment or most important insight — where the lecture peaks intellectually")
    resolution: str = Field(description="How the lecture resolves after the climax — synthesis, application, or forward-looking bridge")
