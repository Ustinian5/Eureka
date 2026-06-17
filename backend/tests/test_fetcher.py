import unittest

from backend.app.tools.fetcher import extract_main_text, extract_quote


class FetcherTest(unittest.TestCase):
    def test_extract_main_text_removes_scripts_and_keeps_readable_body(self):
        html = """
        <html><head><title>MCP Guide</title><script>ignore()</script></head>
        <body><nav>Menu</nav><article><h1>MCP Guide</h1><p>MCP connects AI tools.</p></article></body></html>
        """

        page = extract_main_text(html, "https://example.test/mcp")

        self.assertEqual(page.title, "MCP Guide")
        self.assertIn("MCP connects AI tools.", page.text)
        self.assertNotIn("ignore", page.text)

    def test_extract_quote_prefers_sentence_with_keywords(self):
        quote = extract_quote(
            "Traditional APIs expose fixed endpoints. MCP connects AI tools and context dynamically.",
            ["MCP", "context"],
        )

        self.assertEqual(quote, "MCP connects AI tools and context dynamically.")


if __name__ == "__main__":
    unittest.main()
