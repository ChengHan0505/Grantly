"""
Unit Tests — Readiness Score Logic
Source : backend/src/core/dag_router.py → evaluate_profile_readiness
"""
import pytest
from backend.src.core.dag_router import evaluate_profile_readiness


def _make_docs(*types: str) -> list[dict]:
    return [{"document_type": t} for t in types]


def _full_profile() -> dict:
    return {
        "company_name": "TechBina Sdn Bhd",
        "industry": "Technology",
        "nationality": "Malaysian",
        "employee_count": 50,
        "target_grant_amount": 100_000,
        "summary": "AI grant platform",
        "annual_revenue": 500_000,
        "questionnaire_answers": {"q1": "yes"},
        "extracted_data": {"total_project_cost_rm": 200_000, "ssm_number": "A123"},
    }


def test_empty_profile_scores_zero():
    assert evaluate_profile_readiness({}, []) == 1.0


def test_score_bounded_0_to_100():
    score = evaluate_profile_readiness(_full_profile(), _make_docs("ssm", "financial_statement"))
    assert 0.0 <= score <= 100.0


def test_company_name_adds_to_score():
    assert evaluate_profile_readiness({"company_name": "TechBina"}, []) > evaluate_profile_readiness({}, [])


def test_annual_revenue_adds_to_score():
    base = {"company_name": "TechBina"}
    assert evaluate_profile_readiness({**base, "annual_revenue": 500_000}, []) > evaluate_profile_readiness(base, [])


def test_questionnaire_answers_adds_to_score():
    base = {"company_name": "TechBina"}
    assert evaluate_profile_readiness({**base, "questionnaire_answers": {"q1": "yes"}}, []) > evaluate_profile_readiness(base, [])


def test_sector_alias_for_industry():
    score_alias = evaluate_profile_readiness({"extracted_data": {"sector": "Technology"}}, [])
    score_direct = evaluate_profile_readiness({"industry": "Technology"}, [])
    assert score_alias == score_direct


def test_ssm_document_adds_to_score():
    base = {"company_name": "TechBina"}
    assert evaluate_profile_readiness(base, _make_docs("ssm")) > evaluate_profile_readiness(base, [])


def test_financial_statement_adds_to_score():
    base = {"company_name": "TechBina"}
    assert evaluate_profile_readiness(base, _make_docs("financial_statement")) > evaluate_profile_readiness(base, [])


def test_score_capped_at_79_without_core_docs():
    """Full profile with no core documents must not reach the 80% threshold."""
    assert evaluate_profile_readiness(_full_profile(), []) <= 79.0


def test_full_profile_with_core_docs_reaches_threshold():
    score = evaluate_profile_readiness(_full_profile(), _make_docs("ssm", "financial_statement"))
    assert score >= 80.0


@pytest.mark.parametrize("profile,docs,expect_pass", [
    (
        {**_full_profile()},
        [{"document_type": "ssm"}, {"document_type": "financial_statement"}],
        True,
    ),
    ({"company_name": "StartupX"}, [], False),
    (
        {**_full_profile()},
        [{"document_type": "ssm"}],       # missing financials
        False,
    ),
    (
        {**_full_profile()},
        [{"document_type": "financial_statement"}],   # missing SSM
        False,
    ),
    ({}, [], False),
])
def test_mock_sme_profiles(profile, docs, expect_pass):
    score = evaluate_profile_readiness(profile, docs)
    if expect_pass:
        assert score >= 80.0, f"Expected >=80, got {score}"
    else:
        assert score < 80.0, f"Expected <80, got {score}"