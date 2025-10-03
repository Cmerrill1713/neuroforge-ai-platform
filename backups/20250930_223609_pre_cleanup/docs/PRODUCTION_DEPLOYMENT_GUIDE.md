# 🚀 Production Deployment Guide

## AI Agent Platform - Production Deployment

**Version:** 2.0.0
**Last Updated:** September 29, 2025

---

## 📋 Prerequisites

### System Requirements
- **Docker Engine:** 24.0+ with Docker Compose V2
- **Memory:** 16GB RAM minimum, 32GB recommended
- **CPU:** 4 cores minimum, 8 cores recommended
- **Storage:** 100GB SSD minimum
- **Network:** Stable internet connection (for model downloads)

### Required Environment Variables
```bash
# GitHub Token (for MCP services)
GITHUB_TOKEN=your_github_token_here

# Database Configuration
POSTGRES_DB=ai_system
POSTGRES_USER=ai_user
POSTGRES_PASSWORD=secure_password_here

# Redis Configuration
REDIS_PASSWORD=secure_redis_password

# API Keys (optional, for external services)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

---

## 🏗️ Deployment Options

### Option 1: Full Production Stack (Recommended)

```bash
# Deploy all services with monitoring and load balancing
docker compose --profile monitoring --profile load-balancer --profile vector-db up -d
```

### Option 2: Core Services Only

```bash
# Deploy just the essential services
docker compose up -d backend frontend
```

### Option 3: Development Stack

```bash
# Deploy with additional development services
docker compose --profile database --profile cache up -d
```

---

## 🔧 Post-Deployment Configuration

### 1. Initialize the Database

```bash
# Access the backend container
docker compose exec backend bash

# Run database migrations (if any)
python -c "from src.core.memory.vector_pg import init_database; init_database()"
```

### 2. Verify Services Health

```bash
# Check all services are running
docker compose ps

# Test API endpoints
curl http://localhost/api/health
curl http://localhost/api/system/health

# Test WebSocket connection
# Use a WebSocket client to connect to ws://localhost/ws
```

### 3. Access Monitoring Dashboard

```bash
# Grafana: http://localhost:3001 (admin/admin)
# Prometheus: http://localhost:9090
# Backend API: http://localhost/api/docs
```

---

## 🔒 Security Hardening

### SSL/TLS Configuration

1. **Obtain SSL Certificates:**
   ```bash
   # Using Let's Encrypt
   certbot certonly --webroot -w /var/www/html -d yourdomain.com

   # Or using self-signed for testing
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
   ```

2. **Configure Nginx with SSL:**
   ```bash
   # Copy certificates to nginx/ssl directory
   cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
   cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem

   # Update nginx.conf to enable SSL
   # Uncomment the HTTPS server block in nginx/nginx.conf
   ```

### Environment Variables Security

1. **Create `.env` file:**
   ```bash
   # Create production environment file
   cat > .env << EOF
   GITHUB_TOKEN=${GITHUB_TOKEN}
   POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
   REDIS_PASSWORD=${REDIS_PASSWORD}
   SECRET_KEY=$(openssl rand -hex 32)
   JWT_SECRET=$(openssl rand -hex 32)
   EOF
   ```

2. **Update docker-compose.yml:**
   ```yaml
   # Add to each service
   env_file:
     - .env
   ```

### Network Security

1. **Firewall Configuration:**
   ```bash
   # Allow only necessary ports
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw allow 22/tcp  # SSH
   ufw --force enable
   ```

2. **Docker Network Isolation:**
   ```yaml
   # In docker-compose.yml, use internal networks
   networks:
     ai-network:
       internal: true  # Only accessible from within Docker network
   ```

---

## 📊 Monitoring & Alerting

### Setting Up Alerts

1. **Configure AlertManager:**
   ```yaml
   # monitoring/alertmanager.yml
   global:
     smtp_smarthost: 'smtp.gmail.com:587'
     smtp_from: 'alerts@yourdomain.com'
     smtp_auth_username: 'your-email@gmail.com'
     smtp_auth_password: 'your-app-password'

   route:
     group_by: ['alertname']
     group_wait: 10s
     group_interval: 10s
     repeat_interval: 1h
     receiver: 'email'

   receivers:
     - name: 'email'
       email_configs:
         - to: 'admin@yourdomain.com'
   ```

2. **Key Metrics to Monitor:**
   - API Response Time (< 500ms)
   - Error Rate (< 1%)
   - Memory Usage (< 80%)
   - CPU Usage (< 70%)
   - WebSocket Connections
   - RAG Query Performance

### Log Aggregation

```bash
# Use Docker logging drivers
docker compose up -d --log-driver json-file --log-opt max-size=10m --log-opt max-file=3
```

---

## 🔄 Backup & Recovery

### Database Backups

```bash
# PostgreSQL backup
docker compose exec postgres pg_dump -U ai_user ai_system > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/ai-platform/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
docker compose exec -T postgres pg_dump -U ai_user ai_system > $BACKUP_DIR/db_$TIMESTAMP.sql

# Knowledge base backup
docker run --rm -v ai-platform_knowledge_base:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/knowledge_$TIMESTAMP.tar.gz -C /data .

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $TIMESTAMP"
EOF

chmod +x backup.sh
# Add to crontab: 0 2 * * * /opt/ai-platform/backup.sh
```

### Knowledge Base Backup

```bash
# Backup knowledge base volume
docker run --rm -v ai-platform_knowledge_base:/data -v $(pwd):/backup alpine tar czf knowledge_base_$(date +%Y%m%d).tar.gz -C /data .
```

---

## 🚀 Scaling & Performance

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  backend:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  frontend:
    deploy:
      replicas: 2
```

### Performance Optimization

1. **Enable Redis Caching:**
   ```bash
   docker compose --profile cache up -d
   ```

2. **Database Indexing:**
   ```sql
   CREATE INDEX CONCURRENTLY idx_documents_type ON documents(document_type);
   CREATE INDEX CONCURRENTLY idx_documents_source ON documents(source);
   CREATE INDEX CONCURRENTLY idx_embeddings_document_id ON embeddings(document_id);
   ```

3. **Model Caching:**
   - Pre-load frequently used models
   - Use model versioning for faster deployments

---

## 🔍 Troubleshooting

### Common Issues

#### 1. Backend Not Starting
```bash
# Check logs
docker compose logs backend

# Check dependencies
docker compose exec backend pip list | grep -E "(fastapi|uvicorn|chromadb)"

# Verify database connection
docker compose exec backend python -c "import psycopg2; print('DB OK')"
```

#### 2. Frontend Build Failures
```bash
# Clear Next.js cache
docker compose exec frontend rm -rf .next

# Rebuild without cache
docker compose build --no-cache frontend
```

#### 3. WebSocket Connection Issues
```bash
# Check WebSocket endpoint
curl -I http://localhost/api/health

# Test WebSocket connection
docker run --rm -it alpine sh -c "apk add websocat && echo 'test' | websocat ws://host.docker.internal/ws"
```

#### 4. Memory Issues
```bash
# Monitor memory usage
docker stats

# Adjust memory limits in docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
```

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks

1. **Weekly:**
   - Review monitoring dashboards
   - Check log files for errors
   - Update dependencies (security patches)

2. **Monthly:**
   - Run full backup verification
   - Performance benchmarking
   - Security vulnerability scans

3. **Quarterly:**
   - Major version updates
   - Architecture reviews
   - Capacity planning

### Support Contacts

- **Technical Issues:** devops@yourdomain.com
- **Security Issues:** security@yourdomain.com
- **Business Issues:** support@yourdomain.com

### Documentation Updates

Keep this guide updated with:
- New deployment procedures
- Security updates
- Performance optimizations
- Troubleshooting solutions

---

## 🎯 Success Metrics

Monitor these KPIs for deployment success:

- **Availability:** 99.9% uptime
- **Performance:** <500ms API response time
- **Security:** Zero critical vulnerabilities
- **User Satisfaction:** >95% positive feedback
- **Scalability:** Handle 1000+ concurrent users

---

*This guide should be reviewed and updated quarterly to reflect system changes and best practices.*
