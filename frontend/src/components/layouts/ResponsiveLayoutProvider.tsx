'use client'

import React, { useState, useEffect } from 'react'
import { useTheme, useMediaQuery, Box } from '@mui/material'
import { CardBasedDesktopLayout } from './CardBasedDesktopLayout'
import { CardBasedMobileLayout } from './CardBasedMobileLayout'
import { AppThemeProvider } from '../../theme'

interface Panel {
  id: string
  label: string
  icon: React.ComponentType<any>
  color: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info'
  description: string
  trend: string
}

interface ResponsiveLayoutProviderProps {
  panels: Panel[]
  children: React.ReactNode
}

export function ResponsiveLayoutProvider({ panels, children }: ResponsiveLayoutProviderProps) {
  const [darkMode, setDarkMode] = useState(true)
  const [activePanel, setActivePanel] = useState('chat')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(false)
  const [activeModel, setActiveModel] = useState('qwen2.5:7b')
  const [isMobile, setIsMobile] = useState(false)

  // Handle responsive breakpoints
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
    }
    
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  // Auto-close sidebar on mobile
  useEffect(() => {
    if (isMobile) {
      setSidebarOpen(false)
    }
  }, [isMobile])

  const commonProps = {
    activePanel,
    setActivePanel,
    panels,
    isVoiceEnabled,
    setIsVoiceEnabled,
    darkMode,
    setDarkMode,
    activeModel
  }

  return (
    <AppThemeProvider darkMode={darkMode}>
      <Box sx={{ height: '100vh', overflow: 'hidden' }}>
        {isMobile ? (
          <CardBasedMobileLayout {...commonProps}>
            {children}
          </CardBasedMobileLayout>
        ) : (
          <CardBasedDesktopLayout
            {...commonProps}
            sidebarOpen={sidebarOpen}
            setSidebarOpen={setSidebarOpen}
          >
            {children}
          </CardBasedDesktopLayout>
        )}
      </Box>
    </AppThemeProvider>
  )
}

// Hook for accessing layout context
export function useLayout() {
  return {
    // Add any shared layout state here if needed
  }
}
