from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy.orm import Session

from backend.src.core.dag_router import (
    build_application_checklist,
    build_application_summary,
    build_coach_output,
    cap_readiness_without_core_documents,
    evaluate_grant_match,
    evaluate_profile_readiness,
)
from backend.src.database.models import (
    CompanyDocument,
    Grant,
    GrantRequirement,
    RequirementSource,
    SMEProfile,
    SessionLocal,
    SystemState,
    User,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, username: str, email: str, external_auth_id: str | None = None) -> User:
    user = User(username=username, email=email, external_auth_id=external_auth_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _has_profile_value(value: object) -> bool:
    return value not in (None, "", {}, [])


def _document_key(document: dict) -> tuple[str, str]:
    return (str(document["document_type"]).lower(), str(document["file_name"]).lower())


def _document_payload_from_model(document: CompanyDocument) -> dict:
    return {
        "document_type": document.document_type,
        "file_name": document.file_name,
        "file_url": document.file_url,
        "status": document.status,
        "metadata": document.metadata_json or {},
    }


INLINE_REVIEW_DOCUMENT_TYPES = {"pitch_deck_critique", "pitch_deck_review", "pitch_deck_evaluation"}


def is_inline_review_document(document: CompanyDocument) -> bool:
    document_type = (document.document_type or "").lower()
    file_name = (document.file_name or "").lower()
    return (
        document_type in INLINE_REVIEW_DOCUMENT_TYPES
        or "pitch_deck_critique" in file_name
        or "pitch_deck_review" in file_name
    )


def _profile_payload_from_model(profile: SMEProfile) -> dict:
    return {
        "company_name": profile.company_name,
        "industry": profile.industry,
        "nationality": profile.nationality,
        "annual_revenue": profile.annual_revenue,
        "employee_count": profile.employee_count,
        "target_grant_amount": profile.target_grant_amount,
        "business_stage": profile.business_stage,
        "summary": profile.summary,
        "questionnaire_answers": profile.questionnaire_answers or {},
        "extracted_data": profile.extracted_data or {},
    }


def _merge_profile_payload(existing_profile: SMEProfile | None, incoming_payload: dict) -> dict:
    if existing_profile is None:
        return dict(incoming_payload)

    merged = _profile_payload_from_model(existing_profile)
    for key, value in incoming_payload.items():
        if key in {"questionnaire_answers", "extracted_data"}:
            if isinstance(value, dict) and value:
                merged[key] = {**(merged.get(key) or {}), **value}
            continue
        if key == "company_name" and value == "Unknown Company" and _has_profile_value(merged.get(key)):
            continue
        if _has_profile_value(value):
            merged[key] = value
    return merged


def upsert_company_profile(
    db: Session,
    user_id: int,
    profile_data: dict,
    documents: Iterable[dict] | None = None,
) -> SMEProfile:
    documents_list = list(documents or [])
    profile = db.query(SMEProfile).filter(SMEProfile.user_id == user_id).first()
    existing_documents = db.query(CompanyDocument).filter(CompanyDocument.user_id == user_id).all()
    readiness_documents = {
        _document_key(_document_payload_from_model(document)): _document_payload_from_model(document)
        for document in existing_documents
    }
    readiness_documents.update({_document_key(document): document for document in documents_list})

    profile_payload = _merge_profile_payload(profile, profile_data)
    readiness_score = evaluate_profile_readiness(profile_payload, list(readiness_documents.values()))
    profile_payload["readiness_score"] = readiness_score

    if profile is None:
        profile = SMEProfile(user_id=user_id, **profile_payload)
        db.add(profile)
    else:
        for key, value in profile_payload.items():
            setattr(profile, key, value)

    if documents_list:
        existing_docs = {
            (doc.document_type.lower(), doc.file_name.lower()): doc
            for doc in existing_documents
        }
        for document in documents_list:
            doc_key = _document_key(document)
            stored = existing_docs.get(doc_key)
            if stored is None:
                db.add(
                    CompanyDocument(
                        user_id=user_id,
                        document_type=document["document_type"],
                        file_name=document["file_name"],
                        file_url=document.get("file_url"),
                        status=document.get("status", "uploaded"),
                        metadata_json=document.get("metadata", {}),
                    )
                )
            else:
                stored.file_url = document.get("file_url")
                stored.status = document.get("status", stored.status)
                stored.metadata_json = document.get("metadata", stored.metadata_json)

    update_system_state(
        db=db,
        user_id=user_id,
        score=readiness_score,
        track="grant_matching" if readiness_score >= 60 else "onboarding",
        trace={"profile_ready": readiness_score >= 60, "document_count": len(readiness_documents)},
        last_step="company_profile_completed",
        auto_commit=False,
    )
    db.commit()
    db.refresh(profile)
    return profile


def get_company_profile(db: Session, user_id: int) -> SMEProfile | None:
    return db.query(SMEProfile).filter(SMEProfile.user_id == user_id).first()


def get_company_documents(db: Session, user_id: int) -> list[CompanyDocument]:
    return db.query(CompanyDocument).filter(CompanyDocument.user_id == user_id).order_by(CompanyDocument.created_at.desc()).all()


def refresh_company_profile_readiness(db: Session, user_id: int, auto_commit: bool = True) -> SMEProfile | None:
    profile = get_company_profile(db, user_id)
    if profile is None:
        return None

    documents = get_company_documents(db, user_id)
    readiness_score = evaluate_profile_readiness(
        _profile_payload_from_model(profile),
        [_document_payload_from_model(document) for document in documents],
    )
    if profile.readiness_score == readiness_score:
        return profile

    profile.readiness_score = readiness_score
    update_system_state(
        db=db,
        user_id=user_id,
        score=readiness_score,
        track="grant_matching" if readiness_score >= 60 else "onboarding",
        trace={"profile_ready": readiness_score >= 60, "document_count": len(documents)},
        last_step="company_profile_refreshed",
        auto_commit=False,
    )
    if auto_commit:
        db.commit()
        db.refresh(profile)
    return profile


def upsert_company_document(db: Session, user_id: int, document_data: dict, auto_commit: bool = True) -> CompanyDocument:
    document_type = document_data["document_type"]
    file_name = document_data["file_name"]
    stored = (
        db.query(CompanyDocument)
        .filter(CompanyDocument.user_id == user_id)
        .filter(CompanyDocument.document_type == document_type)
        .filter(CompanyDocument.file_name == file_name)
        .first()
    )
    if stored is None:
        stored = CompanyDocument(
            user_id=user_id,
            document_type=document_type,
            file_name=file_name,
            file_url=document_data.get("file_url"),
            status=document_data.get("status", "uploaded"),
            metadata_json=document_data.get("metadata", {}),
        )
        db.add(stored)
    else:
        stored.file_url = document_data.get("file_url", stored.file_url)
        stored.status = document_data.get("status", stored.status)
        stored.metadata_json = document_data.get("metadata", stored.metadata_json)

    if auto_commit:
        db.commit()
        db.refresh(stored)
    return stored


def update_system_state(
    db: Session,
    user_id: int,
    score: float,
    track: str,
    trace: dict,
    last_step: str | None = None,
    auto_commit: bool = True,
) -> SystemState:
    state = db.query(SystemState).filter(SystemState.user_id == user_id).first()
    if not state:
        state = SystemState(user_id=user_id)
        db.add(state)

    state.readiness_score = score
    state.current_track = track
    state.evidence_trace = trace
    state.last_step = last_step

    if auto_commit:
        db.commit()
        db.refresh(state)
    return state


def list_grants(db: Session, include_all: bool = False) -> list[Grant]:
    query = db.query(Grant)
    if not include_all:
        query = query.filter(Grant.status == "open")
    return query.order_by(Grant.updated_at.desc()).all()


def get_grant_by_id(db: Session, grant_id: int) -> Grant | None:
    return db.query(Grant).filter(Grant.id == grant_id).first()


def create_grant(db: Session, grant_data: dict) -> Grant:
    requirements_data = grant_data.pop("requirements", [])
    grant = Grant(**grant_data)
    db.add(grant)
    db.flush()

    for requirement in requirements_data:
        db.add(
            GrantRequirement(
                grant_id=grant.id,
                name=requirement["name"],
                description=requirement.get("description"),
                source_type=RequirementSource(requirement["source_type"]),
                document_type=requirement.get("document_type"),
                is_required=requirement.get("is_required", True),
            )
        )

    db.commit()
    db.refresh(grant)
    return grant


def _requirement_source(value: object) -> RequirementSource:
    try:
        return RequirementSource(value)
    except (TypeError, ValueError):
        return RequirementSource.ATTACHED


def upsert_grant_from_scout(db: Session, grant_data: dict) -> tuple[Grant, bool]:
    grant_payload = dict(grant_data)
    requirements_data = grant_payload.pop("requirements", [])
    source_url = grant_payload.get("source_url")
    title = grant_payload.get("title")
    provider_name = grant_payload.get("provider_name")

    grant = None
    if source_url:
        grant = db.query(Grant).filter(Grant.source_url == source_url).first()
    if grant is None and title and provider_name:
        grant = (
            db.query(Grant)
            .filter(Grant.title == title)
            .filter(Grant.provider_name == provider_name)
            .first()
        )

    created = False
    if grant is None:
        grant = Grant(**grant_payload)
        db.add(grant)
        db.flush()
        created = True
    else:
        for key, value in grant_payload.items():
            setattr(grant, key, value)
        db.query(GrantRequirement).filter(GrantRequirement.grant_id == grant.id).delete()

    for requirement in requirements_data:
        db.add(
            GrantRequirement(
                grant_id=grant.id,
                name=requirement["name"],
                description=requirement.get("description"),
                source_type=_requirement_source(requirement.get("source_type")),
                document_type=requirement.get("document_type"),
                is_required=requirement.get("is_required", True),
            )
        )
    db.flush()
    return grant, created


def seed_sample_grants(db: Session) -> None:
    if db.query(Grant).count() > 0:
        return

    sample_grants = [
        {
            "title": "SME Digitalisation Matching Grant",
            "provider_name": "MDEC",
            "source_url": "https://example.com/grants/sme-digitalisation",
            "description": "Supports SMEs adopting digital tools and e-commerce capabilities.",
            "amount_min": 5000,
            "amount_max": 50000,
            "nationality": "Malaysia",
            "industry": "Technology",
            "eligibility_notes": "Open to Malaysian SMEs with active operations.",
            "application_deadline": "2026-12-31",
            "status": "open",
            "metadata_json": {"source": "seed"},
            "requirements": [
                {
                    "name": "SSM Certificate",
                    "description": "Business registration certificate.",
                    "source_type": "attached",
                    "document_type": "ssm",
                },
                {
                    "name": "Latest Financial Statement",
                    "description": "Most recent audited or management accounts.",
                    "source_type": "attached",
                    "document_type": "financial_statement",
                },
                {
                    "name": "Pitch Deck",
                    "description": "Business growth presentation for the digitalisation plan.",
                    "source_type": "generated",
                    "document_type": "pitch_deck",
                },
            ],
        },
        {
            "title": "Market Expansion Support Fund",
            "provider_name": "SME Corp",
            "source_url": "https://example.com/grants/market-expansion",
            "description": "Funds export readiness, branding, and regional market expansion.",
            "amount_min": 10000,
            "amount_max": 80000,
            "nationality": "Malaysia",
            "industry": "General",
            "eligibility_notes": "Strong fit for growth-stage SMEs with export ambitions.",
            "application_deadline": "2026-10-15",
            "status": "open",
            "metadata_json": {"source": "seed"},
            "requirements": [
                {
                    "name": "Company Profile",
                    "description": "Structured company background and growth narrative.",
                    "source_type": "generated",
                    "document_type": "company_profile",
                },
                {
                    "name": "Financial Statement",
                    "description": "Recent company financial statement.",
                    "source_type": "attached",
                    "document_type": "financial_statement",
                },
            ],
        },
    ]

    for grant_data in sample_grants:
        create_grant(db, grant_data)


def rank_grants_for_user(db: Session, user_id: int) -> list[dict]:
    profile = get_company_profile(db, user_id)
    documents = get_company_documents(db, user_id)
    grants = list_grants(db)

    ranked = []
    for grant in grants:
        suitability = evaluate_grant_match(profile=profile, grant=grant, documents=documents)
        ranked.append({"grant": grant, **suitability})

    ranked.sort(key=lambda item: item["suitability_score"], reverse=True)
    return ranked


def build_grant_application_snapshot(db: Session, user_id: int, grant_id: int) -> dict | None:
    grant = get_grant_by_id(db, grant_id)
    profile = get_company_profile(db, user_id)
    if grant is None:
        return None

    documents = get_company_documents(db, user_id)
    checklist = build_application_checklist(grant.requirements, documents, profile)
    documents_by_type = {}
    for doc in documents:
        if doc.status == "generated" and doc.metadata_json.get("grant_id") != grant_id:
            continue
        documents_by_type.setdefault(doc.document_type.lower(), doc)
    for item in checklist:
        if not item["document_type"]:
            continue
        document = documents_by_type.get(item["document_type"].lower())
        if document is not None:
            item["download_url"] = f"/grants/{grant_id}/application/{user_id}/documents/{document.id}/download"
    summary = build_application_summary(checklist)
    capped_readiness_score = cap_readiness_without_core_documents(
        summary["readiness_score"],
        {document.document_type for document in documents},
    )
    if capped_readiness_score != summary["readiness_score"]:
        summary["readiness_score"] = capped_readiness_score
        summary["readiness_level"] = f"{int(round(capped_readiness_score))}% Ready"
        summary["track"] = "coach"
    requirement_types = {
        item["document_type"].lower()
        for item in checklist
        if item["document_type"]
    }
    attached_documents = [
        doc
        for doc in documents
        if doc.status != "generated" and doc.document_type.lower() in requirement_types
    ]
    generated_documents = [
        doc
        for doc in documents
        if doc.status == "generated"
        and doc.metadata_json.get("grant_id") == grant_id
        and not is_inline_review_document(doc)
    ]
    return {
        "grant": grant,
        "checklist": checklist,
        **summary,
        "attached_documents": attached_documents,
        "generated_documents": generated_documents,
        "coach": build_coach_output(summary["missing_required_documents"]) if summary["track"] == "coach" else None,
        "download_package_url": f"/grants/{grant_id}/application/{user_id}/package",
    }
