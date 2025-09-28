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
  BottomNavigation,
  BottomNavigationAction,
  Paper
} from '@mui/material'
import { motion } from 'framer-motion'
import { 
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

interface CardBasedMobileLayoutProps {
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

export function CardBasedMobileLayout({
  activePanel,
  setActivePanel,
  panels,
  isVoiceEnabled,
  setIsVoiceEnabled,
  darkMode,
  setDarkMode,
  activeModel,
  children
}: CardBasedMobileLayoutProps) {
  const handleNavigationChange = (_: React.SyntheticEvent, newValue: string) => {
    setActivePanel(newValue)
  }

  return (
    <>
      {/* Mobile Header */}
      <AppBar position="fixed">
        <Toolbar sx={{ justifyContent: 'space-between', px: 2 }}>
          <Typography variant="h6" noWrap component="div">
            AI Assistant
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
          height: 'calc(100vh - 64px - 80px)', // Account for header + bottom nav
          overflow: 'auto',
          pb: 2
        }}
      >
        {children}
      </Box>

      {/* Mobile Bottom Navigation */}
      <Paper 
        sx={{ 
          position: 'fixed', 
          bottom: 0, 
          left: 0, 
          right: 0, 
          zIndex: 1300,
          borderTop: '1px solid',
          borderColor: 'divider'
        }} 
        elevation={8}
      >
        <BottomNavigation
          value={activePanel}
          onChange={handleNavigationChange}
          sx={{
            height: 80,
            backgroundColor: 'background.paper',
            '& .MuiBottomNavigationAction-root': {
              minWidth: 'auto',
              paddingTop: 1,
              '&.Mui-selected': {
                color: 'primary.main',
              },
            },
          }}
        >
          {panels.map((panel) => (
            <BottomNavigationAction
              key={panel.id}
              label={panel.label.split(' ')[0]}
              value={panel.id}
              icon={
                <motion.div
                  animate={{ scale: activePanel === panel.id ? 1.1 : 1 }}
                  transition={{ type: "spring", stiffness: 400, damping: 17 }}
                >
                  <Avatar
                    sx={{
                      width: 32,
                      height: 32,
                      backgroundColor: activePanel === panel.id ? 'primary.main' : 'transparent',
                      color: activePanel === panel.id ? 'white' : 'text.secondary',
                      border: activePanel === panel.id ? 'none' : '2px solid',
                      borderColor: 'text.secondary'
                    }}
                  >
                    {React.createElement(panel.icon, { fontSize: 'small' })}
                  </Avatar>
                </motion.div>
              }
              sx={{
                '& .MuiBottomNavigationAction-label': {
                  fontSize: '0.7rem',
                  fontWeight: activePanel === panel.id ? 600 : 400,
                }
              }}
            />
          ))}
        </BottomNavigation>
      </Paper>
    </>
  )
}
