"""
Unit Tests — DAG Router (P1 Critical)
======================================
Scope  : Threshold logic (>=80 → drafter, <80 → coach), core-document cap,
         profile readiness, checklist summary.
Source : backend/src/core/dag_router.py
Mocking: No external LLM calls — all pure-function tests.
"""

import pytest

from backend.src.core.dag_router import (
    READINESS_THRESHOLD_PERCENT,
    build_application_summary,
    cap_readiness_without_core_documents,
    evaluate_profile_readiness,
)


# ──────────────────────────────────────────────────────────────────────────────
# 1. THRESHOLD CONSTANT
# ──────────────────────────────────────────────────────────────────────────────

def test_readiness_threshold_is_80():
    """P1 Critical: The routing threshold must be exactly 80."""
    assert READINESS_THRESHOLD_PERCENT == 80


# ──────────────────────────────────────────────────────────────────────────────
# 2. TRACK ASSIGNMENT via build_application_summary
#    (This exercises the same threshold used by evaluate_grant_match)
# ──────────────────────────────────────────────────────────────────────────────

def _make_checklist(total: int, met: int) -> list[dict]:
    """Build a synthetic checklist with `met` fulfilled items out of `total`."""
    items = []
    for i in range(total):
        fulfilled = i < met
        items.append(
            {
                "requirement_id": i + 1,
                "name": f"Req {i + 1}",
                "description": None,
                "source_type": "attached",
                "document_type": "ssm",
                "is_required": True,
                "fulfilled": fulfilled,
                "fulfillment_source": "uploaded:ssm.pdf" if fulfilled else None,
                "category": "attached",
                "completion_status": "complete" if fulfilled else "missing",
                "can_generate": False,
                "can_upload": not fulfilled,
                "download_url": None,
                "action_label": "Ready to download" if fulfilled else "Upload document",
            }
        )
    return items


@pytest.mark.parametrize(
    "met, total, expected_track",
    [
        (10, 10, "drafter"),   # 100% → Track B (Drafter)
        (9, 10, "drafter"),    # 90%  → Track B
        (8, 10, "drafter"),    # 80%  → Track B  ← exact boundary (P1 pass condition)
        (7, 10, "coach"),      # 70%  → Track A (Coach)
        (5, 10, "coach"),      # 50%  → Track A
        (0, 10, "coach"),      # 0%   → Track A
    ],
)
def test_dag_track_assignment(met, total, expected_track):
    """P1 Critical: Score exactly 80 must route to drafter (Track B)."""
    checklist = _make_checklist(total, met)
    summary = build_application_summary(checklist)
    assert summary["track"] == expected_track


def test_dag_score_exactly_80_routes_to_drafter():
    """P1 Critical explicit boundary test: score == 80 → drafter."""
    checklist = _make_checklist(10, 8)          # 8/10 = 80%
    summary = build_application_summary(checklist)
    assert summary["readiness_score"] == 80.0
    assert summary["track"] == "drafter"


def test_dag_score_79_routes_to_coach():
    """P1 Critical: score 79 must NOT reach drafter."""
    # 79/100 rounded — approximate with 79 out of 100 items
    checklist = _make_checklist(100, 79)
    summary = build_application_summary(checklist)
    assert summary["readiness_score"] == 79.0
    assert summary["track"] == "coach"


def test_dag_empty_checklist_returns_100_and_drafter():
    """Edge case: no required items → 100% by convention → drafter."""
    summary = build_application_summary([])
    assert summary["readiness_score"] == 100.0
    assert summary["track"] == "drafter"


# ──────────────────────────────────────────────────────────────────────────────
# 3. CORE-DOCUMENT CAP  (CORE_READINESS_DOCUMENT_CAP = 79.0)
# ──────────────────────────────────────────────────────────────────────────────

def test_score_capped_at_79_without_ssm_and_financials():
    """Without SSM + financial_statement, score must not exceed 79."""
    score = cap_readiness_without_core_documents(95.0, {"business_plan"})
    assert score <= 79.0


def test_score_not_capped_with_both_core_documents():
    """With SSM + financial_statement present, the cap should not apply."""
    score = cap_readiness_without_core_documents(95.0, {"ssm", "financial_statement"})
    assert score == 95.0


def test_score_not_capped_with_ssm_alias():
    """SSM aliases (e.g. ssm_cert) should satisfy the core-document check."""
    score = cap_readiness_without_core_documents(90.0, {"ssm_cert", "financial_statement"})
    assert score == 90.0


def test_score_not_capped_with_financials_alias():
    """Financial statement aliases should satisfy the core-document check."""
    score = cap_readiness_without_core_documents(90.0, {"ssm", "audited_financial_statement"})
    assert score == 90.0


def test_cap_applied_with_only_ssm_present():
    """SSM alone (without financials) must still cap the score."""
    score = cap_readiness_without_core_documents(85.0, {"ssm"})
    assert score <= 79.0


def test_cap_applied_with_only_financials_present():
    """Financials alone (without SSM) must still cap the score."""
    score = cap_readiness_without_core_documents(85.0, {"financial_statement"})
    assert score <= 79.0


# ──────────────────────────────────────────────────────────────────────────────
# 4. PROFILE READINESS  (evaluate_profile_readiness — pure function)
# ──────────────────────────────────────────────────────────────────────────────

def _full_profile() -> dict:
    return {
        "company_name": "TechBina Sdn Bhd",
        "industry": "Technology",
        "nationality": "Malaysian",
        "employee_count": 50,
        "target_grant_amount": 100_000,
        "summary": "AI-powered grant matching for Malaysian SMEs.",
        "annual_revenue": 500_000,
        "questionnaire_answers": {"q1": "yes"},
        "extracted_data": {
            "total_project_cost_rm": 200_000,
            "ssm_number": "1234567-A",
        },
    }


def _core_docs() -> list[dict]:
    return [
        {"document_type": "ssm"},
        {"document_type": "financial_statement"},
    ]


def test_profile_readiness_full_profile_with_core_docs_reaches_threshold():
    """A fully filled profile with both core docs should meet the 80% threshold."""
    score = evaluate_profile_readiness(_full_profile(), _core_docs())
    assert score >= READINESS_THRESHOLD_PERCENT


def test_profile_readiness_empty_profile_scores_zero():
    """An empty profile with no docs should score 0."""
    score = evaluate_profile_readiness({}, [])
    assert score == 0.0


def test_profile_readiness_capped_without_core_docs():
    """Even a full profile is capped at 79 if core docs are missing."""
    score = evaluate_profile_readiness(_full_profile(), [])
    assert score <= 79.0


def test_profile_readiness_score_bounded_0_to_100():
    """Score must always be within [0, 100]."""
    score = evaluate_profile_readiness(_full_profile(), _core_docs())
    assert 0.0 <= score <= 100.0


# ──────────────────────────────────────────────────────────────────────────────
# 5. READINESS LEVEL LABEL
# ──────────────────────────────────────────────────────────────────────────────

def test_readiness_level_label_format():
    """Readiness level string should follow '<N>% Ready' format."""
    checklist = _make_checklist(10, 8)
    summary = build_application_summary(checklist)
    assert summary["readiness_level"] == "80% Ready"


def test_missing_documents_listed_for_coach_track():
    """Coach track summary must list which required documents are still missing."""
    checklist = _make_checklist(5, 3)
    summary = build_application_summary(checklist)
    assert summary["track"] == "coach"
    assert len(summary["missing_required_documents"]) == 2