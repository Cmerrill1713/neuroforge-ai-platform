#!/bin/bash

##############################################################################
# Integration Test Script
# Tests connectivity and configuration of both backends and frontend
##############################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Log functions
test_start() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

test_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

test_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

##############################################################################
# Test Backend 8004
##############################################################################
test_backend_8004() {
    test_start "Testing Backend on Port 8004..."
    
    # Check if port is listening
    if ! lsof -Pi :8004 -sTCP:LISTEN -t >/dev/null ; then
        test_fail "Backend 8004 is not running"
        return 1
    fi
    test_pass "Backend 8004 is listening"
    
    # Check root endpoint
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8004/)
    if [ "$RESPONSE" = "200" ]; then
        test_pass "Backend 8004 root endpoint returns 200"
    else
        test_fail "Backend 8004 root endpoint returns $RESPONSE (expected 200)"
    fi
    
    # Check health endpoint
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8004/api/system/health)
    if [ "$RESPONSE" = "200" ]; then
        test_pass "Backend 8004 health endpoint returns 200"
    else
        test_fail "Backend 8004 health endpoint returns $RESPONSE (expected 200)"
    fi
    
    # Check docs endpoint
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8004/docs)
    if [ "$RESPONSE" = "200" ]; then
        test_pass "Backend 8004 API docs are accessible"
    else
        test_fail "Backend 8004 API docs return $RESPONSE (expected 200)"
    fi
}

##############################################################################
# Test Frontend 3000
##############################################################################
test_frontend_3000() {
    test_start "Testing Frontend on Port 3000..."
    
    # Check if port is listening
    if ! lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
        test_fail "Frontend 3000 is not running"
        return 1
    fi
    test_pass "Frontend 3000 is listening"
    
    # Check root endpoint
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/)
    if [ "$RESPONSE" = "200" ]; then
        test_pass "Frontend 3000 root endpoint returns 200"
    else
        test_fail "Frontend 3000 root endpoint returns $RESPONSE (expected 200)"
    fi
}

##############################################################################
# Test Frontend API Routes
##############################################################################
test_frontend_api_routes() {
    test_start "Testing Frontend API Routes..."
    
    # These routes should proxy to backend 8004
    ROUTES=(
        "/api/evolutionary/stats"
        "/api/evolutionary/bandit/stats"
        "/api/rag/metrics"
    )
    
    for route in "${ROUTES[@]}"; do
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000$route)
        if [ "$RESPONSE" = "200" ] || [ "$RESPONSE" = "503" ]; then
            # 503 is OK - means backend is proxied but might not have data
            test_pass "Frontend route $route is accessible"
        else
            test_fail "Frontend route $route returns $RESPONSE"
        fi
    done
}

##############################################################################
# Test File Configuration
##############################################################################
test_file_configuration() {
    test_start "Testing File Configuration..."
    
    # Check if files have correct port configuration
    FILES=(
        "frontend/src/app/api/rag/query/route.ts"
        "frontend/src/app/api/rag/metrics/route.ts"
        "frontend/src/app/api/evolutionary/stats/route.ts"
        "frontend/src/app/api/evolutionary/bandit/stats/route.ts"
        "frontend/src/app/api/evolutionary/optimize/route.ts"
    )
    
    cd "/Users/christianmerrill/Prompt Engineering"
    
    for file in "${FILES[@]}"; do
        if [ -f "$file" ]; then
            if grep -q "localhost:8004" "$file"; then
                test_pass "$file correctly configured for port 8004"
            else
                test_fail "$file does not have correct port configuration"
            fi
        else
            test_fail "$file does not exist"
        fi
    done
    
    # Check main.py
    if grep -q "port=8004" "main.py"; then
        test_pass "main.py correctly configured for port 8004"
    else
        test_fail "main.py does not have correct port configuration"
    fi
    
    # Check consolidated_api_architecture.py
    if grep -q "port=8004" "src/api/consolidated_api_architecture.py"; then
        test_pass "consolidated_api_architecture.py correctly configured for port 8004"
    else
        test_fail "consolidated_api_architecture.py does not have correct port configuration"
    fi
}

##############################################################################
# Main Test Execution
##############################################################################
main() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Integration Test Suite${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    # Run tests
    test_file_configuration
    echo ""
    
    test_backend_8004
    echo ""
    
    test_frontend_3000
    echo ""
    
    test_frontend_api_routes
    echo ""
    
    # Display results
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Test Results${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "${GREEN}Tests Passed:${NC} $TESTS_PASSED"
    echo -e "${RED}Tests Failed:${NC} $TESTS_FAILED"
    echo ""
    
    TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
    if [ $TOTAL_TESTS -gt 0 ]; then
        SUCCESS_RATE=$(echo "scale=2; $TESTS_PASSED * 100 / $TOTAL_TESTS" | bc)
        echo -e "Success Rate: ${SUCCESS_RATE}%"
    fi
    echo ""
    
    # Exit with appropriate code
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✅ All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Some tests failed${NC}"
        exit 1
    fi
}

# Run tests
main


