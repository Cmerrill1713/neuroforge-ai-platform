#!/bin/bash
# ============================================================================
# NeuroForge Local Development Deployment Script
# Simplified deployment for local development and testing
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
COMPOSE_FILE="docker-compose.local.yml"
PROJECT_NAME="neuroforge-local"

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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi

    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi

    # Check if compose file exists
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        log_error "Docker Compose file '$COMPOSE_FILE' not found"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Pull images
pull_images() {
    log_info "Pulling Docker images..."

    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$COMPOSE_FILE" pull
    else
        docker compose -f "$COMPOSE_FILE" pull
    fi

    log_success "Images pulled successfully"
}

# Start services
start_services() {
    local profile="${1:-}"

    log_info "Starting NeuroForge services..."

    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi

    if [[ -n "$profile" ]]; then
        log_info "Starting with profile: $profile"
        $COMPOSE_CMD -f "$COMPOSE_FILE" -p "$PROJECT_NAME" --profile "$profile" up -d
    else
        $COMPOSE_CMD -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d
    fi

    log_success "Services started successfully"
}

# Stop services
stop_services() {
    log_info "Stopping NeuroForge services..."

    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down
    else
        docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down
    fi

    log_success "Services stopped"
}

# Show status
show_status() {
    echo "NeuroForge Local Development Status"
    echo "===================================="
    echo ""

    echo "Running Containers:"
    docker ps --filter "label=com.docker.compose.project=$PROJECT_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

    echo ""
    echo "Service URLs:"
    echo "  API:        http://localhost:8000"
    echo "  Frontend:   http://localhost:3000"
    echo "  API Docs:   http://localhost:8000/docs"
    echo "  PgAdmin:    http://localhost:5050 (dev-tools profile)"
    echo "  RedisInsight: http://localhost:5540 (dev-tools profile)"
    echo "  Prometheus: http://localhost:9090 (monitoring profile)"
    echo "  Grafana:    http://localhost:3001 (monitoring profile)"
    echo ""
    echo "Database Access:"
    echo "  PostgreSQL: localhost:5432 (neuroforge/dev_password)"
    echo "  Redis:      localhost:6379"
    echo "  Weaviate:   localhost:8080"
}

# Show logs
show_logs() {
    local service="${1:-}"

    if command -v docker-compose &> /dev/null; then
        if [[ -n "$service" ]]; then
            docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f "$service"
        else
            docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f
        fi
    else
        if [[ -n "$service" ]]; then
            docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f "$service"
        else
            docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f
        fi
    fi
}

# Reset everything
reset_all() {
    log_warn "This will reset all data and containers. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        log_info "Resetting NeuroForge local environment..."

        # Stop services
        stop_services

        # Remove volumes
        docker volume rm neuroforge-local_postgres_data neuroforge-local_redis_data neuroforge-local_weaviate_data 2>/dev/null || true

        # Remove images
        docker rmi neuroforge/api:dev neuroforge/frontend:dev 2>/dev/null || true

        log_success "Reset complete"
    else
        log_info "Reset cancelled"
    fi
}

# Health check
run_health_check() {
    log_info "Running health checks..."

    # Wait a bit for services to start
    sleep 5

    # Check API
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        log_success "✅ API is healthy"
    else
        log_error "❌ API is not responding"
    fi

    # Check Frontend
    if curl -f -s http://localhost:3000 > /dev/null 2>&1; then
        log_success "✅ Frontend is healthy"
    else
        log_warn "⚠️  Frontend is not responding (might still be building)"
    fi

    # Check Database
    if docker exec $PROJECT_NAME-neuroforge-postgres-1 pg_isready -U neuroforge -d neuroforge >/dev/null 2>&1; then
        log_success "✅ PostgreSQL is healthy"
    else
        log_error "❌ PostgreSQL is not responding"
    fi

    # Check Redis
    if docker exec $PROJECT_NAME-neuroforge-redis-1 redis-cli ping | grep -q "PONG"; then
        log_success "✅ Redis is healthy"
    else
        log_error "❌ Redis is not responding"
    fi

    # Check Weaviate
    if curl -f -s http://localhost:8080/v1/meta > /dev/null 2>&1; then
        log_success "✅ Weaviate is healthy"
    else
        log_error "❌ Weaviate is not responding"
    fi
}

# Show usage
usage() {
    echo "NeuroForge Local Development Deployment Script"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  start          - Start all core services"
    echo "  start-monitoring - Start with monitoring (Prometheus + Grafana)"
    echo "  start-dev-tools  - Start with development tools (PgAdmin, RedisInsight)"
    echo "  stop           - Stop all services"
    echo "  restart        - Restart all services"
    echo "  status         - Show service status"
    echo "  logs [service] - Show logs (optionally for specific service)"
    echo "  health         - Run health checks"
    echo "  reset          - Reset all data and containers"
    echo "  pull           - Pull latest images"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start basic services"
    echo "  $0 start-monitoring         # Start with monitoring"
    echo "  $0 logs neuroforge-api      # Show API logs"
    echo "  $0 health                   # Check all services"
    echo ""
    echo "Services:"
    echo "  neuroforge-api      - Main API server"
    echo "  neuroforge-frontend - Frontend application"
    echo "  neuroforge-postgres - PostgreSQL database"
    echo "  neuroforge-redis    - Redis cache"
    echo "  neuroforge-weaviate - Vector database"
}

# Main script logic
case "${1:-help}" in
    "start")
        check_prerequisites
        pull_images
        start_services
        sleep 5
        run_health_check
        show_status
        ;;
    "start-monitoring")
        check_prerequisites
        pull_images
        start_services "monitoring"
        sleep 5
        run_health_check
        show_status
        ;;
    "start-dev-tools")
        check_prerequisites
        pull_images
        start_services "dev-tools"
        sleep 5
        run_health_check
        show_status
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        sleep 2
        start_services
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs "$2"
        ;;
    "health")
        run_health_check
        ;;
    "reset")
        reset_all
        ;;
    "pull")
        pull_images
        ;;
    *)
        usage
        ;;
esac
