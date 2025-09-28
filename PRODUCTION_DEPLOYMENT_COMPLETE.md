# 🚀 Production Deployment Guide - Agentic LLM Core

## Overview
This guide provides complete instructions for deploying the Agentic LLM Core system to production with enterprise-grade security, monitoring, and scalability.

## 🎯 What We've Built

### ✅ Production-Ready Components
- **Production API Server** (`production_api_server_working.py`)
  - Security headers and CORS protection
  - Input validation and rate limiting
  - Health checks and monitoring endpoints
  - Error handling and logging
  - 8 AI agents with full functionality

- **Docker Infrastructure**
  - `Dockerfile.production` - Optimized container
  - `docker-compose.production.yml` - Multi-service orchestration
  - `requirements.production.txt` - Production dependencies

- **Nginx Reverse Proxy** (`nginx.production.conf`)
  - Security headers and SSL termination
  - Rate limiting and DDoS protection
  - Static file serving and caching
  - Load balancing and health checks

- **Automated Deployment** (`deploy.production.sh`)
  - One-command deployment
  - Pre-deployment validation
  - Remote server orchestration
  - Post-deployment verification

## 🏗️ Architecture

```
Internet → Nginx (Port 80/443) → API Server (Port 8002) → AI Models
                ↓
         Static Frontend Files
                ↓
         PostgreSQL Database (Optional)
```

## 📋 Prerequisites

### Local Machine
- Docker and Docker Compose
- Node.js 18+ and npm
- SSH access to production server
- Git

### Production Server
- Ubuntu 20.04+ LTS or similar
- Docker and Docker Compose installed
- 4GB+ RAM, 2+ CPU cores
- Domain name pointing to server IP
- SSL certificate (Let's Encrypt recommended)

## 🚀 Quick Deployment

### 1. Configure Environment
```bash
# Edit production environment
cp production.env.example production.env
# Update with your actual values:
# - DOMAIN=yourdomain.com
# - SECRET_KEY=your-secure-key
# - Database credentials
```

### 2. Build Frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

### 3. Deploy
```bash
# Make deployment script executable
chmod +x deploy.production.sh

# Update script with your server details
# Edit deploy.production.sh:
# - DOMAIN="yourdomain.com"
# - REMOTE_HOST="user@your-server-ip"

# Deploy to production
./deploy.production.sh
```

## 🔧 Manual Deployment Steps

### 1. Server Setup
```bash
# On your production server
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose nginx -y
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

### 2. Transfer Files
```bash
# From your local machine
rsync -avz --exclude 'node_modules' --exclude '.git' \
  ./ user@your-server:/var/www/agentic-llm-core/
```

### 3. Start Services
```bash
# On production server
cd /var/www/agentic-llm-core
docker compose -f docker-compose.production.yml up -d
```

### 4. Configure SSL (Let's Encrypt)
```bash
# Install Certbot
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 🔒 Security Features

### API Security
- **Rate Limiting**: 10 requests/second for API, 30 for general
- **Input Validation**: Message length limits, sanitization
- **CORS Protection**: Configured origins only
- **Security Headers**: XSS, CSRF, content-type protection
- **Error Handling**: No sensitive information in error responses

### Infrastructure Security
- **Non-root containers**: Security-hardened Docker images
- **Network isolation**: Internal Docker networks
- **SSL/TLS**: End-to-end encryption
- **Firewall**: Only necessary ports exposed
- **Updates**: Automated security patches

## 📊 Monitoring & Health Checks

### Available Endpoints
- `GET /` - System status and API info
- `GET /api/agents` - Available AI agents (8 agents)
- `GET /models/status` - Model health and performance
- `GET /monitoring/metrics` - System metrics
- `POST /api/chat` - Main chat endpoint
- `POST /knowledge/search` - Knowledge base search

### Health Monitoring
```bash
# Check container health
docker compose -f docker-compose.production.yml ps

# View logs
docker compose -f docker-compose.production.yml logs -f api

# Test API health
curl http://yourdomain.com/api/agents
```

## 🎛️ Configuration

### Environment Variables (`production.env`)
```bash
# Core Settings
ENVIRONMENT=production
DEBUG=false
PORT=8002

# Security
SECRET_KEY=your-super-secure-key-here
RATE_LIMIT_PER_MINUTE=100/minute

# CORS (comma-separated)
CORS_ORIGINS_LIST=https://yourdomain.com,https://www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:pass@db:5432/agentic_llm

# Monitoring
MONITORING_ENABLED=true
```

### Nginx Configuration
- **Rate Limiting**: API and general request limits
- **Caching**: Static assets cached for 1 year
- **Compression**: Gzip compression enabled
- **Security**: Multiple security headers
- **SSL**: TLS 1.2+ with modern ciphers

## 🔄 Updates & Maintenance

### Deploy Updates
```bash
# Make changes locally
git pull origin main
cd frontend && npm run build && cd ..

# Deploy updates
./deploy.production.sh
```

### Backup Strategy
```bash
# Database backup
docker compose -f docker-compose.production.yml exec db \
  pg_dump -U agentic_user agentic_llm > backup_$(date +%Y%m%d).sql

# Model files backup
tar -czf models_backup_$(date +%Y%m%d).tar.gz ollama_models/
```

### Monitoring Commands
```bash
# System resources
docker stats

# Container logs
docker compose -f docker-compose.production.yml logs -f

# API performance
curl -w "@curl-format.txt" -s http://yourdomain.com/api/chat \
  -X POST -H "Content-Type: application/json" \
  -d '{"message":"test"}'
```

## 🚨 Troubleshooting

### Common Issues

**1. Containers won't start**
```bash
# Check logs
docker compose -f docker-compose.production.yml logs

# Check disk space
df -h

# Restart services
docker compose -f docker-compose.production.yml restart
```

**2. API not responding**
```bash
# Check if API is running
curl http://localhost:8002/

# Check Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

**3. SSL certificate issues**
```bash
# Renew certificate
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

**4. Frontend not loading**
```bash
# Check if frontend files exist
ls -la frontend/out/

# Check Nginx static file serving
curl -I http://yourdomain.com/
```

## 📈 Performance Optimization

### Production Tuning
- **Docker Resources**: Allocate adequate CPU/memory
- **Database**: Use connection pooling
- **Caching**: Enable Redis for session storage
- **CDN**: Use CloudFlare for static assets
- **Monitoring**: Set up Prometheus + Grafana

### Scaling Options
- **Horizontal**: Multiple API server instances
- **Load Balancer**: HAProxy or AWS ALB
- **Database**: Read replicas for queries
- **Caching**: Redis cluster for sessions

## 🎉 Success Metrics

### ✅ Deployment Checklist
- [ ] Production server accessible at your domain
- [ ] SSL certificate installed and working
- [ ] API responding to health checks
- [ ] All 8 AI agents available
- [ ] Frontend loading correctly
- [ ] Chat functionality working
- [ ] Knowledge base search working
- [ ] Monitoring endpoints responding
- [ ] Logs being generated properly
- [ ] Backup strategy implemented

### 🎯 Performance Targets
- **Response Time**: < 2 seconds for chat
- **Uptime**: 99.9% availability
- **Throughput**: 100+ requests/minute
- **Error Rate**: < 1% API errors

## 📞 Support & Maintenance

### Regular Maintenance
- **Weekly**: Check logs, update dependencies
- **Monthly**: Security patches, performance review
- **Quarterly**: Full system backup, disaster recovery test

### Monitoring Alerts
- High error rates (>5%)
- Response time degradation (>5s)
- Disk space low (<20% free)
- Memory usage high (>80%)
- SSL certificate expiring (<30 days)

---

## 🎊 Congratulations!

You now have a **production-ready, enterprise-grade AI system** with:
- ✅ **8 AI Agents** with specialized capabilities
- ✅ **Real-time Chat** with intelligent responses
- ✅ **Knowledge Base** search functionality
- ✅ **Security Hardening** with rate limiting
- ✅ **Monitoring & Health Checks**
- ✅ **Automated Deployment**
- ✅ **SSL/TLS Encryption**
- ✅ **Docker Containerization**
- ✅ **Nginx Reverse Proxy**
- ✅ **Scalable Architecture**

Your Agentic LLM Core is ready for production use! 🚀
