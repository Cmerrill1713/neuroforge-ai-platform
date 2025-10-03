'use client'

import { useState, useEffect } from 'react'
import { ChatInterface } from '@/components/ChatInterface'
import { AgentPanel } from '@/components/AgentPanel'
import { KnowledgePanel } from '@/components/KnowledgePanel'
import { SystemStatus } from '@/components/SystemStatus'
import { EvolutionaryOptimizerPanel } from '@/components/EvolutionaryOptimizerPanel'
import { RAGPanel } from '@/components/RAGPanel'
import { apiClient } from '@/lib/api'
import { SystemHealthResponse } from '@/types/api'

type Tab = 'chat' | 'agents' | 'knowledge' | 'evolution' | 'rag'

export default function Home() {
  const [activeTab, setActiveTab] = useState<Tab>('chat')
  const [systemHealth, setSystemHealth] = useState<SystemHealthResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadInitialData()
  }, [])

  const loadInitialData = async () => {
    try {
      const healthData = await apiClient.getHealth()
      setSystemHealth(healthData)
    } catch (error) {
      console.error('Failed to load initial data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-foreground">
              🤖 AI Assistant Platform
            </h1>
            <SystemStatus health={systemHealth} />
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="border-b bg-muted/50">
        <div className="container mx-auto px-4">
          <div className="flex space-x-8 overflow-x-auto">
            {[
              { id: 'chat' as Tab, label: 'Chat', icon: '✨' },
              { id: 'agents' as Tab, label: 'Agents', icon: '🧠' },
              { id: 'knowledge' as Tab, label: 'Knowledge', icon: '📚' },
              { id: 'evolution' as Tab, label: 'Evolution', icon: '🧬' },
              { id: 'rag' as Tab, label: 'RAG Search', icon: '🔍' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-primary text-primary'
                    : 'border-transparent text-muted-foreground hover:text-foreground'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {activeTab === 'chat' && <ChatInterface />}
        {activeTab === 'agents' && <AgentPanel />}
        {activeTab === 'knowledge' && <KnowledgePanel />}
        {activeTab === 'evolution' && <EvolutionaryOptimizerPanel />}
        {activeTab === 'rag' && <RAGPanel />}
      </main>
    </div>
  )
}
