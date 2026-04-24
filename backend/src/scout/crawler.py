from __future__ import annotations

from collections import deque
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from src.scout.schemas import ScoutSource


def _is_allowed_url(url: str, source: ScoutSource) -> bool:
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if not any(domain == allowed or domain.endswith(f".{allowed}") for allowed in source.allowed_domains):
        return False
    if not source.allow_url_patterns:
        return True
    return any(pattern.lower() in parsed.path.lower() for pattern in source.allow_url_patterns)


def _extract_text(html: str, selectors: list[str]) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()

    chunks: list[str] = []
    targets = selectors or ["main", "article", "body"]
    for selector in targets:
        for node in soup.select(selector):
            text = node.get_text(" ", strip=True)
            if text:
                chunks.append(text)

    if not chunks:
        body = soup.get_text(" ", strip=True)
        if body:
            chunks.append(body)
    return "\n".join(chunks)


def crawl_source(
    source: ScoutSource,
    session: requests.Session,
    timeout_seconds: int,
    max_pages: int,
    max_links_per_page: int,
    max_chars_per_page: int,
) -> tuple[list[dict], list[str]]:
    queue: deque[str] = deque(source.seed_urls)
    visited: set[str] = set()
    crawled_pages: list[dict] = []
    errors: list[str] = []
    effective_max_pages = min(max_pages, source.max_pages)

    while queue and len(crawled_pages) < effective_max_pages:
        current_url = queue.popleft()
        if current_url in visited:
            continue
        visited.add(current_url)
        if not _is_allowed_url(current_url, source):
            continue

        try:
            response = session.get(current_url, timeout=timeout_seconds)
            response.raise_for_status()
            html = response.text
            text = _extract_text(html, source.selectors)[:max_chars_per_page]
            crawled_pages.append({"url": current_url, "text": text, "html": html})

            soup = BeautifulSoup(html, "html.parser")
            discovered = 0
            for anchor in soup.find_all("a", href=True):
                if discovered >= max_links_per_page:
                    break
                candidate = urljoin(current_url, anchor["href"])
                candidate = candidate.split("#")[0]
                if candidate in visited:
                    continue
                if _is_allowed_url(candidate, source):
                    queue.append(candidate)
                    discovered += 1
        except requests.RequestException as exc:
            errors.append(f"{source.name}: failed to fetch {current_url} ({exc})")

    return crawled_pages, errors
