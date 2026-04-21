from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.api.schemas import GrantApplicationRead, GrantCreate, GrantRead, RankedGrantRead
from backend.src.database.db import build_grant_application_snapshot, create_grant, get_db, get_grant_by_id, rank_grants_for_user


router = APIRouter(prefix="/grants", tags=["grants"])


# Create a grant record, used by the Scout Agent
@router.post("", response_model=GrantRead, status_code=status.HTTP_201_CREATED)
def create_grant_record(payload: GrantCreate, db: Session = Depends(get_db)):
    grant = create_grant(db, payload.model_dump())
    return grant


# Get grant details in "Grant" tab to display to users
@router.get("/match/{user_id}", response_model=list[RankedGrantRead])
def get_ranked_grants(user_id: int, db: Session = Depends(get_db)):
    ranked = rank_grants_for_user(db, user_id)
    return ranked


# To get ranked matching grants for a user, used by the Evaluator Agent
@router.get("/{grant_id}", response_model=GrantRead)
def get_grant_detail(grant_id: int, db: Session = Depends(get_db)):
    grant = get_grant_by_id(db, grant_id)
    if grant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found.")
    return grant


# To get grant application snapshot
@router.get("/{grant_id}/application/{user_id}", response_model=GrantApplicationRead)
def get_grant_application(grant_id: int, user_id: int, db: Session = Depends(get_db)):
    snapshot = build_grant_application_snapshot(db, user_id, grant_id)
    if snapshot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found.")
    return snapshot
