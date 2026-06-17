from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser


@dataclass(slots=True)
class FetchedPage:
    url: str
    title: str
    text: str


class _ReadableHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self._skip_depth = 0
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg"}:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg"} and self._skip_depth:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self.title_parts.append(text)
        elif not self._skip_depth:
            self.text_parts.append(text)


def extract_main_text(html: str, url: str) -> FetchedPage:
    parser = _ReadableHTMLParser()
    parser.feed(html)
    title = _compact(" ".join(parser.title_parts)) or url
    text = _compact(" ".join(parser.text_parts))
    return FetchedPage(url=url, title=title[:120], text=text)


def extract_quote(text: str, keywords: list[str], max_length: int = 220) -> str:
    sentences = [item.strip() for item in re.split(r"(?<=[。！？.!?])\s+", _compact(text)) if item.strip()]
    lowered_keywords = [keyword.lower() for keyword in keywords if keyword]
    best = ""
    best_score = -1
    for sentence in sentences or [_compact(text)]:
        lower = sentence.lower()
        score = sum(1 for keyword in lowered_keywords if keyword in lower)
        if score > best_score:
            best = sentence
            best_score = score
    return best[:max_length]


async def fetch_page_text(url: str, timeout: float = 8.0) -> FetchedPage:
    httpx = _load_httpx()
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        response = await client.get(url, headers={"User-Agent": "EurekaResearchBot/0.1"})
        response.raise_for_status()
        return extract_main_text(response.text, str(response.url))


def _compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _load_httpx():
    try:
        import httpx
    except ImportError as exc:
        raise RuntimeError("httpx is required. Install dependencies from environment.yml.") from exc
    return httpx
