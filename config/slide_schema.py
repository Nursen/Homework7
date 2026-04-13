"""Pydantic schema for slide descriptions."""

from pydantic import BaseModel, Field


class SlideDescription(BaseModel):
    """Rich description of a single lecture slide, designed to inform narration generation."""
    slide_number: int = Field(description="1-indexed slide number")
    slide_type: str = Field(description="Category: title, section-header, content, diagram, code, comparison, summary, transition, etc.")
    headline: str = Field(description="The main heading or title text on the slide, verbatim if visible")
    key_points: list[str] = Field(description="Bullet points or main ideas presented on the slide, in order")
    visual_elements: str = Field(description="Description of any diagrams, charts, images, icons, or visual layout choices")
    text_on_slide: str = Field(description="All readable text on the slide, preserving structure")
    pedagogical_purpose: str = Field(description="What this slide is trying to teach or communicate in the arc of the lecture")
    narrative_context: str = Field(description="How this slide connects to the previous slides — what thread is being continued or what new topic is being introduced")
    suggested_talking_points: list[str] = Field(description="What an instructor would likely say or emphasize when presenting this slide, based on its content and position in the deck")
    speaker_notes_hint: str = Field(description="Inferred speaker intent — what the instructor probably wants the audience to take away from this slide")


class SlideDescriptions(BaseModel):
    """Collection of all slide descriptions for a lecture deck."""
    lecture_title: str = Field(default="", description="Overall lecture title if identifiable")
    total_slides: int = Field(description="Total number of slides in the deck")
    slides: list[SlideDescription] = Field(description="Ordered list of slide descriptions")
