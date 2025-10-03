#!/bin/bash

# Lightweight Agent Startup Script
# Starts a resource-efficient document processing agent with existing grading system integration

set -e

echo "🤖 Starting Lightweight Document Agent"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_success "Docker is running"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

print_success "docker-compose is available"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p data logs

# Check if required files exist
required_files=(
    "docker-compose.lightweight.yml"
    "Dockerfile.lightweight-agent"
    "src/agents/lightweight_agent.py"
    "requirements-minimal.txt"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file $file not found"
        exit 1
    fi
done

print_success "All required files found"

# Start the base services first
print_status "Starting base services (Redis, PostgreSQL, Weaviate)..."
docker-compose -f docker-compose.yml up -d redis postgres weaviate

# Wait for base services to be ready
print_status "Waiting for base services to be ready..."
sleep 30

# Check if base services are healthy
print_status "Checking base services health..."

# Check Redis
if docker-compose -f docker-compose.yml exec -T redis redis-cli ping | grep -q "PONG"; then
    print_success "Redis is healthy"
else
    print_error "Redis is not healthy"
    exit 1
fi

# Check Weaviate
if curl -s http://localhost:8080/v1/meta | grep -q "version"; then
    print_success "Weaviate is healthy"
else
    print_error "Weaviate is not healthy"
    exit 1
fi

# Start the lightweight agent
print_status "Starting lightweight document agent..."
docker-compose -f docker-compose.lightweight.yml up -d

# Wait for agent to be ready
print_status "Waiting for agent to be ready..."
sleep 30

# Check agent health
print_status "Checking agent health..."

if curl -s http://localhost:8010/health | grep -q "healthy"; then
    print_success "Lightweight Document Agent is healthy"
else
    print_warning "Agent may not be ready yet - check logs"
fi

# Display system status
echo ""
echo "🎉 Lightweight Document Agent Started!"
echo "======================================"
echo ""
echo "📊 Service Status:"
echo "  • Redis:           http://localhost:6379"
echo "  • Weaviate:        http://localhost:8080"
echo "  • Document Agent:  http://localhost:8010"
echo ""
echo "🔧 Management Commands:"
echo "  • Health Check:    curl http://localhost:8010/health"
echo "  • Agent Status:    curl http://localhost:8010/status"
echo "  • Start Migration: curl -X POST http://localhost:8010/migrate"
echo "  • Grading Report:  curl http://localhost:8010/grading/report"
echo "  • View Logs:       docker-compose -f docker-compose.lightweight.yml logs -f"
echo ""
echo "📋 Resource Limits:"
echo "  • Memory:          512MB max"
echo "  • CPU:             50% max"
echo "  • Batch Size:      10 documents"
echo "  • Concurrent Tasks: 2 max"
echo ""
echo "🎯 Next Steps:"
echo "  1. Check agent health: curl http://localhost:8010/health"
echo "  2. Start migration: curl -X POST http://localhost:8010/migrate"
echo "  3. Monitor progress: curl http://localhost:8010/status"
echo "  4. Check grading: curl http://localhost:8010/grading/report"
echo ""

# Optional: Start migration automatically
read -p "🤖 Would you like to start document migration now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Starting document migration..."
    curl -X POST http://localhost:8010/migrate
    print_success "Document migration started! Check status for progress."
fi

print_success "Lightweight agent startup complete!"
