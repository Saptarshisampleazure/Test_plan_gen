from pathlib import Path

from PyPDF2 import PdfReader
from docx import Document
from fastapi import HTTPException, status

from app.models.file_record import FileRecord


def _read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_docx(path: Path) -> str:
    document = Document(path)
    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs]
    table_text = []
    for table in document.tables:
        for row in table.rows:
            table_text.append(" | ".join(cell.text.strip() for cell in row.cells if cell.text.strip()))
    return "\n".join([*paragraphs, *table_text])


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
