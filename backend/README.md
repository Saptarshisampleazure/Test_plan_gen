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

Test plan generation uses the Colab Qwen service. Configure the backend with:

```env
COLAB_SRS_BASE_URL=https://your-ngrok-url.example
COLAB_SRS_GENERATE_PATH=/generate-srs
COLAB_SRS_FALLBACK_PATHS=/generate-srs,/generate,/api/generate,/
COLAB_SRS_LOCAL_FALLBACK=true
COLAB_SRS_MODEL=qwen2.5:7b
COLAB_SRS_TIMEOUT_SECONDS=600
MAX_PROMPT_DOCUMENT_CHARS=24000
```

If your ngrok URL already includes the `/generate-srs` endpoint, the backend
will detect that and use the full URL as-is instead of appending the path twice.

If the Colab SRS API is exposed at the root of your ngrok URL, set:

```env
COLAB_SRS_GENERATE_PATH=/  # or leave blank in .env to use the base URL directly
```

The backend tries `COLAB_SRS_GENERATE_PATH` first. If that returns 404, it tries
`COLAB_SRS_FALLBACK_PATHS` in order, which keeps generation working when the
Colab notebook exposes `/generate`, `/api/generate`, or the ngrok root instead
of `/generate-srs`.

If the ngrok tunnel is offline or the Colab API cannot be reached,
`COLAB_SRS_LOCAL_FALLBACK=true` lets the backend generate a deterministic local
test plan from the extracted SRS text instead of failing the request.

If the Colab API sets `SRS_API_KEY`, configure the backend with
`COLAB_SRS_API_KEY=<your-colab-srs-api-key>` so requests include the matching bearer token.

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
```
