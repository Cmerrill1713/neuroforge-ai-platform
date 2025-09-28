'use client'

import { useState, useEffect, useCallback } from 'react'

interface LayoutPreferences {
  sidebarOpen: boolean
  activePanel: string
  darkMode: boolean
  isVoiceEnabled: boolean
  activeModel: string
  sidebarWidth: number
  layoutDensity: 'compact' | 'comfortable' | 'spacious'
  animationSpeed: 'slow' | 'normal' | 'fast'
  theme: 'auto' | 'light' | 'dark'
}

const DEFAULT_PREFERENCES: LayoutPreferences = {
  sidebarOpen: true,
  activePanel: 'chat',
  darkMode: true,
  isVoiceEnabled: false,
  activeModel: 'qwen2.5:7b',
  sidebarWidth: 280,
  layoutDensity: 'comfortable',
  animationSpeed: 'normal',
  theme: 'auto'
}

const STORAGE_KEY = 'ai-assistant-layout-preferences'

export function useLayoutPersistence() {
  const [preferences, setPreferences] = useState<LayoutPreferences>(DEFAULT_PREFERENCES)
  const [isLoaded, setIsLoaded] = useState(false)

  // Load preferences from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) {
        const parsedPreferences = JSON.parse(saved)
        setPreferences({ ...DEFAULT_PREFERENCES, ...parsedPreferences })
      }
    } catch (error) {
      console.warn('Failed to load layout preferences:', error)
    } finally {
      setIsLoaded(true)
    }
  }, [])

  // Save preferences to localStorage
  const updatePreference = useCallback(<K extends keyof LayoutPreferences>(
    key: K,
    value: LayoutPreferences[K]
  ) => {
    setPreferences(prev => {
      const newPreferences = { ...prev, [key]: value }
      try {
        // Only save serializable data, filter out any DOM elements or circular references
        const serializablePreferences = {
          activePanel: newPreferences.activePanel,
          sidebarOpen: newPreferences.sidebarOpen,
          darkMode: newPreferences.darkMode,
          isVoiceEnabled: newPreferences.isVoiceEnabled,
          theme: newPreferences.theme,
          layoutDensity: newPreferences.layoutDensity,
          animationSpeed: newPreferences.animationSpeed,
        }
        localStorage.setItem(STORAGE_KEY, JSON.stringify(serializablePreferences))
      } catch (error) {
        console.warn('Failed to save layout preferences:', error)
      }
      return newPreferences
    })
  }, [])

  // Batch update multiple preferences
  const updatePreferences = useCallback((updates: Partial<LayoutPreferences>) => {
    setPreferences(prev => {
      const newPreferences = { ...prev, ...updates }
      try {
        // Only save serializable data, filter out any DOM elements or circular references
        const serializablePreferences = {
          activePanel: newPreferences.activePanel,
          sidebarOpen: newPreferences.sidebarOpen,
          darkMode: newPreferences.darkMode,
          isVoiceEnabled: newPreferences.isVoiceEnabled,
          theme: newPreferences.theme,
          layoutDensity: newPreferences.layoutDensity,
          animationSpeed: newPreferences.animationSpeed,
        }
        localStorage.setItem(STORAGE_KEY, JSON.stringify(serializablePreferences))
      } catch (error) {
        console.warn('Failed to save layout preferences:', error)
      }
      return newPreferences
    })
  }, [])

  // Reset to defaults
  const resetPreferences = useCallback(() => {
    setPreferences(DEFAULT_PREFERENCES)
    try {
      localStorage.removeItem(STORAGE_KEY)
    } catch (error) {
      console.warn('Failed to reset layout preferences:', error)
    }
  }, [])

  // Export preferences
  const exportPreferences = useCallback(() => {
    try {
      // Only export serializable data
      const serializablePreferences = {
        activePanel: preferences.activePanel,
        sidebarOpen: preferences.sidebarOpen,
        darkMode: preferences.darkMode,
        isVoiceEnabled: preferences.isVoiceEnabled,
        theme: preferences.theme,
        layoutDensity: preferences.layoutDensity,
        animationSpeed: preferences.animationSpeed,
      }
      const dataStr = JSON.stringify(serializablePreferences, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(dataBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'ai-assistant-preferences.json'
      link.click()
      URL.revokeObjectURL(url)
    } catch (error) {
      console.warn('Failed to export preferences:', error)
    }
  }, [preferences])

  // Import preferences
  const importPreferences = useCallback((file: File) => {
    return new Promise<void>((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const imported = JSON.parse(e.target?.result as string)
          const validatedPreferences = { ...DEFAULT_PREFERENCES, ...imported }
          setPreferences(validatedPreferences)
          
          // Only save serializable data, filter out any DOM elements or circular references
          const serializablePreferences = {
            activePanel: validatedPreferences.activePanel,
            sidebarOpen: validatedPreferences.sidebarOpen,
            darkMode: validatedPreferences.darkMode,
            isVoiceEnabled: validatedPreferences.isVoiceEnabled,
            themeName: validatedPreferences.themeName,
            layoutDensity: validatedPreferences.layoutDensity,
            animationSpeed: validatedPreferences.animationSpeed,
          }
          localStorage.setItem(STORAGE_KEY, JSON.stringify(serializablePreferences))
          resolve()
        } catch (error) {
          reject(new Error('Invalid preferences file'))
        }
      }
      reader.onerror = () => reject(new Error('Failed to read file'))
      reader.readAsText(file)
    })
  }, [])

  return {
    preferences,
    isLoaded,
    updatePreference,
    updatePreferences,
    resetPreferences,
    exportPreferences,
    importPreferences
  }
}

// Theme detection hook
export function useThemeDetection() {
  const [systemTheme, setSystemTheme] = useState<'light' | 'dark'>('dark')

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    
    const handleChange = (e: MediaQueryListEvent) => {
      setSystemTheme(e.matches ? 'dark' : 'light')
    }

    setSystemTheme(mediaQuery.matches ? 'dark' : 'light')
    mediaQuery.addEventListener('change', handleChange)

    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  return systemTheme
}

// Responsive breakpoint hook
export function useResponsiveBreakpoint() {
  const [breakpoint, setBreakpoint] = useState<'mobile' | 'tablet' | 'desktop'>('desktop')

  useEffect(() => {
    const updateBreakpoint = () => {
      const width = window.innerWidth
      if (width < 768) {
        setBreakpoint('mobile')
      } else if (width < 1024) {
        setBreakpoint('tablet')
      } else {
        setBreakpoint('desktop')
      }
    }

    updateBreakpoint()
    window.addEventListener('resize', updateBreakpoint)
    return () => window.removeEventListener('resize', updateBreakpoint)
  }, [])

  return breakpoint
}

// Performance monitoring hook
export function usePerformanceMonitoring() {
  const [metrics, setMetrics] = useState({
    renderTime: 0,
    memoryUsage: 0,
    frameRate: 60
  })

  useEffect(() => {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries()
      const renderTime = entries.reduce((acc, entry) => acc + entry.duration, 0)
      
      setMetrics(prev => ({
        ...prev,
        renderTime: renderTime / entries.length
      }))
    })

    observer.observe({ entryTypes: ['measure', 'navigation'] })

    // Monitor memory usage
    const checkMemory = () => {
      if ('memory' in performance) {
        const memory = (performance as any).memory
        setMetrics(prev => ({
          ...prev,
          memoryUsage: memory.usedJSHeapSize / memory.jsHeapSizeLimit
        }))
      }
    }

    const interval = setInterval(checkMemory, 5000)

    return () => {
      observer.disconnect()
      clearInterval(interval)
    }
  }, [])

  return metrics
}
