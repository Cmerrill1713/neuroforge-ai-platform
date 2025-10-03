#!/bin/bash
# ============================================================================
# NeuroForge Production Docker Entrypoint - Phase 5
# Production-ready startup script with health checks and graceful shutdown
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Environment validation
validate_environment() {
    log_info "Validating environment variables..."

    # Required environment variables
    required_vars=("ENVIRONMENT" "PORT")

    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            log_error "Required environment variable $var is not set"
            exit 1
        fi
    done

    # Validate port
    if ! [[ "$PORT" =~ ^[0-9]+$ ]] || [ "$PORT" -lt 1000 ] || [ "$PORT" -gt 65535 ]; then
        log_error "Invalid PORT: $PORT (must be between 1000-65535)"
        exit 1
    fi

    log_success "Environment validation passed"
}

# Wait for dependencies
wait_for_dependencies() {
    log_info "Checking service dependencies..."

    # Wait for Redis if configured
    if [[ -n "$REDIS_URL" ]]; then
        log_info "Waiting for Redis..."
        timeout=30
        while ! nc -z redis 6379 2>/dev/null; do
            if [ $timeout -le 0 ]; then
                log_error "Redis is not available after 30 seconds"
                exit 1
            fi
            timeout=$((timeout-1))
            sleep 1
        done
        log_success "Redis is available"
    fi

    # Wait for PostgreSQL if configured
    if [[ -n "$DATABASE_URL" ]]; then
        log_info "Waiting for PostgreSQL..."
        timeout=30
        while ! nc -z postgres 5432 2>/dev/null; do
            if [ $timeout -le 0 ]; then
                log_error "PostgreSQL is not available after 30 seconds"
                exit 1
            fi
            timeout=$((timeout-1))
            sleep 1
        done
        log_success "PostgreSQL is available"
    fi

    # Wait for Weaviate if configured
    if [[ -n "$WEAVIATE_URL" ]]; then
        log_info "Waiting for Weaviate..."
        timeout=30
        while ! curl -f "$WEAVIATE_URL/v1/meta" >/dev/null 2>&1; do
            if [ $timeout -le 0 ]; then
                log_warn "Weaviate is not available, continuing without it"
                break
            fi
            timeout=$((timeout-1))
            sleep 1
        done
        if [ $timeout -gt 0 ]; then
            log_success "Weaviate is available"
        fi
    fi
}

# Pre-flight checks
preflight_checks() {
    log_info "Running pre-flight checks..."

    # Check if application directory exists
    if [[ ! -d "/app" ]]; then
        log_error "Application directory /app not found"
        exit 1
    fi

    # Check if main application file exists
    if [[ ! -f "/app/main.py" ]] && [[ ! -f "/app/src/api/main.py" ]]; then
        log_error "Main application file not found"
        exit 1
    fi

    # Check Python installation
    if ! python3 --version >/dev/null 2>&1; then
        log_error "Python3 is not available"
        exit 1
    fi

    # Check if port is available
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
        log_error "Port $PORT is already in use"
        exit 1
    fi

    log_success "Pre-flight checks passed"
}

# Application startup
start_application() {
    log_info "Starting NeuroForge application..."

    # Set Python path
    export PYTHONPATH="/app:$PYTHONPATH"

    # Set production environment
    export ENVIRONMENT="${ENVIRONMENT:-production}"

    # Determine startup command
    if [[ -n "$GUNICORN_WORKERS" ]]; then
        WORKERS="$GUNICORN_WORKERS"
    else
        # Calculate workers based on CPU cores (2x cores + 1)
        CPU_CORES=$(nproc 2>/dev/null || echo "4")
        WORKERS=$((CPU_CORES * 2 + 1))
        WORKERS=$((WORKERS > 12 ? 12 : WORKERS))  # Cap at 12 workers
    fi

    log_info "Starting with $WORKERS workers on port $PORT"

    # Choose startup command based on environment
    if [[ "$ENVIRONMENT" == "development" ]]; then
        log_info "Starting in development mode with uvicorn reload"
        exec uvicorn \
            --host 0.0.0.0 \
            --port "$PORT" \
            --reload \
            --log-level debug \
            --access-log \
            src.api.main:app
    else
        log_info "Starting in production mode with gunicorn"
        exec gunicorn \
            --bind "0.0.0.0:$PORT" \
            --workers "$WORKERS" \
            --worker-class uvicorn.workers.UvicornWorker \
            --max-requests 1000 \
            --max-requests-jitter 50 \
            --access-logfile - \
            --error-logfile - \
            --log-level info \
            --timeout 30 \
            --keep-alive 10 \
            src.api.main:app
    fi
}

# Graceful shutdown handler
shutdown_handler() {
    log_info "Received shutdown signal, initiating graceful shutdown..."
    # Send SIGTERM to child processes
    kill -TERM "$child_pid" 2>/dev/null || true

    # Wait for graceful shutdown (max 30 seconds)
    for i in {1..30}; do
        if ! kill -0 "$child_pid" 2>/dev/null; then
            log_success "Application shutdown complete"
            exit 0
        fi
        sleep 1
    done

    log_warn "Force terminating application after 30 seconds"
    kill -KILL "$child_pid" 2>/dev/null || true
    exit 1
}

# Main execution
main() {
    log_info "🚀 Starting NeuroForge Production Entrypoint"

    # Validate environment
    validate_environment

    # Run pre-flight checks
    preflight_checks

    # Wait for dependencies
    wait_for_dependencies

    # Set up signal handlers
    trap shutdown_handler SIGTERM SIGINT

    # Start application in background
    start_application &
    child_pid=$!

    # Wait for child process
    wait "$child_pid"
}

# Run main function
main "$@"
