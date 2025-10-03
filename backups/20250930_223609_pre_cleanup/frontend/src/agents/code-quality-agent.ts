/**
 * Code Quality Agent - Ensures clean, maintainable, and high-quality code
 * This agent performs comprehensive code quality analysis and provides suggestions
 */

import { EventEmitter } from 'events'
import * as fs from 'fs'
import * as path from 'path'

interface QualityMetric {
  name: string
  value: number
  maxValue: number
  score: number
  description: string
}

interface QualityReport {
  filePath: string
  overallScore: number
  metrics: QualityMetric[]
  issues: QualityIssue[]
  suggestions: string[]
  timestamp: Date
}

interface QualityIssue {
  type: 'complexity' | 'maintainability' | 'readability' | 'performance' | 'best-practice'
  severity: 'low' | 'medium' | 'high'
  message: string
  line?: number
  column?: number
  suggestion: string
  rule: string
}

interface CodeComplexity {
  cyclomaticComplexity: number
  cognitiveComplexity: number
  nestingDepth: number
  functionLength: number
}

class CodeQualityAgent extends EventEmitter {
  private qualityReports: Map<string, QualityReport> = new Map()
  private isAnalyzing: boolean = false

  constructor() {
    super()
    this.setupEventHandlers()
  }

  private setupEventHandlers() {
    this.on('qualityIssue', this.handleQualityIssue.bind(this))
    this.on('analysisCompleted', this.handleAnalysisCompleted.bind(this))
  }

  /**
   * Start code quality analysis
   */
  startAnalysis(directories: string[]): void {
    if (this.isAnalyzing) {
      console.log('📊 Code Quality Agent: Already analyzing')
      return
    }

    this.isAnalyzing = true
    console.log('📊 Code Quality Agent: Started code quality analysis')
    
    this.performQualityAnalysis(directories)
  }

  /**
   * Stop code quality analysis
   */
  stopAnalysis(): void {
    this.isAnalyzing = false
    console.log('📊 Code Quality Agent: Stopped analysis')
  }

  /**
   * Perform comprehensive quality analysis
   */
  async performQualityAnalysis(directories: string[]): Promise<void> {
    console.log('📊 Code Quality Agent: Performing comprehensive quality analysis')
    
    try {
      for (const directory of directories) {
        if (fs.existsSync(directory)) {
          await this.analyzeDirectory(directory)
        }
      }
      
      this.emit('analysisCompleted', { reportsCount: this.qualityReports.size })
    } catch (error) {
      console.error('❌ Code Quality Agent: Analysis failed:', error)
    }
  }

  private async analyzeDirectory(directory: string): Promise<void> {
    try {
      const files = fs.readdirSync(directory, { withFileTypes: true })
      
      for (const file of files) {
        const filePath = path.join(directory, file.name)
        
        if (file.isDirectory() && !file.name.startsWith('.') && file.name !== 'node_modules') {
          await this.analyzeDirectory(filePath)
        } else if (file.isFile() && this.isCodeFile(file.name)) {
          await this.analyzeFile(filePath)
        }
      }
    } catch (error) {
      console.error(`❌ Code Quality Agent: Error analyzing ${directory}:`, error)
    }
  }

  private isCodeFile(filename: string): boolean {
    const codeExtensions = ['.ts', '.tsx', '.js', '.jsx', '.py', '.go', '.rs', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.swift', '.kt']
    return codeExtensions.some(ext => filename.endsWith(ext))
  }

  private async analyzeFile(filePath: string): Promise<void> {
    try {
      const content = fs.readFileSync(filePath, 'utf-8')
      
      const report: QualityReport = {
        filePath,
        overallScore: 0,
        metrics: [],
        issues: [],
        suggestions: [],
        timestamp: new Date()
      }

      // Analyze different quality aspects
      report.metrics.push(...this.analyzeComplexity(filePath, content))
      report.metrics.push(...this.analyzeMaintainability(filePath, content))
      report.metrics.push(...this.analyzeReadability(filePath, content))
      report.metrics.push(...this.analyzePerformance(filePath, content))
      report.metrics.push(...this.analyzeBestPractices(filePath, content))

      // Calculate overall score
      report.overallScore = this.calculateOverallScore(report.metrics)
      
      // Generate suggestions
      report.suggestions = this.generateSuggestions(report.issues)

      this.qualityReports.set(filePath, report)
      
      console.log(`📊 Code Quality Agent: ${filePath} - Score: ${report.overallScore}/100`)
      
      // Emit issues for monitoring
      report.issues.forEach(issue => {
        this.emit('qualityIssue', { filePath, issue })
      })

    } catch (error) {
      console.error(`❌ Code Quality Agent: Error analyzing ${filePath}:`, error)
    }
  }

  private analyzeComplexity(filePath: string, content: string): QualityMetric[] {
    const metrics: QualityMetric[] = []
    const complexity = this.calculateComplexity(content)
    
    // Cyclomatic Complexity
    const complexityScore = Math.max(0, 100 - (complexity.cyclomaticComplexity * 5))
    metrics.push({
      name: 'Cyclomatic Complexity',
      value: complexity.cyclomaticComplexity,
      maxValue: 10,
      score: complexityScore,
      description: 'Measures the number of linearly independent paths through code'
    })

    // Cognitive Complexity
    const cognitiveScore = Math.max(0, 100 - (complexity.cognitiveComplexity * 3))
    metrics.push({
      name: 'Cognitive Complexity',
      value: complexity.cognitiveComplexity,
      maxValue: 15,
      score: cognitiveScore,
      description: 'Measures how difficult code is to understand'
    })

    // Nesting Depth
    const nestingScore = Math.max(0, 100 - (complexity.nestingDepth * 10))
    metrics.push({
      name: 'Nesting Depth',
      value: complexity.nestingDepth,
      maxValue: 4,
      score: nestingScore,
      description: 'Measures the maximum nesting level in the code'
    })

    return metrics
  }

  private analyzeMaintainability(filePath: string, content: string): QualityMetric[] {
    const metrics: QualityMetric[] = []
    const lines = content.split('\n')
    
    // Function Length
    const functionLengths = this.getFunctionLengths(content)
    const avgFunctionLength = functionLengths.reduce((a, b) => a + b, 0) / functionLengths.length || 0
    const functionLengthScore = Math.max(0, 100 - (avgFunctionLength * 2))
    
    metrics.push({
      name: 'Average Function Length',
      value: avgFunctionLength,
      maxValue: 20,
      score: functionLengthScore,
      description: 'Measures the average length of functions'
    })

    // Code Duplication
    const duplicationScore = this.calculateDuplicationScore(content)
    metrics.push({
      name: 'Code Duplication',
      value: (1 - duplicationScore) * 100,
      maxValue: 100,
      score: duplicationScore * 100,
      description: 'Measures the percentage of duplicated code'
    })

    // Comment Coverage
    const commentCoverage = this.calculateCommentCoverage(content)
    metrics.push({
      name: 'Comment Coverage',
      value: commentCoverage,
      maxValue: 100,
      score: commentCoverage,
      description: 'Measures the percentage of code covered by comments'
    })

    return metrics
  }

  private analyzeReadability(filePath: string, content: string): QualityMetric[] {
    const metrics: QualityMetric[] = []
    const lines = content.split('\n')
    
    // Line Length
    const longLines = lines.filter(line => line.length > 100).length
    const lineLengthScore = Math.max(0, 100 - (longLines / lines.length) * 100)
    
    metrics.push({
      name: 'Line Length',
      value: longLines,
      maxValue: lines.length * 0.1,
      score: lineLengthScore,
      description: 'Measures the number of lines exceeding recommended length'
    })

    // Naming Quality
    const namingScore = this.analyzeNamingQuality(content)
    metrics.push({
      name: 'Naming Quality',
      value: namingScore,
      maxValue: 100,
      score: namingScore,
      description: 'Measures the quality of variable and function names'
    })

    return metrics
  }

  private analyzePerformance(filePath: string, content: string): QualityMetric[] {
    const metrics: QualityMetric[] = []
    
    // Performance Anti-patterns
    const antiPatterns = this.detectPerformanceAntiPatterns(content)
    const performanceScore = Math.max(0, 100 - (antiPatterns * 10))
    
    metrics.push({
      name: 'Performance Anti-patterns',
      value: antiPatterns,
      maxValue: 5,
      score: performanceScore,
      description: 'Measures the number of performance anti-patterns detected'
    })

    return metrics
  }

  private analyzeBestPractices(filePath: string, content: string): QualityMetric[] {
    const metrics: QualityMetric[] = []
    
    // Error Handling
    const errorHandlingScore = this.analyzeErrorHandling(content)
    metrics.push({
      name: 'Error Handling',
      value: errorHandlingScore,
      maxValue: 100,
      score: errorHandlingScore,
      description: 'Measures the quality of error handling'
    })

    // Type Safety (for TypeScript files)
    if (filePath.endsWith('.ts') || filePath.endsWith('.tsx')) {
      const typeSafetyScore = this.analyzeTypeSafety(content)
      metrics.push({
        name: 'Type Safety',
        value: typeSafetyScore,
        maxValue: 100,
        score: typeSafetyScore,
        description: 'Measures the use of TypeScript types'
      })
    }

    return metrics
  }

  private calculateComplexity(content: string): CodeComplexity {
    const lines = content.split('\n')
    let cyclomaticComplexity = 1 // Base complexity
    let cognitiveComplexity = 0
    let nestingDepth = 0
    let maxNestingDepth = 0
    let currentFunctionLength = 0
    let maxFunctionLength = 0

    lines.forEach(line => {
      const trimmedLine = line.trim()
      
      // Cyclomatic complexity keywords
      if (/if|else|while|for|switch|case|catch|\?\s*:/.test(trimmedLine)) {
        cyclomaticComplexity++
      }

      // Cognitive complexity
      if (/if|else if|while|for|switch/.test(trimmedLine)) {
        cognitiveComplexity += 1 + nestingDepth
        nestingDepth++
      } else if (/\}|\)/.test(trimmedLine)) {
        nestingDepth = Math.max(0, nestingDepth - 1)
      }

      maxNestingDepth = Math.max(maxNestingDepth, nestingDepth)

      // Function length tracking
      if (trimmedLine.includes('function') || trimmedLine.includes('=>') || trimmedLine.includes('class')) {
        if (currentFunctionLength > maxFunctionLength) {
          maxFunctionLength = currentFunctionLength
        }
        currentFunctionLength = 0
      } else {
        currentFunctionLength++
      }
    })

    return {
      cyclomaticComplexity,
      cognitiveComplexity,
      nestingDepth: maxNestingDepth,
      functionLength: maxFunctionLength
    }
  }

  private getFunctionLengths(content: string): number[] {
    const functions: number[] = []
    const lines = content.split('\n')
    let currentLength = 0
    let inFunction = false

    lines.forEach(line => {
      const trimmedLine = line.trim()
      
      if (trimmedLine.includes('function') || trimmedLine.includes('=>')) {
        if (inFunction) {
          functions.push(currentLength)
        }
        inFunction = true
        currentLength = 0
      } else if (inFunction) {
        currentLength++
        if (trimmedLine.includes('}') && !trimmedLine.includes('{')) {
          functions.push(currentLength)
          inFunction = false
          currentLength = 0
        }
      }
    })

    return functions
  }

  private calculateDuplicationScore(content: string): number {
    const lines = content.split('\n').filter(line => line.trim().length > 0)
    const lineCount = lines.length
    const uniqueLines = new Set(lines.map(line => line.trim())).size
    
    return uniqueLines / lineCount
  }

  private calculateCommentCoverage(content: string): number {
    const lines = content.split('\n')
    const commentLines = lines.filter(line => 
      line.trim().startsWith('//') || 
      line.trim().startsWith('/*') || 
      line.trim().startsWith('*') ||
      line.trim().startsWith('#')
    ).length
    
    return (commentLines / lines.length) * 100
  }

  private analyzeNamingQuality(content: string): number {
    // Extract variable and function names
    const variableNames = content.match(/(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)/g) || []
    const functionNames = content.match(/function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)/g) || []
    
    const allNames = [...variableNames, ...functionNames]
    let qualityScore = 100
    
    allNames.forEach(name => {
      const cleanName = name.replace(/(?:const|let|var|function)\s+/, '')
      
      // Check for descriptive names
      if (cleanName.length < 3) qualityScore -= 5
      if (/^[a-z]/.test(cleanName) && !cleanName.includes('_') && !cleanName.includes('$')) {
        // Good camelCase
      } else {
        qualityScore -= 2
      }
      
      // Check for common bad names
      if (['temp', 'tmp', 'data', 'value', 'item', 'obj', 'arr'].includes(cleanName.toLowerCase())) {
        qualityScore -= 10
      }
    })
    
    return Math.max(0, qualityScore)
  }

  private detectPerformanceAntiPatterns(content: string): number {
    let antiPatterns = 0
    
    // Check for common performance anti-patterns
    if (content.includes('document.getElementById') && content.includes('for')) {
      antiPatterns++ // DOM queries in loops
    }
    
    if (content.includes('eval(')) {
      antiPatterns++ // eval usage
    }
    
    if (content.includes('innerHTML') && !content.includes('sanitize')) {
      antiPatterns++ // unsafe innerHTML
    }
    
    if (content.match(/for\s*\([^)]*\.length[^)]*\)/)) {
      antiPatterns++ // length in loop condition
    }
    
    return antiPatterns
  }

  private analyzeErrorHandling(content: string): number {
    let score = 100
    
    // Check for try-catch blocks
    const tryBlocks = (content.match(/try\s*{/g) || []).length
    const catchBlocks = (content.match(/catch\s*\(/g) || []).length
    
    if (tryBlocks > 0 && tryBlocks !== catchBlocks) {
      score -= 20 // Unmatched try-catch
    }
    
    // Check for proper error handling
    if (content.includes('throw') && !content.includes('catch')) {
      score -= 15 // Throwing without catching
    }
    
    return Math.max(0, score)
  }

  private analyzeTypeSafety(content: string): number {
    let score = 100
    
    // Check for any types
    const anyTypes = (content.match(/:\s*any/g) || []).length
    score -= anyTypes * 5
    
    // Check for proper type annotations
    const functions = (content.match(/function\s+[^(]*\(/g) || []).length
    const typedFunctions = (content.match(/function\s+[^(]*\([^)]*:\s*[^)]+/g) || []).length
    
    if (functions > 0) {
      const typeCoverage = (typedFunctions / functions) * 100
      score = Math.min(score, typeCoverage)
    }
    
    return Math.max(0, score)
  }

  private calculateOverallScore(metrics: QualityMetric[]): number {
    if (metrics.length === 0) return 0
    
    const totalScore = metrics.reduce((sum, metric) => sum + metric.score, 0)
    return Math.round(totalScore / metrics.length)
  }

  private generateSuggestions(issues: QualityIssue[]): string[] {
    const suggestions: string[] = []
    
    const highSeverityIssues = issues.filter(i => i.severity === 'high')
    const mediumSeverityIssues = issues.filter(i => i.severity === 'medium')
    
    if (highSeverityIssues.length > 0) {
      suggestions.push('Address high-severity quality issues immediately')
    }
    
    if (mediumSeverityIssues.length > 0) {
      suggestions.push('Consider addressing medium-severity quality issues')
    }
    
    if (issues.some(i => i.type === 'complexity')) {
      suggestions.push('Refactor complex functions to improve maintainability')
    }
    
    if (issues.some(i => i.type === 'performance')) {
      suggestions.push('Optimize performance-critical code sections')
    }
    
    return suggestions
  }

  private handleQualityIssue(data: { filePath: string; issue: QualityIssue }): void {
    console.log(`📊 Code Quality Agent: ${data.issue.type} issue in ${data.filePath} - ${data.issue.message}`)
  }

  private handleAnalysisCompleted(data: { reportsCount: number }): void {
    console.log(`📊 Code Quality Agent: Analysis completed - ${data.reportsCount} files analyzed`)
  }

  /**
   * Get quality report for a specific file
   */
  getQualityReport(filePath: string): QualityReport | undefined {
    return this.qualityReports.get(filePath)
  }

  /**
   * Get all quality reports
   */
  getAllQualityReports(): QualityReport[] {
    return Array.from(this.qualityReports.values())
  }

  /**
   * Get average quality score across all files
   */
  getAverageQualityScore(): number {
    const reports = this.getAllQualityReports()
    if (reports.length === 0) return 0
    
    const totalScore = reports.reduce((sum, report) => sum + report.overallScore, 0)
    return Math.round(totalScore / reports.length)
  }
}

export const codeQualityAgent = new CodeQualityAgent()
export type { QualityMetric, QualityReport, QualityIssue, CodeComplexity }
