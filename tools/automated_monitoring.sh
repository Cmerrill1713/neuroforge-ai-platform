#!/bin/bash

# Automated Quality Checks and Monitoring Script
# This script runs quality checks and heartbeat monitoring
# Designed to be run via cron or manually

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Log file for automation
LOG_FILE="$PROJECT_ROOT/archive/logs/automation.log"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to run quality checks
run_quality_checks() {
    log "🔍 Starting automated quality checks..."
    cd "$PROJECT_ROOT"
    
    # Run Python quality checks
    if python3 tools/run_quality_checks.py >> "$LOG_FILE" 2>&1; then
        log "✅ Quality checks completed successfully"
        return 0
    else
        log "❌ Quality checks failed - check logs for details"
        return 1
    fi
}

# Function to run heartbeat check
run_heartbeat_check() {
    log "💓 Starting heartbeat check..."
    cd "$PROJECT_ROOT"
    
    # Run heartbeat check
    if python3 tools/check_heartbeat.py >> "$LOG_FILE" 2>&1; then
        log "✅ Heartbeat check completed successfully"
        return 0
    else
        log "❌ Heartbeat check failed - system may be down"
        return 1
    fi
}

# Function to send notification (if configured)
send_notification() {
    local message="$1"
    local status="$2"
    
    # Add notification logic here (email, Slack, etc.)
    log "📧 Notification: $status - $message"
}

# Main execution
main() {
    log "🚀 Starting automated monitoring cycle..."
    
    # Run quality checks
    if run_quality_checks; then
        log "✅ Quality checks passed"
    else
        log "❌ Quality checks failed"
        send_notification "Quality checks failed" "ERROR"
    fi
    
    # Run heartbeat check
    if run_heartbeat_check; then
        log "✅ Heartbeat check passed"
    else
        log "❌ Heartbeat check failed"
        send_notification "Heartbeat check failed - system may be down" "CRITICAL"
    fi
    
    log "🏁 Automated monitoring cycle completed"
}

# Run main function
main "$@"
