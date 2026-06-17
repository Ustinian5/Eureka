import asyncio
import json
import unittest

from backend.app.agents.orchestrator import MultiAgentOrchestrator
from backend.app.models import ResearchRequest, SearchResult


class FakeRouter:
    async def decide(self, request):
        from backend.app.models import IntentDecision

        return IntentDecision(
            route="deep_research",
            reason="needs outside evidence",
            search_queries=["MCP traditional API difference"],
        )


class FakeLLM:
    async def complete_chat(self, messages, temperature=0.2):
        from backend.app.models import ChatResponse

        return ChatResponse(content="MCP 是一种上下文和工具连接协议。")

    async def stream_chat(self, messages, temperature=0.3):
        yield "# Final Report\n"
        yield "MCP 与传统 API 的差异在于上下文协作。[1]"


class FakeSearch:
    async def search_many(self, queries):
        return [
            SearchResult(
                title="MCP Overview",
                url="https://example.test/mcp",
                snippet="MCP connects AI assistants to tools and context.",
            )
        ]


class MultiAgentTest(unittest.TestCase):
    def test_orchestrator_streams_trace_token_and_done_events(self):
        orchestrator = MultiAgentOrchestrator(FakeRouter(), FakeLLM(), FakeSearch())
        request = ResearchRequest(
            context="文章讨论 MCP。",
            user_query="对比 MCP 和传统 API",
            page_title="MCP Article",
            page_url="https://example.test/article",
            template="tech_research",
            provider="deepseek",
        )

        events = asyncio.run(self._collect(orchestrator.stream_events(request)))

        event_types = [event["type"] for event in events]
        agents = [event.get("agent") for event in events if event["type"] == "trace"]
        final = "".join(event["content"] for event in events if event["type"] == "token")

        self.assertIn("trace", event_types)
        self.assertIn("token", event_types)
        self.assertEqual(events[-1]["type"], "done")
        self.assertIn("RouterAgent", agents)
        self.assertIn("ResearchPlannerAgent", agents)
        self.assertIn("SearchEvidenceAgent", agents)
        self.assertIn("CriticAgent", agents)
        self.assertIn("Final Report", final)
        self.assertEqual(events[-1]["report"]["route"], "deep_research")

    def test_ndjson_serialization_outputs_one_json_object_per_line(self):
        orchestrator = MultiAgentOrchestrator(FakeRouter(), FakeLLM(), FakeSearch())
        request = ResearchRequest(context="文章讨论 MCP。", user_query="对比 MCP 和传统 API")

        lines = asyncio.run(self._collect(orchestrator.stream_ndjson(request)))

        self.assertGreater(len(lines), 3)
        for line in lines:
            parsed = json.loads(line)
            self.assertIn("type", parsed)

    async def _collect(self, stream):
        return [item async for item in stream]


if __name__ == "__main__":
    unittest.main()
