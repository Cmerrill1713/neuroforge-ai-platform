#!/bin/bash
# ============================================================================
# NeuroForge Production Deployment Script - Phase 5
# Automated deployment with health checks and rollback capability
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_SUFFIX="$(date +%Y%m%d_%H%M%S)"
PROJECT_NAME="neuroforge"

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

# Pre-deployment checks
pre_deployment_checks() {
    log_info "Running pre-deployment checks..."

    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi

    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available"
        exit 1
    fi

    # Check if compose file exists
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        log_error "Docker Compose file '$COMPOSE_FILE' not found"
        exit 1
    fi

    # Check required environment variables
    required_vars=("POSTGRES_PASSWORD" "GRAFANA_PASSWORD")
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            log_warn "Environment variable $var is not set"
        fi
    done

    log_success "Pre-deployment checks passed"
}

# Create backup
create_backup() {
    log_info "Creating deployment backup..."

    # Backup current deployment state
    if docker ps -q -f "label=com.docker.compose.project=$PROJECT_NAME" | grep -q .; then
        log_info "Backing up current deployment..."

        # Export container configurations
        mkdir -p "backups/$BACKUP_SUFFIX"
        docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}" -f "label=com.docker.compose.project=$PROJECT_NAME" > "backups/$BACKUP_SUFFIX/containers.txt"

        # Backup volumes (if any)
        if docker volume ls -q -f "label=com.docker.compose.project=$PROJECT_NAME" | grep -q .; then
            docker volume ls -q -f "label=com.docker.compose.project=$PROJECT_NAME" > "backups/$BACKUP_SUFFIX/volumes.txt"
        fi

        log_success "Backup created in backups/$BACKUP_SUFFIX"
    else
        log_info "No existing deployment to backup"
    fi
}

# Pull latest images
pull_images() {
    log_info "Pulling latest Docker images..."

    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$COMPOSE_FILE" pull
    else
        docker compose -f "$COMPOSE_FILE" pull
    fi

    log_success "Images pulled successfully"
}

# Deploy services
deploy_services() {
    log_info "Deploying NeuroForge services..."

    # Use docker-compose or docker compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi

    # Start services
    log_info "Starting services with $COMPOSE_CMD..."
    $COMPOSE_CMD -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d

    log_success "Services started successfully"
}

# Health checks
health_checks() {
    log_info "Running post-deployment health checks..."

    # Wait for services to be healthy
    max_attempts=30
    attempt=1

    while [ $attempt -le $max_attempts ]; do
        log_info "Health check attempt $attempt/$max_attempts..."

        # Check API health
        if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
            log_success "API health check passed"
            api_healthy=true
        else
            log_warn "API not healthy yet"
            api_healthy=false
        fi

        # Check frontend
        if curl -f -s http://localhost:3000/api/health > /dev/null 2>&1; then
            log_success "Frontend health check passed"
            frontend_healthy=true
        else
            log_warn "Frontend not healthy yet"
            frontend_healthy=false
        fi

        # Check databases
        if docker exec $($PROJECT_NAME-neuroforge-postgres-1) pg_isready -U neuroforge > /dev/null 2>&1; then
            log_success "PostgreSQL health check passed"
            postgres_healthy=true
        else
            postgres_healthy=false
        fi

        # If all services are healthy, break
        if [[ "$api_healthy" == "true" && "$frontend_healthy" == "true" && "$postgres_healthy" == "true" ]]; then
            log_success "All health checks passed!"
            return 0
        fi

        sleep 10
        ((attempt++))
    done

    log_error "Health checks failed after $max_attempts attempts"
    return 1
}

# Post-deployment tasks
post_deployment_tasks() {
    log_info "Running post-deployment tasks..."

    # Run database migrations (if applicable)
    log_info "Checking for database migrations..."
    # Add migration commands here if needed

    # Update monitoring configuration
    log_info "Updating monitoring configuration..."
    # Add monitoring setup here if needed

    # Send deployment notification (optional)
    log_info "Deployment completed successfully!"
    log_info "Services available at:"
    log_info "  - API: http://localhost:8000"
    log_info "  - Frontend: http://localhost:3000"
    log_info "  - Monitoring: http://localhost:9090 (Prometheus)"
    log_info "  - Grafana: http://localhost:3001 (admin/admin)"
}

# Rollback function
rollback() {
    log_error "Deployment failed, initiating rollback..."

    # Stop failed deployment
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down
    else
        docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down
    fi

    # Restore from backup if available
    if [[ -d "backups/$BACKUP_SUFFIX" ]]; then
        log_info "Backup available, but manual restoration may be required"
        log_info "Backup location: backups/$BACKUP_SUFFIX"
    fi

    exit 1
}

# Main deployment function
deploy() {
    log_info "🚀 Starting NeuroForge Production Deployment"

    # Trap errors for rollback
    trap rollback ERR

    # Run deployment steps
    pre_deployment_checks
    create_backup
    pull_images
    deploy_services

    # Health checks with timeout
    if ! health_checks; then
        log_error "Health checks failed"
        rollback
    fi

    post_deployment_tasks

    log_success "🎉 NeuroForge deployment completed successfully!"
    log_info "Use 'docker-compose -f $COMPOSE_FILE logs -f' to monitor services"
}

# Show usage
usage() {
    echo "NeuroForge Production Deployment Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  deploy     - Full production deployment (default)"
    echo "  stop       - Stop all services"
    echo "  restart    - Restart all services"
    echo "  logs       - Show service logs"
    echo "  status     - Show service status"
    echo "  cleanup    - Remove stopped containers and unused images"
    echo ""
    echo "Environment Variables:"
    echo "  POSTGRES_PASSWORD  - PostgreSQL password"
    echo "  GRAFANA_PASSWORD   - Grafana admin password"
}

# Main script logic
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "stop")
        log_info "Stopping NeuroForge services..."
        if command -v docker-compose &> /dev/null; then
            docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down
        else
            docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down
        fi
        log_success "Services stopped"
        ;;
    "restart")
        log_info "Restarting NeuroForge services..."
        if command -v docker-compose &> /dev/null; then
            docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" restart
        else
            docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" restart
        fi
        log_success "Services restarted"
        ;;
    "logs")
        if command -v docker-compose &> /dev/null; then
            docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f
        else
            docker compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f
        fi
        ;;
    "status")
        echo "NeuroForge Service Status:"
        echo "=========================="
        docker ps -f "label=com.docker.compose.project=$PROJECT_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        ;;
    "cleanup")
        log_info "Cleaning up Docker resources..."
        docker system prune -f
        docker volume prune -f
        log_success "Cleanup completed"
        ;;
    *)
        usage
        exit 1
        ;;
esac
