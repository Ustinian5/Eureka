from __future__ import annotations

from backend.app.models import ResearchState


class ResearchPlannerAgent:
    name = "ResearchPlannerAgent"

    async def run(self, state: ResearchState) -> ResearchState:
        query = state.request.user_query.strip() or "总结当前网页"
        state.sub_questions = [
            f"当前网页对“{query}”提供了哪些信息？",
            f"外部资料如何解释“{query}”的背景？",
            f"有哪些可验证的事实或来源支持结论？",
        ]
        if not state.search_queries:
            state.search_queries = [query, f"{query} background", f"{query} comparison"]
        state.add_trace(self.name, f"拆解出 {len(state.sub_questions)} 个子问题和 {len(state.search_queries)} 个检索词。")
        return state
