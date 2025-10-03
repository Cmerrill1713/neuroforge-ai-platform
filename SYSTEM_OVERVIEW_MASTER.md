# 🎯 SYSTEM OVERVIEW - MASTER DOCUMENT
**Last Updated**: January 2025  
**Purpose**: Complete system overview and reference for all development work

---

## 🚨 **CRITICAL: READ THIS FIRST**

This document is the **SINGLE SOURCE OF TRUTH** for the entire system. Before working on ANY feature or making ANY changes:

1. **READ**: This entire document
2. **FOLLOW**: All requirements in `CURSOR_WORK_REQUIREMENTS.md`
3. **CHECK**: System state before making changes
4. **VERIFY**: Dependencies are met

---

## 🗺️ **SYSTEM ARCHITECTURE OVERVIEW**

### **Current System State**
- ✅ **Consolidated API**: Port 8004 (Main service)
- ✅ **Frontend**: Port 3000 (Next.js interface)
- ✅ **Ollama**: Port 11434 (AI models)
- ⚠️ **Optional Services**: Ports 8000, 8005, 8086, 8087, 8090

### **Service Dependencies**
```
Frontend (3000) → Consolidated API (8004) → Ollama (11434)
Consolidated API (8004) → Optional Services (8000, 8005, 8086, 8087, 8090)
```

---

## 📋 **QUICK REFERENCE**

### **Essential Commands**
```bash
# Check system status
python3 system_cli.py

# Start main system
python3 main.py

# Start frontend
cd frontend && npm run dev

# Check health
curl http://localhost:8004/api/system/health
```

### **Key Files**
- `main.py` - Main entry point
- `consolidated_api_optimized.py` - Alternative entry point
- `frontend/` - Frontend application
- `src/api/` - API implementations
- `system_cli.py` - System management

### **Critical Ports**
- **8004**: Consolidated API (REQUIRED)
- **3000**: Frontend (REQUIRED)
- **11434**: Ollama (REQUIRED)

---

## 🏗️ **SYSTEM COMPONENTS**

### **1. Consolidated API (Port 8004)**
**Purpose**: Main API server with all integrations
**Features**:
- Chat system with AI models
- Agent management
- Knowledge base search
- System health monitoring
- MCP tool integration
- Voice services (optional)
- Evolutionary optimization (optional)

**Key Endpoints**:
- `GET /` - System status
- `POST /api/chat/` - Chat interactions
- `GET /api/agents/` - Agent management
- `GET /api/knowledge/` - Knowledge search
- `GET /api/system/health` - Health check

### **2. Frontend (Port 3000)**
**Purpose**: User interface
**Framework**: Next.js 14.2.33
**Features**:
- Chat interface
- Agent selection
- Knowledge base access
- System monitoring
- Voice controls

### **3. Ollama (Port 11434)**
**Purpose**: Local AI models
**Models Available**:
- `qwen2.5:72b` - Complex reasoning
- `qwen2.5:14b` - Balanced performance
- `qwen2.5:7b` - Fast responses
- `mistral:7b` - Code generation
- `llama3.2:3b` - Simple tasks

---

## 🔧 **DEVELOPMENT WORKFLOW**

### **Starting Development**
1. **Check System State**: `python3 system_cli.py`
2. **Verify Ports**: Check for conflicts
3. **Start Services**: Use proper startup procedures
4. **Test Health**: Verify all services are working

### **Making Changes**
1. **Identify Dependencies**: Check what your feature needs
2. **Start Required Services**: Ensure dependencies are running
3. **Make Changes**: Work incrementally
4. **Test Changes**: Verify functionality
5. **Update Documentation**: Keep docs current

### **Testing Changes**
1. **Health Check**: `curl http://localhost:8004/api/system/health`
2. **Feature Test**: Test specific functionality
3. **Integration Test**: Verify other features still work
4. **Log Check**: Look for errors

---

## 🚫 **COMMON MISTAKES TO AVOID**

### **Port Conflicts**
- ❌ Starting services without checking port availability
- ❌ Using wrong ports for services
- ❌ Not killing conflicting processes

### **Dependency Issues**
- ❌ Working on features without required services
- ❌ Making changes without understanding dependencies
- ❌ Skipping health checks

### **Testing Issues**
- ❌ Not testing changes before moving on
- ❌ Ignoring error logs
- ❌ Not verifying other features still work

---

## 🔍 **TROUBLESHOOTING GUIDE**

### **System Won't Start**
1. Check port conflicts: `lsof -i :<port>`
2. Verify dependencies: `pip install -r requirements.txt`
3. Check logs: `logs/` directory
4. Restart services: Use proper startup procedures

### **API Errors**
1. Check backend logs: `logs/backend_8004.log`
2. Verify Ollama: `curl http://localhost:11434/api/tags`
3. Test endpoints: Use curl or Postman
4. Check service health: `curl http://localhost:8004/api/system/health`

### **Frontend Issues**
1. Check browser console for errors
2. Verify backend is running
3. Check network requests
4. Restart frontend: `cd frontend && npm run dev`

---

## 📊 **PERFORMANCE TARGETS**

### **Response Times**
- API responses: < 3 seconds
- Frontend loading: < 2 seconds
- Knowledge search: < 2 seconds
- System health: < 500ms

### **Resource Usage**
- Memory: 4-8GB (depending on features)
- CPU: 2+ cores
- Storage: 10GB+ (for models and data)

---

## 🔒 **SECURITY CONSIDERATIONS**

### **Development**
- Use environment variables for configuration
- Validate all inputs
- Handle errors gracefully
- Never commit secrets

### **Production**
- Use HTTPS
- Implement authentication
- Monitor for security issues
- Keep dependencies updated

---

## 📈 **MONITORING & LOGGING**

### **Health Monitoring**
- System health: `GET /api/system/health`
- Service status: `python3 system_cli.py`
- Performance metrics: Check logs

### **Log Locations**
- Backend: `logs/backend_8004.log`
- Frontend: `logs/frontend_3000.log`
- System: `logs/` directory

### **Error Monitoring**
- Check logs regularly
- Monitor error rates
- Track performance metrics
- Alert on critical issues

---

## 🎯 **FEATURE DEVELOPMENT GUIDE**

### **Chat System**
- **Dependencies**: Ollama (Port 11434)
- **Testing**: `POST /api/chat/` with test message
- **Logs**: Check backend logs for errors

### **Knowledge Base**
- **Dependencies**: Weaviate (Port 8090) - Optional
- **Testing**: `GET /api/knowledge/`
- **Logs**: Check knowledge base logs

### **Agent Management**
- **Dependencies**: Ollama (Port 11434)
- **Testing**: `GET /api/agents/`
- **Logs**: Check agent selection logs

### **Voice Services**
- **Dependencies**: TTS (Port 8086), Whisper (Port 8087)
- **Testing**: Voice endpoint tests
- **Logs**: Check voice service logs

---

## 📚 **DOCUMENTATION STRUCTURE**

### **Master Documents**
- `SYSTEM_OVERVIEW_MASTER.md` - This document (READ FIRST)
- `SYSTEM_ARCHITECTURE_MAP.md` - Detailed architecture
- `FEATURE_DEPENDENCY_MAP.md` - Feature dependencies
- `CURSOR_WORK_REQUIREMENTS.md` - Development requirements

### **Additional Documentation**
- `README.md` - Project overview
- `docs/` directory - Detailed documentation
- `logs/` directory - System logs

---

## 🚀 **QUICK START GUIDE**

### **For New Developers**
1. **Read**: This entire document
2. **Check**: System requirements
3. **Install**: Dependencies
4. **Start**: Services using proper procedures
5. **Test**: System health
6. **Begin**: Development work

### **For Existing Developers**
1. **Check**: Current system state
2. **Verify**: Required services are running
3. **Review**: Recent changes
4. **Begin**: Development work

---

## 📞 **SUPPORT & HELP**

### **Self-Help Resources**
- System CLI: `python3 system_cli.py`
- Health checks: `curl http://localhost:8004/api/system/health`
- Logs: `logs/` directory
- Documentation: This document and related files

### **Emergency Procedures**
1. **System Down**: Check logs, restart services
2. **Port Conflicts**: Kill conflicting processes
3. **Dependency Issues**: Reinstall dependencies
4. **Data Corruption**: Restore from backup

---

## ✅ **SUCCESS CHECKLIST**

### **Before Starting Work**
- [ ] Read this document
- [ ] Check system state
- [ ] Verify port availability
- [ ] Start required services
- [ ] Test system health

### **After Making Changes**
- [ ] Test changes thoroughly
- [ ] Check logs for errors
- [ ] Verify other features work
- [ ] Update documentation
- [ ] Confirm performance targets

---

**🎯 REMEMBER**: This system has multiple interconnected components. Always understand the full impact of your changes before making them. When in doubt, check the documentation and test thoroughly.

---

**Last Updated**: January 2025  
**System Status**: ✅ **OPERATIONAL**  
**Version**: 2.0.0
