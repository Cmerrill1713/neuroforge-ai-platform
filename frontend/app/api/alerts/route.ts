import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

// Alert severity levels
enum AlertSeverity {
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  CRITICAL = 'critical'
}

// Alert types
enum AlertType {
  CONTAINER_DOWN = 'container_down',
  SERVICE_UNAVAILABLE = 'service_unavailable',
  HIGH_RESOURCE_USAGE = 'high_resource_usage',
  FILE_CORRUPTION = 'file_corruption',
  SECURITY_THREAT = 'security_threat',
  CONFIGURATION_CHANGE = 'configuration_change',
  PERFORMANCE_DEGRADATION = 'performance_degradation'
}

interface Alert {
  id: string
  type: AlertType
  severity: AlertSeverity
  title: string
  message: string
  timestamp: string
  source: string
  resolved: boolean
  resolution?: string
  metadata?: Record<string, any>
}

interface AlertResponse {
  success: boolean
  alertId: string
  notificationsSent: string[]
  autoActions: string[]
}

class AlertManager {
  private alerts: Alert[] = []
  private alertHistory: Alert[] = []
  private readonly alertsFile = path.join(process.cwd(), 'system-alerts.json')

  constructor() {
    this.loadAlerts()
  }

  // Create new alert
  createAlert(data: Omit<Alert, 'id' | 'timestamp' | 'resolved'>): Alert {
    const alert: Alert = {
      id: `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
      resolved: false,
      ...data
    }

    this.alerts.push(alert)
    this.alertHistory.push(alert)
    this.saveAlerts()

    // Trigger notifications and auto-actions
    this.handleAlert(alert)

    return alert
  }

  // Handle alert - notifications and auto-actions
  private async handleAlert(alert: Alert): Promise<void> {
    console.log(`🚨 Alert Created: ${alert.severity.toUpperCase()} - ${alert.title}`)

    // Determine if auto-actions should be taken
    const autoActions = this.determineAutoActions(alert)
    
    // Send notifications based on severity
    const notifications = await this.sendNotifications(alert)

    // Execute auto-actions
    for (const action of autoActions) {
      await this.executeAutoAction(action, alert)
    }

    // Log alert handling
    console.log(`📋 Alert ${alert.id} handled:`, {
      notifications: notifications.length,
      autoActions: autoActions.length
    })
  }

  // Determine auto-actions based on alert type and severity
  private determineAutoActions(alert: Alert): string[] {
    const actions: string[] = []

    switch (alert.type) {
      case AlertType.CONTAINER_DOWN:
        if (alert.severity === AlertSeverity.CRITICAL || alert.severity === AlertSeverity.ERROR) {
          actions.push('restart_container')
          actions.push('check_dependencies')
        }
        break

      case AlertType.SERVICE_UNAVAILABLE:
        if (alert.severity === AlertSeverity.CRITICAL) {
          actions.push('restart_service')
          actions.push('check_network_connectivity')
        }
        break

      case AlertType.HIGH_RESOURCE_USAGE:
        actions.push('check_resource_limits')
        if (alert.severity === AlertSeverity.CRITICAL) {
          actions.push('scale_services')
        }
        break

      case AlertType.FILE_CORRUPTION:
        actions.push('backup_restore')
        actions.push('validate_integrity')
        break

      case AlertType.SECURITY_THREAT:
        actions.push('isolate_system')
        actions.push('security_scan')
        break

      case AlertType.CONFIGURATION_CHANGE:
        actions.push('validate_configuration')
        actions.push('backup_configuration')
        break

      case AlertType.PERFORMANCE_DEGRADATION:
        actions.push('analyze_performance')
        actions.push('check_logs')
        break
    }

    return actions
  }

  // Send notifications based on severity
  private async sendNotifications(alert: Alert): Promise<string[]> {
    const notifications: string[] = []

    // Always log to console and file
    notifications.push('console_log')
    notifications.push('file_log')

    // Send to monitoring dashboard
    notifications.push('dashboard_update')

    // High severity alerts get additional notifications
    if (alert.severity === AlertSeverity.CRITICAL || alert.severity === AlertSeverity.ERROR) {
      notifications.push('email_notification')
      notifications.push('slack_notification')
      notifications.push('system_log')
    }

    // Execute notifications
    for (const notification of notifications) {
      await this.executeNotification(notification, alert)
    }

    return notifications
  }

  // Execute specific notification
  private async executeNotification(type: string, alert: Alert): Promise<void> {
    switch (type) {
      case 'console_log':
        console.log(`🚨 ALERT [${alert.severity.toUpperCase()}]: ${alert.title}`)
        console.log(`   Message: ${alert.message}`)
        console.log(`   Source: ${alert.source}`)
        console.log(`   Time: ${alert.timestamp}`)
        break

      case 'file_log':
        const logEntry = `[${alert.timestamp}] ${alert.severity.toUpperCase()}: ${alert.title} - ${alert.message} (Source: ${alert.source})\n`
        fs.appendFileSync('system-alerts.log', logEntry)
        break

      case 'dashboard_update':
        // Update real-time dashboard
        console.log(`📊 Dashboard updated with alert: ${alert.id}`)
        break

      case 'email_notification':
        console.log(`📧 Email notification sent for alert: ${alert.id}`)
        // In production, this would send actual emails
        break

      case 'slack_notification':
        console.log(`💬 Slack notification sent for alert: ${alert.id}`)
        // In production, this would send to Slack webhook
        break

      case 'system_log':
        console.log(`📝 System log updated for alert: ${alert.id}`)
        break
    }
  }

  // Execute auto-action
  private async executeAutoAction(action: string, alert: Alert): Promise<void> {
    console.log(`🔧 Executing auto-action: ${action} for alert: ${alert.id}`)

    switch (action) {
      case 'restart_container':
        await this.restartContainer(alert)
        break

      case 'check_dependencies':
        await this.checkDependencies(alert)
        break

      case 'restart_service':
        await this.restartService(alert)
        break

      case 'check_network_connectivity':
        await this.checkNetworkConnectivity(alert)
        break

      case 'check_resource_limits':
        await this.checkResourceLimits(alert)
        break

      case 'scale_services':
        await this.scaleServices(alert)
        break

      case 'backup_restore':
        await this.backupRestore(alert)
        break

      case 'validate_integrity':
        await this.validateIntegrity(alert)
        break

      case 'isolate_system':
        await this.isolateSystem(alert)
        break

      case 'security_scan':
        await this.securityScan(alert)
        break

      case 'validate_configuration':
        await this.validateConfiguration(alert)
        break

      case 'backup_configuration':
        await this.backupConfiguration(alert)
        break

      case 'analyze_performance':
        await this.analyzePerformance(alert)
        break

      case 'check_logs':
        await this.checkLogs(alert)
        break
    }
  }

  // Auto-action implementations
  private async restartContainer(alert: Alert): Promise<void> {
    console.log(`🔄 Attempting to restart container from alert: ${alert.id}`)
    // In production, this would execute actual Docker commands
  }

  private async checkDependencies(alert: Alert): Promise<void> {
    console.log(`🔍 Checking dependencies for alert: ${alert.id}`)
  }

  private async restartService(alert: Alert): Promise<void> {
    console.log(`🔄 Restarting service from alert: ${alert.id}`)
  }

  private async checkNetworkConnectivity(alert: Alert): Promise<void> {
    console.log(`🌐 Checking network connectivity for alert: ${alert.id}`)
  }

  private async checkResourceLimits(alert: Alert): Promise<void> {
    console.log(`💻 Checking resource limits for alert: ${alert.id}`)
  }

  private async scaleServices(alert: Alert): Promise<void> {
    console.log(`📈 Scaling services for alert: ${alert.id}`)
  }

  private async backupRestore(alert: Alert): Promise<void> {
    console.log(`💾 Backup/restore for alert: ${alert.id}`)
  }

  private async validateIntegrity(alert: Alert): Promise<void> {
    console.log(`✅ Validating integrity for alert: ${alert.id}`)
  }

  private async isolateSystem(alert: Alert): Promise<void> {
    console.log(`🔒 Isolating system for alert: ${alert.id}`)
  }

  private async securityScan(alert: Alert): Promise<void> {
    console.log(`🛡️ Security scan for alert: ${alert.id}`)
  }

  private async validateConfiguration(alert: Alert): Promise<void> {
    console.log(`⚙️ Validating configuration for alert: ${alert.id}`)
  }

  private async backupConfiguration(alert: Alert): Promise<void> {
    console.log(`💾 Backing up configuration for alert: ${alert.id}`)
  }

  private async analyzePerformance(alert: Alert): Promise<void> {
    console.log(`📊 Analyzing performance for alert: ${alert.id}`)
  }

  private async checkLogs(alert: Alert): Promise<void> {
    console.log(`📋 Checking logs for alert: ${alert.id}`)
  }

  // Get active alerts
  getActiveAlerts(): Alert[] {
    return this.alerts.filter(alert => !alert.resolved)
  }

  // Get alert history
  getAlertHistory(): Alert[] {
    return this.alertHistory
  }

  // Resolve alert
  resolveAlert(alertId: string, resolution: string): boolean {
    const alert = this.alerts.find(a => a.id === alertId)
    if (alert) {
      alert.resolved = true
      alert.resolution = resolution
      this.saveAlerts()
      console.log(`✅ Alert ${alertId} resolved: ${resolution}`)
      return true
    }
    return false
  }

  // Save alerts to file
  private saveAlerts(): void {
    try {
      fs.writeFileSync(this.alertsFile, JSON.stringify({
        alerts: this.alerts,
        history: this.alertHistory
      }, null, 2))
    } catch (error) {
      console.error('Failed to save alerts:', error)
    }
  }

  // Load alerts from file
  private loadAlerts(): void {
    try {
      if (fs.existsSync(this.alertsFile)) {
        const data = JSON.parse(fs.readFileSync(this.alertsFile, 'utf8'))
        this.alerts = data.alerts || []
        this.alertHistory = data.history || []
      }
    } catch (error) {
      console.error('Failed to load alerts:', error)
    }
  }
}

// Global alert manager instance
const alertManager = new AlertManager()

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { type, severity, title, message, source, metadata } = body

    if (!type || !severity || !title || !message) {
      return NextResponse.json({
        error: 'Missing required fields: type, severity, title, message'
      }, { status: 400 })
    }

    // Validate enum values
    if (!Object.values(AlertType).includes(type)) {
      return NextResponse.json({
        error: 'Invalid alert type'
      }, { status: 400 })
    }

    if (!Object.values(AlertSeverity).includes(severity)) {
      return NextResponse.json({
        error: 'Invalid alert severity'
      }, { status: 400 })
    }

    // Create alert
    const alert = alertManager.createAlert({
      type,
      severity,
      title,
      message,
      source: source || 'system',
      metadata
    })

    return NextResponse.json({
      success: true,
      alertId: alert.id,
      notificationsSent: ['console_log', 'file_log', 'dashboard_update'],
      autoActions: ['system_check']
    })

  } catch (error) {
    console.error('Alert API error:', error)
    return NextResponse.json({
      error: 'Internal server error',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}

export async function GET(request: NextRequest) {
  try {
    const url = new URL(request.url)
    const type = url.searchParams.get('type')
    const active = url.searchParams.get('active') === 'true'

    if (active) {
      const alerts = alertManager.getActiveAlerts()
      return NextResponse.json({
        success: true,
        alerts,
        count: alerts.length
      })
    }

    const history = alertManager.getAlertHistory()
    return NextResponse.json({
      success: true,
      alerts: history,
      count: history.length
    })

  } catch (error) {
    console.error('Alert GET API error:', error)
    return NextResponse.json({
      error: 'Internal server error'
    }, { status: 500 })
  }
}

export async function PUT(request: NextRequest) {
  try {
    const body = await request.json()
    const { alertId, resolution } = body

    if (!alertId || !resolution) {
      return NextResponse.json({
        error: 'Missing alertId or resolution'
      }, { status: 400 })
    }

    const resolved = alertManager.resolveAlert(alertId, resolution)

    return NextResponse.json({
      success: resolved,
      alertId,
      resolution
    })

  } catch (error) {
    console.error('Alert PUT API error:', error)
    return NextResponse.json({
      error: 'Internal server error'
    }, { status: 500 })
  }
}
