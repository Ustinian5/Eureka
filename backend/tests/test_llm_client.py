import unittest

from backend.app.llm_client import collect_stream_delta, sanitize_messages


class LLMClientTest(unittest.TestCase):
    def test_collects_content_and_reasoning_from_openai_compatible_chunk(self):
        content, reasoning = collect_stream_delta(
            {
                "choices": [
                    {
                        "delta": {
                            "reasoning_content": "先判断是否需要搜索。",
                            "content": "需要外部资料。",
                        }
                    }
                ]
            }
        )

        self.assertEqual(reasoning, "先判断是否需要搜索。")
        self.assertEqual(content, "需要外部资料。")

    def test_sanitize_messages_removes_reasoning_content_before_api_call(self):
        sanitized = sanitize_messages(
            [
                {
                    "role": "assistant",
                    "content": "最终回答",
                    "reasoning_content": "隐藏思考",
                    "name": "assistant",
                }
            ]
        )

        self.assertEqual(
            sanitized,
            [{"role": "assistant", "content": "最终回答", "name": "assistant"}],
        )


if __name__ == "__main__":
    unittest.main()
