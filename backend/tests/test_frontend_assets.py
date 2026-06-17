from pathlib import Path
import unittest


class FrontendAssetsTest(unittest.TestCase):
    def test_web_demo_assets_exist_and_reference_streaming_api(self):
        root = Path(__file__).resolve().parents[2]
        html = (root / "web" / "index.html").read_text(encoding="utf-8")
        js = (root / "web" / "app.js").read_text(encoding="utf-8")

        self.assertIn("Agent Trace", html)
        self.assertIn("historyList", html)
        self.assertIn("exportMarkdownButton", html)
        self.assertIn("exportPdfButton", html)
        self.assertIn("evidenceList", html)
        self.assertIn("/api/demo/research", js)
        self.assertIn("providers", js)
        self.assertIn("loadHistory", js)
        self.assertIn("exportMarkdown", js)
        self.assertIn("exportPdf", js)

    def test_extension_exposes_agent_trace_and_provider_selector(self):
        root = Path(__file__).resolve().parents[2]
        html = (root / "extension" / "popup.html").read_text(encoding="utf-8")
        js = (root / "extension" / "popup.js").read_text(encoding="utf-8")

        self.assertIn("providerSelect", html)
        self.assertIn("traceList", html)
        self.assertIn("handleStreamEvent", js)


if __name__ == "__main__":
    unittest.main()
