from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from backend.src.database.models import RequirementSource


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


class ExtractorProfileInput(BaseModel):
    company_name: str | None = None
    ssm_number: str | None = None
    age_in_months: int | None = None
    full_time_employees: int | None = None
    ownership_majority: str | None = None
    sector: str | None = None
    total_project_cost_rm: float | None = None
    requested_funding_rm: float | None = None
    outsourced_cost_rm: float | None = None
    has_end_user_partner: bool | None = None
    documents_provided: list[str] = Field(default_factory=list)
    uploaded_pitch_deck_text: str | None = None


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_type: str
    file_name: str
    file_url: str | None = None
    status: str
    metadata_json: dict[str, Any]
    created_at: datetime

    @field_serializer("metadata_json")
    def serialize_metadata(self, metadata_json: dict[str, Any]) -> dict[str, Any]:
        if "content_base64" not in metadata_json:
            return metadata_json
        sanitized = dict(metadata_json)
        sanitized["content_base64"] = "<stored>"
        return sanitized


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


class CompanyProfileGenerationRequest(BaseModel):
    raw_text: str | None = None
    questionnaire_answers: dict[str, Any] = Field(default_factory=dict)
    extracted_data: dict[str, Any] = Field(default_factory=dict)
    extractor_profile: ExtractorProfileInput | None = None
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


class EvidenceTraceRead(BaseModel):
    requirement: str
    status: str
    source_document: str
    reasoning: str


class RankedGrantRead(BaseModel):
    grant: GrantRead
    suitability_score: float
    readiness_score: float
    readiness_level: str
    track: str
    status: str
    reasons: list[str]
    evidence_traces: list[EvidenceTraceRead] = Field(default_factory=list)


class WorkspaceRead(BaseModel):
    user: UserRead
    profile: CompanyProfileRead | None = None
    documents: list[DocumentRead] = Field(default_factory=list)
    ranked_grants: list[RankedGrantRead] = Field(default_factory=list)
    grants: list[GrantRead] = Field(default_factory=list)


class ChecklistItemRead(BaseModel):
    requirement_id: int
    name: str
    description: str | None = None
    source_type: RequirementSource
    document_type: str | None = None
    is_required: bool
    fulfilled: bool
    fulfillment_source: str | None = None
    category: str
    completion_status: str
    can_generate: bool
    can_upload: bool
    download_url: str | None = None
    action_label: str


class CoachStepRead(BaseModel):
    document_name: str
    explanation: str
    action_required: str


class CoachOutputRead(BaseModel):
    encouraging_message: str
    next_steps: list[CoachStepRead] = Field(default_factory=list)


class ApplicationRoadmapStepRead(BaseModel):
    step_number: int
    title: str
    status: str
    owner: str
    description: str
    action: str
    requirement_id: int | None = None
    document_type: str | None = None
    download_url: str | None = None


class ApplicationRoadmapRead(BaseModel):
    grant_id: int
    grant_title: str
    provider_name: str
    generated_by: str
    encouraging_message: str
    steps: list[ApplicationRoadmapStepRead] = Field(default_factory=list)


class GrantApplicationRead(BaseModel):
    grant: GrantRead
    checklist: list[ChecklistItemRead]
    readiness_score: float
    readiness_level: str
    track: str
    missing_required_documents: list[str] = Field(default_factory=list)
    attached_documents: list[DocumentRead] = Field(default_factory=list)
    generated_documents: list[DocumentRead] = Field(default_factory=list)
    coach: CoachOutputRead | None = None
    download_package_url: str


class SystemStateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    readiness_score: float
    current_track: str
    evidence_trace: dict[str, Any]
    last_step: str | None = None
    updated_at: datetime


class CompanyProfileGenerationRead(BaseModel):
    profile: CompanyProfileRead
    documents: list[DocumentRead]
    system_state: SystemStateRead
    next_endpoint: str


class GenerateDocumentRequest(BaseModel):
    requirement_id: int | None = None
    document_type: str | None = None
    document_name: str | None = None
    regenerate: bool = False
    extra_context: dict[str, Any] = Field(default_factory=dict)


class GeneratedDocumentRead(BaseModel):
    document: DocumentRead
    requirement_id: int | None = None
    document_type: str
    content_markdown: str
    message: str


class DraftApplicationRequest(BaseModel):
    uploaded_pitch_deck_text: str | None = None
    extra_context: dict[str, Any] = Field(default_factory=dict)


class SlideMetricRead(BaseModel):
    label: str
    value: str


class SlideContentRead(BaseModel):
    slide_number: int
    title: str
    subtitle: str | None = None
    bullet_points: list[str]
    metrics: list[SlideMetricRead] = Field(default_factory=list)
    grant_alignment: str | None = None
    speaker_notes: str | None = None


class DeckCritiqueRead(BaseModel):
    overall_score: int | None = None
    review_summary: str | None = None
    strengths: list[str]
    weaknesses: list[str]
    action_items_to_improve: list[str]


class PitchDeckEvaluationRead(BaseModel):
    critique: DeckCritiqueRead
    evaluated_document: DocumentRead
    review_document: DocumentRead | None = None
    message: str


class DrafterOutputRead(BaseModel):
    business_proposal_markdown: str
    presentation_script_markdown: str
    generated_deck: list[SlideContentRead] | None = None
    deck_critique: DeckCritiqueRead | None = None
    generated_documents: list[DocumentRead] = Field(default_factory=list)


class PitchDeckRequest(BaseModel):
    sme_profile: dict[str, Any]
    grant_context: dict[str, Any] = Field(default_factory=dict)
    filename: str | None = None


class PitchDeckGenerateRequest(BaseModel):
    creative: bool = True
    filename: str | None = None
    extra_context: dict[str, Any] = Field(default_factory=dict)


class GeneratedFileSummaryRead(BaseModel):
    id: int
    document_type: str
    file_name: str
    status: str
    content_type: str | None = None
    generation_mode: str | None = None
    created_at: datetime


class StoredPitchDeckRead(BaseModel):
    document: GeneratedFileSummaryRead
    download_url: str
    message: str
    layout_plan: dict[str, Any] = Field(default_factory=dict)


class ScoutStartRequest(BaseModel):
    source_file: str | None = None
    run_mode: str = "curated"
    max_links_per_page: int | None = None


class ScoutStatusRead(BaseModel):
    status: str
    run_mode: str | None = None
    started_at: str | None = None
    finished_at: str | None = None
    max_runtime_hours: float
    stop_requested: bool
    last_report: dict[str, Any] | None = None
    message: str | None = None
