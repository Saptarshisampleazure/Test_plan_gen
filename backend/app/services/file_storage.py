import json
import re
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.config import STORAGE_DIR, UPLOAD_DIR, get_settings
from app.models.file_record import FileRecord


INDEX_PATH = STORAGE_DIR / "files.json"
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def ensure_storage() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    if not INDEX_PATH.exists():
        INDEX_PATH.write_text("{}", encoding="utf-8")


def _load_index() -> dict:
    ensure_storage()
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def _save_index(index: dict) -> None:
    ensure_storage()
    INDEX_PATH.write_text(json.dumps(index, indent=2), encoding="utf-8")


def _safe_filename(filename: str) -> str:
    name = Path(filename).name
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._") or "upload.txt"


def get_file_record(file_id: str) -> FileRecord:
    index = _load_index()
    item = index.get(file_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Uploaded file not found.")

    path = Path(item["path"])
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file is missing.")

    return FileRecord(
        file_id=file_id,
        file_name=item["fileName"],
        content_type=item["contentType"],
        size=item["size"],
        path=path,
    )


async def save_upload(file: UploadFile) -> FileRecord:
    ensure_storage()
    settings = get_settings()
    original_name = file.filename or "upload.txt"
    extension = Path(original_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Upload PDF, DOCX, or TXT files.",
        )

    file_id = str(uuid4())
    safe_name = _safe_filename(original_name)
    stored_path = UPLOAD_DIR / f"{file_id}_{safe_name}"

    size = 0
    with stored_path.open("wb") as output:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > settings.max_upload_size_bytes:
                output.close()
                stored_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds {settings.max_upload_size_mb} MB upload limit.",
                )
            output.write(chunk)

    record = FileRecord(
        file_id=file_id,
        file_name=safe_name,
        content_type=file.content_type or "application/octet-stream",
        size=size,
        path=stored_path,
    )

    index = _load_index()
    index[file_id] = {
        "fileId": record.file_id,
        "fileName": record.file_name,
        "contentType": record.content_type,
        "size": record.size,
        "path": str(record.path),
    }
    _save_index(index)
    return record
