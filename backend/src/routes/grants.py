from fastapi import APIRouter, Depends, HTTPException, status
from pathlib import Path
from sqlalchemy.orm import Session

from src.api.schemas import GrantApplicationRead, GrantCreate, GrantRead, RankedGrantRead
from src.core.config import settings
from src.database.db import build_grant_application_snapshot, create_grant, get_db, get_grant_by_id, rank_grants_for_user
from src.scout.runner import run_scout
from src.scout.storage import read_last_report
from src.scout.sources import check_sources_health_from_sources, load_sources_from_curated_outputs


router = APIRouter(prefix="/grants", tags=["grants"])


def _curated_source_files() -> list[str]:
    base_dir = Path(__file__).resolve().parents[2]
    return [
        str(base_dir / "data" / "scout_runs" / "cradle_funds.json"),
        str(base_dir / "data" / "scout_runs" / "mdec.json"),
        str(base_dir / "data" / "scout_runs" / "mtdc_commercial_funds.json"),
        str(base_dir / "data" / "scout_runs" / "mtdc_development_funds.json"),
    ]


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


@router.post("/scout/run")
def run_grant_scout(db: Session = Depends(get_db)):
    sources = load_sources_from_curated_outputs(_curated_source_files())
    report = run_scout(db, sources_override=sources, max_links_per_page_override=0)
    if report.get("status") == "error":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=report["message"])
    return report


@router.get("/scout/last-report")
def get_last_scout_report():
    report = read_last_report(settings.scout_report_path)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No scout report available yet.")
    return report


@router.get("/scout/source-health")
def get_scout_source_health():
    sources = load_sources_from_curated_outputs(_curated_source_files())
    checks = check_sources_health_from_sources(
        sources=sources,
        timeout_seconds=settings.scout_http_timeout_seconds,
        user_agent=settings.scout_user_agent,
    )
    total = sum(len(item["seeds"]) for item in checks)
    healthy = sum(
        1
        for item in checks
        for seed in item["seeds"]
        if seed["status"] == "ok" and (seed["status_code"] or 0) < 400
    )
    return {"summary": {"total_seeds": total, "healthy_seeds": healthy}, "sources": checks}
