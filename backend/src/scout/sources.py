from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

import requests

from src.scout.schemas import ScoutSource


def load_sources_from_file(path: str) -> list[ScoutSource]:
    source_path = Path(path)
    if not source_path.exists():
        return []

    payload = json.loads(source_path.read_text(encoding="utf-8"))
    sources = [ScoutSource.model_validate(item) for item in payload]
    return [source for source in sources if source.enabled]


def check_sources_health(
    path: str,
    timeout_seconds: int,
    user_agent: str,
) -> list[dict]:
    sources = load_sources_from_file(path)
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent})
    results: list[dict] = []

    for source in sources:
        source_result = _check_single_source(session, source, timeout_seconds)
        results.append(source_result)
    return results


def check_sources_health_from_sources(
    sources: list[ScoutSource],
    timeout_seconds: int,
    user_agent: str,
) -> list[dict]:
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent})
    results: list[dict] = []
    for source in sources:
        source_result = _check_single_source(session, source, timeout_seconds)
        results.append(source_result)
    return results


def _check_single_source(session: requests.Session, source: ScoutSource, timeout_seconds: int) -> dict:
    source_result = {"name": source.name, "seeds": []}
    for url in source.seed_urls:
        status = "ok"
        status_code = None
        error = None
        try:
            response = session.get(url, timeout=timeout_seconds, allow_redirects=True)
            status_code = response.status_code
            if response.status_code >= 400:
                status = "http_error"
        except requests.RequestException as exc:
            status = "request_failed"
            error = str(exc)

        source_result["seeds"].append(
            {
                "url": url,
                "status": status,
                "status_code": status_code,
                "error": error,
            }
        )
    return source_result


def _collect_urls(payload: object) -> list[str]:
    urls: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key == "url" and isinstance(value, str) and value.startswith(("http://", "https://")):
                urls.append(value)
            urls.extend(_collect_urls(value))
    elif isinstance(payload, list):
        for item in payload:
            urls.extend(_collect_urls(item))
    return urls


def load_sources_from_curated_outputs(paths: list[str]) -> list[ScoutSource]:
    sources: list[ScoutSource] = []
    for path in paths:
        file_path = Path(path)
        if not file_path.exists():
            continue
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        raw_urls = _collect_urls(payload)
        seen: set[str] = set()
        seed_urls: list[str] = []
        for url in raw_urls:
            if url in seen:
                continue
            seen.add(url)
            seed_urls.append(url)
        if not seed_urls:
            continue

        allowed_domains = sorted({urlparse(url).netloc.lower() for url in seed_urls if urlparse(url).netloc})
        allow_url_patterns = sorted(
            {
                urlparse(url).path.rstrip("/") or "/"
                for url in seed_urls
                if urlparse(url).path
            }
        )
        source = ScoutSource(
            name=f"curated:{file_path.stem}",
            seed_urls=seed_urls,
            allowed_domains=allowed_domains,
            allow_url_patterns=allow_url_patterns,
            selectors=["main", "article", ".content", ".entry-content", ".post-content"],
            max_pages=len(seed_urls),
            enabled=True,
        )
        sources.append(source)
    return sources
