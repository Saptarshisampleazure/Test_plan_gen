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

Ollama generation defaults to `http://localhost:11434/api/generate` with
`LOCAL_AI_SRS_VISION_MODEL_2=qwen2.5:3b`. The backend also sends
`OLLAMA_NUM_GPU=-1` as Ollama's `options.num_gpu` value so Ollama offloads as many
layers as it can to the GPU. Adjust `OLLAMA_NUM_GPU` only if your GPU needs a
specific layer count. Generation uses Ollama streaming plus `OLLAMA_NUM_CTX`
and `MAX_PROMPT_DOCUMENT_CHARS` to fit the local model context. The backend does
not set a response wait timeout or output token cap by default, so slow devices
can let Ollama finish the test plan.

To use the Colab Qwen service instead, keep the Ollama values in place and set:

```env
TESTPLAN_GENERATOR_PROVIDER=colab
COLAB_SRS_BASE_URL=https://your-ngrok-url.example
COLAB_SRS_GENERATE_PATH=/generate-srs
COLAB_SRS_MODEL=qwen2.5:7b
```

If the Colab API sets `SRS_API_KEY`, configure the backend with
`COLAB_SRS_API_KEY` so requests include the matching bearer token.

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
