# SRS QA Forge Backend

FastAPI backend for the React QA dashboard.

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m uvicorn app.main:app --reload --reload-dir app --host 127.0.0.1 --port 8000
```

The `--reload-dir app` option keeps auto-reload focused on source code. Without it,
uploads written to `backend/storage` can trigger a backend restart in the middle of
the upload/generate flow.

Default login:

```text
username: admin
password: admin123
```

## Endpoints

- `POST /login`
- `POST /upload`
- `POST /generate-testplan`
- `POST /export/pdf`
- `POST /export/docx`
- `GET /health`

Set the frontend `.env` to:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_ENABLE_MOCK_API=false
```
