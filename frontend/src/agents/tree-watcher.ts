/**
 * Tree Watcher Agent - Monitors file system changes and ensures code quality
 * This agent watches for file changes and triggers appropriate quality checks
 */

import { EventEmitter } from 'events'
import * as fs from 'fs'
import * as path from 'path'

interface FileChangeEvent {
  filePath: string
  changeType: 'created' | 'modified' | 'deleted'
  timestamp: Date
  content?: string
  size?: number
}

interface CodeQualityReport {
  filePath: string
  issues: CodeIssue[]
  score: number
  suggestions: string[]
  timestamp: Date
}

interface CodeIssue {
  type: 'error' | 'warning' | 'info'
  severity: 'low' | 'medium' | 'high' | 'critical'
  message: string
  line?: number
  column?: number
  rule?: string
}

interface SecurityIssue {
  type: 'vulnerability' | 'suspicious' | 'dangerous'
  severity: 'low' | 'medium' | 'high' | 'critical'
  description: string
  filePath: string
  line?: number
  suggestion: string
}

class TreeWatcherAgent extends EventEmitter {
  private watchedDirectories: Set<string> = new Set()
  private fileHashes: Map<string, string> = new Map()
  private isWatching: boolean = false
  private debounceTimers: Map<string, NodeJS.Timeout> = new Map()
  private readonly DEBOUNCE_DELAY = 1000 // 1 second

  constructor() {
    super()
    this.setupEventHandlers()
  }

  private setupEventHandlers() {
    this.on('fileChanged', this.handleFileChange.bind(this))
    this.on('fileCreated', this.handleFileCreated.bind(this))
    this.on('fileDeleted', this.handleFileDeleted.bind(this))
  }

  /**
   * Start watching directories for changes
   */
  startWatching(directories: string[]): void {
    if (this.isWatching) {
      console.log('🔍 Tree Watcher Agent: Already watching')
      return
    }

    directories.forEach(dir => {
      if (fs.existsSync(dir)) {
        this.watchedDirectories.add(dir)
        this.watchDirectory(dir)
        console.log(`🔍 Tree Watcher Agent: Started watching ${dir}`)
      } else {
        console.warn(`⚠️ Tree Watcher Agent: Directory ${dir} does not exist`)
      }
    })

    this.isWatching = true
    console.log('🔍 Tree Watcher Agent: Started monitoring file system')
  }

  /**
   * Stop watching directories
   */
  stopWatching(): void {
    this.isWatching = false
    this.debounceTimers.forEach(timer => clearTimeout(timer))
    this.debounceTimers.clear()
    this.watchedDirectories.clear()
    console.log('🔍 Tree Watcher Agent: Stopped monitoring')
  }

  private watchDirectory(directory: string): void {
    // In a real implementation, this would use fs.watch or chokidar
    // For now, we'll simulate file watching
    console.log(`🔍 Tree Watcher Agent: Monitoring ${directory}`)
    
    // Simulate file change detection
    this.scanDirectory(directory)
  }

  private scanDirectory(directory: string): void {
    try {
      const files = fs.readdirSync(directory, { withFileTypes: true })
      
      files.forEach(file => {
        const filePath = path.join(directory, file.name)
        
        if (file.isDirectory() && !file.name.startsWith('.') && file.name !== 'node_modules') {
          this.scanDirectory(filePath)
        } else if (file.isFile() && this.isCodeFile(file.name)) {
          this.checkFileHash(filePath)
        }
      })
    } catch (error) {
      console.error(`❌ Tree Watcher Agent: Error scanning ${directory}:`, error)
    }
  }

  private isCodeFile(filename: string): boolean {
    const codeExtensions = ['.ts', '.tsx', '.js', '.jsx', '.py', '.go', '.rs', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.swift', '.kt']
    return codeExtensions.some(ext => filename.endsWith(ext))
  }

  private checkFileHash(filePath: string): void {
    try {
      const stats = fs.statSync(filePath)
      const currentHash = `${stats.mtime.getTime()}-${stats.size}`
      const previousHash = this.fileHashes.get(filePath)

      if (previousHash !== currentHash) {
        this.fileHashes.set(filePath, currentHash)
        
        if (previousHash) {
          // File was modified
          this.emitFileChange(filePath, 'modified')
        } else {
          // File is new
          this.emitFileChange(filePath, 'created')
        }
      }
    } catch (error) {
      // File might have been deleted
      if (this.fileHashes.has(filePath)) {
        this.fileHashes.delete(filePath)
        this.emitFileChange(filePath, 'deleted')
      }
    }
  }

  private emitFileChange(filePath: string, changeType: FileChangeEvent['changeType']): void {
    const event: FileChangeEvent = {
      filePath,
      changeType,
      timestamp: new Date()
    }

    // Debounce rapid changes
    const existingTimer = this.debounceTimers.get(filePath)
    if (existingTimer) {
      clearTimeout(existingTimer)
    }

    const timer = setTimeout(() => {
      this.debounceTimers.delete(filePath)
      this.emit('fileChanged', event)
      
      switch (changeType) {
        case 'created':
          this.emit('fileCreated', event)
          break
        case 'modified':
          this.emit('fileModified', event)
          break
        case 'deleted':
          this.emit('fileDeleted', event)
          break
      }
    }, this.DEBOUNCE_DELAY)

    this.debounceTimers.set(filePath, timer)
  }

  private async handleFileChange(event: FileChangeEvent): Promise<void> {
    console.log(`🔍 Tree Watcher Agent: File ${event.changeType}: ${event.filePath}`)
    
    if (event.changeType === 'modified' || event.changeType === 'created') {
      await this.performQualityChecks(event.filePath)
    }
  }

  private async handleFileCreated(event: FileChangeEvent): Promise<void> {
    console.log(`🔍 Tree Watcher Agent: New file created: ${event.filePath}`)
    await this.performSecurityScan(event.filePath)
  }

  private async handleFileDeleted(event: FileChangeEvent): Promise<void> {
    console.log(`🔍 Tree Watcher Agent: File deleted: ${event.filePath}`)
    // Could trigger dependency checks, cleanup tasks, etc.
  }

  /**
   * Perform comprehensive code quality checks
   */
  private async performQualityChecks(filePath: string): Promise<CodeQualityReport> {
    console.log(`🔍 Tree Watcher Agent: Performing quality checks on ${filePath}`)
    
    try {
      const content = fs.readFileSync(filePath, 'utf-8')
      const issues: CodeIssue[] = []
      
      // Basic code quality checks
      issues.push(...this.checkCodeStyle(filePath, content))
      issues.push(...this.checkSecurityPatterns(filePath, content))
      issues.push(...this.checkPerformanceIssues(filePath, content))
      issues.push(...this.checkBestPractices(filePath, content))
      
      const score = this.calculateQualityScore(issues)
      const suggestions = this.generateSuggestions(issues)
      
      const report: CodeQualityReport = {
        filePath,
        issues,
        score,
        suggestions,
        timestamp: new Date()
      }

      console.log(`🔍 Tree Watcher Agent: Quality score for ${filePath}: ${score}/100`)
      
      if (issues.length > 0) {
        console.log(`🔍 Tree Watcher Agent: Found ${issues.length} issues in ${filePath}`)
        this.emit('qualityIssues', report)
      }

      return report
    } catch (error) {
      console.error(`❌ Tree Watcher Agent: Error checking ${filePath}:`, error)
      return {
        filePath,
        issues: [{
          type: 'error',
          severity: 'critical',
          message: `Failed to read file: ${error}`
        }],
        score: 0,
        suggestions: ['Fix file access permissions'],
        timestamp: new Date()
      }
    }
  }

  /**
   * Perform security scan on file
   */
  private async performSecurityScan(filePath: string): Promise<SecurityIssue[]> {
    console.log(`🔍 Tree Watcher Agent: Performing security scan on ${filePath}`)
    
    try {
      const content = fs.readFileSync(filePath, 'utf-8')
      const securityIssues: SecurityIssue[] = []
      
      // Check for common security vulnerabilities
      securityIssues.push(...this.checkForHardcodedSecrets(filePath, content))
      securityIssues.push(...this.checkForSQLInjection(filePath, content))
      securityIssues.push(...this.checkForXSS(filePath, content))
      securityIssues.push(...this.checkForInsecureDependencies(filePath, content))
      
      if (securityIssues.length > 0) {
        console.log(`🔍 Tree Watcher Agent: Found ${securityIssues.length} security issues in ${filePath}`)
        this.emit('securityIssues', securityIssues)
      }

      return securityIssues
    } catch (error) {
      console.error(`❌ Tree Watcher Agent: Error scanning ${filePath}:`, error)
      return []
    }
  }

  private checkCodeStyle(filePath: string, content: string): CodeIssue[] {
    const issues: CodeIssue[] = []
    const lines = content.split('\n')

    lines.forEach((line, index) => {
      // Check for very long lines
      if (line.length > 120) {
        issues.push({
          type: 'warning',
          severity: 'low',
          message: `Line ${index + 1} is too long (${line.length} characters)`,
          line: index + 1,
          rule: 'max-line-length'
        })
      }

      // Check for trailing whitespace
      if (line.endsWith(' ') || line.endsWith('\t')) {
        issues.push({
          type: 'warning',
          severity: 'low',
          message: `Line ${index + 1} has trailing whitespace`,
          line: index + 1,
          rule: 'no-trailing-whitespace'
        })
      }

      // Check for TODO comments
      if (line.toLowerCase().includes('todo') || line.toLowerCase().includes('fixme')) {
        issues.push({
          type: 'info',
          severity: 'low',
          message: `Line ${index + 1} contains TODO/FIXME comment`,
          line: index + 1,
          rule: 'no-todos'
        })
      }
    })

    return issues
  }

  private checkSecurityPatterns(filePath: string, content: string): CodeIssue[] {
    const issues: CodeIssue[] = []
    const lines = content.split('\n')

    lines.forEach((line, index) => {
      // Check for hardcoded secrets
      if (line.includes('password') && line.includes('=') && !line.includes('process.env')) {
        issues.push({
          type: 'error',
          severity: 'critical',
          message: `Line ${index + 1} may contain hardcoded password`,
          line: index + 1,
          rule: 'no-hardcoded-secrets'
        })
      }

      // Check for eval usage
      if (line.includes('eval(')) {
        issues.push({
          type: 'error',
          severity: 'high',
          message: `Line ${index + 1} uses eval() which is dangerous`,
          line: index + 1,
          rule: 'no-eval'
        })
      }

      // Check for innerHTML without sanitization
      if (line.includes('.innerHTML') && !line.includes('sanitize')) {
        issues.push({
          type: 'warning',
          severity: 'medium',
          message: `Line ${index + 1} uses innerHTML without sanitization`,
          line: index + 1,
          rule: 'no-unsafe-innerhtml'
        })
      }
    })

    return issues
  }

  private checkPerformanceIssues(filePath: string, content: string): CodeIssue[] {
    const issues: CodeIssue[] = []

    // Check for console.log in production code
    if (content.includes('console.log') && !filePath.includes('test')) {
      issues.push({
        type: 'warning',
        severity: 'low',
        message: 'File contains console.log statements that should be removed in production',
        rule: 'no-console-logs'
      })
    }

    return issues
  }

  private checkBestPractices(filePath: string, content: string): CodeIssue[] {
    const issues: CodeIssue[] = []

    // Check for proper error handling
    if (content.includes('try') && !content.includes('catch')) {
      issues.push({
        type: 'warning',
        severity: 'medium',
        message: 'File has try block without catch block',
        rule: 'proper-error-handling'
      })
    }

    return issues
  }

  private checkForHardcodedSecrets(filePath: string, content: string): SecurityIssue[] {
    const issues: SecurityIssue[] = []
    const lines = content.split('\n')

    lines.forEach((line, index) => {
      // Check for API keys, passwords, tokens
      const secretPatterns = [
        /(api[_-]?key|apikey)\s*[:=]\s*["'][^"']+["']/i,
        /(password|passwd)\s*[:=]\s*["'][^"']+["']/i,
        /(token|secret)\s*[:=]\s*["'][^"']+["']/i
      ]

      secretPatterns.forEach(pattern => {
        if (pattern.test(line)) {
          issues.push({
            type: 'vulnerability',
            severity: 'critical',
            description: `Hardcoded secret detected on line ${index + 1}`,
            filePath,
            line: index + 1,
            suggestion: 'Use environment variables or secure configuration management'
          })
        }
      })
    })

    return issues
  }

  private checkForSQLInjection(filePath: string, content: string): SecurityIssue[] {
    const issues: SecurityIssue[] = []
    
    // Check for direct SQL string concatenation
    if (content.includes('SELECT') && content.includes('+') && content.includes('WHERE')) {
      issues.push({
        type: 'vulnerability',
        severity: 'high',
        description: 'Potential SQL injection vulnerability detected',
        filePath,
        suggestion: 'Use parameterized queries or prepared statements'
      })
    }

    return issues
  }

  private checkForXSS(filePath: string, content: string): SecurityIssue[] {
    const issues: SecurityIssue[] = []
    
    // Check for unsafe HTML manipulation
    if (content.includes('innerHTML') && !content.includes('sanitize')) {
      issues.push({
        type: 'vulnerability',
        severity: 'medium',
        description: 'Potential XSS vulnerability - unsafe HTML manipulation',
        filePath,
        suggestion: 'Use textContent or sanitize HTML input'
      })
    }

    return issues
  }

  private checkForInsecureDependencies(filePath: string, content: string): SecurityIssue[] {
    const issues: SecurityIssue[] = []
    
    // Check for known vulnerable packages (simplified)
    const vulnerablePackages = ['lodash@4.17.0', 'moment@2.24.0']
    
    vulnerablePackages.forEach(pkg => {
      if (content.includes(pkg)) {
        issues.push({
          type: 'vulnerability',
          severity: 'medium',
          description: `Vulnerable dependency detected: ${pkg}`,
          filePath,
          suggestion: `Update ${pkg} to latest secure version`
        })
      }
    })

    return issues
  }

  private calculateQualityScore(issues: CodeIssue[]): number {
    let score = 100
    
    issues.forEach(issue => {
      switch (issue.severity) {
        case 'critical':
          score -= 20
          break
        case 'high':
          score -= 15
          break
        case 'medium':
          score -= 10
          break
        case 'low':
          score -= 5
          break
      }
    })

    return Math.max(0, score)
  }

  private generateSuggestions(issues: CodeIssue[]): string[] {
    const suggestions: string[] = []
    
    if (issues.some(i => i.rule === 'max-line-length')) {
      suggestions.push('Consider breaking long lines into multiple lines')
    }
    
    if (issues.some(i => i.rule === 'no-hardcoded-secrets')) {
      suggestions.push('Move secrets to environment variables')
    }
    
    if (issues.some(i => i.rule === 'no-eval')) {
      suggestions.push('Replace eval() with safer alternatives')
    }

    return suggestions
  }

  /**
   * Get current status of the tree watcher
   */
  getStatus() {
    return {
      isWatching: this.isWatching,
      watchedDirectories: Array.from(this.watchedDirectories),
      filesBeingTracked: this.fileHashes.size,
      activeDebounceTimers: this.debounceTimers.size
    }
  }
}

export const treeWatcherAgent = new TreeWatcherAgent()
export type { FileChangeEvent, CodeQualityReport, CodeIssue, SecurityIssue }
