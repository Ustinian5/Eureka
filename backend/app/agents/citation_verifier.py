from __future__ import annotations

import re

from backend.app.models import ResearchState


class CitationVerifierAgent:
    name = "CitationVerifierAgent"

    async def run(self, state: ResearchState) -> ResearchState:
        if not state.evidence_cards:
            state.add_trace(self.name, "无外部证据，引用校验跳过。")
            return state

        expected = {str(index) for index in range(1, len(state.evidence_cards) + 1)}
        found = set(re.findall(r"\[(\d+)\]", state.final_report))
        missing = sorted(expected - found, key=int)
        if missing:
            note = "## 引用校验\n\n以下来源已纳入证据表，但正文缺少显式引用编号：" + ", ".join(f"[{item}]" for item in missing)
            state.final_report = state.final_report.rstrip() + "\n\n" + note + "\n"
            state.add_trace(self.name, f"发现缺少引用编号：{', '.join(missing)}，已追加引用校验说明。")
        else:
            state.add_trace(self.name, "报告中的关键外部来源均有引用编号。")
        return state
