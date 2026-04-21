from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.schemas import CompanyProfileRead, CompanyProfileUpsert, DocumentRead, SystemStateRead, UserCreate, UserRead
from src.database.db import create_user, get_company_documents, get_company_profile, get_db, get_user_by_id, upsert_company_profile
from src.database.models import SystemState, User


router = APIRouter(prefix="/users", tags=["users"])


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
