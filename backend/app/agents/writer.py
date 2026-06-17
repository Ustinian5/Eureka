from __future__ import annotations

from backend.app.models import ResearchState


TEMPLATE_LABELS = {
    "summary": "网页总结",
    "study_note": "课程学习笔记",
    "tech_research": "技术调研报告",
    "product_compare": "产品/竞品分析",
    "paper_reading": "论文阅读笔记",
}


class ReportWriterAgent:
    name = "ReportWriterAgent"

    def __init__(self, llm):
        self.llm = llm

    async def run(self, state: ResearchState) -> ResearchState:
        prompt = _build_prompt(state)
        chunks: list[str] = []
        async for chunk in self.llm.stream_chat(
            [
                {"role": "system", "content": "你是 Eureka 的报告写作智能体，输出中文 Markdown。"},
                {"role": "user", "content": prompt},
            ]
        ):
            chunks.append(chunk)
        state.draft_report = "".join(chunks).strip() or _fallback_report(state)
        state.final_report = state.draft_report
        state.add_trace(self.name, f"生成“{TEMPLATE_LABELS.get(state.request.template, '结构化')}”报告草稿。")
        return state


def _build_prompt(state: ResearchState) -> str:
    evidence = "\n\n".join(
        f"[{index}] {card.title}\nURL: {card.url}\n类型: {card.source_type}\n置信度: {card.confidence:.2f}\n引文: {card.quote or card.snippet}\n摘要: {card.snippet}"
        for index, card in enumerate(state.evidence_cards, start=1)
    )
    return (
        f"报告模板：{TEMPLATE_LABELS.get(state.request.template, state.request.template)}\n"
        f"网页标题：{state.request.page_title}\n"
        f"网页 URL：{state.request.page_url}\n"
        f"用户问题：{state.request.user_query or '总结当前网页'}\n"
        f"路由：{state.route}，原因：{state.route_reason}\n\n"
        f"网页摘要：\n{state.context_summary}\n\n"
        f"关键观点：\n" + "\n".join(f"- {point}" for point in state.key_points) + "\n\n"
        f"证据来源：\n{evidence or '无外部证据，仅基于网页上下文。'}\n\n"
        "请输出结构化 Markdown，包含结论摘要、关键发现、行动建议和参考来源。"
    )


def _fallback_report(state: ResearchState) -> str:
    source_lines = [
        f"- [{index}] {card.title}: {card.url} (confidence={card.confidence:.2f})"
        for index, card in enumerate(state.evidence_cards, start=1)
    ]
    return (
        "# Eureka 调研报告\n\n"
        f"## 结论摘要\n{state.context_summary or '已完成网页上下文分析。'}\n\n"
        "## 关键发现\n"
        + "\n".join(f"- {point}" for point in state.key_points)
        + "\n\n## 参考来源\n"
        + ("\n".join(source_lines) if source_lines else "- 当前网页上下文")
    )
