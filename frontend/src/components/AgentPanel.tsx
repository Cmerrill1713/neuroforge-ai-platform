import { AgentInfo, AgentPerformanceStats } from '@/types/api'
import { apiClient } from '@/lib/api'
import { useState, useEffect, useCallback } from 'react'
import { Bot, Activity, Clock, CheckCircle, XCircle, Sparkles } from 'lucide-react'

interface AgentPanelProps {
}

export function AgentPanel() {
  const [agents, setAgents] = useState<AgentInfo[]>([])
  const [stats, setStats] = useState<AgentPerformanceStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  
  // Load selected agent from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('selectedAgent')
    if (saved) {
      setSelectedAgent(saved)
    } else if (agents.length > 0) {
      // Default to LFM2 if available, otherwise qwen2.5:14b, otherwise first agent
      const defaultAgent = agents.find(a => a.id === 'lfm2') || agents.find(a => a.id === 'qwen2.5:14b') || agents[0]
      setSelectedAgent(defaultAgent.id)
      localStorage.setItem('selectedAgent', defaultAgent.id)
    }
  }, [agents])
  
  const selectAgent = (agentId: string) => {
    setSelectedAgent(agentId)
    localStorage.setItem('selectedAgent', agentId)
  }

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

      {/* Currently Selected Agent */}
      {selectedAgent && (
        <div className="bg-gradient-to-r from-primary/10 to-primary/5 border border-primary/20 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-5 h-5 text-primary" />
            <h3 className="font-semibold text-primary">Currently Active Agent</h3>
          </div>
          <p className="text-sm text-muted-foreground">
            {agents.find(a => a.id === selectedAgent)?.name || 'None'} - 
            This agent will be used for your chat interactions
          </p>
        </div>
      )}

      {/* Agent List */}
      <div className="bg-card rounded-lg border">
        <div className="p-6 border-b">
          <h2 className="text-lg font-semibold">Available Agents</h2>
          <p className="text-sm text-muted-foreground">
            Click &quot;Select Agent&quot; to use a model for chat interactions
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
                <div 
                  key={agent.id} 
                  className={`border rounded-lg p-4 transition-all ${
                    selectedAgent === agent.id 
                      ? 'ring-2 ring-primary shadow-lg bg-primary/5' 
                      : 'hover:shadow-md hover:bg-muted/50'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        selectedAgent === agent.id ? 'bg-primary text-primary-foreground' : 'bg-primary/10'
                      }`}>
                        <Bot className={`w-5 h-5 ${selectedAgent === agent.id ? 'text-primary-foreground' : 'text-primary'}`} />
                      </div>
                      <div>
                        <h3 className="font-medium">{agent.name}</h3>
                        <p className="text-sm text-muted-foreground">{agent.type}</p>
                      </div>
                    </div>
                    {selectedAgent === agent.id ? (
                      <div className="flex items-center gap-1 text-xs font-medium text-primary">
                        <CheckCircle className="w-4 h-4" />
                        Active
                      </div>
                    ) : (
                      getStatusIcon(agent.status)
                    )}
                  </div>

                  <div className="space-y-3">
                    <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(agent.status)}`}>
                      {agent.status}
                    </div>

                    <div className="text-xs text-muted-foreground">
                      Last active: {new Date(agent.lastActivity).toLocaleDateString()}
                    </div>

                    {agent.capabilities.length > 0 && (
                      <div className="flex flex-wrap gap-1">
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
                    
                    {/* Select Button */}
                    <button
                      onClick={() => selectAgent(agent.id)}
                      className={`w-full mt-3 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                        selectedAgent === agent.id
                          ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                          : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                      }`}
                    >
                      {selectedAgent === agent.id ? '✓ Selected' : 'Select Agent'}
                    </button>
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