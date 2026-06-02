from pathlib import Path

from PyPDF2 import PdfReader
from docx import Document
from docx.document import Document as DocxDocument
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph
from fastapi import HTTPException, status

from app.models.file_record import FileRecord


def _read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_docx(path: Path) -> str:
    document = Document(path)
    lines = []
    heading_stack: list[str] = []
    table_index = 0

    for block in _iter_docx_blocks(document):
        if isinstance(block, Paragraph):
            text = _clean_cell_text(block.text)
            if not text:
                continue

            style_name = block.style.name if block.style else ""
            if style_name.lower().startswith("toc"):
                continue

            heading_level = _heading_level(style_name)
            if heading_level:
                heading_stack = heading_stack[: heading_level - 1]
                heading_stack.append(text)
                lines.append(text)
            else:
                lines.append(text)
            continue

        table_index += 1
        rows = _table_rows(block)
        if not rows:
            continue

        kv_rows = _key_value_rows(rows)
        section_path = " > ".join(heading_stack)

        if any(key == "REQ ID" for key, _ in kv_rows):
            lines.append(f"Requirement Table {table_index}")
            if section_path:
                lines.append(f"Section Path: {section_path}")
            for key, value in kv_rows:
                lines.append(f"{key}: {value}")
            lines.append("End Requirement Table")
            continue

        lines.append(f"Table {table_index}")
        if section_path:
            lines.append(f"Section Path: {section_path}")
        for row in rows:
            lines.append(" | ".join(row))

    return "\n".join(lines)


def _iter_docx_blocks(document: DocxDocument):
    for child in document.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield Table(child, document)


def _heading_level(style_name: str) -> int | None:
    if not style_name.startswith("Heading "):
        return None

    try:
        return int(style_name.removeprefix("Heading ").strip())
    except ValueError:
        return None


def _table_rows(table: Table) -> list[list[str]]:
    rows = []
    for row in table.rows:
        cells = []
        for cell in row.cells:
            text = _clean_cell_text(cell.text)
            if text and (not cells or cells[-1] != text):
                cells.append(text)
        if cells:
            rows.append(cells)
    return rows


def _key_value_rows(rows: list[list[str]]) -> list[tuple[str, str]]:
    pairs = []
    for row in rows:
        if len(row) < 2:
            continue
        key = _clean_cell_text(row[0])
        value = _clean_cell_text(" ".join(row[1:]))
        if key and value:
            pairs.append((key, value))
    return pairs


def _clean_cell_text(value: str) -> str:
    text = value.replace("\xa0", " ")
    text = " / ".join(part.strip() for part in text.splitlines() if part.strip())
    return " ".join(text.split())


def _read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def extract_text(record: FileRecord) -> str:
    extension = record.path.suffix.lower()
    try:
        if extension == ".txt":
            text = _read_txt(record.path)
        elif extension == ".docx":
            text = _read_docx(record.path)
        elif extension == ".pdf":
            text = _read_pdf(record.path)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot parse unsupported file extension: {extension}",
            )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not parse {record.file_name}. Check that the document is readable.",
        ) from exc

    cleaned = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"No readable text found in {record.file_name}.",
        )
    return cleaned
