# 🔗 Full System Integration Guide

**Date**: October 1, 2025  
**Status**: ✅ Integrated and Ready

---

## 📋 System Architecture

### Port Assignments

| Port | Service | Location | Purpose |
|------|---------|----------|---------|
| **8000** | Agentic Engineering Platform | `/Users/christianmerrill/agentic-engineering-platform/` | Workflow orchestration, model management, knowledge graph |
| **8004** | Consolidated AI Chat API | `/Users/christianmerrill/Prompt Engineering/` | AI chat, DSPy optimization, R1 RAG system |
| **3000** | Next.js Frontend | `/Users/christianmerrill/Prompt Engineering/frontend/` | User interface |

---

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)

```bash
cd "/Users/christianmerrill/Prompt Engineering"
./start_integrated_system.sh
```

This script will:
- ✅ Start Backend on port 8004
- ✅ Start Frontend on port 3000
- ✅ Run health checks
- ✅ Display logs and URLs
- ✅ Handle graceful shutdown with Ctrl+C

### Option 2: Manual Startup

#### Start Backend (Port 8004)
```bash
cd "/Users/christianmerrill/Prompt Engineering"
python3 main.py
```

#### Start Frontend (Port 3000)
```bash
cd "/Users/christianmerrill/Prompt Engineering/frontend"
npm install  # First time only
npm run dev
```

---

## 🔍 Health Checks

### Backend 8004
```bash
curl http://localhost:8004/
```

Expected response:
```json
{
  "message": "Consolidated AI Chat API",
  "version": "2.0.0",
  "status": "running"
}
```

### Frontend 3000
```bash
curl http://localhost:3000/
```

Should return the Next.js application HTML.

---

## 🌐 API Endpoints

### Backend 8004 - Consolidated API

#### Core Endpoints
- **GET** `/` - API status
- **GET** `/docs` - Interactive API documentation (Swagger UI)
- **GET** `/redoc` - ReDoc documentation

#### Chat System
- **POST** `/api/chat/` - Send chat message
- **GET** `/api/agents/` - List available agents
- **GET** `/api/agents/{agent_id}` - Get agent details
- **POST** `/api/agents/{agent_id}/feedback` - Submit feedback

#### Knowledge & RAG
- **POST** `/api/knowledge/search` - Search knowledge base
- **GET** `/api/knowledge/stats` - Knowledge base statistics
- **POST** `/api/rag/query` - RAG hybrid search
- **GET** `/api/rag/metrics` - RAG performance metrics

#### Evolutionary Optimization
- **GET** `/api/evolutionary/stats` - Evolutionary optimization stats
- **GET** `/api/evolutionary/bandit/stats` - Thompson sampling statistics
- **POST** `/api/evolutionary/optimize` - Run optimization

#### System
- **GET** `/api/system/health` - System health check
- **GET** `/api/system/metrics` - System performance metrics
- **POST** `/api/admin/cache/clear` - Clear response cache

---

## 🎨 Frontend Configuration

### API Routes

All frontend API routes in `frontend/src/app/api/` now correctly proxy to port **8004**:

```typescript
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8004'
```

### Environment Variables

Create `frontend/.env.local`:

```env
BACKEND_URL=http://localhost:8004
NEXT_PUBLIC_API_URL=http://localhost:8004
NEXT_PUBLIC_WS_URL=ws://localhost:8004
NODE_ENV=development
```

---

## 🐳 Docker Deployment

### Using Docker Compose

```bash
cd "/Users/christianmerrill/Prompt Engineering"
docker-compose up -d
```

Services included:
- **ai-assistant-api**: Backend on port 8004
- **frontend**: Next.js on port 3000
- **nginx**: Reverse proxy on ports 80/443

### Check Docker Status
```bash
docker-compose ps
docker-compose logs -f
```

---

## 🔧 Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8004
lsof -i :3000

# Kill process
kill -9 <PID>
```

### Backend Not Starting

1. Check Python dependencies:
```bash
pip install -r requirements.txt
```

2. Check logs:
```bash
tail -f logs/backend_8004.log
```

3. Verify Python version:
```bash
python3 --version  # Should be 3.8+
```

### Frontend Not Starting

1. Clear Next.js cache:
```bash
cd frontend
rm -rf .next
npm run dev
```

2. Check logs:
```bash
tail -f logs/frontend_3000.log
```

3. Verify Node version:
```bash
node --version  # Should be 18+
```

### API Connection Issues

1. Verify backend is running:
```bash
curl http://localhost:8004/
```

2. Check CORS settings in backend

3. Verify environment variables in frontend:
```bash
cd frontend
cat .env.local
```

---

## 📊 Testing the Integration

### 1. Test Backend API
```bash
# Health check
curl http://localhost:8004/api/system/health

# Chat endpoint
curl -X POST http://localhost:8004/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?", "task_type": "text_generation"}'

# Knowledge search
curl -X POST http://localhost:8004/api/knowledge/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "limit": 5}'
```

### 2. Test Frontend
1. Open browser: http://localhost:3000
2. Navigate through tabs: Chat, Agents, Knowledge, Evolution, RAG
3. Test chat functionality
4. Check network tab for API calls to port 8004

### 3. Test Integration
```bash
cd "/Users/christianmerrill/Prompt Engineering"
# Run the test script (if available)
node frontend/functional_api_tests.js
```

---

## 📁 Project Structure

```
/Users/christianmerrill/Prompt Engineering/
├── main.py                              # Starts backend on port 8004
├── start_integrated_system.sh           # Automated startup script
├── src/
│   └── api/
│       └── consolidated_api_architecture.py  # Main API server
├── frontend/
│   ├── src/
│   │   └── app/
│   │       └── api/                     # Next.js API routes (proxy to 8004)
│   ├── package.json
│   └── .env.local                       # Frontend environment config
├── logs/
│   ├── backend_8004.log
│   └── frontend_3000.log
└── docker-compose.yml
```

---

## 🔄 Integration Changes Made

### ✅ Backend Changes
1. **Fixed port configuration** in `main.py` (8000 → 8004)
2. **Fixed port configuration** in `src/api/consolidated_api_architecture.py` (8000 → 8004)

### ✅ Frontend Changes
Updated all API route files to use port **8004** instead of 8005:
1. `frontend/src/app/api/rag/query/route.ts`
2. `frontend/src/app/api/rag/metrics/route.ts`
3. `frontend/src/app/api/evolutionary/stats/route.ts`
4. `frontend/src/app/api/evolutionary/bandit/stats/route.ts`
5. `frontend/src/app/api/evolutionary/optimize/route.ts`

### ✅ New Files Created
1. `start_integrated_system.sh` - Automated startup script
2. `INTEGRATION_GUIDE.md` - This comprehensive guide

---

## 🎯 Next Steps

### Immediate Actions
1. ✅ Start the integrated system using the startup script
2. ✅ Verify all services are running
3. ✅ Test API endpoints
4. ✅ Test frontend functionality

### Future Enhancements
1. 🔄 Integrate with Agentic Platform on port 8000 (if needed)
2. 🔄 Set up monitoring and logging dashboards
3. 🔄 Configure production deployment
4. 🔄 Set up CI/CD pipeline
5. 🔄 Add WebSocket support for real-time updates

---

## 📞 Support

### Logs Location
- Backend: `logs/backend_8004.log`
- Frontend: `logs/frontend_3000.log`

### API Documentation
- Swagger UI: http://localhost:8004/docs
- ReDoc: http://localhost:8004/redoc

### Useful Commands
```bash
# View all running processes
ps aux | grep -E "python|node"

# Check port usage
lsof -i :8004
lsof -i :3000

# Restart services
./start_integrated_system.sh

# View logs in real-time
tail -f logs/backend_8004.log
tail -f logs/frontend_3000.log
```

---

## ✅ Status Summary

| Component | Status | Port | URL |
|-----------|--------|------|-----|
| Backend API | ✅ Configured | 8004 | http://localhost:8004 |
| Frontend | ✅ Configured | 3000 | http://localhost:3000 |
| Docker Setup | ✅ Ready | - | - |
| Startup Script | ✅ Created | - | - |
| Health Checks | ✅ Configured | - | - |

**Integration Status**: 🎉 **COMPLETE & READY TO START**

---

## 🚦 Getting Started Checklist

- [ ] Run `./start_integrated_system.sh`
- [ ] Verify backend is accessible at http://localhost:8004
- [ ] Verify frontend is accessible at http://localhost:3000
- [ ] Test API endpoints using curl or Swagger UI
- [ ] Test frontend chat functionality
- [ ] Check logs for any errors
- [ ] Review API documentation at http://localhost:8004/docs

---

**Last Updated**: October 1, 2025  
**Maintained By**: Christian Merrill


