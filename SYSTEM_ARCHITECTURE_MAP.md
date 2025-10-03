# 🗺️ COMPLETE SYSTEM ARCHITECTURE MAP
**Last Updated**: October 2, 2025 (Docling Integration Complete - Advanced Document Processing)  
**Purpose**: Single source of truth for all system components, ports, and configurations

---

## 🎯 **SYSTEM OVERVIEW**

This is a comprehensive AI engineering platform with multiple integrated services. The system has undergone several consolidations but still maintains some distributed components.

---

## 🔌 **PORT CONFIGURATION - DEFINITIVE**

### **Primary Services (Active)**

| Port | Service | Status | Purpose | Entry Point |
|------|---------|--------|---------|-------------|
| **3000** | Frontend (Next.js) | ✅ Active | User Interface | `frontend/` directory |
| **8004** | Consolidated API | ✅ Active | Main API Server | `main.py` or `consolidated_api_optimized.py` |
| **11434** | Ollama (External) | ✅ Active | Local AI Models | `ollama serve` |

### **Secondary Services (Optional/Proxy)**

| Port | Service | Status | Purpose | Entry Point |
|------|---------|--------|---------|-------------|
| **8000** | MCP Tools | ⚠️ Optional | Multi-Call Protocol | `mcp_servers/` directory |
| **8005** | Evolutionary API | ⚠️ Optional | Optimization Engine | `src/api/evolutionary_api_server_8005.py` |
| **8086** | TTS Service | ⚠️ Optional | Text-to-Speech | `src/api/tts_server.py` |
| **8087** | Whisper Service | ⚠️ Optional | Speech-to-Text | `src/api/whisper_server.py` |
| **8090** | Weaviate | ⚠️ Optional | Vector Database | Docker container |

---

## 🏗️ **SERVICE ARCHITECTURE**

### **1. Consolidated API (Port 8004) - MAIN SERVICE**
**File**: `main.py` or `consolidated_api_optimized.py`

**Endpoints**:
```
/                           - System status
/api/chat/                  - Chat interactions
/api/agents/                - Agent management
/api/knowledge/             - Knowledge base search
/api/system/                - System health
/api/admin/                 - Admin operations
/api/voice/                 - Voice services (TTS/STT)
/api/rag/                   - Enhanced RAG system
/api/mcp/                   - Enhanced MCP tools
/api/healing/               - Self-healing system
/api/vision/                - LLaVA vision integration
/api/model/                 - Optimized large models
/api/mlx/                   - MLX processing
/api/docling/               - Advanced document processing (Docling)
/docs                       - API documentation
```

**Features**:
- MCP tool integration
- Ollama model integration
- RAG system integration
- Performance monitoring
- Caching system
- Voice services (TTS/STT)
- Self-healing capabilities
- Vision processing (LLaVA)
- Optimized large model integration
- MLX processing
- Enhanced research system
- Parallel crawling
- Intelligent error resolution
- Advanced document processing (Docling)
- External drive ingestion
- OCR and table extraction

### **2. Frontend (Port 3000)**
**Directory**: `frontend/`
**Framework**: Next.js 14.2.33
**Scripts**:
- `npm run dev` - Development server
- `npm run build` - Production build
- `npm run start` - Production server

**API Proxy Configuration**:
- Proxies requests to backend (Port 8004)
- Environment variables required in `frontend/.env.local`:
  ```bash
  NEXT_PUBLIC_CONSOLIDATED_API_URL=http://localhost:8004
  NEXT_PUBLIC_AGENTIC_PLATFORM_URL=http://localhost:8000
  NEXT_PUBLIC_API_URL=http://localhost:8004
  ```

**Frontend API Routes**:
- `/api/system/health` → `http://localhost:8004/api/system/health`
- `/api/chat` → `http://localhost:8004/api/chat/`
- `/api/voice/options` → `http://localhost:8004/api/voice/options`
- `/api/voice/health` → `http://localhost:8004/api/voice/health`
- `/api/rag/query` → `http://localhost:8004/api/rag/enhanced/search`

### **3. Optional Services**

#### **MCP Tools (Port 8000)**
- **Purpose**: Multi-Call Protocol tool execution
- **Entry**: `mcp_servers/` directory
- **Integration**: Proxied through Consolidated API

#### **Evolutionary API (Port 8005)**
- **Purpose**: Prompt optimization and evolution
- **Entry**: `src/api/evolutionary_api_server_8005.py`
- **Integration**: Proxied through Consolidated API

#### **Voice Services**
- **TTS (Port 8086)**: Text-to-speech conversion
- **Whisper (Port 8087)**: Speech-to-text conversion
- **Integration**: Proxied through Consolidated API

#### **Weaviate (Port 8090)**
- **Purpose**: Vector database for RAG
- **Integration**: Docker container
- **Usage**: Knowledge base storage

---

## 🚀 **STARTUP PROCEDURES**

### **Quick Start (Recommended)**
```bash
# Start main system
python3 main.py

# Start frontend (separate terminal)
cd frontend && npm run dev
```

### **Full System Start**
```bash
# Use integrated startup script
./start_integrated_system.sh
```

### **Individual Service Start**
```bash
# Backend only
python3 consolidated_api_optimized.py

# Frontend only
cd frontend && npm run dev

# Ollama (if not running)
ollama serve

# Docker services
docker-compose up -d
```

---

## 📁 **KEY DIRECTORY STRUCTURE**

```
/Users/christianmerrill/Prompt Engineering/
├── 📁 frontend/                 # Next.js frontend (Port 3000)
├── 📁 src/                     # Source code
│   ├── 📁 api/                 # API services
│   │   ├── consolidated_api_architecture.py
│   │   ├── evolutionary_api_server_8005.py
│   │   ├── tts_server.py
│   │   └── whisper_server.py
│   ├── 📁 core/                # Core functionality
│   ├── 📁 services/            # Service layer
│   └── 📁 agents/              # Agent implementations
├── 📁 mcp_servers/             # MCP tool servers (Port 8000)
├── 📁 knowledge_base/          # Knowledge documents
├── 📁 logs/                    # System logs
├── 📁 docs/                    # Documentation
├── main.py                     # Main entry point (Port 8004)
├── consolidated_api_optimized.py  # Alternative main entry
├── start_integrated_system.sh  # Full system startup
└── system_cli.py              # System management CLI
```

---

## 🔧 **CONFIGURATION FILES**

### **Docker Configuration**
- `docker-compose.yml` - Main Docker setup
- `docker-compose.agents.yml` - Agent services
- `docker-compose.prod.yml` - Production setup

### **Frontend Configuration**
- `frontend/package.json` - Dependencies and scripts
- `frontend/next.config.js` - Next.js configuration
- `frontend/tailwind.config.js` - Styling configuration

### **Environment Configuration**
- `env.example` - Environment template
- `env.local` - Local environment variables

---

## 🛠️ **DEVELOPMENT WORKFLOW**

### **Making Changes**
1. **Backend Changes**: Edit files in `src/` directory
2. **Frontend Changes**: Edit files in `frontend/` directory
3. **API Changes**: Update `src/api/` files
4. **Configuration**: Update relevant config files

### **Testing Changes**
```bash
# Test backend
curl http://localhost:8004/api/system/health

# Test frontend
# Navigate to http://localhost:3000

# Test specific endpoints
curl http://localhost:8004/api/agents/
curl http://localhost:8004/api/knowledge/
```

---

## 🔍 **TROUBLESHOOTING**

### **Common Issues**

#### **Port Conflicts**
```bash
# Check what's using a port
lsof -i :8004
lsof -i :3000

# Kill process using port
kill -9 <PID>
```

#### **Service Not Starting**
```bash
# Check logs
tail -f logs/backend_8004.log
tail -f logs/frontend_3000.log

# Check system health
python3 system_cli.py
```

#### **Dependencies Missing**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend && npm install
```

### **Health Checks**
```bash
# Backend health
curl http://localhost:8004/api/system/health

# Frontend health
curl http://localhost:3000

# Ollama health
curl http://localhost:11434/api/tags
```

---

## 📊 **MONITORING & LOGS**

### **Log Locations**
- Backend logs: `logs/backend_8004.log`
- Frontend logs: `logs/frontend_3000.log`
- System logs: `logs/` directory

### **Monitoring Endpoints**
- System health: `GET /api/system/health`
- Agent status: `GET /api/agents/`
- Knowledge stats: `GET /api/knowledge/`

---

## 🔒 **SECURITY & PERMISSIONS**

### **CORS Configuration**
- Frontend: `http://localhost:3000`
- Development: `http://127.0.0.1:3000`

### **Authentication**
- Currently development mode
- No authentication required for local development

---

## 📋 **REQUIREMENTS FOR CURSOR WORK**

### **Before Working on Any Feature:**

1. **Verify Current System State**
   ```bash
   python3 system_cli.py
   ```

2. **Check Port Availability**
   ```bash
   lsof -i :8004  # Backend
   lsof -i :3000  # Frontend
   ```

3. **Verify Dependencies**
   ```bash
   pip install -r requirements.txt
   cd frontend && npm install
   ```

4. **Start Required Services**
   ```bash
   python3 main.py &
   cd frontend && npm run dev &
   ```

5. **Test System Health**
   ```bash
   curl http://localhost:8004/api/system/health
   ```

### **Working on Features:**

1. **Backend Features**: Work in `src/` directory
2. **Frontend Features**: Work in `frontend/` directory
3. **API Changes**: Update relevant files in `src/api/`
4. **Configuration**: Update relevant config files

### **Testing Changes:**

1. **Restart Affected Services**
2. **Run Health Checks**
3. **Test Specific Endpoints**
4. **Check Logs for Errors**

---

## 🎯 **CURRENT SYSTEM STATUS**

- ✅ **Consolidated API**: Running on port 8004
- ✅ **Frontend**: Running on port 3000
- ✅ **Ollama**: Available on port 11434
- ⚠️ **MCP Tools**: Optional, proxied through main API
- ⚠️ **Evolutionary API**: Optional, proxied through main API
- ⚠️ **Voice Services**: Optional, proxied through main API

---

## 📞 **SUPPORT & DOCUMENTATION**

- **System CLI**: `python3 system_cli.py`
- **API Docs**: `http://localhost:8004/docs`
- **Logs**: `logs/` directory
- **Documentation**: `docs/` directory

---

**⚠️ IMPORTANT**: Always check this document before making changes to understand the current system architecture and avoid port conflicts or service disruptions.
