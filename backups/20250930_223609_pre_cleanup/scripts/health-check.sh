#!/bin/bash
# ============================================================================
# NeuroForge Health Check Script - Phase 5
# Comprehensive health monitoring for production deployment
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
API_URL=${API_URL:-"http://localhost:8000"}
FRONTEND_URL=${FRONTEND_URL:-"http://localhost:3000"}
TIMEOUT=${TIMEOUT:-10}
RETRIES=${RETRIES:-3}

# Health status
OVERALL_STATUS="HEALTHY"
ISSUES_FOUND=0

# Logging functions
log_info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARN: $1${NC}"
    OVERALL_STATUS="WARNING"
    ((ISSUES_FOUND++))
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    OVERALL_STATUS="UNHEALTHY"
    ((ISSUES_FOUND++))
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}"
}

# Check HTTP endpoint
check_http_endpoint() {
    local url="$1"
    local name="$2"
    local expected_status="${3:-200}"

    log_info "Checking $name: $url"

    local response
    local status_code

    # Try multiple times
    for attempt in $(seq 1 "$RETRIES"); do
        log_info "  Attempt $attempt/$RETRIES..."

        if response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
                          --max-time "$TIMEOUT" \
                          --connect-timeout 5 \
                          "$url" 2>/dev/null); then

            status_code=$(echo "$response" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')

            if [[ "$status_code" == "$expected_status" ]]; then
                log_success "  $name is healthy (HTTP $status_code)"
                return 0
            else
                log_warn "  $name returned HTTP $status_code (expected $expected_status)"
                if [[ $attempt -eq $RETRIES ]]; then
                    return 1
                fi
            fi
        else
            log_warn "  Failed to connect to $name (attempt $attempt/$RETRIES)"
            if [[ $attempt -eq $RETRIES ]]; then
                log_error "  $name is unreachable after $RETRIES attempts"
                return 1
            fi
        fi

        sleep 2
    done
}

# Check database connectivity
check_database() {
    log_info "Checking PostgreSQL database..."

    if command -v pg_isready &> /dev/null; then
        if pg_isready -h neuroforge-postgres -U neuroforge -d neuroforge 2>/dev/null; then
            log_success "  PostgreSQL is healthy"
            return 0
        else
            log_error "  PostgreSQL is not responding"
            return 1
        fi
    elif command -v docker &> /dev/null && docker ps -q -f name=neuroforge-postgres | grep -q .; then
        # Check via docker
        if docker exec neuroforge-postgres pg_isready -U neuroforge -d neuroforge >/dev/null 2>&1; then
            log_success "  PostgreSQL is healthy"
            return 0
        else
            log_error "  PostgreSQL is not responding"
            return 1
        fi
    else
        log_warn "  PostgreSQL check skipped (pg_isready not available)"
        return 0
    fi
}

# Check Redis connectivity
check_redis() {
    log_info "Checking Redis cache..."

    if command -v redis-cli &> /dev/null; then
        if redis-cli -h neuroforge-redis ping 2>/dev/null | grep -q "PONG"; then
            log_success "  Redis is healthy"
            return 0
        else
            log_error "  Redis is not responding"
            return 1
        fi
    elif command -v docker &> /dev/null && docker ps -q -f name=neuroforge-redis | grep -q .; then
        # Check via docker
        if docker exec neuroforge-redis redis-cli ping | grep -q "PONG"; then
            log_success "  Redis is healthy"
            return 0
        else
            log_error "  Redis is not responding"
            return 1
        fi
    else
        log_warn "  Redis check skipped (redis-cli not available)"
        return 0
    fi
}

# Check Weaviate
check_weaviate() {
    log_info "Checking Weaviate vector database..."

    local weaviate_url="http://neuroforge-weaviate:8080"

    if curl -f -s --max-time "$TIMEOUT" "$weaviate_url/v1/meta" >/dev/null 2>&1; then
        log_success "  Weaviate is healthy"
        return 0
    else
        log_error "  Weaviate is not responding"
        return 1
    fi
}

# Check Docker containers
check_containers() {
    log_info "Checking Docker containers..."

    if ! command -v docker &> /dev/null; then
        log_warn "  Docker not available, skipping container checks"
        return 0
    fi

    local containers=("neuroforge-api" "neuroforge-frontend" "neuroforge-postgres" "neuroforge-redis")
    local failed_containers=()

    for container in "${containers[@]}"; do
        if docker ps -q -f name="$container" | grep -q .; then
            local status
            status=$(docker inspect "$container" --format='{{.State.Status}}' 2>/dev/null || echo "unknown")

            if [[ "$status" == "running" ]]; then
                log_success "  Container $container is running"
            else
                log_error "  Container $container is $status"
                failed_containers+=("$container")
            fi
        else
            log_error "  Container $container is not running"
            failed_containers+=("$container")
        fi
    done

    if [[ ${#failed_containers[@]} -gt 0 ]]; then
        return 1
    fi

    return 0
}

# Check system resources
check_system_resources() {
    log_info "Checking system resources..."

    # Check disk space
    local disk_usage
    disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')

    if [[ $disk_usage -gt 90 ]]; then
        log_error "  Disk usage is ${disk_usage}% (threshold: 90%)"
    elif [[ $disk_usage -gt 80 ]]; then
        log_warn "  Disk usage is ${disk_usage}% (warning threshold: 80%)"
    else
        log_success "  Disk usage: ${disk_usage}%"
    fi

    # Check memory usage
    if command -v free &> /dev/null; then
        local mem_usage
        mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')

        if [[ $mem_usage -gt 90 ]]; then
            log_error "  Memory usage is ${mem_usage}% (threshold: 90%)"
        elif [[ $mem_usage -gt 80 ]]; then
            log_warn "  Memory usage is ${mem_usage}% (warning threshold: 80%)"
        else
            log_success "  Memory usage: ${mem_usage}%"
        fi
    fi

    # Check CPU load
    if command -v uptime &> /dev/null; then
        local load_avg
        load_avg=$(uptime | awk -F'load average:' '{ print $2 }' | awk -F, '{ print $1 }' | tr -d ' ')

        local cpu_cores
        cpu_cores=$(nproc 2>/dev/null || echo "4")

        # Simple load check (load > cores * 0.8)
        local load_threshold
        load_threshold=$(echo "scale=2; $cpu_cores * 0.8" | bc 2>/dev/null || echo "3.2")

        if [[ $(echo "$load_avg > $load_threshold" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
            log_warn "  CPU load average: $load_avg (high load)"
        else
            log_success "  CPU load average: $load_avg"
        fi
    fi
}

# Check SSL certificates
check_ssl_certificate() {
    log_info "Checking SSL certificates..."

    if [[ -n "$SSL_DOMAIN" ]]; then
        if command -v openssl &> /dev/null; then
            local cert_expiry
            if cert_expiry=$(echo | openssl s_client -servername "$SSL_DOMAIN" -connect "$SSL_DOMAIN":443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null | grep notAfter | cut -d'=' -f2); then

                local expiry_date
                expiry_date=$(date -d "$cert_expiry" +%s 2>/dev/null || date -j -f "%b %d %H:%M:%S %Y %Z" "$cert_expiry" +%s 2>/dev/null)
                local current_date
                current_date=$(date +%s)
                local days_until_expiry=$(( (expiry_date - current_date) / 86400 ))

                if [[ $days_until_expiry -lt 7 ]]; then
                    log_error "  SSL certificate expires in $days_until_expiry days"
                elif [[ $days_until_expiry -lt 30 ]]; then
                    log_warn "  SSL certificate expires in $days_until_expiry days"
                else
                    log_success "  SSL certificate expires in $days_until_expiry days"
                fi
            else
                log_error "  Could not retrieve SSL certificate information"
            fi
        else
            log_warn "  OpenSSL not available, skipping SSL certificate check"
        fi
    else
        log_info "  SSL domain not configured, skipping certificate check"
    fi
}

# Generate health report
generate_report() {
    local report_file="/tmp/neuroforge-health-report-$(date +%Y%m%d_%H%M%S).json"

    cat << EOF > "$report_file"
{
  "timestamp": "$(date -Iseconds)",
  "overall_status": "$OVERALL_STATUS",
  "issues_found": $ISSUES_FOUND,
  "checks": {
    "api_health": "$(check_http_endpoint "$API_URL/health" "API" "200" 2>/dev/null && echo "PASS" || echo "FAIL")",
    "frontend_health": "$(check_http_endpoint "$FRONTEND_URL/api/health" "Frontend" "200" 2>/dev/null && echo "PASS" || echo "FAIL")",
    "database": "$(check_database 2>/dev/null && echo "PASS" || echo "FAIL")",
    "redis": "$(check_redis 2>/dev/null && echo "PASS" || echo "FAIL")",
    "weaviate": "$(check_weaviate 2>/dev/null && echo "PASS" || echo "FAIL")",
    "containers": "$(check_containers 2>/dev/null && echo "PASS" || echo "FAIL")"
  },
  "system_info": {
    "hostname": "$(hostname)",
    "uptime": "$(uptime -p 2>/dev/null || uptime)",
    "load_average": "$(uptime | awk -F'load average:' '{ print $2 }' | tr -d ' ' 2>/dev/null || echo 'unknown')"
  }
}
EOF

    log_info "Health report generated: $report_file"
}

# Main health check function
perform_health_checks() {
    log_info "🚀 Starting NeuroForge Health Check"

    # API endpoints
    check_http_endpoint "$API_URL/health" "API Health"
    check_http_endpoint "$API_URL/docs" "API Documentation"

    # Frontend
    check_http_endpoint "$FRONTEND_URL" "Frontend"

    # Databases
    check_database
    check_redis
    check_weaviate

    # Infrastructure
    check_containers
    check_system_resources
    check_ssl_certificate

    # Generate report
    generate_report

    # Final status
    log_info "==============================================="
    if [[ "$OVERALL_STATUS" == "HEALTHY" ]]; then
        log_success "🎉 All health checks passed!"
        exit 0
    elif [[ "$OVERALL_STATUS" == "WARNING" ]]; then
        log_warn "⚠️  Health check completed with warnings ($ISSUES_FOUND issues)"
        exit 1
    else
        log_error "❌ Health check failed ($ISSUES_FOUND issues)"
        exit 2
    fi
}

# Show usage
usage() {
    echo "NeuroForge Health Check Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -a, --api-url URL       API base URL (default: http://localhost:8000)"
    echo "  -f, --frontend-url URL  Frontend base URL (default: http://localhost:3000)"
    echo "  -t, --timeout SEC       Request timeout in seconds (default: 10)"
    echo "  -r, --retries NUM       Number of retries (default: 3)"
    echo "  -s, --ssl-domain DOMAIN Domain for SSL certificate check"
    echo "  -h, --help             Show this help"
    echo ""
    echo "Environment Variables:"
    echo "  API_URL       API base URL"
    echo "  FRONTEND_URL  Frontend base URL"
    echo "  TIMEOUT       Request timeout"
    echo "  RETRIES       Number of retries"
    echo "  SSL_DOMAIN    Domain for SSL check"
    echo ""
    echo "Exit codes:"
    echo "  0  All checks passed"
    echo "  1  Warnings found"
    echo "  2  Errors found"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--api-url)
            API_URL="$2"
            shift 2
            ;;
        -f|--frontend-url)
            FRONTEND_URL="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -r|--retries)
            RETRIES="$2"
            shift 2
            ;;
        -s|--ssl-domain)
            SSL_DOMAIN="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Run health checks
perform_health_checks
