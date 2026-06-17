from __future__ import annotations

import json
from collections.abc import AsyncIterator
from dataclasses import asdict

from pydantic import BaseModel, Field

from backend.app.agents.orchestrator import MultiAgentOrchestrator
from backend.app.config import load_settings
from backend.app.export.markdown import export_report_markdown
from backend.app.export.pdf import markdown_to_pdf_bytes
from backend.app.intent import IntentRouter
from backend.app.llm_client import OpenAICompatibleClient
from backend.app.models import ChatResponse, IntentDecision, ReportRecord, ResearchRequest, SearchResult
from backend.app.providers import public_provider_list, resolve_provider_settings
from backend.app.search import DuckDuckGoSearchClient
from backend.app.storage.repositories import ReportRepository
from backend.app.workflow import ResearchWorkflow


class ResearchPayload(BaseModel):
    context: str = Field(min_length=1)
    user_query: str = ""
    page_title: str = ""
    page_url: str = ""
    provider: str = "custom"
    template: str = "summary"


def create_app():
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import StreamingResponse
    except ImportError as exc:
        raise RuntimeError("FastAPI dependencies are missing. Run: python -m pip install -r requirements.txt") from exc

    settings = load_settings()
    app = FastAPI(title="Eureka Research Copilot", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health():
        return {"status": "ok", "model": settings.model}

    @app.get("/api/providers")
    async def providers():
        return {"providers": public_provider_list()}

    @app.post("/api/research")
    async def research(payload: ResearchPayload):
        orchestrator = _build_orchestrator(payload.provider)
        request = ResearchRequest(
            context=payload.context,
            user_query=payload.user_query,
            page_title=payload.page_title,
            page_url=payload.page_url,
            provider=payload.provider,
            template=payload.template,
        )
        return StreamingResponse(
            _stream_and_save(orchestrator, request),
            media_type="application/x-ndjson; charset=utf-8",
        )

    @app.post("/api/demo/research")
    async def demo_research(payload: ResearchPayload):
        orchestrator = MultiAgentOrchestrator(DemoRouter(), DemoLLM(), DemoSearchClient())
        request = ResearchRequest(
            context=payload.context,
            user_query=payload.user_query,
            page_title=payload.page_title or "Eureka Demo Page",
            page_url=payload.page_url,
            provider=payload.provider or "demo",
            template=payload.template,
        )
        return StreamingResponse(
            _stream_and_save(orchestrator, request),
            media_type="application/x-ndjson; charset=utf-8",
        )

    @app.get("/api/reports")
    async def list_reports():
        repository = ReportRepository()
        return {"reports": [asdict(record) for record in repository.list_reports()]}

    @app.get("/api/reports/{report_id}")
    async def get_report(report_id: int):
        repository = ReportRepository()
        loaded = repository.get_report(report_id)
        return {
            "report": asdict(loaded.report),
            "traces": [asdict(item) for item in loaded.traces],
            "evidence": [asdict(item) for item in loaded.evidence],
        }

    @app.get("/api/reports/{report_id}/markdown")
    async def get_report_markdown(report_id: int):
        from fastapi.responses import PlainTextResponse

        repository = ReportRepository()
        return PlainTextResponse(export_report_markdown(repository.get_report(report_id)))

    @app.get("/api/reports/{report_id}/pdf")
    async def get_report_pdf(report_id: int):
        from fastapi.responses import Response

        repository = ReportRepository()
        loaded = repository.get_report(report_id)
        markdown = export_report_markdown(loaded)
        return Response(
            content=markdown_to_pdf_bytes(markdown, loaded.report.title),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="eureka-report-{report_id}.pdf"'},
        )

    @app.delete("/api/reports/{report_id}")
    async def delete_report(report_id: int):
        repository = ReportRepository()
        repository.delete_report(report_id)
        return {"status": "deleted", "id": report_id}

    return app


def _build_workflow() -> ResearchWorkflow:
    settings = load_settings()
    llm = OpenAICompatibleClient(settings)
    return ResearchWorkflow(
        router=IntentRouter(llm),
        llm=llm,
        search_client=DuckDuckGoSearchClient(settings),
    )


def _build_orchestrator(provider: str) -> MultiAgentOrchestrator:
    provider_settings = resolve_provider_settings(provider)
    llm = OpenAICompatibleClient(provider_settings)
    return MultiAgentOrchestrator(
        router=IntentRouter(llm),
        llm=llm,
        search_client=DuckDuckGoSearchClient(load_settings()),
    )


async def _stream_text(workflow: ResearchWorkflow, request: ResearchRequest) -> AsyncIterator[str]:
    async for chunk in workflow.stream(request):
        yield chunk


async def _stream_and_save(orchestrator: MultiAgentOrchestrator, request: ResearchRequest) -> AsyncIterator[str]:
    state = await orchestrator.run(request)
    for event in state.trace:
        yield json.dumps(
            {"type": "trace", "agent": event.agent, "content": event.content, "metadata": event.metadata},
            ensure_ascii=False,
        ) + "\n"
    for chunk in _chunk_text(state.final_report):
        yield json.dumps({"type": "token", "content": chunk}, ensure_ascii=False) + "\n"

    report_id = None
    try:
        settings = resolve_provider_settings(request.provider)
        repository = ReportRepository()
        report_id = repository.save_report(
            ReportRecord(
                title=request.page_title or "Eureka Research Report",
                page_url=request.page_url,
                user_query=request.user_query,
                provider=request.provider,
                model=settings.model,
                route=state.route,
                final_report=state.final_report,
            ),
            state.trace,
            state.evidence_cards,
        )
    except OSError:
        report_id = None

    yield json.dumps(
        {
            "type": "done",
            "report_id": report_id,
            "report": {
                "title": request.page_title or "Eureka Research Report",
                "route": state.route,
                "critique": state.critique,
                "evidence": [asdict(card) for card in state.evidence_cards],
            },
        },
        ensure_ascii=False,
    ) + "\n"


def _chunk_text(text: str, size: int = 80) -> list[str]:
    return [text[index : index + size] for index in range(0, len(text), size)] or [""]


class DemoRouter:
    async def decide(self, request: ResearchRequest) -> IntentDecision:
        query = request.user_query.strip()
        needs_research = any(word in query for word in ["对比", "调研", "搜索", "区别", "外部", "竞品"])
        if needs_research:
            return IntentDecision(
                route="deep_research",
                reason="演示模式识别到对比/调研意图，需要外部证据。",
                search_queries=[query or "Model Context Protocol", "MCP traditional API comparison"],
            )
        return IntentDecision(route="context_answer", reason="演示模式判断网页上下文足够回答。")


class DemoLLM:
    async def complete_chat(self, messages: list[dict], temperature: float = 0.2) -> ChatResponse:
        return ChatResponse(content="demo")

    async def stream_chat(self, messages: list[dict], temperature: float = 0.3) -> AsyncIterator[str]:
        prompt = messages[-1]["content"]
        if "技术调研" in prompt:
            yield "# Final Report\n\n## 结论摘要\nMCP 更适合让 AI 应用连接工具、数据和上下文，传统 API 更适合稳定的点对点业务调用。[1]\n\n"
            yield "## 关键发现\n- MCP 强调上下文协作和工具发现。\n- 传统 API 强调确定接口、请求和响应。\n- 在 Agent 应用中，MCP 能降低工具接入成本。\n\n"
            yield "## 参考来源\n- [1] MCP Overview: https://example.test/mcp\n"
        else:
            yield "# Eureka Summary\n\n当前网页围绕 AI Agent 和上下文工具连接展开，核心价值是减少阅读和调研时的上下文切换。\n"


class DemoSearchClient:
    async def search_many(self, queries: list[str]) -> list[SearchResult]:
        return [
            SearchResult(
                title="MCP Overview",
                url="https://example.test/mcp",
                snippet="MCP connects AI assistants with tools, data sources, and context.",
            ),
            SearchResult(
                title="Traditional API Design",
                url="https://example.test/api",
                snippet="Traditional APIs expose fixed endpoints for predictable application integration.",
            ),
        ]


app = create_app()
