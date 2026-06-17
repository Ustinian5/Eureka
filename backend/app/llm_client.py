from __future__ import annotations

import json
from collections.abc import AsyncIterator, Iterable
from typing import Any

from backend.app.config import Settings
from backend.app.models import ChatResponse


ALLOWED_MESSAGE_FIELDS = {"role", "content", "name", "tool_call_id", "tool_calls"}


def sanitize_messages(messages: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    sanitized: list[dict[str, Any]] = []
    for message in messages:
        sanitized.append(
            {
                key: value
                for key, value in message.items()
                if key in ALLOWED_MESSAGE_FIELDS and value is not None
            }
        )
    return sanitized


def collect_stream_delta(payload: dict[str, Any]) -> tuple[str, str]:
    choices = payload.get("choices") or []
    if not choices:
        return "", ""

    delta = choices[0].get("delta") or {}
    content = delta.get("content") or ""
    reasoning = delta.get("reasoning_content") or ""
    return content, reasoning


def _parse_sse_data(line: str) -> dict[str, Any] | None:
    if not line.startswith("data:"):
        return None
    data = line.removeprefix("data:").strip()
    if not data or data == "[DONE]":
        return None
    return json.loads(data)


class OpenAICompatibleClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.last_reasoning_content = ""

    async def complete_chat(self, messages: list[dict[str, Any]], temperature: float = 0.2) -> ChatResponse:
        httpx = _load_httpx()
        payload = {
            "model": self.settings.model,
            "messages": sanitize_messages(messages),
            "temperature": temperature,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=self.settings.llm_timeout_seconds) as client:
            response = await client.post(
                f"{self.settings.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        message = data["choices"][0]["message"]
        return ChatResponse(
            content=message.get("content") or "",
            reasoning_content=message.get("reasoning_content") or "",
        )

    async def stream_chat(self, messages: list[dict[str, Any]], temperature: float = 0.3) -> AsyncIterator[str]:
        httpx = _load_httpx()
        self.last_reasoning_content = ""
        payload = {
            "model": self.settings.model,
            "messages": sanitize_messages(messages),
            "temperature": temperature,
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=self.settings.llm_timeout_seconds) as client:
            async with client.stream(
                "POST",
                f"{self.settings.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    parsed = _parse_sse_data(line)
                    if parsed is None:
                        continue
                    content, reasoning = collect_stream_delta(parsed)
                    if reasoning:
                        self.last_reasoning_content += reasoning
                    if content:
                        yield content

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.settings.api_key:
            headers["Authorization"] = f"Bearer {self.settings.api_key}"
        return headers


def _load_httpx():
    try:
        import httpx
    except ImportError as exc:
        raise RuntimeError("httpx is required. Install dependencies with: python -m pip install -r requirements.txt") from exc
    return httpx
