import { AgentInfo, AgentPerformanceStats } from '@/types/api'
import { apiClient } from '@/lib/api'
import { useState, useEffect, useCallback } from 'react'
import { Bot, Activity, Clock, CheckCircle, XCircle } from 'lucide-react'

interface AgentPanelProps {
}

export function AgentPanel() {
  const [agents, setAgents] = useState<AgentInfo[]>([])
  const [stats, setStats] = useState<AgentPerformanceStats | null>(null)
  const [loading, setLoading] = useState(true)

  const loadAgents = useCallback(async () => {
    try {
      setLoading(true)
      const agentsData = await apiClient.getAgents()
      setAgents(agentsData)
    } catch (error) {
      console.error('Failed to load agents:', error)
      setAgents([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadAgents()
    loadAgentStats()
  }, [loadAgents])

  const loadAgentStats = async () => {
    try {
      const statsData = await apiClient.getAgentStats()
      setStats(statsData)
    } catch (error) {
      console.error('Failed to load agent stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'inactive':
        return <Clock className="w-4 h-4 text-yellow-500" />
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />
      default:
        return <Activity className="w-4 h-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'inactive':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'error':
        return 'bg-red-100 text-red-800 border-red-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-card p-4 rounded-lg border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Agents</p>
                <p className="text-2xl font-bold">{stats.total_agents}</p>
              </div>
              <Bot className="w-8 h-8 text-primary" />
            </div>
          </div>

          <div className="bg-card p-4 rounded-lg border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Active Agents</p>
                <p className="text-2xl font-bold">{stats.active_agents}</p>
              </div>
              <Activity className="w-8 h-8 text-green-500" />
            </div>
          </div>

          <div className="bg-card p-4 rounded-lg border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Requests</p>
                <p className="text-2xl font-bold">{stats.total_requests}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-card p-4 rounded-lg border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Success Rate</p>
                <p className="text-2xl font-bold">{(stats.success_rate * 100).toFixed(1)}%</p>
              </div>
              <Clock className="w-8 h-8 text-purple-500" />
            </div>
          </div>
        </div>
      )}

      {/* Agent List */}
      <div className="bg-card rounded-lg border">
        <div className="p-6 border-b">
          <h2 className="text-lg font-semibold">Available Agents</h2>
          <p className="text-sm text-muted-foreground">
            Intelligent agents for various tasks and workflows
          </p>
        </div>

        <div className="p-6">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {agents.map((agent) => (
                <div key={agent.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                        <Bot className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <h3 className="font-medium">{agent.name}</h3>
                        <p className="text-sm text-muted-foreground">{agent.type}</p>
                      </div>
                    </div>
                    {getStatusIcon(agent.status)}
                  </div>

                  <div className="space-y-2">
                    <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(agent.status)}`}>
                      {agent.status}
                    </div>

                    <div className="text-xs text-muted-foreground">
                      Last active: {new Date(agent.lastActivity).toLocaleDateString()}
                    </div>

                    {agent.capabilities.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {agent.capabilities.slice(0, 3).map((capability) => (
                          <span
                            key={capability}
                            className="px-2 py-1 bg-muted text-muted-foreground text-xs rounded"
                          >
                            {capability}
                          </span>
                        ))}
                        {agent.capabilities.length > 3 && (
                          <span className="px-2 py-1 bg-muted text-muted-foreground text-xs rounded">
                            +{agent.capabilities.length - 3} more
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {agents.length === 0 && !loading && (
            <div className="text-center py-8 text-muted-foreground">
              <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No agents available</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}