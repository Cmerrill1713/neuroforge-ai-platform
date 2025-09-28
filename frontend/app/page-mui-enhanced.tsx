"use client"

import React, { useState, useEffect } from 'react'
import {
  ThemeProvider,
  CssBaseline,
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Chip,
  Avatar,
  Card,
  CardContent,
  Stack,
  Fab,
  Tooltip,
  Badge,
  Switch,
  FormControlLabel,
  Divider,
  Paper,
  Grid
} from '@mui/material'
import {
  Menu as MenuIcon,
  Chat as ChatIcon,
  Code as CodeIcon,
  Image as ImageIcon,
  Analytics as AnalyticsIcon,
  Add as AddIcon,
  Mic as MicIcon,
  MicOff as MicOffIcon,
  Palette as PaletteIcon,
  SmartToy as SmartToyIcon,
  Memory as MemoryIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
  Storage as StorageIcon,
  Wifi as WifiIcon,
  WifiOff as WifiOffIcon
} from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'
import { aiStudioEnhancedTheme } from '@/theme/muiTheme'
import { MuiEnhancedChatPanel } from '@/components/MuiEnhancedChatPanel'
import { MuiPatternsProvider } from '@/components/MuiPatternsProvider'
import { MuiPatternsPanel } from '@/components/MuiPatternsPanel'
import { CodeEditor } from '@/components/CodeEditor'
import { LearningDashboard } from '@/components/LearningDashboard'
import { MultimodalPanel } from '@/components/MultimodalPanel'
import { AIModelSelector } from '@/components/AIModelSelector'
import { RedisCacheIndicator } from '@/components/RedisCacheIndicator'
import { WebSocketStatus } from '@/components/WebSocketStatus'
import { PerformanceMonitor } from '@/components/PerformanceMonitor'

const drawerWidth = 280

export default function MuiEnhancedHome() {
  const [activeModel, setActiveModel] = useState('qwen2.5:7b')
  const [darkMode, setDarkMode] = useState(true)
  const [activePanel, setActivePanel] = useState('chat')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(false)
  const [scrollY, setScrollY] = useState(0)
  const [isLoaded, setIsLoaded] = useState(false)

  useEffect(() => {
    setIsLoaded(true)
    
    const handleScroll = () => setScrollY(window.scrollY)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const panels = [
    { 
      id: 'chat', 
      label: 'AI Chat', 
      icon: ChatIcon, 
      color: 'primary',
      description: 'Intelligent conversations with AI',
      trend: 'AI-Powered Personalization'
    },
    { 
      id: 'patterns', 
      label: 'MUI Patterns', 
      icon: PaletteIcon, 
      color: 'secondary',
      description: 'Material-UI design patterns',
      trend: 'Design System Integration'
    },
    { 
      id: 'code', 
      label: 'Code Editor', 
      icon: CodeIcon, 
      color: 'success',
      description: 'AI-assisted development',
      trend: 'Component-Driven Development'
    },
    { 
      id: 'multimodal', 
      label: 'Multimodal', 
      icon: ImageIcon, 
      color: 'info',
      description: 'Vision and image analysis',
      trend: 'AR/VR Integration'
    },
    { 
      id: 'learning', 
      label: 'Learning', 
      icon: AnalyticsIcon, 
      color: 'warning',
      description: 'Progress tracking & analytics',
      trend: 'Data Visualization'
    }
  ]

  const performanceMetrics = [
    { label: 'Load', value: '0ms', icon: SpeedIcon, color: 'primary' },
    { label: 'Render', value: '0ms', icon: MemoryIcon, color: 'success' },
    { label: 'Memory', value: '0MB', icon: StorageIcon, color: 'info' },
    { label: 'Security', value: '100%', icon: SecurityIcon, color: 'error' }
  ]

  return (
    <MuiPatternsProvider>
      <ThemeProvider theme={aiStudioEnhancedTheme}>
        <CssBaseline />
      <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
        {/* Enhanced AppBar */}
        <AppBar
          position="fixed"
          sx={{
            zIndex: (theme) => theme.zIndex.drawer + 1,
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(20px)',
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            boxShadow: 'none'
          }}
        >
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

            <Avatar
              sx={{
                mr: 2,
                background: 'linear-gradient(135deg, #1976d2 0%, #9c27b0 100%)',
                width: 40,
                height: 40
              }}
            >
              <SmartToyIcon />
            </Avatar>

            <Box sx={{ flexGrow: 1 }}>
              <Typography
                variant="h6"
                sx={{
                  background: 'linear-gradient(135deg, #ffffff 0%, #e3f2fd 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  fontWeight: 700
                }}
              >
                AI Studio 2025 Enhanced
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                Next-Gen Development Environment with Material-UI
              </Typography>
            </Box>

            <Stack direction="row" spacing={1} alignItems="center">
              {/* Voice UI Toggle */}
              <Tooltip title={isVoiceEnabled ? 'Disable Voice' : 'Enable Voice'}>
                <IconButton
                  onClick={() => setIsVoiceEnabled(!isVoiceEnabled)}
                  sx={{
                    color: isVoiceEnabled ? '#4caf50' : 'rgba(255, 255, 255, 0.7)',
                    background: isVoiceEnabled ? 'rgba(76, 175, 80, 0.2)' : 'transparent',
                    border: isVoiceEnabled ? '1px solid rgba(76, 175, 80, 0.3)' : 'none'
                  }}
                >
                  {isVoiceEnabled ? <MicIcon /> : <MicOffIcon />}
                </IconButton>
              </Tooltip>

              <AIModelSelector 
                activeModel={activeModel} 
                onModelChange={setActiveModel}
                customModelNames={{}}
                onCustomNameChange={() => {}}
              />

              <RedisCacheIndicator />
              <WebSocketStatus />

              <Tooltip title="Toggle Theme">
                <IconButton onClick={() => setDarkMode(!darkMode)} color="inherit">
                  <PaletteIcon />
                </IconButton>
              </Tooltip>
            </Stack>
          </Toolbar>
        </AppBar>

        {/* Enhanced Performance Monitor */}
        <Paper
          elevation={0}
          sx={{
            position: 'fixed',
            top: 80,
            left: 0,
            right: 0,
            zIndex: (theme) => theme.zIndex.drawer - 1,
            background: 'rgba(255, 255, 255, 0.03)',
            backdropFilter: 'blur(10px)',
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            py: 1
          }}
        >
          <Stack
            direction="row"
            spacing={4}
            justifyContent="center"
            alignItems="center"
            sx={{ px: 2 }}
          >
            {performanceMetrics.map((metric, index) => (
              <Stack key={index} direction="row" spacing={1} alignItems="center">
                <metric.icon sx={{ fontSize: 16, color: `${metric.color}.main` }} />
                <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  {metric.label}:
                </Typography>
                <Typography variant="caption" sx={{ color: `${metric.color}.main`, fontWeight: 600 }}>
                  {metric.value}
                </Typography>
              </Stack>
            ))}
            
            {/* Voice Status Indicator */}
            {isVoiceEnabled && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                exit={{ scale: 0 }}
              >
                <Chip
                  icon={<MicIcon />}
                  label="Voice Active"
                  size="small"
                  sx={{
                    background: 'rgba(76, 175, 80, 0.2)',
                    color: '#4caf50',
                    border: '1px solid rgba(76, 175, 80, 0.3)',
                    '& .MuiChip-icon': { color: '#4caf50' }
                  }}
                />
              </motion.div>
            )}
          </Stack>
        </Paper>

        {/* Enhanced Sidebar */}
        <Drawer
          variant="persistent"
          anchor="left"
          open={sidebarOpen}
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: drawerWidth,
              boxSizing: 'border-box',
              background: 'rgba(255, 255, 255, 0.03)',
              backdropFilter: 'blur(20px)',
              borderRight: '1px solid rgba(255, 255, 255, 0.1)',
              mt: '64px'
            }
          }}
        >
          <Box sx={{ p: 2 }}>
            <List>
              {panels.map((panel, index) => (
                <motion.div
                  key={panel.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <ListItem disablePadding sx={{ mb: 1 }}>
                    <ListItemButton
                      selected={activePanel === panel.id}
                      onClick={() => setActivePanel(panel.id)}
                      sx={{
                        borderRadius: 2,
                        mb: 1,
                        background: activePanel === panel.id
                          ? panel.color === 'primary' ? 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)'
                          : panel.color === 'secondary' ? 'linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%)'
                          : panel.color === 'success' ? 'linear-gradient(135deg, #4caf50 0%, #388e3c 100%)'
                          : 'linear-gradient(135deg, #ff9800 0%, #f57c00 100%)'
                          : 'transparent',
                        '&:hover': {
                          background: activePanel === panel.id
                            ? panel.color === 'primary' ? 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)'
                            : panel.color === 'secondary' ? 'linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%)'
                            : panel.color === 'success' ? 'linear-gradient(135deg, #4caf50 0%, #388e3c 100%)'
                            : 'linear-gradient(135deg, #ff9800 0%, #f57c00 100%)'
                            : 'rgba(255, 255, 255, 0.05)',
                          transform: 'translateX(4px)'
                        },
                        transition: 'all 0.3s ease-in-out'
                      }}
                    >
                      <ListItemIcon>
                        <panel.icon sx={{ color: activePanel === panel.id ? 'white' : `${panel.color}.main` as any }} />
                      </ListItemIcon>
                      <ListItemText
                        primary={panel.label}
                        secondary={panel.trend}
                        primaryTypographyProps={{
                          fontWeight: activePanel === panel.id ? 600 : 400,
                          color: activePanel === panel.id ? 'white' : 'text.primary'
                        }}
                        secondaryTypographyProps={{
                          fontSize: '0.75rem',
                          color: activePanel === panel.id ? 'rgba(255, 255, 255, 0.7)' : 'text.secondary'
                        }}
                      />
                    </ListItemButton>
                  </ListItem>
                </motion.div>
              ))}
            </List>

            <Divider sx={{ my: 2, borderColor: 'rgba(255, 255, 255, 0.1)' }} />

            {/* Enhanced Model Status Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <Card
                sx={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }}
              >
                <CardContent>
                  <Stack spacing={2}>
                    <Stack direction="row" spacing={2} alignItems="center">
                      <Avatar
                        sx={{
                          width: 32,
                          height: 32,
                          background: 'linear-gradient(135deg, #4caf50 0%, #2e7d32 100%)'
                        }}
                      >
                        <SmartToyIcon fontSize="small" />
                      </Avatar>
                      <Box>
                        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                          Active Model
                        </Typography>
                        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                          {activeModel}
                        </Typography>
                      </Box>
                    </Stack>

                    <Stack direction="row" spacing={1} alignItems="center">
                      <Box
                        sx={{
                          width: 8,
                          height: 8,
                          borderRadius: '50%',
                          background: '#4caf50',
                          animation: 'pulse 2s infinite'
                        }}
                      />
                      <Typography variant="caption" sx={{ color: '#4caf50' }}>
                        Online
                      </Typography>
                    </Stack>

                    <Box>
                      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                          Performance
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#4caf50', fontWeight: 600 }}>
                          Excellent
                        </Typography>
                      </Stack>
                      <Box
                        sx={{
                          width: '100%',
                          height: 4,
                          background: 'rgba(255, 255, 255, 0.1)',
                          borderRadius: 2,
                          overflow: 'hidden'
                        }}
                      >
                        <Box
                          sx={{
                            width: '85%',
                            height: '100%',
                            background: 'linear-gradient(90deg, #4caf50 0%, #1976d2 100%)',
                            borderRadius: 2
                          }}
                        />
                      </Box>
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </motion.div>
          </Box>
        </Drawer>

        {/* Main Content */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 3,
            mt: '120px', // Account for AppBar and Performance Monitor
            ml: sidebarOpen ? 0 : `-${drawerWidth}px`,
            transition: 'margin-left 0.3s ease-in-out',
            height: 'calc(100vh - 120px)',
            overflow: 'hidden'
          }}
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={activePanel}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.95 }}
              transition={{ duration: 0.4, ease: "easeInOut" }}
              style={{ height: '100%' }}
            >
              {activePanel === 'chat' && <MuiEnhancedChatPanel activeModel={activeModel} />}
              {activePanel === 'patterns' && <MuiPatternsPanel />}
              {activePanel === 'code' && (
                <Box sx={{ height: '100%', background: 'rgba(255, 255, 255, 0.02)', borderRadius: 3, p: 2 }}>
                  <CodeEditor />
                </Box>
              )}
              {activePanel === 'multimodal' && (
                <Box sx={{ height: '100%', background: 'rgba(255, 255, 255, 0.02)', borderRadius: 3, p: 2 }}>
                  <MultimodalPanel 
                    activeModel={activeModel}
                    onImageAnalysis={(image, analysis) => {
                      console.log('Image analyzed:', image.file.name, analysis)
                    }}
                  />
                </Box>
              )}
              {activePanel === 'learning' && (
                <Box sx={{ height: '100%', background: 'rgba(255, 255, 255, 0.02)', borderRadius: 3, p: 2 }}>
                  <LearningDashboard />
                </Box>
              )}
            </motion.div>
          </AnimatePresence>
        </Box>

        {/* Enhanced Floating Action Button */}
        <Tooltip title="Quick Actions">
          <Fab
            color="primary"
            sx={{
              position: 'fixed',
              bottom: 24,
              right: 24,
              background: 'linear-gradient(135deg, #1976d2 0%, #9c27b0 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #1565c0 0%, #7b1fa2 100%)',
                transform: 'scale(1.1) rotate(90deg)',
                boxShadow: '0 8px 25px rgba(25, 118, 210, 0.4)'
              },
              transition: 'all 0.3s ease-in-out'
            }}
          >
            <AddIcon />
          </Fab>
        </Tooltip>

        {/* Background Effects */}
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            zIndex: -1,
            pointerEvents: 'none',
            background: 'linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: '10%',
              left: '5%',
              width: '200px',
              height: '200px',
              background: 'radial-gradient(circle, rgba(25, 118, 210, 0.1) 0%, transparent 70%)',
              borderRadius: '50%',
              filter: 'blur(40px)',
              animation: 'float 6s ease-in-out infinite'
            },
            '&::after': {
              content: '""',
              position: 'absolute',
              bottom: '10%',
              right: '5%',
              width: '150px',
              height: '150px',
              background: 'radial-gradient(circle, rgba(156, 39, 176, 0.1) 0%, transparent 70%)',
              borderRadius: '50%',
              filter: 'blur(30px)',
              animation: 'float 8s ease-in-out infinite reverse'
            }
          }}
        />

        <style jsx global>{`
          @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-20px) rotate(5deg); }
          }
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
        `}</style>
      </Box>
      </ThemeProvider>
    </MuiPatternsProvider>
  )
}
