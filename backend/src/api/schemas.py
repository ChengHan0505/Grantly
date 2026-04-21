from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.database.models import RequirementSource


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    email: str
    external_auth_id: str | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    external_auth_id: str | None = None
    created_at: datetime


class DocumentInput(BaseModel):
    document_type: str
    file_name: str
    file_url: str | None = None
    status: str = "uploaded"
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_type: str
    file_name: str
    file_url: str | None = None
    status: str
    metadata_json: dict[str, Any]
    created_at: datetime


class CompanyProfileUpsert(BaseModel):
    company_name: str
    industry: str | None = None
    nationality: str | None = None
    annual_revenue: float | None = None
    employee_count: int | None = None
    target_grant_amount: float | None = None
    business_stage: str | None = None
    summary: str | None = None
    questionnaire_answers: dict[str, Any] = Field(default_factory=dict)
    extracted_data: dict[str, Any] = Field(default_factory=dict)
    documents: list[DocumentInput] = Field(default_factory=list)


class CompanyProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    company_name: str
    industry: str | None = None
    nationality: str | None = None
    annual_revenue: float | None = None
    employee_count: int | None = None
    target_grant_amount: float | None = None
    business_stage: str | None = None
    summary: str | None = None
    questionnaire_answers: dict[str, Any]
    extracted_data: dict[str, Any]
    readiness_score: float
    created_at: datetime
    updated_at: datetime


class RequirementCreate(BaseModel):
    name: str
    description: str | None = None
    source_type: RequirementSource
    document_type: str | None = None
    is_required: bool = True


class RequirementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    source_type: RequirementSource
    document_type: str | None = None
    is_required: bool


class GrantCreate(BaseModel):
    title: str
    provider_name: str
    source_url: str | None = None
    description: str | None = None
    amount_min: float | None = None
    amount_max: float | None = None
    nationality: str | None = None
    industry: str | None = None
    eligibility_notes: str | None = None
    application_deadline: str | None = None
    status: str = "open"
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    requirements: list[RequirementCreate] = Field(default_factory=list)


class GrantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    provider_name: str
    source_url: str | None = None
    description: str | None = None
    amount_min: float | None = None
    amount_max: float | None = None
    nationality: str | None = None
    industry: str | None = None
    eligibility_notes: str | None = None
    application_deadline: str | None = None
    status: str
    metadata_json: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    requirements: list[RequirementRead] = Field(default_factory=list)


class RankedGrantRead(BaseModel):
    grant: GrantRead
    suitability_score: float
    status: str
    reasons: list[str]


class ChecklistItemRead(BaseModel):
    requirement_id: int
    name: str
    description: str | None = None
    source_type: RequirementSource
    document_type: str | None = None
    is_required: bool
    fulfilled: bool
    fulfillment_source: str | None = None
    action_label: str


class GrantApplicationRead(BaseModel):
    grant: GrantRead
    checklist: list[ChecklistItemRead]


class SystemStateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    readiness_score: float
    current_track: str
    evidence_trace: dict[str, Any]
    last_step: str | None = None
    updated_at: datetime
