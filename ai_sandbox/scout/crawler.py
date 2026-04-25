from __future__ import annotations

from collections.abc import Callable
from collections import deque
import time
from urllib import robotparser
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .schemas import ScoutSource


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


def _robots_key(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    return parsed.scheme, parsed.netloc.lower()


def _robots_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}/robots.txt"


def _can_fetch_url(
    url: str,
    user_agent: str,
    robots_cache: dict[tuple[str, str], robotparser.RobotFileParser],
    fetch: Callable[[str], requests.Response],
    errors: list[str],
    source_name: str,
) -> bool:
    key = _robots_key(url)
    parser = robots_cache.get(key)
    if parser is None:
        parser = robotparser.RobotFileParser()
        robots_txt_url = _robots_url(url)
        parser.set_url(robots_txt_url)
        try:
            response = fetch(robots_txt_url)
            if response.status_code < 400:
                parser.parse(response.text.splitlines())
            else:
                parser.parse([])
        except requests.RequestException as exc:
            parser.parse([])
            errors.append(f"{source_name}: failed to read robots.txt {robots_txt_url} ({exc})")
        robots_cache[key] = parser
    return parser.can_fetch(user_agent or "*", url)


def crawl_source(
    source: ScoutSource,
    session: requests.Session,
    timeout_seconds: int,
    max_pages: int,
    max_links_per_page: int,
    max_chars_per_page: int,
    user_agent: str = "*",
    respect_robots_txt: bool = True,
    request_delay_seconds: float = 0.0,
    should_stop: Callable[[], bool] | None = None,
) -> tuple[list[dict], list[str]]:
    queue: deque[str] = deque(source.seed_urls)
    visited: set[str] = set()
    crawled_pages: list[dict] = []
    errors: list[str] = []
    effective_max_pages = min(max_pages, source.max_pages)
    robots_cache: dict[tuple[str, str], robotparser.RobotFileParser] = {}
    last_request_at = 0.0

    def fetch(url: str) -> requests.Response:
        nonlocal last_request_at
        if request_delay_seconds > 0 and last_request_at:
            elapsed = time.monotonic() - last_request_at
            remaining = request_delay_seconds - elapsed
            if remaining > 0:
                time.sleep(remaining)
        response = session.get(url, timeout=timeout_seconds)
        last_request_at = time.monotonic()
        return response

    while queue and len(crawled_pages) < effective_max_pages:
        if should_stop and should_stop():
            errors.append(f"{source.name}: crawl stopped before completing the queue")
            break
        current_url = queue.popleft()
        if current_url in visited:
            continue
        visited.add(current_url)
        if not _is_allowed_url(current_url, source):
            continue

        try:
            if respect_robots_txt and not _can_fetch_url(
                current_url,
                user_agent,
                robots_cache,
                fetch,
                errors,
                source.name,
            ):
                errors.append(f"{source.name}: blocked by robots.txt {current_url}")
                continue

            response = fetch(current_url)
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
