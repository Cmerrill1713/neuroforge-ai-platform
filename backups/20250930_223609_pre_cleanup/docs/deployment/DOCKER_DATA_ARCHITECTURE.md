# Docker Data Architecture - NeuroForge System

## 🎯 Architecture Principle
**ALL knowledge and data operations run through Docker containers**

## 📊 Data Layer Services

### Weaviate (Knowledge Graph + Vector DB)
- **Container**: `weaviate`
- **Image**: `semitechnologies/weaviate:latest` (v1.33.0)
- **External Port**: `8090` (HTTP), `50051` (gRPC)
- **Internal Port**: `8080`
- **Network**: `agentic-engineering-platform_default`
- **Purpose**: Primary knowledge graph with vector search
- **Schema Classes**: 
  - `ComprehensiveDocument`
  - `KnowledgeDocument`
  - `Document`
  - `MetaAIDocument`
- **Current Objects**: 5 documents loaded

### PostgreSQL (Structured Data)
- **Container**: `ai-postgres` and `db`
- **Image**: `postgres:15-alpine`
- **External Ports**: `5432`, `5433`
- **Network**: `agentic-engineering-platform_default`
- **Purpose**: Relational data, user sessions, audit logs
- **Extensions**: pgvector for vector operations

### Redis (Caching & Sessions)
- **Container**: `redis`
- **Image**: `redis:7-alpine`
- **External Port**: `6379`
- **Network**: `agentic-engineering-platform_default`
- **Purpose**: Response caching, session storage, pub/sub

### Unified Knowledge Base
- **Container**: `unified-knowledge-base`
- **Image**: `agentic-engineering-platform-knowledge-base`
- **External Port**: `8001`
- **Internal Port**: `8000`
- **Network**: `agentic-engineering-platform_default`
- **Purpose**: Knowledge base API service
- **Environment**: `KNOWLEDGE_BASES=indydevdan_apify,indydevdan_2025,indydevdan_searxng`

## 🤖 Application Layer

### Agentic Platform
- **Container**: `agentic-engineering-platform-agentic-platform-1`
- **External Ports**: `8000` (API), `8080` (WebSocket)
- **Network**: `agentic-engineering-platform_default`
- **Purpose**: Main agentic AI platform
- **Status**: Running, healthy

### Consolidated API (Port 8004)
- **Container**: Currently running as local process
- **Should Be**: Dockerized
- **Purpose**: Consolidated AI chat API
- **Status**: Needs containerization

### Frontend (Port 3000)
- **Container**: Currently running as local process  
- **Should Be**: Dockerized
- **Purpose**: Next.js frontend
- **Status**: Needs containerization

## 📈 Monitoring Layer

### Prometheus (Metrics)
- **Container**: `agentic-monitoring`
- **External Port**: `9090`
- **Purpose**: Time-series metrics collection

### Grafana (Visualization)
- **Container**: `agentic-grafana`
- **External Port**: `3002`
- **Purpose**: Metrics dashboards and visualization

### Elasticsearch (Logging)
- **Container**: `agentic-logging`
- **External Port**: `9200`
- **Purpose**: Centralized log aggregation

### Kibana (Log Visualization)
- **Container**: `agentic-kibana`
- **External Port**: `5601`
- **Purpose**: Log search and visualization

## 🔧 Infrastructure Layer

### Nginx (Load Balancer)
- **Container**: `agentic-nginx`
- **External Ports**: `80` (HTTP), `443` (HTTPS)
- **Purpose**: Reverse proxy, load balancing, SSL termination

### Exporters (Metrics)
- `redis-exporter`: Port 9121
- `db-exporter`: Port 9187  
- `agentic-node-exporter`: Port 9100

### Alertmanager
- **Container**: `agentic-alertmanager`
- **External Port**: `9093`
- **Purpose**: Alert routing and management

### SearXNG (Web Search)
- **Container**: `agentic-searxng`
- **External Port**: `8081`
- **Purpose**: Meta search engine for web queries

## 🔄 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Port 3000)                     │
│                   Should route to Docker                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
┌─────────▼──────────┐          ┌────────▼─────────┐
│ Consolidated API   │          │ Agentic Platform │
│  (Port 8004)       │          │  (Port 8000)     │
│ Should use Docker  │          │  ✅ Docker       │
└─────────┬──────────┘          └────────┬─────────┘
          │                               │
          └───────────────┬───────────────┘
                          │
          ┌───────────────┴────────────────────┐
          │                                    │
┌─────────▼──────────┐              ┌─────────▼──────────┐
│   WEAVIATE         │              │   PostgreSQL       │
│ Knowledge Graph    │              │ Structured Data    │
│ ✅ Port 8090       │              │ ✅ Port 5432/5433  │
└────────────────────┘              └────────────────────┘
          │
┌─────────▼──────────┐
│      Redis         │
│   Caching Layer    │
│   ✅ Port 6379     │
└────────────────────┘
```

## 📋 Configuration Requirements

### Environment Variables Needed

**Agentic Platform:**
```env
WEAVIATE_URL=http://weaviate:8080
POSTGRES_URL=postgresql://user:pass@db:5432/neuroforge
REDIS_URL=redis://redis:6379
```

**Consolidated API (when Dockerized):**
```env
WEAVIATE_URL=http://weaviate:8080
POSTGRES_URL=postgresql://user:pass@ai-postgres:5432/ai_system
REDIS_URL=redis://redis:6379
AGENTIC_PLATFORM_URL=http://agentic-platform-1:8000
```

**Unified Knowledge Base:**
```env
WEAVIATE_URL=http://weaviate:8080
KNOWLEDGE_BASES=indydevdan_apify,indydevdan_2025,indydevdan_searxng
```

## ✅ Current Status

| Service | Status | Configured for Docker Data |
|---------|--------|----------------------------|
| Weaviate | ✅ Running | ✅ In network |
| PostgreSQL | ✅ Running | ✅ Ready |
| Redis | ✅ Running | ✅ Ready |
| Unified KB | ✅ Running | ⚠️ Needs Weaviate config |
| Agentic Platform | ✅ Running | ⚠️ Needs Weaviate config |
| Consolidated API | ❌ Local | ⚠️ Needs Dockerization |
| Frontend | ❌ Local | ⚠️ Needs Dockerization |

## 🎯 Action Items

1. **Update unified-knowledge-base** to use Weaviate
2. **Update agentic-platform** to use Weaviate for knowledge graph
3. **Stop using local file-based knowledge** 
4. **Route all queries through Docker services**
5. **Dockerize Consolidated API and Frontend**

