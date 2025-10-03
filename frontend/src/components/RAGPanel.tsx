'use client'

import { useState, useEffect } from 'react'
import { Search, Database, Zap, TrendingUp, FileText, ExternalLink } from 'lucide-react'

interface RAGResult {
  id: string
  text: string
  score: number
  metadata: {
    title?: string
    url?: string
    source_type?: string
    domain?: string
    distance?: number
    certainty?: number
  }
}

interface RAGMetrics {
  latency_ms: number
  num_results: number
  retrieval_method: string
  cache_hit?: boolean
}

export function RAGPanel() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<RAGResult[]>([])
  const [metrics, setMetrics] = useState<RAGMetrics | null>(null)
  const [isSearching, setIsSearching] = useState(false)
  const [retrievalMethod, setRetrievalMethod] = useState<'vector' | 'hybrid'>('hybrid')
  const [topK, setTopK] = useState(5)
  
  // System metrics
  const [systemMetrics, setSystemMetrics] = useState({
    cache_hit_ratio: 0,
    avg_latency_ms: 0,
    total_queries: 0,
    weaviate_docs: 0
  })
  
  // Load metrics on mount
  useEffect(() => {
    loadSystemMetrics()
  }, [])
  
  const loadSystemMetrics = async () => {
    try {
      const { apiClient } = await import('@/lib/api')
      const metricsData = await apiClient.getRagMetrics()
      setSystemMetrics(metricsData)
    } catch (error) {
      console.error('Failed to load system metrics:', error)
    }
  }
  
  const handleSearch = async () => {
    if (!query.trim() || isSearching) return
    
    setIsSearching(true)
    
    try {
      const { apiClient } = await import('@/lib/api')
      
      const data = await apiClient.ragQuery(query, topK, retrievalMethod)
      
      setResults(data.results || [])
      setMetrics({
        latency_ms: data.latency_ms,
        num_results: data.num_results,
        retrieval_method: data.retrieval_method,
        cache_hit: data.cache_hit
      })
      
      // Reload system metrics
      await loadSystemMetrics()
      
    } catch (error) {
      console.error('RAG search failed:', error)
      setResults([])
    } finally {
      setIsSearching(false)
    }
  }
  
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Database className="w-6 h-6 text-primary" />
          RAG System
        </h2>
        <p className="text-sm text-muted-foreground mt-1">
          Hybrid retrieval: Weaviate (ANN) + Elasticsearch (BM25) + RRF + Reranking
        </p>
      </div>
      
      {/* System Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Cache Hit Ratio"
          value={`${(systemMetrics.cache_hit_ratio * 100).toFixed(1)}%`}
          icon={<Zap className="w-4 h-4" />}
          color="green"
        />
        <MetricCard
          label="Avg Latency"
          value={`${systemMetrics.avg_latency_ms}ms`}
          icon={<TrendingUp className="w-4 h-4" />}
          color="blue"
        />
        <MetricCard
          label="Total Queries"
          value={systemMetrics.total_queries.toLocaleString()}
          icon={<Search className="w-4 h-4" />}
          color="purple"
        />
        <MetricCard
          label="Documents"
          value={systemMetrics.weaviate_docs.toLocaleString()}
          icon={<FileText className="w-4 h-4" />}
          color="orange"
        />
      </div>
      
      {/* Search Interface */}
      <div className="bg-card border rounded-lg p-6">
        <div className="mb-4 flex gap-4 items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium mb-2">
              Search Query
            </label>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Enter your search query..."
              className="w-full px-4 py-2 border rounded-lg bg-background"
              disabled={isSearching}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">
              Method
            </label>
            <select
              value={retrievalMethod}
              onChange={(e) => setRetrievalMethod(e.target.value as 'vector' | 'hybrid')}
              className="px-4 py-2 border rounded-lg bg-background"
            >
              <option value="vector">Vector Only</option>
              <option value="hybrid">Hybrid (Vector + BM25)</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">
              Top K
            </label>
            <input
              type="number"
              value={topK}
              onChange={(e) => setTopK(parseInt(e.target.value))}
              min={1}
              max={20}
              className="w-20 px-3 py-2 border rounded-lg bg-background"
            />
          </div>
          
          <button
            onClick={handleSearch}
            disabled={isSearching || !query.trim()}
            className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 flex items-center gap-2"
          >
            {isSearching ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                Searching...
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                Search
              </>
            )}
          </button>
        </div>
        
        {/* Query Metrics */}
        {metrics && (
          <div className="flex items-center gap-6 text-sm text-muted-foreground p-3 bg-muted/30 rounded-md">
            <span>⏱️ {metrics.latency_ms.toFixed(0)}ms</span>
            <span>📄 {metrics.num_results} results</span>
            <span>🔍 {metrics.retrieval_method}</span>
            {metrics.cache_hit && <span className="text-green-500">⚡ Cache hit</span>}
          </div>
        )}
      </div>
      
      {/* Results */}
      <div className="space-y-3">
        {results.length > 0 ? (
          results.map((result, index) => (
            <ResultCard key={result.id} result={result} rank={index + 1} />
          ))
        ) : (
          query && !isSearching && (
            <div className="text-center text-muted-foreground py-12 bg-card border rounded-lg">
              <Search className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No results found</p>
              <p className="text-sm mt-1">Try a different query or adjust search parameters</p>
            </div>
          )
        )}
      </div>
    </div>
  )
}

function MetricCard({ label, value, icon, color }: {
  label: string
  value: string
  icon: React.ReactNode
  color: string
}) {
  const colorClasses = {
    green: 'bg-green-500/10 text-green-500',
    blue: 'bg-blue-500/10 text-blue-500',
    purple: 'bg-purple-500/10 text-purple-500',
    orange: 'bg-orange-500/10 text-orange-500'
  }
  
  return (
    <div className="bg-card border rounded-lg p-4">
      <div className="flex items-center justify-between mb-1">
        <p className="text-xs text-muted-foreground">{label}</p>
        <div className={`p-1.5 rounded ${colorClasses[color as keyof typeof colorClasses]}`}>
          {icon}
        </div>
      </div>
      <p className="text-xl font-bold">{value}</p>
    </div>
  )
}

function ResultCard({ result, rank }: { result: RAGResult; rank: number }) {
  const [isExpanded, setIsExpanded] = useState(false)
  
  return (
    <div className="bg-card border rounded-lg p-5 hover:border-primary/50 transition-colors">
      <div className="flex items-start gap-4">
        {/* Rank & Score */}
        <div className="flex-shrink-0 text-center">
          <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center mb-1">
            <span className="font-bold text-primary">{rank}</span>
          </div>
          <div className="text-xs text-muted-foreground">
            {(result.score * 100).toFixed(0)}%
          </div>
        </div>
        
        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Title */}
          {result.metadata.title && (
            <h4 className="font-semibold mb-1 flex items-center gap-2">
              {result.metadata.title}
              {result.metadata.url && (
                <a 
                  href={result.metadata.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-primary hover:text-primary/80"
                >
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </h4>
          )}
          
          {/* Metadata badges */}
          <div className="flex flex-wrap gap-2 mb-2">
            {result.metadata.source_type && (
              <span className="px-2 py-0.5 text-xs bg-blue-500/10 text-blue-500 rounded">
                {result.metadata.source_type}
              </span>
            )}
            {result.metadata.domain && (
              <span className="px-2 py-0.5 text-xs bg-purple-500/10 text-purple-500 rounded">
                {result.metadata.domain}
              </span>
            )}
            {result.metadata.certainty && (
              <span className="px-2 py-0.5 text-xs bg-green-500/10 text-green-500 rounded">
                {(result.metadata.certainty * 100).toFixed(0)}% certain
              </span>
            )}
          </div>
          
          {/* Text content */}
          <p className="text-sm text-muted-foreground">
            {isExpanded ? result.text : `${result.text.slice(0, 200)}...`}
          </p>
          
          {result.text.length > 200 && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-xs text-primary hover:text-primary/80 mt-2"
            >
              {isExpanded ? 'Show less' : 'Show more'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

