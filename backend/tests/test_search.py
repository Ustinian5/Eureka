import unittest

from backend.app.search import normalize_duckduckgo_results


class SearchTest(unittest.TestCase):
    def test_normalizes_instant_answer_and_related_topics(self):
        results = normalize_duckduckgo_results(
            {
                "Heading": "Model Context Protocol",
                "AbstractText": "MCP connects AI systems with tools.",
                "AbstractURL": "https://example.test/mcp",
                "RelatedTopics": [
                    {
                        "Text": "MCP specification - protocol details",
                        "FirstURL": "https://example.test/spec",
                    },
                    {
                        "Topics": [
                            {
                                "Text": "API - application programming interface",
                                "FirstURL": "https://example.test/api",
                            }
                        ]
                    },
                ],
            },
            limit=3,
        )

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].title, "Model Context Protocol")
        self.assertEqual(results[1].url, "https://example.test/spec")
        self.assertEqual(results[2].title, "API")


if __name__ == "__main__":
    unittest.main()
