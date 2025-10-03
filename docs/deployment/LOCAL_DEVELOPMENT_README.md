# 🚀 NeuroForge Local Development Guide

**AI Development Platform - Local Development Setup**

---

## 📋 Quick Start

```bash
# 1. Clone and setup
git clone <repository>
cd neuroforge

# 2. Start local environment
./scripts/deploy-local.sh start

# 3. Check everything is working
./scripts/health-local.sh

# 4. Open in browser
open http://localhost:3000  # Frontend
open http://localhost:8000/docs  # API Documentation
```

**That's it! NeuroForge is now running locally.** 🎉

---

## 🏗️ Architecture Overview

NeuroForge local development includes:

- **API Backend** (FastAPI) - `http://localhost:8000`
- **Frontend** (Next.js) - `http://localhost:3000`
- **PostgreSQL Database** - `localhost:5432`
- **Redis Cache** - `localhost:6379`
- **Weaviate Vector DB** - `localhost:8080`

### Optional Services
- **Prometheus Monitoring** - `http://localhost:9090`
- **Grafana Dashboards** - `http://localhost:3001`
- **PgAdmin** (DB Admin) - `http://localhost:5050`
- **RedisInsight** (Cache Admin) - `http://localhost:5540`

---

## 🚀 Development Commands

### Start Services

```bash
# Basic services (API, Frontend, Databases)
./scripts/deploy-local.sh start

# With monitoring
./scripts/deploy-local.sh start-monitoring

# With development tools
./scripts/deploy-local.sh start-dev-tools

# All services
./scripts/deploy-local.sh start-monitoring && ./scripts/deploy-local.sh start-dev-tools
```

### Stop Services
```bash
./scripts/deploy-local.sh stop
```

### Check Status
```bash
./scripts/deploy-local.sh status
```

### View Logs
```bash
# All logs
./scripts/deploy-local.sh logs

# Specific service logs
./scripts/deploy-local.sh logs neuroforge-api
./scripts/deploy-local.sh logs neuroforge-frontend
```

### Health Check
```bash
./scripts/health-local.sh
```

### Reset Everything
```bash
# WARNING: This deletes all data
./scripts/deploy-local.sh reset
```

---

## 🔧 Development Workflow

### 1. Code Changes
- Edit files in `src/` (backend) or `frontend/` (frontend)
- Changes auto-reload (hot reload enabled)
- Check logs for any errors: `./scripts/deploy-local.sh logs`

### 2. Database Changes
```bash
# Access database directly
psql -h localhost -U neuroforge -d neuroforge
# Password: dev_password

# Or use PgAdmin at http://localhost:5050
# Email: admin@neuroforge.dev
# Password: dev_password
```

### 3. Testing
```bash
# Run tests (when available)
pytest

# Check code quality
flake8 src
black --check src
```

### 4. API Documentation
- **Interactive API Docs**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`

---

## 📁 Project Structure

```
neuroforge/
├── src/                    # Backend Python code
│   ├── api/               # FastAPI endpoints
│   ├── core/              # Core business logic
│   ├── services/          # External service integrations
│   └── utils/             # Utility functions
├── frontend/              # Next.js frontend
├── scripts/               # Development scripts
│   ├── deploy-local.sh    # Local deployment
│   └── health-local.sh    # Health checks
├── docker-compose.local.yml # Local Docker setup
├── Dockerfile.dev         # Development Dockerfile
├── env.local             # Local environment config
└── knowledge_base/       # Knowledge base data
```

---

## 🔧 Configuration

### Environment Variables
Edit `env.local` for local configuration:

```bash
# Development settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Database (auto-configured)
DATABASE_URL=postgresql://neuroforge:dev_password@neuroforge-postgres:5432/neuroforge
REDIS_URL=redis://neuroforge-redis:6379
```

### Custom Configuration
- Database schemas in `scripts/postgres-init.sql`
- Monitoring config in `monitoring/`
- Docker setup in `docker-compose.local.yml`

---

## 🐛 Troubleshooting

### Services Won't Start
```bash
# Check Docker
docker --version
docker-compose --version

# Check logs
./scripts/deploy-local.sh logs

# Restart services
./scripts/deploy-local.sh restart
```

### Database Connection Issues
```bash
# Check database container
docker ps | grep postgres

# Test connection
psql -h localhost -U neuroforge -d neuroforge

# Reset database
./scripts/deploy-local.sh reset
```

### Port Conflicts
```bash
# Check what's using ports
lsof -i :8000
lsof -i :3000

# Change ports in docker-compose.local.yml if needed
```

### Frontend Build Issues
```bash
# Check frontend logs
./scripts/deploy-local.sh logs neuroforge-frontend

# Rebuild frontend
docker-compose -f docker-compose.local.yml build neuroforge-frontend
```

---

## 🔄 Development Tips

### Hot Reload
- Backend: Auto-reloads on Python file changes
- Frontend: Auto-reloads on React/Next.js changes
- Database: Schema changes require manual migration

### Debugging
```bash
# API debug logs
./scripts/deploy-local.sh logs neuroforge-api

# Database queries
# Use PgAdmin or psql for database debugging

# Network issues
curl -v http://localhost:8000/health
```

### Performance
- Use Redis for caching (enabled by default)
- Monitor with `./scripts/health-local.sh`
- Check resource usage with `docker stats`

---

## 🚀 Next Steps

1. **Explore the API**: Visit `http://localhost:8000/docs`
2. **Check the Frontend**: Open `http://localhost:3000`
3. **Database Admin**: Use PgAdmin at `http://localhost:5050`
4. **Monitoring**: Enable with `./scripts/deploy-local.sh start-monitoring`

---

## 📞 Support

### Local Development Issues
- Check logs: `./scripts/deploy-local.sh logs`
- Health check: `./scripts/health-local.sh`
- Reset environment: `./scripts/deploy-local.sh reset`

### Documentation
- API Docs: `http://localhost:8000/docs`
- Code comments in source files
- This README for setup instructions

---

**Happy developing with NeuroForge!** 🤖✨

**Quick start reminder:**
```bash
./scripts/deploy-local.sh start
./scripts/health-local.sh
open http://localhost:3000
```
