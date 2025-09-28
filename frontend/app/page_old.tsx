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
  TrendingUp as TrendingUpIcon,
  // Removed unused icons for cleaner imports
  Wifi as WifiIcon,
  WifiOff as WifiOffIcon
} from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'
import { aiStudioEnhancedTheme } from '@/theme/muiTheme'
import { MuiEnhancedChatPanel } from '@/components/MuiEnhancedChatPanel'
// Advanced and voice features integrated into main chat panel
import { CodeEditor } from '@/components/CodeEditor'
import { LearningDashboard } from '@/components/LearningDashboard'
import { MultimodalPanel } from '@/components/MultimodalPanel'
import { IntelligentModelSelector } from '@/components/IntelligentModelSelector'
import { RedisCacheIndicator } from '@/components/RedisCacheIndicator'
import { WebSocketStatus } from '@/components/WebSocketStatus'
import { AgentControlPanel } from '@/components/AgentControlPanel'
import { SelfOptimizationPanel } from "@/components/SelfOptimizationPanel"
// PerformanceMonitor removed for clean design

const drawerWidth = 280

export default function MuiEnhancedHome() {
  const [activeModel, setActiveModel] = useState('qwen2.5:7b')
  const [customModelNames, setCustomModelNames] = useState<Record<string, string>>({})
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
      label: 'AI Assistant', 
      icon: ChatIcon, 
      color: 'primary',
      description: 'Intelligent conversations with AI + Voice + Advanced features',
      trend: 'Personal AI Assistant'
    },
    { 
      id: 'agents', 
      label: 'AI Agents', 
      icon: SmartToyIcon, 
      color: 'secondary',
      description: 'Prompt-based intelligent agents for productivity and automation',
      trend: 'Smart Automation'
    },
    { 
      id: 'optimization', 
      label: 'Self-Optimization', 
      icon: TrendingUpIcon, 
      color: 'success', 
      description: 'AI-driven task automation and productivity enhancement', 
      trend: 'Autonomous Productivity' 
    },
    { 
      id: 'code', 
      label: 'Code Assistant', 
      icon: CodeIcon, 
      color: 'success',
      description: 'AI-assisted coding and development',
      trend: 'Smart Development'
    },
    { 
      id: 'multimodal', 
      label: 'Vision Assistant', 
      icon: ImageIcon, 
      color: 'secondary',
      description: 'Image analysis and visual understanding',
      trend: 'Visual Intelligence'
    },
    { 
      id: 'learning', 
      label: 'Learning Hub', 
      icon: AnalyticsIcon, 
      color: 'warning',
      description: 'Personal progress tracking & skill development',
      trend: 'Growth Analytics'
    }
  ]

  // Performance metrics removed for clean header design

  return (
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
          <Toolbar sx={{ 
            minHeight: '64px !important', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            px: { xs: 2, sm: 3, md: 4 }, // Fixed: Increased padding for better spacing
            py: 1 // Fixed: Added vertical padding for better alignment
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <IconButton
                color="inherit"
                aria-label="open drawer"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                edge="start"
                sx={{ 
                  mr: { xs: 1, sm: 2 }, 
                  alignSelf: 'center' 
                }}
              >
                <MenuIcon />
              </IconButton>

              <Avatar
                sx={{
                  mr: { xs: 1, sm: 2 },
                  background: 'linear-gradient(135deg, #1976d2 0%, #9c27b0 100%)',
                  width: { xs: 32, sm: 40 },
                  height: { xs: 32, sm: 40 },
                  alignSelf: 'center'
                }}
              >
                <SmartToyIcon />
              </Avatar>

              <Box sx={{ 
                flexGrow: 1, 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'flex-start',
                minHeight: '64px',
                flexWrap: 'wrap', // Fixed: Allow wrapping on smaller screens
                gap: { xs: 1, sm: 2 } // Fixed: Added gap for better spacing
              }}>
                <Typography
                  variant="h6"
                  sx={{
                    background: 'linear-gradient(135deg, #ffffff 0%, #e3f2fd 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                    fontWeight: 700,
                    alignSelf: 'center',
                    fontSize: { xs: '1rem', sm: '1.25rem', md: '1.5rem' } // Fixed: Responsive font size
                  }}
                >
                  Personal AI Assistant
                </Typography>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    color: 'rgba(255, 255, 255, 0.7)',
                    alignSelf: 'center',
                    display: { xs: 'none', sm: 'block' }, // Fixed: Hide subtitle on mobile to prevent overlap
                    fontSize: { sm: '0.75rem', md: '0.875rem' } // Fixed: Responsive font size
                  }}
                >
                  Your Intelligent Personal Assistant
                </Typography>
              </Box>
            </Box>

            <Stack 
              direction="row" 
              spacing={{ xs: 0.5, sm: 1, md: 1.5 }} 
              alignItems="center" 
              justifyContent="flex-end"
              sx={{ minHeight: '64px' }}
            >
              {/* Voice UI Toggle */}
              <Tooltip title={isVoiceEnabled ? 'Disable Voice' : 'Enable Voice'}>
                <IconButton
                  onClick={() => setIsVoiceEnabled(!isVoiceEnabled)}
                  sx={{
                    color: isVoiceEnabled ? '#4caf50' : 'rgba(255, 255, 255, 0.7)',
                    background: isVoiceEnabled ? 'rgba(76, 175, 80, 0.2)' : 'transparent',
                    border: isVoiceEnabled ? '1px solid rgba(76, 175, 80, 0.3)' : 'none',
                    alignSelf: 'center'
                  }}
                >
                  {isVoiceEnabled ? <MicIcon /> : <MicOffIcon />}
                </IconButton>
              </Tooltip>

              <IntelligentModelSelector 
                currentTask="general"
                onTaskChange={(task) => console.log('Task changed to:', task)}
              />

              {/* <RedisCacheIndicator /> */}
              {/* <WebSocketStatus /> */}

              <Tooltip title="Toggle Theme">
                <IconButton 
                  onClick={() => setDarkMode(!darkMode)} 
                  color="inherit"
                  sx={{ alignSelf: 'center' }}
                >
                  <PaletteIcon />
                </IconButton>
              </Tooltip>
            </Stack>
          </Toolbar>
        </AppBar>

        {/* Performance Monitor Removed - Clean Header Design */}

        {/* Mobile Overlay */}
        {sidebarOpen && (
          <Box
            sx={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
              zIndex: 1299,
              display: { xs: 'block', sm: 'none' } // Only show on mobile
            }}
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Desktop Sidebar */}
        <Drawer
          variant="persistent"
          anchor="left"
          open={sidebarOpen}
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            display: { xs: 'none', sm: 'block' }, // Hide on mobile
            '& .MuiDrawer-paper': {
              width: drawerWidth,
              boxSizing: 'border-box',
              background: 'rgba(255, 255, 255, 0.03)',
              backdropFilter: 'blur(20px)',
              borderRight: '1px solid rgba(255, 255, 255, 0.1)',
              mt: '64px',
              height: 'calc(100vh - 64px)',
              position: 'relative',
              zIndex: 'auto'
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
            mt: { xs: '64px', sm: '64px' }, // Account for AppBar on all sizes
            ml: { 
              xs: 0, // No left margin on mobile
              sm: sidebarOpen ? `${drawerWidth}px` : 0 // Desktop behavior
            },
            transition: 'margin-left 0.3s ease-in-out',
            height: { 
              xs: 'calc(100vh - 64px - 72px)', // Mobile: account for AppBar + bottom nav
              sm: 'calc(100vh - 64px)' // Desktop: account for AppBar only
            },
            overflow: 'hidden',
            width: { 
              xs: '100%', // Full width on mobile
              sm: sidebarOpen ? `calc(100% - ${drawerWidth}px)` : '100%' // Desktop responsive width
            }
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
        {activePanel === 'chat' && (
            <MuiEnhancedChatPanel 
                activeModel={activeModel} 
                customModelName={customModelNames[activeModel]}
                onSwitchPanel={setActivePanel}
            />
        )}
              
              {/* Advanced chat and voice features integrated into main chat panel */}
              
              {activePanel === 'code' && <CodeEditor />}
              
              {activePanel === 'multimodal' && (
                <MultimodalPanel 
                  activeModel={activeModel}
                  onImageAnalysis={(image, analysis) => {
                    console.log('Image analyzed:', image.file.name, analysis)
                  }}
                />
              )}
              
              {activePanel === 'learning' && <LearningDashboard />}

              {activePanel === 'agents' && <AgentControlPanel />}
              {activePanel === 'optimization' && <SelfOptimizationPanel />}
            </motion.div>
          </AnimatePresence>
        </Box>

        {/* Enhanced Floating Action Button */}
        <Tooltip title="Quick Actions">
          <Fab
            color="primary"
            sx={{
              position: 'fixed',
              bottom: { xs: 80, sm: 88 }, // Moved higher to avoid chat input area
              right: { xs: 16, sm: 24 },
              background: 'linear-gradient(135deg, #1976d2 0%, #9c27b0 100%)',
              width: { xs: 48, sm: 56 },
              height: { xs: 48, sm: 56 },
              zIndex: (theme) => theme.zIndex.speedDial - 1, // Lower z-index to avoid interfering with chat
              '&:hover': {
                background: 'linear-gradient(135deg, #1565c0 0%, #7b1fa2 100%)',
                transform: 'scale(1.1) rotate(90deg)',
                boxShadow: '0 8px 25px rgba(25, 118, 210, 0.4)'
              },
              transition: 'all 0.3s ease-in-out'
            }}
          >
            <AddIcon sx={{ fontSize: { xs: 20, sm: 24 } }} />
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

        {/* Mobile Bottom Navigation */}
        <Box
          sx={{
            display: { xs: 'flex', sm: 'none' },
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            backdropFilter: 'blur(20px)',
            borderTop: '1px solid rgba(255, 255, 255, 0.1)',
            zIndex: 1300,
            padding: '8px 0',
            justifyContent: 'space-around',
            alignItems: 'center'
          }}
        >
          {panels.map((panel) => (
            <motion.div
              key={`mobile-${panel.id}`}
              whileTap={{ scale: 0.95 }}
              transition={{ type: "spring", stiffness: 400, damping: 17 }}
            >
              <IconButton
                onClick={() => setActivePanel(panel.id)}
                sx={{
                  color: activePanel === panel.id ? 'primary.main' : 'text.secondary',
                  backgroundColor: activePanel === panel.id ? 'rgba(25, 118, 210, 0.1)' : 'transparent',
                  borderRadius: 2,
                  padding: '12px',
                  minWidth: '60px',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: 0.5
                }}
              >
                <Box sx={{ fontSize: '1.2rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  {React.createElement(panel.icon, { fontSize: 'inherit' })}
                </Box>
                <Typography 
                  variant="caption" 
                  sx={{ 
                    fontSize: '0.7rem',
                    fontWeight: activePanel === panel.id ? 600 : 400,
                    lineHeight: 1
                  }}
                >
                  {panel.label.split(' ')[0]}
                </Typography>
              </IconButton>
            </motion.div>
          ))}
        </Box>

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
  )
}
