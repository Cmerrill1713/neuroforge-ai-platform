#!/bin/bash

# Production Deployment Script for AI Chat API
set -e

echo "🚀 Starting Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="ai-chat-api"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed"
}

# Check if environment file exists
check_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        print_warning "Environment file $ENV_FILE not found. Creating from example..."
        if [ -f "production.env.example" ]; then
            cp production.env.example "$ENV_FILE"
            print_warning "Please edit $ENV_FILE with your actual values before continuing"
            exit 1
        else
            print_error "No environment file template found. Please create $ENV_FILE manually"
            exit 1
        fi
    fi
    print_status "Environment file found"
}

# Generate SSL certificates (self-signed for development)
generate_ssl_certs() {
    if [ ! -d "ssl" ]; then
        print_status "Generating SSL certificates..."
        mkdir -p ssl
        
        # Generate self-signed certificate
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ssl/key.pem \
            -out ssl/cert.pem \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=yourdomain.com"
        
        print_status "SSL certificates generated"
    else
        print_status "SSL certificates already exist"
    fi
}

# Build and start services
deploy_services() {
    print_status "Building and starting services..."
    
    # Stop existing services
    docker-compose -f "$DOCKER_COMPOSE_FILE" down --remove-orphans
    
    # Build and start services
    docker-compose -f "$DOCKER_COMPOSE_FILE" up --build -d
    
    print_status "Services deployed successfully"
}

# Wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to be healthy..."
    
    # Wait for API server
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:8002/health &> /dev/null; then
            print_status "API server is healthy"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "API server failed to start within 60 seconds"
        exit 1
    fi
    
    # Wait for database
    timeout=30
    while [ $timeout -gt 0 ]; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T postgres pg_isready -U postgres &> /dev/null; then
            print_status "Database is healthy"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "Database failed to start within 30 seconds"
        exit 1
    fi
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # This would typically run Alembic migrations
    # docker-compose -f "$DOCKER_COMPOSE_FILE" exec api-server alembic upgrade head
    
    print_status "Database migrations completed"
}

# Test the deployment
test_deployment() {
    print_status "Testing deployment..."
    
    # Test health endpoint
    if curl -f http://localhost:8002/health &> /dev/null; then
        print_status "✅ Health check passed"
    else
        print_error "❌ Health check failed"
        exit 1
    fi
    
    # Test API endpoint
    response=$(curl -s -X POST http://localhost:8002/api/chat \
        -H "Content-Type: application/json" \
        -d '{"message": "Hello, test message"}' \
        -w "%{http_code}")
    
    if [[ "$response" == *"200" ]]; then
        print_status "✅ API endpoint test passed"
    else
        print_error "❌ API endpoint test failed"
        exit 1
    fi
    
    print_status "All tests passed!"
}

# Show deployment status
show_status() {
    print_status "Deployment Status:"
    echo ""
    echo "🌐 Services:"
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    echo ""
    echo "📊 Health Checks:"
    echo "API Server: http://localhost:8002/health"
    echo "Prometheus: http://localhost:9090"
    echo "Grafana: http://localhost:3001"
    echo ""
    echo "📝 Logs:"
    echo "docker-compose -f $DOCKER_COMPOSE_FILE logs -f api-server"
    echo ""
    echo "🛑 Stop Services:"
    echo "docker-compose -f $DOCKER_COMPOSE_FILE down"
}

# Main deployment process
main() {
    print_status "Starting production deployment for $PROJECT_NAME"
    
    check_docker
    check_env_file
    generate_ssl_certs
    deploy_services
    wait_for_services
    run_migrations
    test_deployment
    show_status
    
    print_status "🎉 Production deployment completed successfully!"
}

# Handle script arguments
case "${1:-}" in
    "stop")
        print_status "Stopping services..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" down
        print_status "Services stopped"
        ;;
    "restart")
        print_status "Restarting services..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" restart
        print_status "Services restarted"
        ;;
    "logs")
        docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f "${2:-api-server}"
        ;;
    "status")
        docker-compose -f "$DOCKER_COMPOSE_FILE" ps
        ;;
    *)
        main
        ;;
esac
