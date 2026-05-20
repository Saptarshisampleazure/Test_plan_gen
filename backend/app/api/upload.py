from fastapi import APIRouter, Depends, File, UploadFile

from app.core.security import get_current_user
from app.services.file_storage import save_upload


router = APIRouter(tags=["Uploads"])


@router.post("/upload")
async def upload_srs(
    file: UploadFile = File(...),
    _: dict = Depends(get_current_user),
) -> dict:
    record = await save_upload(file)
    return {
        "fileId": record.file_id,
        "fileName": record.file_name,
        "contentType": record.content_type,
        "size": record.size,
        "status": "uploaded",
    }
