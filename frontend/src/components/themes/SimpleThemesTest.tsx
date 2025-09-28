'use client'

import React from 'react'
import { Box, Typography, Card, CardContent, Button } from '@mui/material'
import { Palette as PaletteIcon } from '@mui/icons-material'

export function SimpleThemesTest() {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
        <PaletteIcon color="primary" />
        2025 Color Optimization System
      </Typography>
      
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            🎨 Peach Fuzz - Pantone Color of the Year 2025
          </Typography>
          <Typography variant="body1" sx={{ mb: 2 }}>
            The soft, warm peach color that embodies comfort and connection in 2025.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <Box sx={{ width: 60, height: 60, background: '#FFB4A2', borderRadius: 2, border: '2px solid rgba(255, 255, 255, 0.2)' }} />
            <Box sx={{ width: 60, height: 60, background: '#FF8A65', borderRadius: 2, border: '2px solid rgba(255, 255, 255, 0.2)' }} />
            <Box sx={{ width: 60, height: 60, background: '#FF7043', borderRadius: 2, border: '2px solid rgba(255, 255, 255, 0.2)' }} />
          </Box>
          <Button variant="contained" sx={{ background: '#FFB4A2' }}>
            Apply Peach Fuzz Theme
          </Button>
        </CardContent>
      </Card>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            🤖 AI-Powered Color Optimization
          </Typography>
          <Typography variant="body1" sx={{ mb: 2 }}>
            Advanced algorithms for perfect color harmony, accessibility, and trend alignment.
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <Button variant="outlined" size="small">Neural Harmony</Button>
            <Button variant="outlined" size="small">WCAG Pro</Button>
            <Button variant="outlined" size="small">Trend Fusion</Button>
            <Button variant="outlined" size="small">Emotional AI</Button>
          </Box>
          <Button variant="contained" color="primary">
            Optimize Colors
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            📊 2025 Color Trends Analysis
          </Typography>
          <Typography variant="body1" sx={{ mb: 2 }}>
            Market insights and emotional profiles for trending colors.
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <Button variant="outlined" size="small">Digital Wellness</Button>
            <Button variant="outlined" size="small">Earth Regenerative</Button>
            <Button variant="outlined" size="small">Creamy Pastels</Button>
            <Button variant="outlined" size="small">Retro-Futurism</Button>
          </Box>
          <Button variant="contained" color="secondary">
            View Analysis
          </Button>
        </CardContent>
      </Card>
    </Box>
  )
}
