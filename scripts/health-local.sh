#!/bin/bash
# ============================================================================
# NeuroForge Local Health Check Script
# Simple health checks for local development
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARN: $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}"
}

# Check if service is running
check_service() {
    local name="$1"
    local url="$2"
    local expected_code="${3:-200}"

    log_info "Checking $name..."

    if curl -f -s --max-time 5 "$url" > /dev/null 2>&1; then
        log_success "✅ $name is healthy"
        return 0
    else
        log_error "❌ $name is not responding"
        return 1
    fi
}

# Check Docker container
check_container() {
    local container="$1"
    local name="$2"

    log_info "Checking $name container..."

    if docker ps -q -f name="$container" | grep -q .; then
        log_success "✅ $name container is running"
        return 0
    else
        log_error "❌ $name container is not running"
        return 1
    fi
}

# Main health check
main() {
    log_info "🚀 NeuroForge Local Health Check"
    echo ""

    local all_healthy=true

    # Check core services
    check_service "API" "http://localhost:8000/health" || all_healthy=false
    check_service "Frontend" "http://localhost:3000" || all_healthy=false

    # Check containers
    check_container "neuroforge-local-neuroforge-postgres-1" "PostgreSQL" || all_healthy=false
    check_container "neuroforge-local-neuroforge-redis-1" "Redis" || all_healthy=false
    check_container "neuroforge-local-neuroforge-weaviate-1" "Weaviate" || all_healthy=false

    # Optional services
    if docker ps -q -f name="neuroforge-local-neuroforge-prometheus-1" | grep -q .; then
        check_service "Prometheus" "http://localhost:9090" || all_healthy=false
    fi

    if docker ps -q -f name="neuroforge-local-neuroforge-grafana-1" | grep -q .; then
        check_service "Grafana" "http://localhost:3001" || all_healthy=false
    fi

    echo ""

    if [[ "$all_healthy" == "true" ]]; then
        log_success "🎉 All services are healthy!"
        echo ""
        echo "NeuroForge Local URLs:"
        echo "  API:        http://localhost:8000"
        echo "  Frontend:   http://localhost:3000"
        echo "  API Docs:   http://localhost:8000/docs"
        echo "  PgAdmin:    http://localhost:5050 (if dev-tools enabled)"
        echo "  RedisInsight: http://localhost:5540 (if dev-tools enabled)"
        echo "  Prometheus: http://localhost:9090 (if monitoring enabled)"
        echo "  Grafana:    http://localhost:3001 (if monitoring enabled)"
        exit 0
    else
        log_error "❌ Some services are unhealthy"
        echo ""
        echo "Troubleshooting:"
        echo "1. Check service logs: ./scripts/deploy-local.sh logs"
        echo "2. Restart services: ./scripts/deploy-local.sh restart"
        echo "3. Reset environment: ./scripts/deploy-local.sh reset"
        exit 1
    fi
}

# Run main function
main "$@"
