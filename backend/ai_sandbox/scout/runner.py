from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

import requests
from sqlalchemy.orm import Session

from backend.ai_sandbox.glm_client import GLMClient
from backend.src.core.config import settings
from backend.src.database.db import upsert_grant_from_scout

from .crawler import crawl_source
from .curated import load_grants_from_curated_outputs
from .extractor import extract_grants_from_page, fallback_extract_grants_from_page
from .normalize import normalize_record
from .sources import load_sources_from_file
from .storage import persist_raw_results, persist_report


def _grant_title(record: object) -> str:
    if hasattr(record, "title"):
        return str(getattr(record, "title") or "unknown")
    if isinstance(record, dict):
        return str(record.get("title") or "unknown")
    return "unknown"


def _upsert_normalized_grant(db: Session, normalized) -> bool:
    with db.begin_nested():
        _, created = upsert_grant_from_scout(db, normalized.model_dump(mode="python"))
    return created


def _summarize_extraction_error(exc: Exception) -> str:
    text = str(exc).replace("\n", " ").strip()
    lower_text = text.lower()
    if "401" in text and "claude" in lower_text:
        return "Claude Sonnet authentication failed with 401. Check CLAUDE_SONNET_API_KEY in .env."
    if "401" in text and "z.ai" in text.lower():
        return "Gemini failed and Z.ai authentication failed with 401. Check ZAI_API_KEY in .env."
    if "401" in text and "openrouter" in lower_text:
        return "Claude failed and OpenRouter Gemini authentication failed with 401. Check OPENROUTER_GEMINI_API_KEY or OPENROUTER_API_KEY in .env."
    if "401" in text:
        return "Gemini authentication failed with 401. Check GOOGLE_API_KEY in .env."
    if "429" in text or "rate limit" in lower_text or "quota" in lower_text:
        return "Claude/OpenRouter/Gemini/Z.ai rate limit reached. Local fallback extraction will be used for this Scout run."
    return text[:300]


def _page_text_with_metadata(page: dict) -> str:
    metadata = page.get("metadata") or {}
    header_lines = [
        str(metadata.get("heading") or ""),
        str(metadata.get("title") or ""),
        str(metadata.get("description") or ""),
    ]
    header = "\n".join(line for line in header_lines if line.strip())
    return f"{header}\n\n{page['text']}" if header else page["text"]


def run_scout(
    db: Session,
    source_file: str | None = None,
    sources_override: list | None = None,
    curated_files: list[str] | None = None,
    max_links_per_page_override: int | None = None,
    should_stop: Callable[[], bool] | None = None,
) -> dict:
    if not settings.scout_enabled:
        return {"status": "disabled", "message": "Scout is disabled in settings."}
    if curated_files is not None:
        return _ingest_curated_grants(db, curated_files)
    if sources_override is not None:
        sources = sources_override
    else:
        if not source_file:
            return {"status": "error", "message": "No source file provided and no source override supplied."}
        config_path = Path(source_file)
        if not config_path.is_absolute():
            root_dir = Path(__file__).resolve().parents[3]
            backend_dir = Path(__file__).resolve().parents[2]
            config_path = root_dir / config_path if config_path.parts and config_path.parts[0] == "backend" else backend_dir / config_path
        sources = load_sources_from_file(str(config_path))
    project_dir = Path(__file__).resolve().parents[3]
    backend_dir = Path(__file__).resolve().parents[2]
    results_dir = Path(settings.scout_results_dir)
    if not results_dir.is_absolute():
        results_dir = project_dir / results_dir if results_dir.parts and results_dir.parts[0] == "backend" else backend_dir / results_dir
    report_path = Path(settings.scout_report_path)
    if not report_path.is_absolute():
        report_path = project_dir / report_path if report_path.parts and report_path.parts[0] == "backend" else backend_dir / report_path

    client = (
        GLMClient(
            api_key=settings.google_api_key,
            model=settings.gemini_model,
            claude_api_key=settings.claude_sonnet_api_key,
            claude_model=settings.claude_sonnet_model,
            openrouter_api_key=settings.openrouter_api_key,
            openrouter_model=settings.openrouter_model,
            zai_api_key=settings.zai_api_key,
            zai_model=settings.zai_model,
        )
        if settings.claude_sonnet_api_key or settings.google_api_key or settings.openrouter_api_key or settings.zai_api_key
        else None
    )
    http = requests.Session()
    http.headers.update({"User-Agent": settings.scout_user_agent})

    pages_fetched = 0
    pages_failed = 0
    grants_inserted = 0
    grants_updated = 0
    grants_found_open = 0
    grants_found_closed = 0
    grants_found_unknown = 0
    errors: list[str] = []
    all_records = []
    llm_disabled_reason = (
        "Missing CLAUDE_SONNET_API_KEY, OPENROUTER_GEMINI_API_KEY/OPENROUTER_API_KEY, GOOGLE_API_KEY, and ZAI_API_KEY; "
        "using local fallback extractor."
    ) if client is None else None
    auth_notice_added = False
    fallback_notice_added = False

    for source in sources:
        if should_stop and should_stop():
            errors.append("Scout run stopped before all sources were crawled.")
            break
        pages, crawl_errors = crawl_source(
            source=source,
            session=http,
            timeout_seconds=settings.scout_http_timeout_seconds,
            max_pages=settings.scout_max_pages_per_source,
            max_links_per_page=(
                max_links_per_page_override
                if max_links_per_page_override is not None
                else settings.scout_max_links_per_page
            ),
            max_chars_per_page=settings.scout_max_chars_per_page,
            user_agent=settings.scout_user_agent,
            respect_robots_txt=settings.scout_respect_robots_txt,
            request_delay_seconds=settings.scout_request_delay_seconds,
            should_stop=should_stop,
        )
        pages_fetched += len(pages)
        pages_failed += len(crawl_errors)
        errors.extend(crawl_errors)

        for page in pages:
            if should_stop and should_stop():
                errors.append("Scout run stopped before all fetched pages were extracted.")
                break
            try:
                page_text = _page_text_with_metadata(page)
                if client is None:
                    extracted = fallback_extract_grants_from_page(
                        page_url=page["url"],
                        page_text=page_text,
                        source_name=source.name,
                        reason=llm_disabled_reason,
                        page_metadata=page.get("metadata"),
                    )
                    if extracted and not fallback_notice_added:
                        errors.append(f"{source.name}: {llm_disabled_reason}")
                        fallback_notice_added = True
                else:
                    try:
                        extracted = extract_grants_from_page(
                            client=client,
                            page_url=page["url"],
                            page_text=page_text,
                            source_name=source.name,
                        )
                    except Exception as exc:  # noqa: BLE001
                        fallback_reason = _summarize_extraction_error(exc)
                        if "401" in fallback_reason or "rate limit" in fallback_reason.lower():
                            llm_disabled_reason = fallback_reason
                            client = None
                            if not auth_notice_added:
                                errors.append(f"{source.name}: {fallback_reason} Local fallback extraction will be used.")
                                auth_notice_added = True
                        extracted = fallback_extract_grants_from_page(
                            page_url=page["url"],
                            page_text=page_text,
                            source_name=source.name,
                            reason=fallback_reason,
                            page_metadata=page.get("metadata"),
                        )
                        if extracted:
                            if not fallback_notice_added:
                                errors.append(f"{source.name}: used local fallback extractor for MDEC grant pages.")
                                fallback_notice_added = True
                        else:
                            if client is not None:
                                raise
                for record in extracted:
                    normalized = normalize_record(record)
                    if normalized.status == "open":
                        grants_found_open += 1
                    elif normalized.status == "closed":
                        grants_found_closed += 1
                    else:
                        grants_found_unknown += 1
                    all_records.append(normalized)
                    try:
                        created = _upsert_normalized_grant(db, normalized)
                        if created:
                            grants_inserted += 1
                        else:
                            grants_updated += 1
                    except Exception as db_exc:  # noqa: BLE001
                        errors.append(f"{source.name}: failed to save grant '{_grant_title(normalized)}' to database ({db_exc})")
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{source.name}: extraction failed for {page['url']} ({exc})")

    try:
        db.commit()
    except Exception as commit_exc:  # noqa: BLE001
        errors.append(f"Failed to commit grants to database: {commit_exc}")
        db.rollback()
    stopped = should_stop() if should_stop else False
    raw_path = persist_raw_results(str(results_dir), all_records)
    report = {
        "status": "stopped" if stopped else "ok",
        "run_at": datetime.now(timezone.utc).isoformat(),
        "source_count": len(sources),
        "pages_fetched": pages_fetched,
        "pages_failed": pages_failed,
        "grants_extracted": len(all_records),
        "grants_inserted": grants_inserted,
        "grants_updated": grants_updated,
        "grants_found_open": grants_found_open,
        "grants_found_closed": grants_found_closed,
        "grants_found_unknown": grants_found_unknown,
        "raw_results_path": str(raw_path),
        "errors": errors[:100],
    }
    persist_report(str(report_path), report)
    return report


def _ingest_curated_grants(db: Session, curated_files: list[str]) -> dict:
    grants_inserted = 0
    grants_updated = 0
    grants_found_open = 0
    grants_found_closed = 0
    grants_found_unknown = 0
    errors: list[str] = []
    all_records = []

    try:
        records = load_grants_from_curated_outputs(curated_files)
        for record in records:
            normalized = normalize_record(record)
            if normalized.status == "open":
                grants_found_open += 1
            elif normalized.status == "closed":
                grants_found_closed += 1
            else:
                grants_found_unknown += 1
            all_records.append(normalized)
            try:
                created = _upsert_normalized_grant(db, normalized)
                if created:
                    grants_inserted += 1
                else:
                    grants_updated += 1
            except Exception as db_exc:  # noqa: BLE001
                errors.append(f"Failed to save grant '{_grant_title(normalized)}' to database: {db_exc}")
        try:
            db.commit()
        except Exception as commit_exc:  # noqa: BLE001
            errors.append(f"Failed to commit grants to database: {commit_exc}")
            db.rollback()
    except Exception as exc:  # noqa: BLE001
        errors.append(f"Curated grants ingestion error: {exc}")
        db.rollback()

    project_dir = Path(__file__).resolve().parents[3]
    backend_dir = Path(__file__).resolve().parents[2]
    results_dir = Path(settings.scout_results_dir)
    if not results_dir.is_absolute():
        results_dir = project_dir / results_dir if results_dir.parts and results_dir.parts[0] == "backend" else backend_dir / results_dir
    report_path = Path(settings.scout_report_path)
    if not report_path.is_absolute():
        report_path = project_dir / report_path if report_path.parts and report_path.parts[0] == "backend" else backend_dir / report_path

    raw_path = persist_raw_results(str(results_dir), all_records)
    report = {
        "status": "error" if errors else "ok",
        "run_at": datetime.now(timezone.utc).isoformat(),
        "source_count": len(curated_files),
        "pages_fetched": 0,
        "pages_failed": 0,
        "grants_extracted": len(all_records),
        "grants_inserted": grants_inserted,
        "grants_updated": grants_updated,
        "grants_found_open": grants_found_open,
        "grants_found_closed": grants_found_closed,
        "grants_found_unknown": grants_found_unknown,
        "raw_results_path": str(raw_path),
        "errors": errors,
        "mode": "curated_json",
    }
    persist_report(str(report_path), report)
    return report
