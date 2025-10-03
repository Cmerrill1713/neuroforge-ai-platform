# 🐳 Docker Containerization Guide

This guide provides comprehensive instructions for containerizing and deploying your AI system using Docker.

## 📋 Prerequisites

- **Docker**: Version 20.10+ installed
- **Docker Compose**: Version 2.0+ installed
- **Git**: For cloning the repository
- **curl**: For health checks

## 🚀 Quick Start

### 1. Build and Run Development Environment

```bash
# Build all images
./docker-deploy.sh build

# Start development environment
./docker-deploy.sh dev

# Check health
./docker-deploy.sh health
```

### 2. Access Your Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🏗️ Architecture Overview

### Services

| Service | Port | Description |
|---------|------|-------------|
| **Frontend** | 3000 | Next.js React application |
| **Backend** | 8000 | FastAPI Python server |
| **TTS Server** | 8086 | Text-to-Speech service (optional) |
| **Redis** | 6379 | Caching layer (optional) |
| **PostgreSQL** | 5432 | Database (optional) |

### Docker Images

- **ai-backend**: Python FastAPI server
- **ai-frontend**: Next.js React application
- **nginx**: Reverse proxy (production only)

## 🔧 Development Environment

### Basic Setup

```bash
# Clone repository
git clone <your-repo-url>
cd ai-system

# Build images
./docker-deploy.sh build

# Start services
./docker-deploy.sh dev

# View logs
./docker-deploy.sh logs
```

### With Optional Services

```bash
# Include TTS server
./docker-deploy.sh dev --profile tts

# Include caching
./docker-deploy.sh dev --profile cache

# Include database
./docker-deploy.sh dev --profile database

# Include monitoring
./docker-deploy.sh dev --profile monitoring
```

## 🏭 Production Environment

### Production Deployment

```bash
# Build production images
./docker-deploy.sh build --no-cache

# Start production environment
./docker-deploy.sh prod

# With monitoring
./docker-deploy.sh prod --profile monitoring
```

### Production Features

- **Nginx Reverse Proxy**: Load balancing and SSL termination
- **Resource Limits**: Memory and CPU constraints
- **Health Checks**: Automatic container health monitoring
- **Logging**: Structured logging with rotation
- **Security**: Rate limiting and security headers

## 📊 Monitoring and Observability

### Health Checks

```bash
# Check container health
./docker-deploy.sh health

# Manual health checks
curl http://localhost:8000/health  # Backend
curl http://localhost:3000/api/health  # Frontend
```

### Monitoring Stack (Optional)

```bash
# Start with monitoring
./docker-deploy.sh prod --profile monitoring

# Access monitoring tools
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001 (admin/admin)
```

## 🛠️ Management Commands

### Container Management

```bash
# Stop all containers
./docker-deploy.sh stop

# Clean up everything
./docker-deploy.sh clean

# View logs
./docker-deploy.sh logs

# Check health
./docker-deploy.sh health
```

### Manual Docker Commands

```bash
# Build specific image
docker build -f Dockerfile.backend -t ai-backend:latest .
docker build -f Dockerfile.frontend -t ai-frontend:latest .

# Run individual containers
docker run -p 8000:8000 ai-backend:latest
docker run -p 3000:3000 ai-frontend:latest

# View container logs
docker logs ai-backend
docker logs ai-frontend

# Execute commands in containers
docker exec -it ai-backend bash
docker exec -it ai-frontend sh
```

## 🔒 Security Considerations

### Production Security

1. **Environment Variables**: Use `.env` files for secrets
2. **Network Security**: Use Docker networks for isolation
3. **Resource Limits**: Prevent resource exhaustion
4. **Image Security**: Use official base images
5. **Regular Updates**: Keep images updated

### Security Headers (Nginx)

- X-Frame-Options: SAMEORIGIN
- X-XSS-Protection: 1; mode=block
- X-Content-Type-Options: nosniff
- Content-Security-Policy: configured

## 📈 Performance Optimization

### Resource Allocation

```yaml
# Production resource limits
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
    reservations:
      memory: 512M
      cpus: '0.5'
```

### Caching Strategy

- **Static Assets**: 1 year cache
- **API Responses**: Configurable TTL
- **Redis**: Optional caching layer

## 🐛 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check port usage
   lsof -i :3000
   lsof -i :8000
   
   # Kill conflicting processes
   kill -9 <PID>
   ```

2. **Build Failures**
   ```bash
   # Clean build
   ./docker-deploy.sh clean
   ./docker-deploy.sh build --no-cache
   ```

3. **Container Won't Start**
   ```bash
   # Check logs
   docker logs <container-name>
   
   # Check health
   ./docker-deploy.sh health
   ```

4. **Memory Issues**
   ```bash
   # Increase Docker memory limit
   # Docker Desktop > Settings > Resources > Memory
   ```

### Debug Mode

```bash
# Run with debug output
docker-compose up --verbose

# Check container status
docker-compose ps

# Inspect container
docker inspect <container-name>
```

## 📝 Environment Variables

### Backend Environment

```bash
PYTHONPATH=/app
PYTHONUNBUFFERED=1
NODE_ENV=production
BACKEND_API_URL=http://backend:8000
```

### Frontend Environment

```bash
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1
NEXT_PUBLIC_API_URL=http://localhost:8000
BACKEND_API_URL=http://backend:8000
```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Docker Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker images
        run: ./docker-deploy.sh build
      - name: Run tests
        run: ./docker-deploy.sh health
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Next.js Docker Guide](https://nextjs.org/docs/deployment#docker-image)
- [FastAPI Docker Guide](https://fastapi.tiangolo.com/deployment/docker/)

## 🆘 Support

If you encounter issues:

1. Check the logs: `./docker-deploy.sh logs`
2. Verify health: `./docker-deploy.sh health`
3. Clean and rebuild: `./docker-deploy.sh clean && ./docker-deploy.sh build`
4. Check Docker resources and permissions

---

**🎉 Your AI system is now fully containerized and ready for production deployment!**
