from __future__ import annotations

import json
from collections.abc import AsyncIterator

from backend.app.agents.context_analyst import ContextAnalystAgent
from backend.app.agents.critic import CriticAgent
from backend.app.agents.citation_verifier import CitationVerifierAgent
from backend.app.agents.evidence import SearchEvidenceAgent
from backend.app.agents.planner import ResearchPlannerAgent
from backend.app.agents.writer import ReportWriterAgent
from backend.app.models import ResearchRequest, ResearchState, TraceEvent


class MultiAgentOrchestrator:
    def __init__(self, router, llm, search_client):
        self.router = router
        self.context_analyst = ContextAnalystAgent()
        self.planner = ResearchPlannerAgent()
        self.evidence = SearchEvidenceAgent(search_client)
        self.writer = ReportWriterAgent(llm)
        self.critic = CriticAgent()
        self.citation_verifier = CitationVerifierAgent()

    async def run(self, request: ResearchRequest) -> ResearchState:
        state = ResearchState(request=request)
        decision = await self.router.decide(request)
        state.route = decision.route
        state.route_reason = decision.reason
        state.search_queries = list(decision.search_queries)
        state.add_trace("RouterAgent", f"判断为 {state.route}：{state.route_reason or '按上下文和问题自动判断'}")

        await self.context_analyst.run(state)
        if state.route == "deep_research":
            await self.planner.run(state)
            await self.evidence.run(state)
        else:
            state.add_trace("ResearchPlannerAgent", "上下文足够回答，跳过外部调研计划。")
            state.add_trace("SearchEvidenceAgent", "未调用搜索工具。")

        await self.writer.run(state)
        await self.citation_verifier.run(state)
        await self.critic.run(state)
        return state

    async def stream_events(self, request: ResearchRequest) -> AsyncIterator[dict]:
        state = await self.run(request)
        for event in state.trace:
            yield _trace_payload(event)
        for chunk in _chunk_text(state.final_report):
            yield {"type": "token", "content": chunk}
        yield {"type": "done", "report": _report_payload(state)}

    async def stream_ndjson(self, request: ResearchRequest) -> AsyncIterator[str]:
        async for event in self.stream_events(request):
            yield json.dumps(event, ensure_ascii=False) + "\n"


def _trace_payload(event: TraceEvent) -> dict:
    return {
        "type": "trace",
        "agent": event.agent,
        "content": event.content,
        "metadata": event.metadata,
    }


def _chunk_text(text: str, size: int = 80) -> list[str]:
    if not text:
        return [""]
    return [text[index : index + size] for index in range(0, len(text), size)]


def _report_payload(state: ResearchState) -> dict:
    return {
        "title": state.request.page_title or "Eureka Research Report",
        "page_url": state.request.page_url,
        "user_query": state.request.user_query,
        "provider": state.request.provider,
        "template": state.request.template,
        "route": state.route,
        "critique": state.critique,
        "evidence": [
            {
                "title": card.title,
                "url": card.url,
                "snippet": card.snippet,
                "relevance": card.relevance,
                "quote": card.quote,
                "source_type": card.source_type,
                "confidence": card.confidence,
            }
            for card in state.evidence_cards
        ],
    }
