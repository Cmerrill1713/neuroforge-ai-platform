#!/usr/bin/env node

/**
 * System Health Monitor and Self-Healing Script
 * Monitors containers, services, and system health
 * Provides automated recovery and alerting capabilities
 */

const { execSync } = require('child_process');
const fs = require('fs');

class SystemMonitor {
  constructor() {
    this.containers = ['agentic-platform', 'ollama', 'postgres', 'redis', 'nginx'];
    this.criticalFiles = [
      '/etc/hosts',
      '/etc/resolv.conf',
      'docker-compose.yml',
      'package.json'
    ];
    this.healthChecks = [];
  }

  // Check container health
  checkContainerHealth() {
    console.log('🔍 Checking container health...');
    const results = {};
    
    this.containers.forEach(container => {
      try {
        const status = execSync(`docker ps --filter "name=${container}" --format "{{.Status}}"`, 
          { encoding: 'utf8', timeout: 5000 }).trim();
        
        results[container] = {
          status: status.includes('Up') ? 'healthy' : 'unhealthy',
          details: status
        };
        
        if (!status.includes('Up')) {
          this.triggerAlert(`Container ${container} is down: ${status}`);
          this.attemptRecovery(container);
        }
      } catch (error) {
        results[container] = {
          status: 'error',
          details: error.message
        };
        this.triggerAlert(`Failed to check container ${container}: ${error.message}`);
      }
    });
    
    return results;
  }

  // Check critical file integrity
  checkFileIntegrity() {
    console.log('📁 Checking file integrity...');
    const results = {};
    
    this.criticalFiles.forEach(file => {
      try {
        if (fs.existsSync(file)) {
          const stats = fs.statSync(file);
          results[file] = {
            status: 'exists',
            size: stats.size,
            modified: stats.mtime
          };
        } else {
          results[file] = {
            status: 'missing',
            alert: true
          };
          this.triggerAlert(`Critical file missing: ${file}`);
        }
      } catch (error) {
        results[file] = {
          status: 'error',
          details: error.message
        };
        this.triggerAlert(`Error checking file ${file}: ${error.message}`);
      }
    });
    
    return results;
  }

  // Check service connectivity
  checkServiceConnectivity() {
    console.log('🌐 Checking service connectivity...');
    const services = {
      'ollama': 'http://localhost:11434/api/tags',
      'frontend': 'http://localhost:3000/api/system/status',
      'postgres': 'localhost:5432',
      'redis': 'localhost:6379'
    };
    
    const results = {};
    
    Object.entries(services).forEach(([service, endpoint]) => {
      try {
        if (endpoint.startsWith('http')) {
          // HTTP endpoint check
          const response = execSync(`curl -s -m 5 "${endpoint}"`, 
            { encoding: 'utf8', timeout: 5000 });
          results[service] = {
            status: response.length > 0 ? 'responsive' : 'unresponsive',
            endpoint
          };
        } else {
          // TCP port check
          const [host, port] = endpoint.split(':');
          execSync(`nc -z ${host} ${port}`, { timeout: 5000 });
          results[service] = {
            status: 'listening',
            endpoint
          };
        }
      } catch (error) {
        results[service] = {
          status: 'unreachable',
          endpoint,
          error: error.message
        };
        this.triggerAlert(`Service ${service} unreachable: ${endpoint}`);
      }
    });
    
    return results;
  }

  // Check system resources
  checkSystemResources() {
    console.log('💻 Checking system resources...');
    const results = {};
    
    try {
      // CPU usage
      const cpuUsage = execSync("top -l 1 | grep 'CPU usage' | awk '{print $3}' | sed 's/%//'", 
        { encoding: 'utf8', timeout: 5000 }).trim();
      
      // Memory usage
      const memInfo = execSync("vm_stat | grep 'Pages free' | awk '{print $3}' | sed 's/\\.//'", 
        { encoding: 'utf8', timeout: 5000 }).trim();
      
      // Disk usage
      const diskUsage = execSync("df -h / | awk 'NR==2 {print $5}' | sed 's/%//'", 
        { encoding: 'utf8', timeout: 5000 }).trim();
      
      results.cpu = parseFloat(cpuUsage);
      results.memory = parseInt(memInfo);
      results.disk = parseFloat(diskUsage);
      
      // Alert on high resource usage
      if (results.cpu > 80) {
        this.triggerAlert(`High CPU usage: ${results.cpu}%`);
      }
      if (results.disk > 90) {
        this.triggerAlert(`High disk usage: ${results.disk}%`);
      }
      
    } catch (error) {
      results.error = error.message;
      this.triggerAlert(`Failed to check system resources: ${error.message}`);
    }
    
    return results;
  }

  // Attempt automatic recovery
  attemptRecovery(container) {
    console.log(`🔧 Attempting recovery for ${container}...`);
    
    try {
      // Try to restart the container
      execSync(`docker restart ${container}`, { timeout: 10000 });
      console.log(`✅ Successfully restarted ${container}`);
      
      // Wait and verify
      setTimeout(() => {
        const status = execSync(`docker ps --filter "name=${container}" --format "{{.Status}}"`, 
          { encoding: 'utf8', timeout: 5000 }).trim();
        
        if (status.includes('Up')) {
          this.triggerAlert(`✅ Recovery successful: ${container} is now running`);
        } else {
          this.triggerAlert(`❌ Recovery failed: ${container} still down after restart`);
        }
      }, 5000);
      
    } catch (error) {
      this.triggerAlert(`❌ Recovery attempt failed for ${container}: ${error.message}`);
    }
  }

  // Trigger alerts
  triggerAlert(message) {
    const timestamp = new Date().toISOString();
    const alert = `[${timestamp}] 🚨 ${message}`;
    
    console.log(alert);
    
    // Log to file
    fs.appendFileSync('system-alerts.log', alert + '\n');
    
    // Send to monitoring system (placeholder)
    this.sendToMonitoringSystem(alert);
  }

  // Send alerts to monitoring system
  sendToMonitoringSystem(alert) {
    // This could integrate with Slack, Discord, email, or other alerting systems
    try {
      // Example: Send to webhook
      execSync(`curl -X POST -H 'Content-Type: application/json' \
        -d '{"text":"${alert}"}' \
        http://localhost:3000/api/alerts`, 
        { timeout: 5000 });
    } catch (error) {
      console.log('Failed to send alert to monitoring system:', error.message);
    }
  }

  // Run comprehensive health check
  async runHealthCheck() {
    console.log('🏥 Starting comprehensive system health check...\n');
    
    const results = {
      timestamp: new Date().toISOString(),
      containers: this.checkContainerHealth(),
      files: this.checkFileIntegrity(),
      services: this.checkServiceConnectivity(),
      resources: this.checkSystemResources()
    };
    
    console.log('\n📊 Health Check Results:');
    console.log(JSON.stringify(results, null, 2));
    
    // Save results
    fs.writeFileSync('health-check-results.json', JSON.stringify(results, null, 2));
    
    return results;
  }

  // Start continuous monitoring
  startMonitoring(interval = 30000) {
    console.log(`🔄 Starting continuous monitoring (interval: ${interval}ms)...`);
    
    // Initial health check
    this.runHealthCheck();
    
    // Set up interval
    setInterval(() => {
      this.runHealthCheck();
    }, interval);
  }
}

// CLI interface
if (require.main === module) {
  const monitor = new SystemMonitor();
  
  const command = process.argv[2];
  
  switch (command) {
    case 'check':
      monitor.runHealthCheck();
      break;
    case 'monitor':
      const interval = parseInt(process.argv[3]) || 30000;
      monitor.startMonitoring(interval);
      break;
    case 'recover':
      const container = process.argv[3];
      if (container) {
        monitor.attemptRecovery(container);
      } else {
        console.log('Usage: node system-monitor.js recover <container-name>');
      }
      break;
    default:
      console.log(`
System Health Monitor Usage:
  node system-monitor.js check                    - Run one-time health check
  node system-monitor.js monitor [interval]       - Start continuous monitoring
  node system-monitor.js recover <container>      - Attempt recovery for container

Examples:
  node system-monitor.js check
  node system-monitor.js monitor 60000
  node system-monitor.js recover postgres
      `);
  }
}

module.exports = SystemMonitor;
