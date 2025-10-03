#!/bin/bash

##############################################################################
# Integrated System Startup Script
# Starts both backends (8000, 8004) and frontend (3000)
##############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# PID file locations
BACKEND_8004_PID="/tmp/backend_8004.pid"
FRONTEND_PID="/tmp/frontend_3000.pid"

# Cleanup function
cleanup() {
    log_info "Shutting down services..."
    
    # Kill backend on 8004
    if [ -f "$BACKEND_8004_PID" ]; then
        PID=$(cat "$BACKEND_8004_PID")
        if ps -p $PID > /dev/null 2>&1; then
            log_info "Stopping backend on port 8004 (PID: $PID)..."
            kill $PID 2>/dev/null || true
        fi
        rm -f "$BACKEND_8004_PID"
    fi
    
    # Kill frontend
    if [ -f "$FRONTEND_PID" ]; then
        PID=$(cat "$FRONTEND_PID")
        if ps -p $PID > /dev/null 2>&1; then
            log_info "Stopping frontend on port 3000 (PID: $PID)..."
            kill $PID 2>/dev/null || true
        fi
        rm -f "$FRONTEND_PID"
    fi
    
    # Kill any remaining processes on these ports
    lsof -ti:8004 | xargs kill -9 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    
    log_success "All services stopped"
}

# Register cleanup function
trap cleanup EXIT INT TERM

# Check if ports are available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        log_warning "Port $port is already in use!"
        log_info "Killing process on port $port..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

##############################################################################
# Start Consolidated API (Port 8004)
##############################################################################
start_backend_8004() {
    log_info "Starting Consolidated AI Chat API on port 8004..."
    
    check_port 8004
    
    cd "/Users/christianmerrill/Prompt Engineering"
    
    # Start backend in background
    python3 main.py > logs/backend_8004.log 2>&1 &
    echo $! > "$BACKEND_8004_PID"
    
    # Wait for backend to start
    log_info "Waiting for backend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:8004/ > /dev/null 2>&1; then
            log_success "Backend on port 8004 is running (PID: $(cat $BACKEND_8004_PID))"
            return 0
        fi
        sleep 1
    done
    
    log_error "Backend on port 8004 failed to start"
    return 1
}

##############################################################################
# Start Frontend (Port 3000)
##############################################################################
start_frontend() {
    log_info "Starting Next.js Frontend on port 3000..."
    
    check_port 3000
    
    cd "/Users/christianmerrill/Prompt Engineering/frontend"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        log_info "Installing frontend dependencies..."
        npm install
    fi
    
    # Set environment variables
    export BACKEND_URL=http://localhost:8004
    export NEXT_PUBLIC_API_URL=http://localhost:8004
    
    # Start frontend in background
    npm run dev > ../logs/frontend_3000.log 2>&1 &
    echo $! > "$FRONTEND_PID"
    
    # Wait for frontend to start
    log_info "Waiting for frontend to start..."
    for i in {1..60}; do
        if curl -s http://localhost:3000/ > /dev/null 2>&1; then
            log_success "Frontend on port 3000 is running (PID: $(cat $FRONTEND_PID))"
            return 0
        fi
        sleep 1
    done
    
    log_error "Frontend on port 3000 failed to start"
    return 1
}

##############################################################################
# Health Checks
##############################################################################
run_health_checks() {
    log_info "Running health checks..."
    
    # Check backend 8004
    if curl -s http://localhost:8004/ > /dev/null 2>&1; then
        log_success "✓ Backend 8004: HEALTHY"
    else
        log_error "✗ Backend 8004: UNHEALTHY"
    fi
    
    # Check frontend 3000
    if curl -s http://localhost:3000/ > /dev/null 2>&1; then
        log_success "✓ Frontend 3000: HEALTHY"
    else
        log_error "✗ Frontend 3000: UNHEALTHY"
    fi
}

##############################################################################
# Main Execution
##############################################################################
main() {
    log_info "=================================================="
    log_info "  Integrated System Startup"
    log_info "=================================================="
    echo ""
    
    # Create logs directory if it doesn't exist
    mkdir -p "/Users/christianmerrill/Prompt Engineering/logs"
    
    # Start services
    start_backend_8004 || exit 1
    echo ""
    
    start_frontend || exit 1
    echo ""
    
    # Run health checks
    run_health_checks
    echo ""
    
    # Display status
    log_info "=================================================="
    log_success "  System Ready!"
    log_info "=================================================="
    echo ""
    echo -e "${GREEN}Services:${NC}"
    echo -e "  ${BLUE}Consolidated API:${NC}  http://localhost:8004"
    echo -e "  ${BLUE}API Docs:${NC}          http://localhost:8004/docs"
    echo -e "  ${BLUE}Frontend:${NC}          http://localhost:3000"
    echo ""
    echo -e "${YELLOW}Logs:${NC}"
    echo -e "  Backend 8004: logs/backend_8004.log"
    echo -e "  Frontend 3000: logs/frontend_3000.log"
    echo ""
    echo -e "${GREEN}Press Ctrl+C to stop all services${NC}"
    echo ""
    
    # Keep script running
    wait
}

# Run main function
main


