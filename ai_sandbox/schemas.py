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


class GrantRequirement(BaseModel):
    """Structured representation of a single grant's eligibility rules."""

    grant_name: str
    promoted_sectors: List[str]
    max_funding_rm: int
    funding_tier_local_percent: int
    funding_tier_foreign_percent: int
    max_outsourcing_percent: int
    requires_end_user_partner: bool


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
