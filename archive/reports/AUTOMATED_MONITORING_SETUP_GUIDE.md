# 🤖 **Automated Monitoring Setup Guide**

## **Overview**

This guide explains how to set up automated quality checks and heartbeat monitoring for your AI system. The automation ensures your system stays healthy without manual intervention.

---

## **📋 Available Automation Tools**

### **1. Automated Monitoring Script**
- **File**: `tools/automated_monitoring.sh`
- **Purpose**: Runs quality checks and heartbeat monitoring
- **Features**: Logging, error handling, notifications

### **2. Cron Setup Script**
- **File**: `tools/setup_cron_monitoring.sh`
- **Purpose**: Easy setup/removal of cron jobs
- **Features**: Automated scheduling, job management

### **3. Systemd Service (Alternative)**
- **File**: `tools/ai-monitoring.service`
- **Purpose**: System-level service for monitoring
- **Features**: Better logging, system integration

---

## **🚀 Quick Setup (Recommended)**

### **Step 1: Set Up Cron Jobs**
```bash
# Navigate to project root
cd /Users/christianmerrill/Prompt\ Engineering

# Set up automated monitoring
./tools/setup_cron_monitoring.sh setup
```

### **Step 2: Verify Setup**
```bash
# Check cron jobs
./tools/setup_cron_monitoring.sh list

# Or use crontab directly
crontab -l
```

### **Step 3: Test Monitoring**
```bash
# Run monitoring manually
./tools/automated_monitoring.sh
```

---

## **📊 Monitoring Schedule**

| **Check Type** | **Frequency** | **Purpose** |
|----------------|---------------|-------------|
| **Quality Checks** | Every 6 hours | Code quality, linting |
| **Heartbeat Check** | Every 15 minutes | System health |
| **Daily Quality** | 2:00 AM daily | Comprehensive check |

---

## **📝 Log Files**

- **Main Log**: `archive/logs/automation.log`
- **Quality Checks**: `archive/logs/quality_checks.log`
- **Heartbeat**: `archive/logs/heartbeat.log`

---

## **🔧 Manual Commands**

### **Run Quality Checks**
```bash
python3 tools/run_quality_checks.py
```

### **Run Heartbeat Check**
```bash
python3 tools/check_heartbeat.py
```

### **Run Full Monitoring**
```bash
./tools/automated_monitoring.sh
```

---

## **⚙️ Advanced Setup**

### **Systemd Service (macOS/Linux)**
```bash
# Copy service file
sudo cp tools/ai-monitoring.service /etc/systemd/system/

# Enable service
sudo systemctl enable ai-monitoring.service

# Start service
sudo systemctl start ai-monitoring.service

# Check status
sudo systemctl status ai-monitoring.service
```

### **Custom Cron Schedule**
```bash
# Edit crontab
crontab -e

# Add custom schedule (example: every 30 minutes)
*/30 * * * * /Users/christianmerrill/Prompt\ Engineering/tools/automated_monitoring.sh
```

---

## **🛠️ Troubleshooting**

### **Check Cron Jobs**
```bash
# List all cron jobs
crontab -l

# Check cron service status
sudo systemctl status cron
```

### **Check Logs**
```bash
# View automation logs
tail -f archive/logs/automation.log

# View system logs
journalctl -u ai-monitoring.service
```

### **Test Scripts Manually**
```bash
# Test quality checks
python3 tools/run_quality_checks.py

# Test heartbeat
python3 tools/check_heartbeat.py

# Test full monitoring
./tools/automated_monitoring.sh
```

---

## **📈 Monitoring Benefits**

### **Automated Quality Assurance**
- ✅ Continuous code quality monitoring
- ✅ Early detection of issues
- ✅ Consistent quality standards

### **System Health Monitoring**
- ✅ Real-time system status
- ✅ Proactive issue detection
- ✅ Automated alerting

### **Operational Efficiency**
- ✅ Reduced manual monitoring
- ✅ Consistent check schedules
- ✅ Centralized logging

---

## **🔔 Notification Setup**

### **Email Notifications**
Add to `tools/automated_monitoring.sh`:
```bash
send_notification() {
    local message="$1"
    local status="$2"
    
    # Send email
    echo "$message" | mail -s "$status Alert" your-email@example.com
}
```

### **Slack Notifications**
Add to `tools/automated_monitoring.sh`:
```bash
send_notification() {
    local message="$1"
    local status="$2"
    
    # Send to Slack webhook
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"$status: $message\"}" \
        YOUR_SLACK_WEBHOOK_URL
}
```

---

## **🎯 Next Steps**

1. **Set up monitoring** using the cron setup script
2. **Configure notifications** for alerts
3. **Monitor logs** for the first few days
4. **Adjust schedules** based on your needs
5. **Set up additional checks** as needed

---

## **✅ Success Indicators**

- ✅ Cron jobs are running
- ✅ Log files are being created
- ✅ Quality checks are passing
- ✅ Heartbeat checks are successful
- ✅ Notifications are working (if configured)

Your automated monitoring system is now ready to keep your AI system healthy! 🎉
