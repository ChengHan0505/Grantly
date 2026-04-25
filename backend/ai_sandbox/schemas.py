"""Pydantic data contracts for the Malaysia SME Grant Copilot.

These models define the strict structures exchanged between the ingestion,
evaluator, and drafter components of the system.
"""

from typing import List, Literal

from pydantic import BaseModel, Field


class SMEProfile(BaseModel):
    """Normalized profile of a Malaysian SME extracted from source documents."""

    company_name: str
    ssm_number: str
    age_in_months: int
    full_time_employees: int
    ownership_majority: Literal["Local", "Foreign"]
    sector: str
    total_project_cost_rm: int
    requested_funding_rm: int
    outsourced_cost_rm: int
    has_end_user_partner: bool
    company_logo_url: str | None = None
    documents_provided: List[str]
    uploaded_pitch_deck_text: str | None = None


class GrantRequirement(BaseModel):
    """Structured representation of a single grant's eligibility rules."""

    grant_name: str
    promoted_sectors: List[str]
    max_funding_rm: int
    funding_tier_local_percent: int
    funding_tier_foreign_percent: int
    max_outsourcing_percent: int
    requires_end_user_partner: bool
    mandatory_documents: List[str] = Field(default_factory=list)
    application_roadmap: List[str] = Field(default_factory=list)


class EvidenceTrace(BaseModel):
    """A single auditable trace linking one requirement to its evidence."""

    requirement: str
    status: Literal["MET", "UNMET", "UNKNOWN"]
    source_document: str
    reasoning: str


class EvaluatorOutput(BaseModel):
    """Aggregated evaluator result with per-requirement traces and a score."""

    evidence_traces: List[EvidenceTrace] = Field(default_factory=list)
    readiness_score: int


class ActionStep(BaseModel):
    document_name: str
    explanation: str
    action_required: str


class CoachOutput(BaseModel):
    encouraging_message: str
    next_steps: List[ActionStep]


class DeckMetric(BaseModel):
    label: str
    value: str | int | float


class DeckSlide(BaseModel):
    slide_number: int
    title: str
    subtitle: str | None = None
    bullet_points: List[str]
    metrics: List[DeckMetric] = Field(default_factory=list)
    grant_alignment: str | None = None
    speaker_notes: str | None = None


class DeckCritique(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    action_items_to_improve: List[str]


class DeckOutput(BaseModel):
    generated_deck: List[DeckSlide]


class ProposalOutput(BaseModel):
    business_proposal_markdown: str


class ScriptOutput(BaseModel):
    presentation_script_markdown: str


class DrafterOutput(BaseModel):
    proposal: ProposalOutput | None
    deck: DeckOutput | None
    script: ScriptOutput | None
    deck_critique: DeckCritique | None = None
