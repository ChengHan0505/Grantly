from __future__ import annotations

from pydantic import BaseModel, Field


class ScoutSource(BaseModel):
    name: str
    seed_urls: list[str] = Field(default_factory=list)
    allowed_domains: list[str] = Field(default_factory=list)
    allow_url_patterns: list[str] = Field(default_factory=list)
    selectors: list[str] = Field(default_factory=list)
    max_pages: int = 5
    enabled: bool = True


class ScoutRequirement(BaseModel):
    name: str
    description: str | None = None
    source_type: str = "attached"
    document_type: str | None = None
    is_required: bool = True


class ScoutGrantRecord(BaseModel):
    title: str
    provider_name: str
    source_url: str
    description: str | None = None
    amount_min: float | None = None
    amount_max: float | None = None
    nationality: str | None = None
    industry: str | None = None
    eligibility_notes: str | None = None
    application_deadline: str | None = None
    status: str = "open"
    metadata_json: dict = Field(default_factory=dict)
    requirements: list[ScoutRequirement] = Field(default_factory=list)


class ScoutRunReport(BaseModel):
    run_at: str
    source_count: int
    pages_fetched: int
    pages_failed: int
    grants_extracted: int
    grants_inserted: int
    grants_updated: int
    errors: list[str] = Field(default_factory=list)
