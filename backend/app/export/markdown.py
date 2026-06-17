from __future__ import annotations

from backend.app.models import LoadedReport


def export_report_markdown(loaded: LoadedReport) -> str:
    report = loaded.report
    trace = "\n".join(f"- **{event.agent}**: {event.content}" for event in loaded.traces)
    evidence = "\n".join(
        f"- [{index}] {card.title}\n  - URL: {card.url}\n  - 摘要: {card.snippet}\n  - 相关性: {card.relevance}"
        f"\n  - 类型: {card.source_type}\n  - 置信度: {card.confidence:.2f}\n  - 引文: {card.quote or card.snippet}"
        for index, card in enumerate(loaded.evidence, start=1)
    )
    return (
        f"# {report.title}\n\n"
        "## 元数据\n\n"
        f"- 页面 URL: {report.page_url or '无'}\n"
        f"- 用户问题: {report.user_query or '总结当前网页'}\n"
        f"- 模型供应商: {report.provider}\n"
        f"- 模型: {report.model}\n"
        f"- 路由: {report.route}\n"
        f"- 创建时间: {report.created_at}\n\n"
        "## Agent 执行过程\n\n"
        f"{trace or '- 无'}\n\n"
        "## 调研报告\n\n"
        f"{report.final_report}\n\n"
        "## 参考来源\n\n"
        f"{evidence or '- 当前网页上下文'}\n"
    )
