'use client'

import { useState, useCallback, useRef } from 'react'

interface ReasoningStep {
  id: string
  level: number
  type: 'observation' | 'analysis' | 'hypothesis' | 'evaluation' | 'conclusion' | 'action'
  content: string
  confidence: number
  evidence: string[]
  dependencies: string[]
  alternatives: string[]
  timestamp: Date
  status: 'pending' | 'active' | 'completed' | 'failed'
}

interface DecisionNode {
  id: string
  question: string
  options: DecisionOption[]
  criteria: DecisionCriteria[]
  weight: number
  parent?: string
  children: string[]
  reasoning: string
  confidence: number
}

interface DecisionOption {
  id: string
  label: string
  description: string
  pros: string[]
  cons: string[]
  probability: number
  impact: 'low' | 'medium' | 'high'
  cost: number
  timeRequired: number
}

interface DecisionCriteria {
  id: string
  name: string
  weight: number
  description: string
  measurement: string
}

interface ReasoningChain {
  id: string
  problem: string
  steps: ReasoningStep[]
  decisions: DecisionNode[]
  conclusion: string
  confidence: number
  alternatives: string[]
  metadata: {
    domain: string
    complexity: 'low' | 'medium' | 'high'
    timeSpent: number
    resourcesUsed: string[]
  }
}

interface HRMConfig {
  maxDepth: number
  confidenceThreshold: number
  enableChainOfThought: boolean
  enableMultiStepPlanning: boolean
  enableDecisionTrees: boolean
  enableAlternativeExploration: boolean
  reasoningDomains: string[]
}

interface UseHRMReturn {
  // State
  reasoningChains: ReasoningChain[]
  currentChain: ReasoningChain | null
  isReasoning: boolean
  reasoningProgress: number
  config: HRMConfig
  
  // Actions
  startReasoning: (problem: string) => Promise<void>
  addReasoningStep: (step: Omit<ReasoningStep, 'id' | 'timestamp'>) => void
  addDecisionNode: (decision: Omit<DecisionNode, 'id'>) => void
  updateConfig: (newConfig: Partial<HRMConfig>) => void
  getReasoningChain: (id: string) => ReasoningChain | null
  getActiveReasoning: () => ReasoningChain | null
  
  // Analysis
  analyzeProblem: (problem: string) => Promise<ReasoningChain>
  generateAlternatives: (problem: string) => Promise<string[]>
  evaluateDecision: (decision: DecisionNode) => Promise<DecisionOption | null>
  
  // Utilities
  clearReasoningHistory: () => void
  exportReasoningChain: (id: string) => string
  importReasoningChain: (data: string) => ReasoningChain | null
}

export function useHRM(initialConfig?: Partial<HRMConfig>): UseHRMReturn {
  const [reasoningChains, setReasoningChains] = useState<ReasoningChain[]>([])
  const [currentChain, setCurrentChain] = useState<ReasoningChain | null>(null)
  const [isReasoning, setIsReasoning] = useState(false)
  const [reasoningProgress, setReasoningProgress] = useState(0)
  const [config, setConfig] = useState<HRMConfig>({
    maxDepth: 5,
    confidenceThreshold: 0.7,
    enableChainOfThought: true,
    enableMultiStepPlanning: true,
    enableDecisionTrees: true,
    enableAlternativeExploration: true,
    reasoningDomains: ['general', 'technical', 'business', 'personal', 'creative'],
    ...initialConfig
  })
  
  const reasoningRef = useRef<AbortController | null>(null)

  const startReasoning = useCallback(async (problem: string): Promise<void> => {
    if (isReasoning) {
      console.warn('Reasoning already in progress')
      return
    }

    setIsReasoning(true)
    setReasoningProgress(0)
    
    // Cancel any existing reasoning
    if (reasoningRef.current) {
      reasoningRef.current.abort()
    }
    
    reasoningRef.current = new AbortController()
    
    const newChain: ReasoningChain = {
      id: Date.now().toString(),
      problem,
      steps: [],
      decisions: [],
      conclusion: '',
      confidence: 0,
      alternatives: [],
      metadata: {
        domain: 'general',
        complexity: 'medium',
        timeSpent: 0,
        resourcesUsed: []
      }
    }
    
    setCurrentChain(newChain)
    
    try {
      await simulateReasoningProcess(newChain, reasoningRef.current.signal)
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        console.error('Reasoning process failed:', error)
      }
    } finally {
      setIsReasoning(false)
      setReasoningProgress(100)
      reasoningRef.current = null
    }
  }, [isReasoning, config])

  const simulateReasoningProcess = async (chain: ReasoningChain, signal: AbortSignal) => {
    const steps = [
      { type: 'observation', content: 'Analyzing the problem statement...', level: 1 },
      { type: 'analysis', content: 'Breaking down into components...', level: 2 },
      { type: 'hypothesis', content: 'Generating potential solutions...', level: 3 },
      { type: 'evaluation', content: 'Evaluating alternatives...', level: 4 },
      { type: 'conclusion', content: 'Reaching final conclusion...', level: 5 }
    ]
    
    for (let i = 0; i < steps.length; i++) {
      if (signal.aborted) throw new Error('AbortError')
      
      const step = steps[i]
      const progress = ((i + 1) / steps.length) * 100
      
      const reasoningStep: ReasoningStep = {
        id: `${chain.id}-${i + 1}`,
        level: step.level,
        type: step.type as any,
        content: step.content,
        confidence: 0.8 - (i * 0.1),
        evidence: [`Step ${i + 1} evidence`],
        dependencies: i > 0 ? [`${chain.id}-${i}`] : [],
        alternatives: [`Alternative ${i + 1}`],
        timestamp: new Date(),
        status: 'active'
      }
      
      chain.steps.push(reasoningStep)
      setReasoningProgress(progress)
      
      await new Promise(resolve => setTimeout(resolve, 1000))
    }
    
    chain.conclusion = 'Based on hierarchical analysis, here is the recommended solution...'
    chain.confidence = 0.85
    
    setReasoningChains(prev => [chain, ...prev])
    setCurrentChain(chain)
  }

  const addReasoningStep = useCallback((step: Omit<ReasoningStep, 'id' | 'timestamp'>) => {
    if (!currentChain) return
    
    const newStep: ReasoningStep = {
      ...step,
      id: `${currentChain.id}-${Date.now()}`,
      timestamp: new Date()
    }
    
    setCurrentChain(prev => prev ? {
      ...prev,
      steps: [...prev.steps, newStep]
    } : null)
  }, [currentChain])

  const addDecisionNode = useCallback((decision: Omit<DecisionNode, 'id'>) => {
    if (!currentChain) return
    
    const newDecision: DecisionNode = {
      ...decision,
      id: `decision-${Date.now()}`
    }
    
    setCurrentChain(prev => prev ? {
      ...prev,
      decisions: [...prev.decisions, newDecision]
    } : null)
  }, [currentChain])

  const updateConfig = useCallback((newConfig: Partial<HRMConfig>) => {
    setConfig(prev => ({ ...prev, ...newConfig }))
  }, [])

  const getReasoningChain = useCallback((id: string): ReasoningChain | null => {
    return reasoningChains.find(chain => chain.id === id) || null
  }, [reasoningChains])

  const getActiveReasoning = useCallback((): ReasoningChain | null => {
    return currentChain
  }, [currentChain])

  const analyzeProblem = useCallback(async (problem: string): Promise<ReasoningChain> => {
    await startReasoning(problem)
    return currentChain || {
      id: 'analysis-' + Date.now(),
      problem,
      steps: [],
      decisions: [],
      conclusion: 'Analysis not completed',
      confidence: 0,
      alternatives: [],
      metadata: {
        domain: 'general',
        complexity: 'low',
        timeSpent: 0,
        resourcesUsed: []
      }
    }
  }, [startReasoning, currentChain])

  const generateAlternatives = useCallback(async (problem: string): Promise<string[]> => {
    // Simulate alternative generation
    await new Promise(resolve => setTimeout(resolve, 500))
    
    const alternatives = [
      'Alternative approach 1',
      'Alternative approach 2',
      'Alternative approach 3'
    ]
    
    return alternatives
  }, [])

  const evaluateDecision = useCallback(async (decision: DecisionNode): Promise<DecisionOption | null> => {
    // Simulate decision evaluation
    await new Promise(resolve => setTimeout(resolve, 300))
    
    // Return the option with highest probability
    return decision.options.reduce((best, current) => 
      current.probability > best.probability ? current : best
    )
  }, [])

  const clearReasoningHistory = useCallback(() => {
    setReasoningChains([])
    setCurrentChain(null)
    setReasoningProgress(0)
  }, [])

  const exportReasoningChain = useCallback((id: string): string => {
    const chain = getReasoningChain(id)
    return chain ? JSON.stringify(chain, null, 2) : ''
  }, [getReasoningChain])

  const importReasoningChain = useCallback((data: string): ReasoningChain | null => {
    try {
      const chain = JSON.parse(data) as ReasoningChain
      setReasoningChains(prev => [chain, ...prev])
      return chain
    } catch (error) {
      console.error('Failed to import reasoning chain:', error)
      return null
    }
  }, [])

  return {
    // State
    reasoningChains,
    currentChain,
    isReasoning,
    reasoningProgress,
    config,
    
    // Actions
    startReasoning,
    addReasoningStep,
    addDecisionNode,
    updateConfig,
    getReasoningChain,
    getActiveReasoning,
    
    // Analysis
    analyzeProblem,
    generateAlternatives,
    evaluateDecision,
    
    // Utilities
    clearReasoningHistory,
    exportReasoningChain,
    importReasoningChain
  }
}

export default useHRM
