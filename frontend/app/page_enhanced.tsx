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
import { StaggerContainer, AnimatedCard } from '@/components/animations/AdvancedAnimations'
import { useLayoutPersistence } from '@/hooks/useLayoutPersistence'
import { useKeyboardNavigation } from '@/hooks/useKeyboardNavigation'
import { getDefaultTheme, themeConfigs } from '@/theme/AdvancedThemes'

// Lazy load panels for performance
import { LazyChatPanel, LazyCodeEditor, LazyLearningDashboard, LazyMultimodalPanel, LazyAgentControlPanel, LazySelfOptimizationPanel } from '@/components/performance/LazyComponents'

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

export default function EnhancedPersonalAIAssistant() {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const [settingsOpen, setSettingsOpen] = useState(false)
  
  // Use our persistence system
  const { preferences, updatePreference } = useLayoutPersistence()
  const [activePanel, setActivePanel] = useState(preferences.activePanel)
  const [sidebarOpen, setSidebarOpen] = useState(preferences.sidebarOpen)

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

  const renderPanelContent = () => {
    const panelProps = {
      activeModel: preferences.activeModel,
      customModelName: preferences.activeModel,
      onSwitchPanel: () => {}
    }

    switch (activePanel) {
      case 'chat':
        return <LazyChatPanel {...panelProps} />
      case 'agents':
        return <LazyAgentControlPanel />
      case 'optimization':
        return <LazySelfOptimizationPanel />
      case 'code':
        return <LazyCodeEditor />
      case 'multimodal':
        return (
          <LazyMultimodalPanel 
            activeModel={preferences.activeModel}
            onImageAnalysis={(image, analysis) => {
              console.log('Image analyzed:', image.file.name, analysis)
            }}
          />
        )
      case 'learning':
        return <LazyLearningDashboard />
      default:
        return <LazyChatPanel {...panelProps} />
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
      </Box>

      {/* Advanced Settings Dialog */}
      <AdvancedSettings 
        open={settingsOpen} 
        onClose={() => setSettingsOpen(false)} 
      />
    </Box>
  )
}
