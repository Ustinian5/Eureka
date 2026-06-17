from __future__ import annotations

import json
from typing import Protocol

from backend.app.models import IntentDecision, ResearchRequest


VALID_ROUTES = {"context_answer", "deep_research"}


class ChatCompleter(Protocol):
    async def complete_chat(self, messages: list[dict], temperature: float = 0.2): ...


def parse_intent_decision(raw: str) -> IntentDecision:
    if not raw.strip():
        return IntentDecision(route="context_answer", reason="no user query")

    try:
        payload = json.loads(_extract_json(raw))
    except json.JSONDecodeError:
        return IntentDecision(route="context_answer", reason="router returned non-json")

    route = payload.get("route")
    if route not in VALID_ROUTES:
        return IntentDecision(route="context_answer", reason="unknown route")

    queries = payload.get("search_queries") or []
    clean_queries = [str(query).strip() for query in queries if str(query).strip()]
    if route == "context_answer":
        clean_queries = []

    return IntentDecision(
        route=route,
        reason=str(payload.get("reason") or ""),
        search_queries=clean_queries[:5],
    )


def _extract_json(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end >= start:
        return text[start : end + 1]
    return text


class IntentRouter:
    def __init__(self, llm: ChatCompleter):
        self.llm = llm

    async def decide(self, request: ResearchRequest) -> IntentDecision:
        if not request.user_query.strip():
            return IntentDecision(route="context_answer", reason="empty user query")

        prompt = (
            "你是 Eureka 的意图路由器。只输出 JSON，不要输出解释。\n"
            "如果用户问题可以完全由网页上下文回答，route=context_answer。\n"
            "如果需要检索外部资料、对比全网信息、解释上下文未展开概念，route=deep_research。\n"
            "JSON 格式：{\"route\":\"context_answer|deep_research\",\"reason\":\"...\",\"search_queries\":[\"...\"]}\n\n"
            f"网页上下文：\n{request.context[:6000]}\n\n"
            f"用户问题：\n{request.user_query}"
        )
        response = await self.llm.complete_chat(
            [
                {"role": "system", "content": "You are a strict JSON intent router."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
        decision = parse_intent_decision(response.content)
        if decision.route == "deep_research" and not decision.search_queries:
            decision.search_queries.append(request.user_query.strip())
        return decision
