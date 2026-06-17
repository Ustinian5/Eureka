from __future__ import annotations

from pathlib import Path
import sys

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "docs" / "report.md"
DEFAULT_TARGET = ROOT / "docs" / "report.pdf"
FONT = Path("C:/Windows/Fonts/simhei.ttf")


def main() -> None:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SOURCE
    target = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_TARGET
    if not source.is_absolute():
        source = ROOT / source
    if not target.is_absolute():
        target = ROOT / target

    pdfmetrics.registerFont(TTFont("SimHei", str(FONT)))
    styles = getSampleStyleSheet()
    normal = ParagraphStyle(
        "EurekaNormal",
        parent=styles["Normal"],
        fontName="SimHei",
        fontSize=10.5,
        leading=16,
        spaceAfter=6,
    )
    heading = ParagraphStyle(
        "EurekaHeading",
        parent=styles["Heading2"],
        fontName="SimHei",
        fontSize=15,
        leading=22,
        spaceBefore=10,
        spaceAfter=8,
    )
    title = ParagraphStyle(
        "EurekaTitle",
        parent=styles["Title"],
        fontName="SimHei",
        fontSize=20,
        leading=28,
        spaceAfter=12,
    )

    story = []
    in_code = False
    for raw_line in source.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if not line:
            story.append(Spacer(1, 4))
            continue
        if in_code:
            story.append(Paragraph(_escape(raw_line), normal))
            continue
        if line.startswith("# "):
            story.append(Paragraph(_escape(line[2:]), title))
        elif line.startswith("## "):
            story.append(Paragraph(_escape(line[3:]), heading))
        elif line.startswith("- "):
            story.append(Paragraph("• " + _escape(line[2:]), normal))
        else:
            story.append(Paragraph(_escape(line), normal))

    target.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(target),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="Eureka Course Report",
    )
    document.build(story)


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("  ", "&nbsp;&nbsp;")
    )


if __name__ == "__main__":
    main()
