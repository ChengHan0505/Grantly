from __future__ import annotations

from src.database.models import CompanyDocument, Grant, GrantRequirement, RequirementSource, SMEProfile


def evaluate_profile_readiness(profile_data: dict, documents: list[dict]) -> float:
    score = 0.0
    weighted_fields = {
        "company_name": 0.15,
        "industry": 0.1,
        "nationality": 0.1,
        "annual_revenue": 0.15,
        "employee_count": 0.1,
        "target_grant_amount": 0.15,
        "summary": 0.1,
    }

    for field, weight in weighted_fields.items():
        value = profile_data.get(field)
        if value not in (None, "", {}, []):
            score += weight

    if profile_data.get("questionnaire_answers"):
        score += 0.1

    document_types = {doc["document_type"].lower() for doc in documents}
    if "ssm" in document_types:
        score += 0.025
    if "financial_statement" in document_types:
        score += 0.025

    return round(min(score, 1.0), 2)


def evaluate_grant_match(profile: SMEProfile | None, grant: Grant, documents: list[CompanyDocument]) -> dict:
    if profile is None:
        return {
            "suitability_score": 0.0,
            "status": "profile_required",
            "reasons": ["Complete the company profile before grants can be ranked."],
        }

    score = 0.3
    reasons: list[str] = []

    if profile.nationality and grant.nationality and profile.nationality.lower() == grant.nationality.lower():
        score += 0.25
        reasons.append("Nationality matches the grant target market.")

    if profile.industry and grant.industry:
        if grant.industry.lower() == "general":
            score += 0.1
            reasons.append("Grant is open to multiple industries.")
        elif profile.industry.lower() == grant.industry.lower():
            score += 0.25
            reasons.append("Industry matches the grant focus.")

    if profile.target_grant_amount and grant.amount_max and profile.target_grant_amount <= grant.amount_max:
        score += 0.15
        reasons.append("Target grant amount fits within the funding range.")

    if profile.annual_revenue is not None and profile.annual_revenue > 0:
        score += 0.05
        reasons.append("Revenue data is available for eligibility screening.")

    available_document_types = {doc.document_type.lower() for doc in documents}
    requirement_document_types = {req.document_type.lower() for req in grant.requirements if req.document_type}
    covered_count = len(available_document_types.intersection(requirement_document_types))
    if requirement_document_types:
        score += min(covered_count / len(requirement_document_types), 1.0) * 0.15
        if covered_count:
            reasons.append("Some required documents are already available.")

    final_score = round(min(score, 1.0), 2)
    status = "high_fit" if final_score >= 0.75 else "medium_fit" if final_score >= 0.5 else "low_fit"
    if not reasons:
        reasons.append("Basic profile data exists, but fit signals are still limited.")

    return {"suitability_score": final_score, "status": status, "reasons": reasons}


def build_application_checklist(
    requirements: list[GrantRequirement],
    documents: list[CompanyDocument],
    profile: SMEProfile | None,
) -> list[dict]:
    checklist = []
    documents_by_type = {doc.document_type.lower(): doc for doc in documents}

    for requirement in requirements:
        fulfilled = False
        fulfillment_source = None

        if requirement.document_type:
            matching_document = documents_by_type.get(requirement.document_type.lower())
            if matching_document:
                fulfilled = True
                fulfillment_source = f"uploaded:{matching_document.file_name}"

        if not fulfilled and requirement.document_type == "company_profile" and profile is not None:
            fulfilled = True
            fulfillment_source = "generated:company_profile"

        if requirement.source_type == RequirementSource.GENERATED and not fulfilled:
            action_label = "Generate document"
        elif fulfilled:
            action_label = "Ready to download"
        else:
            action_label = "Upload document"

        checklist.append(
            {
                "requirement_id": requirement.id,
                "name": requirement.name,
                "description": requirement.description,
                "source_type": requirement.source_type,
                "document_type": requirement.document_type,
                "is_required": requirement.is_required,
                "fulfilled": fulfilled,
                "fulfillment_source": fulfillment_source,
                "action_label": action_label,
            }
        )

    return checklist
