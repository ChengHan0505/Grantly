from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from dateutil import parser as date_parser

from backend.ai_sandbox.glm_client import GLMClient
from .schemas import ScoutGrantRecord, ScoutRequirement


DATE_PATTERN = (
    r"(?:\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{4}|"
    r"[A-Za-z]+\s+\d{1,2},?\s+\d{4}|"
    r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
)

OPEN_PATTERNS = [
    r"\bapply\s+now\b",
    r"\bnow\s+open\b",
    r"\bapplications?\s+(?:are\s+)?open\b",
    r"\bopen\s+for\s+applications?\b",
    r"\bcurrently\s+accepting\b",
    r"\bapplication\s+open\s+until\b",
    r"\bopen\s+until\b",
    r"\bavailable\s+throughout\s+the\s+year\b",
    r"\brolling\s+(?:basis|deadline|applications?)\b",
]

CLOSED_PATTERNS = [
    r"\bapplication\s+closed\b",
    r"\bapplications?\s+(?:are\s+)?closed\b",
    r"\bclosed\s+for\s+applications?\b",
    r"\bnot\s+currently\s+accepting\b",
    r"\bno\s+longer\s+accepting\b",
    r"\bdeadline\s+has\s+passed\b",
    r"\bexpired\b",
]


def _first_match(patterns: list[str], text: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return " ".join(match.group(1).split())
    return None


def _clean_text(text: str) -> str:
    return " ".join(text.split())


def _amount_bounds(text: str) -> tuple[float | None, float | None]:
    amounts: list[float] = []
    for raw in re.findall(r"RM\s*([0-9][0-9,]*(?:\.\d+)?)\s*(million|m)?", text, re.IGNORECASE):
        value = float(raw[0].replace(",", ""))
        if raw[1].lower() in {"million", "m"}:
            value *= 1_000_000
        amounts.append(value)
    amounts = [amount for amount in amounts if 1_000 <= amount <= 50_000_000]
    if not amounts:
        return None, None
    return min(amounts), max(amounts)


def _deadline_from_text(text: str) -> str | None:
    interval = re.search(
        rf"({DATE_PATTERN})\s+(?:to|until|-)\s+({DATE_PATTERN})",
        text,
        re.IGNORECASE,
    )
    if interval:
        return f"{_clean_date_text(interval.group(1))} until {_clean_date_text(interval.group(2))}"

    deadline = _first_match(
        [
            rf"opening date from\s+({DATE_PATTERN})",
            rf"application open until\s+({DATE_PATTERN})",
            rf"open until\s+({DATE_PATTERN})",
            rf"closing date\s*[:\-]?\s*({DATE_PATTERN})",
            rf"application deadline\s*[:\-]?\s*({DATE_PATTERN})",
            rf"deadline\s*[:\-]?\s*({DATE_PATTERN})",
            rf"grant opens on\s+({DATE_PATTERN})",
            rf"grants opens on\s+({DATE_PATTERN})",
        ],
        text,
    )
    if deadline:
        clean = _clean_date_text(deadline)
        if re.search(r"available throughout the year", clean, re.IGNORECASE):
            date_match = re.search(r"\d{1,2}\s+[A-Za-z]+\s+\d{4}", clean)
            if date_match:
                return f"From {date_match.group(0)}; subject to funds"
        return clean
    if re.search(r"available throughout the year", text, re.IGNORECASE):
        return "Available throughout the year, subject to availability of funds"
    return None


def _clean_date_text(value: str) -> str:
    return re.sub(r"(\d{1,2})(st|nd|rd|th)", r"\1", value.strip(), flags=re.IGNORECASE).rstrip(".")


def _parse_deadline_date(deadline: str | None) -> datetime | None:
    if not deadline:
        return None
    if re.search(r"throughout|rolling|subject to funds|from\b", deadline, re.IGNORECASE):
        return None
    matches = re.findall(DATE_PATTERN, deadline, re.IGNORECASE)
    candidate = matches[-1] if matches else deadline
    try:
        return date_parser.parse(_clean_date_text(candidate), fuzzy=True, dayfirst=True)
    except (ValueError, OverflowError, TypeError):
        return None


def _infer_status_from_text(text: str, deadline: str | None) -> str:
    today = datetime.now(timezone.utc).date()
    deadline_date = _parse_deadline_date(deadline)
    if deadline_date and deadline_date.date() < today:
        return "closed"
    if deadline_date and deadline_date.date() >= today:
        return "open"

    closed_hit = any(re.search(pattern, text, re.IGNORECASE) for pattern in CLOSED_PATTERNS)
    open_hit = any(re.search(pattern, text, re.IGNORECASE) for pattern in OPEN_PATTERNS)
    if closed_hit and not open_hit:
        return "closed"
    if open_hit and not closed_hit:
        return "open"
    if open_hit and re.search(r"\bapply\s+now\b", text, re.IGNORECASE):
        return "open"
    return "unknown"


def _title_from_page(page_url: str, page_text: str, page_metadata: dict | None = None) -> str | None:
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

    parsed = urlparse(page_url)
    if parsed.path.rstrip("/").lower() in {"/grants", "/funds", "/funding", "/programmes", "/programs"}:
        return None

    metadata_candidates = []
    if page_metadata:
        metadata_candidates.extend([page_metadata.get("heading"), page_metadata.get("title")])
    for candidate in metadata_candidates:
        if not candidate:
            continue
        normalized = _clean_title(candidate)
        if normalized:
            return normalized

    for line in page_text.splitlines()[:80]:
        normalized = _clean_title(line)
        if normalized:
            return normalized

    segment = parsed.path.rstrip("/").split("/")[-1]
    if segment and any(term in segment.lower() for term in ("grant", "fund", "programme", "program", "incentive")):
        return segment.replace("-", " ").replace("_", " ").title()
    return None


def _clean_title(value: str) -> str | None:
    cleaned = _clean_text(value)
    if not 8 <= len(cleaned) <= 120:
        return None
    upper = cleaned.upper()
    if upper in {"MDEC GRANTS", "GRANTS", "FUNDING", "HOME"}:
        return None
    if any(term in cleaned.lower() for term in ("grant", "fund", "programme", "program", "incentive", "financing")):
        return cleaned
    return None


def _description_from_text(title: str, text: str, page_metadata: dict | None = None) -> str | None:
    candidates: list[str] = []
    if page_metadata and page_metadata.get("description"):
        candidates.append(str(page_metadata["description"]))
    cleaned = " ".join(text.split())
    title_index = cleaned.lower().find(title.lower().split(" (")[0].lower())
    excerpt = cleaned[title_index + len(title) :] if title_index >= 0 else cleaned
    candidates.extend(re.split(r"(?<=[.!?])\s+", excerpt))
    candidates.extend(re.split(r"\s{2,}|\n+", text))

    useful = []
    for candidate in candidates:
        sentence = _clean_text(candidate)
        if not 45 <= len(sentence) <= 360:
            continue
        lower = sentence.lower()
        if "cookie" in lower or "privacy" in lower or "all rights reserved" in lower:
            continue
        if "application closed" in lower and "aim" not in lower and "support" not in lower:
            continue
        if any(term in lower for term in ("aim", "objective", "support", "assist", "accelerate", "commercial", "fund", "grant")):
            useful.append(sentence)
    if useful:
        return useful[0][:360]
    return None


def _requirements_from_text(text: str) -> list[ScoutRequirement]:
    known_documents = [
        ("SSM Certificate", "ssm", "attached"),
        ("Latest audited financial statement", "financial_statement", "attached"),
        ("Financial Statement", "financial_statement", "attached"),
        ("Board resolution", "bod_resolution", "attached"),
        ("Integrity Declaration Form", "integrity_declaration", "generated"),
        ("Company profile", "company_profile", "generated"),
        ("Project proposal", "business_proposal", "generated"),
        ("Pitch deck", "pitch_deck", "generated"),
        ("Letter of Intent", "loi", "attached"),
        ("MOU", "mou", "attached"),
        ("Purchase Order", "purchase_order", "attached"),
    ]
    requirements: list[ScoutRequirement] = []
    seen: set[str] = set()
    lower_text = text.lower()
    for name, document_type, source_type in known_documents:
        if name.lower() not in lower_text or document_type in seen:
            continue
        seen.add(document_type)
        requirements.append(
            ScoutRequirement(
                name=name,
                document_type=document_type,
                source_type=source_type,
                is_required=True,
            )
        )
    return requirements[:8]


def _provider_from_url(page_url: str, source_name: str) -> str:
    domain = urlparse(page_url).netloc.lower()
    if "mdec" in domain:
        return "Malaysia Digital Economy Corporation (MDEC)"
    if "cradle" in domain:
        return "Cradle Fund"
    if "mtdc" in domain:
        return "Malaysia Technology Development Corporation (MTDC)"
    return source_name.replace("-", " ").replace("_", " ").title()


def fallback_extract_grants_from_page(
    page_url: str,
    page_text: str,
    source_name: str,
    reason: str | None = None,
    page_metadata: dict | None = None,
) -> list[ScoutGrantRecord]:
    title = _title_from_page(page_url, page_text, page_metadata)
    if not title:
        return []

    amount_min, amount_max = _amount_bounds(page_text)
    deadline = _deadline_from_text(page_text)
    status = _infer_status_from_text(page_text, deadline)
    description = _description_from_text(title, page_text, page_metadata)
    metadata = {
        "source_name": source_name,
        "extraction_mode": "fallback_regex",
        "status_evidence": status,
    }
    if reason:
        metadata["fallback_reason"] = reason[:240]

    return [
        ScoutGrantRecord(
            title=title,
            provider_name=_provider_from_url(page_url, source_name),
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
            requirements=_requirements_from_text(page_text),
        )
    ]


def extract_grants_from_page(
    client: GLMClient,
    page_url: str,
    page_text: str,
    source_name: str,
) -> list[ScoutGrantRecord]:
    today = datetime.now(timezone.utc).date().isoformat()
    prompt = (
        "You are extracting Malaysia SME grants/funding opportunities.\n"
        "Return JSON only, with shape: "
        '{"grants":[{"title":"","provider_name":"","source_url":"","description":"","amount_min":null,'
        '"amount_max":null,"nationality":"Malaysia","industry":null,"eligibility_notes":null,'
        '"application_deadline":null,"status":"open","requirements":[{"name":"","description":null,'
        '"source_type":"attached","document_type":null,"is_required":true}]}]}.\n'
        "Rules:\n"
        "1) Only include grant/funding/program pages relevant for SMEs/startups.\n"
        f"2) Today is {today}. Only include grants currently open for application or rolling/available throughout the year. Exclude closed, expired, or not-yet-open intakes.\n"
        "3) max 3 grants from one page.\n"
        "4) If page is irrelevant or no open grant exists, return {\"grants\":[]}.\n"
        "5) Keep descriptions informative: one to two factual sentences about purpose, target applicant, and funding support.\n"
        f"6) If source_url missing, use {page_url}.\n"
        f"Source: {source_name}\n"
        f"Page URL: {page_url}\n\n"
        f"Page Text:\n{page_text}"
    )

    payload = client.generate_json_sync(
        system_prompt="You are a strict JSON extraction engine.",
        user_prompt=prompt,
        temperature=0.1,
    )
    records: list[ScoutGrantRecord] = []
    for item in payload.get("grants", []):
        if not item.get("source_url"):
            item["source_url"] = page_url
        metadata = item.get("metadata_json") or {}
        metadata["source_name"] = source_name
        item["metadata_json"] = metadata
        records.append(ScoutGrantRecord.model_validate(item))
    return records
