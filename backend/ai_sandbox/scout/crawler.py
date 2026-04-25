from __future__ import annotations

from collections.abc import Callable
from collections import deque
import time
from urllib import robotparser
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .schemas import ScoutSource


HIGH_VALUE_LINK_TERMS = (
    "grant",
    "fund",
    "funding",
    "programme",
    "program",
    "application",
    "apply",
    "incentive",
)

LOW_VALUE_LINK_TERMS = (
    "privacy",
    "terms",
    "cookie",
    "login",
    "sign-in",
    "signin",
    "contact",
    "career",
    "news",
    "media",
    "event",
)


def _is_allowed_url(url: str, source: ScoutSource) -> bool:
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if not any(domain == allowed or domain.endswith(f".{allowed}") for allowed in source.allowed_domains):
        return False
    if not source.allow_url_patterns:
        return True
    return any(pattern.lower() in parsed.path.lower() for pattern in source.allow_url_patterns)


def _extract_metadata(html: str) -> dict[str, str | None]:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else None
    description_node = soup.find("meta", attrs={"name": "description"}) or soup.find(
        "meta",
        attrs={"property": "og:description"},
    )
    description = description_node.get("content", "").strip() if description_node else None
    h1 = soup.find("h1")
    heading = h1.get_text(" ", strip=True) if h1 else None
    return {
        "title": title or None,
        "description": description or None,
        "heading": heading or None,
    }


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


def _link_score(url: str, anchor_text: str) -> int:
    parsed = urlparse(url)
    haystack = f"{parsed.path} {parsed.query} {anchor_text}".lower()
    score = 0
    for term in HIGH_VALUE_LINK_TERMS:
        if term in haystack:
            score += 4
    for term in LOW_VALUE_LINK_TERMS:
        if term in haystack:
            score -= 6
    if parsed.path.rstrip("/").count("/") <= 1:
        score += 1
    if parsed.query:
        score -= 1
    return score


def _discover_links(
    html: str,
    current_url: str,
    source: ScoutSource,
    visited: set[str],
    max_links_per_page: int,
) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    candidates: dict[str, tuple[int, int]] = {}
    for index, anchor in enumerate(soup.find_all("a", href=True)):
        candidate = urljoin(current_url, anchor["href"]).split("#")[0]
        if candidate in visited or not _is_allowed_url(candidate, source):
            continue
        score = _link_score(candidate, anchor.get_text(" ", strip=True))
        previous = candidates.get(candidate)
        if previous is None or score > previous[0]:
            candidates[candidate] = (score, index)

    ordered = sorted(candidates.items(), key=lambda item: (-item[1][0], item[1][1]))
    return [url for url, _score in ordered[:max_links_per_page]]


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
            metadata = _extract_metadata(html)
            text = _extract_text(html, source.selectors)[:max_chars_per_page]
            crawled_pages.append({"url": current_url, "text": text, "html": html, "metadata": metadata})

            for candidate in _discover_links(html, current_url, source, visited, max_links_per_page):
                queue.append(candidate)
        except requests.RequestException as exc:
            errors.append(f"{source.name}: failed to fetch {current_url} ({exc})")

    return crawled_pages, errors
