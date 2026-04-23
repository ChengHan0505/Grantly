from __future__ import annotations

import json
import re

from zhipuai import ZhipuAI

from src.scout.schemas import ScoutGrantRecord


def _safe_json_slice(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else "{}"


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
