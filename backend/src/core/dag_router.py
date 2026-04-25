from __future__ import annotations

from backend.src.core.config import settings
from backend.src.database.models import CompanyDocument, Grant, GrantRequirement, RequirementSource, SMEProfile


READINESS_THRESHOLD_PERCENT = float(settings.readiness_threshold_percent)
CORE_READINESS_DOCUMENT_CAP = 79.0
CORE_DOCUMENT_ALIASES = {
    "ssm": {
        "ssm",
        "company_ssm",
        "ssm_cert",
        "ssm_certificate",
        "business_registration",
        "company_registration",
    },
    "financial_statement": {
        "financial_statement",
        "financials",
        "financial_statement_audited",
        "audited_financial_statement",
        "financial_report",
        "management_accounts",
    },
}


def _score_label(score: float) -> str:
    return f"{int(round(score))}% Ready"


def _document_label(document_type: str | None) -> str:
    if not document_type:
        return "document"
    return document_type.replace("_", " ").title()


def _has_value(value: object) -> bool:
    return value not in (None, "", {}, [])


def _normalized_document_types(document_types: set[str]) -> set[str]:
    normalized = set(document_types)
    for canonical_type, aliases in CORE_DOCUMENT_ALIASES.items():
        if normalized.intersection(aliases):
            normalized.add(canonical_type)
    return normalized


def _cap_without_core_documents(score: float, document_types: set[str]) -> float:
    normalized_types = _normalized_document_types(document_types)
    if {"ssm", "financial_statement"}.issubset(normalized_types):
        return score
    return min(score, CORE_READINESS_DOCUMENT_CAP)


def cap_readiness_without_core_documents(score: float, document_types: set[str]) -> float:
    return round(_cap_without_core_documents(score, {document_type.lower() for document_type in document_types}), 1)


def evaluate_profile_readiness(profile_data: dict, documents: list[dict]) -> float:
    score = 0.0
    weighted_fields = {
        "company_name": 15,
        "industry": 10,
        "nationality": 10,
        "employee_count": 10,
        "target_grant_amount": 10,
        "summary": 10,
    }
    extracted_data = profile_data.get("extracted_data") or {}
    aliases = {
        "industry": ["sector"],
        "nationality": ["ownership_majority"],
        "employee_count": ["full_time_employees"],
        "target_grant_amount": ["requested_funding_rm"],
    }

    for field, weight in weighted_fields.items():
        value = profile_data.get(field)
        if not _has_value(value):
            for alias in aliases.get(field, []):
                value = extracted_data.get(alias)
                if _has_value(value):
                    break
        if _has_value(value):
            score += weight

    if _has_value(profile_data.get("annual_revenue")):
        score += 5
    if _has_value(extracted_data.get("total_project_cost_rm")):
        score += 10
    if _has_value(extracted_data.get("ssm_number")):
        score += 5
    if profile_data.get("questionnaire_answers"):
        score += 10

    document_types = _normalized_document_types({doc["document_type"].lower() for doc in documents if doc.get("document_type")})
    if "ssm" in document_types:
        score += 5
    if "financial_statement" in document_types:
        score += 5

    return cap_readiness_without_core_documents(min(score, 100.0), document_types)


def evaluate_grant_match(profile: SMEProfile | None, grant: Grant, documents: list[CompanyDocument]) -> dict:
    if profile is None:
        return {
            "suitability_score": 0.0,
            "readiness_score": 0.0,
            "readiness_level": "Profile required",
            "track": "onboarding",
            "status": "profile_required",
            "reasons": ["Complete the company profile before grants can be ranked."],
            "evidence_traces": [],
        }

    score = 30.0
    reasons: list[str] = []
    evidence_traces: list[dict] = []

    if profile.nationality and grant.nationality and profile.nationality.lower() == grant.nationality.lower():
        score += 20
        reasons.append("Nationality matches the grant target market.")
        evidence_traces.append(
            {
                "requirement": "Nationality eligibility",
                "status": "MET",
                "source_document": "Company Profile.nationality",
                "reasoning": f"{profile.nationality} matches {grant.nationality}.",
            }
        )
    elif grant.nationality:
        evidence_traces.append(
            {
                "requirement": "Nationality eligibility",
                "status": "UNMET" if profile.nationality else "UNKNOWN",
                "source_document": "Company Profile.nationality",
                "reasoning": "The company nationality does not clearly match this grant target.",
            }
        )

    if profile.industry and grant.industry:
        if grant.industry.lower() == "general":
            score += 10
            reasons.append("Grant is open to multiple industries.")
            trace_status = "MET"
            trace_reason = "The grant is open to multiple industries."
        elif profile.industry.lower() == grant.industry.lower():
            score += 20
            reasons.append("Industry matches the grant focus.")
            trace_status = "MET"
            trace_reason = f"{profile.industry} matches {grant.industry}."
        else:
            trace_status = "UNMET"
            trace_reason = f"{profile.industry} does not match the grant focus {grant.industry}."
        evidence_traces.append(
            {
                "requirement": "Sector eligibility",
                "status": trace_status,
                "source_document": "Company Profile.industry",
                "reasoning": trace_reason,
            }
        )

    if profile.target_grant_amount and grant.amount_max and profile.target_grant_amount <= grant.amount_max:
        score += 15
        reasons.append("Target grant amount fits within the funding range.")
        evidence_traces.append(
            {
                "requirement": "Funding cap",
                "status": "MET",
                "source_document": "Company Profile.target_grant_amount",
                "reasoning": f"Requested funding RM {profile.target_grant_amount:,.0f} is within the grant cap.",
            }
        )
    elif grant.amount_max:
        evidence_traces.append(
            {
                "requirement": "Funding cap",
                "status": "UNMET" if profile.target_grant_amount else "UNKNOWN",
                "source_document": "Company Profile.target_grant_amount",
                "reasoning": "Requested funding is missing or exceeds the grant cap.",
            }
        )

    if profile.annual_revenue is not None and profile.annual_revenue > 0:
        score += 5
        reasons.append("Revenue data is available for eligibility screening.")

    available_document_types = {doc.document_type.lower() for doc in documents}
    requirement_document_types = {req.document_type.lower() for req in grant.requirements if req.document_type}
    covered_count = len(available_document_types.intersection(requirement_document_types))
    if requirement_document_types:
        score += min(covered_count / len(requirement_document_types), 1.0) * 10
        if covered_count:
            reasons.append("Some required documents are already available.")
    for requirement in grant.requirements:
        if not requirement.is_required:
            continue
        if requirement.source_type == RequirementSource.GENERATED:
            status = "MET"
            reasoning = "This soft document can be generated by the Drafter Agent."
        elif requirement.document_type and requirement.document_type.lower() in available_document_types:
            status = "MET"
            reasoning = f"{_document_label(requirement.document_type)} is already uploaded."
        else:
            status = "UNMET"
            reasoning = f"{requirement.name} still needs to be uploaded."
        evidence_traces.append(
            {
                "requirement": f"Mandatory document: {requirement.name}",
                "status": status,
                "source_document": "Company Documents",
                "reasoning": reasoning,
            }
        )

    final_score = round(min(score, 100.0), 1)
    required_traces = [trace for trace in evidence_traces if trace["status"] in {"MET", "UNMET", "UNKNOWN"}]
    met_count = sum(1 for trace in required_traces if trace["status"] == "MET")
    readiness_score = round((met_count / len(required_traces)) * 100, 1) if required_traces else final_score
    readiness_score = cap_readiness_without_core_documents(readiness_score, available_document_types)
    track = "drafter" if readiness_score >= READINESS_THRESHOLD_PERCENT else "coach"
    status = "ready" if track == "drafter" else "needs_documents" if final_score >= 50 else "low_fit"
    if not reasons:
        reasons.append("Basic profile data exists, but fit signals are still limited.")

    return {
        "suitability_score": final_score,
        "readiness_score": readiness_score,
        "readiness_level": _score_label(readiness_score),
        "track": track,
        "status": status,
        "reasons": reasons,
        "evidence_traces": evidence_traces,
    }


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

        can_generate = requirement.source_type == RequirementSource.GENERATED and not fulfilled
        can_upload = requirement.source_type == RequirementSource.ATTACHED and not fulfilled
        if can_generate:
            action_label = "Generate document"
            completion_status = "generatable"
        elif fulfilled:
            action_label = "Ready to download"
            completion_status = "complete"
        else:
            action_label = "Upload document"
            completion_status = "missing"

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
                "category": requirement.source_type.value,
                "completion_status": completion_status,
                "can_generate": can_generate,
                "can_upload": can_upload,
                "download_url": None,
                "action_label": action_label,
            }
        )

    return checklist


def build_application_summary(checklist: list[dict]) -> dict:
    required_items = [item for item in checklist if item["is_required"]]
    ready_items = [
        item
        for item in required_items
        if item["fulfilled"] or item["can_generate"]
    ]
    readiness_score = round((len(ready_items) / len(required_items)) * 100, 1) if required_items else 100.0
    missing_required_documents = [
        item["name"]
        for item in required_items
        if not item["fulfilled"] and not item["can_generate"]
    ]
    track = "drafter" if readiness_score >= READINESS_THRESHOLD_PERCENT else "coach"
    return {
        "readiness_score": readiness_score,
        "readiness_level": _score_label(readiness_score),
        "track": track,
        "missing_required_documents": missing_required_documents,
    }


def build_coach_output(missing_documents: list[str]) -> dict | None:
    if not missing_documents:
        return None

    steps = []
    for document_name in missing_documents:
        steps.append(
            {
                "document_name": document_name,
                "explanation": (
                    f"{document_name} is a required hard document for this grant application. "
                    "It normally proves eligibility, company standing, or internal approval."
                ),
                "action_required": (
                    "Upload the existing file if your company already has it. Otherwise, request it "
                    "from the relevant Malaysian authority, licensed auditor, or company secretary, "
                    "then return to this checklist and attach it."
                ),
            }
        )

    return {
        "encouraging_message": (
            "You are close. These missing items are a practical checklist, not a rejection."
        ),
        "next_steps": steps,
    }
