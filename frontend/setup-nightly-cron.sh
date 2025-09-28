#!/bin/bash

# Nightly Startup Cron Job Setup Script
# This script sets up automated nightly execution of the startup system

echo "🌙 Setting up nightly startup automation..."

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NIGHTLY_SCRIPT="$SCRIPT_DIR/nightly-scheduler.js"
LOG_DIR="$SCRIPT_DIR/nightly-logs"

# Create log directory
mkdir -p "$LOG_DIR"

# Create cron job entry
CRON_ENTRY="0 2 * * * cd $SCRIPT_DIR && node nightly-scheduler.js run >> $LOG_DIR/nightly-startup.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "nightly-scheduler.js"; then
    echo "⚠️  Nightly cron job already exists"
    echo "Current cron jobs:"
    crontab -l | grep "nightly-scheduler.js"
    
    read -p "Do you want to update the existing cron job? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove existing cron job
        crontab -l 2>/dev/null | grep -v "nightly-scheduler.js" | crontab -
        echo "✅ Removed existing cron job"
    else
        echo "❌ Keeping existing cron job"
        exit 0
    fi
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Nightly cron job added successfully"
    echo "📅 Scheduled for 2:00 AM UTC daily"
    echo "📁 Logs will be saved to: $LOG_DIR/nightly-startup.log"
    echo ""
    echo "Current cron jobs:"
    crontab -l | grep "nightly-scheduler.js"
    echo ""
    echo "To test the nightly startup manually:"
    echo "  node nightly-scheduler.js run"
    echo ""
    echo "To view logs:"
    echo "  tail -f $LOG_DIR/nightly-startup.log"
    echo ""
    echo "To remove the cron job:"
    echo "  crontab -e"
    echo "  (remove the line with nightly-scheduler.js)"
else
    echo "❌ Failed to add cron job"
    exit 1
fi

# Create additional monitoring scripts
echo "📊 Creating monitoring scripts..."

# Create log rotation script
cat > "$SCRIPT_DIR/rotate-logs.sh" << 'EOF'
#!/bin/bash
# Log rotation script for nightly startup logs

LOG_DIR="$(dirname "$0")/nightly-logs"
MAX_LOGS=30

if [ -d "$LOG_DIR" ]; then
    # Keep only the last MAX_LOGS log files
    find "$LOG_DIR" -name "*.log" -type f | sort -r | tail -n +$((MAX_LOGS + 1)) | xargs -r rm -f
    echo "✅ Log rotation completed"
else
    echo "⚠️  Log directory not found: $LOG_DIR"
fi
EOF

chmod +x "$SCRIPT_DIR/rotate-logs.sh"

# Create system status check script
cat > "$SCRIPT_DIR/check-system-status.sh" << 'EOF'
#!/bin/bash
# System status check script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔍 Checking system status..."

# Check if nightly scheduler is running
if pgrep -f "nightly-scheduler.js" > /dev/null; then
    echo "✅ Nightly scheduler is running"
else
    echo "❌ Nightly scheduler is not running"
fi

# Check last cron execution
LOG_FILE="$SCRIPT_DIR/nightly-logs/nightly-startup.log"
if [ -f "$LOG_FILE" ]; then
    LAST_RUN=$(tail -n 50 "$LOG_FILE" | grep -E "Starting nightly startup|Nightly startup completed" | tail -n 2)
    echo "📅 Last execution:"
    echo "$LAST_RUN"
else
    echo "⚠️  No log file found: $LOG_FILE"
fi

# Check system health
echo ""
echo "🏥 System Health Check:"
cd "$SCRIPT_DIR"
node nightly-scheduler.js validate
EOF

chmod +x "$SCRIPT_DIR/check-system-status.sh"

# Create emergency restart script
cat > "$SCRIPT_DIR/emergency-restart.sh" << 'EOF'
#!/bin/bash
# Emergency restart script for critical system recovery

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚨 Emergency system restart initiated..."

# Kill any stuck processes
pkill -f "nightly-scheduler.js" 2>/dev/null
pkill -f "next dev" 2>/dev/null

# Wait a moment
sleep 5

# Restart Docker containers
echo "🐳 Restarting Docker containers..."
docker restart $(docker ps -q) 2>/dev/null || true

# Wait for containers to start
sleep 10

# Start the application
echo "🚀 Starting application..."
cd "$SCRIPT_DIR"
npm run dev &
APP_PID=$!

# Wait for application to start
sleep 15

# Check if application is running
if curl -s http://localhost:3000/api/system/status > /dev/null; then
    echo "✅ Application started successfully (PID: $APP_PID)"
else
    echo "❌ Application failed to start"
    exit 1
fi

# Run immediate health check
echo "🔍 Running immediate health check..."
node nightly-scheduler.js validate

echo "✅ Emergency restart completed"
EOF

chmod +x "$SCRIPT_DIR/emergency-restart.sh"

# Create notification script
cat > "$SCRIPT_DIR/send-notification.sh" << 'EOF'
#!/bin/bash
# Notification script for nightly startup results

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/nightly-logs/nightly-startup.log"

if [ -f "$LOG_FILE" ]; then
    # Get the last startup result
    LAST_RESULT=$(tail -n 100 "$LOG_FILE" | grep -E "Nightly startup result|success|failed" | tail -n 1)
    
    if echo "$LAST_RESULT" | grep -q "success"; then
        STATUS="✅ SUCCESS"
        COLOR="green"
    else
        STATUS="❌ FAILED"
        COLOR="red"
    fi
    
    # Send notification (customize this for your notification system)
    echo "Nightly Startup Status: $STATUS"
    echo "Last result: $LAST_RESULT"
    
    # Example: Send to Slack webhook (uncomment and configure)
    # curl -X POST -H 'Content-type: application/json' \
    #   --data "{\"text\":\"Nightly Startup: $STATUS - $LAST_RESULT\"}" \
    #   YOUR_SLACK_WEBHOOK_URL
    
    # Example: Send email (uncomment and configure)
    # echo "Nightly Startup: $STATUS - $LAST_RESULT" | mail -s "Nightly Startup Report" your-email@domain.com
else
    echo "⚠️  No log file found for notifications"
fi
EOF

chmod +x "$SCRIPT_DIR/send-notification.sh"

# Add log rotation to cron (weekly)
LOG_ROTATION_ENTRY="0 3 * * 0 $SCRIPT_DIR/rotate-logs.sh >> $LOG_DIR/rotation.log 2>&1"
(crontab -l 2>/dev/null; echo "$LOG_ROTATION_ENTRY") | crontab -

echo "✅ Additional monitoring scripts created:"
echo "  📄 rotate-logs.sh - Log rotation (weekly)"
echo "  📄 check-system-status.sh - System status check"
echo "  📄 emergency-restart.sh - Emergency system restart"
echo "  📄 send-notification.sh - Send notifications"

echo ""
echo "🎉 Nightly startup automation setup completed!"
echo ""
echo "📋 Summary:"
echo "  ⏰ Nightly execution: 2:00 AM UTC daily"
echo "  📁 Logs: $LOG_DIR/nightly-startup.log"
echo "  🔄 Log rotation: Weekly (Sunday 3:00 AM UTC)"
echo ""
echo "🛠️  Available commands:"
echo "  node nightly-scheduler.js run                    - Manual startup"
echo "  node nightly-scheduler.js validate               - System validation"
echo "  ./check-system-status.sh                         - Check system status"
echo "  ./emergency-restart.sh                           - Emergency restart"
echo "  ./send-notification.sh                           - Send notifications"
echo ""
echo "📊 To monitor the system:"
echo "  tail -f $LOG_DIR/nightly-startup.log"
echo "  crontab -l                                        - View cron jobs"
echo "  ./check-system-status.sh                         - Check status"
