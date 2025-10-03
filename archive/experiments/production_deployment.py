#!/usr/bin/env python3
"""
Production Deployment Configuration for AI Assistant Platform
Comprehensive production setup with monitoring, logging, and deployment scripts.
"""

import os
import logging
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
import yaml

class ProductionDeployment:
    """
    Production deployment manager for the AI Assistant Platform.
    
    Features:
    - Environment configuration
    - Docker containerization
    - Monitoring and logging setup
    - Health checks and metrics
    - Security configurations
    - Backup and recovery
    """
    
    def __init__(self, project_root: str):
        """Initialize production deployment."""
        self.project_root = Path(project_root)
        self.logger = logging.getLogger(__name__)
        
    def create_docker_configuration(self) -> None:
        """Create Docker configuration for production deployment."""
        self.logger.info("🐳 Creating Docker configuration...")
        
        # Dockerfile for the API server
        dockerfile_content = """# Multi-stage Dockerfile for AI Assistant Platform
FROM python:3.9-slim as base

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY knowledge_base/ ./knowledge_base/
COPY *.py ./

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8004

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8004/api/system/health || exit 1

# Start command
CMD ["python", "-m", "uvicorn", "src.api.consolidated_api_architecture:create_consolidated_app", "--host", "0.0.0.0", "--port", "8004"]
"""
        
        # Docker Compose for full stack
        docker_compose_content = """version: '3.8'

services:
  ai-assistant-api:
    build: .
    ports:
      - "8004:8004"
    environment:
      - PYTHONPATH=/app
      - ENVIRONMENT=production
    volumes:
      - ./knowledge_base:/app/knowledge_base
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8004/api/system/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8004
    depends_on:
      - ai-assistant-api
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - ai-assistant-api
      - frontend
    restart: unless-stopped

volumes:
  knowledge_base:
  logs:
"""
        
        # Write Docker files
        (self.project_root / "Dockerfile").write_text(dockerfile_content)
        (self.project_root / "docker-compose.yml").write_text(docker_compose_content)
        
        self.logger.info("✅ Docker configuration created")
    
    def create_nginx_configuration(self) -> None:
        """Create Nginx configuration for production."""
        self.logger.info("🌐 Creating Nginx configuration...")
        
        nginx_config = """events {
    worker_connections 1024;
}

http {
    upstream api_backend {
        server ai-assistant-api:8004;
    }
    
    upstream frontend_backend {
        server frontend:3000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # API routes
        location /api/ {
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # CORS headers
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "Content-Type, Authorization";
            
            # Handle preflight requests
            if ($request_method = 'OPTIONS') {
                add_header Access-Control-Allow-Origin *;
                add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
                add_header Access-Control-Allow-Headers "Content-Type, Authorization";
                add_header Content-Length 0;
                add_header Content-Type text/plain;
                return 200;
            }
        }
        
        # Frontend routes
        location / {
            proxy_pass http://frontend_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }
    }
}
"""
        
        (self.project_root / "nginx.conf").write_text(nginx_config)
        self.logger.info("✅ Nginx configuration created")
    
    def create_monitoring_configuration(self) -> None:
        """Create monitoring and logging configuration."""
        self.logger.info("📊 Creating monitoring configuration...")
        
        # Prometheus configuration
        prometheus_config = """global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ai-assistant-api'
    static_configs:
      - targets: ['ai-assistant-api:8004']
    metrics_path: '/api/system/metrics'
    scrape_interval: 30s
"""
        
        # Logging configuration
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                },
                "simple": {
                    "format": "%(levelname)s - %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "formatter": "simple",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "detailed",
                    "filename": "/app/logs/ai_assistant.log",
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5
                }
            },
            "loggers": {
                "": {
                    "level": "DEBUG",
                    "handlers": ["console", "file"]
                }
            }
        }
        
        # Write configuration files
        (self.project_root / "prometheus.yml").write_text(prometheus_config)
        (self.project_root / "logging_config.json").write_text(json.dumps(logging_config, indent=2))
        
        self.logger.info("✅ Monitoring configuration created")
    
    def create_environment_configuration(self) -> None:
        """Create environment configuration files."""
        self.logger.info("🔧 Creating environment configuration...")
        
        # Production environment variables
        env_content = """# Production Environment Configuration
ENVIRONMENT=production
PYTHONPATH=/app
LOG_LEVEL=INFO

# API Configuration
API_HOST=0.0.0.0
API_PORT=8004
API_WORKERS=4

# Model Configuration
DEFAULT_CHAT_MODEL=qwen2.5:7b
FALLBACK_CHAT_MODEL=llama3.2:3b
VISION_MODEL=apple/FastVLM-7B
EMBEDDING_MODEL=Snowflake/snowflake-arctic-embed-m

# Performance Configuration
MAX_MEMORY_USAGE=0.85
MEMORY_CLEANUP_INTERVAL=300
LAZY_LOADING_ENABLED=true

# Security Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
API_KEY_REQUIRED=false

# Monitoring Configuration
METRICS_ENABLED=true
HEALTH_CHECK_INTERVAL=30
"""
        
        # Development environment variables
        env_dev_content = """# Development Environment Configuration
ENVIRONMENT=development
PYTHONPATH=/Users/christianmerrill/Prompt Engineering
LOG_LEVEL=DEBUG

# API Configuration
API_HOST=0.0.0.0
API_PORT=8004
API_WORKERS=1

# Model Configuration
DEFAULT_CHAT_MODEL=qwen2.5:7b
FALLBACK_CHAT_MODEL=llama3.2:3b
VISION_MODEL=apple/FastVLM-7B
EMBEDDING_MODEL=Snowflake/snowflake-arctic-embed-m

# Performance Configuration
MAX_MEMORY_USAGE=0.75
MEMORY_CLEANUP_INTERVAL=180
LAZY_LOADING_ENABLED=true

# Security Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
API_KEY_REQUIRED=false

# Monitoring Configuration
METRICS_ENABLED=true
HEALTH_CHECK_INTERVAL=15
"""
        
        # Write environment files
        (self.project_root / ".env.production").write_text(env_content)
        (self.project_root / ".env.development").write_text(env_dev_content)
        
        self.logger.info("✅ Environment configuration created")
    
    def create_deployment_scripts(self) -> None:
        """Create deployment and management scripts."""
        self.logger.info("📜 Creating deployment scripts...")
        
        # Production deployment script
        deploy_script = """#!/bin/bash
# Production Deployment Script for AI Assistant Platform

set -e

echo "🚀 Starting production deployment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build and start services
echo "📦 Building Docker images..."
docker-compose build

echo "🔄 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check health
echo "🏥 Checking service health..."
if curl -f http://localhost:8004/api/system/health > /dev/null 2>&1; then
    echo "✅ API service is healthy"
else
    echo "❌ API service is not responding"
    docker-compose logs ai-assistant-api
    exit 1
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend service is healthy"
else
    echo "❌ Frontend service is not responding"
    docker-compose logs frontend
    exit 1
fi

echo "🎉 Production deployment completed successfully!"
echo "📱 Frontend: http://localhost:3000"
echo "🔌 API: http://localhost:8004"
echo "📊 Health: http://localhost:8004/api/system/health"
"""
        
        # Backup script
        backup_script = """#!/bin/bash
# Backup Script for AI Assistant Platform

set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="ai_assistant_backup_${TIMESTAMP}"

echo "💾 Creating backup: ${BACKUP_NAME}"

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Backup knowledge base
if [ -d "knowledge_base" ]; then
    echo "📚 Backing up knowledge base..."
    tar -czf "${BACKUP_DIR}/${BACKUP_NAME}_knowledge.tar.gz" knowledge_base/
fi

# Backup logs
if [ -d "logs" ]; then
    echo "📝 Backing up logs..."
    tar -czf "${BACKUP_DIR}/${BACKUP_NAME}_logs.tar.gz" logs/
fi

# Backup configuration
echo "⚙️ Backing up configuration..."
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}_config.tar.gz" \
    docker-compose.yml \
    nginx.conf \
    .env.production \
    logging_config.json

echo "✅ Backup completed: ${BACKUP_DIR}/${BACKUP_NAME}_*.tar.gz"
"""
        
        # Health check script
        health_script = """#!/bin/bash
# Health Check Script for AI Assistant Platform

echo "🏥 Running health checks..."

# Check API health
echo "🔌 Checking API health..."
if curl -f http://localhost:8004/api/system/health > /dev/null 2>&1; then
    echo "✅ API is healthy"
else
    echo "❌ API is not responding"
    exit 1
fi

# Check frontend health
echo "📱 Checking frontend health..."
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend is not responding"
    exit 1
fi

# Check performance metrics
echo "📊 Checking performance metrics..."
if curl -f http://localhost:8004/api/system/performance-report > /dev/null 2>&1; then
    echo "✅ Performance metrics available"
else
    echo "⚠️ Performance metrics not available"
fi

echo "🎉 All health checks passed!"
"""
        
        # Write scripts
        scripts_dir = self.project_root / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        (scripts_dir / "deploy.sh").write_text(deploy_script)
        (scripts_dir / "backup.sh").write_text(backup_script)
        (scripts_dir / "health_check.sh").write_text(health_script)
        
        # Make scripts executable
        for script in scripts_dir.glob("*.sh"):
            script.chmod(0o755)
        
        self.logger.info("✅ Deployment scripts created")
    
    def create_production_readme(self) -> None:
        """Create production deployment README."""
        self.logger.info("📖 Creating production README...")
        
        readme_content = """# AI Assistant Platform - Production Deployment

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- 8GB+ RAM recommended
- 20GB+ disk space

### Deployment
```bash
# Clone and navigate to project
cd ai-assistant-platform

# Run deployment script
./scripts/deploy.sh
```

### Access Points
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8004
- **Health Check**: http://localhost:8004/api/system/health
- **API Documentation**: http://localhost:8004/docs

## 🏗️ Architecture

### Services
- **ai-assistant-api**: FastAPI backend with AI models
- **frontend**: Next.js React frontend
- **nginx**: Reverse proxy and load balancer

### Features
- **Lazy Model Loading**: Models loaded on-demand to optimize memory
- **Performance Monitoring**: Real-time memory and performance tracking
- **Intelligent Routing**: Automatic model selection based on task type
- **Semantic Search**: Arctic embeddings for knowledge base search
- **Adaptive Fine-tuning**: Automatic model improvement based on performance

## 📊 Monitoring

### Health Checks
```bash
# Run health check script
./scripts/health_check.sh

# Check API health
curl http://localhost:8004/api/system/health

# Check performance metrics
curl http://localhost:8004/api/system/performance-report
```

### Logs
```bash
# View API logs
docker-compose logs ai-assistant-api

# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f
```

## 🔧 Management

### Backup
```bash
# Create backup
./scripts/backup.sh
```

### Restart Services
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart ai-assistant-api
```

### Update Deployment
```bash
# Pull latest changes and redeploy
git pull
./scripts/deploy.sh
```

## 🛠️ Configuration

### Environment Variables
- `.env.production`: Production configuration
- `.env.development`: Development configuration

### Model Configuration
- Default Chat Model: `qwen2.5:7b`
- Fallback Chat Model: `llama3.2:3b`
- Vision Model: `apple/FastVLM-7B`
- Embedding Model: `Snowflake/snowflake-arctic-embed-m`

### Performance Settings
- Memory Usage Threshold: 85%
- Cleanup Interval: 5 minutes
- Lazy Loading: Enabled

## 🔒 Security

### CORS Configuration
- Allowed Origins: `http://localhost:3000`, `http://127.0.0.1:3000`
- API Key Required: `false` (configurable)

### Network Security
- Services communicate through Docker network
- Nginx handles external traffic
- Health checks for service monitoring

## 📈 Performance Optimization

### Memory Management
- Dynamic memory allocation based on system state
- Automatic model unloading when memory usage is high
- Quantization for large models (7B+ parameters)

### Monitoring
- Real-time memory usage tracking
- Model performance profiling
- Automatic cleanup and optimization

## 🆘 Troubleshooting

### Common Issues

#### Service Not Starting
```bash
# Check Docker status
docker info

# Check service logs
docker-compose logs ai-assistant-api
```

#### High Memory Usage
```bash
# Trigger memory optimization
curl -X POST http://localhost:8004/api/system/optimize-memory

# Check model status
curl http://localhost:8004/api/system/model-status
```

#### API Not Responding
```bash
# Check health
curl http://localhost:8004/api/system/health

# Restart API service
docker-compose restart ai-assistant-api
```

### Support
- Check logs: `docker-compose logs`
- Run health checks: `./scripts/health_check.sh`
- Review configuration files
- Check system resources (RAM, disk space)

## 📝 License
This project is licensed under the MIT License.
"""
        
        (self.project_root / "PRODUCTION_README.md").write_text(readme_content)
        self.logger.info("✅ Production README created")
    
    def setup_production_environment(self) -> None:
        """Set up complete production environment."""
        self.logger.info("🏭 Setting up production environment...")
        
        # Create necessary directories
        directories = ["logs", "backups", "ssl"]
        for directory in directories:
            (self.project_root / directory).mkdir(exist_ok=True)
        
        # Create all configurations
        self.create_docker_configuration()
        self.create_nginx_configuration()
        self.create_monitoring_configuration()
        self.create_environment_configuration()
        self.create_deployment_scripts()
        self.create_production_readme()
        
        self.logger.info("🎉 Production environment setup complete!")
        self.logger.info("📖 See PRODUCTION_README.md for deployment instructions")

def main():
    """Main function to set up production deployment."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    
    # Get project root
    project_root = "/Users/christianmerrill/Prompt Engineering"
    
    # Create production deployment
    deployment = ProductionDeployment(project_root)
    deployment.setup_production_environment()

if __name__ == "__main__":
    main()
