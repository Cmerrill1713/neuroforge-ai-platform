# AI Assistant Platform - Production Deployment

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
