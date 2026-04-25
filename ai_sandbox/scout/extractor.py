from __future__ import annotations

import json
import re

from zhipuai import ZhipuAI

from .schemas import ScoutGrantRecord


def _safe_json_slice(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else "{}"


def _first_match(patterns: list[str], text: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return " ".join(match.group(1).split())
    return None


def _amount_bounds(text: str) -> tuple[float | None, float | None]:
    amounts: list[float] = []
    for raw in re.findall(r"RM\s*([0-9][0-9,]*(?:\.\d+)?)\s*(million|m)?", text, re.IGNORECASE):
        value = float(raw[0].replace(",", ""))
        if raw[1].lower() in {"million", "m"}:
            value *= 1_000_000
        amounts.append(value)
    if not amounts:
        return None, None
    return min(amounts), max(amounts)


def _deadline_from_text(text: str) -> str | None:
    deadline = _first_match(
        [
            r"opening date from\s+([^.\n]+)",
            r"application open until\s+([^.\n]+)",
            r"grant opens on\s+([^.\n]+)",
            r"grants opens on\s+([^.\n]+)",
            r"(\d{1,2}\s+[A-Za-z]+\s+\d{4}\s+until\s+\d{1,2}\s+[A-Za-z]+\s+\d{4})",
        ],
        text,
    )
    if deadline:
        clean = deadline.rstrip(".")
        if re.search(r"available throughout the year", clean, re.IGNORECASE):
            date_match = re.search(r"\d{1,2}\s+[A-Za-z]+\s+\d{4}", clean)
            if date_match:
                return f"From {date_match.group(0)}; subject to funds"
        return clean
    if re.search(r"available throughout the year", text, re.IGNORECASE):
        return "Available throughout the year, subject to availability of funds"
    return None


def _title_from_page(page_url: str, page_text: str) -> str | None:
    known_titles = {
        "/dcg": "DIGITAL CONTENT GRANT (DCG)",
        "/mdxg": "MALAYSIA DIGITAL X-PORT GRANT (MDXG)",
        "/mdcg": "MALAYSIA DIGITAL CATALYST GRANT (MDCG)",
        "/mdag-ai": "MALAYSIA DIGITAL ACCELERATION GRANT - ARTIFICIAL INTELLIGENCE (MDAG-AI)",
        "/mdag": "MALAYSIA DIGITAL ACCELERATION GRANT (MDAG)",
    }
    for suffix, title in known_titles.items():
        if page_url.rstrip("/").lower().endswith(suffix):
            return title
    title = _first_match([r"#\s*([A-Z][^\n]{8,90})", r"^([A-Z][A-Z0-9 &()/-]{8,90})$"], page_text)
    if title and "MDEC GRANTS" not in title.upper():
        return title
    return None


def _description_from_text(title: str, text: str) -> str | None:
    cleaned = " ".join(text.split())
    title_index = cleaned.lower().find(title.lower().split(" (")[0].lower())
    excerpt = cleaned[title_index + len(title) :] if title_index >= 0 else cleaned
    sentences = re.split(r"(?<=[.!?])\s+", excerpt)
    useful = [
        sentence.strip()
        for sentence in sentences
        if 40 <= len(sentence.strip()) <= 260 and "grant" in sentence.lower()
    ]
    return useful[0] if useful else None


def fallback_extract_grants_from_page(
    page_url: str,
    page_text: str,
    source_name: str,
    reason: str | None = None,
) -> list[ScoutGrantRecord]:
    title = _title_from_page(page_url, page_text)
    if not title:
        return []

    amount_min, amount_max = _amount_bounds(page_text)
    status = "closed" if re.search(r"application\s+closed", page_text, re.IGNORECASE) else "unknown"
    deadline = _deadline_from_text(page_text)
    description = _description_from_text(title, page_text)
    metadata = {
        "source_name": source_name,
        "extraction_mode": "fallback_regex",
    }
    if reason:
        metadata["fallback_reason"] = reason[:240]

    return [
        ScoutGrantRecord(
            title=title,
            provider_name="Malaysia Digital Economy Corporation (MDEC)",
            source_url=page_url,
            description=description,
            amount_min=amount_min,
            amount_max=amount_max,
            nationality="Malaysia",
            industry="Digital economy",
            eligibility_notes=None,
            application_deadline=deadline,
            status=status,
            metadata_json=metadata,
            requirements=[],
        )
    ]


def extract_grants_from_page(
    client: ZhipuAI,
    model: str,
    page_url: str,
    page_text: str,
    source_name: str,
) -> list[ScoutGrantRecord]:
    prompt = (
        "You are extracting Malaysia SME grants/funding opportunities.\n"
        "Return JSON only, with shape: "
        '{"grants":[{"title":"","provider_name":"","source_url":"","description":"","amount_min":null,'
        '"amount_max":null,"nationality":"Malaysia","industry":null,"eligibility_notes":null,'
        '"application_deadline":null,"status":"open","requirements":[{"name":"","description":null,'
        '"source_type":"attached","document_type":null,"is_required":true}]}]}.\n'
        "Rules:\n"
        "1) Only include grant/funding/program pages relevant for SMEs/startups.\n"
        "2) If page is irrelevant, return {\"grants\":[]}.\n"
        "3) max 3 grants from one page.\n"
        "4) Keep text concise and factual from the page.\n"
        f"5) If source_url missing, use {page_url}.\n"
        f"Source: {source_name}\n"
        f"Page URL: {page_url}\n\n"
        f"Page Text:\n{page_text}"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a strict JSON extraction engine."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )
    raw_text = response.choices[0].message.content if response.choices else "{}"
    json_text = _safe_json_slice(raw_text)
    payload = json.loads(json_text)
    records: list[ScoutGrantRecord] = []
    for item in payload.get("grants", []):
        if not item.get("source_url"):
            item["source_url"] = page_url
        metadata = item.get("metadata_json") or {}
        metadata["source_name"] = source_name
        item["metadata_json"] = metadata
        records.append(ScoutGrantRecord.model_validate(item))
    return records
