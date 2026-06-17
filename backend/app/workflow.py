from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol

from backend.app.models import IntentDecision, ResearchRequest, SearchResult


class Router(Protocol):
    async def decide(self, request: ResearchRequest) -> IntentDecision: ...


class StreamingLLM(Protocol):
    async def stream_chat(self, messages: list[dict], temperature: float = 0.3) -> AsyncIterator[str]: ...


class Searcher(Protocol):
    async def search_many(self, queries: list[str]) -> list[SearchResult]: ...


class ResearchWorkflow:
    def __init__(self, router: Router, llm: StreamingLLM, search_client: Searcher):
        self.router = router
        self.llm = llm
        self.search_client = search_client

    async def stream(self, request: ResearchRequest) -> AsyncIterator[str]:
        decision = await self.router.decide(request)
        if decision.route == "deep_research":
            async for chunk in self._stream_deep_research(request, decision):
                yield chunk
            return

        async for chunk in self._stream_context_answer(request):
            yield chunk

    async def _stream_context_answer(self, request: ResearchRequest) -> AsyncIterator[str]:
        user_task = request.user_query.strip() or "请总结当前网页，提炼核心观点、关键事实和可行动结论。"
        messages = [
            {
                "role": "system",
                "content": "你是 Eureka，一个严谨的中文网页阅读助手。只基于用户提供的网页上下文回答。",
            },
            {
                "role": "user",
                "content": f"网页上下文：\n{request.context}\n\n用户任务：\n{user_task}",
            },
        ]
        async for chunk in self.llm.stream_chat(messages):
            yield chunk

    async def _stream_deep_research(self, request: ResearchRequest, decision: IntentDecision) -> AsyncIterator[str]:
        queries = decision.search_queries or [request.user_query]
        results = await self.search_client.search_many(queries)
        references = _format_references(results)
        prompt = (
            "请基于网页上下文和外部参考资料，生成结构化 Markdown 研报。\n"
            "必须包含：结论摘要、背景、关键发现、与当前网页的关系、参考来源。\n"
            "引用外部资料时使用 [1]、[2] 这样的编号。\n\n"
            f"网页上下文：\n{request.context}\n\n"
            f"用户问题：\n{request.user_query}\n\n"
            f"路由原因：\n{decision.reason}\n\n"
            f"外部参考资料：\n{references if references else '未检索到可靠外部资料，请明确说明。'}"
        )
        messages = [
            {
                "role": "system",
                "content": "你是 Eureka，一个会整合网页上下文与检索资料的中文深度调研助手。",
            },
            {"role": "user", "content": prompt},
        ]
        async for chunk in self.llm.stream_chat(messages):
            yield chunk


def _format_references(results: list[SearchResult]) -> str:
    lines: list[str] = []
    for index, result in enumerate(results, start=1):
        lines.append(f"[{index}] {result.title}\nURL: {result.url}\n摘要: {result.snippet}")
    return "\n\n".join(lines)
