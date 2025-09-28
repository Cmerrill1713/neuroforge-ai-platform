'use client'

import React from 'react'
import { Box, Typography, Card, CardContent } from '@mui/material'

export function DynamicThemeGenerator() {
  return (
    <Card sx={{ mb: 3, background: 'rgba(255, 255, 255, 0.05)' }}>
      <CardContent>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Dynamic Theme Generator
        </Typography>
        <Typography variant="body2" color="text.secondary">
          This component is temporarily simplified for testing. The full theme generator 
          with AI-powered color palette generation, accessibility scoring, and trend analysis 
          will be restored after resolving syntax issues.
        </Typography>
      </CardContent>
    </Card>
  )
}