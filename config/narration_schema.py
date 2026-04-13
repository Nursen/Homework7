"""Pydantic schema for slide narrations."""

from pydantic import BaseModel, Field

from config.slide_schema import SlideDescription


class SlideNarration(BaseModel):
    """A single slide's narration paired with its description."""
    slide_number: int = Field(description="1-indexed slide number")
    narration: str = Field(description="The spoken narration for this slide — what the instructor says aloud")
    slide_description: SlideDescription = Field(description="The full slide description this narration was generated from")


class SlideNarrations(BaseModel):
    """All narrations for a lecture deck."""
    lecture_title: str = Field(default="", description="Lecture title")
    instructor_name: str = Field(default="", description="Instructor name from the style profile")
    total_slides: int = Field(description="Total number of slides")
    narrations: list[SlideNarration] = Field(description="Ordered list of slide narrations with their descriptions")
