# Agentic LLM Core

Prototype environment for experimenting with agent routing, lightweight knowledge search, and a Next.js front-end. The codebase ships a FastAPI backend that orchestrates agent selection, a small demo knowledge base, and a Material UI dashboard. Many advanced capabilities that appear elsewhere in the repository are aspirational – the current stack is intentionally simple and designed for local experimentation.

## What’s Included

- **FastAPI backend** (`api_server.py`) exposing chat, metrics, and knowledge search endpoints. Agent selection wraps a lightweight heuristic and can call local Ollama models when available.
- **Next.js frontend** (`/frontend`) that proxies chat requests to the backend, renders agent telemetry, and stubs several UI panels for future work.
- **Simple knowledge base** (`src/core/knowledge/simple_knowledge_base.py`) backed by JSON/text files for quick retrieval demos.
- **Optional TTS helper** (`production_tts_server.py`) that can synthesize audio responses when the required dependencies are installed.

## Current Status & Limits

- Without Ollama running locally the backend falls back to echo-style replies; no hosted model keys are bundled.
- Redis, Postgres, and other infrastructure noted in the source code are not required for local runs. Where those services are unavailable, the code degrades gracefully.
- The TTS server is optional: if `edge-tts`, `torchaudio`, or `chatterbox-tts` are unavailable it will log a warning and fall back to text-only responses.

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- (Optional) [Ollama](https://ollama.com) running locally

### Backend
```bash
pip install -r requirements.txt
uvicorn api_server:app --host 0.0.0.0 --port 8002
```
The script `api_server.py` exposes the same app if you prefer `python api_server.py` during development.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
The development server listens on [http://localhost:3000](http://localhost:3000). Chat requests proxy to the backend at `http://localhost:8002` by default.

## Docker Compose Workflow

A convenience stack is provided in `docker-compose.yml`:
```bash
docker-compose up --build
```
- Backend: http://localhost:8002
- Frontend: http://localhost:3000
- Redis (optional cache/rate limiting): exposed on localhost:6380; remove the service from `docker-compose.yml` if you do not need it.
- Knowledge base volume: the backend mounts `./knowledge_base` read-only so local edits are reflected immediately.
  - Regenerate the index after adding or removing entries:
    ```bash
    python tools/manage_kb.py rebuild
    ```

## Local Quality & Maintenance Scripts

- `tools/run_quality_checks.py` – runs `git diff --stat`, backend lint/tests (`ruff`, `pytest`), and `npm run lint` (if available) to spot issues quickly.
- `tools/check_heartbeat.py` – reads `logs/events.jsonl` and warns if no events were logged in the past 24 hours (useful for monitoring nightly automation).

Environment variables passed into the containers:
- `NEXT_PUBLIC_API_URL` / `BACKEND_API_URL` – base URL for the backend (default `http://localhost:8002`).
- `REDIS_URL` – optional; the backend behaves sensibly if Redis is unavailable.

## Knowledge Base Utilities

The knowledge base assets live in `knowledge_base/`. You can load them directly:
```python
from core.knowledge.simple_knowledge_base import SimpleKnowledgeBase
kb = SimpleKnowledgeBase()
results = kb.search("parallel thinking")
```
The CLI helper `python test_knowledge_base.py` prints a small demo against the bundled data.

## Testing

```bash
PYTHONPATH=. pytest
```
The suite exercises prompt agents, runner orchestration, and the knowledge base helpers. Several tests assume Ollama and the MLX runtimes are available and that Torch can initialise OpenMP. Run them in an environment where those services are running (or set the environment variables from the troubleshooting section). Otherwise, skip or mark xfail the model-dependent suites.

## Optional Text-to-Speech

`production_tts_server.py` can serve synthesized audio over HTTP. It checks for `edge-tts`, `torchaudio`, `torch`, and `chatterbox-tts` at runtime and falls back to text-only responses if they are not installed. Start it with:
```bash
python production_tts_server.py
```
To have the frontend request audio, set
```bash
export TTS_ENABLED=true
export TTS_SERVER_URL=http://localhost:8086
```
By default the chat bridge leaves TTS disabled to avoid spamming the endpoint when the service is absent.

## Directory Highlights

- `src/core/` – shared backend modules (agents, reasoning engine, adapters).
- `frontend/` – Next.js application.
- Chat UI displays the answering agent, confidence, latency, and fallback status for each assistant response.
- The backend writes structured orchestration events to `logs/events.jsonl` (one JSON record per chat response) so you can audit agent/model choices over time.
- Basic input sanitisation flags potentially dangerous shell commands and marks the response for manual review in the UI.
- `tests/` – pytest suite covering core components.
- `Dockerfile.backend` – image definition for the backend service.

## Having Issues?

If something fails to start:
1. Verify the backend is reachable at `http://localhost:8002/`.
2. Check that Ollama is running (or expect fallback responses).
3. Inspect the Next.js API route logs (`frontend/app/api/chat/route.ts`) for detailed error messages.
4. When running code that imports Torch (the agent selector/parallel reasoning engine), set the following environment variables if you hit OpenMP shared-memory errors on macOS sandboxed environments:
   ```bash
   export KMP_DUPLICATE_LIB_OK=TRUE
   export KMP_AFFINITY=disabled
   export KMP_USE_SHM=0
   export OMP_NUM_THREADS=${OMP_NUM_THREADS:-1}
   ```

Feel free to extend the agents, add new knowledge base entries, or replace the placeholder UI panels with real features as you iterate.
