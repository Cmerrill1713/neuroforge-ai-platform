#!/bin/bash

# Production Deployment Script
set -e

echo "🚀 Starting Production Deployment..."

# Configuration
DOMAIN="yourdomain.com"
REMOTE_HOST="user@your-server-ip"
REMOTE_DIR="/var/www/agentic-llm-core"
DOCKER_COMPOSE_FILE="docker-compose.production.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Pre-deployment checks
echo "1. Performing pre-deployment checks..."
if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
    print_error "Docker Compose file '$DOCKER_COMPOSE_FILE' not found!"
    exit 1
fi

if [ ! -f "production.env" ]; then
    print_error "Production environment file 'production.env' not found!"
    print_warning "Please create it from production.env.example"
    exit 1
fi

if [ ! -f "Dockerfile.production" ]; then
    print_error "Production Dockerfile not found!"
    exit 1
fi

print_status "Pre-deployment checks passed"

# Build frontend
echo "2. Building frontend for production..."
cd frontend
if [ ! -f "package.json" ]; then
    print_error "Frontend package.json not found!"
    exit 1
fi

npm install
npm run build
cd ..
print_status "Frontend build complete"

# Transfer files to server
echo "3. Transferring files to server..."
ssh "$REMOTE_HOST" "mkdir -p $REMOTE_DIR"

# Use rsync to transfer files
rsync -avz --delete \
    --exclude 'node_modules/' \
    --exclude '.git/' \
    --exclude '.next/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '.env' \
    --exclude 'ollama_models/' \
    ./ "$REMOTE_HOST":"$REMOTE_DIR"

print_status "File transfer complete"

# Deploy on remote server
echo "4. Deploying on remote server..."
ssh "$REMOTE_HOST" << EOF
    set -e
    echo "Navigating to $REMOTE_DIR"
    cd "$REMOTE_DIR"
    
    echo "Stopping existing containers..."
    docker compose -f "$DOCKER_COMPOSE_FILE" down || true
    
    echo "Building and starting new containers..."
    docker compose -f "$DOCKER_COMPOSE_FILE" up --build -d
    
    echo "Waiting for services to be ready..."
    sleep 30
    
    echo "Checking container status..."
    docker compose -f "$DOCKER_COMPOSE_FILE" ps
    
    echo "Testing API health..."
    curl -f http://localhost:8002/health || echo "API health check failed"
EOF

print_status "Remote deployment complete"

# Post-deployment verification
echo "5. Verifying deployment..."
print_warning "Please manually verify your application at http://$DOMAIN"
print_warning "Check API health at http://$DOMAIN/health"
print_warning "Check API docs at http://$DOMAIN/docs"

echo "🎉 Production deployment completed successfully!"
echo ""
echo "Next steps:"
echo "1. Configure your domain DNS to point to your server"
echo "2. Set up SSL certificates (Let's Encrypt recommended)"
echo "3. Monitor application logs: docker compose -f $DOCKER_COMPOSE_FILE logs -f"
echo "4. Set up monitoring and alerting"
echo "5. Configure backup strategies"
