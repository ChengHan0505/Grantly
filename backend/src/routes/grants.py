from __future__ import annotations

import base64
import io
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ai_sandbox.scout.runner import run_scout
from ai_sandbox.scout.sources import (
    check_sources_health_from_sources,
    load_sources_from_curated_outputs,
    load_sources_from_file,
)
from ai_sandbox.scout.storage import read_last_report
from ai_sandbox.pptx_drafter import (
    PPTX_MIME,
    build_creative_pitch_deck_pptx,
    build_pitch_deck_pptx,
    build_pitch_deck_slides,
)
from backend.src.api.schemas import (
    DraftApplicationRequest,
    DrafterOutputRead,
    GeneratedDocumentRead,
    GenerateDocumentRequest,
    GrantApplicationRead,
    GrantCreate,
    GrantRead,
    PitchDeckGenerateRequest,
    PitchDeckRequest,
    RankedGrantRead,
    ScoutStartRequest,
    ScoutStatusRead,
    StoredPitchDeckRead,
)
from backend.src.core.config import settings
from backend.src.database.db import (
    build_grant_application_snapshot,
    create_grant,
    get_company_documents,
    get_company_profile,
    get_db,
    get_grant_by_id,
    get_user_by_id,
    list_grants,
    rank_grants_for_user,
    upsert_company_document,
)
from backend.src.database.models import CompanyDocument, RequirementSource, SessionLocal


router = APIRouter(prefix="/grants", tags=["grants"])

SCOUT_STATE: dict[str, Any] = {
    "status": "idle",
    "run_mode": None,
    "started_at": None,
    "finished_at": None,
    "stop_requested": False,
    "last_report": None,
    "message": "Scout has not started in this process.",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _project_dir() -> Path:
    return Path(__file__).resolve().parents[3]


def _backend_dir() -> Path:
    return Path(__file__).resolve().parents[2]


def _resolve_backend_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    project_candidate = _project_dir() / path
    if path.parts and path.parts[0] == "backend":
        return project_candidate
    backend_candidate = _backend_dir() / path
    return backend_candidate if backend_candidate.exists() else project_candidate


def _curated_source_files() -> list[str]:
    base_dir = _backend_dir()
    return [
        str(base_dir / "data" / "scout_runs" / "cradle_funds.json"),
        str(base_dir / "data" / "scout_runs" / "mdec.json"),
        str(base_dir / "data" / "scout_runs" / "mtdc_commercial_funds.json"),
        str(base_dir / "data" / "scout_runs" / "mtdc_development_funds.json"),
    ]


def _default_scout_source_file() -> Path:
    return _resolve_backend_path(settings.scout_source_file)


def _load_default_scout_sources() -> list:
    sources = load_sources_from_file(str(_default_scout_source_file()))
    if sources:
        return sources
    return load_sources_from_curated_outputs(_curated_source_files())


def _scout_status(message: str | None = None) -> dict:
    report = SCOUT_STATE.get("last_report")
    if report is None:
        report = read_last_report(str(_resolve_backend_path(settings.scout_report_path)))
    return {
        "status": SCOUT_STATE["status"],
        "run_mode": SCOUT_STATE.get("run_mode"),
        "started_at": SCOUT_STATE.get("started_at"),
        "finished_at": SCOUT_STATE.get("finished_at"),
        "max_runtime_hours": settings.scout_max_runtime_hours,
        "stop_requested": SCOUT_STATE["stop_requested"],
        "last_report": report,
        "message": message if message is not None else SCOUT_STATE.get("message"),
    }


def _run_scout_job(source_file: str | None, run_mode: str, max_links_per_page: int | None) -> None:
    db = SessionLocal()
    start_time = datetime.now(timezone.utc)
    try:
        SCOUT_STATE.update(
            {
                "status": "running",
                "run_mode": run_mode,
                "started_at": start_time.isoformat(),
                "finished_at": None,
                "stop_requested": SCOUT_STATE.get("stop_requested", False),
                "message": "Scout is crawling and extracting grant data.",
            }
        )

        def should_stop() -> bool:
            elapsed_hours = (datetime.now(timezone.utc) - start_time).total_seconds() / 3600
            return bool(SCOUT_STATE["stop_requested"]) or elapsed_hours >= settings.scout_max_runtime_hours

        sources = _load_default_scout_sources() if run_mode == "curated" else None
        report = run_scout(
            db,
            source_file=source_file,
            sources_override=sources,
            max_links_per_page_override=max_links_per_page,
            should_stop=should_stop,
        )
        SCOUT_STATE.update(
            {
                "status": report.get("status", "completed"),
                "finished_at": _utc_now_iso(),
                "last_report": report,
                "message": "Scout run finished.",
            }
        )
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        SCOUT_STATE.update(
            {
                "status": "error",
                "finished_at": _utc_now_iso(),
                "message": f"Scout run failed: {exc}",
            }
        )
    finally:
        db.close()


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_") or "document"


def _profile_deck_context(profile: Any) -> dict[str, Any]:
    extracted = profile.extracted_data or {}
    data = dict(extracted)
    data.update(
        {
            "company_name": profile.company_name,
            "sector": profile.industry or extracted.get("sector"),
            "nationality": profile.nationality,
            "employee_count": profile.employee_count,
            "requested_funding_rm": profile.target_grant_amount or extracted.get("requested_funding_rm"),
            "target_grant_amount": profile.target_grant_amount,
            "summary": profile.summary,
        }
    )
    return {key: value for key, value in data.items() if value not in (None, "", [], {})}


def _grant_deck_context(grant: Any) -> dict[str, Any]:
    return {
        "grant_name": grant.title,
        "title": grant.title,
        "provider_name": grant.provider_name,
        "amount_min": grant.amount_min,
        "amount_max": grant.amount_max,
        "industry": grant.industry,
        "nationality": grant.nationality,
        "application_deadline": grant.application_deadline,
    }


def _pptx_response(content: bytes, filename: str) -> StreamingResponse:
    return StreamingResponse(
        io.BytesIO(content),
        media_type=PPTX_MIME,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _render_generated_document(
    document_name: str,
    document_type: str,
    grant: Any,
    profile: Any,
    extra_context: dict[str, Any],
) -> str:
    extracted = profile.extracted_data or {}
    company_name = profile.company_name
    sector = profile.industry or extracted.get("sector") or "the target sector"
    requested_amount = profile.target_grant_amount or extracted.get("requested_funding_rm")
    project_cost = extracted.get("total_project_cost_rm")
    employees = profile.employee_count or extracted.get("full_time_employees")

    if document_type == "pitch_deck":
        return (
            f"# {company_name} Pitch Deck for {grant.title}\n\n"
            "## Slide 1: Problem and Solution\n"
            f"- {company_name} operates in {sector} and is applying for {grant.title}.\n"
            "- The project addresses a practical SME growth or digitalisation gap.\n\n"
            "## Slide 2: Traction and Execution\n"
            f"- Team size: {employees or 'not specified'} full-time employees.\n"
            f"- Total project cost: RM {project_cost or 'not specified'}.\n\n"
            "## Slide 3: Grant Ask and Use of Funds\n"
            f"- Requested funding: RM {requested_amount or 'not specified'}.\n"
            f"- Provider: {grant.provider_name}.\n"
        )

    if document_type in {"business_proposal", "proposal"}:
        return (
            f"# Business Proposal: {grant.title}\n\n"
            f"{company_name} is a Malaysian SME in {sector} seeking support from "
            f"{grant.provider_name} through {grant.title}. The company is requesting "
            f"RM {requested_amount or 'an amount aligned with the grant cap'} to co-fund "
            f"a project with total cost RM {project_cost or 'to be confirmed'}. "
            "The proposal emphasizes eligibility, execution readiness, measurable outcomes, "
            "and responsible use of funds.\n\n"
            f"Additional context: {json.dumps(extra_context, ensure_ascii=True)}\n"
        )

    if document_type == "company_profile":
        return (
            f"# Company Profile: {company_name}\n\n"
            f"- Sector: {sector}\n"
            f"- Nationality / ownership: {profile.nationality or extracted.get('ownership_majority') or 'not specified'}\n"
            f"- Employees: {employees or 'not specified'}\n"
            f"- Target grant amount: RM {requested_amount or 'not specified'}\n\n"
            f"{profile.summary or 'Company summary to be completed.'}\n"
        )

    return (
        f"# {document_name}\n\n"
        f"Generated draft for {company_name}'s {grant.title} application.\n\n"
        "Review this draft, fill in any agency-specific fields, and attach it to the submission package.\n"
    )


def _select_requirement(grant: Any, payload: GenerateDocumentRequest) -> Any | None:
    if payload.requirement_id is not None:
        return next((requirement for requirement in grant.requirements if requirement.id == payload.requirement_id), None)
    if payload.document_type:
        return next(
            (
                requirement
                for requirement in grant.requirements
                if requirement.document_type and requirement.document_type.lower() == payload.document_type.lower()
            ),
            None,
        )
    return None


def _store_generated_markdown(
    db: Session,
    user_id: int,
    grant_id: int,
    grant_title: str,
    document_type: str,
    document_name: str,
    content: str,
    extra_metadata: dict[str, Any] | None = None,
) -> CompanyDocument:
    metadata = {
        "source": "drafter_agent",
        "grant_id": grant_id,
        "content_markdown": content,
        "generated_at": _utc_now_iso(),
    }
    if extra_metadata:
        metadata.update(extra_metadata)
    return upsert_company_document(
        db,
        user_id,
        {
            "document_type": document_type,
            "file_name": f"{_slug(grant_title)}_{_slug(document_name)}.md",
            "file_url": None,
            "status": "generated",
            "metadata": metadata,
        },
    )


def _store_generated_pptx(
    db: Session,
    user_id: int,
    grant_id: int,
    filename: str,
    content: bytes,
    layout_plan: dict[str, Any],
    generation_mode: str,
) -> CompanyDocument:
    if not filename.lower().endswith(".pptx"):
        filename = f"{filename}.pptx"
    return upsert_company_document(
        db,
        user_id,
        {
            "document_type": "pitch_deck",
            "file_name": filename,
            "file_url": None,
            "status": "generated",
            "metadata": {
                "source": "drafter_agent",
                "grant_id": grant_id,
                "content_type": PPTX_MIME,
                "content_base64": base64.b64encode(content).decode("ascii"),
                "layout_plan": layout_plan,
                "generation_mode": generation_mode,
                "generated_at": _utc_now_iso(),
            },
        },
    )


def _stored_pptx_document(db: Session, user_id: int, grant_id: int) -> CompanyDocument | None:
    candidates = (
        db.query(CompanyDocument)
        .filter(CompanyDocument.user_id == user_id)
        .filter(CompanyDocument.document_type == "pitch_deck")
        .filter(CompanyDocument.status == "generated")
        .order_by(CompanyDocument.created_at.desc())
        .all()
    )
    for document in candidates:
        if document.metadata_json.get("grant_id") == grant_id and document.metadata_json.get("content_base64"):
            return document
    return None


def _pptx_bytes_from_document(document: CompanyDocument) -> bytes | None:
    content_base64 = document.metadata_json.get("content_base64")
    if not content_base64:
        return None
    return base64.b64decode(content_base64)


def _generated_file_summary(document: CompanyDocument) -> dict[str, Any]:
    return {
        "id": document.id,
        "document_type": document.document_type,
        "file_name": document.file_name,
        "status": document.status,
        "content_type": document.metadata_json.get("content_type"),
        "generation_mode": document.metadata_json.get("generation_mode"),
        "created_at": document.created_at,
    }


@router.post("", response_model=GrantRead, status_code=status.HTTP_201_CREATED)
def create_grant_record(payload: GrantCreate, db: Session = Depends(get_db)):
    grant = create_grant(db, payload.model_dump())
    return grant


@router.get("", response_model=list[GrantRead])
def list_grant_records(db: Session = Depends(get_db)):
    return list_grants(db)


@router.get("/match/{user_id}", response_model=list[RankedGrantRead])
def get_ranked_grants(user_id: int, db: Session = Depends(get_db)):
    if get_user_by_id(db, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return rank_grants_for_user(db, user_id)


@router.post("/drafter/pitch-deck")
def generate_pitch_deck_from_profile(payload: PitchDeckRequest):
    content = build_pitch_deck_pptx(payload.sme_profile, payload.grant_context)
    company = payload.sme_profile.get("company_name") or "sme"
    filename = payload.filename or f"{_slug(str(company))}_pitch_deck.pptx"
    if not filename.lower().endswith(".pptx"):
        filename = f"{filename}.pptx"
    return _pptx_response(content, filename)


@router.post("/drafter/pitch-deck/creative")
async def generate_creative_pitch_deck_from_profile(payload: PitchDeckRequest):
    content, _plan = await build_creative_pitch_deck_pptx(
        payload.sme_profile,
        payload.grant_context,
        api_key=settings.zai_api_key,
    )
    company = payload.sme_profile.get("company_name") or "sme"
    filename = payload.filename or f"{_slug(str(company))}_creative_pitch_deck.pptx"
    if not filename.lower().endswith(".pptx"):
        filename = f"{filename}.pptx"
    return _pptx_response(content, filename)


@router.post("/scout/start", response_model=ScoutStatusRead, status_code=status.HTTP_202_ACCEPTED)
def start_grant_scout(
    payload: ScoutStartRequest,
    background_tasks: BackgroundTasks,
):
    if SCOUT_STATE["status"] == "running":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Scout is already running.")
    if payload.run_mode not in {"curated", "file"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="run_mode must be 'curated' or 'file'.")
    if payload.run_mode == "file" and not payload.source_file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="source_file is required for file mode.")

    background_tasks.add_task(_run_scout_job, payload.source_file, payload.run_mode, payload.max_links_per_page)
    SCOUT_STATE.update(
        {
            "status": "queued",
            "run_mode": payload.run_mode,
            "started_at": _utc_now_iso(),
            "finished_at": None,
            "stop_requested": False,
            "message": "Scout run queued.",
        }
    )
    return _scout_status()


@router.post("/scout/stop", response_model=ScoutStatusRead)
def stop_grant_scout():
    if SCOUT_STATE["status"] not in {"queued", "running"}:
        return _scout_status("No active scout run to stop.")
    SCOUT_STATE["stop_requested"] = True
    SCOUT_STATE["message"] = "Stop requested. Scout will halt at the next safe checkpoint."
    return _scout_status()


@router.get("/scout/status", response_model=ScoutStatusRead)
def get_grant_scout_status():
    return _scout_status()


@router.post("/scout/run")
def run_grant_scout(db: Session = Depends(get_db)):
    sources = _load_default_scout_sources()
    report = run_scout(db, sources_override=sources)
    if report.get("status") == "error":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=report["message"])
    SCOUT_STATE.update({"status": report.get("status", "ok"), "last_report": report, "finished_at": _utc_now_iso()})
    return report


@router.get("/scout/last-report")
def get_last_scout_report():
    report = read_last_report(str(_resolve_backend_path(settings.scout_report_path)))
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No scout report available yet.")
    return report


@router.get("/scout/source-health")
def get_scout_source_health():
    sources = _load_default_scout_sources()
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


@router.get("/{grant_id}", response_model=GrantRead)
def get_grant_detail(grant_id: int, db: Session = Depends(get_db)):
    grant = get_grant_by_id(db, grant_id)
    if grant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found.")
    return grant


@router.get("/{grant_id}/application/{user_id}", response_model=GrantApplicationRead)
def get_grant_application(grant_id: int, user_id: int, db: Session = Depends(get_db)):
    if get_user_by_id(db, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    snapshot = build_grant_application_snapshot(db, user_id, grant_id)
    if snapshot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found.")
    return snapshot


@router.post("/{grant_id}/application/{user_id}/documents/generate", response_model=GeneratedDocumentRead)
def generate_application_document(
    grant_id: int,
    user_id: int,
    payload: GenerateDocumentRequest,
    db: Session = Depends(get_db),
):
    if get_user_by_id(db, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    grant = get_grant_by_id(db, grant_id)
    if grant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found.")
    profile = get_company_profile(db, user_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company profile not found.")

    requirement = _select_requirement(grant, payload)
    if payload.requirement_id is not None and requirement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found for this grant.")
    if requirement is not None and requirement.source_type != RequirementSource.GENERATED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only generated requirements can use Drafter.")

    document_type = payload.document_type or (requirement.document_type if requirement else None)
    document_name = payload.document_name or (requirement.name if requirement else None)
    if not document_type and not document_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="document_type or requirement_id is required.")
    document_type = document_type or _slug(document_name or "generated_document")
    document_name = document_name or document_type.replace("_", " ").title()
    content = _render_generated_document(document_name, document_type, grant, profile, payload.extra_context)

    document = _store_generated_markdown(
        db,
        user_id,
        grant_id,
        grant.title,
        document_type,
        document_name,
        content,
        {
            "requirement_id": requirement.id if requirement else None,
            "extra_context": payload.extra_context,
        },
    )
    return {
        "document": document,
        "requirement_id": requirement.id if requirement else None,
        "document_type": document_type,
        "content_markdown": content,
        "message": "Generated document is ready for the submission package.",
    }


@router.post("/{grant_id}/application/{user_id}/draft", response_model=DrafterOutputRead)
def draft_application_bundle(
    grant_id: int,
    user_id: int,
    payload: DraftApplicationRequest,
    db: Session = Depends(get_db),
):
    grant = get_grant_by_id(db, grant_id)
    if grant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found.")
    profile = get_company_profile(db, user_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company profile not found.")
    snapshot = build_grant_application_snapshot(db, user_id, grant_id)
    if snapshot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found.")
    if snapshot["track"] != "drafter":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Complete the hard-document checklist before running the Drafter Agent.",
                "readiness_score": snapshot["readiness_score"],
                "missing_required_documents": snapshot["missing_required_documents"],
            },
        )

    business_proposal = _render_generated_document(
        "Business Proposal",
        "business_proposal",
        grant,
        profile,
        payload.extra_context,
    )
    presentation_script = (
        f"# Presentation Script: {grant.title}\n\n"
        f"Good day. {profile.company_name} is applying for {grant.title} from {grant.provider_name}. "
        f"Our company operates in {profile.industry or 'the target sector'} and is seeking "
        f"RM {profile.target_grant_amount or 'an aligned funding amount'} to execute a focused growth project. "
        "This submission is backed by the required company documents and a clear plan for responsible delivery."
    )

    extracted = profile.extracted_data or {}
    uploaded_deck_text = payload.uploaded_pitch_deck_text or extracted.get("uploaded_pitch_deck_text")
    generated_deck = None
    deck_critique = None
    if uploaded_deck_text:
        deck_critique = {
            "strengths": [
                "The uploaded deck gives the Drafter Agent a concrete founder narrative to refine.",
                "Existing material can be reused instead of starting from a blank page.",
            ],
            "weaknesses": [
                "Ensure the deck explicitly connects project cost, funding ask, and grant outcomes.",
                "Add evidence for traction, partner validation, and document readiness where possible.",
            ],
            "action_items_to_improve": [
                "Add one slide on use of funds.",
                "Add one slide mapping the company profile to the grant criteria.",
                "Keep financial figures consistent with the company profile.",
            ],
        }
        deck_markdown = (
            "# Pitch Deck Critique\n\n"
            "## Strengths\n"
            + "\n".join(f"- {item}" for item in deck_critique["strengths"])
            + "\n\n## Weaknesses\n"
            + "\n".join(f"- {item}" for item in deck_critique["weaknesses"])
            + "\n\n## Action Items\n"
            + "\n".join(f"- {item}" for item in deck_critique["action_items_to_improve"])
            + "\n"
        )
        deck_document_type = "pitch_deck_critique"
        deck_document_name = "Pitch Deck Critique"
    else:
        generated_deck = [
            {
                "slide_number": 1,
                "title": "Problem and Solution",
                "bullet_points": [
                    f"{profile.company_name} addresses a practical gap in {profile.industry or 'the target sector'}.",
                    "The proposed project is aligned with the grant's intended outcomes.",
                    "The solution is scoped for measurable delivery after funding.",
                ],
            },
            {
                "slide_number": 2,
                "title": "Traction and Team",
                "bullet_points": [
                    f"Team size: {profile.employee_count or 'not specified'} full-time employees.",
                    "Core company documents are available for submission.",
                    "Execution risk is reduced through a focused application checklist.",
                ],
            },
            {
                "slide_number": 3,
                "title": "Ask and Use of Funds",
                "bullet_points": [
                    f"Target grant amount: RM {profile.target_grant_amount or 'not specified'}.",
                    f"Provider: {grant.provider_name}.",
                    "Funds will support project delivery and application outcomes.",
                ],
            },
        ]
        deck_markdown = "# Generated Pitch Deck\n\n" + "\n\n".join(
            "## Slide {slide_number}: {title}\n{bullets}".format(
                slide_number=slide["slide_number"],
                title=slide["title"],
                bullets="\n".join(f"- {point}" for point in slide["bullet_points"]),
            )
            for slide in generated_deck
        )
        deck_document_type = "pitch_deck"
        deck_document_name = "Pitch Deck"

    generated_documents = [
        _store_generated_markdown(
            db,
            user_id,
            grant_id,
            grant.title,
            "business_proposal",
            "Business Proposal",
            business_proposal,
            {"bundle": "drafter"},
        ),
        _store_generated_markdown(
            db,
            user_id,
            grant_id,
            grant.title,
            "presentation_script",
            "Presentation Script",
            presentation_script,
            {"bundle": "drafter"},
        ),
        _store_generated_markdown(
            db,
            user_id,
            grant_id,
            grant.title,
            deck_document_type,
            deck_document_name,
            deck_markdown,
            {"bundle": "drafter"},
        ),
    ]

    return {
        "business_proposal_markdown": business_proposal,
        "presentation_script_markdown": presentation_script,
        "generated_deck": generated_deck,
        "deck_critique": deck_critique,
        "generated_documents": generated_documents,
    }


@router.post("/{grant_id}/application/{user_id}/pitch-deck/generate", response_model=StoredPitchDeckRead)
async def generate_and_store_application_pitch_deck(
    grant_id: int,
    user_id: int,
    payload: PitchDeckGenerateRequest,
    db: Session = Depends(get_db),
):
    if get_user_by_id(db, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    grant = get_grant_by_id(db, grant_id)
    if grant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found.")
    profile = get_company_profile(db, user_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company profile not found.")

    profile_context = _profile_deck_context(profile)
    grant_context = {**_grant_deck_context(grant), **payload.extra_context}
    filename = payload.filename or f"{_slug(profile.company_name)}_{_slug(grant.title)}_pitch_deck.pptx"

    if payload.creative:
        content, layout_plan = await build_creative_pitch_deck_pptx(
            profile_context,
            grant_context,
            api_key=settings.zai_api_key,
        )
        generation_mode = "zai_creative"
    else:
        slides = build_pitch_deck_slides(profile_context, grant_context)
        content = build_pitch_deck_pptx(profile_context, grant_context)
        layout_plan = {"slides": slides}
        generation_mode = "deterministic"

    document = _store_generated_pptx(
        db=db,
        user_id=user_id,
        grant_id=grant_id,
        filename=filename,
        content=content,
        layout_plan=layout_plan,
        generation_mode=generation_mode,
    )
    return {
        "document": _generated_file_summary(document),
        "download_url": f"/grants/{grant_id}/application/{user_id}/documents/{document.id}/download",
        "message": "Pitch deck generated by Drafter Agent and stored in the user document database.",
        "layout_plan": layout_plan,
    }


@router.get("/{grant_id}/application/{user_id}/pitch-deck.pptx")
def download_application_pitch_deck(
    grant_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):
    grant = get_grant_by_id(db, grant_id)
    if grant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found.")
    profile = get_company_profile(db, user_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company profile not found.")
    document = _stored_pptx_document(db, user_id, grant_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No stored pitch deck found. Call POST /grants/{grant_id}/application/{user_id}/pitch-deck/generate first.",
        )
    content = _pptx_bytes_from_document(document)
    if content is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Stored pitch deck is missing binary content.")
    return _pptx_response(content, document.file_name)


@router.get("/{grant_id}/application/{user_id}/documents/{document_id}/download")
def download_application_document(
    grant_id: int,
    user_id: int,
    document_id: int,
    db: Session = Depends(get_db),
):
    if get_grant_by_id(db, grant_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found.")
    document = (
        db.query(CompanyDocument)
        .filter(CompanyDocument.id == document_id)
        .filter(CompanyDocument.user_id == user_id)
        .first()
    )
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    generated_pptx = _pptx_bytes_from_document(document)
    if generated_pptx:
        return _pptx_response(generated_pptx, document.file_name)

    generated_content = document.metadata_json.get("content_markdown")
    if generated_content:
        buffer = io.BytesIO(generated_content.encode("utf-8"))
        return StreamingResponse(
            buffer,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{document.file_name}"'},
        )

    return {
        "document_id": document.id,
        "document_type": document.document_type,
        "file_name": document.file_name,
        "file_url": document.file_url,
        "status": document.status,
        "message": "Uploaded hard documents are referenced from the document vault.",
    }


@router.get("/{grant_id}/application/{user_id}/package")
def download_submission_package(grant_id: int, user_id: int, db: Session = Depends(get_db)):
    snapshot = build_grant_application_snapshot(db, user_id, grant_id)
    if snapshot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found.")
    profile = get_company_profile(db, user_id)
    documents = get_company_documents(db, user_id)
    grant = snapshot["grant"]
    requirement_types = {
        item["document_type"]
        for item in snapshot["checklist"]
        if item["document_type"]
    }
    package_documents = [
        document
        for document in documents
        if document.document_type in requirement_types
        or document.metadata_json.get("grant_id") == grant_id
    ]

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "application_manifest.json",
            json.dumps(
                {
                    "grant_id": grant.id,
                    "grant_title": grant.title,
                    "provider_name": grant.provider_name,
                    "user_id": user_id,
                    "company_name": profile.company_name if profile else None,
                    "readiness_score": snapshot["readiness_score"],
                    "readiness_level": snapshot["readiness_level"],
                    "track": snapshot["track"],
                    "missing_required_documents": snapshot["missing_required_documents"],
                    "checklist": snapshot["checklist"],
                },
                ensure_ascii=True,
                indent=2,
                default=str,
            ),
        )

        if profile:
            archive.writestr(
                "company_profile.md",
                (
                    f"# {profile.company_name}\n\n"
                    f"- Industry: {profile.industry or 'not specified'}\n"
                    f"- Nationality: {profile.nationality or 'not specified'}\n"
                    f"- Employees: {profile.employee_count or 'not specified'}\n"
                    f"- Target grant amount: RM {profile.target_grant_amount or 'not specified'}\n\n"
                    f"{profile.summary or ''}\n"
                ),
            )
        uploaded_manifest = []
        for document in package_documents:
            generated_pptx = _pptx_bytes_from_document(document)
            if generated_pptx:
                archive.writestr(f"generated/{document.file_name}", generated_pptx)
                continue
            generated_content = document.metadata_json.get("content_markdown")
            if generated_content:
                archive.writestr(f"generated/{document.file_name}", generated_content)
            else:
                uploaded_manifest.append(
                    {
                        "document_id": document.id,
                        "document_type": document.document_type,
                        "file_name": document.file_name,
                        "file_url": document.file_url,
                        "status": document.status,
                    }
                )
        archive.writestr("uploaded_documents_manifest.json", json.dumps(uploaded_manifest, ensure_ascii=True, indent=2))

    buffer.seek(0)
    filename = f"{_slug(grant.title)}_submission_package.zip"
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
