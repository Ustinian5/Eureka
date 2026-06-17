from __future__ import annotations

import re
from urllib.parse import urlparse

from backend.app.models import EvidenceCard
from backend.app.tools.fetcher import extract_quote


OFFICIAL_HINTS = ("official", "docs", "documentation", "spec", "developer", "github.com")
AUTHORITATIVE_DOMAINS = (
    "modelcontextprotocol.io",
    "openai.com",
    "deepseek.com",
    "kimi.com",
    "moonshot.cn",
    "bigmodel.cn",
    "google.com",
    "minimaxi.com",
    "github.com",
)


def score_evidence_cards(cards: list[EvidenceCard], queries: list[str]) -> list[EvidenceCard]:
    keywords = _keywords(" ".join(queries))
    scored = []
    for card in cards:
        card.source_type = classify_source(card.url, card.title)
        card.quote = card.quote or extract_quote(card.snippet, keywords)
        card.confidence = round(_score(card, keywords), 2)
        card.relevance = f"{card.relevance or '相关证据'}; confidence={card.confidence:.2f}; source_type={card.source_type}"
        scored.append(card)
    return sorted(scored, key=lambda item: item.confidence, reverse=True)


def classify_source(url: str, title: str) -> str:
    host = urlparse(url).netloc.lower()
    text = f"{url} {title}".lower()
    if any(domain in host for domain in AUTHORITATIVE_DOMAINS) or any(hint in text for hint in OFFICIAL_HINTS):
        return "official"
    if any(part in host for part in ("arxiv", "acm.org", "ieee.org", "semanticscholar")):
        return "paper"
    if any(part in host for part in ("blog", "medium.com", "substack.com")):
        return "blog"
    if any(part in host for part in ("forum", "reddit", "zhihu")):
        return "community"
    return "web"


def _score(card: EvidenceCard, keywords: list[str]) -> float:
    text = f"{card.title} {card.snippet} {card.quote}".lower()
    overlap = sum(1 for keyword in keywords if keyword in text)
    overlap_score = min(0.55, overlap * 0.12)
    source_score = {"official": 0.3, "paper": 0.24, "blog": 0.16, "web": 0.12, "community": 0.06}.get(card.source_type, 0.1)
    length_score = 0.15 if len(card.snippet) >= 60 else 0.06
    return min(0.99, 0.15 + overlap_score + source_score + length_score)


def _keywords(text: str) -> list[str]:
    return [item.lower() for item in re.findall(r"[\w\u4e00-\u9fff]{2,}", text)][:20]
