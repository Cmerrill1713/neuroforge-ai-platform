# 🔌 Port Configuration - Dual Backend System

## Correct Port Assignments

### Port 8000: **Agentic Engineering Platform**
**Location**: `/Users/christianmerrill/agentic-engineering-platform/main.py`

**Purpose**: Primary orchestration and management platform

**Endpoints**:
- `/` - Platform status
- `/knowledge-graph/search` - Knowledge graph queries
- `/models/list` - Model management
- `/monitoring/metrics` - System metrics
- `/workflow/*` - Workflow management
- `/code-assistant/*` - Code assistance
- `/embedding-system/*` - Embedding operations

**Components**:
- Workflow orchestration
- Code assistant
- Multi-agent analyzer
- Knowledge graph
- Embedding system
- Web crawler
- Model management
- Monitoring & analytics

---

### Port 8004: **Consolidated AI Chat API** (Updated ✅)
**Location**: `/Users/christianmerrill/Prompt Engineering/src/api/consolidated_api_architecture.py`

**Purpose**: AI chat, DSPy optimization, R1 RAG system

**Endpoints**:
- `/api/chat/` - Chat with intelligent agent selection
- `/api/agents/` - Agent management & performance
- `/api/knowledge/` - R1-inspired RAG search
- `/api/system/` - System health & metrics
- `/api/admin/` - Admin operations & cache management
- `/docs` - API documentation

**Components**:
- R1-Inspired RAG System
- DSPy MIPRO Optimizer
- Evolutionary Optimization
- Thompson Bandit Routing
- Agent Selector
- Response Cache
- Knowledge Base

---

## Frontend Configuration

**Frontend** should route requests based on functionality:

```javascript
// Agentic Platform (Port 8000)
const agenticAPI = 'http://localhost:8000';
- Workflows
- Model management  
- System monitoring
- Knowledge graph

// Consolidated API (Port 8004)
const consolidatedAPI = 'http://localhost:8004';
- Chat interactions
- Knowledge search (R1 RAG)
- Agent selection
- System health
```

---

## Docker Compose Configuration

If using Docker, update `docker-compose.yml`:

```yaml
services:
  agentic-platform:
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
      
  consolidated-api:
    ports:
      - "8004:8004"
    environment:
      - PORT=8004
```

---

## Starting Both Services

### Start Agentic Platform (Port 8000)
```bash
cd /Users/christianmerrill/agentic-engineering-platform
python3 main.py
```

### Start Consolidated API (Port 8004)
```bash
cd "/Users/christianmerrill/Prompt Engineering"
python3 src/api/consolidated_api_architecture.py
```

Or with uvicorn:
```bash
cd "/Users/christianmerrill/Prompt Engineering"
uvicorn src.api.consolidated_api_architecture:app --host 0.0.0.0 --port 8004
```

---

## Health Checks

### Check Agentic Platform (Port 8000)
```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "message": "Agentic Engineering Platform",
  "status": "running",
  "version": "1.0.0",
  "components": { ... }
}
```

### Check Consolidated API (Port 8004)
```bash
curl http://localhost:8004/
```

Expected response:
```json
{
  "message": "Consolidated AI Chat API",
  "version": "2.0.0",
  "status": "running",
  "endpoints": { ... }
}
```

---

## Port Conflict Resolution

If ports are already in use:

### Find process using port
```bash
lsof -i :8000
lsof -i :8004
```

### Kill process if needed
```bash
kill -9 <PID>
```

---

## Summary

✅ **Port 8000**: Agentic Engineering Platform (orchestration, workflows, models)
✅ **Port 8004**: Consolidated AI Chat API (chat, RAG, DSPy optimization)
✅ **Port 3000**: Frontend (Next.js)
✅ **Port 8090**: Weaviate (knowledge base)

**Status**: Configuration updated and documented! 🎉
