# 🤖 Lightweight Document Agent

A **resource-efficient, single-container agent** for document processing that integrates with your existing grading system.

## 🎯 Design Philosophy

**Small but Capable** - This agent is designed to be:
- ✅ **Resource-efficient**: 512MB RAM max, 50% CPU max
- ✅ **Lightweight**: Single container, minimal dependencies
- ✅ **Graded**: Integrates with your existing grading system
- ✅ **Monitored**: Real-time resource and performance monitoring
- ✅ **Safe**: Won't blow out system resources

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                Lightweight Document Agent               │
│                    (Single Container)                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────┐ │
│  │  Document       │  │  Resource       │  │ Grading │ │
│  │  Processing     │  │  Monitor        │  │ System  │ │
│  │  Engine         │  │  (psutil)       │  │ (Your   │ │
│  │                 │  │                 │  │ Existing│ │
│  └─────────────────┘  └─────────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Knowledge     │    │     Redis       │    │   Weaviate      │
│   Base (8004)   │    │   (6379)        │    │   (8080)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Start the Agent

```bash
# Make the startup script executable
chmod +x start-lightweight-agent.sh

# Start the lightweight agent
./start-lightweight-agent.sh
```

### 2. Check Agent Health

```bash
curl http://localhost:8010/health
```

### 3. Start Document Migration

```bash
curl -X POST http://localhost:8010/migrate
```

### 4. Check Grading Report

```bash
curl http://localhost:8010/grading/report
```

## 📊 Resource Management

### **Hard Limits**
- **Memory**: 512MB maximum
- **CPU**: 50% maximum  
- **Batch Size**: 10 documents per batch
- **Concurrent Tasks**: 2 maximum

### **Resource Monitoring**
- Real-time memory and CPU monitoring
- Automatic task throttling when limits approached
- Graceful degradation under resource pressure
- Health checks every 60 seconds

### **Safety Features**
- **Resource Violation Detection**: Agent pauses when limits exceeded
- **Automatic Recovery**: Resumes when resources free up
- **Graceful Shutdown**: Clean exit on resource exhaustion
- **Progress Preservation**: Work saved before pausing

## 🎯 Grading System Integration

### **Your Existing Grading System**
The agent integrates with your existing grading infrastructure:
- `src.core.assessment.grading_integration.GradingIntegrationSystem`
- `src.core.monitoring.model_grading_system.grade_response`

### **Agent Assessment**
The agent uses your grading system to assess its own performance:
- **Performance Score**: Based on task completion and efficiency
- **Resource Efficiency**: Memory and CPU usage evaluation
- **Quality Metrics**: Document processing quality assessment
- **Recommendations**: Actionable improvement suggestions

### **Grading Endpoints**
```bash
# Get comprehensive grading report
GET /grading/report

# Example response:
{
  "agent_id": "doc-agent-001",
  "overall_grade": "B+",
  "numeric_score": 87.5,
  "confidence_level": "high",
  "risk_level": "low",
  "recommended_actions": [
    "Consider increasing batch size for better efficiency",
    "Monitor memory usage more closely"
  ],
  "quality_metrics": {
    "accuracy": 0.92,
    "efficiency": 0.88,
    "reliability": 0.95
  }
}
```

## 🔧 Configuration

### **Environment Variables**
```bash
AGENT_ID=doc-agent-001              # Unique agent identifier
MAX_MEMORY_MB=512                   # Memory limit in MB
MAX_CPU_PERCENT=50                  # CPU limit percentage
BATCH_SIZE=10                       # Documents per batch
MAX_CONCURRENT_TASKS=2              # Max parallel tasks
WEAVIATE_HOST=weaviate              # Weaviate hostname
WEAVIATE_HTTP_PORT=8080            # Weaviate HTTP port
KNOWLEDGE_BASE_URL=http://knowledge-base:8004
REDIS_URL=redis://redis:6379        # Redis connection
LOG_LEVEL=INFO                      # Logging level
```

### **Docker Resource Limits**
```yaml
deploy:
  resources:
    limits:
      memory: 512M      # Hard memory limit
      cpus: '0.5'       # Hard CPU limit
    reservations:
      memory: 256M      # Guaranteed memory
      cpus: '0.25'      # Guaranteed CPU
```

## 📡 API Endpoints

### **Health & Status**
```bash
GET  /health                    # Health check with resource status
GET  /status                    # Detailed agent status
```

### **Document Processing**
```bash
POST /migrate                   # Start document migration
```

### **Grading & Monitoring**
```bash
GET  /grading/report           # Get grading system assessment
```

## 🔍 Monitoring & Debugging

### **Resource Monitoring**
```bash
# Check current resource usage
curl http://localhost:8010/health | jq '.resources'

# Example response:
{
  "memory_mb": 234.5,
  "memory_limit_mb": 512,
  "cpu_percent": 23.1,
  "cpu_limit_percent": 50,
  "healthy": true
}
```

### **Agent Status**
```bash
# Get detailed status
curl http://localhost:8010/status | jq '.'

# Example response:
{
  "agent_id": "doc-agent-001",
  "resources": { ... },
  "active_tasks": 1,
  "documents_processed": 45,
  "last_grading_report": { ... },
  "timestamp": "2025-10-01T18:30:00"
}
```

### **View Logs**
```bash
# Follow agent logs
docker-compose -f docker-compose.lightweight.yml logs -f doc-agent

# Check specific log files
docker exec lightweight-doc-agent tail -f /app/logs/agent.log
```

## 🎯 Migration Process

### **1. Document Discovery**
- Searches Knowledge Base using targeted queries
- Retrieves documents in small batches (10 at a time)
- Deduplicates by URL to avoid processing same document twice

### **2. Resource-Aware Processing**
- Checks resource limits before each batch
- Pauses processing if limits exceeded
- Resumes automatically when resources available

### **3. Progress Reporting**
- Reports progress to grading system via Redis
- Stores intermediate results for recovery
- Provides real-time status updates

### **4. Quality Assurance**
- Uses your existing grading system for assessment
- Generates performance reports
- Provides actionable recommendations

## 🛠️ Troubleshooting

### **Common Issues**

1. **Agent Won't Start**
   ```bash
   # Check Docker logs
   docker-compose -f docker-compose.lightweight.yml logs doc-agent
   
   # Check if base services are running
   docker-compose ps
   ```

2. **Resource Limits Exceeded**
   ```bash
   # Check current resource usage
   curl http://localhost:8010/health
   
   # Reduce batch size if needed
   # Edit docker-compose.lightweight.yml: BATCH_SIZE=5
   ```

3. **Grading System Not Available**
   ```bash
   # Check if grading system files exist
   ls -la src/core/assessment/grading_integration.py
   
   # Agent will fall back to basic monitoring
   curl http://localhost:8010/grading/report
   ```

4. **Migration Stuck**
   ```bash
   # Check agent status
   curl http://localhost:8010/status
   
   # Restart migration
   curl -X POST http://localhost:8010/migrate
   ```

### **Performance Tuning**

1. **Increase Batch Size** (if resources allow):
   ```yaml
   environment:
     - BATCH_SIZE=20
   ```

2. **Increase Memory Limit** (if system allows):
   ```yaml
   deploy:
     resources:
       limits:
         memory: 1G
   ```

3. **Adjust CPU Limit**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1.0'
   ```

## 🔒 Security & Safety

- **Resource Isolation**: Hard Docker limits prevent resource exhaustion
- **Read-Only Volumes**: Agent can't modify source data
- **Network Isolation**: Runs in isolated Docker network
- **Health Monitoring**: Automatic restart on failure
- **Graceful Degradation**: Continues working under resource pressure

## 📈 Benefits

✅ **Resource Efficient**: Won't overwhelm your system  
✅ **Graded Performance**: Uses your existing grading system  
✅ **Real-time Monitoring**: Live resource and progress tracking  
✅ **Automatic Recovery**: Self-healing under resource pressure  
✅ **Safe Operation**: Hard limits prevent system overload  
✅ **Easy Management**: Simple API for control and monitoring  

## 🎉 Summary

This lightweight agent is designed to be **small but capable**:

- **512MB RAM max** - Won't blow out resources
- **Single container** - Simple deployment and management  
- **Your grading system** - Integrates with existing infrastructure
- **Resource monitoring** - Real-time limits and health checks
- **Safe operation** - Hard limits and graceful degradation

**Perfect for checking in on with your grading system while keeping resource usage minimal!**

---

**🚀 Ready to start? Run `./start-lightweight-agent.sh` and let the agent handle your document migration efficiently!**
