"""Pydantic schema for a lecture premise — the WHAT of the lecture.

This captures the lecture's identity: thesis, scope, audience, concepts, objectives.
It does NOT describe how the lecture unfolds — that's the arc's job.
"""

from pydantic import BaseModel, Field


class AudienceProfile(BaseModel):
    level: str = Field(description="Audience level: introductory, intermediate, advanced, mixed")
    assumed_background: list[str] = Field(description="Knowledge or skills the audience is assumed to have coming in")
    persona: str = Field(description="Who is in the room — e.g. 'MBA students with coding exposure', 'senior engineers new to ML'")
    pain_points: list[str] = Field(description="What frustrations or gaps this audience likely walks in with that the lecture addresses")


class LearningObjective(BaseModel):
    objective: str = Field(description="What the student should be able to do or understand after this lecture")
    bloom_level: str = Field(description="Bloom's taxonomy level: remember, understand, apply, analyze, evaluate, create")


class ConceptNode(BaseModel):
    concept: str = Field(description="A key concept or topic covered in the lecture")
    definition: str = Field(description="Concise definition or explanation of this concept")
    why_it_matters: str = Field(description="Why this concept is important in the context of this lecture")
    prerequisites: list[str] = Field(default_factory=list, description="Other concepts from this lecture that should be understood first")


class ConceptRelationship(BaseModel):
    from_concept: str = Field(description="The prerequisite concept")
    to_concept: str = Field(description="The concept that depends on it")
    relationship: str = Field(description="How they connect: 'enables', 'motivates', 'contrasts with', 'is a special case of', etc.")


class LecturePremise(BaseModel):
    """Lecture premise — the identity card. WHAT this lecture is, not HOW it flows."""
    title: str = Field(description="Lecture title")
    course: str = Field(description="Course name/number if identifiable, otherwise inferred context")
    lecture_number: str = Field(default="", description="Lecture number or session identifier if identifiable")
    thesis: str = Field(description="The single core argument or thesis of this lecture, in one sentence")
    thesis_expanded: str = Field(description="The thesis unpacked in 2-3 sentences — what exactly is being claimed and why it matters")
    antithesis: str = Field(description="The naive or opposing view this lecture argues against — what would someone believe BEFORE this lecture that they shouldn't believe after?")
    scope_includes: list[str] = Field(description="What this lecture explicitly covers")
    scope_excludes: list[str] = Field(description="What this lecture intentionally does NOT cover and why")
    audience: AudienceProfile
    learning_objectives: list[LearningObjective] = Field(description="3-6 measurable learning objectives")
    key_concepts: list[ConceptNode] = Field(description="Core concepts introduced or reinforced, with dependency ordering")
    concept_relationships: list[ConceptRelationship] = Field(description="How the key concepts relate to each other — the dependency graph")
    common_misconceptions: list[str] = Field(description="Misunderstandings the audience likely has that this lecture addresses or should preempt")
    bridge_from: str = Field(description="What prior knowledge or previous lecture this one builds on")
    bridge_to: str = Field(description="What this lecture sets up for next — the natural follow-on topic")
    takeaway: str = Field(description="The one thing the audience should remember if they forget everything else")
