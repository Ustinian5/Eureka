from __future__ import annotations

import re

from backend.app.models import ResearchState


class ContextAnalystAgent:
    name = "ContextAnalystAgent"

    async def run(self, state: ResearchState) -> ResearchState:
        text = _compact_text(state.request.context)
        title = state.request.page_title or _infer_title(text)
        sentences = _split_sentences(text)
        state.context_summary = " ".join(sentences[:3])[:800] or text[:800]
        state.key_points = [sentence[:180] for sentence in sentences[:5]]
        state.add_trace(self.name, f"提取网页标题“{title}”，生成 {len(state.key_points)} 条关键观点。")
        return state


def _compact_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _infer_title(text: str) -> str:
    first_line = text.strip().splitlines()[0] if text.strip() else "Untitled Page"
    return first_line.removeprefix("#").strip()[:80] or "Untitled Page"


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。！？.!?])\s+", _compact_text(text))
    return [part.strip() for part in parts if part.strip()]
