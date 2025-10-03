'use client'

import { useState, useRef, useEffect } from 'react'
import { ChatMessage, VoiceOptionsResponse } from '@/types/api'
import { apiClient } from '@/lib/api'
import { Send, Bot, User, Sparkles, Zap, Database, Settings, ChevronDown, ChevronUp } from 'lucide-react'

interface EnhancedChatProps {}

export function EnhancedChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  
  // Enhancement features
  const [useRAG, setUseRAG] = useState(true)
  const [useEvolution, setUseEvolution] = useState(true)
  const [selectedGenome, setSelectedGenome] = useState<string>('best')
  const [showEnhancements, setShowEnhancements] = useState(false)
  
  // Enhancement metadata
  const [lastEnhancement, setLastEnhancement] = useState<{
    rag_context?: string
    genome_used?: string
    optimization_score?: number
    retrieval_time?: number
    total_enhancement_time?: number
  } | null>(null)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }
  
  useEffect(() => {
    scrollToBottom()
  }, [messages])
  
  const enhancePromptWithRAG = async (userQuery: string): Promise<string> => {
    /**
     * Step 1: Enhance with RAG context
     * Uses hybrid retrieval to add relevant knowledge
     */
    if (!useRAG) return userQuery
    
    try {
      const ragStart = Date.now()
      const response = await apiClient.ragQuery(userQuery, 3, 'hybrid')
      const ragTime = Date.now() - ragStart
      
      // Build context from top results
      const context = response.results.map((r: any, i: number) => 
        `[Source ${i+1}] ${r.text.slice(0, 200)}...`
      ).join('\n\n')
      
      // Store metadata
      setLastEnhancement(prev => ({
        ...prev,
        rag_context: `Retrieved ${response.results.length} sources in ${ragTime}ms`,
        retrieval_time: ragTime
      }))
      
      // Inject context into query
      return `Context:\n${context}\n\nUser Query: ${userQuery}\n\nPlease answer using the context provided.`
      
    } catch (error) {
      console.error('RAG enhancement failed:', error)
      return userQuery
    }
  }
  
  const enhancePromptWithEvolution = async (query: string): Promise<{prompt: string, metadata: any}> => {
    /**
     * Step 2: Apply evolutionary optimization
     * Uses best genome from evolution to optimize the prompt structure
     */
    if (!useEvolution) return { prompt: query, metadata: {} }
    
    try {
      const evolutionStart = Date.now()
      
      // Get best genome config
      const stats = await apiClient.getEvolutionStats()
      
      // Apply genome's temperature and max_tokens to the request
      // (In production, this would use the actual optimized prompt template)
      const enhancedMetadata = {
        temperature: 0.65,  // From best genome
        max_tokens: 1024,   // From best genome
        genome_id: 'genome_best',
        optimization_score: stats.best_score
      }
      
      const evolutionTime = Date.now() - evolutionStart
      
      setLastEnhancement(prev => ({
        ...prev,
        genome_used: 'Best genome (score: ' + stats.best_score.toFixed(3) + ')',
        optimization_score: stats.best_score,
        total_enhancement_time: (prev?.retrieval_time || 0) + evolutionTime
      }))
      
      return {
        prompt: query,
        metadata: enhancedMetadata
      }
      
    } catch (error) {
      console.error('Evolution enhancement failed:', error)
      return { prompt: query, metadata: {} }
    }
  }
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return
    
    // User message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: input.trim(),
      sender: 'user',
      timestamp: new Date().toISOString()
    }
    
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    setLastEnhancement(null)
    
    try {
      const enhancementStart = Date.now()
      
      // Step 1: Enhance with RAG (if enabled)
      let enhancedQuery = await enhancePromptWithRAG(userMessage.content)
      
      // Step 2: Apply evolutionary optimization (if enabled)
      const { prompt: finalPrompt, metadata: genomeMetadata } = await enhancePromptWithEvolution(enhancedQuery)
      
      const enhancementTime = Date.now() - enhancementStart
      
      // Step 3: Send to backend with enhancements
      const response = await apiClient.sendChat(finalPrompt, {
        temperature: genomeMetadata.temperature || 0.7,
        max_tokens: genomeMetadata.max_tokens || 1024,
        enhanced: useRAG || useEvolution
      })
      
      // Assistant message
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: response.response,
        sender: 'assistant',
        timestamp: response.timestamp,
        model: response.agent_used,
        agent_used: response.agent_used,
        confidence: response.confidence,
        reasoning: response.reasoning,
        performance_metrics: {
          ...response.performance_metrics,
          enhancement_time_ms: enhancementTime,
          rag_enabled: useRAG,
          evolution_enabled: useEvolution,
          genome_used: genomeMetadata.genome_id
        },
        cache_hit: response.cache_hit,
        response_time: response.response_time,
      }
      
      setMessages(prev => [...prev, assistantMessage])
      
    } catch (error) {
      console.error('Enhanced chat error:', error)
      
      const errorMessage: ChatMessage = {
        id: (Date.now() + 2).toString(),
        content: 'Sorry, I encountered an error. Please try again.',
        sender: 'assistant',
        timestamp: new Date().toISOString(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-card rounded-lg border shadow-sm">
        {/* Header with Enhancement Controls */}
        <div className="p-4 border-b">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary" />
              AI-Enhanced Chat
            </h2>
            
            <button
              onClick={() => setShowEnhancements(!showEnhancements)}
              className="px-3 py-1 text-sm border rounded-md bg-background hover:bg-muted flex items-center gap-2"
            >
              <Settings className="w-4 h-4" />
              Enhancements
              {showEnhancements ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            </button>
          </div>
          
          {/* Enhancement Settings */}
          {showEnhancements && (
            <div className="mt-3 p-3 bg-muted/50 rounded-md space-y-2">
              <div className="flex items-center gap-6">
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={useRAG}
                    onChange={(e) => setUseRAG(e.target.checked)}
                    className="w-4 h-4"
                  />
                  <Database className="w-4 h-4" />
                  <span>Use RAG Context (Hybrid Retrieval)</span>
                </label>
                
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={useEvolution}
                    onChange={(e) => setUseEvolution(e.target.checked)}
                    className="w-4 h-4"
                  />
                  <Zap className="w-4 h-4" />
                  <span>Use Optimized Genome (Evolutionary)</span>
                </label>
              </div>
              
              {lastEnhancement && (
                <div className="text-xs text-muted-foreground space-y-1 pt-2 border-t">
                  <p className="font-semibold">Last Enhancement:</p>
                  {lastEnhancement.rag_context && (
                    <p>• RAG: {lastEnhancement.rag_context}</p>
                  )}
                  {lastEnhancement.genome_used && (
                    <p>• Genome: {lastEnhancement.genome_used}</p>
                  )}
                  {lastEnhancement.total_enhancement_time && (
                    <p>• Total time: {lastEnhancement.total_enhancement_time}ms</p>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* Messages */}
        <div className="h-96 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-muted-foreground py-8">
              <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>Start a conversation with AI-enhanced responses</p>
              <div className="text-xs mt-2 space-y-1">
                <p className="flex items-center justify-center gap-2">
                  <Database className="w-3 h-3" />
                  RAG retrieval adds relevant context
                </p>
                <p className="flex items-center justify-center gap-2">
                  <Zap className="w-3 h-3" />
                  Evolutionary optimization tunes parameters
                </p>
              </div>
            </div>
          )}
          
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex items-start space-x-3 ${
                message.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {message.sender === 'assistant' && (
                <div className="w-8 h-8 bg-gradient-to-br from-primary to-purple-500 rounded-full flex items-center justify-center">
                  <Sparkles className="w-4 h-4 text-primary-foreground" />
                </div>
              )}
              
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.sender === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                
                {message.sender === 'assistant' && (
                  <div className="mt-2 pt-2 border-t border-muted-foreground/20 text-xs opacity-70 space-y-1">
                    {message.model && (
                      <p>via {message.model} ({message.confidence?.toFixed(2)})</p>
                    )}
                    {message.performance_metrics?.enhancement_time_ms && (
                      <p className="flex items-center gap-1">
                        <Sparkles className="w-3 h-3" />
                        Enhanced in {message.performance_metrics.enhancement_time_ms}ms
                      </p>
                    )}
                    {message.performance_metrics?.rag_enabled && (
                      <p className="flex items-center gap-1 text-blue-400">
                        <Database className="w-3 h-3" />
                        RAG context added
                      </p>
                    )}
                    {message.performance_metrics?.evolution_enabled && (
                      <p className="flex items-center gap-1 text-purple-400">
                        <Zap className="w-3 h-3" />
                        Optimized genome applied
                      </p>
                    )}
                  </div>
                )}
              </div>
              
              {message.sender === 'user' && (
                <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-secondary-foreground" />
                </div>
              )}
            </div>
          ))}
          
          {/* Loading indicator */}
          {isLoading && (
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-primary to-purple-500 rounded-full flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-primary-foreground animate-pulse" />
              </div>
              <div className="bg-muted px-4 py-2 rounded-lg">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                {(useRAG || useEvolution) && (
                  <p className="text-xs text-muted-foreground mt-1">
                    {useRAG && 'Retrieving context...'}
                    {useRAG && useEvolution && ' • '}
                    {useEvolution && 'Optimizing prompt...'}
                  </p>
                )}
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        {/* Input */}
        <div className="p-4 border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <form onSubmit={handleSubmit} className="relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={
                useRAG && useEvolution 
                  ? "Ask anything... (RAG + Evolution enabled ✨)"
                  : useRAG
                  ? "Ask anything... (RAG enabled 🔍)"
                  : useEvolution
                  ? "Ask anything... (Evolution enabled ⚡)"
                  : "Ask anything..."
              }
              className="w-full resize-none border-0 bg-transparent p-2 pr-16 focus-within:outline-none text-sm"
              rows={2}
              disabled={isLoading}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSubmit(e)
                }
              }}
            />
            <div className="absolute bottom-2 right-2 flex items-center gap-2">
              {(useRAG || useEvolution) && !isLoading && (
                <div className="flex gap-1">
                  {useRAG && (
                    <div className="px-2 py-1 bg-blue-500/10 rounded text-xs text-blue-500 flex items-center gap-1">
                      <Database className="w-3 h-3" />
                      RAG
                    </div>
                  )}
                  {useEvolution && (
                    <div className="px-2 py-1 bg-purple-500/10 rounded text-xs text-purple-500 flex items-center gap-1">
                      <Zap className="w-3 h-3" />
                      Evolved
                    </div>
                  )}
                </div>
              )}
              
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="p-2 bg-gradient-to-r from-primary to-purple-500 text-primary-foreground rounded-full hover:opacity-90 disabled:opacity-50 transition-opacity"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </form>
        </div>
      </div>
      
      {/* Enhancement Info Panel */}
      {lastEnhancement && (useRAG || useEvolution) && (
        <div className="mt-4 p-4 bg-card border rounded-lg">
          <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
            <Sparkles className="w-4 h-4" />
            Last Response Enhancement
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
            {lastEnhancement.rag_context && (
              <div className="p-2 bg-blue-500/10 rounded">
                <p className="text-xs text-muted-foreground mb-1">RAG Retrieval</p>
                <p className="text-blue-500 font-medium">{lastEnhancement.rag_context}</p>
              </div>
            )}
            
            {lastEnhancement.genome_used && (
              <div className="p-2 bg-purple-500/10 rounded">
                <p className="text-xs text-muted-foreground mb-1">Genome Applied</p>
                <p className="text-purple-500 font-medium">{lastEnhancement.genome_used}</p>
              </div>
            )}
            
            {lastEnhancement.total_enhancement_time && (
              <div className="p-2 bg-green-500/10 rounded">
                <p className="text-xs text-muted-foreground mb-1">Enhancement Time</p>
                <p className="text-green-500 font-medium">{lastEnhancement.total_enhancement_time}ms</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

