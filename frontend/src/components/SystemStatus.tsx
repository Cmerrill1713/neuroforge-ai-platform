import { SystemHealthResponse } from '@/types/api'

interface SystemStatusProps {
  health: SystemHealthResponse | null
}

export function SystemStatus({ health }: SystemStatusProps) {
  if (!health) {
    return (
      <div className="flex items-center space-x-2 text-sm text-muted-foreground">
        <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
        <span>Connecting...</span>
      </div>
    )
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-500'
      case 'degraded':
        return 'bg-yellow-500'
      default:
        return 'bg-red-500'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'Online'
      case 'degraded':
        return 'Degraded'
      default:
        return 'Offline'
    }
  }

  return (
    <div className="flex items-center space-x-4 text-sm">
      <div className="flex items-center space-x-2">
        <div className={`w-2 h-2 rounded-full animate-pulse ${getStatusColor(health.status)}`}></div>
        <span className="text-muted-foreground">
          System: {getStatusText(health.status)}
        </span>
      </div>

      <div className="text-xs text-muted-foreground">
        v{health.version}
      </div>

      {health.database_connected && (
        <div className="flex items-center space-x-1">
          <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
          <span className="text-xs text-muted-foreground">DB</span>
        </div>
      )}
    </div>
  )
}