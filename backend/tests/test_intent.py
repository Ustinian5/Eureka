import unittest

from backend.app.intent import parse_intent_decision


class IntentParsingTest(unittest.TestCase):
    def test_parse_deep_research_decision_from_json(self):
        decision = parse_intent_decision(
            '{"route":"deep_research","reason":"needs external comparison","search_queries":["MCP vs REST API","MCP protocol"]}'
        )

        self.assertEqual(decision.route, "deep_research")
        self.assertEqual(decision.reason, "needs external comparison")
        self.assertEqual(decision.search_queries, ["MCP vs REST API", "MCP protocol"])

    def test_parse_context_answer_when_query_is_empty(self):
        decision = parse_intent_decision("")

        self.assertEqual(decision.route, "context_answer")
        self.assertEqual(decision.search_queries, [])

    def test_unknown_route_falls_back_to_context_answer(self):
        decision = parse_intent_decision('{"route":"other","search_queries":["ignored"]}')

        self.assertEqual(decision.route, "context_answer")
        self.assertEqual(decision.search_queries, [])


if __name__ == "__main__":
    unittest.main()
