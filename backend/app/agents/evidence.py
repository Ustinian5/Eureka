from __future__ import annotations

from backend.app.models import EvidenceCard, ResearchState, SearchResult
from backend.app.agents.scorer import score_evidence_cards


class SearchEvidenceAgent:
    name = "SearchEvidenceAgent"

    def __init__(self, search_client):
        self.search_client = search_client

    async def run(self, state: ResearchState) -> ResearchState:
        if state.route != "deep_research":
            state.add_trace(self.name, "当前任务不需要外部搜索。")
            return state

        results = await self.search_client.search_many(state.search_queries)
        state.evidence_cards = score_evidence_cards([_to_card(result) for result in results], state.search_queries)
        state.add_trace(self.name, f"检索并整理 {len(state.evidence_cards)} 条证据来源。")
        return state


def _to_card(result: SearchResult) -> EvidenceCard:
    return EvidenceCard(
        title=result.title,
        url=result.url,
        snippet=result.snippet,
        relevance="与用户问题和网页上下文相关",
        query="",
    )
