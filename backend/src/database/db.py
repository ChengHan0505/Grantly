from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy.orm import Session

from src.core.dag_router import build_application_checklist, evaluate_grant_match, evaluate_profile_readiness
from src.database.models import (
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


def upsert_company_profile(
    db: Session,
    user_id: int,
    profile_data: dict,
    documents: Iterable[dict] | None = None,
) -> SMEProfile:
    profile = db.query(SMEProfile).filter(SMEProfile.user_id == user_id).first()
    readiness_score = evaluate_profile_readiness(profile_data, documents or [])
    profile_payload = dict(profile_data)
    profile_payload["readiness_score"] = readiness_score

    if profile is None:
        profile = SMEProfile(user_id=user_id, **profile_payload)
        db.add(profile)
    else:
        for key, value in profile_payload.items():
            setattr(profile, key, value)

    if documents:
        existing_docs = {
            (doc.document_type.lower(), doc.file_name.lower()): doc
            for doc in db.query(CompanyDocument).filter(CompanyDocument.user_id == user_id).all()
        }
        for document in documents:
            doc_key = (document["document_type"].lower(), document["file_name"].lower())
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
        track="grant_search" if readiness_score >= 0.6 else "onboarding",
        trace={"profile_ready": readiness_score >= 0.6, "document_count": len(list(documents or []))},
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


def list_grants(db: Session) -> list[Grant]:
    return db.query(Grant).order_by(Grant.updated_at.desc()).all()


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


def upsert_grant_from_scout(db: Session, grant_data: dict) -> tuple[Grant, bool]:
    requirements_data = grant_data.pop("requirements", [])
    source_url = grant_data.get("source_url")
    title = grant_data.get("title")
    provider_name = grant_data.get("provider_name")

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
        grant = Grant(**grant_data)
        db.add(grant)
        db.flush()
        created = True
    else:
        for key, value in grant_data.items():
            setattr(grant, key, value)
        db.query(GrantRequirement).filter(GrantRequirement.grant_id == grant.id).delete()

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
    return {"grant": grant, "checklist": checklist}
