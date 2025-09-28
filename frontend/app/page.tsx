'use client'

import React, { useState, useEffect } from 'react'
import { 
  Box, 
  AppBar, 
  Toolbar, 
  Typography, 
  IconButton,
  useTheme,
  useMediaQuery
} from '@mui/material'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Menu as MenuIcon,
  Settings as SettingsIcon,
  Mic as MicIcon,
  MicOff as MicOffIcon,
  Palette as PaletteIcon,
  Chat as ChatIcon,
  SmartToy as SmartToyIcon,
  TrendingUp as TrendingUpIcon,
  Code as CodeIcon,
  Visibility as VisibilityIcon,
  School as SchoolIcon
} from '@mui/icons-material'

// Import our enhanced components
import { NavigationCard } from '@/components/navigation/NavigationCard'
import { AdvancedSettings } from '@/components/settings/AdvancedSettings'
import { AnimatedCard } from '@/components/animations/AdvancedAnimations'
import { useLayoutPersistence } from '@/hooks/useLayoutPersistence'
import { useKeyboardNavigation } from '@/hooks/useKeyboardNavigation'
import { getDefaultTheme, themeConfigs } from '@/theme/AdvancedThemes'

// Import components directly instead of lazy loading
import { MuiEnhancedChatPanel } from '@/components/MuiEnhancedChatPanel'
import { CodeEditor } from '@/components/CodeEditor'
import { LearningDashboard } from '@/components/LearningDashboard'
import { MultimodalPanel } from '@/components/MultimodalPanel'
import { AgentControlPanel } from '@/components/AgentControlPanel'
import { SelfOptimizationPanel } from '@/components/SelfOptimizationPanel'

// Import new enhanced components
import { VoiceProfileSelector } from '@/components/VoiceProfileSelector'
import { StatusIndicator } from '@/components/StatusIndicator'
import { NotificationCenter, useNotifications, ErrorBoundary } from '@/components/ErrorHandling'
import { useAudioFeedback } from '@/hooks/useAudioFeedback'
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { ThemeCustomizationProvider, ThemeCustomizationPanel } from '@/components/ThemeCustomization'
import { 
  MicroInteractionButton, 
  FloatingActionButton, 
  LoadingSpinner,
  ProgressBar,
  StaggerContainer,
  fadeInUp,
  scaleIn,
  bounceIn
} from '@/components/animations/AdvancedAnimations'

const panels = [
  { 
    id: 'chat', 
    label: 'AI Assistant', 
    icon: ChatIcon, 
    color: 'primary' as const,
    description: 'Intelligent conversations with AI + Voice + Advanced features',
    trend: 'Personal AI Assistant'
  },
  { 
    id: 'agents', 
    label: 'AI Agents', 
    icon: SmartToyIcon, 
    color: 'secondary' as const,
    description: 'Prompt-based intelligent agents for productivity and automation',
    trend: 'Smart Automation'
  },
  { 
    id: 'optimization', 
    label: 'Self-Optimization', 
    icon: TrendingUpIcon, 
    color: 'success' as const,
    description: 'AI-driven task automation and productivity enhancement',
    trend: 'Autonomous Productivity'
  },
  { 
    id: 'code', 
    label: 'Code Assistant', 
    icon: CodeIcon, 
    color: 'info' as const,
    description: 'AI-assisted coding and development with intelligent suggestions',
    trend: 'Smart Development'
  },
  { 
    id: 'multimodal', 
    label: 'Vision Assistant', 
    icon: VisibilityIcon, 
    color: 'warning' as const,
    description: 'Upload images for AI analysis and visual understanding',
    trend: 'Visual Intelligence'
  },
  { 
    id: 'learning', 
    label: 'Learning Hub', 
    icon: SchoolIcon, 
    color: 'error' as const,
    description: 'Track your progress and achievements in your personal AI learning journey',
    trend: 'Growth Analytics'
  }
]

function HomePageContent() {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [themeCustomizationOpen, setThemeCustomizationOpen] = useState(false)
  
  // Use our persistence system
  const { preferences, updatePreference } = useLayoutPersistence()
  const [activePanel, setActivePanel] = useState(preferences.activePanel)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [selectedVoiceProfile, setSelectedVoiceProfile] = useState('assistant')
  const [showVoiceSelector, setShowVoiceSelector] = useState(false)
  const [showStatusIndicator, setShowStatusIndicator] = useState(true)
  const [isLoading, setIsLoading] = useState(false)
  const [loadingProgress, setLoadingProgress] = useState(0)

  // Enhanced features
  const notifications = useNotifications()
  const audioFeedback = useAudioFeedback({
    enabled: true,
    volume: 0.3,
    sounds: {
      messageSent: 'messageSent',
      messageReceived: 'messageReceived',
      error: 'error',
      success: 'success',
      notification: 'notification',
      click: 'click',
      hover: 'hover'
    }
  })

  // Keyboard shortcuts
  const keyboardShortcuts = useKeyboardShortcuts({
    onSendMessage: () => {
      audioFeedback.sounds.click()
      notifications.showInfo('Keyboard Shortcut', 'Ctrl/Cmd + Enter to send message')
    },
    onToggleVoiceSelector: () => {
      setShowVoiceSelector(!showVoiceSelector)
      audioFeedback.sounds.click()
    },
    onToggleStatusIndicator: () => {
      setShowStatusIndicator(!showStatusIndicator)
      audioFeedback.sounds.click()
    },
    onToggleSidebar: () => {
      setSidebarOpen(!sidebarOpen)
      audioFeedback.sounds.click()
    },
    onSwitchPanel: (panelId) => {
      setActivePanel(panelId)
      audioFeedback.sounds.click()
      notifications.showSuccess('Panel Switched', `Switched to ${panelId} panel`)
    },
    onFocusInput: () => {
      const input = document.querySelector('textarea[placeholder*="Ask me anything"]') as HTMLTextAreaElement
      if (input) {
        input.focus()
        audioFeedback.sounds.click()
      }
    },
    onEscape: () => {
      setShowVoiceSelector(false)
      setShowStatusIndicator(false)
      setSettingsOpen(false)
      setThemeCustomizationOpen(false)
      audioFeedback.sounds.click()
    }
  })

  // Keyboard navigation
  useKeyboardNavigation({
    onNext: () => {
      const currentIndex = panels.findIndex(p => p.id === activePanel)
      const nextIndex = (currentIndex + 1) % panels.length
      setActivePanel(panels[nextIndex].id)
    },
    onPrevious: () => {
      const currentIndex = panels.findIndex(p => p.id === activePanel)
      const prevIndex = currentIndex === 0 ? panels.length - 1 : currentIndex - 1
      setActivePanel(panels[prevIndex].id)
    },
    onSelect: () => {
      // Panel is already selected, could add additional action here
    },
    onEscape: () => {
      setSettingsOpen(false)
    }
  })

  // Update preferences when state changes
  useEffect(() => {
    updatePreference('activePanel', activePanel)
  }, [activePanel, updatePreference])

  useEffect(() => {
    updatePreference('sidebarOpen', sidebarOpen)
  }, [sidebarOpen, updatePreference])

  // Voice profile testing function with enhanced feedback
  const handleTestVoice = async (profileId: string) => {
    try {
      setIsLoading(true)
      setLoadingProgress(0)
      
      // Simulate progress
      const progressInterval = setInterval(() => {
        setLoadingProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 100)

      audioFeedback.sounds.click()
      notifications.showInfo('Testing Voice', `Testing ${profileId} voice profile...`)

      const response = await fetch('http://localhost:8086/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: `This is a test of the ${profileId} voice profile.`,
          voice_profile: profileId,
          emotion: 'neutral',
          speed: 'normal'
        }),
      })
      
      if (response.ok) {
        const data = await response.json()
        setLoadingProgress(100)
        audioFeedback.sounds.success()
        notifications.showSuccess('Voice Test Complete', `Successfully tested ${profileId} voice profile`)
        console.log('Voice test successful:', data)
      } else {
        throw new Error('Voice test failed')
      }
    } catch (error) {
      audioFeedback.sounds.error()
      notifications.showError('Voice Test Failed', `Failed to test ${profileId} voice profile`, {
        details: error instanceof Error ? error.message : 'Unknown error'
      })
      console.error('Error testing voice:', error)
    } finally {
      setIsLoading(false)
      setLoadingProgress(0)
    }
  }

  const renderPanelContent = () => {
    const panelProps = {
      activeModel: preferences.activeModel,
      customModelName: preferences.activeModel,
      onSwitchPanel: () => {}
    }

    switch (activePanel) {
      case 'chat':
        return <MuiEnhancedChatPanel {...panelProps} />
      case 'agents':
        return <AgentControlPanel />
      case 'optimization':
        return <SelfOptimizationPanel />
      case 'code':
        return <CodeEditor />
      case 'multimodal':
        return (
          <MultimodalPanel 
            activeModel={preferences.activeModel}
            onImageAnalysis={(image, analysis) => {
              console.log('Image analyzed:', image.file.name, analysis)
            }}
          />
        )
      case 'learning':
        return <LearningDashboard />
      default:
        return <MuiEnhancedChatPanel {...panelProps} />
    }
  }

  return (
    <Box sx={{ 
      height: '100vh', 
      overflow: 'hidden',
      background: theme.palette.background.default,
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Enhanced Header */}
      <AppBar position="fixed" sx={{ zIndex: theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            edge="start"
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Personal AI Assistant
          </Typography>

          {/* Status Indicator */}
          {showStatusIndicator && (
            <Box sx={{ mr: 2 }}>
              <StatusIndicator compact onRefresh={() => window.location.reload()} />
            </Box>
          )}

          {/* Voice Profile Selector */}
          <Box sx={{ mr: 2 }}>
            <VoiceProfileSelector
              selectedProfile={selectedVoiceProfile}
              onProfileChange={setSelectedVoiceProfile}
              onTestVoice={handleTestVoice}
              compact
            />
          </Box>

          <IconButton
            color="inherit"
            onClick={() => updatePreference('isVoiceEnabled', !preferences.isVoiceEnabled)}
            sx={{ mr: 1 }}
          >
            {preferences.isVoiceEnabled ? <MicOffIcon /> : <MicIcon />}
          </IconButton>

          <IconButton
            color="inherit"
            onClick={() => setSettingsOpen(true)}
          >
            <SettingsIcon />
          </IconButton>

          {/* Toggle buttons for enhanced features */}
          <IconButton
            color="inherit"
            onClick={() => setShowVoiceSelector(!showVoiceSelector)}
            sx={{ ml: 1 }}
            onMouseEnter={() => audioFeedback.sounds.hover()}
          >
            <PaletteIcon />
          </IconButton>
          
          <IconButton
            color="inherit"
            onClick={() => setShowStatusIndicator(!showStatusIndicator)}
            sx={{ ml: 1 }}
            onMouseEnter={() => audioFeedback.sounds.hover()}
          >
            <TrendingUpIcon />
          </IconButton>

          <IconButton
            color="inherit"
            onClick={() => setThemeCustomizationOpen(!themeCustomizationOpen)}
            sx={{ ml: 1 }}
            onMouseEnter={() => audioFeedback.sounds.hover()}
          >
            <SettingsIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Box sx={{ 
        flexGrow: 1, 
        mt: '64px',
        display: 'flex',
        height: 'calc(100vh - 64px)'
      }}>
        {/* Desktop Sidebar */}
        {!isMobile && (
          <Box sx={{
            width: sidebarOpen ? 320 : 0,
            transition: 'width 0.3s ease-in-out',
            overflow: 'hidden',
            background: 'rgba(255, 255, 255, 0.03)',
            backdropFilter: 'blur(20px)',
            borderRight: '1px solid rgba(255, 255, 255, 0.1)',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <Box sx={{ p: 3, flex: 1, overflow: 'auto' }}>
              <StaggerContainer>
                {panels.map((panel, index) => (
                  <AnimatedCard key={panel.id} delay={index * 0.1}>
                    <NavigationCard
                      id={panel.id}
                      label={panel.label}
                      icon={panel.icon}
                      color={panel.color}
                      description={panel.description}
                      trend={panel.trend}
                      isActive={activePanel === panel.id}
                      onClick={() => setActivePanel(panel.id)}
                      variant="desktop"
                    />
                  </AnimatedCard>
                ))}
              </StaggerContainer>
            </Box>

            {/* Status Card */}
            <AnimatedCard delay={0.8}>
              <Box sx={{ 
                p: 2, 
                m: 2, 
                background: 'rgba(255, 255, 255, 0.05)',
                borderRadius: 2,
                border: '1px solid rgba(255, 255, 255, 0.1)'
              }}>
                <Typography variant="subtitle2" color="text.primary" sx={{ mb: 1 }}>
                  Active Model
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {preferences.activeModel}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    background: 'linear-gradient(45deg, #4caf50 30%, #81c784 90%)',
                    animation: 'pulse 2s infinite'
                  }} />
                  <Typography variant="caption" color="text.secondary">
                    Online • Excellent Performance
                  </Typography>
                </Box>
              </Box>
            </AnimatedCard>
          </Box>
        )}

        {/* Main Panel Content */}
        <Box sx={{ 
          flexGrow: 1,
          height: '100%',
          overflow: 'hidden',
          position: 'relative'
        }}>
          <AnimatePresence mode="wait">
            <motion.div
              key={activePanel}
              initial={{ opacity: 0, x: 20, scale: 0.95 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: -20, scale: 0.95 }}
              transition={{ 
                duration: 0.4, 
                ease: [0.4, 0, 0.2, 1],
                scale: { duration: 0.3 }
              }}
              style={{ height: '100%' }}
            >
              {renderPanelContent()}
            </motion.div>
          </AnimatePresence>
        </Box>

        {/* Mobile Bottom Navigation */}
        {isMobile && (
          <Box sx={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            background: 'rgba(0, 0, 0, 0.8)',
            backdropFilter: 'blur(20px)',
            borderTop: '1px solid rgba(255, 255, 255, 0.1)',
            zIndex: 1300,
            p: 1
          }}>
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'space-around',
              alignItems: 'center'
            }}>
              {panels.map((panel) => (
                <AnimatedCard key={`mobile-${panel.id}`}>
                  <NavigationCard
                    id={panel.id}
                    label={panel.label}
                    icon={panel.icon}
                    color={panel.color}
                    description={panel.description}
                    trend={panel.trend}
                    isActive={activePanel === panel.id}
                    onClick={() => setActivePanel(panel.id)}
                    variant="mobile"
                  />
                </AnimatedCard>
              ))}
            </Box>
          </Box>
        )}

        {/* Enhanced Features Floating Panel */}
        <Box sx={{
          position: 'fixed',
          bottom: 20,
          right: 20,
          zIndex: 1000,
          display: 'flex',
          flexDirection: 'column',
          gap: 2
        }}>
          {/* Voice Profile Selector */}
          {showVoiceSelector && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
            >
              <VoiceProfileSelector
                selectedProfile={selectedVoiceProfile}
                onProfileChange={setSelectedVoiceProfile}
                onTestVoice={handleTestVoice}
              />
            </motion.div>
          )}


          {/* Theme Customization Panel */}
          {themeCustomizationOpen && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
            >
              <AnimatedCard>
                <Box sx={{ p: 2, bgcolor: 'rgba(255, 255, 255, 0.95)', borderRadius: 2 }}>
                  <ThemeCustomizationPanel />
                </Box>
              </AnimatedCard>
            </motion.div>
          )}

          {/* Loading Indicator */}
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
            >
              <AnimatedCard>
                <Box sx={{ p: 2, bgcolor: 'rgba(255, 255, 255, 0.95)', borderRadius: 2 }}>
                  <LoadingSpinner text="Testing voice profile..." />
                  <Box sx={{ mt: 2 }}>
                    <ProgressBar progress={loadingProgress} />
                  </Box>
                </Box>
              </AnimatedCard>
            </motion.div>
          )}
        </Box>

        {/* Notification Center */}
        <NotificationCenter
          notifications={notifications.notifications}
          onRemove={notifications.removeNotification}
          onClearAll={notifications.clearAll}
        />

        {/* Floating Action Button */}
        <FloatingActionButton
          onClick={() => {
            audioFeedback.sounds.click()
            notifications.showInfo('Help', 'Use keyboard shortcuts for quick actions!')
          }}
          position="bottom-left"
          color="#4caf50"
        >
          ?
        </FloatingActionButton>
      </Box>

      {/* Advanced Settings Dialog */}
      <AdvancedSettings 
        open={settingsOpen} 
        onClose={() => setSettingsOpen(false)} 
      />
    </Box>
  )
}

export default function EnhancedPersonalAIAssistant() {
  return (
    <ErrorBoundary>
      <ThemeCustomizationProvider>
        <HomePageContent />
      </ThemeCustomizationProvider>
    </ErrorBoundary>
  )
}
