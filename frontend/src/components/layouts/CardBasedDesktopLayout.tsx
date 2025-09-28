'use client'

import React from 'react'
import { 
  Box, 
  AppBar, 
  Toolbar, 
  Typography, 
  IconButton,
  Card,
  CardContent,
  Stack,
  Chip,
  Avatar,
  Drawer,
  List,
  ListItem
} from '@mui/material'
import { motion } from 'framer-motion'
import { 
  Menu as MenuIcon, 
  Mic as MicIcon, 
  MicOff as MicOffIcon,
  Palette as PaletteIcon
} from '@mui/icons-material'
import { NavigationCard } from '../navigation/NavigationCard'

interface Panel {
  id: string
  label: string
  icon: React.ComponentType<any>
  color: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info'
  description: string
  trend: string
}

interface CardBasedDesktopLayoutProps {
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
  activePanel: string
  setActivePanel: (panel: string) => void
  panels: Panel[]
  isVoiceEnabled: boolean
  setIsVoiceEnabled: (enabled: boolean) => void
  darkMode: boolean
  setDarkMode: (dark: boolean) => void
  activeModel: string
  children: React.ReactNode
}

const drawerWidth = 320

export function CardBasedDesktopLayout({
  sidebarOpen,
  setSidebarOpen,
  activePanel,
  setActivePanel,
  panels,
  isVoiceEnabled,
  setIsVoiceEnabled,
  darkMode,
  setDarkMode,
  activeModel,
  children
}: CardBasedDesktopLayoutProps) {
  return (
    <>
      {/* Header */}
      <AppBar position="fixed">
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="toggle sidebar"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            edge="start"
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Personal AI Assistant
          </Typography>
          
          <Stack direction="row" spacing={2} alignItems="center">
            <IconButton
              color="inherit"
              onClick={() => setIsVoiceEnabled(!isVoiceEnabled)}
            >
              {isVoiceEnabled ? <MicOffIcon /> : <MicIcon />}
            </IconButton>
            
            <Chip
              icon={<Avatar sx={{ width: 20, height: 20, fontSize: '0.7rem' }}>AI</Avatar>}
              label={`${activeModel} • ${isVoiceEnabled ? 'Voice On' : 'Voice Off'}`}
              size="small"
              variant="outlined"
              sx={{ 
                borderColor: 'rgba(255, 255, 255, 0.3)',
                color: 'inherit'
              }}
            />
            
            <IconButton
              color="inherit"
              onClick={() => setDarkMode(!darkMode)}
            >
              <PaletteIcon />
            </IconButton>
          </Stack>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
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
            mt: '64px',
            height: 'calc(100vh - 64px)',
            position: 'relative',
            zIndex: 'auto',
            border: 'none',
            background: 'transparent'
          }
        }}
      >
        <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
          <Stack spacing={2}>
            {panels.map((panel, index) => (
              <motion.div
                key={panel.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <NavigationCard
                  {...panel}
                  isActive={activePanel === panel.id}
                  onClick={() => setActivePanel(panel.id)}
                  variant="desktop"
                />
              </motion.div>
            ))}
          </Stack>
          
          {/* Status Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: panels.length * 0.1 }}
          >
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Stack spacing={2}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Avatar sx={{ bgcolor: 'success.main' }}>
                      AI
                    </Avatar>
                    <Box>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        Active Model
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {activeModel}
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Stack direction="row" spacing={1}>
                    <Chip 
                      label="Online" 
                      size="small" 
                      color="success"
                      variant="outlined"
                    />
                    <Chip 
                      label="Performance: Excellent" 
                      size="small" 
                      variant="outlined"
                    />
                  </Stack>
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
          mt: '64px',
          ml: sidebarOpen ? `${drawerWidth}px` : 0,
          transition: 'margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          height: 'calc(100vh - 64px)',
          overflow: 'hidden'
        }}
      >
        {children}
      </Box>
    </>
  )
}
