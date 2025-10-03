#!/bin/bash

# Setup Automated File Cleanup Cron Jobs
# This script sets up automated file system cleanup to prevent excessive junk accumulation

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
CLEANUP_SCRIPT="$SCRIPT_DIR/comprehensive_file_cleanup.py"
LOG_FILE="$PROJECT_ROOT/logs/automated_cleanup.log"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to add a cron job
add_cron_job() {
    local schedule="$1"
    local command="$2"
    local description="$3"
    
    # Create cron job entry
    local cron_entry="$schedule cd $PROJECT_ROOT && python3 $CLEANUP_SCRIPT >> $LOG_FILE 2>&1 # $description"
    
    # Add to crontab
    (crontab -l 2>/dev/null; echo "$cron_entry") | crontab -
    
    if [ $? -eq 0 ]; then
        log "✅ Added cron job: $description"
        log "   Schedule: $schedule"
        log "   Command: $command"
    else
        log "❌ Failed to add cron job: $description"
        return 1
    fi
}

# Function to remove a cron job
remove_cron_job() {
    local description="$1"
    
    # Remove cron job by description
    crontab -l 2>/dev/null | grep -v "# $description" | crontab -
    
    if [ $? -eq 0 ]; then
        log "✅ Removed cron job: $description"
    else
        log "❌ Failed to remove cron job: $description"
        return 1
    fi
}

# Function to list current cron jobs
list_cron_jobs() {
    echo "📋 Current cleanup cron jobs:"
    echo "================================"
    crontab -l 2>/dev/null | grep "comprehensive_file_cleanup.py" || echo "No cleanup cron jobs found"
    echo ""
}

# Function to setup all cleanup jobs
setup_cleanup() {
    log "🧹 Setting up automated file cleanup cron jobs..."
    
    # Ensure cleanup script is executable
    chmod +x "$CLEANUP_SCRIPT"
    
    # Ensure logs directory exists
    mkdir -p "$PROJECT_ROOT/logs"
    
    # Add cron jobs for different cleanup frequencies
    add_cron_job "0 2 * * *" "daily_cleanup" "Daily comprehensive cleanup at 2 AM"
    add_cron_job "0 */6 * * *" "cache_cleanup" "Cache cleanup every 6 hours"
    add_cron_job "0 0 * * 0" "weekly_cleanup" "Weekly deep cleanup on Sunday at midnight"
    add_cron_job "0 1 1 * *" "monthly_cleanup" "Monthly archive cleanup on 1st at 1 AM"
    
    log ""
    log "🎉 Automated file cleanup setup complete!"
    log "📊 Cleanup schedule:"
    log "   - Daily cleanup: 2:00 AM (comprehensive)"
    log "   - Cache cleanup: Every 6 hours"
    log "   - Weekly cleanup: Sunday at midnight (deep)"
    log "   - Monthly cleanup: 1st of month at 1 AM (archive)"
    log ""
    log "📝 Logs will be written to: $LOG_FILE"
    log "🔍 View current cron jobs with: crontab -l"
    log "📊 View cleanup stats with: python3 $CLEANUP_SCRIPT"
}

# Function to remove all cleanup jobs
remove_cleanup() {
    log "🗑️ Removing automated file cleanup cron jobs..."
    
    remove_cron_job "Daily comprehensive cleanup at 2 AM"
    remove_cron_job "Cache cleanup every 6 hours"
    remove_cron_job "Weekly deep cleanup on Sunday at midnight"
    remove_cron_job "Monthly archive cleanup on 1st at 1 AM"
    
    log "✅ All cleanup cron jobs removed"
}

# Function to run cleanup manually
run_cleanup() {
    log "🧹 Running manual file cleanup..."
    cd "$PROJECT_ROOT"
    python3 "$CLEANUP_SCRIPT"
}

# Function to show cleanup stats
show_stats() {
    log "📊 File cleanup statistics:"
    echo "================================"
    
    if [ -f "$PROJECT_ROOT/logs/cleanup_stats.json" ]; then
        python3 -c "
import json
import sys
from datetime import datetime

try:
    with open('$PROJECT_ROOT/logs/cleanup_stats.json', 'r') as f:
        stats = json.load(f)
    
    if stats:
        print('Recent cleanup history:')
        print('-' * 40)
        for stat in stats[-10:]:  # Show last 10
            timestamp = stat['timestamp']
            files = stat['files_deleted']
            space = stat['space_freed_mb']
            duration = stat['cleanup_duration']
            print(f'{timestamp}: {files} files, {space:.1f}MB freed ({duration:.1f}s)')
        
        # Calculate totals
        total_files = sum(s['files_deleted'] for s in stats)
        total_space = sum(s['space_freed_mb'] for s in stats)
        print('-' * 40)
        print(f'Total: {total_files} files, {total_space:.1f}MB freed')
    else:
        print('No cleanup history found')
        
except Exception as e:
    print(f'Error reading stats: {e}')
"
    else
        echo "No cleanup statistics found"
    fi
    
    echo ""
    echo "Disk usage:"
    echo "-----------"
    df -h "$PROJECT_ROOT" | tail -1
}

# Function to show help
show_help() {
    echo "🧹 Automated File Cleanup Cron Setup"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  setup     - Set up automated cleanup cron jobs"
    echo "  remove    - Remove all cleanup cron jobs"
    echo "  list      - List current cleanup cron jobs"
    echo "  run       - Run cleanup manually"
    echo "  stats     - Show cleanup statistics"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup    # Set up automated cleanup"
    echo "  $0 remove   # Remove automated cleanup"
    echo "  $0 run      # Run cleanup now"
    echo "  $0 stats    # Show cleanup history"
    echo ""
    echo "Cleanup Configuration:"
    echo "  Config file: $PROJECT_ROOT/config/cleanup_config.json"
    echo "  Log file: $LOG_FILE"
    echo "  Stats file: $PROJECT_ROOT/logs/cleanup_stats.json"
}

# Main execution
case "${1:-help}" in
    "setup")
        setup_cleanup
        ;;
    "remove")
        remove_cleanup
        ;;
    "list")
        list_cron_jobs
        ;;
    "run")
        run_cleanup
        ;;
    "stats")
        show_stats
        ;;
    "help"|*)
        show_help
        ;;
esac
