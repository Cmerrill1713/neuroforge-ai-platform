'use client'

import { useState, useEffect } from 'react'
import { KnowledgeSearchRequest, KnowledgeSearchResponse, KnowledgeStatsResponse } from '@/types/api'
import { apiClient } from '@/lib/api'
import { Search, BookOpen, Clock, Database } from 'lucide-react'

export function KnowledgePanel() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<KnowledgeSearchResponse | null>(null)
  const [stats, setStats] = useState<KnowledgeStatsResponse | null>(null)
  const [isSearching, setIsSearching] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const statsData = await apiClient.getKnowledgeStats()
      setStats(statsData)
    } catch (error) {
      console.error('Failed to load knowledge stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim() || isSearching) return

    setIsSearching(true)
    try {
      const searchResults = await apiClient.searchKnowledge(query.trim(), {
        limit: 10
      })
      setResults(searchResults)
    } catch (error) {
      console.error('Search failed:', error)
      setResults(null)
    } finally {
      setIsSearching(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-card p-4 rounded-lg border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Documents</p>
                <p className="text-2xl font-bold">{stats.total_documents}</p>
              </div>
              <BookOpen className="w-8 h-8 text-primary" />
            </div>
          </div>

          <div className="bg-card p-4 rounded-lg border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Knowledge Chunks</p>
                <p className="text-2xl font-bold">{stats.total_chunks}</p>
              </div>
              <Database className="w-8 h-8 text-green-500" />
            </div>
          </div>

          <div className="bg-card p-4 rounded-lg border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Last Updated</p>
                <p className="text-lg font-semibold">
                  {new Date(stats.last_updated).toLocaleDateString()}
                </p>
              </div>
              <Clock className="w-8 h-8 text-blue-500" />
            </div>
          </div>
        </div>
      )}

      {/* Search Interface */}
      <div className="bg-card rounded-lg border">
        <div className="p-6 border-b">
          <h2 className="text-lg font-semibold">Knowledge Base Search</h2>
          <p className="text-sm text-muted-foreground">
            Search through the AI knowledge base for relevant information
          </p>
        </div>

        <div className="p-6">
          {/* Search Form */}
          <form onSubmit={handleSearch} className="mb-6">
            <div className="flex space-x-2">
              <div className="flex-1">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Enter your search query..."
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  disabled={isSearching}
                />
              </div>
              <button
                type="submit"
                disabled={!query.trim() || isSearching}
                className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <Search className="w-4 h-4" />
                <span>{isSearching ? 'Searching...' : 'Search'}</span>
              </button>
            </div>
          </form>

          {/* Search Results */}
          {results && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-md font-medium">
                  Found {results.total_found} results
                </h3>
                <span className="text-sm text-muted-foreground">
                  Search time: {(results.search_time * 1000).toFixed(0)}ms
                </span>
              </div>

              {results.results.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Search className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No results found for your query</p>
                  <p className="text-sm mt-2">Try different keywords or check your spelling</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {results.results.map((result, index) => (
                    <div key={index} className="border rounded-lg p-4 hover:bg-muted/50 transition-colors">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium text-sm mb-2">
                            {result.title || `Result ${index + 1}`}
                          </h4>
                          <p className="text-sm text-muted-foreground line-clamp-3">
                            {result.content || result.text || JSON.stringify(result)}
                          </p>
                          {result.score && (
                            <div className="mt-2 text-xs text-muted-foreground">
                              Relevance: {(result.score * 100).toFixed(1)}%
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Loading State */}
          {isSearching && (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mr-2"></div>
              <span className="text-muted-foreground">Searching knowledge base...</span>
            </div>
          )}

          {/* Initial State */}
          {!results && !isSearching && (
            <div className="text-center py-8 text-muted-foreground">
              <BookOpen className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>Enter a query to search the knowledge base</p>
              <p className="text-sm mt-2">
                The AI assistant can help you find relevant information from the knowledge base
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}