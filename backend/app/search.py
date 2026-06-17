from __future__ import annotations

from collections.abc import Iterable
from urllib.parse import urlencode

from backend.app.config import Settings
from backend.app.models import SearchResult


def normalize_duckduckgo_results(payload: dict, limit: int = 5) -> list[SearchResult]:
    results: list[SearchResult] = []

    heading = str(payload.get("Heading") or "").strip()
    abstract = str(payload.get("AbstractText") or "").strip()
    url = str(payload.get("AbstractURL") or "").strip()
    if heading and abstract and url:
        results.append(SearchResult(title=heading, url=url, snippet=abstract))

    for topic in _iter_related_topics(payload.get("RelatedTopics") or []):
        if len(results) >= limit:
            break
        text = str(topic.get("Text") or "").strip()
        first_url = str(topic.get("FirstURL") or "").strip()
        if not text or not first_url:
            continue
        title, _, snippet = text.partition(" - ")
        results.append(
            SearchResult(
                title=title.strip() or text[:80],
                url=first_url,
                snippet=snippet.strip() or text,
            )
        )

    return _dedupe(results)[:limit]


def _iter_related_topics(topics: Iterable[dict]) -> Iterable[dict]:
    for topic in topics:
        if "Topics" in topic:
            yield from _iter_related_topics(topic["Topics"])
        else:
            yield topic


def _dedupe(results: list[SearchResult]) -> list[SearchResult]:
    seen: set[str] = set()
    unique: list[SearchResult] = []
    for result in results:
        if result.url in seen:
            continue
        seen.add(result.url)
        unique.append(result)
    return unique


class DuckDuckGoSearchClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        httpx = _load_httpx()
        params = urlencode(
            {
                "q": query,
                "format": "json",
                "no_redirect": "1",
                "no_html": "1",
                "skip_disambig": "1",
            }
        )
        async with httpx.AsyncClient(timeout=self.settings.search_timeout_seconds) as client:
            response = await client.get(f"https://api.duckduckgo.com/?{params}")
            response.raise_for_status()
            return normalize_duckduckgo_results(response.json(), limit=limit)

    async def search_many(self, queries: list[str], limit_per_query: int = 4) -> list[SearchResult]:
        all_results: list[SearchResult] = []
        for query in queries:
            all_results.extend(await self.search(query, limit=limit_per_query))
        return _dedupe(all_results)


def _load_httpx():
    try:
        import httpx
    except ImportError as exc:
        raise RuntimeError("httpx is required. Install dependencies with: python -m pip install -r requirements.txt") from exc
    return httpx
