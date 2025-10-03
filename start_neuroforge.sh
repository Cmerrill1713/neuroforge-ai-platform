#!/bin/bash

##############################################################################
# NeuroForge System Startup Script
# Integrated AI Development Platform with Phase 1 Orchestration Enhancement
##############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# PID files
BACKEND_PID="/tmp/neuroforge_backend_8004.pid"
FRONTEND_PID="/tmp/neuroforge_frontend_3000.pid"

# Log files
LOG_DIR="/Users/christianmerrill/Prompt Engineering/logs"
BACKEND_LOG="$LOG_DIR/neuroforge_backend.log"
FRONTEND_LOG="$LOG_DIR/neuroforge_frontend.log"

# Cleanup function
cleanup() {
    echo -e "\n${CYAN}[NEUROFORGE]${NC} Shutting down system..."
    
    if [ -f "$BACKEND_PID" ]; then
        PID=$(cat "$BACKEND_PID")
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${BLUE}[INFO]${NC} Stopping backend (PID: $PID)..."
            kill $PID 2>/dev/null || true
        fi
        rm -f "$BACKEND_PID"
    fi
    
    if [ -f "$FRONTEND_PID" ]; then
        PID=$(cat "$FRONTEND_PID")
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${BLUE}[INFO]${NC} Stopping frontend (PID: $PID)..."
            kill $PID 2>/dev/null || true
        fi
        rm -f "$FRONTEND_PID"
    fi
    
    lsof -ti:8004 | xargs kill -9 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    
    echo -e "${GREEN}[SUCCESS]${NC} NeuroForge shutdown complete"
}

trap cleanup EXIT INT TERM

# Check and kill if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}[WARNING]${NC} Port $port is in use, clearing..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Create log directory
mkdir -p "$LOG_DIR"

# Banner
echo -e "${PURPLE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                                ║
║           ███╗   ██╗███████╗██╗   ██╗██████╗  ██████╗         ║
║           ████╗  ██║██╔════╝██║   ██║██╔══██╗██╔═══██╗        ║
║           ██╔██╗ ██║█████╗  ██║   ██║██████╔╝██║   ██║        ║
║           ██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██║   ██║        ║
║           ██║ ╚████║███████╗╚██████╔╝██║  ██║╚██████╔╝        ║
║           ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝         ║
║                                                                ║
║    ███████╗ ██████╗ ██████╗  ██████╗ ███████╗                 ║
║    ██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝                 ║
║    █████╗  ██║   ██║██████╔╝██║  ███╗█████╗                   ║
║    ██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝                   ║
║    ██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗                 ║
║    ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝                 ║
║                                                                ║
║              AI Development Platform v1.0                      ║
║          Phase 1: Enhanced Orchestration Active               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${CYAN}[NEUROFORGE]${NC} Initializing system components..."
echo ""

# System check
echo -e "${BLUE}[PHASE 1]${NC} Verifying NeuroForge Components..."

COMPONENTS=(
    "Enhanced Model Registry:src/core/models/enhanced_registry.py"
    "Intelligent Router:src/core/engines/intelligent_model_router.py"
    "Enhanced Monitor:src/core/monitoring/enhanced_monitor.py"
    "Orchestration Bridge:src/core/orchestration_bridge.py"
    "Evolutionary Optimizer:src/core/prompting/evolutionary_optimizer.py"
    "Performance Learner:src/core/routing/intelligent_router.py"
)

for component in "${COMPONENTS[@]}"; do
    IFS=':' read -r name file <<< "$component"
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $name"
    else
        echo -e "  ${RED}✗${NC} $name ${YELLOW}(Warning: File not found)${NC}"
    fi
done

echo ""
echo -e "${BLUE}[STARTUP]${NC} Starting NeuroForge services..."
echo ""

##############################################################################
# Start Backend (Port 8004)
##############################################################################
echo -e "${CYAN}[BACKEND]${NC} Starting Consolidated API on port 8004..."
check_port 8004

cd "/Users/christianmerrill/Prompt Engineering"

# Start backend with enhanced logging
python3 main.py > "$BACKEND_LOG" 2>&1 &
echo $! > "$BACKEND_PID"

echo -e "${BLUE}[INFO]${NC} Backend starting (PID: $(cat $BACKEND_PID))..."
echo -e "${BLUE}[INFO]${NC} Logs: $BACKEND_LOG"

# Wait for backend
for i in {1..30}; do
    if curl -s http://localhost:8004/ > /dev/null 2>&1; then
        echo -e "${GREEN}[SUCCESS]${NC} Backend API is running"
        echo -e "  ${CYAN}→${NC} API: http://localhost:8004"
        echo -e "  ${CYAN}→${NC} Docs: http://localhost:8004/docs"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}[ERROR]${NC} Backend failed to start"
        echo -e "${YELLOW}[INFO]${NC} Check logs: tail -f $BACKEND_LOG"
        exit 1
    fi
done

echo ""

##############################################################################
# Start Frontend (Port 3000)
##############################################################################
echo -e "${CYAN}[FRONTEND]${NC} Starting Next.js Frontend on port 3000..."
check_port 3000

cd "/Users/christianmerrill/Prompt Engineering/frontend"

export BACKEND_URL=http://localhost:8004
export NEXT_PUBLIC_API_URL=http://localhost:8004

npm run dev > "$FRONTEND_LOG" 2>&1 &
echo $! > "$FRONTEND_PID"

echo -e "${BLUE}[INFO]${NC} Frontend starting (PID: $(cat $FRONTEND_PID))..."
echo -e "${BLUE}[INFO]${NC} Logs: $FRONTEND_LOG"

# Wait for frontend
for i in {1..60}; do
    if curl -s http://localhost:3000/ > /dev/null 2>&1; then
        echo -e "${GREEN}[SUCCESS]${NC} Frontend is running"
        echo -e "  ${CYAN}→${NC} UI: http://localhost:3000"
        break
    fi
    sleep 1
    if [ $i -eq 60 ]; then
        echo -e "${RED}[ERROR]${NC} Frontend failed to start"
        echo -e "${YELLOW}[INFO]${NC} Check logs: tail -f $FRONTEND_LOG"
        exit 1
    fi
done

echo ""

##############################################################################
# System Status
##############################################################################
echo -e "${PURPLE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                                                        ║${NC}"
echo -e "${PURPLE}║${NC}  ${GREEN}✓${NC} NeuroForge System Ready                            ${PURPLE}║${NC}"
echo -e "${PURPLE}║                                                        ║${NC}"
echo -e "${PURPLE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}[SERVICES]${NC}"
echo -e "  ${GREEN}●${NC} Consolidated API   http://localhost:8004"
echo -e "  ${GREEN}●${NC} API Documentation  http://localhost:8004/docs"
echo -e "  ${GREEN}●${NC} Frontend UI        http://localhost:3000"
echo ""

echo -e "${CYAN}[FEATURES ACTIVE]${NC}"
echo -e "  ${BLUE}◆${NC} Enhanced Model Registry"
echo -e "  ${BLUE}◆${NC} Intelligent Router (ML-Based)"
echo -e "  ${BLUE}◆${NC} Thompson Bandit Selection"
echo -e "  ${BLUE}◆${NC} Evolutionary Optimization"
echo -e "  ${BLUE}◆${NC} Performance Learning"
echo -e "  ${BLUE}◆${NC} Advanced Monitoring"
echo ""

echo -e "${CYAN}[LOGS]${NC}"
echo -e "  ${YELLOW}→${NC} Backend:  tail -f $BACKEND_LOG"
echo -e "  ${YELLOW}→${NC} Frontend: tail -f $FRONTEND_LOG"
echo ""

echo -e "${CYAN}[HEALTH CHECK]${NC}"
BACKEND_STATUS=$(curl -s http://localhost:8004/ | grep -o "running" || echo "unknown")
FRONTEND_STATUS=$(curl -s http://localhost:3000/ | grep -o "DOCTYPE" && echo "running" || echo "unknown")

if [ "$BACKEND_STATUS" = "running" ]; then
    echo -e "  ${GREEN}✓${NC} Backend: Healthy"
else
    echo -e "  ${YELLOW}⚠${NC} Backend: $BACKEND_STATUS"
fi

if [ "$FRONTEND_STATUS" = "running" ]; then
    echo -e "  ${GREEN}✓${NC} Frontend: Healthy"
else
    echo -e "  ${YELLOW}⚠${NC} Frontend: $FRONTEND_STATUS"
fi

echo ""
echo -e "${CYAN}[NEUROFORGE]${NC} Press ${YELLOW}Ctrl+C${NC} to stop all services"
echo ""

# Keep script running
wait

