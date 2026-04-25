from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .schemas import ScoutGrantRecord, ScoutRequirement


DOCUMENT_HINTS: tuple[tuple[str, str, str, str], ...] = (
    ("ssm", "SSM Certificate", "ssm", "attached"),
    ("companies act", "SSM Certificate", "ssm", "attached"),
    ("financial", "Latest Financial Statement", "financial_statement", "attached"),
    ("audited", "Latest Audited Financial Statement", "financial_statement", "attached"),
    ("pitch deck", "Project Proposal Pitch Deck", "pitch_deck", "generated"),
    ("proposal", "Business Proposal", "business_proposal", "generated"),
    ("project proposal", "Project Proposal", "business_proposal", "generated"),
    ("board resolution", "Board Resolution", "bod_resolution", "attached"),
    ("bod resolution", "Board Resolution", "bod_resolution", "attached"),
    ("integrity declaration", "Integrity Declaration Form", "integrity_declaration", "generated"),
    ("mou", "End-user Partner MOU / LOI", "partner_mou", "attached"),
    ("loi", "End-user Partner MOU / LOI", "partner_mou", "attached"),
    ("jakim", "Halal Certification", "halal_certificate", "attached"),
    ("halal certification", "Halal Certification", "halal_certificate", "attached"),
    ("mysti", "MySTI Certification", "mysti_certificate", "attached"),
    ("mof", "MOF / ePerolehan Registration", "mof_registration", "attached"),
    ("eperolehan", "MOF / ePerolehan Registration", "mof_registration", "attached"),
)

DEFAULT_REQUIREMENTS: tuple[tuple[str, str, str], ...] = (
    ("SSM Certificate", "ssm", "attached"),
    ("Latest Financial Statement", "financial_statement", "attached"),
    ("Company Profile", "company_profile", "generated"),
    ("Business Proposal", "business_proposal", "generated"),
    ("Pitch Deck", "pitch_deck", "generated"),
)


def load_grants_from_curated_outputs(paths: list[str]) -> list[ScoutGrantRecord]:
    records: list[ScoutGrantRecord] = []
    seen: set[tuple[str, str]] = set()
    for path in paths:
        file_path = Path(path)
        if not file_path.exists():
            continue
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        for item, provider_name, source_name in _walk_grant_items(payload, file_path.stem):
            url = str(item.get("url") or "").strip()
            name = str(item.get("name") or item.get("title") or "").strip()
            if not name or not url:
                continue
            key = (name.lower(), url.lower())
            if key in seen:
                continue
            seen.add(key)
            records.append(_record_from_item(item, provider_name, source_name))
    return records


def _walk_grant_items(payload: Any, source_name: str, provider_name: str | None = None):
    if isinstance(payload, dict):
        next_provider = provider_name or _provider_from_payload(payload, source_name)
        if payload.get("name") and payload.get("url"):
            yield payload, next_provider, source_name
            return
        for value in payload.values():
            yield from _walk_grant_items(value, source_name, next_provider)
    elif isinstance(payload, list):
        for item in payload:
            yield from _walk_grant_items(item, source_name, provider_name)


def _provider_from_payload(payload: dict[str, Any], source_name: str) -> str:
    text = json.dumps(payload, ensure_ascii=True).lower()
    if "mdec" in source_name or "malaysia digital economy corporation" in text:
        return "Malaysia Digital Economy Corporation (MDEC)"
    if "cradle" in source_name or "cradle fund" in text:
        return "Cradle Fund"
    if "mtdc" in source_name or "mtdc" in text:
        return "Malaysia Technology Development Corporation (MTDC)"
    if "smifunding" in source_name:
        return "SMI Funding"
    domain = urlparse(str(payload.get("url") or "")).netloc.replace("www.", "")
    return domain or source_name.replace("_", " ").title()


def _record_from_item(item: dict[str, Any], provider_name: str, source_name: str) -> ScoutGrantRecord:
    body_text = _flatten_text(item)
    amount_min, amount_max = _amount_bounds(body_text)
    requirements = _requirements_from_item(item, body_text)
    description = _pick_text(
        item,
        "introduction",
        "objective",
        "overview",
        "summary",
        "grant_type",
        fallback="Grant or funding programme captured from curated Scout source data.",
    )
    eligibility_notes = _eligibility_notes(item)
    return ScoutGrantRecord(
        title=str(item.get("name") or item.get("title")).strip(),
        provider_name=provider_name,
        source_url=str(item["url"]).strip(),
        description=description,
        amount_min=amount_min,
        amount_max=amount_max,
        nationality="Malaysia",
        industry=_industry_from_item(item),
        eligibility_notes=eligibility_notes,
        application_deadline=_pick_text(item, "application_deadline", "closing_date", "deadline"),
        status="open",
        metadata_json={
            "source_name": source_name,
            "extraction_mode": "curated_json",
            "raw_item": item,
        },
        requirements=requirements,
    )


def _flatten_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(_flatten_text(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(_flatten_text(item) for item in value)
    return str(value)


def _pick_text(item: dict[str, Any], *keys: str, fallback: str | None = None) -> str | None:
    for key in keys:
        value = item.get(key)
        if value in (None, "", [], {}):
            continue
        if isinstance(value, (list, dict)):
            return _clip(_flatten_text(value), 420)
        return _clip(str(value), 420)
    return fallback


def _clip(value: str, limit: int) -> str:
    value = " ".join(value.split())
    return value[: limit - 3].rstrip() + "..." if len(value) > limit else value


def _amount_bounds(text: str) -> tuple[float | None, float | None]:
    amounts: list[float] = []
    for number, multiplier in re.findall(r"RM\s*([0-9][0-9,.]*)\s*(million|m)?", text, re.IGNORECASE):
        try:
            value = float(number.replace(",", ""))
        except ValueError:
            continue
        if multiplier.lower() in {"million", "m"}:
            value *= 1_000_000
        if 1_000 <= value <= 100_000_000:
            amounts.append(value)
    if not amounts:
        return None, None
    return min(amounts), max(amounts)


def _requirements_from_item(item: dict[str, Any], body_text: str) -> list[ScoutRequirement]:
    requirement_sources = []
    for key in (
        "application_documents_required",
        "mandatory_documents",
        "basic_eligibility",
        "company_eligibility",
        "individual_eligibility",
        "eligibility",
        "specific_conditions",
    ):
        if key in item:
            requirement_sources.append(item[key])
    haystack = f"{body_text} {' '.join(_flatten_text(value) for value in requirement_sources)}".lower()
    requirements: dict[str, ScoutRequirement] = {}
    for needle, name, document_type, source_type in DOCUMENT_HINTS:
        if needle not in haystack:
            continue
        requirements[document_type] = ScoutRequirement(
            name=name,
            description=f"Captured from curated Scout source data for {item.get('name') or 'this grant'}.",
            source_type=source_type,
            document_type=document_type,
            is_required=True,
        )

    for name, document_type, source_type in DEFAULT_REQUIREMENTS:
        requirements.setdefault(
            document_type,
            ScoutRequirement(
                name=name,
                description="Baseline submission document used by the Evaluator checklist.",
                source_type=source_type,
                document_type=document_type,
                is_required=True,
            ),
        )
    return list(requirements.values())


def _eligibility_notes(item: dict[str, Any]) -> str | None:
    parts = []
    for key in (
        "basic_eligibility",
        "company_eligibility",
        "individual_eligibility",
        "eligibility",
        "specific_conditions",
        "application_hint",
    ):
        if key in item:
            parts.append(f"{key.replace('_', ' ').title()}: {_flatten_text(item[key])}")
    return _clip(" ".join(parts), 900) if parts else None


def _industry_from_item(item: dict[str, Any]) -> str | None:
    text = _flatten_text(item).lower()
    if any(term in text for term in ("digital", "technology", "software", "4ir", "semiconductor", "aerospace")):
        return "Technology"
    if "halal" in text:
        return "Halal"
    if "creative" in text or "content" in text:
        return "Creative Content"
    return "General"
