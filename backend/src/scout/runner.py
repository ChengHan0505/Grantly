from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import requests
from sqlalchemy.orm import Session
from zhipuai import ZhipuAI

from src.core.config import settings
from src.database.db import upsert_grant_from_scout
from src.scout.crawler import crawl_source
from src.scout.extractor import extract_grants_from_page
from src.scout.normalize import normalize_record
from src.scout.sources import load_sources_from_file
from src.scout.storage import persist_raw_results, persist_report


def run_scout(
    db: Session,
    source_file: str | None = None,
    sources_override: list | None = None,
    max_links_per_page_override: int | None = None,
) -> dict:
    if not settings.scout_enabled:
        return {"status": "disabled", "message": "Scout is disabled in settings."}
    if not settings.zai_api_key:
        return {"status": "error", "message": "Missing ZAI_API_KEY in environment."}

    if sources_override is not None:
        sources = sources_override
    else:
        if not source_file:
            return {"status": "error", "message": "No source file provided and no source override supplied."}
        config_path = Path(source_file)
        if not config_path.is_absolute():
            config_path = Path(__file__).resolve().parents[2] / config_path
        sources = load_sources_from_file(str(config_path))
    base_dir = Path(__file__).resolve().parents[2]
    results_dir = Path(settings.scout_results_dir)
    if not results_dir.is_absolute():
        results_dir = base_dir / results_dir
    report_path = Path(settings.scout_report_path)
    if not report_path.is_absolute():
        report_path = base_dir / report_path

    client = ZhipuAI(api_key=settings.zai_api_key)
    http = requests.Session()
    http.headers.update({"User-Agent": settings.scout_user_agent})

    pages_fetched = 0
    pages_failed = 0
    grants_inserted = 0
    grants_updated = 0
    errors: list[str] = []
    all_records = []

    for source in sources:
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
        )
        pages_fetched += len(pages)
        pages_failed += len(crawl_errors)
        errors.extend(crawl_errors)

        for page in pages:
            try:
                extracted = extract_grants_from_page(
                    client=client,
                    model=settings.zai_model,
                    page_url=page["url"],
                    page_text=page["text"],
                    source_name=source.name,
                )
                for record in extracted:
                    normalized = normalize_record(record)
                    all_records.append(normalized)
                    _, created = upsert_grant_from_scout(db, normalized.model_dump(mode="python"))
                    if created:
                        grants_inserted += 1
                    else:
                        grants_updated += 1
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{source.name}: extraction failed for {page['url']} ({exc})")

    db.commit()
    raw_path = persist_raw_results(str(results_dir), all_records)
    report = {
        "status": "ok",
        "run_at": datetime.now(timezone.utc).isoformat(),
        "source_count": len(sources),
        "pages_fetched": pages_fetched,
        "pages_failed": pages_failed,
        "grants_extracted": len(all_records),
        "grants_inserted": grants_inserted,
        "grants_updated": grants_updated,
        "raw_results_path": str(raw_path),
        "errors": errors[:100],
    }
    persist_report(str(report_path), report)
    return report
