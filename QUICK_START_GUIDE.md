# Quick Start Guide

This walkthrough gets the demo stack running locally with the FastAPI backend, the Next.js dashboard, and (optionally) the text-to-speech sidecar.

## 1. Clone & Install
```bash
git clone <repository-url>
cd "Prompt Engineering"

# Python dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install
cd ..
```

## 2. Start the Backend
```bash
uvicorn api_server:app --host 0.0.0.0 --port 8002
```
The OpenAPI docs are available at [http://localhost:8002/docs](http://localhost:8002/docs). The chat endpoint lives at `/api/chat`.

## 3. Start the Frontend
```bash
cd frontend
npm run dev
```
Head to [http://localhost:3000](http://localhost:3000) and use the chat panel. Messages are proxied to the backend at `http://localhost:8002`.

## 4. Optional: Docker Compose
```bash
docker-compose up --build
```
This launches both services. Stop them with `Ctrl+C` or `docker-compose down`.

## 5. Optional: Enable Ollama + TTS
- Run `ollama serve` locally to let the backend call models such as `qwen2.5:7b`.
- Start the TTS sidecar (requires `edge-tts`, `torchaudio`, `torch`, and `chatterbox-tts`):
  ```bash
  python production_tts_server.py
  ```
  The chat API will try to attach audio responses when the server is reachable at `http://localhost:8086`.

## 6. Verify Everything
```bash
# Basic backend health
curl http://localhost:8002/

# Chat roundtrip
curl -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message"}'
```

If the response echoes your message, the stack is wired correctly. Enable Ollama for richer replies.

## 7. Run Tests
```bash
pytest
```
Use `pytest -k <name>` to run individual suites when Ollama or optional services are unavailable.

Happy hacking!
