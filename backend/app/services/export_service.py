from io import BytesIO
from typing import Any

from docx import Document
from docx.shared import Inches
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


SECTION_TITLES = {
    "scope": "Scope",
    "objectives": "Objectives",
    "featuresToTest": "Features to Test",
    "featuresNotToTest": "Features Not to Test",
    "testStrategy": "Test Strategy",
    "functionalTesting": "Functional Testing",
    "nonFunctionalTesting": "Non Functional Testing",
    "securityTesting": "Security Testing",
    "apiTesting": "API Testing",
    "uiTesting": "UI Testing",
    "regressionTesting": "Regression Testing",
    "risks": "Risks",
    "deliverables": "Deliverables",
    "testCases": "Test Cases",
}


def _normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if "sections" in payload and isinstance(payload["sections"], dict):
        return payload["sections"]
    return payload


def _line_items(value: Any) -> list[str]:
    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, dict):
                item_id = item.get("id", "")
                title = item.get("title", "")
                priority = item.get("priority", "")
                expected = item.get("expected", "")
                prefix = f"{item_id} - " if item_id else ""
                suffix = f" ({priority})" if priority else ""
                lines.append(f"{prefix}{title}{suffix}: {expected}".strip(": "))
            else:
                lines.append(str(item))
        return lines
    return [str(value)]


def render_pdf(payload: dict[str, Any]) -> bytes:
    sections = _normalize_payload(payload)
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="AI Generated Test Plan",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocumentTitle",
        parent=styles["Title"],
        fontSize=20,
        leading=24,
        spaceAfter=18,
    )
    section_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=12,
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=13,
        spaceAfter=5,
    )

    story = [Paragraph("AI Generated Software Test Plan", title_style)]
    for key, title in SECTION_TITLES.items():
        value = sections.get(key)
        if not value:
            continue
        story.append(Paragraph(title, section_style))
        for line in _line_items(value):
            story.append(Paragraph(line.replace("\n", "<br/>"), body_style))
        story.append(Spacer(1, 6))

    doc.build(story)
    return buffer.getvalue()


def render_docx(payload: dict[str, Any]) -> bytes:
    sections = _normalize_payload(payload)
    document = Document()
    section = document.sections[0]
    section.top_margin = Inches(0.6)
    section.bottom_margin = Inches(0.6)
    section.left_margin = Inches(0.7)
    section.right_margin = Inches(0.7)

    document.add_heading("AI Generated Software Test Plan", level=0)
    for key, title in SECTION_TITLES.items():
        value = sections.get(key)
        if not value:
            continue
        document.add_heading(title, level=1)
        lines = _line_items(value)
        if len(lines) == 1 and not isinstance(value, list):
            document.add_paragraph(lines[0])
        else:
            for line in lines:
                document.add_paragraph(line, style="List Bullet")

    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()
