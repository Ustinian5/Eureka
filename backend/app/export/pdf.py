from __future__ import annotations

from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


FONT = Path("C:/Windows/Fonts/simhei.ttf")


def markdown_to_pdf_bytes(markdown: str, title: str = "Eureka Report") -> bytes:
    if FONT.is_file():
        pdfmetrics.registerFont(TTFont("SimHei", str(FONT)))
        font_name = "SimHei"
    else:
        font_name = "Helvetica"

    styles = getSampleStyleSheet()
    normal = ParagraphStyle("EurekaNormal", parent=styles["Normal"], fontName=font_name, fontSize=10, leading=15)
    heading = ParagraphStyle("EurekaHeading", parent=styles["Heading2"], fontName=font_name, fontSize=14, leading=20, spaceBefore=8)
    title_style = ParagraphStyle("EurekaTitle", parent=styles["Title"], fontName=font_name, fontSize=18, leading=26)

    story = []
    in_code = False
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if not line:
            story.append(Spacer(1, 4))
        elif line.startswith("# "):
            story.append(Paragraph(_escape(line[2:]), title_style))
        elif line.startswith("## "):
            story.append(Paragraph(_escape(line[3:]), heading))
        elif line.startswith("- "):
            story.append(Paragraph("• " + _escape(line[2:]), normal))
        else:
            story.append(Paragraph(_escape(raw_line), normal))

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=title,
    )
    document.build(story)
    return buffer.getvalue()


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
