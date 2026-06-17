from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "screenshots"
FONT = Path("C:/Windows/Fonts/msyh.ttc")
BOLD = Path("C:/Windows/Fonts/msyhbd.ttc")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    web = _draw_web_demo()
    trace = _draw_trace()
    web.save(OUT / "web-demo.png")
    trace.save(OUT / "agent-trace.png")
    frames = [_draw_frame(step) for step in range(4)]
    frames[0].save(
        OUT / "demo.gif",
        save_all=True,
        append_images=frames[1:],
        duration=650,
        loop=0,
    )


def _font(size: int, bold: bool = False):
    path = BOLD if bold and BOLD.is_file() else FONT
    return ImageFont.truetype(str(path), size) if path.is_file() else ImageFont.load_default()


def _draw_web_demo() -> Image.Image:
    image = Image.new("RGB", (1400, 820), "#eef2f7")
    draw = ImageDraw.Draw(image)
    _panel(draw, 20, 20, 330, 780, "输入区")
    _panel(draw, 370, 20, 250, 780, "历史报告")
    _panel(draw, 640, 20, 300, 780, "Agent Trace")
    _panel(draw, 960, 20, 420, 780, "最终报告")

    _text(draw, 48, 74, "Eureka", 30, True)
    _text(draw, 48, 118, "多 Agent 网页调研工作台", 17)
    _button(draw, 48, 682, 145, 44, "运行离线演示")
    _button(draw, 205, 682, 120, 44, "调用真实模型")

    for i in range(4):
        _button(draw, 395, 82 + i * 58, 195, 42, f"#{12 - i} MCP 调研报告")

    trace_items = ["RouterAgent", "ContextAnalystAgent", "ResearchPlannerAgent", "SearchEvidenceAgent", "ReportWriterAgent", "CitationVerifierAgent", "CriticAgent"]
    for i, item in enumerate(trace_items):
        y = 82 + i * 88
        _text(draw, 670, y, item, 16, True, "#1f6feb")
        _text(draw, 670, y + 26, "完成当前步骤并写入 Trace", 13, False, "#344054")

    report = [
        "# Final Report",
        "## 结论摘要",
        "MCP 更适合让 AI 应用连接工具、数据和上下文。",
        "传统 API 更适合稳定的点对点业务调用。[1]",
        "",
        "## 证据来源",
        "[1] MCP Overview · official · confidence 0.84",
    ]
    for i, line in enumerate(report):
        _text(draw, 990, 78 + i * 34, line, 15, i in {0, 1, 5})

    return image


def _draw_trace() -> Image.Image:
    image = Image.new("RGB", (520, 820), "#ffffff")
    draw = ImageDraw.Draw(image)
    _text(draw, 30, 28, "Agent Trace", 28, True)
    items = [
        ("RouterAgent", "判断为 deep_research"),
        ("ContextAnalystAgent", "提取网页摘要和关键观点"),
        ("ResearchPlannerAgent", "生成子问题和检索词"),
        ("SearchEvidenceAgent", "整理证据卡并评分"),
        ("ReportWriterAgent", "生成结构化 Markdown"),
        ("CitationVerifierAgent", "检查引用编号"),
        ("CriticAgent", "审查报告完整性"),
    ]
    for i, (agent, desc) in enumerate(items):
        y = 90 + i * 96
        draw.rounded_rectangle([28, y, 492, y + 72], radius=10, fill="#f8fafc", outline="#d6deeb")
        _text(draw, 48, y + 12, agent, 17, True, "#1f6feb")
        _text(draw, 48, y + 40, desc, 14, False, "#344054")
    return image


def _draw_frame(step: int) -> Image.Image:
    image = Image.new("RGB", (760, 420), "#eef2f7")
    draw = ImageDraw.Draw(image)
    steps = ["读取网页上下文", "Agent 规划和检索", "生成带引用报告", "保存并导出"]
    _text(draw, 40, 36, "Eureka Demo", 32, True)
    for i, label in enumerate(steps):
        x = 60 + i * 170
        color = "#1f6feb" if i <= step else "#c7d0dd"
        draw.ellipse([x, 130, x + 60, 190], fill=color)
        _text(draw, x - 24, 210, label, 15, i <= step)
    _text(draw, 70, 310, f"当前步骤：{steps[step]}", 24, True, "#1d2433")
    return image


def _panel(draw, x, y, w, h, title):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=12, fill="#ffffff", outline="#d6deeb")
    _text(draw, x + 22, y + 20, title, 20, True)


def _button(draw, x, y, w, h, label):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=8, fill="#1f6feb")
    _text(draw, x + 14, y + 12, label, 14, True, "#ffffff")


def _text(draw, x, y, text, size, bold=False, fill="#1d2433"):
    draw.text((x, y), text, font=_font(size, bold), fill=fill)


if __name__ == "__main__":
    main()
