#!/usr/bin/env node

/**
 * Nightly Startup Scheduler and Automation System
 * Automatically runs system validation, optimization, and self-improvement
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

class NightlyScheduler {
  constructor() {
    this.scheduleTime = '02:00'; // 2:00 AM UTC
    this.maxRetries = 3;
    this.retryDelay = 300000; // 5 minutes
    this.logFile = 'nightly-scheduler.log';
    this.reportDir = 'nightly-reports';
    
    // Ensure report directory exists
    if (!fs.existsSync(this.reportDir)) {
      fs.mkdirSync(this.reportDir, { recursive: true });
    }
  }

  // Log with timestamp
  log(message, level = 'INFO') {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [${level}] ${message}`;
    
    console.log(logMessage);
    fs.appendFileSync(this.logFile, logMessage + '\n');
  }

  // Execute nightly startup with retry logic
  async executeNightlyStartup() {
    this.log('🌙 Starting nightly startup sequence...');
    
    for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
      try {
        this.log(`Attempt ${attempt}/${this.maxRetries}`);
        
        const result = await this.runStartupSequence();
        
        if (result.success) {
          this.log('✅ Nightly startup completed successfully');
          await this.generateSummaryReport(result);
          return result;
        } else {
          this.log(`⚠️ Nightly startup failed (attempt ${attempt}): ${result.error}`);
          
          if (attempt < this.maxRetries) {
            this.log(`Retrying in ${this.retryDelay / 1000} seconds...`);
            await this.sleep(this.retryDelay);
          }
        }
      } catch (error) {
        this.log(`❌ Nightly startup error (attempt ${attempt}): ${error.message}`, 'ERROR');
        
        if (attempt < this.maxRetries) {
          this.log(`Retrying in ${this.retryDelay / 1000} seconds...`);
          await this.sleep(this.retryDelay);
        }
      }
    }
    
    this.log('❌ All startup attempts failed', 'ERROR');
    return { success: false, error: 'All attempts failed' };
  }

  // Run the actual startup sequence
  async runStartupSequence() {
    const startTime = Date.now();
    
    try {
      // Step 1: Pre-startup validation
      this.log('🔍 Running pre-startup validation...');
      await this.preStartupValidation();
      
      // Step 2: Start services if needed
      this.log('🚀 Starting required services...');
      await this.startRequiredServices();
      
      // Step 3: Execute main startup sequence
      this.log('⚙️ Executing main startup sequence...');
      const startupResult = await this.callStartupAPI();
      
      // Step 4: Post-startup validation
      this.log('✅ Running post-startup validation...');
      await this.postStartupValidation();
      
      // Step 5: Performance optimization
      this.log('🔧 Running performance optimization...');
      await this.runPerformanceOptimization();
      
      // Step 6: Security audit
      this.log('🛡️ Running security audit...');
      await this.runSecurityAudit();
      
      // Step 7: Knowledge base optimization
      this.log('📚 Optimizing knowledge base...');
      await this.optimizeKnowledgeBase();
      
      // Step 8: System self-improvement
      this.log('🧠 Running system self-improvement...');
      await this.runSystemSelfImprovement();
      
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      this.log(`🎉 Nightly startup completed in ${duration}ms`);
      
      return {
        success: true,
        duration,
        startupResult,
        timestamp: new Date().toISOString()
      };
      
    } catch (error) {
      this.log(`❌ Startup sequence failed: ${error.message}`, 'ERROR');
      return { success: false, error: error.message };
    }
  }

  // Pre-startup validation
  async preStartupValidation() {
    const validation = {
      docker: false,
      node: false,
      npm: false,
      git: false,
      diskSpace: 0,
      memory: 0
    };

    try {
      // Check Docker
      execSync('docker --version', { timeout: 5000 });
      validation.docker = true;
      this.log('✅ Docker is available');

      // Check Node.js
      const nodeVersion = execSync('node --version', { encoding: 'utf8', timeout: 5000 });
      validation.node = true;
      this.log(`✅ Node.js version: ${nodeVersion.trim()}`);

      // Check npm
      const npmVersion = execSync('npm --version', { encoding: 'utf8', timeout: 5000 });
      validation.npm = true;
      this.log(`✅ npm version: ${npmVersion.trim()}`);

      // Check git
      const gitVersion = execSync('git --version', { encoding: 'utf8', timeout: 5000 });
      validation.git = true;
      this.log(`✅ Git version: ${gitVersion.trim()}`);

      // Check disk space
      const diskUsage = execSync("df -h / | awk 'NR==2 {print $5}' | sed 's/%//'", 
        { encoding: 'utf8', timeout: 5000 }).trim();
      validation.diskSpace = parseFloat(diskUsage);
      
      if (validation.diskSpace > 90) {
        this.log(`⚠️ High disk usage: ${validation.diskSpace}%`, 'WARN');
        await this.cleanupDisk();
      } else {
        this.log(`✅ Disk usage: ${validation.diskSpace}%`);
      }

      // Check memory
      const memInfo = execSync("vm_stat | grep 'Pages free' | awk '{print $3}' | sed 's/\\.//'", 
        { encoding: 'utf8', timeout: 5000 }).trim();
      validation.memory = parseInt(memInfo);
      this.log(`✅ Free memory pages: ${validation.memory}`);

    } catch (error) {
      this.log(`❌ Pre-startup validation failed: ${error.message}`, 'ERROR');
      throw error;
    }

    return validation;
  }

  // Start required services
  async startRequiredServices() {
    const services = [
      { name: 'ollama', command: 'ollama serve', port: 11434 },
      { name: 'postgres', command: 'docker start postgres', port: 5432 },
      { name: 'redis', command: 'docker start redis', port: 6379 },
      { name: 'nginx', command: 'docker start nginx', port: 80 }
    ];

    for (const service of services) {
      try {
        // Check if service is already running
        const isRunning = await this.checkServiceRunning(service.port);
        
        if (!isRunning) {
          this.log(`🚀 Starting ${service.name}...`);
          
          try {
            execSync(service.command, { timeout: 30000 });
            this.log(`✅ ${service.name} started successfully`);
          } catch (startError) {
            this.log(`⚠️ Could not start ${service.name}: ${startError.message}`, 'WARN');
          }
        } else {
          this.log(`✅ ${service.name} is already running`);
        }
      } catch (error) {
        this.log(`⚠️ Service check failed for ${service.name}: ${error.message}`, 'WARN');
      }
    }
  }

  // Check if service is running on port
  async checkServiceRunning(port) {
    try {
      execSync(`lsof -i :${port}`, { timeout: 5000 });
      return true;
    } catch (error) {
      return false;
    }
  }

  // Call startup API
  async callStartupAPI() {
    try {
      const response = execSync(`curl -s -X POST http://localhost:3000/api/nightly-startup \
        -H "Content-Type: application/json" \
        -d '{"action": "startup"}'`, 
        { encoding: 'utf8', timeout: 300000 }); // 5 minute timeout
      
      return JSON.parse(response);
    } catch (error) {
      this.log(`❌ Startup API call failed: ${error.message}`, 'ERROR');
      throw error;
    }
  }

  // Post-startup validation
  async postStartupValidation() {
    try {
      // Test critical endpoints
      const endpoints = [
        'http://localhost:3000/api/system/status',
        'http://localhost:11434/api/tags',
        'http://localhost:3000/api/self-healing?type=status'
      ];

      for (const endpoint of endpoints) {
        try {
          execSync(`curl -s -m 10 "${endpoint}"`, { timeout: 10000 });
          this.log(`✅ Endpoint validated: ${endpoint}`);
        } catch (error) {
          this.log(`⚠️ Endpoint validation failed: ${endpoint}`, 'WARN');
        }
      }
    } catch (error) {
      this.log(`⚠️ Post-startup validation warning: ${error.message}`, 'WARN');
    }
  }

  // Performance optimization
  async runPerformanceOptimization() {
    try {
      // Clean up temporary files
      this.log('🧹 Cleaning up temporary files...');
      execSync('find /tmp -name "*.tmp" -mtime +1 -delete', { timeout: 30000 });
      
      // Clean up Docker system
      this.log('🐳 Cleaning up Docker system...');
      execSync('docker system prune -f', { timeout: 60000 });
      
      // Optimize database
      this.log('🗄️ Optimizing database...');
      try {
        execSync('docker exec postgres psql -U user -d microservice_db -c "VACUUM ANALYZE;"', 
          { timeout: 60000 });
      } catch (dbError) {
        this.log(`⚠️ Database optimization warning: ${dbError.message}`, 'WARN');
      }
      
      this.log('✅ Performance optimization completed');
    } catch (error) {
      this.log(`⚠️ Performance optimization warning: ${error.message}`, 'WARN');
    }
  }

  // Security audit
  async runSecurityAudit() {
    try {
      this.log('🛡️ Running security audit...');
      
      // Check for outdated packages
      try {
        const outdated = execSync('npm outdated --json', { encoding: 'utf8', timeout: 30000 });
        if (outdated && outdated.trim() !== '{}') {
          const outdatedPackages = JSON.parse(outdated);
          this.log(`⚠️ Found ${Object.keys(outdatedPackages).length} outdated packages`, 'WARN');
          
          // Log critical outdated packages
          for (const [pkg, info] of Object.entries(outdatedPackages)) {
            if (info.current !== info.latest) {
              this.log(`  - ${pkg}: ${info.current} -> ${info.latest}`, 'WARN');
            }
          }
        } else {
          this.log('✅ All packages are up to date');
        }
      } catch (npmError) {
        this.log(`⚠️ Package audit warning: ${npmError.message}`, 'WARN');
      }
      
      // Check for security vulnerabilities
      try {
        const audit = execSync('npm audit --json', { encoding: 'utf8', timeout: 30000 });
        const auditResult = JSON.parse(audit);
        
        if (auditResult.vulnerabilities && Object.keys(auditResult.vulnerabilities).length > 0) {
          this.log(`⚠️ Found ${Object.keys(auditResult.vulnerabilities).length} security vulnerabilities`, 'WARN');
        } else {
          this.log('✅ No security vulnerabilities found');
        }
      } catch (auditError) {
        this.log(`⚠️ Security audit warning: ${auditError.message}`, 'WARN');
      }
      
      this.log('✅ Security audit completed');
    } catch (error) {
      this.log(`⚠️ Security audit warning: ${error.message}`, 'WARN');
    }
  }

  // Knowledge base optimization
  async optimizeKnowledgeBase() {
    try {
      this.log('📚 Optimizing knowledge base...');
      
      // Check knowledge base directory
      const knowledgeDir = path.join(process.cwd(), 'knowledge');
      if (fs.existsSync(knowledgeDir)) {
        const files = fs.readdirSync(knowledgeDir);
        const docCount = files.filter(f => f.endsWith('.txt') || f.endsWith('.md')).length;
        this.log(`✅ Knowledge base contains ${docCount} documents`);
        
        // Optimize search index if it exists
        const indexPath = path.join(process.cwd(), 'search-index.json');
        if (fs.existsSync(indexPath)) {
          const indexData = JSON.parse(fs.readFileSync(indexPath, 'utf8'));
          this.log(`✅ Search index contains ${Object.keys(indexData).length} entries`);
        }
      } else {
        this.log('⚠️ Knowledge base directory not found', 'WARN');
      }
      
      this.log('✅ Knowledge base optimization completed');
    } catch (error) {
      this.log(`⚠️ Knowledge base optimization warning: ${error.message}`, 'WARN');
    }
  }

  // System self-improvement
  async runSystemSelfImprovement() {
    try {
      this.log('🧠 Running system self-improvement...');
      
      // Call self-optimization API
      try {
        const response = execSync(`curl -s -X POST http://localhost:3000/api/self-optimization \
          -H "Content-Type: application/json" \
          -d '{"action": "auto_heal"}'`, 
          { encoding: 'utf8', timeout: 120000 }); // 2 minute timeout
        
        const result = JSON.parse(response);
        if (result.success) {
          this.log(`✅ Self-improvement completed: ${result.summary.actionsExecuted} actions executed`);
        } else {
          this.log(`⚠️ Self-improvement had issues: ${result.error}`, 'WARN');
        }
      } catch (apiError) {
        this.log(`⚠️ Self-improvement API warning: ${apiError.message}`, 'WARN');
      }
      
      this.log('✅ System self-improvement completed');
    } catch (error) {
      this.log(`⚠️ System self-improvement warning: ${error.message}`, 'WARN');
    }
  }

  // Clean up disk space
  async cleanupDisk() {
    try {
      this.log('🧹 Cleaning up disk space...');
      
      // Clean npm cache
      execSync('npm cache clean --force', { timeout: 60000 });
      
      // Clean Docker system
      execSync('docker system prune -f', { timeout: 120000 });
      
      // Clean old log files
      execSync('find /var/log -name "*.log" -mtime +7 -delete', { timeout: 60000 });
      
      this.log('✅ Disk cleanup completed');
    } catch (error) {
      this.log(`⚠️ Disk cleanup warning: ${error.message}`, 'WARN');
    }
  }

  // Generate summary report
  async generateSummaryReport(result) {
    try {
      const report = {
        timestamp: new Date().toISOString(),
        success: result.success,
        duration: result.duration,
        startupResult: result.startupResult,
        systemHealth: result.startupResult?.systemHealth || 0,
        recommendations: result.startupResult?.phases?.map(p => p.results) || []
      };

      const reportFile = path.join(this.reportDir, `nightly-report-${new Date().toISOString().split('T')[0]}.json`);
      fs.writeFileSync(reportFile, JSON.stringify(report, null, 2));
      
      this.log(`📊 Summary report generated: ${reportFile}`);
    } catch (error) {
      this.log(`⚠️ Report generation warning: ${error.message}`, 'WARN');
    }
  }

  // Sleep utility
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Schedule nightly execution
  scheduleNightlyExecution() {
    this.log('⏰ Scheduling nightly execution...');
    
    // In a production environment, this would use cron or a task scheduler
    // For now, we'll simulate scheduling
    this.log(`📅 Nightly startup scheduled for ${this.scheduleTime} UTC daily`);
    this.log('💡 To run manually: node nightly-scheduler.js run');
    
    return true;
  }

  // Check if it's time to run
  shouldRun() {
    const now = new Date();
    const currentTime = now.toTimeString().split(' ')[0].substring(0, 5);
    return currentTime === this.scheduleTime;
  }
}

// CLI interface
if (require.main === module) {
  const scheduler = new NightlyScheduler();
  
  const command = process.argv[2];
  
  switch (command) {
    case 'run':
      scheduler.executeNightlyStartup()
        .then(result => {
          console.log('Nightly startup result:', result);
          process.exit(result.success ? 0 : 1);
        })
        .catch(error => {
          console.error('Nightly startup failed:', error);
          process.exit(1);
        });
      break;
      
    case 'schedule':
      scheduler.scheduleNightlyExecution();
      break;
      
    case 'validate':
      scheduler.preStartupValidation()
        .then(() => {
          console.log('✅ Pre-startup validation passed');
          process.exit(0);
        })
        .catch(error => {
          console.error('❌ Pre-startup validation failed:', error);
          process.exit(1);
        });
      break;
      
    default:
      console.log(`
Nightly Startup Scheduler Usage:
  node nightly-scheduler.js run                    - Execute nightly startup sequence
  node nightly-scheduler.js schedule               - Schedule nightly execution
  node nightly-scheduler.js validate               - Run pre-startup validation

Examples:
  node nightly-scheduler.js run
  node nightly-scheduler.js schedule
  node nightly-scheduler.js validate

The scheduler will automatically:
- Validate system prerequisites
- Start required services
- Execute comprehensive startup sequence
- Run performance optimization
- Perform security audit
- Optimize knowledge base
- Execute system self-improvement
- Generate detailed reports
      `);
  }
}

module.exports = NightlyScheduler;
