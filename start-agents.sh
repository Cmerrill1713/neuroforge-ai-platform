#!/bin/bash

# Agent-Based Document Processing Startup Script
# This script starts the complete agent ecosystem for document processing

set -e

echo "🚀 Starting Agent-Based Document Processing System"
echo "=================================================="

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
mkdir -p data logs scripts config

# Check if required files exist
required_files=(
    "docker-compose.agents.yml"
    "Dockerfile.agent"
    "Dockerfile.orchestrator"
    "Dockerfile.monitor"
    "Dockerfile.kb"
    "src/agents/document_agent.py"
    "src/agents/orchestrator.py"
    "src/agents/monitor.py"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file $file not found"
        exit 1
    fi
done

print_success "All required files found"

# Start the agent ecosystem
print_status "Starting agent ecosystem..."

# First, start the base services (Redis, PostgreSQL, Weaviate)
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

# Check PostgreSQL
if docker-compose -f docker-compose.yml exec -T postgres pg_isready -U postgres | grep -q "accepting connections"; then
    print_success "PostgreSQL is healthy"
else
    print_error "PostgreSQL is not healthy"
    exit 1
fi

# Check Weaviate
if curl -s http://localhost:8080/v1/meta | grep -q "version"; then
    print_success "Weaviate is healthy"
else
    print_error "Weaviate is not healthy"
    exit 1
fi

# Start the agent services
print_status "Starting agent services..."
docker-compose -f docker-compose.agents.yml up -d

# Wait for agent services to be ready
print_status "Waiting for agent services to be ready..."
sleep 60

# Check agent services health
print_status "Checking agent services health..."

# Check Document Agent
if curl -s http://localhost:8006/health | grep -q "healthy"; then
    print_success "Document Agent is healthy"
else
    print_warning "Document Agent may not be ready yet"
fi

# Check Orchestrator
if curl -s http://localhost:8007/health | grep -q "healthy"; then
    print_success "Agent Orchestrator is healthy"
else
    print_warning "Agent Orchestrator may not be ready yet"
fi

# Check Monitor
if curl -s http://localhost:8008/api/status | grep -q "orchestrator"; then
    print_success "Agent Monitor is healthy"
else
    print_warning "Agent Monitor may not be ready yet"
fi

# Check Knowledge Base
if curl -s http://localhost:8004/api/knowledge/stats | grep -q "total_documents"; then
    print_success "Knowledge Base is healthy"
else
    print_warning "Knowledge Base may not be ready yet"
fi

# Display system status
echo ""
echo "🎉 Agent-Based Document Processing System Started!"
echo "=================================================="
echo ""
echo "📊 Service Status:"
echo "  • Redis:           http://localhost:6379"
echo "  • PostgreSQL:      localhost:5432"
echo "  • Weaviate:        http://localhost:8080"
echo "  • Knowledge Base:  http://localhost:8004"
echo "  • Document Agent:  http://localhost:8006"
echo "  • Orchestrator:    http://localhost:8007"
echo "  • Monitor:         http://localhost:8008"
echo ""
echo "🔧 Management Commands:"
echo "  • View Monitor:    open http://localhost:8008"
echo "  • Start Migration: curl -X POST http://localhost:8007/migrate/documents"
echo "  • Check Status:    curl http://localhost:8007/status"
echo "  • View Logs:       docker-compose -f docker-compose.agents.yml logs -f"
echo ""
echo "📋 Next Steps:"
echo "  1. Open the monitor dashboard: http://localhost:8008"
echo "  2. Start document migration from the dashboard"
echo "  3. Monitor progress in real-time"
echo ""

# Optional: Start migration automatically
read -p "🤖 Would you like to start document migration now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Starting document migration..."
    curl -X POST http://localhost:8007/migrate/documents
    print_success "Document migration started! Check the monitor dashboard for progress."
fi

print_success "Agent system startup complete!"
