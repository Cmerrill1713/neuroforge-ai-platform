"use client"

import React from 'react'
import { Box, Typography, Button, Paper } from '@mui/material'
import { ThemeProvider } from '@mui/material/styles'
import { aiStudioEnhancedTheme } from '@/theme/muiTheme'

export default function TestPage() {
  return (
    <ThemeProvider theme={aiStudioEnhancedTheme}>
      <Box sx={{ 
        minHeight: '100vh', 
        background: 'linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 3
      }}>
        <Paper sx={{ p: 4, textAlign: 'center', maxWidth: 600 }}>
          <Typography variant="h3" gutterBottom>
            🎉 Frontend Test Page
          </Typography>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            If you can see this page, the frontend is working!
          </Typography>
          <Typography variant="body1" sx={{ mb: 3 }}>
            This test page verifies that:
          </Typography>
          <Box component="ul" sx={{ textAlign: 'left', mb: 3 }}>
            <li>Next.js is running</li>
            <li>Material-UI is working</li>
            <li>Theme is applied</li>
            <li>Components are rendering</li>
          </Box>
          <Button 
            variant="contained" 
            size="large"
            onClick={() => alert('Button works!')}
          >
            Test Button
          </Button>
        </Paper>
      </Box>
    </ThemeProvider>
  )
}
