"use client"

import React, { createContext, useContext, useState, useEffect } from 'react'

interface MuiPattern {
  id: string
  pattern_name: string
  from_agent_type: string
  to_agent_type: string
  message_type: string
  pattern_schema: any
  description: string
  usage_count: number
  created_at: string
  updated_at: string
}

interface MuiPatternsContextType {
  patterns: MuiPattern[]
  loading: boolean
  error: string | null
  fetchPatterns: () => Promise<void>
  getPatternsByType: (type: string) => MuiPattern[]
  incrementUsage: (patternId: string) => void
}

const MuiPatternsContext = createContext<MuiPatternsContextType | undefined>(undefined)

export function MuiPatternsProvider({ children }: { children: React.ReactNode }) {
  const [patterns, setPatterns] = useState<MuiPattern[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchPatterns = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch('http://localhost:54321/rest/v1/agent_communication_patterns?from_agent_type=eq.ui_designer&message_type=eq.design_pattern', {
        headers: {
          'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0',
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`Failed to fetch patterns: ${response.statusText}`)
      }

      const data = await response.json()
      setPatterns(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch patterns')
      console.error('Error fetching MUI patterns:', err)
    } finally {
      setLoading(false)
    }
  }

  const getPatternsByType = (type: string): MuiPattern[] => {
    return patterns.filter(pattern => 
      pattern.pattern_name.toLowerCase().includes(type.toLowerCase()) ||
      pattern.description.toLowerCase().includes(type.toLowerCase())
    )
  }

  const incrementUsage = async (patternId: string) => {
    try {
      const response = await fetch(`http://localhost:54321/rest/v1/agent_communication_patterns?id=eq.${patternId}`, {
        method: 'PATCH',
        headers: {
          'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          usage_count: (patterns.find(p => p.id === patternId)?.usage_count || 0) + 1
        })
      })

      if (response.ok) {
        // Update local state
        setPatterns(prev => prev.map(p => 
          p.id === patternId 
            ? { ...p, usage_count: p.usage_count + 1 }
            : p
        ))
      }
    } catch (err) {
      console.error('Error incrementing usage:', err)
    }
  }

  useEffect(() => {
    fetchPatterns()
  }, [])

  return (
    <MuiPatternsContext.Provider value={{
      patterns,
      loading,
      error,
      fetchPatterns,
      getPatternsByType,
      incrementUsage
    }}>
      {children}
    </MuiPatternsContext.Provider>
  )
}

export function useMuiPatterns() {
  const context = useContext(MuiPatternsContext)
  if (context === undefined) {
    throw new Error('useMuiPatterns must be used within a MuiPatternsProvider')
  }
  return context
}
