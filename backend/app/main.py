from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api import auth, export, testplan, upload
from app.core.config import get_settings
from app.services.file_storage import ensure_storage


settings = get_settings()
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = PROJECT_ROOT / "dist"
FRONTEND_INDEX = FRONTEND_DIST / "index.html"
FRONTEND_ASSETS = FRONTEND_DIST / "assets"

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Local API for converting SRS documents into structured QA test plans.",
)

allowed_origins = {
    settings.frontend_origin,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    ensure_storage()


@app.get("/health", tags=["System"])
def health() -> dict:
    return {"status": "ok", "service": settings.app_name, "environment": settings.app_env}


app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(testplan.router)
app.include_router(export.router)

if FRONTEND_ASSETS.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_ASSETS),
        name="frontend-assets",
    )


@app.get("/", include_in_schema=False)
def frontend_index():
    if FRONTEND_INDEX.exists():
        return FileResponse(
            FRONTEND_INDEX,
            headers={"Cache-Control": "no-store"},
        )

    return HTMLResponse(
        """
        <!doctype html>
        <html>
          <head><title>Frontend build missing</title></head>
          <body>
            <h1>Frontend build missing</h1>
            <p>Run <code>npm run build</code>, then restart the Python backend.</p>
          </body>
        </html>
        """,
        status_code=503,
    )


@app.get("/{path:path}", include_in_schema=False)
def frontend_fallback(path: str):
    if path.startswith(("docs", "redoc", "openapi.json")):
        return HTMLResponse("Not found", status_code=404)

    return frontend_index()
