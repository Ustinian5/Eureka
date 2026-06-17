import asyncio
import unittest

from backend.app.models import IntentDecision, ResearchRequest, SearchResult
from backend.app.workflow import ResearchWorkflow


class FakeRouter:
    async def decide(self, request):
        return IntentDecision(
            route="deep_research",
            reason="requires external evidence",
            search_queries=["MCP protocol"],
        )


class FakeSearchClient:
    async def search_many(self, queries):
        return [
            SearchResult(
                title="MCP Spec",
                url="https://example.test/spec",
                snippet="MCP standardizes context and tool connections.",
            )
        ]


class FakeLLMClient:
    def __init__(self):
        self.messages = None

    async def stream_chat(self, messages):
        self.messages = messages
        yield "## 结论\n"
        yield "MCP 适合工具上下文集成。[1]"


class WorkflowTest(unittest.TestCase):
    def test_deep_research_stream_includes_reference_context(self):
        llm = FakeLLMClient()
        workflow = ResearchWorkflow(FakeRouter(), llm, FakeSearchClient())
        request = ResearchRequest(context="文章提到 MCP。", user_query="对比传统 API")

        chunks = asyncio.run(self._collect(workflow.stream(request)))

        self.assertEqual("".join(chunks), "## 结论\nMCP 适合工具上下文集成。[1]")
        prompt = llm.messages[-1]["content"]
        self.assertIn("https://example.test/spec", prompt)
        self.assertIn("MCP standardizes context", prompt)

    async def _collect(self, stream):
        return [chunk async for chunk in stream]


if __name__ == "__main__":
    unittest.main()
