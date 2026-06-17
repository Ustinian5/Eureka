import json
import unittest

from fastapi.testclient import TestClient

from backend.app.main import app


class ApiExportTest(unittest.TestCase):
    def test_demo_research_saves_report_and_exports_markdown_and_pdf(self):
        client = TestClient(app)

        response = client.post(
            "/api/demo/research",
            json={
                "context": "MCP connects AI apps with tools and context.",
                "user_query": "对比 MCP 和传统 API",
                "provider": "demo",
                "template": "tech_research",
            },
        )
        events = [json.loads(line) for line in response.text.splitlines() if line.strip()]
        report_id = events[-1]["report_id"]

        markdown = client.get(f"/api/reports/{report_id}/markdown")
        pdf = client.get(f"/api/reports/{report_id}/pdf")

        self.assertEqual(markdown.status_code, 200)
        self.assertIn("MCP", markdown.text)
        self.assertEqual(pdf.status_code, 200)
        self.assertEqual(pdf.headers["content-type"], "application/pdf")
        self.assertGreater(len(pdf.content), 1000)


if __name__ == "__main__":
    unittest.main()
