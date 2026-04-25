from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .schemas import ScoutGrantRecord


def persist_raw_results(results_dir: str, records: list[ScoutGrantRecord]) -> Path:
    target_dir = Path(results_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_path = target_dir / f"run_{timestamp}.json"
    run_path.write_text(
        json.dumps([record.model_dump(mode="json") for record in records], ensure_ascii=True, indent=2),
        encoding="utf-8",
    )
    return run_path


def persist_report(report_path: str, payload: dict) -> None:
    target = Path(report_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")


def read_last_report(report_path: str) -> dict | None:
    target = Path(report_path)
    if not target.exists():
        return None
    return json.loads(target.read_text(encoding="utf-8"))
