import unittest

from backend.app.export.markdown import export_report_markdown
from backend.app.models import EvidenceCard, ReportRecord, TraceEvent
from backend.app.storage.repositories import ReportRepository


class StorageExportTest(unittest.TestCase):
    def test_repository_saves_report_traces_and_evidence_then_exports_markdown(self):
        repository = ReportRepository(":memory:")
        report = ReportRecord(
            title="MCP Research",
            page_url="https://example.test/article",
            user_query="MCP vs API",
            provider="deepseek",
            model="deepseek-chat",
            route="deep_research",
            final_report="# MCP Research\n结论。[1]",
        )
        traces = [TraceEvent(agent="RouterAgent", content="deep_research")]
        evidence = [
            EvidenceCard(
                title="MCP Overview",
                url="https://example.test/mcp",
                snippet="MCP connects context.",
                relevance="supports comparison",
            )
        ]

        report_id = repository.save_report(report, traces, evidence)
        loaded = repository.get_report(report_id)
        markdown = export_report_markdown(loaded)

        self.assertEqual(loaded.report.title, "MCP Research")
        self.assertEqual(len(loaded.traces), 1)
        self.assertEqual(len(loaded.evidence), 1)
        self.assertIn("模型供应商: deepseek", markdown)
        self.assertIn("https://example.test/mcp", markdown)


if __name__ == "__main__":
    unittest.main()
