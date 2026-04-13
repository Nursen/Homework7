"""Pydantic schema for the instructor speaking-style profile."""

from pydantic import BaseModel, Field


class VocalMannerisms(BaseModel):
    fillers: list[str] = Field(description="Filler words/sounds used frequently (e.g. 'um', 'uh', 'like', 'you know', 'right?')")
    filler_frequency: str = Field(description="How often fillers appear: sparse, moderate, heavy")
    verbal_tics: list[str] = Field(description="Recurring verbal habits beyond fillers (e.g. 'yo', 'bro', trailing 'so…')")
    self_corrections: str = Field(description="How often and how they correct themselves mid-sentence")
    trailing_off: str = Field(description="Pattern of trailing off or leaving sentences unfinished")


class ToneAndEnergy(BaseModel):
    overall_tone: str = Field(description="Primary emotional register (e.g. casual, authoritative, playful)")
    energy_level: str = Field(description="Baseline energy: low-key, moderate, high-energy, variable")
    enthusiasm_markers: list[str] = Field(description="Words/phrases that signal excitement or emphasis")
    humor_style: str = Field(description="Type of humor used: self-deprecating, irreverent, dry, pop-culture, none")
    humor_examples: list[str] = Field(description="Representative funny lines or joke patterns from the transcript")
    warmth: str = Field(description="How warm/approachable vs. distant the speaker feels")


class PacingAndRhythm(BaseModel):
    sentence_length: str = Field(description="Typical sentence length: short/punchy, medium, long/winding, mixed")
    pacing: str = Field(description="Overall speech tempo and variation")
    pause_patterns: str = Field(description="How and when they pause — for emphasis, to think, for audience response")
    build_up_style: str = Field(description="How they build to key points: gradual, sudden reveal, rhetorical question then answer")
    rhythm_signature: str = Field(description="The overall rhythmic feel — staccato, flowing, conversational ping-pong, etc.")


class AudienceInteraction(BaseModel):
    direct_address: str = Field(description="How they address the audience: 'you guys', 'y'all', 'folks', formal 'you'")
    rhetorical_questions: str = Field(description="Frequency and style of rhetorical questions")
    audience_check_ins: list[str] = Field(description="Phrases used to check understanding or engagement (e.g. 'Okay?', 'Right?', 'Makes sense?')")
    call_and_response: str = Field(description="Whether they solicit responses and how")
    chat_integration: str = Field(description="How they reference or integrate live chat/audience input")


class ExplanatoryStyle(BaseModel):
    analogy_usage: str = Field(description="How frequently and what kind of analogies they use")
    example_types: list[str] = Field(description="Types of examples: real-world, hypothetical, pop-culture, personal anecdote")
    abstraction_level: str = Field(description="Do they start abstract then ground, or start concrete then generalize?")
    scaffolding: str = Field(description="How they build on prior knowledge — referencing past lectures, layering concepts")
    simplification_strategy: str = Field(description="How they make complex ideas accessible — anthropomorphize AI, use casual language, etc.")
    jargon_handling: str = Field(description="How they introduce and handle technical terms")


class PedagogyDescriptors(BaseModel):
    teaching_persona: str = Field(description="The overall persona they adopt: mentor, entertainer, coach, expert, peer")
    motivational_tactics: list[str] = Field(description="How they motivate — career relevance, humor, fear of missing out, practical value")
    tangent_behavior: str = Field(description="How they handle tangents — lean in, catch themselves, use them pedagogically")
    real_world_grounding: str = Field(description="How much and how they connect to industry, jobs, real applications")
    opinion_expression: str = Field(description="How openly they share opinions and preferences (e.g. 'OpenAI sucks')")
    vulnerability: str = Field(description="Willingness to say 'I don't know' or admit uncertainty")


class LanguageAndDiction(BaseModel):
    vocabulary_level: str = Field(description="Casual/colloquial, mixed, academic, technical")
    slang_and_colloquialisms: list[str] = Field(description="Specific slang terms used (e.g. 'crashed out', 'let it rip', 'yap')")
    profanity_level: str = Field(description="None, mild ('hell no', 'sucks'), moderate, heavy")
    code_switching: str = Field(description="Whether they shift between registers — e.g. casual to technical and back")
    signature_phrases: list[str] = Field(description="Catchphrases or repeated signature expressions")


class StructuralPatterns(BaseModel):
    opening_style: str = Field(description="How they start a lecture — announcements, anecdotes, diving in")
    transition_phrases: list[str] = Field(description="How they move between topics (e.g. 'Okay, so…', 'Alright', 'Now…')")
    recap_style: str = Field(description="How they summarize or revisit previous material")
    signposting: str = Field(description="How they signal what's coming next")
    closing_style: str = Field(description="How they wrap up sections or the lecture")


class TangentAndAsideStyle(BaseModel):
    """How the instructor goes off-script — the improvised texture that makes lectures feel live."""
    tangent_types: list[str] = Field(description="Categories of tangents: recent news stories, personal anecdotes, career warnings, industry gossip, pop-culture riffs, meta-commentary about the class")
    tangent_examples: list[str] = Field(description="Short examples of actual tangents from the transcript — the topic and how they entered/exited it")
    tangent_frequency: str = Field(description="How often tangents occur: rarely, occasionally, frequently, constantly")
    reentry_phrases: list[str] = Field(description="How they get back on track after a tangent (e.g. 'Anyways…', 'Okay, so…', 'But yeah…')")
    aside_style: str = Field(description="Quick parenthetical comments vs. extended riffs — and how they signal 'this is an aside'")


class SpontaneousInteraction(BaseModel):
    """The texture of real-time audience interaction — not just that they interact, but HOW it feels."""
    name_calling: str = Field(description="Whether and how they call out specific students by name")
    live_reactions: list[str] = Field(description="Examples of reacting to something a student said/typed in real time")
    improvised_roles: str = Field(description="Assigning roles or tasks to students on the fly (e.g. 'you're the mod today')")
    audience_as_characters: str = Field(description="Whether they pull audience members into examples or scenarios")


class MessySpeechPatterns(BaseModel):
    """The genuinely unpolished texture of live speech — not performed messiness, but real messiness."""
    incomplete_thoughts: list[str] = Field(description="Examples of sentences that genuinely don't finish — thoughts abandoned mid-air")
    mid_sentence_pivots: list[str] = Field(description="Examples where they change direction mid-sentence")
    genuine_confusion: list[str] = Field(description="Moments of real uncertainty or forgetting — not performed, actually lost (e.g. 'all 6… the 6? No, 7')")
    math_out_loud: list[str] = Field(description="Examples of working through numbers/costs/sizes in real time, often imprecisely")
    wrong_then_right: list[str] = Field(description="Moments where they say something incorrect, get corrected or self-correct, and move on")


class ComicTiming(BaseModel):
    """The mechanics of how humor lands — rhythm, placement, and delivery."""
    standalone_punchlines: list[str] = Field(description="One-liners delivered as their own beat, hanging in the air (e.g. 'Just a heads up.', 'Like and subscribe.')")
    comic_renaming: list[str] = Field(description="Irreverent nicknames for technical terms invented on the fly (e.g. HNSW → 'not safe for work method')")
    deadpan_moments: list[str] = Field(description="Lines delivered flat/dry for comic effect")
    callback_humor: list[str] = Field(description="Jokes that reference something from earlier in the lecture")
    timing_pattern: str = Field(description="How they set up and deliver jokes — quick throwaway, slow build, or drop-it-and-move-on")


class PerformanceNotes(BaseModel):
    """Notes an actor or voice actor would need to portray this speaker."""
    vocal_energy_arc: str = Field(description="How energy changes through the lecture — steady, builds, peaks and valleys")
    character_essence: str = Field(description="One-paragraph description of who this person IS as a speaker — the vibe, the energy, the persona, as if directing an actor")
    dos: list[str] = Field(description="Key things to DO when imitating this speaker")
    donts: list[str] = Field(description="Things that would feel wrong or out of character")
    comparable_personas: list[str] = Field(description="Public figures or archetypes this speaking style resembles")


class InstructorStyleProfile(BaseModel):
    """Complete speaking-style profile for an instructor, derived from lecture transcripts."""
    instructor_name: str = Field(default="Unknown", description="Instructor name if identifiable")
    course_context: str = Field(default="", description="Course name/number and topic if identifiable")
    vocal_mannerisms: VocalMannerisms
    tone_and_energy: ToneAndEnergy
    pacing_and_rhythm: PacingAndRhythm
    audience_interaction: AudienceInteraction
    explanatory_style: ExplanatoryStyle
    pedagogy: PedagogyDescriptors
    language_and_diction: LanguageAndDiction
    structural_patterns: StructuralPatterns
    tangent_and_aside_style: TangentAndAsideStyle
    spontaneous_interaction: SpontaneousInteraction
    messy_speech_patterns: MessySpeechPatterns
    comic_timing: ComicTiming
    performance_notes: PerformanceNotes
