#!/bin/bash

# Docker Build and Deploy Script for AI System
# This script builds and deploys the containerized AI system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show help
show_help() {
    echo "🐳 AI System Docker Deployment Script"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  build       - Build Docker images"
    echo "  dev         - Start development environment"
    echo "  prod        - Start production environment"
    echo "  stop        - Stop all containers"
    echo "  clean       - Clean up containers and images"
    echo "  logs        - Show container logs"
    echo "  health      - Check container health"
    echo "  help        - Show this help message"
    echo ""
    echo "Options:"
    echo "  --no-cache  - Build without cache"
    echo "  --profile   - Use specific profile (tts, cache, database, monitoring)"
    echo ""
    echo "Examples:"
    echo "  $0 build --no-cache"
    echo "  $0 dev --profile tts"
    echo "  $0 prod --profile monitoring"
}

# Function to build images
build_images() {
    local no_cache=""
    if [[ "$1" == "--no-cache" ]]; then
        no_cache="--no-cache"
    fi
    
    print_status "Building Docker images..."
    
    # Build backend
    print_status "Building backend image..."
    docker build -f Dockerfile.backend -t ai-backend:latest $no_cache .
    
    # Build frontend
    print_status "Building frontend image..."
    docker build -f Dockerfile.frontend -t ai-frontend:latest $no_cache .
    
    print_success "All images built successfully!"
}

# Function to start development environment
start_dev() {
    local profile=""
    if [[ "$1" == "--profile" ]]; then
        profile="--profile $2"
    fi
    
    print_status "Starting development environment..."
    docker-compose up -d $profile
    
    print_success "Development environment started!"
    print_status "Backend: http://localhost:8000"
    print_status "Frontend: http://localhost:3000"
}

# Function to start production environment
start_prod() {
    local profile=""
    if [[ "$1" == "--profile" ]]; then
        profile="--profile $2"
    fi
    
    print_status "Starting production environment..."
    docker-compose -f docker-compose.prod.yml up -d $profile
    
    print_success "Production environment started!"
    print_status "Application: http://localhost"
    print_status "Backend API: http://localhost/api"
}

# Function to stop containers
stop_containers() {
    print_status "Stopping all containers..."
    docker-compose down
    docker-compose -f docker-compose.prod.yml down
    
    print_success "All containers stopped!"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up containers and images..."
    
    # Stop containers
    docker-compose down
    docker-compose -f docker-compose.prod.yml down
    
    # Remove images
    docker rmi ai-backend:latest ai-frontend:latest 2>/dev/null || true
    
    # Clean up unused resources
    docker system prune -f
    
    print_success "Cleanup completed!"
}

# Function to show logs
show_logs() {
    print_status "Showing container logs..."
    docker-compose logs -f
}

# Function to check health
check_health() {
    print_status "Checking container health..."
    
    # Check if containers are running
    if docker-compose ps | grep -q "Up"; then
        print_success "Containers are running"
        
        # Check backend health
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            print_success "Backend is healthy"
        else
            print_warning "Backend health check failed"
        fi
        
        # Check frontend health
        if curl -f http://localhost:3000/api/health >/dev/null 2>&1; then
            print_success "Frontend is healthy"
        else
            print_warning "Frontend health check failed"
        fi
    else
        print_error "No containers are running"
    fi
}

# Main script logic
case "${1:-help}" in
    "build")
        build_images "$2" "$3"
        ;;
    "dev")
        start_dev "$2" "$3"
        ;;
    "prod")
        start_prod "$2" "$3"
        ;;
    "stop")
        stop_containers
        ;;
    "clean")
        cleanup
        ;;
    "logs")
        show_logs
        ;;
    "health")
        check_health
        ;;
    "help"|*)
        show_help
        ;;
esac
