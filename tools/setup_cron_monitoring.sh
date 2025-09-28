#!/bin/bash

# Cron Setup Script for Automated Monitoring
# This script sets up cron jobs for quality checks and heartbeat monitoring

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MONITORING_SCRIPT="$PROJECT_ROOT/tools/automated_monitoring.sh"

# Function to add cron job
add_cron_job() {
    local schedule="$1"
    local command="$2"
    local description="$3"
    
    # Create cron job entry
    local cron_entry="$schedule $command # $description"
    
    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "$description"; then
        echo "⚠️  Cron job '$description' already exists"
        return 1
    fi
    
    # Add cron job
    (crontab -l 2>/dev/null; echo "$cron_entry") | crontab -
    echo "✅ Added cron job: $description"
    echo "   Schedule: $schedule"
    echo "   Command: $command"
}

# Function to remove cron job
remove_cron_job() {
    local description="$1"
    
    # Remove cron job
    crontab -l 2>/dev/null | grep -v "$description" | crontab -
    echo "✅ Removed cron job: $description"
}

# Function to list current cron jobs
list_cron_jobs() {
    echo "📋 Current cron jobs:"
    crontab -l 2>/dev/null | grep -E "(quality|heartbeat|monitoring)" || echo "   No monitoring cron jobs found"
}

# Function to setup all monitoring jobs
setup_monitoring() {
    echo "🔧 Setting up automated monitoring cron jobs..."
    
    # Ensure monitoring script is executable
    chmod +x "$MONITORING_SCRIPT"
    
    # Add cron jobs
    add_cron_job "0 */6 * * *" "$MONITORING_SCRIPT" "Quality checks every 6 hours"
    add_cron_job "*/15 * * * *" "$MONITORING_SCRIPT" "Heartbeat check every 15 minutes"
    add_cron_job "0 2 * * *" "$MONITORING_SCRIPT" "Daily quality check at 2 AM"
    
    echo ""
    echo "🎉 Automated monitoring setup complete!"
    echo "📊 Monitoring schedule:"
    echo "   - Quality checks: Every 6 hours"
    echo "   - Heartbeat checks: Every 15 minutes"
    echo "   - Daily quality check: 2:00 AM"
    echo ""
    echo "📝 Logs will be written to: $PROJECT_ROOT/archive/logs/automation.log"
    echo "🔍 View current cron jobs with: crontab -l"
}

# Function to remove all monitoring jobs
remove_monitoring() {
    echo "🗑️  Removing automated monitoring cron jobs..."
    
    remove_cron_job "Quality checks every 6 hours"
    remove_cron_job "Heartbeat check every 15 minutes"
    remove_cron_job "Daily quality check at 2 AM"
    
    echo "✅ All monitoring cron jobs removed"
}

# Function to show help
show_help() {
    echo "🤖 Automated Monitoring Cron Setup"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  setup     - Set up automated monitoring cron jobs"
    echo "  remove    - Remove all monitoring cron jobs"
    echo "  list      - List current monitoring cron jobs"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup    # Set up monitoring"
    echo "  $0 remove   # Remove monitoring"
    echo "  $0 list     # List current jobs"
}

# Main execution
case "${1:-help}" in
    "setup")
        setup_monitoring
        ;;
    "remove")
        remove_monitoring
        ;;
    "list")
        list_cron_jobs
        ;;
    "help"|*)
        show_help
        ;;
esac
