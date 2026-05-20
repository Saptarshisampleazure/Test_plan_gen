from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user
from app.schemas.testplan import GenerateTestPlanRequest, GenerateTestPlanResponse
from app.services.document_parser import extract_text
from app.services.file_storage import get_file_record
from app.services.testplan_generator import generate_plan


router = APIRouter(tags=["Test Plans"])


@router.post("/generate-testplan", response_model=GenerateTestPlanResponse)
def generate_test_plan(
    payload: GenerateTestPlanRequest,
    _: dict = Depends(get_current_user),
) -> dict:
    if not payload.files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one uploaded file reference is required.",
        )

    source_files = []
    text_parts = []

    for file_ref in payload.files:
        file_id = file_ref.fileId
        if not file_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Each file reference must include fileId.",
            )

        record = get_file_record(file_id)
        source_files.append(record.file_name)
        text_parts.append(extract_text(record))

    return generate_plan("\n\n".join(text_parts), source_files)
