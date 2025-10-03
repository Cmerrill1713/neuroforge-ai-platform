# 🤖 Agent-Based Document Processing System

A comprehensive Docker-based agent ecosystem for intelligent document migration, processing, and management.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Agent Monitor │    │   Orchestrator  │    │ Document Agent  │
│   (Port 8008)   │◄──►│   (Port 8007)   │◄──►│   (Port 8006)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Redis       │    │   PostgreSQL    │    │    Weaviate      │
│   (Port 6379)   │    │   (Port 5432)   │    │   (Port 8080)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Knowledge Base  │    │   Agent Tasks   │    │  Vector Store   │
│   (Port 8004)   │    │   Management    │    │   (Port 8090)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Start the Agent System

```bash
# Make the startup script executable
chmod +x start-agents.sh

# Start the complete agent ecosystem
./start-agents.sh
```

### 2. Access the Monitor Dashboard

Open your browser and navigate to: **http://localhost:8008**

### 3. Start Document Migration

From the dashboard, click **"Start Document Migration"** or use the API:

```bash
curl -X POST http://localhost:8007/migrate/documents
```

## 📋 Components

### 🤖 Document Processing Agent
- **Port**: 8006
- **Role**: Handles document migration and processing
- **Features**:
  - Migrates documents from Knowledge Base to Weaviate
  - Processes and enhances document metadata
  - Provides health monitoring and status reporting
  - Supports batch processing with configurable parameters

### 🎯 Agent Orchestrator
- **Port**: 8007
- **Role**: Manages and coordinates all agents
- **Features**:
  - Agent registration and heartbeat monitoring
  - Task creation and distribution
  - Progress tracking and error handling
  - Centralized agent management

### 📊 Agent Monitor Dashboard
- **Port**: 8008
- **Role**: Real-time monitoring and management interface
- **Features**:
  - Live agent status monitoring
  - Task progress visualization
  - System metrics dashboard
  - One-click migration controls

### 📚 Knowledge Base Service
- **Port**: 8004
- **Role**: Source system for document migration
- **Features**:
  - 464 documents with 2,320 chunks
  - Search API for document retrieval
  - Statistics and health monitoring

## 🔧 Configuration

### Environment Variables

```bash
# Agent Configuration
AGENT_ID=doc-processor-001
AGENT_ROLE=document_migration
LOG_LEVEL=INFO

# Service URLs
WEAVIATE_HOST=weaviate
WEAVIATE_HTTP_PORT=8080
WEAVIATE_GRPC_PORT=50051
KNOWLEDGE_BASE_URL=http://knowledge-base:8004
REDIS_URL=redis://redis:6379
POSTGRES_URL=postgresql://postgres:password@postgres:5432/agentic_platform
```

### Docker Compose Services

The system uses two Docker Compose files:

1. **`docker-compose.yml`** - Base services (Redis, PostgreSQL, Weaviate)
2. **`docker-compose.agents.yml`** - Agent services (Document Agent, Orchestrator, Monitor)

## 📡 API Endpoints

### Document Agent (Port 8006)
```bash
GET  /health                    # Health check
GET  /status                    # Agent status
POST /migrate                   # Start migration
GET  /migration/progress        # Migration progress
POST /process/documents         # Process documents
```

### Orchestrator (Port 8007)
```bash
GET  /health                    # Health check
GET  /status                    # Orchestrator status
GET  /agents                    # List registered agents
POST /agents/register           # Register agent
POST /tasks/create              # Create task
GET  /tasks/{task_id}          # Get task status
POST /migrate/documents         # Start document migration
```

### Monitor (Port 8008)
```bash
GET  /                          # Dashboard
GET  /api/status               # System status
POST /api/migrate              # Start migration
```

## 🔍 Monitoring and Debugging

### View Logs
```bash
# All agent services
docker-compose -f docker-compose.agents.yml logs -f

# Specific service
docker-compose -f docker-compose.agents.yml logs -f document-agent
docker-compose -f docker-compose.agents.yml logs -f agent-orchestrator
docker-compose -f docker-compose.agents.yml logs -f agent-monitor
```

### Check Service Health
```bash
# Document Agent
curl http://localhost:8006/health

# Orchestrator
curl http://localhost:8007/health

# Monitor
curl http://localhost:8008/api/status

# Knowledge Base
curl http://localhost:8004/api/knowledge/stats
```

### System Status
```bash
# Get orchestrator status
curl http://localhost:8007/status

# Get registered agents
curl http://localhost:8007/agents

# Get active tasks
curl http://localhost:8007/tasks
```

## 🎯 Migration Process

### 1. Document Discovery
The agent searches the Knowledge Base using multiple search terms to discover all documents:
- Generic terms: "test", "document", "content", "data"
- Technology terms: "github", "wikipedia", "youtube", "api"
- Programming terms: "python", "javascript", "docker"

### 2. Document Processing
Each document is processed and enhanced with:
- Processing metadata (timestamp, agent ID, version)
- Source attribution
- Keyword extraction
- Content validation

### 3. Weaviate Migration
Documents are migrated to Weaviate in batches:
- Batch size: 50 documents (configurable)
- Schema: KnowledgeDocument collection
- Properties: content, title, url, source_type, domain, keywords

### 4. Progress Tracking
Real-time progress monitoring through:
- Redis-based task queuing
- Heartbeat monitoring
- Status updates via API
- Dashboard visualization

## 🛠️ Troubleshooting

### Common Issues

1. **Agent Not Starting**
   ```bash
   # Check Docker logs
   docker-compose -f docker-compose.agents.yml logs document-agent
   
   # Check if base services are running
   docker-compose ps
   ```

2. **Migration Failing**
   ```bash
   # Check orchestrator logs
   docker-compose -f docker-compose.agents.yml logs agent-orchestrator
   
   # Check document agent logs
   docker-compose -f docker-compose.agents.yml logs document-agent
   ```

3. **Weaviate Connection Issues**
   ```bash
   # Check Weaviate health
   curl http://localhost:8080/v1/meta
   
   # Check Weaviate logs
   docker-compose logs weaviate
   ```

4. **Redis Connection Issues**
   ```bash
   # Check Redis health
   docker-compose exec redis redis-cli ping
   
   # Check Redis logs
   docker-compose logs redis
   ```

### Performance Optimization

1. **Batch Size Tuning**
   - Increase batch size for faster migration
   - Decrease batch size for better error handling

2. **Memory Management**
   - Monitor Redis memory usage
   - Adjust Weaviate memory limits

3. **Network Optimization**
   - Use internal Docker networks
   - Optimize connection pooling

## 🔒 Security Considerations

- All services run in isolated Docker containers
- Internal network communication only
- No external ports exposed unnecessarily
- Health checks for service monitoring
- Graceful error handling and recovery

## 📈 Scalability

The agent system is designed for horizontal scaling:

- **Multiple Document Agents**: Add more agents for parallel processing
- **Load Balancing**: Distribute tasks across multiple agents
- **Queue Management**: Redis-based task queuing for scalability
- **Monitoring**: Centralized monitoring for multiple agents

## 🎉 Benefits

✅ **Automated Migration**: No manual intervention required  
✅ **Real-time Monitoring**: Live progress tracking  
✅ **Error Recovery**: Automatic retry and error handling  
✅ **Scalable Architecture**: Easy to add more agents  
✅ **Docker-based**: Consistent deployment across environments  
✅ **Health Monitoring**: Comprehensive health checks  
✅ **Dashboard Interface**: User-friendly management interface  

## 📞 Support

For issues or questions:
1. Check the logs: `docker-compose -f docker-compose.agents.yml logs -f`
2. Check the monitor dashboard: http://localhost:8008
3. Verify service health: Use the health check endpoints
4. Review this documentation for troubleshooting steps

---

**🎯 Ready to migrate your 464 documents? Run `./start-agents.sh` and let the agents handle the rest!**
