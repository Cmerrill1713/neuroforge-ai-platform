# 🎯 FEATURE & DEPENDENCY MAP
**Last Updated**: January 2025  
**Purpose**: Complete mapping of all system features and their dependencies

---

## 🏗️ **CORE FEATURES OVERVIEW**

### **1. AI Chat System**
- **Location**: `src/api/consolidated_api_architecture.py`
- **Port**: 8004
- **Endpoints**: `/api/chat/`
- **Dependencies**:
  - Ollama (Port 11434)
  - MCP Tools (Port 8000) - Optional
  - Response Cache
  - Agent Selector

### **2. Agent Management**
- **Location**: `src/services/optimized_agent_selector.py`
- **Port**: 8004 (via Consolidated API)
- **Endpoints**: `/api/agents/`
- **Dependencies**:
  - Ollama models
  - Performance monitoring
  - Agent registry

### **3. Knowledge Base & RAG**
- **Location**: `src/core/rag/vector_database.py`
- **Port**: 8004 (via Consolidated API)
- **Endpoints**: `/api/knowledge/`
- **Dependencies**:
  - Weaviate (Port 8090) - Optional
  - Vector embeddings
  - Document storage

### **4. System Health Monitoring**
- **Location**: `src/api/consolidated_api_architecture.py`
- **Port**: 8004
- **Endpoints**: `/api/system/health`
- **Dependencies**:
  - All system services
  - Performance metrics
  - Health check endpoints

### **5. Evolutionary Optimization**
- **Location**: `src/api/evolutionary_api_server_8005.py`
- **Port**: 8005 (Optional)
- **Endpoints**: `/api/evolutionary/`
- **Dependencies**:
  - DSPy optimization
  - Thompson Bandit routing
  - Performance tracking

### **6. Voice Services**
- **TTS Location**: `src/api/tts_server.py`
- **Whisper Location**: `src/api/whisper_server.py`
- **Ports**: 8086 (TTS), 8087 (Whisper)
- **Dependencies**:
  - Audio processing libraries
  - Model files

### **7. MCP Tools Integration**
- **Location**: `src/core/tools/`
- **Port**: 8000 (Optional)
- **Dependencies**:
  - MCP protocol implementation
  - Tool registry
  - Execution engine

---

## 🔗 **DEPENDENCY GRAPH**

### **Primary Dependencies**
```
Frontend (3000) → Consolidated API (8004)
Consolidated API (8004) → Ollama (11434)
Consolidated API (8004) → MCP Tools (8000) [Optional]
Consolidated API (8004) → Evolutionary API (8005) [Optional]
Consolidated API (8004) → Voice Services (8086/8087) [Optional]
Consolidated API (8004) → Weaviate (8090) [Optional]
```

### **Secondary Dependencies**
```
Ollama (11434) → Local AI Models
Weaviate (8090) → Vector Database
MCP Tools (8000) → Tool Registry
Evolutionary API (8005) → DSPy Optimization
Voice Services → Audio Models
```

---

## 📋 **FEATURE DEPENDENCY MATRIX**

| Feature | Ollama | MCP | Evolutionary | Voice | Weaviate | Frontend |
|---------|--------|-----|--------------|-------|----------|----------|
| **Chat System** | ✅ Required | ⚠️ Optional | ❌ None | ❌ None | ❌ None | ✅ Required |
| **Agent Management** | ✅ Required | ❌ None | ❌ None | ❌ None | ❌ None | ✅ Required |
| **Knowledge Base** | ❌ None | ❌ None | ❌ None | ❌ None | ⚠️ Optional | ✅ Required |
| **System Health** | ✅ Required | ⚠️ Optional | ⚠️ Optional | ⚠️ Optional | ⚠️ Optional | ✅ Required |
| **Optimization** | ✅ Required | ❌ None | ✅ Required | ❌ None | ❌ None | ❌ None |
| **Voice Processing** | ❌ None | ❌ None | ❌ None | ✅ Required | ❌ None | ❌ None |
| **MCP Tools** | ❌ None | ✅ Required | ❌ None | ❌ None | ❌ None | ❌ None |

**Legend**:
- ✅ **Required**: Feature cannot work without this dependency
- ⚠️ **Optional**: Feature works better with this dependency
- ❌ **None**: No dependency relationship

---

## 🚀 **STARTUP DEPENDENCIES**

### **Minimum System (Core Features)**
```bash
# Required for basic functionality
1. Ollama (Port 11434)
2. Consolidated API (Port 8004)
3. Frontend (Port 3000)
```

### **Full System (All Features)**
```bash
# All services for complete functionality
1. Ollama (Port 11434)
2. Consolidated API (Port 8004)
3. Frontend (Port 3000)
4. MCP Tools (Port 8000) [Optional]
5. Evolutionary API (Port 8005) [Optional]
6. Voice Services (Ports 8086/8087) [Optional]
7. Weaviate (Port 8090) [Optional]
```

---

## 🔧 **FEATURE CONFIGURATION**

### **Chat System Configuration**
```python
# Dependencies
- Ollama: Required for AI responses
- MCP Tools: Optional for enhanced capabilities
- Response Cache: Built-in
- Agent Selector: Built-in

# Configuration
- Temperature: 0.7
- Max Tokens: 1024
- Latency Requirement: 1000ms
```

### **Knowledge Base Configuration**
```python
# Dependencies
- Weaviate: Optional (falls back to file system)
- Vector Embeddings: Built-in
- Document Storage: Built-in

# Configuration
- Similarity Threshold: 0.8
- Max Results: 10
- Cache Enabled: True
```

### **Agent Management Configuration**
```python
# Dependencies
- Ollama Models: Required
- Performance Monitoring: Built-in
- Agent Registry: Built-in

# Configuration
- Model Selection: Automatic
- Performance Tracking: Enabled
- Load Balancing: Enabled
```

---

## 🛠️ **DEVELOPMENT WORKFLOW BY FEATURE**

### **Working on Chat System**
1. Ensure Ollama is running (Port 11434)
2. Start Consolidated API (Port 8004)
3. Test chat endpoint: `POST /api/chat/`
4. Check logs for errors

### **Working on Knowledge Base**
1. Start Consolidated API (Port 8004)
2. Optional: Start Weaviate (Port 8090)
3. Test knowledge endpoint: `GET /api/knowledge/`
4. Verify document indexing

### **Working on Agent Management**
1. Ensure Ollama is running (Port 11434)
2. Start Consolidated API (Port 8004)
3. Test agents endpoint: `GET /api/agents/`
4. Verify model availability

### **Working on Voice Services**
1. Start TTS Server (Port 8086)
2. Start Whisper Server (Port 8087)
3. Test voice endpoints
4. Verify audio processing

### **Working on MCP Tools**
1. Start MCP Server (Port 8000)
2. Start Consolidated API (Port 8004)
3. Test tool integration
4. Verify tool execution

---

## 🔍 **TROUBLESHOOTING BY FEATURE**

### **Chat System Issues**
```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Check chat endpoint
curl -X POST http://localhost:8004/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

### **Knowledge Base Issues**
```bash
# Check knowledge endpoint
curl http://localhost:8004/api/knowledge/

# Check Weaviate (if used)
curl http://localhost:8090/v1/meta
```

### **Agent Management Issues**
```bash
# Check agents endpoint
curl http://localhost:8004/api/agents/

# Check system health
curl http://localhost:8004/api/system/health
```

### **Voice Services Issues**
```bash
# Check TTS service
curl http://localhost:8086/health

# Check Whisper service
curl http://localhost:8087/health
```

---

## 📊 **PERFORMANCE REQUIREMENTS**

### **Response Time Targets**
- Chat System: < 3 seconds
- Knowledge Search: < 2 seconds
- Agent Selection: < 1 second
- System Health: < 500ms

### **Resource Requirements**
- Memory: 4-8GB (depending on features)
- CPU: 2+ cores
- Storage: 10GB+ (for models and data)

---

## 🔒 **SECURITY CONSIDERATIONS**

### **Feature-Specific Security**
- Chat System: Input validation, rate limiting
- Knowledge Base: Access control, data privacy
- Agent Management: Model security, execution sandbox
- Voice Services: Audio processing security
- MCP Tools: Tool execution security

---

## 📈 **MONITORING & METRICS**

### **Feature-Specific Metrics**
- Chat System: Response time, success rate
- Knowledge Base: Search accuracy, cache hit rate
- Agent Management: Model performance, selection accuracy
- Voice Services: Processing time, quality metrics
- MCP Tools: Execution time, success rate

---

## 🎯 **CURSOR WORK REQUIREMENTS**

### **Before Working on Any Feature:**

1. **Identify Dependencies**
   - Check feature dependency matrix
   - Ensure required services are running
   - Verify optional services if needed

2. **Start Required Services**
   - Use startup procedures for each feature
   - Check service health
   - Verify endpoints are accessible

3. **Test Feature Functionality**
   - Run feature-specific tests
   - Check logs for errors
   - Verify performance metrics

### **Feature Development Guidelines:**

1. **Maintain Dependencies**
   - Don't break existing feature dependencies
   - Update dependency matrix if changes are made
   - Test all dependent features

2. **Follow Configuration Standards**
   - Use consistent configuration patterns
   - Document configuration changes
   - Maintain backward compatibility

3. **Monitor Performance**
   - Track response times
   - Monitor resource usage
   - Alert on performance degradation

---

**⚠️ CRITICAL**: Always check feature dependencies before making changes to avoid breaking other system components.
