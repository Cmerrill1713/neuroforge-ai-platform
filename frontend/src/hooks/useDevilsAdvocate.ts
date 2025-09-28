'use client'

import React, { useState, useCallback, useEffect } from 'react'

interface DevilsAdvocateState {
  isVisible: boolean
  currentAction: string
  currentResponse?: string
  challenges: DevilsAdvocateChallenge[]
  isEnabled: boolean
}

interface DevilsAdvocateChallenge {
  id: string
  type: 'warning' | 'question' | 'alternative' | 'risk' | 'bias'
  title: string
  message: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  confidence: number
  alternatives?: string[]
  risks?: string[]
  timestamp: Date
}

interface DevilsAdvocateActions {
  showDevilsAdvocate: (action: string, response?: string) => void
  hideDevilsAdvocate: () => void
  acceptChallenge: (challengeId: string) => void
  rejectChallenge: (challengeId: string) => void
  toggleDevilsAdvocate: () => void
  setEnabled: (enabled: boolean) => void
}

export function useDevilsAdvocate(): DevilsAdvocateState & DevilsAdvocateActions {
  const [state, setState] = useState<DevilsAdvocateState>({
    isVisible: false,
    currentAction: '',
    currentResponse: undefined,
    challenges: [],
    isEnabled: true
  })

  const showDevilsAdvocate = useCallback((action: string, response?: string) => {
    if (!state.isEnabled) return
    
    setState(prev => ({
      ...prev,
      isVisible: true,
      currentAction: action,
      currentResponse: response,
      challenges: []
    }))
  }, [state.isEnabled])

  const hideDevilsAdvocate = useCallback(() => {
    setState(prev => ({
      ...prev,
      isVisible: false,
      currentAction: '',
      currentResponse: undefined,
      challenges: []
    }))
  }, [])

  const acceptChallenge = useCallback((challengeId: string) => {
    console.log(`✅ Devil's Advocate Challenge Accepted: ${challengeId}`)
    setState(prev => ({
      ...prev,
      challenges: prev.challenges.filter(c => c.id !== challengeId)
    }))
  }, [])

  const rejectChallenge = useCallback((challengeId: string) => {
    console.log(`❌ Devil's Advocate Challenge Rejected: ${challengeId}`)
    setState(prev => ({
      ...prev,
      challenges: prev.challenges.filter(c => c.id !== challengeId)
    }))
  }, [])

  const toggleDevilsAdvocate = useCallback(() => {
    setState(prev => ({
      ...prev,
      isEnabled: !prev.isEnabled
    }))
  }, [])

  const setEnabled = useCallback((enabled: boolean) => {
    setState(prev => ({
      ...prev,
      isEnabled: enabled
    }))
  }, [])

  return {
    ...state,
    showDevilsAdvocate,
    hideDevilsAdvocate,
    acceptChallenge,
    rejectChallenge,
    toggleDevilsAdvocate,
    setEnabled
  }
}

// Utility function to trigger Devil's Advocate from anywhere
export function triggerDevilsAdvocate(action: string, response?: string) {
  console.log(`🎭 Devil's Advocate Triggered: ${action}`)
  
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('devils-advocate-trigger', {
      detail: { action, response }
    }))
  }
}

// Hook to listen for Devil's Advocate triggers
export function useDevilsAdvocateListener() {
  const devilsAdvocate = useDevilsAdvocate()
  
  useEffect(() => {
    const handleTrigger = (event: CustomEvent) => {
      const { action, response } = event.detail
      devilsAdvocate.showDevilsAdvocate(action, response)
    }

    window.addEventListener('devils-advocate-trigger', handleTrigger as EventListener)
    
    return () => {
      window.removeEventListener('devils-advocate-trigger', handleTrigger as EventListener)
    }
  }, [devilsAdvocate])

  return devilsAdvocate
}