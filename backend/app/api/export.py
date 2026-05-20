from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.core.security import get_current_user
from app.services.export_service import render_docx, render_pdf


router = APIRouter(tags=["Exports"])


@router.post("/export/pdf")
def export_pdf(payload: dict, _: dict = Depends(get_current_user)) -> Response:
    content = render_pdf(payload)
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="ai-test-plan.pdf"'},
    )


@router.post("/export/docx")
def export_docx(payload: dict, _: dict = Depends(get_current_user)) -> Response:
    content = render_docx(payload)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": 'attachment; filename="ai-test-plan.docx"'},
    )
