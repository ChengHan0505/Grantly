import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.api.schemas import (
    CompanyProfileGenerationRead,
    CompanyProfileGenerationRequest,
    CompanyProfileRead,
    CompanyProfileUpsert,
    DocumentRead,
    SystemStateRead,
    UserCreate,
    UserRead,
)
from backend.src.database.db import create_user, get_company_documents, get_company_profile, get_db, get_user_by_id, upsert_company_profile
from backend.src.database.models import SystemState, User


router = APIRouter(prefix="/users", tags=["users"])


def _has_value(value: object) -> bool:
    return value not in (None, "", {}, [])


def _snake_case(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return normalized or "document"


def _document_type_from_name(name: str) -> str:
    lower_name = name.lower()
    if "ssm" in lower_name:
        return "ssm"
    if "financial" in lower_name or "audit" in lower_name:
        return "financial_statement"
    if "pitch" in lower_name or "deck" in lower_name:
        return "pitch_deck"
    if "bod" in lower_name or "board" in lower_name or "resolution" in lower_name:
        return "bod_resolution"
    if "integrity" in lower_name or "declaration" in lower_name:
        return "integrity_declaration"
    if "proposal" in lower_name:
        return "business_proposal"
    return _snake_case(name)


def _pick_value(primary: dict[str, Any], secondary: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = primary.get(key)
        if _has_value(value):
            return value
    for key in keys:
        value = secondary.get(key)
        if _has_value(value):
            return value
    return None


def _business_stage_from_age(age_in_months: int | float | str | None) -> str | None:
    if age_in_months is None:
        return None
    try:
        age = int(age_in_months)
    except (TypeError, ValueError):
        return None
    if age < 12:
        return "early_stage"
    if age < 36:
        return "growth"
    return "established"


def _build_profile_payload(payload: CompanyProfileGenerationRequest) -> tuple[dict, list[dict]]:
    extractor_profile = payload.extractor_profile.model_dump(exclude_none=True) if payload.extractor_profile else {}
    extracted_data = {**payload.extracted_data, **extractor_profile}
    questionnaire = payload.questionnaire_answers

    ownership = _pick_value(extracted_data, questionnaire, "ownership_majority", "nationality")
    nationality = _pick_value(extracted_data, questionnaire, "nationality")
    if not nationality and isinstance(ownership, str) and ownership.lower() == "local":
        nationality = "Malaysia"

    age_in_months = _pick_value(extracted_data, questionnaire, "age_in_months")
    profile_payload = {
        "company_name": _pick_value(extracted_data, questionnaire, "company_name") or "Unknown Company",
        "industry": _pick_value(extracted_data, questionnaire, "sector", "industry"),
        "nationality": nationality,
        "annual_revenue": _pick_value(extracted_data, questionnaire, "annual_revenue", "revenue"),
        "employee_count": _pick_value(extracted_data, questionnaire, "full_time_employees", "employee_count"),
        "target_grant_amount": _pick_value(extracted_data, questionnaire, "requested_funding_rm", "target_grant_amount"),
        "business_stage": _pick_value(extracted_data, questionnaire, "business_stage")
        or _business_stage_from_age(age_in_months),
        "summary": _pick_value(extracted_data, questionnaire, "summary")
        or payload.raw_text
        or "Company profile generated from onboarding inputs.",
        "questionnaire_answers": questionnaire,
        "extracted_data": {**extracted_data, "raw_text": payload.raw_text} if payload.raw_text else extracted_data,
    }

    documents = [document.model_dump() for document in payload.documents]
    seen_documents = {
        (document["document_type"].lower(), document["file_name"].lower())
        for document in documents
    }
    for document_name in extracted_data.get("documents_provided", []):
        document_type = _document_type_from_name(document_name)
        key = (document_type.lower(), document_name.lower())
        if key in seen_documents:
            continue
        seen_documents.add(key)
        documents.append(
            {
                "document_type": document_type,
                "file_name": document_name,
                "file_url": None,
                "status": "uploaded",
                "metadata": {"source": "extractor_agent"},
            }
        )

    return profile_payload, documents


# Register new user
@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User)
        .filter((User.username == payload.username) | (User.email == payload.email))
        .first()
    )
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with the same username or email already exists.",
        )
    return create_user(
        db,
        username=payload.username,
        email=payload.email,
        external_auth_id=payload.external_auth_id,
    )


# Save company profile
@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


# To get company documents
@router.put("/{user_id}/company-profile", response_model=CompanyProfileRead)
def save_company_profile(user_id: int, payload: CompanyProfileUpsert, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    profile = upsert_company_profile(
        db=db,
        user_id=user_id,
        profile_data=payload.model_dump(exclude={"documents"}),
        documents=[document.model_dump() for document in payload.documents],
    )
    return profile


@router.post("/{user_id}/company-profile/extract", response_model=CompanyProfileGenerationRead)
def generate_company_profile(
    user_id: int,
    payload: CompanyProfileGenerationRequest,
    db: Session = Depends(get_db),
):
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    profile_payload, documents = _build_profile_payload(payload)
    profile = upsert_company_profile(
        db=db,
        user_id=user_id,
        profile_data=profile_payload,
        documents=documents,
    )
    state = db.query(SystemState).filter(SystemState.user_id == user_id).first()
    if state is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="System state was not created.")

    return {
        "profile": profile,
        "documents": get_company_documents(db, user_id),
        "system_state": state,
        "next_endpoint": f"/grants/match/{user_id}",
    }


@router.get("/{user_id}/company-profile", response_model=CompanyProfileRead)
def read_company_profile(user_id: int, db: Session = Depends(get_db)):
    profile = get_company_profile(db, user_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company profile not found.")
    return profile


@router.get("/{user_id}/documents", response_model=list[DocumentRead])
def list_company_documents(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return get_company_documents(db, user_id)


@router.get("/{user_id}/system-state", response_model=SystemStateRead)
def read_system_state(user_id: int, db: Session = Depends(get_db)):
    state = db.query(SystemState).filter(SystemState.user_id == user_id).first()
    if state is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="System state not found.")
    return state
