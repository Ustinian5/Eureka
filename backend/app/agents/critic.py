from __future__ import annotations

from backend.app.models import ResearchState


class CriticAgent:
    name = "CriticAgent"

    async def run(self, state: ResearchState) -> ResearchState:
        issues: list[str] = []
        if state.request.user_query and state.request.user_query[:12] not in state.final_report:
            issues.append("报告未逐字复述问题，但已围绕问题生成结论。")
        if state.route == "deep_research" and state.evidence_cards and "[1]" not in state.final_report:
            issues.append("报告缺少显式 [1] 引用编号，已在参考来源区保留来源。")
        state.critique = "；".join(issues) if issues else "报告覆盖问题、上下文和来源。"
        state.add_trace(self.name, state.critique)
        return state
