'use client'

import React from 'react'
import { 
  Box, 
  Drawer, 
  AppBar, 
  Toolbar, 
  Typography, 
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Chip,
  Avatar,
  Stack
} from '@mui/material'
import { motion } from 'framer-motion'
import { 
  Menu as MenuIcon, 
  Mic as MicIcon, 
  MicOff as MicOffIcon,
  Palette as PaletteIcon,
  Close as CloseIcon
} from '@mui/icons-material'

interface Panel {
  id: string
  label: string
  icon: React.ComponentType<any>
  color: string
  description: string
  trend: string
}

interface DesktopLayoutProps {
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

const drawerWidth = 280

export function DesktopLayout({
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
}: DesktopLayoutProps) {
  return (
    <>
      {/* Header */}
      <AppBar 
        position="fixed" 
        sx={{ 
          background: 'rgba(0, 0, 0, 0.8)', 
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
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
              icon={<Avatar sx={{ width: 16, height: 16 }}>AI</Avatar>}
              label={`${activeModel} • ${isVoiceEnabled ? 'Voice On' : 'Voice Off'}`}
              size="small"
              sx={{ 
                background: 'rgba(255, 255, 255, 0.1)',
                color: 'white'
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
                        : panel.color === 'warning' ? 'linear-gradient(135deg, #ff9800 0%, #f57c00 100%)'
                        : panel.color === 'error' ? 'linear-gradient(135deg, #f44336 0%, #d32f2f 100%)'
                        : panel.color === 'info' ? 'linear-gradient(135deg, #2196f3 0%, #1976d2 100%)'
                        : 'rgba(255, 255, 255, 0.1)'
                        : 'transparent',
                      color: activePanel === panel.id ? 'white' : 'text.primary',
                      '&:hover': {
                        background: activePanel === panel.id
                          ? 'rgba(255, 255, 255, 0.2)'
                          : 'rgba(255, 255, 255, 0.05)'
                      }
                    }}
                  >
                    <ListItemIcon sx={{ color: 'inherit', minWidth: 40 }}>
                      {React.createElement(panel.icon, { fontSize: 'small' })}
                    </ListItemIcon>
                    <ListItemText 
                      primary={panel.label}
                      secondary={panel.trend}
                      primaryTypographyProps={{ fontSize: '0.9rem', fontWeight: 500 }}
                      secondaryTypographyProps={{ fontSize: '0.75rem', sx: { opacity: 0.8 } }}
                    />
                  </ListItemButton>
                </ListItem>
              </motion.div>
            ))}
          </List>
          
          <Divider sx={{ my: 2, opacity: 0.3 }} />
          
          <Box sx={{ p: 2 }}>
            <Stack spacing={2}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Avatar sx={{ width: 24, height: 24, bgcolor: 'success.main' }}>
                  AI
                </Avatar>
                <Box>
                  <Typography variant="subtitle2" sx={{ fontSize: '0.8rem' }}>
                    Active Model
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                    {activeModel}
                  </Typography>
                </Box>
              </Box>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip 
                  label="Online" 
                  size="small" 
                  color="success" 
                  sx={{ fontSize: '0.7rem' }}
                />
                <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                  Performance: Excellent
                </Typography>
              </Box>
            </Stack>
          </Box>
        </Box>
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          mt: '64px',
          ml: sidebarOpen ? `${drawerWidth}px` : 0,
          transition: 'margin-left 0.3s ease-in-out',
          height: 'calc(100vh - 64px)',
          overflow: 'hidden'
        }}
      >
        {children}
      </Box>
    </>
  )
}
