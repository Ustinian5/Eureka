import json
import unittest

from fastapi.testclient import TestClient

from backend.app.main import app


class ApiEventsTest(unittest.TestCase):
    def test_providers_endpoint_returns_presets(self):
        client = TestClient(app)

        response = client.get("/api/providers")

        self.assertEqual(response.status_code, 200)
        provider_ids = {item["id"] for item in response.json()["providers"]}
        self.assertIn("deepseek", provider_ids)
        self.assertIn("qwen", provider_ids)

    def test_demo_research_streams_ndjson_events_without_real_api_key(self):
        client = TestClient(app)

        response = client.post(
            "/api/demo/research",
            json={
                "context": "Model Context Protocol 让 AI 应用连接工具和上下文。",
                "user_query": "对比 MCP 和传统 API",
                "template": "tech_research",
                "provider": "demo",
            },
        )

        self.assertEqual(response.status_code, 200)
        lines = [line for line in response.text.splitlines() if line.strip()]
        events = [json.loads(line) for line in lines]
        self.assertEqual(events[-1]["type"], "done")
        self.assertTrue(any(event["type"] == "trace" for event in events))
        self.assertTrue(any(event["type"] == "token" for event in events))


if __name__ == "__main__":
    unittest.main()
