'use client'

import { useState, useEffect } from 'react'
import { Activity, Zap, TrendingUp, Database, BarChart3, Play, Pause, Settings } from 'lucide-react'

interface Genome {
  genome_id: string
  temperature: number
  max_tokens: number
  model_key: string
  generation: number
  fitness_score: number
}

interface EvolutionStats {
  current_generation: number
  best_score: number
  mean_score: number
  population_size: number
  status: 'idle' | 'running' | 'complete'
}

interface BanditStats {
  [genome_id: string]: {
    pulls: number
    mean_reward: number
    expected_value: number
  }
}

export function EvolutionaryOptimizerPanel() {
  const [evolutionStats, setEvolutionStats] = useState<EvolutionStats>({
    current_generation: 0,
    best_score: 0,
    mean_score: 0,
    population_size: 12,
    status: 'idle'
  })
  
  const [topGenomes, setTopGenomes] = useState<Genome[]>([])
  const [banditStats, setBanditStats] = useState<BanditStats>({})
  const [isRunning, setIsRunning] = useState(false)
  const [fitnessHistory, setFitnessHistory] = useState<Array<{gen: number, best: number, mean: number}>>([])
  
  // Configuration
  const [numGenerations, setNumGenerations] = useState(3)
  const [useMIPRO, setUseMIPRO] = useState(false)
  
  useEffect(() => {
    // Load stats on mount
    loadStats()
    
    // Poll for updates if running
    const interval = setInterval(() => {
      if (isRunning) {
        loadStats()
      }
    }, 2000)
    
    return () => clearInterval(interval)
  }, [isRunning])
  
  const loadStats = async () => {
    try {
      const { apiClient } = await import('@/lib/api')
      const stats = await apiClient.getEvolutionStats()
      setEvolutionStats(stats)
      
      // Load bandit stats
      const banditData = await apiClient.getBanditStats()
      setBanditStats(banditData)
      
    } catch (error) {
      console.error('Failed to load stats:', error)
    }
  }
  
  const startEvolution = async () => {
    setIsRunning(true)
    
    try {
      const { apiClient } = await import('@/lib/api')
      
      const result = await apiClient.startEvolution({
        num_generations: numGenerations,
        use_mipro: useMIPRO
      })
      
      setTopGenomes(result.top_genomes || [])
      setFitnessHistory(result.fitness_history || [])
      setEvolutionStats(prev => ({ ...prev, status: 'complete' }))
      
    } catch (error) {
      console.error('Evolution failed:', error)
      setEvolutionStats(prev => ({ ...prev, status: 'idle' }))
    } finally {
      setIsRunning(false)
    }
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Activity className="w-6 h-6 text-primary" />
            Evolutionary Prompt Optimizer
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Genetic algorithms + Multi-objective fitness + Thompson sampling
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={isRunning ? undefined : startEvolution}
            disabled={isRunning}
            className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors ${
              isRunning
                ? 'bg-muted text-muted-foreground cursor-not-allowed'
                : 'bg-primary text-primary-foreground hover:bg-primary/90'
            }`}
          >
            {isRunning ? (
              <>
                <Pause className="w-4 h-4 animate-pulse" />
                Running...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Start Evolution
              </>
            )}
          </button>
        </div>
      </div>
      
      {/* Configuration */}
      <div className="bg-card border rounded-lg p-4">
        <div className="flex items-center gap-2 mb-3">
          <Settings className="w-4 h-4" />
          <h3 className="font-semibold">Configuration</h3>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              Generations
            </label>
            <input
              type="number"
              value={numGenerations}
              onChange={(e) => setNumGenerations(parseInt(e.target.value))}
              min={1}
              max={20}
              className="w-full px-3 py-2 border rounded-md bg-background"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">
              Use MIPROv2
            </label>
            <label className="flex items-center gap-2 mt-2">
              <input
                type="checkbox"
                checked={useMIPRO}
                onChange={(e) => setUseMIPRO(e.target.checked)}
                className="w-4 h-4"
              />
              <span className="text-sm">Enable prompt text optimization</span>
            </label>
          </div>
        </div>
      </div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          title="Current Generation"
          value={evolutionStats.current_generation}
          icon={<TrendingUp className="w-5 h-5" />}
          color="blue"
        />
        <StatCard
          title="Best Score"
          value={evolutionStats.best_score.toFixed(4)}
          icon={<Zap className="w-5 h-5" />}
          color="green"
        />
        <StatCard
          title="Mean Score"
          value={evolutionStats.mean_score.toFixed(4)}
          icon={<BarChart3 className="w-5 h-5" />}
          color="purple"
        />
        <StatCard
          title="Population"
          value={evolutionStats.population_size}
          icon={<Database className="w-5 h-5" />}
          color="orange"
        />
      </div>
      
      {/* Fitness History Chart */}
      {fitnessHistory.length > 0 && (
        <div className="bg-card border rounded-lg p-6">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            Fitness Progress
          </h3>
          
          <div className="relative h-48">
            <FitnessChart history={fitnessHistory} />
          </div>
        </div>
      )}
      
      {/* Top Genomes */}
      <div className="bg-card border rounded-lg p-6">
        <h3 className="font-semibold mb-4 flex items-center gap-2">
          <Database className="w-4 h-4" />
          Top Genomes
        </h3>
        
        {topGenomes.length > 0 ? (
          <div className="space-y-3">
            {topGenomes.slice(0, 5).map((genome, index) => (
              <GenomeCard key={genome.genome_id} genome={genome} rank={index + 1} />
            ))}
          </div>
        ) : (
          <div className="text-center text-muted-foreground py-8">
            <Database className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>Run evolution to see top performing genomes</p>
          </div>
        )}
      </div>
      
      {/* Bandit Stats */}
      {Object.keys(banditStats).length > 0 && (
        <div className="bg-card border rounded-lg p-6">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Bandit Performance (Production)
          </h3>
          
          <div className="space-y-2">
            {Object.entries(banditStats).map(([genome_id, stats]) => (
              <div key={genome_id} className="flex items-center justify-between p-3 bg-muted/50 rounded-md">
                <div className="flex-1">
                  <p className="text-sm font-medium font-mono">{genome_id.slice(0, 12)}...</p>
                  <p className="text-xs text-muted-foreground">
                    {stats.pulls} pulls • {(stats.mean_reward * 100).toFixed(1)}% reward
                  </p>
                </div>
                
                <div className="w-32">
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary transition-all"
                      style={{ width: `${stats.expected_value * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// Helper Components

function StatCard({ title, value, icon, color }: { 
  title: string
  value: string | number
  icon: React.ReactNode
  color: string 
}) {
  const colorClasses = {
    blue: 'bg-blue-500/10 text-blue-500',
    green: 'bg-green-500/10 text-green-500',
    purple: 'bg-purple-500/10 text-purple-500',
    orange: 'bg-orange-500/10 text-orange-500'
  }
  
  return (
    <div className="bg-card border rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm text-muted-foreground">{title}</p>
        <div className={`p-2 rounded-lg ${colorClasses[color as keyof typeof colorClasses]}`}>
          {icon}
        </div>
      </div>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  )
}

function GenomeCard({ genome, rank }: { genome: Genome; rank: number }) {
  const medals = ['🥇', '🥈', '🥉']
  
  return (
    <div className="p-4 border rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{medals[rank - 1] || `#${rank}`}</span>
          <div>
            <p className="font-mono text-sm font-medium">
              {genome.genome_id.slice(0, 16)}...
            </p>
            <p className="text-xs text-muted-foreground">
              Generation {genome.generation}
            </p>
          </div>
        </div>
        
        <div className="text-right">
          <p className="text-lg font-bold text-green-500">
            {genome.fitness_score.toFixed(4)}
          </p>
          <p className="text-xs text-muted-foreground">Fitness</p>
        </div>
      </div>
      
      <div className="grid grid-cols-3 gap-3 mt-3 pt-3 border-t">
        <div>
          <p className="text-xs text-muted-foreground">Temp</p>
          <p className="text-sm font-medium">{genome.temperature}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Tokens</p>
          <p className="text-sm font-medium">{genome.max_tokens}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Model</p>
          <p className="text-sm font-medium">{genome.model_key}</p>
        </div>
      </div>
    </div>
  )
}

function FitnessChart({ history }: { history: Array<{gen: number, best: number, mean: number}> }) {
  if (history.length === 0) return null
  
  const maxScore = Math.max(...history.map(h => h.best))
  const minScore = Math.min(...history.map(h => h.mean))
  const range = maxScore - minScore
  
  return (
    <div className="relative w-full h-full">
      <svg className="w-full h-full" viewBox="0 0 600 200" preserveAspectRatio="none">
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((y) => (
          <line
            key={y}
            x1="0"
            y1={y * 200}
            x2="600"
            y2={y * 200}
            stroke="currentColor"
            strokeOpacity="0.1"
            strokeWidth="1"
          />
        ))}
        
        {/* Best score line */}
        <polyline
          points={history.map((h, i) => {
            const x = (i / (history.length - 1)) * 600
            const y = 200 - ((h.best - minScore) / range) * 200
            return `${x},${y}`
          }).join(' ')}
          fill="none"
          stroke="rgb(34, 197, 94)"
          strokeWidth="3"
        />
        
        {/* Mean score line */}
        <polyline
          points={history.map((h, i) => {
            const x = (i / (history.length - 1)) * 600
            const y = 200 - ((h.mean - minScore) / range) * 200
            return `${x},${y}`
          }).join(' ')}
          fill="none"
          stroke="rgb(147, 51, 234)"
          strokeWidth="2"
          opacity="0.7"
        />
      </svg>
      
      {/* Legend */}
      <div className="absolute bottom-2 right-2 flex gap-4 text-xs">
        <div className="flex items-center gap-1">
          <div className="w-3 h-0.5 bg-green-500"></div>
          <span>Best</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-0.5 bg-purple-500"></div>
          <span>Mean</span>
        </div>
      </div>
    </div>
  )
}

