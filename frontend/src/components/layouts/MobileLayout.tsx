'use client'

import React from 'react'
import { 
  Box, 
  AppBar, 
  Toolbar, 
  Typography, 
  IconButton,
  Typography as MuiTypography,
  Chip,
  Avatar,
  Stack
} from '@mui/material'
import { motion } from 'framer-motion'
import { 
  Mic as MicIcon, 
  MicOff as MicOffIcon,
  Palette as PaletteIcon
} from '@mui/icons-material'

interface Panel {
  id: string
  label: string
  icon: React.ComponentType<any>
  color: string
  description: string
  trend: string
}

interface MobileLayoutProps {
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

export function MobileLayout({
  activePanel,
  setActivePanel,
  panels,
  isVoiceEnabled,
  setIsVoiceEnabled,
  darkMode,
  setDarkMode,
  activeModel,
  children
}: MobileLayoutProps) {
  return (
    <>
      {/* Mobile Header */}
      <AppBar 
        position="fixed" 
        sx={{ 
          background: 'rgba(0, 0, 0, 0.8)', 
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Typography variant="h6" noWrap component="div">
            Personal AI Assistant
          </Typography>
          
          <Stack direction="row" spacing={1} alignItems="center">
            <IconButton
              color="inherit"
              onClick={() => setIsVoiceEnabled(!isVoiceEnabled)}
              size="small"
            >
              {isVoiceEnabled ? <MicOffIcon /> : <MicIcon />}
            </IconButton>
            
            <IconButton
              color="inherit"
              onClick={() => setDarkMode(!darkMode)}
              size="small"
            >
              <PaletteIcon />
            </IconButton>
          </Stack>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          mt: '64px',
          height: 'calc(100vh - 64px - 72px)', // Account for header + bottom nav
          overflow: 'hidden'
        }}
      >
        {children}
      </Box>

      {/* Mobile Bottom Navigation */}
      <Box
        sx={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.9)',
          backdropFilter: 'blur(20px)',
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
          zIndex: 1300,
          padding: '8px 0',
          display: 'flex',
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
            <Box
              onClick={() => setActivePanel(panel.id)}
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 0.5,
                padding: '8px 12px',
                borderRadius: 2,
                cursor: 'pointer',
                backgroundColor: activePanel === panel.id ? 'rgba(25, 118, 210, 0.15)' : 'transparent',
                border: activePanel === panel.id ? '1px solid rgba(25, 118, 210, 0.3)' : '1px solid transparent',
                transition: 'all 0.2s ease',
                minWidth: '60px'
              }}
            >
              <Box sx={{ 
                fontSize: '1.4rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: activePanel === panel.id ? 'primary.main' : 'text.secondary'
              }}>
                {React.createElement(panel.icon, { fontSize: 'inherit' })}
              </Box>
              <MuiTypography 
                variant="caption" 
                sx={{ 
                  fontSize: '0.65rem',
                  fontWeight: activePanel === panel.id ? 600 : 400,
                  lineHeight: 1,
                  color: activePanel === panel.id ? 'primary.main' : 'text.secondary',
                  textAlign: 'center'
                }}
              >
                {panel.label.split(' ')[0]}
              </MuiTypography>
            </Box>
          </motion.div>
        ))}
      </Box>
    </>
  )
}
