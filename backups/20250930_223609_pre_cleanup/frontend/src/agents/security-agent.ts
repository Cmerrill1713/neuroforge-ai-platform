/**
 * Security Agent - Comprehensive security monitoring and vulnerability detection
 * This agent performs deep security analysis and threat detection
 */

import { EventEmitter } from 'events'
import * as fs from 'fs'
import * as path from 'path'

interface SecurityThreat {
  id: string
  type: 'vulnerability' | 'malware' | 'data-leak' | 'injection' | 'auth-bypass' | 'privilege-escalation'
  severity: 'low' | 'medium' | 'high' | 'critical'
  title: string
  description: string
  filePath: string
  line?: number
  cve?: string
  remediation: string
  confidence: number
  timestamp: Date
}

interface SecurityScan {
  scanId: string
  startTime: Date
  endTime?: Date
  filesScanned: number
  threatsFound: SecurityThreat[]
  riskScore: number
  status: 'running' | 'completed' | 'failed'
}

interface DependencyVulnerability {
  package: string
  version: string
  vulnerabilities: Array<{
    id: string
    severity: 'low' | 'medium' | 'high' | 'critical'
    description: string
    cve?: string
    fix?: string
  }>
}

class SecurityAgent extends EventEmitter {
  private activeScans: Map<string, SecurityScan> = new Map()
  private knownThreats: Map<string, SecurityThreat> = new Map()
  private isMonitoring: boolean = false

  // Security patterns to detect
  private readonly THREAT_PATTERNS = {
    // SQL Injection patterns
    sqlInjection: [
      /SELECT\s+.*\s+FROM\s+.*\s+WHERE\s+.*\+/i,
      /INSERT\s+INTO\s+.*\+/i,
      /UPDATE\s+.*\s+SET\s+.*\+/i,
      /DELETE\s+FROM\s+.*\+/i,
      /\$\{.*\}\s*\+\s*['"]/i,
      /\$\{.*\}\s*\+\s*`/i
    ],
    
    // XSS patterns
    xss: [
      /\.innerHTML\s*=\s*[^;]+(?!.*sanitize)/i,
      /document\.write\s*\(/i,
      /eval\s*\(/i,
      /setTimeout\s*\(\s*['"]/i,
      /setInterval\s*\(\s*['"]/i
    ],
    
    // Command injection patterns
    commandInjection: [
      /exec\s*\(/i,
      /spawn\s*\(/i,
      /system\s*\(/i,
      /shell_exec\s*\(/i,
      /\$\{.*\}/i
    ],
    
    // Authentication bypass patterns
    authBypass: [
      /bypass.*auth/i,
      /skip.*validation/i,
      /admin.*true/i,
      /role.*admin/i,
      /privilege.*escalation/i
    ],
    
    // Data leak patterns
    dataLeak: [
      /console\.log\s*\(.*password/i,
      /console\.log\s*\(.*secret/i,
      /console\.log\s*\(.*token/i,
      /console\.log\s*\(.*key/i,
      /alert\s*\(.*password/i
    ],
    
    // Hardcoded secrets
    hardcodedSecrets: [
      /(?:password|passwd|pwd)\s*[:=]\s*['"][^'"]{3,}['"]/i,
      /(?:api[_-]?key|apikey)\s*[:=]\s*['"][^'"]{8,}['"]/i,
      /(?:token|secret|private[_-]?key)\s*[:=]\s*['"][^'"]{8,}['"]/i,
      /(?:aws[_-]?access[_-]?key|aws[_-]?secret)\s*[:=]\s*['"][^'"]{8,}['"]/i,
      /(?:google[_-]?api[_-]?key|firebase[_-]?config)\s*[:=]\s*['"][^'"]{8,}['"]/i
    ]
  }

  constructor() {
    super()
    this.setupEventHandlers()
  }

  private setupEventHandlers() {
    this.on('threatDetected', this.handleThreatDetected.bind(this))
    this.on('scanCompleted', this.handleScanCompleted.bind(this))
  }

  /**
   * Start security monitoring
   */
  startMonitoring(directories: string[]): void {
    if (this.isMonitoring) {
      console.log('🔒 Security Agent: Already monitoring')
      return
    }

    this.isMonitoring = true
    console.log('🔒 Security Agent: Started security monitoring')
    
    // Perform initial comprehensive scan
    this.performComprehensiveScan(directories)
  }

  /**
   * Stop security monitoring
   */
  stopMonitoring(): void {
    this.isMonitoring = false
    console.log('🔒 Security Agent: Stopped security monitoring')
  }

  /**
   * Perform comprehensive security scan
   */
  async performComprehensiveScan(directories: string[]): Promise<string> {
    const scanId = `scan_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    const scan: SecurityScan = {
      scanId,
      startTime: new Date(),
      filesScanned: 0,
      threatsFound: [],
      riskScore: 0,
      status: 'running'
    }

    this.activeScans.set(scanId, scan)
    console.log(`🔒 Security Agent: Started comprehensive scan ${scanId}`)

    try {
      for (const directory of directories) {
        if (fs.existsSync(directory)) {
          await this.scanDirectory(directory, scan)
        }
      }

      // Check for dependency vulnerabilities
      await this.checkDependencyVulnerabilities(scan)

      // Calculate final risk score
      scan.riskScore = this.calculateRiskScore(scan.threatsFound)
      scan.endTime = new Date()
      scan.status = 'completed'

      console.log(`🔒 Security Agent: Scan ${scanId} completed - ${scan.threatsFound.length} threats found, risk score: ${scan.riskScore}`)
      
      this.emit('scanCompleted', scan)
      return scanId
    } catch (error) {
      scan.status = 'failed'
      scan.endTime = new Date()
      console.error(`❌ Security Agent: Scan ${scanId} failed:`, error)
      throw error
    }
  }

  private async scanDirectory(directory: string, scan: SecurityScan): Promise<void> {
    try {
      const files = fs.readdirSync(directory, { withFileTypes: true })
      
      for (const file of files) {
        const filePath = path.join(directory, file.name)
        
        if (file.isDirectory() && !file.name.startsWith('.') && file.name !== 'node_modules') {
          await this.scanDirectory(filePath, scan)
        } else if (file.isFile() && this.isScannableFile(file.name)) {
          await this.scanFile(filePath, scan)
        }
      }
    } catch (error) {
      console.error(`❌ Security Agent: Error scanning ${directory}:`, error)
    }
  }

  private isScannableFile(filename: string): boolean {
    const scannableExtensions = ['.ts', '.tsx', '.js', '.jsx', '.py', '.go', '.rs', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.swift', '.kt', '.json', '.yaml', '.yml', '.env']
    return scannableExtensions.some(ext => filename.endsWith(ext))
  }

  private async scanFile(filePath: string, scan: SecurityScan): Promise<void> {
    try {
      const content = fs.readFileSync(filePath, 'utf-8')
      scan.filesScanned++

      // Scan for different types of threats
      const threats = [
        ...this.scanForSQLInjection(filePath, content),
        ...this.scanForXSS(filePath, content),
        ...this.scanForCommandInjection(filePath, content),
        ...this.scanForAuthBypass(filePath, content),
        ...this.scanForDataLeaks(filePath, content),
        ...this.scanForHardcodedSecrets(filePath, content),
        ...this.scanForCryptographicIssues(filePath, content),
        ...this.scanForAccessControlIssues(filePath, content)
      ]

      scan.threatsFound.push(...threats)

      // Emit individual threats
      threats.forEach(threat => {
        this.emit('threatDetected', threat)
      })

    } catch (error) {
      console.error(`❌ Security Agent: Error scanning ${filePath}:`, error)
    }
  }

  private scanForSQLInjection(filePath: string, content: string): SecurityThreat[] {
    const threats: SecurityThreat[] = []
    const lines = content.split('\n')

    lines.forEach((line, index) => {
      this.THREAT_PATTERNS.sqlInjection.forEach(pattern => {
        if (pattern.test(line)) {
          threats.push({
            id: `sql_injection_${Date.now()}_${index}`,
            type: 'injection',
            severity: 'high',
            title: 'Potential SQL Injection Vulnerability',
            description: `SQL query construction detected on line ${index + 1} that may be vulnerable to injection attacks`,
            filePath,
            line: index + 1,
            cve: 'CWE-89',
            remediation: 'Use parameterized queries or prepared statements instead of string concatenation',
            confidence: 0.85,
            timestamp: new Date()
          })
        }
      })
    })

    return threats
  }

  private scanForXSS(filePath: string, content: string): SecurityThreat[] {
    const threats: SecurityThreat[] = []
    const lines = content.split('\n')

    lines.forEach((line, index) => {
      this.THREAT_PATTERNS.xss.forEach(pattern => {
        if (pattern.test(line)) {
          threats.push({
            id: `xss_${Date.now()}_${index}`,
            type: 'vulnerability',
            severity: 'medium',
            title: 'Potential Cross-Site Scripting (XSS) Vulnerability',
            description: `Unsafe HTML manipulation detected on line ${index + 1}`,
            filePath,
            line: index + 1,
            cve: 'CWE-79',
            remediation: 'Sanitize user input and use safe DOM manipulation methods',
            confidence: 0.75,
            timestamp: new Date()
          })
        }
      })
    })

    return threats
  }

  private scanForCommandInjection(filePath: string, content: string): SecurityThreat[] {
    const threats: SecurityThreat[] = []
    const lines = content.split('\n')

    lines.forEach((line, index) => {
      this.THREAT_PATTERNS.commandInjection.forEach(pattern => {
        if (pattern.test(line)) {
          threats.push({
            id: `command_injection_${Date.now()}_${index}`,
            type: 'injection',
            severity: 'critical',
            title: 'Potential Command Injection Vulnerability',
            description: `Unsafe command execution detected on line ${index + 1}`,
            filePath,
            line: index + 1,
            cve: 'CWE-78',
            remediation: 'Validate and sanitize all user input before executing commands',
            confidence: 0.90,
            timestamp: new Date()
          })
        }
      })
    })

    return threats
  }

  private scanForAuthBypass(filePath: string, content: string): SecurityThreat[] {
    const threats: SecurityThreat[] = []
    const lines = content.split('\n')

    lines.forEach((line, index) => {
      this.THREAT_PATTERNS.authBypass.forEach(pattern => {
        if (pattern.test(line)) {
          threats.push({
            id: `auth_bypass_${Date.now()}_${index}`,
            type: 'auth-bypass',
            severity: 'critical',
            title: 'Potential Authentication Bypass',
            description: `Authentication bypass pattern detected on line ${index + 1}`,
            filePath,
            line: index + 1,
            cve: 'CWE-287',
            remediation: 'Implement proper authentication and authorization checks',
            confidence: 0.70,
            timestamp: new Date()
          })
        }
      })
    })

    return threats
  }

  private scanForDataLeaks(filePath: string, content: string): SecurityThreat[] {
    const threats: SecurityThreat[] = []
    const lines = content.split('\n')

    lines.forEach((line, index) => {
      this.THREAT_PATTERNS.dataLeak.forEach(pattern => {
        if (pattern.test(line)) {
          threats.push({
            id: `data_leak_${Date.now()}_${index}`,
            type: 'data-leak',
            severity: 'medium',
            title: 'Potential Data Leakage',
            description: `Sensitive data logging detected on line ${index + 1}`,
            filePath,
            line: index + 1,
            remediation: 'Remove or sanitize sensitive data from logs',
            confidence: 0.80,
            timestamp: new Date()
          })
        }
      })
    })

    return threats
  }

  private scanForHardcodedSecrets(filePath: string, content: string): SecurityThreat[] {
    const threats: SecurityThreat[] = []
    const lines = content.split('\n')

    lines.forEach((line, index) => {
      this.THREAT_PATTERNS.hardcodedSecrets.forEach(pattern => {
        if (pattern.test(line)) {
          threats.push({
            id: `hardcoded_secret_${Date.now()}_${index}`,
            type: 'vulnerability',
            severity: 'high',
            title: 'Hardcoded Secret Detected',
            description: `Hardcoded secret detected on line ${index + 1}`,
            filePath,
            line: index + 1,
            cve: 'CWE-798',
            remediation: 'Move secrets to environment variables or secure configuration management',
            confidence: 0.95,
            timestamp: new Date()
          })
        }
      })
    })

    return threats
  }

  private scanForCryptographicIssues(filePath: string, content: string): SecurityThreat[] {
    const threats: SecurityThreat[] = []
    const lines = content.split('\n')

    lines.forEach((line, index) => {
      // Check for weak encryption algorithms
      if (line.includes('MD5') || line.includes('SHA1')) {
        threats.push({
          id: `weak_crypto_${Date.now()}_${index}`,
          type: 'vulnerability',
          severity: 'medium',
          title: 'Weak Cryptographic Algorithm',
          description: `Weak hash algorithm detected on line ${index + 1}`,
          filePath,
          line: index + 1,
          cve: 'CWE-327',
          remediation: 'Use stronger cryptographic algorithms like SHA-256 or bcrypt',
          confidence: 0.85,
          timestamp: new Date()
        })
      }

      // Check for hardcoded encryption keys
      if (line.includes('encrypt') && line.includes('key') && line.includes('=')) {
        threats.push({
          id: `hardcoded_key_${Date.now()}_${index}`,
          type: 'vulnerability',
          severity: 'high',
          title: 'Hardcoded Encryption Key',
          description: `Hardcoded encryption key detected on line ${index + 1}`,
          filePath,
          line: index + 1,
          cve: 'CWE-798',
          remediation: 'Use secure key management and avoid hardcoded encryption keys',
          confidence: 0.90,
          timestamp: new Date()
        })
      }
    })

    return threats
  }

  private scanForAccessControlIssues(filePath: string, content: string): SecurityThreat[] {
    const threats: SecurityThreat[] = []
    const lines = content.split('\n')

    lines.forEach((line, index) => {
      // Check for missing authentication checks
      if ((line.includes('admin') || line.includes('delete') || line.includes('update')) && 
          !line.includes('auth') && !line.includes('permission') && !line.includes('role')) {
        threats.push({
          id: `missing_auth_${Date.now()}_${index}`,
          type: 'auth-bypass',
          severity: 'medium',
          title: 'Missing Authentication Check',
          description: `Admin operation without authentication check on line ${index + 1}`,
          filePath,
          line: index + 1,
          cve: 'CWE-306',
          remediation: 'Implement proper authentication and authorization checks',
          confidence: 0.60,
          timestamp: new Date()
        })
      }
    })

    return threats
  }

  private async checkDependencyVulnerabilities(scan: SecurityScan): Promise<void> {
    try {
      // Check package.json for known vulnerable dependencies
      const packageJsonPath = path.join(process.cwd(), 'package.json')
      if (fs.existsSync(packageJsonPath)) {
        const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'))
        const dependencies = { ...packageJson.dependencies, ...packageJson.devDependencies }
        
        // Known vulnerable packages (simplified list)
        const vulnerablePackages = {
          'lodash': { versions: ['4.17.0'], cve: 'CVE-2019-10744', severity: 'medium' },
          'moment': { versions: ['2.24.0'], cve: 'CVE-2019-10744', severity: 'low' },
          'axios': { versions: ['0.18.0'], cve: 'CVE-2019-10744', severity: 'medium' }
        }

        Object.entries(dependencies).forEach(([pkg, version]) => {
          if (vulnerablePackages[pkg as keyof typeof vulnerablePackages]) {
            const vuln = vulnerablePackages[pkg as keyof typeof vulnerablePackages]
            if (vuln.versions.includes(version as string)) {
              scan.threatsFound.push({
                id: `dep_vuln_${Date.now()}_${pkg}`,
                type: 'vulnerability',
                severity: vuln.severity as any,
                title: `Vulnerable Dependency: ${pkg}`,
                description: `Package ${pkg} version ${version} has known vulnerability ${vuln.cve}`,
                filePath: packageJsonPath,
                cve: vuln.cve,
                remediation: `Update ${pkg} to latest secure version`,
                confidence: 0.95,
                timestamp: new Date()
              })
            }
          }
        })
      }
    } catch (error) {
      console.error('❌ Security Agent: Error checking dependencies:', error)
    }
  }

  private calculateRiskScore(threats: SecurityThreat[]): number {
    let riskScore = 0
    
    threats.forEach(threat => {
      switch (threat.severity) {
        case 'critical':
          riskScore += 10
          break
        case 'high':
          riskScore += 7
          break
        case 'medium':
          riskScore += 4
          break
        case 'low':
          riskScore += 1
          break
      }
    })

    return Math.min(100, riskScore)
  }

  private handleThreatDetected(threat: SecurityThreat): void {
    this.knownThreats.set(threat.id, threat)
    console.log(`🚨 Security Agent: Threat detected - ${threat.title} (${threat.severity}) in ${threat.filePath}`)
  }

  private handleScanCompleted(scan: SecurityScan): void {
    this.activeScans.delete(scan.scanId)
    console.log(`🔒 Security Agent: Scan completed - Risk Score: ${scan.riskScore}/100`)
    
    if (scan.riskScore > 50) {
      console.log(`🚨 Security Agent: HIGH RISK detected! Please review and fix security issues.`)
    }
  }

  /**
   * Get current security status
   */
  getSecurityStatus() {
    return {
      isMonitoring: this.isMonitoring,
      activeScans: this.activeScans.size,
      knownThreats: this.knownThreats.size,
      highRiskThreats: Array.from(this.knownThreats.values()).filter(t => t.severity === 'critical' || t.severity === 'high').length
    }
  }

  /**
   * Get all known threats
   */
  getAllThreats(): SecurityThreat[] {
    return Array.from(this.knownThreats.values())
  }

  /**
   * Get threats by severity
   */
  getThreatsBySeverity(severity: SecurityThreat['severity']): SecurityThreat[] {
    return Array.from(this.knownThreats.values()).filter(t => t.severity === severity)
  }
}

export const securityAgent = new SecurityAgent()
export type { SecurityThreat, SecurityScan, DependencyVulnerability }
