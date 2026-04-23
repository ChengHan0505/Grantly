from __future__ import annotations

from src.scout.schemas import ScoutGrantRecord


def normalize_record(record: ScoutGrantRecord) -> ScoutGrantRecord:
    data = record.model_dump()
    data["title"] = data["title"].strip()
    data["provider_name"] = data["provider_name"].strip()
    if data.get("status") not in {"open", "closed", "unknown"}:
        data["status"] = "unknown"
    if not data.get("nationality"):
        data["nationality"] = "Malaysia"
    if data.get("amount_min") is not None and data.get("amount_max") is not None:
        if data["amount_min"] > data["amount_max"]:
            data["amount_min"], data["amount_max"] = data["amount_max"], data["amount_min"]
    return ScoutGrantRecord.model_validate(data)
