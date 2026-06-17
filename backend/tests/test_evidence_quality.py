import asyncio
import unittest

from backend.app.agents.citation_verifier import CitationVerifierAgent
from backend.app.agents.scorer import score_evidence_cards
from backend.app.models import EvidenceCard, ResearchRequest, ResearchState


class EvidenceQualityTest(unittest.TestCase):
    def test_score_evidence_cards_adds_confidence_source_type_and_quote(self):
        cards = [
            EvidenceCard(
                title="MCP Official Specification",
                url="https://modelcontextprotocol.io/specification",
                snippet="Model Context Protocol connects AI assistants to tools and context.",
                relevance="",
                query="MCP tools context",
            ),
            EvidenceCard(
                title="Random Forum Thread",
                url="https://forum.example.test/thread",
                snippet="I heard about it.",
                relevance="",
                query="MCP tools context",
            ),
        ]

        scored = score_evidence_cards(cards, ["MCP tools context"])

        self.assertGreater(scored[0].confidence, scored[1].confidence)
        self.assertEqual(scored[0].source_type, "official")
        self.assertIn("Model Context Protocol", scored[0].quote)
        self.assertIn("confidence", scored[0].relevance)

    def test_citation_verifier_marks_missing_citation_in_report(self):
        state = ResearchState(
            request=ResearchRequest(context="MCP context", user_query="MCP vs API"),
            route="deep_research",
            final_report="# Report\nMCP differs from traditional API.",
            evidence_cards=[
                EvidenceCard(
                    title="MCP Overview",
                    url="https://example.test/mcp",
                    snippet="MCP connects tools.",
                    relevance="",
                )
            ],
        )

        verified = asyncio.run(CitationVerifierAgent().run(state))

        self.assertIn("引用校验", verified.final_report)
        self.assertIn("CitationVerifierAgent", [event.agent for event in verified.trace])


if __name__ == "__main__":
    unittest.main()
