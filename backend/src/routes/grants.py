from __future__ import annotations

import asyncio
import base64
import io
import json
import re
import textwrap
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.ai_sandbox.coach import run_coach
from backend.ai_sandbox.pitch_deck_evaluator import run_pitch_deck_evaluator
from backend.ai_sandbox.scout.runner import run_scout
from backend.ai_sandbox.scout.sources import (
    check_sources_health_from_sources,
    load_sources_from_curated_outputs,
    load_sources_from_file,
)
from backend.ai_sandbox.scout.storage import read_last_report
from backend.ai_sandbox.pptx_drafter import (
    PPTX_MIME,
    build_creative_pitch_deck_pptx,
    build_pitch_deck_pptx,
    build_pitch_deck_pptx_from_slides,
    build_pitch_deck_slides,
)
from backend.ai_sandbox.drafter import run_drafter
from backend.ai_sandbox.schemas import EvaluatorOutput as AgentEvaluatorOutput
from backend.ai_sandbox.schemas import EvidenceTrace as AgentEvidenceTrace
from backend.ai_sandbox.schemas import GrantRequirement as AgentGrantRequirement
from backend.ai_sandbox.schemas import SMEProfile as AgentSMEProfile
from backend.src.api.schemas import (
    ApplicationRoadmapRead,
    DraftApplicationRequest,
    DocumentRead,
    DrafterOutputRead,
    GeneratedDocumentRead,
    GenerateDocumentRequest,
    GrantApplicationRead,
    GrantCreate,
    GrantRead,
    PitchDeckEvaluationRead,
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
    is_inline_review_document,
    list_grants,
    rank_grants_for_user,
    upsert_company_document,
)
from backend.src.database.models import CompanyDocument, RequirementSource, SessionLocal


router = APIRouter(prefix="/grants", tags=["grants"])

PDF_MIME = "application/pdf"
TEXT_MIME = "text/plain"

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

        try:
            report = run_scout(
                db,
                source_file=source_file,
                sources_override=None,
                curated_files=_curated_source_files() if run_mode == "curated" else None,
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
        except Exception as scout_exc:  # noqa: BLE001
            db.rollback()
            SCOUT_STATE.update(
                {
                    "status": "error",
                    "finished_at": _utc_now_iso(),
                    "message": f"Scout run failed: {str(scout_exc)[:500]}",
                }
            )
            raise
    except Exception as exc:  # noqa: BLE001
        SCOUT_STATE.update(
            {
                "status": "error",
                "finished_at": _utc_now_iso(),
                "message": f"Scout background task error: {str(exc)[:500]}",
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
        "source_url": grant.source_url,
        "description": grant.description,
        "amount_min": grant.amount_min,
        "amount_max": grant.amount_max,
        "industry": grant.industry,
        "nationality": grant.nationality,
        "eligibility_notes": grant.eligibility_notes,
        "application_deadline": grant.application_deadline,
        "mandatory_documents": [requirement.name for requirement in grant.requirements if requirement.is_required],
        "requirements": [
            {
                "name": requirement.name,
                "description": requirement.description,
                "document_type": requirement.document_type,
                "source_type": requirement.source_type.value,
            }
            for requirement in grant.requirements
        ],
    }


def _int_value(value: Any, default: int = 0) -> int:
    try:
        if value in (None, "", [], {}):
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _money_rm(value: Any, fallback: str = "to be confirmed") -> str:
    try:
        if value in (None, "", [], {}):
            return fallback
        return f"RM {float(value):,.0f}"
    except (TypeError, ValueError):
        return fallback


_MISSING_PROPOSAL_VALUES = {
    "",
    "0",
    "0.0",
    "none",
    "null",
    "n/a",
    "na",
    "not specified",
    "to be confirmed",
    "tbc",
    "unknown",
    "undefined",
}


def _proposal_value(value: Any, fallback: str) -> str:
    if value in (None, [], {}):
        return fallback
    cleaned = str(value).strip()
    if cleaned.lower() in _MISSING_PROPOSAL_VALUES:
        return fallback
    return cleaned


def _proposal_summary(profile: Any, extracted: dict[str, Any]) -> str:
    summary = _proposal_value(profile.summary or extracted.get("summary"), "")
    # Avoid dumping short, comma-separated database fragments such as
    # "RM50000, enhance quality" into the final PDF.
    if len(summary.split()) >= 10 and not re.fullmatch(r"[\w\s,.$%-]+", summary):
        return summary
    if len(summary.split()) >= 14:
        return summary
    return (
        "The company is positioning this grant-funded project as a disciplined "
        "capability-building initiative that strengthens delivery quality, "
        "commercial readiness, and evidence-based execution."
    )


def _safe_upload_filename(filename: str | None) -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|]+", "_", (filename or "uploaded_document").strip())
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    return cleaned[:180] or "uploaded_document"


def _agent_sme_profile(profile: Any, documents: list[CompanyDocument]) -> AgentSMEProfile:
    extracted = profile.extracted_data or {}
    ownership = str(extracted.get("ownership_majority") or profile.nationality or "Local")
    ownership_majority = "Foreign" if ownership.lower() == "foreign" else "Local"
    return AgentSMEProfile(
        company_name=profile.company_name or "Unknown Company",
        ssm_number=str(extracted.get("ssm_number") or "Unknown"),
        age_in_months=_int_value(extracted.get("age_in_months")),
        full_time_employees=_int_value(profile.employee_count or extracted.get("full_time_employees")),
        ownership_majority=ownership_majority,
        sector=str(profile.industry or extracted.get("sector") or "General"),
        total_project_cost_rm=_int_value(extracted.get("total_project_cost_rm") or profile.target_grant_amount),
        requested_funding_rm=_int_value(profile.target_grant_amount or extracted.get("requested_funding_rm")),
        outsourced_cost_rm=_int_value(extracted.get("outsourced_cost_rm")),
        has_end_user_partner=bool(extracted.get("has_end_user_partner")),
        documents_provided=[document.file_name for document in documents],
        uploaded_pitch_deck_text=extracted.get("uploaded_pitch_deck_text"),
    )


def _agent_grant_requirement(grant: Any) -> AgentGrantRequirement:
    mandatory_documents = [requirement.name for requirement in grant.requirements if requirement.is_required]
    return AgentGrantRequirement(
        grant_name=grant.title,
        promoted_sectors=[grant.industry or "General"],
        max_funding_rm=_int_value(grant.amount_max, 1000000),
        funding_tier_local_percent=50,
        funding_tier_foreign_percent=30,
        max_outsourcing_percent=20,
        requires_end_user_partner=any(
            "partner" in (requirement.document_type or "").lower()
            or "partner" in requirement.name.lower()
            for requirement in grant.requirements
        ),
        mandatory_documents=mandatory_documents,
        application_roadmap=[],
    )


def _roadmap_status_for_item(item: dict[str, Any]) -> str:
    if item["fulfilled"]:
        return "complete"
    if item["can_generate"]:
        return "ready_to_generate"
    if item["can_upload"]:
        return "needs_upload"
    return "pending"


def _coach_evaluator_output_from_snapshot(snapshot: dict[str, Any]) -> AgentEvaluatorOutput:
    traces = []
    for item in snapshot["checklist"]:
        if not item["is_required"]:
            continue
        status = "MET" if item["fulfilled"] else "UNMET"
        source = item.get("fulfillment_source") or item.get("document_type") or "Application Checklist"
        if not item["fulfilled"] and item["can_generate"]:
            source = "Drafter Agent"
        traces.append(
            AgentEvidenceTrace(
                requirement=item["name"],
                status=status,
                source_document=source,
                reasoning=item.get("description") or item.get("action_label") or "Requirement is pending.",
            )
        )
    return AgentEvaluatorOutput(
        evidence_traces=traces,
        readiness_score=int(round(float(snapshot.get("readiness_score") or 0))),
    )


def _coach_step_lookup(coach: dict[str, Any] | None) -> dict[str, dict[str, str]]:
    if not coach:
        return {}
    lookup = {}
    for step in coach.get("next_steps", []):
        key = _slug(str(step.get("document_name") or ""))
        if key:
            lookup[key] = step
    return lookup


def _build_application_roadmap(
    snapshot: dict[str, Any],
    coach: dict[str, Any] | None,
    generated_by: str,
) -> dict[str, Any]:
    grant = snapshot["grant"]
    checklist = snapshot["checklist"]
    coach_steps = _coach_step_lookup(coach)
    steps: list[dict[str, Any]] = [
        {
            "step_number": 1,
            "title": "Confirm grant fit and deadline",
            "status": "complete" if snapshot["readiness_score"] > 0 else "pending",
            "owner": "Founder",
            "description": f"Review {grant.title} by {grant.provider_name}, funding range, eligibility notes, and deadline before preparing documents.",
            "action": "Open the source page, confirm the company is eligible, and keep the deadline in the application calendar.",
            "requirement_id": None,
            "document_type": None,
            "download_url": None,
        }
    ]

    for item in checklist:
        if not item["is_required"]:
            continue
        coach_step = coach_steps.get(_slug(item["name"]))
        if item["fulfilled"]:
            description = f"{item['name']} is already covered by {item.get('fulfillment_source') or 'a stored document'}."
            action = "No immediate action needed. Keep this evidence in the submission package."
        elif item["can_generate"]:
            description = coach_step.get("explanation") if coach_step else f"{item['name']} can be generated by Grantly for this application."
            action = coach_step.get("action_required") if coach_step else "Click Generate or Run Drafter Agent, then review the generated output before submission."
        else:
            description = coach_step.get("explanation") if coach_step else (item.get("description") or f"{item['name']} is required before submission.")
            action = coach_step.get("action_required") if coach_step else "Upload the required file from this checklist row so it can be linked to the grant package."
        steps.append(
            {
                "step_number": len(steps) + 1,
                "title": item["name"],
                "status": _roadmap_status_for_item(item),
                "owner": "Grantly AI" if item["can_generate"] and not item["fulfilled"] else "Founder",
                "description": description,
                "action": action,
                "requirement_id": item["requirement_id"],
                "document_type": item.get("document_type"),
                "download_url": item.get("download_url"),
            }
        )

    generated_types = {document.document_type for document in snapshot.get("generated_documents", [])}
    has_proposal = "business_proposal" in generated_types
    has_deck = "pitch_deck" in generated_types
    steps.append(
        {
            "step_number": len(steps) + 1,
            "title": "Generate proposal, pitch deck, and script",
            "status": "complete" if has_proposal and has_deck else "ready_to_generate",
            "owner": "Grantly AI",
            "description": "The Drafter Agent prepares the professional proposal PDF, downloadable PPTX deck, and companion speaking script for the application.",
            "action": "Run Drafter Agent, then review each output for factual accuracy and consistency with the company profile.",
            "requirement_id": None,
            "document_type": "drafter_bundle",
            "download_url": None,
        }
    )
    missing_count = len(snapshot.get("missing_required_documents", []))
    steps.append(
        {
            "step_number": len(steps) + 1,
            "title": "Review and package submission files",
            "status": "ready" if missing_count == 0 else "blocked",
            "owner": "Founder",
            "description": "The submission package combines profile evidence, uploaded hard documents, and generated soft documents into one reviewable archive.",
            "action": "Download the package, check file names and dates, and confirm every required item is present before submission.",
            "requirement_id": None,
            "document_type": "submission_package",
            "download_url": snapshot.get("download_package_url"),
        }
    )
    steps.append(
        {
            "step_number": len(steps) + 1,
            "title": f"Submit to {grant.provider_name}",
            "status": "pending" if missing_count == 0 else "blocked",
            "owner": "Founder",
            "description": "Submit through the official grant portal or agency channel, then keep acknowledgement receipts for audit and follow-up.",
            "action": "Use the official source URL or agency instructions, submit before the deadline, and record the submission reference number.",
            "requirement_id": None,
            "document_type": None,
            "download_url": None,
        }
    )

    message = (
        coach.get("encouraging_message")
        if coach
        else "This application is a practical pipeline: close the missing evidence, generate the soft documents, review the package, then submit through the official channel."
    )
    return {
        "grant_id": grant.id,
        "grant_title": grant.title,
        "provider_name": grant.provider_name,
        "generated_by": generated_by,
        "encouraging_message": message,
        "steps": steps,
    }


def _pptx_response(content: bytes, filename: str) -> StreamingResponse:
    return _bytes_response(content, PPTX_MIME, filename)


def _bytes_response(content: bytes, content_type: str, filename: str) -> StreamingResponse:
    return StreamingResponse(
        io.BytesIO(content),
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _plain_text_from_markdown(content: str) -> str:
    lines: list[str] = []
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if line.startswith("#"):
            line = line.lstrip("#").strip().upper()
        elif line.startswith("- "):
            line = f"* {line[2:].strip()}"
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def _pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


# Map common unicode glyphs that Helvetica + WinAnsiEncoding can render
# (or that we want to flatten to ASCII for safety in PDF text streams).
_PDF_UNICODE_REPLACEMENTS = {
    "\u2022": chr(0x95),  # bullet •  -> WinAnsi 0x95
    "\u2013": "-",        # en dash
    "\u2014": "--",       # em dash
    "\u2018": "'",        # left single quote
    "\u2019": "'",        # right single quote
    "\u201c": '"',        # left double quote
    "\u201d": '"',        # right double quote
    "\u2026": "...",      # ellipsis
    "\u00a0": " ",        # non-breaking space
}


def _pdf_safe_text(value: str) -> str:
    for src, dst in _PDF_UNICODE_REPLACEMENTS.items():
        value = value.replace(src, dst)
    return value


# Per-block typography (in PDF points). char_width is an approximate average
# glyph width as a fraction of font size, used purely to estimate wrap width.
_PDF_BLOCK_STYLES: dict[str, dict[str, Any]] = {
    "h1":     {"font": "F2", "size": 20, "leading": 26, "space_before": 14, "space_after": 12, "indent": 0,  "char_width": 0.58},
    "h2":     {"font": "F2", "size": 14, "leading": 20, "space_before": 14, "space_after": 6,  "indent": 0,  "char_width": 0.58},
    "h3":     {"font": "F2", "size": 12, "leading": 17, "space_before": 10, "space_after": 4,  "indent": 0,  "char_width": 0.58},
    "p":      {"font": "F1", "size": 11, "leading": 15, "space_before": 0,  "space_after": 6,  "indent": 0,  "char_width": 0.53},
    "bullet": {"font": "F1", "size": 11, "leading": 15, "space_before": 0,  "space_after": 4,  "indent": 16, "char_width": 0.53},
    "spacer": {"font": "F1", "size": 11, "leading": 8,  "space_before": 0,  "space_after": 0,  "indent": 0,  "char_width": 0.53},
}


def _markdown_blocks(content: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            blocks.append({"type": "spacer"})
            continue
        if stripped.startswith("### "):
            blocks.append({"type": "h3", "text": stripped[4:].strip()})
        elif stripped.startswith("## "):
            blocks.append({"type": "h2", "text": stripped[3:].strip()})
        elif stripped.startswith("# "):
            blocks.append({"type": "h1", "text": stripped[2:].strip()})
        elif stripped.startswith(("- ", "* ")):
            blocks.append({"type": "bullet", "text": stripped[2:].strip()})
        else:
            blocks.append({"type": "p", "text": stripped})
    return blocks


def _wrap_to_width(text: str, max_width_pt: float, char_width_pt: float) -> list[str]:
    if max_width_pt <= 0 or char_width_pt <= 0:
        return [text]
    chars = max(20, int(max_width_pt / char_width_pt))
    return textwrap.wrap(text, width=chars, break_long_words=False, replace_whitespace=False) or [""]


def _pdf_bytes_from_text(title: str, content: str) -> bytes:
    page_width = 595
    page_height = 842
    left_margin = 60
    right_margin = 60
    top_margin = 60
    bottom_margin = 60
    text_width = page_width - left_margin - right_margin

    has_inline_title = bool(content.lstrip().startswith("#"))
    blocks: list[dict[str, Any]] = []
    if not has_inline_title and title:
        blocks.append({"type": "h1", "text": title})
        blocks.append({"type": "spacer"})
    blocks.extend(_markdown_blocks(content))

    pages: list[list[tuple[float, float, str, int, str]]] = [[]]
    y = page_height - top_margin

    def ensure_space(needed: float) -> None:
        nonlocal y
        if y - needed < bottom_margin:
            pages.append([])
            y = page_height - top_margin

    for block in blocks:
        block_type = block["type"]
        style = _PDF_BLOCK_STYLES.get(block_type, _PDF_BLOCK_STYLES["p"])

        if block_type == "spacer":
            y -= style["leading"]
            if y < bottom_margin:
                pages.append([])
                y = page_height - top_margin
            continue

        if block.get("text") is None:
            continue

        text = _pdf_safe_text(block["text"])
        char_pt_width = style["char_width"] * style["size"]

        if block_type == "bullet":
            bullet_indent = style["indent"]
            text_indent = bullet_indent + 14
            wrapped = _wrap_to_width(text, text_width - text_indent, char_pt_width)
            y -= style["space_before"]
            for idx, line in enumerate(wrapped):
                ensure_space(style["leading"])
                if idx == 0:
                    pages[-1].append((left_margin + bullet_indent, y, style["font"], style["size"], chr(0x95)))
                pages[-1].append((left_margin + text_indent, y, style["font"], style["size"], line))
                y -= style["leading"]
            y -= style["space_after"]
        else:
            wrapped = _wrap_to_width(text, text_width - style["indent"], char_pt_width)
            y -= style["space_before"]
            for line in wrapped:
                ensure_space(style["leading"])
                pages[-1].append((left_margin + style["indent"], y, style["font"], style["size"], line))
                y -= style["leading"]
            y -= style["space_after"]

    objects: dict[int, bytes] = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        3: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        4: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>",
    }
    kids: list[int] = []
    next_object_id = 5

    for page_runs in pages:
        commands: list[str] = []
        for x_pos, y_pos, font, size, line in page_runs:
            if not line:
                continue
            commands.append("BT")
            commands.append(f"/{font} {size} Tf")
            commands.append(f"1 0 0 1 {x_pos:.2f} {y_pos:.2f} Tm")
            commands.append(f"({_pdf_escape(line)}) Tj")
            commands.append("ET")
        stream = "\n".join(commands).encode("latin-1", "replace") if commands else b""
        content_id = next_object_id
        page_id = next_object_id + 1
        next_object_id += 2
        objects[content_id] = (
            b"<< /Length "
            + str(len(stream)).encode("ascii")
            + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        )
        objects[page_id] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_width} {page_height}] "
            f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {content_id} 0 R >>"
        ).encode("ascii")
        kids.append(page_id)

    kids_refs = " ".join(f"{page_id} 0 R" for page_id in kids)
    objects[2] = f"<< /Type /Pages /Kids [{kids_refs}] /Count {len(kids)} >>".encode("ascii")

    buffer = io.BytesIO()
    buffer.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for object_id in range(1, max(objects) + 1):
        offsets.append(buffer.tell())
        buffer.write(f"{object_id} 0 obj\n".encode("ascii"))
        buffer.write(objects[object_id])
        buffer.write(b"\nendobj\n")
    xref_at = buffer.tell()
    buffer.write(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    buffer.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        buffer.write(f"{offset:010d} 00000 n \n".encode("ascii"))
    buffer.write(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_at}\n%%EOF\n".encode("ascii")
    )
    return buffer.getvalue()


def _professional_business_proposal_markdown(
    grant: Any,
    profile: Any,
    extra_context: dict[str, Any] | None = None,
) -> str:
    extracted = profile.extracted_data or {}
    company_name = _proposal_value(profile.company_name, "Applicant Company")
    sector = _proposal_value(profile.industry or extracted.get("sector"), "the target sector")
    summary = _proposal_summary(profile, extracted)
    requested_amount = profile.target_grant_amount or extracted.get("requested_funding_rm")
    project_cost = extracted.get("total_project_cost_rm") or requested_amount
    employees = _proposal_value(profile.employee_count or extracted.get("full_time_employees"), "a focused internal delivery team")
    ownership = _proposal_value(profile.nationality or extracted.get("ownership_majority"), "a Malaysian SME profile")
    documents = ", ".join(requirement.name for requirement in grant.requirements if requirement.is_required) or "agency-required supporting documents"
    requested_amount_text = _money_rm(requested_amount, "a funding amount aligned with the eligible project scope")
    project_cost_text = _money_rm(project_cost, "a project cost aligned with the implementation plan")
    grant_cap = _money_rm(grant.amount_max, "the published grant funding parameters")
    deadline = _proposal_value(grant.application_deadline, "the published application window")
    provider = _proposal_value(grant.provider_name, "the grant agency")
    grant_title = _proposal_value(grant.title, "the selected grant programme")
    extra = ""
    if extra_context:
        extra = f"\n\nAdditional submission context: {json.dumps(extra_context, ensure_ascii=True)}"

    return f"""# Business Proposal: {company_name} for {grant_title}

## I. Executive Summary
{company_name} is a Malaysian SME operating in {sector}. The company is applying to {provider} under {grant_title} to co-fund a focused growth initiative with direct commercial, operational, and capability-building outcomes. The requested support is {requested_amount_text} against {project_cost_text}. The purpose of this proposal is not simply to secure subsidy support; it is to demonstrate that the applicant has a clear project thesis, a disciplined execution approach, and a credible pathway to convert grant funding into measurable business value.

The proposal positions the project as a strategic investment in capability and compliance. It is designed to improve execution quality, strengthen market readiness, and create a stronger evidence base for grant monitoring, claims, and post-award reporting. This makes the application practical for assessment and easier for the grant committee to evaluate against eligibility, impact, and implementation risk.

With the support of {grant_title}, {company_name} can accelerate a capability upgrade that would otherwise need to be implemented more slowly or at a reduced scope. The grant will strengthen the company's execution base, support responsible project delivery, and create a clearer path toward commercial resilience. This proposal is therefore positioned as a serious funding case: practical enough to execute, structured enough to audit, and commercially relevant enough to justify public-sector support.

## II. Company Description
{summary}

The company profile records {employees}, an ownership or nationality position of {ownership}, and an operating focus in {sector}. These details support the applicant's eligibility narrative and provide the foundation for grant screening. The attached company documents should be used to verify registration, financial standing, governance accountability, and the organisation's ability to manage public funding responsibly.

From an execution standpoint, the applicant is presented as an operating SME with a defined commercial direction rather than an early concept without implementation capacity. The proposal therefore frames the business as fundable, operationally mature, and ready to use the grant as a catalyst for structured growth.

The business operates in an environment where SMEs are expected to become more digital, more productive, and more evidence-driven. This creates pressure on management teams to improve service quality, implementation speed, customer confidence, and reporting discipline at the same time. {company_name}'s application should therefore be viewed as part of a broader capability-building journey rather than a one-off funding request.

## III. Products & Services
The company's product or service direction is anchored in {sector}, with the proposed project intended to improve quality, execution capacity, and market-facing readiness. The grant-funded initiative should strengthen the company's ability to refine its offering, deliver more consistently, and present a clearer value proposition to customers, partners, and grant evaluators.

The applicant will deploy the funding into a focused implementation plan covering product or service enhancement, operational readiness, validation activity, and go-to-market preparation. The solution is framed as an innovative and sustainable intervention: it strengthens the company's ability to deliver, reduces execution friction, and creates a more credible platform for growth.

The project will be managed through clear internal ownership, milestone-based delivery, and evidence collection for each major work package. Where vendors or outsourced support are required, the company should apply procurement discipline, scope control, and documented acceptance criteria. This approach gives the grant committee confidence that the funds will be deployed with governance rather than treated as general working capital.

The commercial case is strongest when the product or service is positioned not merely as an internal improvement, but as a higher-quality market offering. The project should therefore emphasise better customer outcomes, more reliable delivery, stronger documentation, and the company's ability to translate funded capability into measurable business value.

## IV. Marketing Plan
### Target Market Research
The target market should be defined around customers, partners, or users who experience a clear operational or commercial pain point that the company is positioned to solve. For {company_name}, the priority should be to identify customer segments within {sector} that have the highest urgency, shortest adoption cycle, and strongest willingness to pay or participate. Market research should combine desk research, customer discovery, competitor benchmarking, and validation conversations with potential users or channel partners.

The company should evaluate market attractiveness using practical criteria: customer pain severity, budget availability, decision-maker accessibility, procurement complexity, and the potential for repeatable delivery. This avoids an overly broad market claim and helps the proposal demonstrate a credible path from grant-funded capability to commercial traction.

### Competitor Data Collection Plan
The competitor data collection plan should be systematic and evidence-based. The company should maintain a competitor register covering direct competitors, substitute solutions, pricing signals, service scope, customer segments, delivery channels, and visible differentiators. Sources may include competitor websites, public case studies, marketplace listings, customer interviews, social media activity, tender references, and industry directories.

The purpose of this exercise is not to copy competitors, but to identify where {company_name} can compete more intelligently. The analysis should highlight gaps in service quality, speed, localisation, compliance readiness, affordability, or customer support. These insights can then inform product packaging, pricing, customer messaging, and grant-funded implementation priorities.

### SWOT Analysis
- Strengths: The company has an operating SME profile, a defined sector focus, and a funding request that can be linked to capability-building outcomes.
- Weaknesses: As with many SMEs, the business may need stronger documentation, clearer performance metrics, and more formalised evidence of delivery impact.
- Opportunities: Grant support can accelerate market readiness, strengthen delivery processes, improve customer-facing materials, and support measurable commercial outcomes.
- Threats: Competitive pressure, supplier delays, documentation gaps, and slower customer adoption could reduce project impact if not actively managed.

The marketing strategy should translate this SWOT analysis into action. The company should prioritise a focused customer segment, communicate a clear value proposition, collect evidence from early delivery, and use grant-funded outputs to improve market credibility. This creates a stronger commercial narrative for both customers and grant reviewers.

## V. Operational Plan
The operational plan should convert the proposal into a controlled delivery programme. The company should define project owners, work packages, milestones, required documents, supplier responsibilities, internal approval points, and evidence required for grant reporting. This structure helps ensure that the project remains manageable and auditable from approval through implementation.

Implementation should be managed in stages. The first stage should confirm scope, success criteria, procurement requirements, and internal responsibilities. The second stage should execute the core delivery activities and collect evidence of progress. The final stage should validate outcomes, reconcile expenditure, and prepare reporting materials for management and the grant agency.

Operational controls are essential. The company should maintain a simple governance file containing quotations, invoices, milestone approvals, acceptance evidence, meeting notes, and implementation outputs. This protects the project from cost drift, weak documentation, and unclear ownership. It also makes the proposal more credible because it shows that {company_name} understands the administrative discipline required when public funding is involved.

## VI. Management & Organization
The management and organisation section should present {company_name} as capable of executing the project responsibly. The company profile indicates {employees}, which should be framed as the internal base for coordination, delivery, and accountability. The ownership or nationality position of {ownership} further supports the applicant's eligibility narrative and should be verified through the appropriate supporting documents.

For grant execution, the company should appoint a project lead, a finance or compliance owner, and operational contributors responsible for delivery milestones. The project lead should manage timelines and stakeholder coordination. The finance or compliance owner should track spending, retain documentation, and support claims or reporting. Operational contributors should execute the funded work packages and provide evidence of completion.

This governance model is intentionally practical. It does not require excessive bureaucracy, but it creates clear accountability. Grant evaluators typically want confidence that the applicant can manage funds, deliver outputs, and document outcomes. A simple but disciplined management structure helps address those concerns.

## VII. Startup Expenses & Capitalization
The grant is provided by {provider}, with a funding ceiling of {grant_cap}. The company's requested support is {requested_amount_text}, and the total project cost is {project_cost_text}. These figures should be presented as part of a disciplined funding plan rather than a general cash request. Required checklist items for this application include: {documents}. The application should be submitted by {deadline}, subject to portal availability and agency confirmation.

The use of funds should be treated as a strategic investment in capability and compliance. The budget should prioritise work packages that directly improve the applicant's ability to deliver, validate, and commercialise the project.

- Project execution and technical delivery: build, configure, test, and deploy the funded work packages.
- Validation and compliance evidence: prepare measurable proof that the project is delivered responsibly.
- Commercial readiness: improve materials, pilots, demonstrations, or customer-facing readiness needed for adoption.
- Reporting and governance: maintain documentation for claims, procurement records, milestone evidence, and post-award reporting.
- Capability transfer: ensure the company retains knowledge, operating discipline, and reusable processes after the funded work is complete.

Capitalisation should be framed around responsible leverage. Grant funding reduces the burden on internal cash flow while allowing the company to execute a more complete, higher-quality project. The applicant should still demonstrate responsible ownership of the project through internal coordination, management time, documentation discipline, and readiness to comply with grant conditions.

## VIII. Conclusion
{company_name} respectfully requests consideration for {grant_title}. The requested funding will help convert a defined business need into a controlled implementation project with measurable outcomes, stronger SME capability, and clearer evidence for agency review.

The application should be viewed as a practical, fundable proposal: it connects a real operating need to a structured use of funds, defines an implementation path, and recognises the importance of governance. With grant support, the company can accelerate a capability upgrade that strengthens both commercial resilience and long-term competitiveness.{extra}
"""


def _ensure_professional_business_proposal(
    content: str | None,
    grant: Any,
    profile: Any,
    extra_context: dict[str, Any] | None = None,
) -> str:
    if content and len(_plain_text_from_markdown(content)) >= 1400 and content.count("##") >= 4:
        return content.strip() + "\n"

    baseline = _professional_business_proposal_markdown(grant, profile, extra_context)
    if content and content.strip():
        return baseline + "\n\n## 10. Drafter Agent Narrative\n" + content.strip() + "\n"
    return baseline


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
        profile_context = _profile_deck_context(profile)
        grant_context = {**_grant_deck_context(grant), **extra_context}
        slides = build_pitch_deck_slides(profile_context, grant_context)
        return _deck_markdown_from_slides(slides)

    if document_type in {"business_proposal", "proposal"}:
        return _professional_business_proposal_markdown(grant, profile, extra_context)

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


def _store_generated_text(
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
        "content_type": TEXT_MIME,
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
            "file_name": f"{_slug(grant_title)}_{_slug(document_name)}.txt",
            "file_url": None,
            "status": "generated",
            "metadata": metadata,
        },
    )


def _store_generated_binary(
    db: Session,
    user_id: int,
    grant_id: int,
    document_type: str,
    filename: str,
    content: bytes,
    content_type: str,
    extra_metadata: dict[str, Any] | None = None,
) -> CompanyDocument:
    metadata = {
        "source": "drafter_agent",
        "grant_id": grant_id,
        "content_type": content_type,
        "content_base64": base64.b64encode(content).decode("ascii"),
        "generated_at": _utc_now_iso(),
    }
    if extra_metadata:
        metadata.update(extra_metadata)
    return upsert_company_document(
        db,
        user_id,
        {
            "document_type": document_type,
            "file_name": filename,
            "file_url": None,
            "status": "generated",
            "metadata": metadata,
        },
    )


def _store_generated_pdf(
    db: Session,
    user_id: int,
    grant_id: int,
    grant_title: str,
    document_type: str,
    document_name: str,
    markdown_content: str,
    extra_metadata: dict[str, Any] | None = None,
) -> CompanyDocument:
    filename = f"{_slug(grant_title)}_{_slug(document_name)}.pdf"
    metadata = {"content_markdown": markdown_content}
    if extra_metadata:
        metadata.update(extra_metadata)
    return _store_generated_binary(
        db=db,
        user_id=user_id,
        grant_id=grant_id,
        document_type=document_type,
        filename=filename,
        content=_pdf_bytes_from_text(document_name, markdown_content),
        content_type=PDF_MIME,
        extra_metadata=metadata,
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
    return _store_generated_binary(
        db=db,
        user_id=user_id,
        grant_id=grant_id,
        document_type="pitch_deck",
        filename=filename,
        content=content,
        content_type=PPTX_MIME,
        extra_metadata={"layout_plan": layout_plan, "generation_mode": generation_mode},
    )


def _extract_pptx_text(content: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as deck:
            slide_names = sorted(
                (name for name in deck.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", name)),
                key=lambda value: int(re.search(r"slide(\d+)\.xml$", value).group(1)),
            )
            notes_names = sorted(
                (name for name in deck.namelist() if re.match(r"ppt/notesSlides/notesSlide\d+\.xml$", name)),
                key=lambda value: int(re.search(r"notesSlide(\d+)\.xml$", value).group(1)),
            )
            chunks: list[str] = []
            for index, name in enumerate(slide_names, start=1):
                slide_text = _text_from_office_xml(deck.read(name))
                if slide_text:
                    chunks.append(f"Slide {index}: {slide_text}")
            for index, name in enumerate(notes_names, start=1):
                notes_text = _text_from_office_xml(deck.read(name))
                if notes_text:
                    chunks.append(f"Speaker notes {index}: {notes_text}")
            return "\n".join(chunks)
    except Exception:  # noqa: BLE001
        return ""


def _text_from_office_xml(payload: bytes) -> str:
    try:
        root = ElementTree.fromstring(payload)
    except ElementTree.ParseError:
        return ""
    values = [
        node.text.strip()
        for node in root.iter()
        if node.tag.endswith("}t") and node.text and node.text.strip()
    ]
    return " ".join(values)


def _extract_pdf_text(content: bytes) -> str:
    text_chunks = []
    for match in re.findall(rb"\(([^()]{3,240})\)\s*T[Jj]", content):
        decoded = match.decode("latin-1", errors="ignore").strip()
        if decoded:
            text_chunks.append(decoded)
    if text_chunks:
        return " ".join(text_chunks)
    decoded = content.decode("latin-1", errors="ignore")
    readable = re.findall(r"[A-Za-z0-9][A-Za-z0-9 ,.:%()/+\-]{8,}", decoded)
    return " ".join(readable[:120])


def _text_from_uploaded_pitch_deck(document: CompanyDocument) -> str:
    metadata = document.metadata_json or {}
    for key in ("extracted_text", "content_markdown", "preview_text", "text"):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()[:24000]

    content_base64 = metadata.get("content_base64")
    if not isinstance(content_base64, str) or not content_base64:
        return _deck_metadata_text(document)

    try:
        content = base64.b64decode(content_base64)
    except Exception:  # noqa: BLE001
        return _deck_metadata_text(document)

    content_type = str(metadata.get("content_type") or "").lower()
    file_name = document.file_name.lower()
    if file_name.endswith(".pptx") or content_type == PPTX_MIME:
        extracted = _extract_pptx_text(content)
    elif file_name.endswith(".pdf") or content_type == PDF_MIME:
        extracted = _extract_pdf_text(content)
    elif content_type.startswith("text/") or file_name.endswith((".txt", ".md", ".csv", ".json")):
        extracted = content.decode("utf-8", errors="replace")
    else:
        extracted = content.decode("utf-8", errors="ignore")

    extracted = re.sub(r"\s+", " ", extracted).strip()
    return extracted[:24000] if len(extracted) >= 40 else _deck_metadata_text(document)


def _deck_metadata_text(document: CompanyDocument) -> str:
    metadata = document.metadata_json or {}
    return (
        f"Pitch deck upload: {document.file_name}\n"
        f"Document status: {document.status}\n"
        f"Content type: {metadata.get('content_type') or 'unknown'}\n"
        f"File size: {metadata.get('size_bytes') or 'unknown'} bytes\n"
        "Full slide text could not be extracted automatically. Review should focus on the file metadata and request a readable PPTX, TXT, or PDF export if needed."
    )


def _uploaded_pitch_deck_document(db: Session, user_id: int, grant_id: int, document_id: int | None = None) -> CompanyDocument | None:
    query = (
        db.query(CompanyDocument)
        .filter(CompanyDocument.user_id == user_id)
        .filter(CompanyDocument.document_type == "pitch_deck")
    )
    if document_id is not None:
        return query.filter(CompanyDocument.id == document_id).first()

    candidates = query.order_by(CompanyDocument.created_at.desc()).all()
    uploaded = [document for document in candidates if document.status != "generated"]
    grant_specific = [
        document
        for document in uploaded
        if (document.metadata_json or {}).get("grant_id") == grant_id
    ]
    return (grant_specific or uploaded or [None])[0]


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


def _binary_bytes_from_document(document: CompanyDocument) -> tuple[bytes, str] | None:
    content_base64 = document.metadata_json.get("content_base64")
    if not content_base64:
        return None
    content_type = document.metadata_json.get("content_type") or "application/octet-stream"
    return base64.b64decode(content_base64), content_type


def _pptx_bytes_from_document(document: CompanyDocument) -> bytes | None:
    binary = _binary_bytes_from_document(document)
    if not binary:
        return None
    content, content_type = binary
    if content_type != PPTX_MIME and not document.file_name.lower().endswith(".pptx"):
        return None
    return content


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


def _slide_bullets(slide: dict[str, Any]) -> list[str]:
    raw = slide.get("bullet_points") or slide.get("bullets") or []
    return [str(item).strip() for item in raw if str(item).strip()]


def _slide_metrics(slide: dict[str, Any]) -> list[dict[str, str]]:
    metrics = []
    for raw_metric in slide.get("metrics") or []:
        if not isinstance(raw_metric, dict):
            continue
        label = str(raw_metric.get("label") or "Metric").strip()
        value = str(raw_metric.get("value") or "").strip()
        if label or value:
            metrics.append({"label": label or "Metric", "value": value})
    return metrics


def _sentence(value: str) -> str:
    text = value.strip()
    if not text:
        return ""
    return text if text.endswith((".", "!", "?")) else f"{text}."


def _format_metric_list(metrics: list[dict[str, str]]) -> str:
    return "; ".join(
        f"{metric['label']}: {metric['value']}"
        for metric in metrics
        if metric.get("value")
    )


def _evidence_hint_for_slide(title: str, bullets: list[str]) -> str:
    text = f"{title} {' '.join(bullets)}".lower()
    hints = []
    if any(keyword in text for keyword in ("company", "eligibility", "ownership", "employee", "document")):
        hints.append("company profile, SSM details, and document checklist")
    if any(keyword in text for keyword in ("fund", "budget", "cost", "outsourc", "grant cap")):
        hints.append("budget table, quotations, and grant cap calculation")
    if any(keyword in text for keyword in ("timeline", "milestone", "kpi", "risk")):
        hints.append("implementation timeline, KPI tracker, and risk register")
    if any(keyword in text for keyword in ("solution", "validation", "partner", "market")):
        hints.append("product demo, validation notes, partner evidence, or customer proof")
    return "; ".join(dict.fromkeys(hints)) or "source documents and proposal figures for this section"


def _is_informative_deck(slides: list[dict[str, Any]] | None) -> bool:
    if not slides or len(slides) < 7:
        return False
    total_bullets = sum(len(_slide_bullets(slide)) for slide in slides)
    return total_bullets >= len(slides) * 3


def _ensure_informative_pitch_deck(
    slides: list[dict[str, Any]] | None,
    fallback_slides: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if _is_informative_deck(slides):
        return slides or fallback_slides
    return fallback_slides


def _deck_markdown_from_slides(slides: list[dict[str, Any]]) -> str:
    lines = ["# Generated Pitch Deck", ""]
    for index, slide in enumerate(slides, start=1):
        slide_number = slide.get("slide_number") or index
        title = str(slide.get("title") or f"Slide {slide_number}")
        subtitle = str(slide.get("subtitle") or "").strip()
        bullets = _slide_bullets(slide)
        metrics = _slide_metrics(slide)
        grant_alignment = str(slide.get("grant_alignment") or "").strip()
        speaker_notes = str(slide.get("speaker_notes") or "").strip()

        lines.append(f"## Slide {slide_number}: {title}")
        if subtitle:
            lines.append(f"_{subtitle}_")
            lines.append("")
        if bullets:
            lines.append("### Key Messages")
            lines.extend(f"- {point}" for point in bullets)
            lines.append("")
        if metrics:
            lines.append("### Metrics")
            lines.extend(f"- {metric['label']}: {metric['value']}" for metric in metrics)
            lines.append("")
        if grant_alignment:
            lines.append(f"### Grant Alignment\n{grant_alignment}\n")
        if speaker_notes:
            lines.append(f"### Presenter Notes\n{speaker_notes}\n")
    return "\n".join(lines).strip() + "\n"


def _build_pitch_deck_script(
    company_name: str,
    grant_title: str,
    provider_name: str,
    slides: list[dict[str, Any]] | None,
    fallback_context: str | None = None,
) -> str:
    slide_count = len(slides or [])
    seconds_per_slide = max(35, min(60, round(390 / slide_count))) if slide_count else 45
    lines = [
        f"# Pitch Deck Speaking Script: {grant_title}",
        "",
        "## Presenter Setup",
        f"- Target length: 6-8 minutes; aim for about {seconds_per_slide} seconds per slide.",
        "- Keep every number consistent with the proposal, company profile, and supporting documents.",
        "- Pause after budget, eligibility, and KPI slides so panel members can note the evidence.",
        "",
        "## Opening",
        (
            f"Good day. We are {company_name}, and we are applying for {grant_title} from {provider_name}. "
            "Today I will explain the company profile, the project need, the funding request, "
            "how the funds will be governed, and the outcomes we will report back to the agency."
        ),
        "",
    ]

    if slides:
        for index, slide in enumerate(slides, start=1):
            slide_number = slide.get("slide_number") or index
            title = str(slide.get("title") or f"Slide {slide_number}").strip()
            subtitle = str(slide.get("subtitle") or "").strip()
            bullets = _slide_bullets(slide)
            metrics = _slide_metrics(slide)
            grant_alignment = str(slide.get("grant_alignment") or "").strip()
            speaker_notes = str(slide.get("speaker_notes") or "").strip()
            next_title = str(slides[index].get("title") or f"Slide {index + 1}").strip() if index < slide_count else ""

            lines.append(f"## Slide {slide_number}: {title}")
            if subtitle:
                lines.append(f"Purpose: {_sentence(subtitle)}")
            lines.append("Talk track:")
            if speaker_notes:
                lines.append(_sentence(speaker_notes))
            elif bullets:
                lines.append(f"Start by stating: {_sentence(bullets[0])}")
                for point in bullets[1:4]:
                    lines.append(f"Then explain: {_sentence(point)}")
                if len(bullets) > 4:
                    lines.append(f"Close the slide with: {_sentence(bullets[4])}")
            else:
                lines.append("Introduce this section and connect it directly to the grant review criteria.")
            if metrics:
                metric_text = _format_metric_list(metrics)
                if metric_text:
                    lines.append(f"Figures to say out loud: {_sentence(metric_text)}")
            if grant_alignment:
                lines.append(f"Grant alignment: {_sentence(grant_alignment)}")
            lines.append(f"Evidence to have ready: {_evidence_hint_for_slide(title, bullets)}.")
            if next_title:
                lines.append(f"Transition: With that context, move into {next_title} and show how the next point supports the same funding decision.")
            else:
                lines.append("Transition: Move from this slide into the final ask and invite questions.")
            lines.append("")
    elif fallback_context:
        lines.extend(
            [
                "## Uploaded Deck Talk Track",
                "Use the uploaded deck as the visual source, but strengthen the narration with the grant criteria.",
                "",
                "Key narrative to retain:",
                fallback_context[:1800],
                "",
                "Before presenting, add verbal links to funding amount, use of funds, eligibility documents, milestones, KPIs, and risk controls.",
                "",
            ]
        )

    lines.extend(
        [
            "## Closing Ask",
            (
                f"In closing, {company_name} is requesting support under {grant_title} to execute a controlled, "
                "evidence-backed project. We are ready to provide the required documents, answer questions on the budget, "
                "and report milestones responsibly after award."
            ),
            "",
            "## Likely Panel Questions",
            "- How exactly will the requested funding be used? Answer with the budget categories, project cost, and audit evidence.",
            "- What proves the company can execute? Answer with team size, operating history, documents, partners, and milestone owners.",
            "- What are the key risks? Answer with document, supplier, cost, and evidence risks plus the mitigation plan.",
            "- What outcomes will the agency see? Answer with KPIs, reporting milestones, capability gains, and commercial readiness.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def _ensure_pitch_deck_script(
    content: str | None,
    company_name: str,
    grant_title: str,
    provider_name: str,
    slides: list[dict[str, Any]] | None,
    fallback_context: str | None = None,
) -> str:
    baseline = _build_pitch_deck_script(
        company_name=company_name,
        grant_title=grant_title,
        provider_name=provider_name,
        slides=slides,
        fallback_context=fallback_context,
    )
    if not content or not content.strip():
        return baseline

    plain = _plain_text_from_markdown(content)
    expected_slide_mentions = min(5, len(slides or []))
    if len(plain) >= 1800 and plain.lower().count("slide") >= expected_slide_mentions:
        return content.strip() + "\n"
    return baseline + "\n## Additional Drafter Agent Notes\n" + content.strip() + "\n"


def _slides_for_response(slides: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "slide_number": int(slide.get("slide_number") or index),
            "title": str(slide.get("title") or f"Slide {index}"),
            "subtitle": str(slide.get("subtitle") or "") or None,
            "bullet_points": _slide_bullets(slide),
            "metrics": _slide_metrics(slide),
            "grant_alignment": str(slide.get("grant_alignment") or "") or None,
            "speaker_notes": str(slide.get("speaker_notes") or "") or None,
        }
        for index, slide in enumerate(slides, start=1)
    ]


def _slides_for_pptx(slides: list[dict[str, Any]]) -> list[dict[str, Any]]:
    layouts = ["hero", "split", "cards", "split", "metrics", "split", "timeline", "closing"]
    accents = ["0087A5", "494BD6", "00A676", "E09F3E"]
    valid_layouts = {"hero", "split", "metrics", "timeline", "cards", "closing"}
    return [
        {
            "title": str(slide.get("title") or f"Slide {index}"),
            "subtitle": str(slide.get("subtitle") or ""),
            "layout": str(slide.get("layout") if slide.get("layout") in valid_layouts else layouts[min(index - 1, len(layouts) - 1)]),
            "accent_color": str(slide.get("accent_color") or accents[(index - 1) % len(accents)]),
            "bullets": _slide_bullets(slide),
            "metrics": _slide_metrics(slide),
            "grant_alignment": str(slide.get("grant_alignment") or ""),
            "speaker_notes": str(slide.get("speaker_notes") or ""),
        }
        for index, slide in enumerate(slides, start=1)
    ]


@router.post("", response_model=GrantRead, status_code=status.HTTP_201_CREATED)
def create_grant_record(payload: GrantCreate, db: Session = Depends(get_db)):
    grant = create_grant(db, payload.model_dump())
    return grant


@router.get("", response_model=list[GrantRead])
def list_grant_records(include_all: bool = False, db: Session = Depends(get_db)):
    return list_grants(db, include_all=include_all)


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
        api_key=settings.google_api_key,
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
    SCOUT_STATE.update(
        {
            "status": "running",
            "run_mode": "curated",
            "started_at": _utc_now_iso(),
            "finished_at": None,
            "stop_requested": False,
            "message": "Scout is syncing curated grant data into the database.",
        }
    )
    report = run_scout(db, curated_files=_curated_source_files())
    finished_at = _utc_now_iso()
    if report.get("status") == "error":
        message = "; ".join(str(error) for error in report.get("errors", [])[:3]) or "Scout run failed."
        SCOUT_STATE.update(
            {
                "status": "error",
                "finished_at": finished_at,
                "last_report": report,
                "message": message,
            }
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message)
    SCOUT_STATE.update(
        {
            "status": report.get("status", "ok"),
            "last_report": report,
            "finished_at": finished_at,
            "message": "Scout run finished and the grant database is ready.",
        }
    )
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


@router.get("/{grant_id}/application/{user_id}/roadmap", response_model=ApplicationRoadmapRead)
async def get_application_roadmap(grant_id: int, user_id: int, db: Session = Depends(get_db)):
    if get_user_by_id(db, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    snapshot = build_grant_application_snapshot(db, user_id, grant_id)
    if snapshot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found.")

    try:
        coach_output = await asyncio.wait_for(
            run_coach(_coach_evaluator_output_from_snapshot(snapshot)),
            timeout=18,
        )
        coach = coach_output.model_dump()
        generated_by = "gemini_coach_agent"
    except Exception as exc:  # noqa: BLE001
        coach = snapshot.get("coach") or {
            "encouraging_message": f"Coach Agent fallback is active while live generation is unavailable: {str(exc)[:160]}",
            "next_steps": [],
        }
        generated_by = "deterministic_coach_fallback"

    return _build_application_roadmap(snapshot, coach, generated_by)


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

    metadata = {
        "requirement_id": requirement.id if requirement else None,
        "extra_context": payload.extra_context,
    }
    if document_type in {"business_proposal", "proposal"}:
        document = _store_generated_pdf(
            db,
            user_id,
            grant_id,
            grant.title,
            document_type,
            document_name,
            content,
            metadata,
        )
    else:
        document = _store_generated_markdown(
            db,
            user_id,
            grant_id,
            grant.title,
            document_type,
            document_name,
            content,
            metadata,
        )
    return {
        "document": document,
        "requirement_id": requirement.id if requirement else None,
        "document_type": document_type,
        "content_markdown": content,
        "message": "Generated document is ready for the submission package.",
    }


@router.post("/{grant_id}/application/{user_id}/documents/upload", response_model=DocumentRead)
async def upload_application_document(
    grant_id: int,
    user_id: int,
    document_type: str = Form(...),
    document_name: str | None = Form(None),
    requirement_id: int | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if get_user_by_id(db, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    grant = get_grant_by_id(db, grant_id)
    if grant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found.")
    if requirement_id is not None and not any(requirement.id == requirement_id for requirement in grant.requirements):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found for this grant.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    safe_filename = _safe_upload_filename(file.filename)
    content_type = file.content_type or "application/octet-stream"
    document = upsert_company_document(
        db,
        user_id,
        {
            "document_type": document_type or _slug(document_name or safe_filename),
            "file_name": safe_filename,
            "file_url": None,
            "status": "uploaded",
            "metadata": {
                "source": "grant_application_upload",
                "grant_id": grant_id,
                "grant_title": grant.title,
                "requirement_id": requirement_id,
                "document_name": document_name,
                "content_type": content_type,
                "content_base64": base64.b64encode(content).decode("ascii"),
                "size_bytes": len(content),
                "uploaded_at": _utc_now_iso(),
            },
        },
    )
    return document


@router.post("/{grant_id}/application/{user_id}/pitch-deck/evaluate", response_model=PitchDeckEvaluationRead)
async def evaluate_pitch_deck(
    grant_id: int,
    user_id: int,
    document_id: int | None = None,
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

    pitch_deck_doc = _uploaded_pitch_deck_document(db, user_id, grant_id, document_id)
    if pitch_deck_doc is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No uploaded pitch deck found. Upload your own pitch deck before running the evaluator.",
        )

    if pitch_deck_doc.status == "generated":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Evaluator reviews user-uploaded pitch decks. Upload your own deck instead of evaluating a generated deck.",
        )

    deck_text = _text_from_uploaded_pitch_deck(pitch_deck_doc)
    grant_context = {
        "grant_name": grant.title,
        "provider_name": grant.provider_name,
        "description": grant.description or "",
        "amount_max": grant.amount_max,
        "amount_min": grant.amount_min,
        "eligibility_notes": grant.eligibility_notes,
        "application_deadline": grant.application_deadline,
        "mandatory_documents": [requirement.name for requirement in grant.requirements if requirement.is_required],
    }
    sme_context = {
        "company_name": profile.company_name,
        "industry": profile.industry,
        "nationality": profile.nationality,
        "employee_count": profile.employee_count,
        "business_stage": profile.business_stage,
        "target_grant_amount": profile.target_grant_amount,
        "summary": profile.summary,
    }

    try:
        critique = await asyncio.wait_for(
            run_pitch_deck_evaluator(deck_text, grant_context=grant_context, sme_context=sme_context),
            timeout=30,
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Pitch deck evaluation took too long. Please try again.",
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate pitch deck: {str(exc)[:200]}",
        )

    critique_payload = critique.model_dump() if hasattr(critique, "model_dump") else critique
    pitch_deck_doc.metadata_json = {
        **(pitch_deck_doc.metadata_json or {}),
        "pitch_deck_evaluation": {
            "grant_id": grant_id,
            "evaluated_at": _utc_now_iso(),
            "critique": critique_payload,
        },
    }
    db.add(pitch_deck_doc)
    db.commit()
    db.refresh(pitch_deck_doc)

    return {
        "critique": critique,
        "evaluated_document": pitch_deck_doc,
        "message": "Pitch Deck Evaluator reviewed the uploaded deck and returned inline analytics.",
    }


@router.post("/{grant_id}/application/{user_id}/draft", response_model=DrafterOutputRead)
async def draft_application_bundle(
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
    documents = get_company_documents(db, user_id)

    business_proposal = _render_generated_document(
        "Business Proposal",
        "business_proposal",
        grant,
        profile,
        payload.extra_context,
    )

    extracted = profile.extracted_data or {}
    uploaded_deck_text = payload.uploaded_pitch_deck_text or extracted.get("uploaded_pitch_deck_text")
    profile_context = _profile_deck_context(profile)
    grant_context = {**_grant_deck_context(grant), **payload.extra_context}
    pitch_deck_slides = build_pitch_deck_slides(profile_context, grant_context)
    generated_deck = None
    deck_critique = None
    presentation_script_override = None
    drafter_metadata: dict[str, Any] = {"bundle": "drafter", "readiness_track": snapshot["track"]}
    try:
        agent_sme_profile = _agent_sme_profile(profile, documents)
        if uploaded_deck_text:
            agent_sme_profile = agent_sme_profile.model_copy(update={"uploaded_pitch_deck_text": uploaded_deck_text})
        agent_output = await asyncio.wait_for(
            run_drafter(agent_sme_profile, _agent_grant_requirement(grant)),
            timeout=35,
        )
        drafter_metadata["agent_mode"] = "gemini_drafter"
        if agent_output.proposal:
            business_proposal = agent_output.proposal.business_proposal_markdown
        if agent_output.deck:
            generated_deck = [slide.model_dump() for slide in agent_output.deck.generated_deck]
        if agent_output.script:
            presentation_script_override = agent_output.script.presentation_script_markdown
        if agent_output.deck_critique:
            deck_critique = agent_output.deck_critique.model_dump()
    except Exception as exc:  # noqa: BLE001
        drafter_metadata["agent_mode"] = "deterministic_fallback"
        drafter_metadata["agent_error"] = str(exc)[:300]
        presentation_script_override = None
    business_proposal = _ensure_professional_business_proposal(
        business_proposal,
        grant,
        profile,
        payload.extra_context,
    )

    if uploaded_deck_text:
        active_slides = generated_deck or pitch_deck_slides
        if deck_critique is None:
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
        active_slides = _ensure_informative_pitch_deck(generated_deck, pitch_deck_slides)
        deck_markdown = _deck_markdown_from_slides(active_slides)
        deck_document_type = "pitch_deck"
        deck_document_name = "Pitch Deck"

    generated_deck_response = None if uploaded_deck_text and not generated_deck else _slides_for_response(active_slides)
    pptx_slides = _slides_for_pptx(active_slides)
    presentation_script = _ensure_pitch_deck_script(
        content=presentation_script_override,
        company_name=profile.company_name,
        grant_title=grant.title,
        provider_name=grant.provider_name,
        slides=None if uploaded_deck_text else active_slides,
        fallback_context=uploaded_deck_text,
    )
    drafter_metadata["deck_slide_count"] = len(active_slides)
    pitch_deck_content = build_pitch_deck_pptx_from_slides(pptx_slides)
    pitch_deck_document = _store_generated_pptx(
        db=db,
        user_id=user_id,
        grant_id=grant_id,
        filename=f"{_slug(profile.company_name)}_{_slug(grant.title)}_pitch_deck.pptx",
        content=pitch_deck_content,
        layout_plan={"slides": pptx_slides},
        generation_mode=str(drafter_metadata["agent_mode"]),
    )

    generated_documents = [
        _store_generated_pdf(
            db,
            user_id,
            grant_id,
            grant.title,
            "business_proposal",
            "Business Proposal",
            business_proposal,
            drafter_metadata,
        ),
        _store_generated_text(
            db,
            user_id,
            grant_id,
            grant.title,
            "presentation_script",
            "Presentation Script",
            presentation_script,
            drafter_metadata,
        ),
        pitch_deck_document,
    ]
    if not uploaded_deck_text:
        generated_documents.append(
            _store_generated_markdown(
                db,
                user_id,
                grant_id,
                grant.title,
                deck_document_type,
                deck_document_name,
                deck_markdown,
                drafter_metadata,
            ),
        )

    return {
        "business_proposal_markdown": business_proposal,
        "presentation_script_markdown": presentation_script,
        "generated_deck": generated_deck_response,
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
            api_key=settings.google_api_key,
        )
        generation_mode = str(layout_plan.get("generation_mode") or "gemini_creative")
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
    script_content = _build_pitch_deck_script(
        company_name=profile.company_name,
        grant_title=grant.title,
        provider_name=grant.provider_name,
        slides=layout_plan.get("slides") if isinstance(layout_plan.get("slides"), list) else None,
    )
    _store_generated_text(
        db=db,
        user_id=user_id,
        grant_id=grant_id,
        grant_title=grant.title,
        document_type="presentation_script",
        document_name="Pitch Deck Script",
        content=script_content,
        extra_metadata={"companion_document_id": document.id, "bundle": "pitch_deck"},
    )
    return {
        "document": _generated_file_summary(document),
        "download_url": f"/grants/{grant_id}/application/{user_id}/documents/{document.id}/download",
        "message": "Pitch deck and companion script generated by Drafter Agent and stored in the user document database.",
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

    generated_binary = _binary_bytes_from_document(document)
    if generated_binary:
        content, content_type = generated_binary
        return _bytes_response(content, content_type, document.file_name)

    generated_content = document.metadata_json.get("content_markdown")
    if generated_content:
        buffer = io.BytesIO(generated_content.encode("utf-8"))
        content_type = document.metadata_json.get("content_type") or (
            TEXT_MIME if document.file_name.lower().endswith(".txt") else "text/markdown"
        )
        return StreamingResponse(
            buffer,
            media_type=content_type,
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
        if not is_inline_review_document(document)
        and (
            document.document_type in requirement_types
            or document.metadata_json.get("grant_id") == grant_id
        )
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
            generated_binary = _binary_bytes_from_document(document)
            if generated_binary:
                content, _content_type = generated_binary
                archive.writestr(f"generated/{document.file_name}", content)
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
