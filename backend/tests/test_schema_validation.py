"""
Unit Tests — Pydantic Schema Validation
=========================================
Scope  : Input/output schema acceptance and rejection via Pydantic models.
Source : backend/src/api/schemas.py
Mocking: None — pure model validation.
"""

import pytest
from pydantic import ValidationError

from backend.src.api.schemas import (
    CompanyProfileUpsert,
    DeckCritiqueRead,
    DrafterOutputRead,
    GenerateDocumentRequest,
    GrantCreate,
    RequirementCreate,
    SlideContentRead,
    UserCreate,
)
from backend.src.database.models import RequirementSource


# ──────────────────────────────────────────────────────────────────────────────
# 1. UserCreate
# ──────────────────────────────────────────────────────────────────────────────

def test_user_create_valid():
    user = UserCreate(username="testuser", email="test@example.com")
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.external_auth_id is None


def test_user_create_username_too_short():
    with pytest.raises(ValidationError):
        UserCreate(username="ab", email="x@x.com")          # min_length=3


def test_user_create_username_too_long():
    with pytest.raises(ValidationError):
        UserCreate(username="a" * 81, email="x@x.com")      # max_length=80


def test_user_create_with_external_auth_id():
    user = UserCreate(username="firebase_user", email="fb@test.com", external_auth_id="uid_abc123")
    assert user.external_auth_id == "uid_abc123"


# ──────────────────────────────────────────────────────────────────────────────
# 2. CompanyProfileUpsert
# ──────────────────────────────────────────────────────────────────────────────

def test_company_profile_upsert_minimal_valid():
    profile = CompanyProfileUpsert(company_name="TechBina Sdn Bhd")
    assert profile.company_name == "TechBina Sdn Bhd"
    assert profile.industry is None
    assert profile.documents == []


def test_company_profile_upsert_missing_company_name():
    with pytest.raises(ValidationError):
        CompanyProfileUpsert()                                # company_name is required


def test_company_profile_upsert_full_payload():
    profile = CompanyProfileUpsert(
        company_name="TechBina Sdn Bhd",
        industry="Technology",
        nationality="Malaysian",
        annual_revenue=500_000.0,
        employee_count=50,
        target_grant_amount=100_000.0,
        business_stage="growth",
        summary="AI grant copilot for SMEs.",
        questionnaire_answers={"q1": "yes"},
        extracted_data={"ssm_number": "1234567-A"},
        documents=[],
    )
    assert profile.nationality == "Malaysian"
    assert profile.annual_revenue == 500_000.0


def test_company_profile_upsert_defaults():
    profile = CompanyProfileUpsert(company_name="Test Co")
    assert profile.questionnaire_answers == {}
    assert profile.extracted_data == {}
    assert profile.documents == []


# ──────────────────────────────────────────────────────────────────────────────
# 3. GrantCreate & RequirementCreate
# ──────────────────────────────────────────────────────────────────────────────

def test_grant_create_valid():
    grant = GrantCreate(
        title="MDEC Digital Grant",
        provider_name="MDEC",
        amount_max=500_000,
        nationality="Malaysian",
        industry="Technology",
    )
    assert grant.title == "MDEC Digital Grant"
    assert grant.status == "open"         # default value


def test_grant_create_missing_required_fields():
    with pytest.raises(ValidationError):
        GrantCreate(title="No Provider")  # provider_name is required


def test_requirement_create_valid():
    req = RequirementCreate(
        name="SSM Certificate",
        source_type=RequirementSource.ATTACHED,
        document_type="ssm",
    )
    assert req.is_required is True        # default value


def test_requirement_create_invalid_source_type():
    with pytest.raises(ValidationError):
        RequirementCreate(
            name="Test Doc",
            source_type="nonexistent_type",   # must be a valid RequirementSource enum
        )


def test_grant_create_with_requirements():
    grant = GrantCreate(
        title="SME Grant",
        provider_name="MITI",
        requirements=[
            {"name": "SSM Certificate", "source_type": "attached", "document_type": "ssm", "is_required": True},
            {"name": "Business Plan", "source_type": "generated", "is_required": False},
        ],
    )
    assert len(grant.requirements) == 2
    assert grant.requirements[0].name == "SSM Certificate"


# ──────────────────────────────────────────────────────────────────────────────
# 4. DrafterOutputRead — Pitch Deck / AI Output Schema
# ──────────────────────────────────────────────────────────────────────────────

def test_slide_content_valid():
    slide = SlideContentRead(
        slide_number=1,
        title="Problem",
        bullet_points=["SMEs struggle to find suitable grants."],
    )
    assert slide.slide_number == 1
    assert slide.subtitle is None
    assert slide.metrics == []


def test_slide_content_missing_title():
    with pytest.raises(ValidationError):
        SlideContentRead(slide_number=1, bullet_points=[])    # title is required


def test_drafter_output_valid_minimal():
    output = DrafterOutputRead(
        business_proposal_markdown="# Business Proposal\n...",
        presentation_script_markdown="# Presentation Script\n...",
    )
    assert output.generated_deck is None
    assert output.generated_documents == []


def test_drafter_output_with_deck():
    output = DrafterOutputRead(
        business_proposal_markdown="# Proposal",
        presentation_script_markdown="# Script",
        generated_deck=[
            {
                "slide_number": 1,
                "title": "Problem",
                "bullet_points": ["Lack of grant access"],
            }
        ],
        deck_critique={
            "strengths": ["Clear problem statement"],
            "weaknesses": ["No revenue data"],
            "action_items_to_improve": ["Add financial projections"],
        },
    )
    assert len(output.generated_deck) == 1
    assert output.deck_critique.strengths[0] == "Clear problem statement"


def test_deck_critique_missing_required_fields():
    with pytest.raises(ValidationError):
        DeckCritiqueRead(strengths=["Good"])    # weaknesses & action_items are required


# ──────────────────────────────────────────────────────────────────────────────
# 5. GenerateDocumentRequest
# ──────────────────────────────────────────────────────────────────────────────

def test_generate_document_request_defaults():
    req = GenerateDocumentRequest()
    assert req.regenerate is False
    assert req.extra_context == {}


def test_generate_document_request_with_requirement_id():
    req = GenerateDocumentRequest(requirement_id=42, document_type="business_plan", regenerate=True)
    assert req.requirement_id == 42
    assert req.regenerate is True