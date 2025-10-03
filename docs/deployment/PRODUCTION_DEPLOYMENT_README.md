# 🚀 NeuroForge Production Deployment Guide - Phase 5

**Enterprise-Grade AI Development Platform - Production Ready**

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Prerequisites](#-prerequisites)
- [Environment Setup](#-environment-setup)
- [SSL Configuration](#-ssl-configuration)
- [Production Deployment](#-production-deployment)
- [Monitoring & Observability](#-monitoring--observability)
- [Backup & Recovery](#-backup--recovery)
- [Health Checks](#-health-checks)
- [Troubleshooting](#-troubleshooting)
- [Scaling Guide](#-scaling-guide)

---

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <repository>
cd neuroforge

# 2. Configure environment
cp env.example .env
# Edit .env with your production values

# 3. Deploy to production
export POSTGRES_PASSWORD="your-secure-password"
export GRAFANA_PASSWORD="your-admin-password"
./scripts/deploy-production.sh deploy

# 4. Setup SSL (optional but recommended)
./scripts/setup-ssl.sh --domain yourdomain.com --email admin@yourdomain.com

# 5. Verify deployment
./scripts/health-check.sh
```

---

## 📋 Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / macOS 12+
- **CPU**: 4+ cores (8+ recommended)
- **RAM**: 16GB+ (32GB+ recommended for ML workloads)
- **Storage**: 100GB+ SSD
- **Network**: 1Gbps+ connection

### Software Requirements
```bash
# Docker & Docker Compose
curl -fsSL https://get.docker.com | sh
# Follow post-install steps for non-root usage

# Git & development tools
apt-get update && apt-get install -y git curl wget htop

# SSL certificate tools (optional)
apt-get install -y certbot python3-certbot-nginx
```

### Network Configuration
```bash
# Open required ports
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 9090/tcp  # Prometheus
ufw allow 3001/tcp  # Grafana
ufw --force enable
```

---

## 🔧 Environment Setup

### 1. Clone Repository
```bash
git clone <neuroforge-repository>
cd neuroforge
```

### 2. Configure Environment Variables
```bash
cp env.example .env

# Edit .env with production values
nano .env  # or your preferred editor

# Required variables:
POSTGRES_PASSWORD=your-super-secure-password
GRAFANA_PASSWORD=your-admin-password
SECRET_KEY=your-256-bit-secret-key
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
```

### 3. Generate Secure Keys
```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate secure passwords
openssl rand -base64 32
```

---

## 🔒 SSL Configuration

### Let's Encrypt SSL (Recommended)
```bash
# For production SSL certificates
./scripts/setup-ssl.sh \
  --domain yourdomain.com \
  --email admin@yourdomain.com

# For testing (staging certificates)
./scripts/setup-ssl.sh \
  --domain yourdomain.com \
  --email admin@yourdomain.com \
  --staging
```

### Manual SSL Setup
```bash
# 1. Place certificates in ssl/ directory
mkdir -p ssl/
cp your-cert.pem ssl/neuroforge.crt
cp your-key.pem ssl/neuroforge.key

# 2. Set proper permissions
chmod 600 ssl/neuroforge.key
chmod 644 ssl/neuroforge.crt
```

---

## 🐳 Production Deployment

### Single-Command Deployment
```bash
# Deploy all services
./scripts/deploy-production.sh deploy

# Check deployment status
./scripts/deploy-production.sh status

# View logs
./scripts/deploy-production.sh logs
```

### Manual Deployment Steps
```bash
# 1. Start databases first
docker-compose -f docker-compose.prod.yml up -d neuroforge-postgres neuroforge-redis neuroforge-weaviate

# 2. Wait for databases to be ready
sleep 30

# 3. Start application services
docker-compose -f docker-compose.prod.yml up -d neuroforge-api neuroforge-frontend

# 4. Start monitoring stack
docker-compose -f docker-compose.prod.yml --profile monitoring up -d

# 5. Start load balancer
docker-compose -f docker-compose.prod.yml --profile load-balancer up -d
```

### Service URLs After Deployment
- **API**: `https://yourdomain.com/api/`
- **Frontend**: `https://yourdomain.com/`
- **API Docs**: `https://yourdomain.com/docs`
- **Monitoring**: `http://your-server:9090` (Prometheus)
- **Grafana**: `http://your-server:3001` (admin/admin)

---

## 📊 Monitoring & Observability

### Access Monitoring Dashboards
```bash
# Prometheus metrics
open http://your-server:9090

# Grafana dashboards
open http://your-server:3001
# Default credentials: admin / <GRAFANA_PASSWORD from .env>
```

### Key Metrics to Monitor
- **API Performance**: Response times, error rates, throughput
- **Database**: Connection count, query performance, disk usage
- **Cache**: Hit rates, memory usage, eviction rates
- **System**: CPU, memory, disk I/O, network
- **Business**: Experiment success rates, user activity

### Alert Configuration
Alerts are automatically configured for:
- High response times (>5s)
- High error rates (>5%)
- Service downtime
- Resource exhaustion
- SSL certificate expiration

---

## 💾 Backup & Recovery

### Automated Backups
```bash
# Configure backup environment variables in .env
BACKUP_S3_BUCKET=neuroforge-backups
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret

# Backups run automatically via cron
# Manual backup
docker-compose -f docker-compose.prod.yml --profile backup up neuroforge-backup
```

### Manual Backup
```bash
# Full system backup
./scripts/backup/run_backup.sh

# Database only backup
docker exec neuroforge-postgres pg_dump -U neuroforge neuroforge > backup.sql

# Configuration backup
tar -czf config-backup.tar.gz .env nginx/ monitoring/
```

### Recovery Procedures
```bash
# 1. Stop services
./scripts/deploy-production.sh stop

# 2. Restore from backup
# (Follow specific recovery procedures in docs)

# 3. Restart services
./scripts/deploy-production.sh restart
```

---

## 🏥 Health Checks

### Automated Health Monitoring
```bash
# Run comprehensive health check
./scripts/health-check.sh

# Check specific services
./scripts/health-check.sh --api-url https://yourdomain.com

# Continuous monitoring (add to cron)
# */5 * * * * /path/to/scripts/health-check.sh
```

### Manual Health Verification
```bash
# API health
curl -f https://yourdomain.com/api/health

# Database connectivity
docker exec neuroforge-postgres pg_isready -U neuroforge

# Redis connectivity
docker exec neuroforge-redis redis-cli ping

# Container status
docker ps --filter "label=com.docker.compose.project=neuroforge"
```

---

## 🔧 Troubleshooting

### Common Issues & Solutions

#### Services Won't Start
```bash
# Check logs
./scripts/deploy-production.sh logs

# Check resource usage
docker stats

# Check configuration
docker-compose -f docker-compose.prod.yml config
```

#### Database Connection Issues
```bash
# Check database logs
docker logs neuroforge-postgres

# Test connection
docker exec -it neuroforge-postgres psql -U neuroforge -d neuroforge

# Reset database (CAUTION: destroys data)
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d neuroforge-postgres
```

#### SSL Certificate Problems
```bash
# Check certificate validity
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Renew certificates
certbot renew

# Reload nginx
docker exec neuroforge-nginx nginx -s reload
```

#### High Resource Usage
```bash
# Monitor resource usage
docker stats

# Check container logs for memory leaks
docker logs --tail 100 neuroforge-api

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale neuroforge-api=3
```

---

## 📈 Scaling Guide

### Horizontal Scaling
```bash
# Scale API instances
docker-compose -f docker-compose.prod.yml up -d --scale neuroforge-api=3

# Scale frontend instances
docker-compose -f docker-compose.prod.yml up -d --scale neuroforge-frontend=2
```

### Vertical Scaling
```yaml
# Update docker-compose.prod.yml with higher limits
services:
  neuroforge-api:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
```

### Database Scaling
```bash
# Enable PostgreSQL read replicas (advanced)
# Configure connection pooling with PgBouncer
# Implement database sharding for high-volume deployments
```

### Load Balancing
```nginx
# Advanced NGINX configuration in nginx/prod.nginx.conf
upstream neuroforge_api {
    least_conn;
    server neuroforge-api-1:8000 weight=1;
    server neuroforge-api-2:8000 weight=1;
    server neuroforge-api-3:8000 weight=1;
}
```

---

## 🔐 Security Checklist

### Pre-Production
- [ ] Change all default passwords
- [ ] Configure firewall rules
- [ ] Enable SSL/TLS certificates
- [ ] Set up monitoring and alerting
- [ ] Configure backup procedures
- [ ] Test disaster recovery procedures

### Production
- [ ] Disable debug mode
- [ ] Use secure secrets management
- [ ] Implement rate limiting
- [ ] Configure log aggregation
- [ ] Set up intrusion detection
- [ ] Regular security updates

---

## 📞 Support & Documentation

### Getting Help
- **Documentation**: See `docs/` directory
- **Logs**: `./scripts/deploy-production.sh logs`
- **Health**: `./scripts/health-check.sh`
- **Metrics**: `http://your-server:9090`

### Emergency Contacts
- **System Admin**: admin@yourdomain.com
- **DevOps Team**: devops@yourdomain.com
- **Security Issues**: security@yourdomain.com

---

## 🎯 Next Steps

1. **Domain Configuration**: Set up DNS records
2. **SSL Setup**: Configure production certificates
3. **Monitoring**: Set up alerts and notifications
4. **Backup**: Configure automated backups
5. **Scaling**: Plan for growth and performance
6. **Security**: Implement enterprise security measures

---

**🎉 Congratulations! NeuroForge is now production-ready.**

**Ready to deploy? Run:**
```bash
./scripts/deploy-production.sh deploy
```

**Need help? Check the troubleshooting section above or run:**
```bash
./scripts/health-check.sh --help
```
