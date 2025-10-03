# 🎯 CURSOR WORK REQUIREMENTS
**Last Updated**: October 2, 2025 (API Fixes Complete - All Endpoints Operational)  
**Purpose**: Mandatory requirements for any Cursor work on this system

---

## 🚨 **MANDATORY PRE-WORK CHECKLIST**

### **1. System State Verification**
```bash
# ALWAYS run this first
python3 system_cli.py

# Expected output: All services should show "up" status
```

### **2. Port Conflict Check**
```bash
# Check for port conflicts BEFORE starting work
lsof -i :8004  # Backend
lsof -i :3000  # Frontend
lsof -i :11434 # Ollama

# If ports are in use, kill processes or use different ports
```

### **3. Dependency Verification**
```bash
# Check Python dependencies
pip install -r requirements.txt

# Check frontend dependencies
cd frontend && npm install

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

### **4. Service Health Check**
```bash
# Verify main API is healthy
curl http://localhost:8004/api/system/health

# Expected response: {"status": "healthy", ...}
```

---

## 📋 **REQUIRED DOCUMENTATION UPDATES**

### **Before Making Changes**
1. **Read**: `SYSTEM_ARCHITECTURE_MAP.md`
2. **Read**: `FEATURE_DEPENDENCY_MAP.md`
3. **Understand**: Current system state and dependencies

### **After Making Changes**
1. **Update**: `SYSTEM_ARCHITECTURE_MAP.md` if architecture changes
2. **Update**: `FEATURE_DEPENDENCY_MAP.md` if dependencies change
3. **Update**: This document if requirements change

---

## 🔧 **WORKFLOW REQUIREMENTS**

### **Feature Development**
1. **Identify Dependencies**: Check what services your feature needs
2. **Start Required Services**: Use proper startup procedures
3. **Test Incrementally**: Test each change as you make it
4. **Verify Integration**: Ensure changes don't break other features

### **Bug Fixes**
1. **Identify Root Cause**: Check logs and system state
2. **Fix Systematically**: Don't make multiple changes at once
3. **Test Thoroughly**: Verify fix doesn't introduce new issues
4. **Document Changes**: Update relevant documentation

### **System Changes**
1. **Plan Impact**: Understand what will be affected
2. **Backup State**: Save current working configuration
3. **Change Gradually**: Make one change at a time
4. **Verify Continuously**: Test after each change

---

## 🚫 **FORBIDDEN ACTIONS**

### **Never Do These**
- ❌ Start services without checking port conflicts
- ❌ Make changes without understanding dependencies
- ❌ Skip health checks before and after changes
- ❌ Work on multiple features simultaneously
- ❌ Ignore error logs
- ❌ Make changes without testing
- ❌ Skip documentation updates

### **Always Do These**
- ✅ Check system state before starting
- ✅ Verify port availability
- ✅ Test changes incrementally
- ✅ Check logs for errors
- ✅ Update documentation
- ✅ Verify other features still work

---

## 🎯 **FEATURE-SPECIFIC REQUIREMENTS**

### **Backend Development (Port 8004)**
```bash
# Required checks
1. Check if main.py or consolidated_api_optimized.py is running
2. Verify Ollama is available (Port 11434)
3. Test API endpoints after changes
4. Check logs for errors

# Testing
curl http://localhost:8004/api/system/health
curl http://localhost:8004/api/chat/ -X POST -d '{"message": "test"}'
```

### **Frontend Development (Port 3000)**
```bash
# Required checks
1. Verify backend is running (Port 8004)
2. Check frontend dependencies are installed
3. Test UI functionality after changes
4. Verify API integration still works
5. Set environment variables in frontend/.env.local

# Environment Variables Required
NEXT_PUBLIC_CONSOLIDATED_API_URL=http://localhost:8004
NEXT_PUBLIC_AGENTIC_PLATFORM_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8004

# Testing
npm run dev
# Navigate to http://localhost:3000
# Test all UI components
# Verify frontend API proxy endpoints work
```

### **API Integration**
```bash
# Required checks
1. Verify all dependent services are running
2. Test API endpoints individually
3. Check error handling
4. Verify response formats

# Core API Endpoints (Port 8004)
curl http://localhost:8004/api/system/health
curl http://localhost:8004/api/chat/ -X POST -d '{"message": "test"}'
curl http://localhost:8004/api/agents/
curl http://localhost:8004/api/knowledge/
curl http://localhost:8004/api/admin/

# Enhanced API Endpoints
curl http://localhost:8004/api/voice/options
curl http://localhost:8004/api/voice/health
curl http://localhost:8004/api/rag/enhanced/search -X POST -d '{"query_text": "test"}'
curl http://localhost:8004/api/rag/enhanced/metrics
curl http://localhost:8004/api/rag/enhanced/health
curl http://localhost:8004/api/mcp/tools
curl http://localhost:8004/api/mcp/health
curl http://localhost:8004/api/mcp/execute -X POST -d '{"message": "system_info"}'
curl http://localhost:8004/api/mcp/detect-intent -X POST -d '{"text": "help me find information"}'
curl http://localhost:8004/api/healing/health
curl http://localhost:8004/api/healing/stats
curl http://localhost:8004/api/healing/analyze-and-heal -X POST -d '{"error_message": "test error"}'
curl http://localhost:8004/api/healing/research-unknown-error -X POST -d '{"error_message": "test error"}'
curl http://localhost:8004/api/vision/analyze -X POST -d '{"image_url": "test"}'
curl http://localhost:8004/api/vision/health
curl http://localhost:8004/api/model/status
curl http://localhost:8004/api/mlx/status
curl http://localhost:8004/api/system/metrics
curl http://localhost:8004/api/docling/health
curl http://localhost:8004/api/docling/status
curl http://localhost:8004/api/docling/models
curl http://localhost:8004/api/docling/formats
curl http://localhost:8004/api/docling/process -X POST -d '{"file_path": "test.pdf"}'
curl http://localhost:8004/api/docling/upload -X POST -F "file=@document.pdf"
curl http://localhost:8004/api/docling/batch -X POST -d '{"file_paths": ["doc1.pdf", "doc2.pdf"]}'
curl http://localhost:8004/api/docling/extract-text -X POST -d '{"document_id": "test", "text": "sample text"}'

# Testing
# Test each endpoint with curl or Postman
# Check for proper error responses
# Verify response times
```

### **Database/Knowledge Base**
```bash
# Required checks
1. Verify Weaviate is running (if used)
2. Check document indexing
3. Test search functionality
4. Verify data integrity

# Testing
curl http://localhost:8004/api/knowledge/
# Test search queries
# Verify results accuracy
```

### **Enhanced Features**
```bash
# Self-Healing System
curl http://localhost:8004/api/healing/health
curl http://localhost:8004/api/healing/analyze-and-heal -X POST -d '{"error_message": "test error"}'
curl http://localhost:8004/api/healing/research-unknown-error -X POST -d '{"error_message": "unknown error"}'

# Voice Services
curl http://localhost:8004/api/voice/options
curl http://localhost:8004/api/voice/health
curl http://localhost:8004/api/voice/synthesize -X POST -d '{"text": "Hello", "voice_profile": "assistant"}'

# Enhanced RAG System
curl http://localhost:8004/api/rag/enhanced/search -X POST -d '{"query_text": "search query"}'
curl http://localhost:8004/api/rag/enhanced/health

# Enhanced MCP Tools
curl http://localhost:8004/api/mcp/tools
curl http://localhost:8004/api/mcp/execute -X POST -d '{"tool": "calculator", "args": ["2+2"]}'

# Vision Processing
curl http://localhost:8004/api/vision/analyze -X POST -d '{"image_url": "https://example.com/image.jpg"}'
curl http://localhost:8004/api/vision/health

# Optimized Models
curl http://localhost:8004/api/model/status
curl http://localhost:8004/api/model/optimize -X POST -d '{"model_name": "qwen2.5:72b"}'

# MLX Processing
curl http://localhost:8004/api/mlx/status
curl http://localhost:8004/api/mlx/process -X POST -d '{"text": "process this"}'

        # Frontend-Backend Connectivity (Port 3000)
        curl http://localhost:3000/api/system/health
        curl http://localhost:3000/api/chat -X POST -d '{"message": "test"}'
        curl http://localhost:3000/api/voice/options
        curl http://localhost:3000/api/rag/query -X POST -d '{"query_text": "test"}'
        
        # Stable API Testing (Permanent Solution - No More Recurring Issues)
        curl -s http://localhost:8004/api/system/health | jq '.'  # Test health with graceful degradation
        curl -s -X POST -H "Content-Type: application/json" -d '{"message": "test"}' http://localhost:8004/api/chat/ | jq '.'  # Test chat with fallback
        curl -s http://localhost:8004/ | jq '.'  # Test root endpoint with system status
        
        # Stability Check (Run Before Any Work)
        python3 scripts/startup/ensure_stability.py  # Ensures system stability
```

---

## 🔍 **TROUBLESHOOTING REQUIREMENTS**

### **When Things Break**
1. **Check Logs First**: Always look at logs before making changes
2. **Identify Root Cause**: Don't just fix symptoms
3. **Test Fixes**: Verify fixes actually work
4. **Document Issues**: Record what went wrong and how it was fixed

### **Log Locations**
- Backend logs: `logs/backend_8004.log`
- Frontend logs: `logs/frontend_3000.log`
- System logs: `logs/` directory
- Docker logs: `docker logs <container_name>`

### **Common Issues**
- Port conflicts: Use `lsof -i :<port>` to find and kill processes
- Service not starting: Check dependencies and configuration
- API errors: Check backend logs and service health
- Frontend issues: Check browser console and network requests

---

## 📊 **PERFORMANCE REQUIREMENTS**

### **Response Time Targets**
- API responses: < 3 seconds
- Frontend loading: < 2 seconds
- Knowledge search: < 2 seconds
- System health: < 500ms

### **Resource Monitoring**
- Memory usage: Monitor for leaks
- CPU usage: Check for high utilization
- Disk usage: Monitor log and data growth
- Network: Check for connection issues

---

## 🔒 **SECURITY REQUIREMENTS**

### **Development Security**
- Never commit secrets or API keys
- Use environment variables for configuration
- Validate all inputs
- Handle errors gracefully

### **Production Security**
- Use HTTPS in production
- Implement proper authentication
- Monitor for security issues
- Keep dependencies updated

---

## 📈 **MONITORING REQUIREMENTS**

### **Health Monitoring**
```bash
# Regular health checks
curl http://localhost:8004/api/system/health

# Enhanced feature health checks
curl http://localhost:8004/api/healing/health
curl http://localhost:8004/api/voice/health
curl http://localhost:8004/api/rag/enhanced/health
curl http://localhost:8004/api/vision/health
curl http://localhost:8004/api/model/status
curl http://localhost:8004/api/mlx/status
curl http://localhost:8004/api/docling/health
curl http://localhost:8004/api/docling/status
curl http://localhost:8004/api/mcp/health
curl http://localhost:8004/api/system/metrics

# Service status
python3 system_cli.py

# Performance monitoring
# Check logs for performance issues
# Monitor resource usage
```

### **Error Monitoring**
- Check logs regularly
- Monitor error rates
- Track performance metrics
- Alert on critical issues

---

## 🎯 **SUCCESS CRITERIA**

### **Feature Complete**
- ✅ All tests pass
- ✅ No errors in logs
- ✅ Performance targets met
- ✅ Documentation updated
- ✅ Other features still work

### **Bug Fix Complete**
- ✅ Root cause identified and fixed
- ✅ No new issues introduced
- ✅ All related tests pass
- ✅ Documentation updated
- ✅ System stable

### **System Change Complete**
- ✅ All services healthy
- ✅ No port conflicts
- ✅ All features working
- ✅ Performance maintained
- ✅ Documentation updated

---

## 📞 **SUPPORT RESOURCES**

### **Documentation**
- `SYSTEM_ARCHITECTURE_MAP.md` - System overview
- `FEATURE_DEPENDENCY_MAP.md` - Feature dependencies
- `API_ENDPOINT_REFERENCE.md` - Complete API endpoint reference
- `README.md` - Project overview
- `docs/` directory - Additional documentation

### **Tools**
- `system_cli.py` - System management
- `start_integrated_system.sh` - System startup
- Health check endpoints
- Log files

### **Emergency Procedures**
1. **System Down**: Check logs, restart services
2. **Port Conflicts**: Kill conflicting processes
3. **Dependency Issues**: Reinstall dependencies
4. **Data Corruption**: Restore from backup

---

**⚠️ CRITICAL**: These requirements are MANDATORY. Failure to follow them will result in system instability and recurring issues. Always check system state before making changes.
