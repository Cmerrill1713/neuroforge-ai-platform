'use client'

import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Avatar,
  LinearProgress,
  Tooltip,
  IconButton,
  Stack,
  Divider,
  Alert,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material'
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Palette as PaletteIcon,
  Psychology as PsychologyIcon,
  Visibility as VisibilityIcon,
  Accessibility as AccessibilityIcon,
  Star as StarIcon,
  Insights as InsightsIcon,
  Timeline as TimelineIcon,
  Compare as CompareIcon,
  Refresh as RefreshIcon,
  Share as ShareIcon
} from '@mui/icons-material'
import { motion } from 'framer-motion'

interface ColorTrend {
  name: string
  color: string
  category: string
  trend: 'rising' | 'stable' | 'declining'
  change: number
  usage: number
  emotional: {
    calm: number
    energetic: number
    professional: number
    creative: number
  }
  accessibility: number
  marketShare: number
  year: number
  description: string
}

interface TrendAnalysis {
  overallTrend: 'up' | 'stable' | 'down'
  topRising: ColorTrend[]
  topDeclining: ColorTrend[]
  categoryBreakdown: Record<string, number>
  emotionalAnalysis: {
    dominant: string
    distribution: Record<string, number>
  }
  accessibilityTrend: number
  marketInsights: string[]
}

// 2025 Color Trends Data
const colorTrendsData: ColorTrend[] = [
  {
    name: 'Peach Fuzz',
    color: '#FFB4A2',
    category: 'Warm Neutrals',
    trend: 'rising',
    change: 95,
    usage: 85,
    emotional: { calm: 85, energetic: 45, professional: 60, creative: 75 },
    accessibility: 88,
    marketShare: 25,
    year: 2025,
    description: 'Pantone Color of the Year 2025 - embodies comfort and connection'
  },
  {
    name: 'Digital Wellness Blue',
    color: '#64B5F6',
    category: 'Tech Wellness',
    trend: 'rising',
    change: 78,
    usage: 72,
    emotional: { calm: 90, energetic: 40, professional: 95, creative: 55 },
    accessibility: 94,
    marketShare: 18,
    year: 2025,
    description: 'Calming blues designed to reduce digital eye strain'
  },
  {
    name: 'Earth Regenerative Green',
    color: '#4CAF50',
    category: 'Sustainable',
    trend: 'rising',
    change: 65,
    usage: 68,
    emotional: { calm: 80, energetic: 50, professional: 70, creative: 65 },
    accessibility: 90,
    marketShare: 15,
    year: 2025,
    description: 'Rich greens symbolizing environmental renewal'
  },
  {
    name: 'Creamy Pastel Pink',
    color: '#F8BBD9',
    category: 'Soft & Calm',
    trend: 'rising',
    change: 58,
    usage: 62,
    emotional: { calm: 95, energetic: 30, professional: 50, creative: 85 },
    accessibility: 82,
    marketShare: 12,
    year: 2025,
    description: 'Soft pastels bringing calm and optimism'
  },
  {
    name: 'Nostalgic Futurism Purple',
    color: '#9C27B0',
    category: 'Retro-Future',
    trend: 'stable',
    change: 12,
    usage: 45,
    emotional: { calm: 60, energetic: 75, professional: 45, creative: 95 },
    accessibility: 87,
    marketShare: 8,
    year: 2025,
    description: 'Retrofuturistic elements with contemporary sensibilities'
  },
  {
    name: 'High-Tech Metallic',
    color: '#607D8B',
    category: 'Futuristic',
    trend: 'stable',
    change: 8,
    usage: 38,
    emotional: { calm: 70, energetic: 40, professional: 90, creative: 60 },
    accessibility: 89,
    marketShare: 6,
    year: 2025,
    description: 'Metallics and chrome for sleek, modern aesthetics'
  },
  {
    name: 'Vibrant Neon Electric',
    color: '#00BCD4',
    category: 'Bold Energy',
    trend: 'declining',
    change: -15,
    usage: 28,
    emotional: { calm: 20, energetic: 95, professional: 30, creative: 90 },
    accessibility: 91,
    marketShare: 4,
    year: 2025,
    description: 'Electric neons for high-energy interfaces'
  },
  {
    name: 'Soft Butter Yellow',
    color: '#FFF176',
    category: 'Warm Neutral',
    trend: 'rising',
    change: 42,
    usage: 55,
    emotional: { calm: 75, energetic: 60, professional: 55, creative: 70 },
    accessibility: 88,
    marketShare: 10,
    year: 2025,
    description: 'Light yellows as versatile alternatives to whites'
  }
]

export function ColorTrendAnalysis() {
  const [analysis, setAnalysis] = useState<TrendAnalysis | null>(null)
  const [selectedTrend, setSelectedTrend] = useState<ColorTrend | null>(null)
  const [showDetails, setShowDetails] = useState(false)
  const [timeframe, setTimeframe] = useState<'2024' | '2025' | '2026'>('2025')

  useEffect(() => {
    generateAnalysis()
  }, [timeframe])

  const generateAnalysis = () => {
    const rising = colorTrendsData.filter(t => t.trend === 'rising')
    const declining = colorTrendsData.filter(t => t.trend === 'declining')
    
    const categoryBreakdown = colorTrendsData.reduce((acc, trend) => {
      acc[trend.category] = (acc[trend.category] || 0) + trend.marketShare
      return acc
    }, {} as Record<string, number>)
    
    const emotionalDistribution = colorTrendsData.reduce((acc, trend) => {
      Object.entries(trend.emotional).forEach(([emotion, value]) => {
        acc[emotion] = (acc[emotion] || 0) + value
      })
      return acc
    }, {} as Record<string, number>)
    
    const dominantEmotion = Object.entries(emotionalDistribution).reduce((a, b) => 
      emotionalDistribution[a[0]] > emotionalDistribution[b[0]] ? a : b
    )[0]
    
    const avgAccessibility = colorTrendsData.reduce((sum, trend) => sum + trend.accessibility, 0) / colorTrendsData.length
    
    const insights = [
      'Peach Fuzz leads 2025 trends with 95% growth',
      'Digital wellness colors show strong adoption',
      'Sustainability drives green color popularity',
      'Accessibility scores average 88% across trends',
      'Soft pastels gaining momentum in professional settings'
    ]
    
    setAnalysis({
      overallTrend: rising.length > declining.length ? 'up' : declining.length > rising.length ? 'down' : 'stable',
      topRising: rising.sort((a, b) => b.change - a.change).slice(0, 3),
      topDeclining: declining.sort((a, b) => a.change - b.change).slice(0, 3),
      categoryBreakdown,
      emotionalAnalysis: {
        dominant: dominantEmotion,
        distribution: emotionalDistribution
      },
      accessibilityTrend: avgAccessibility,
      marketInsights: insights
    })
  }

  const getTrendIcon = (trend: 'rising' | 'stable' | 'declining') => {
    switch (trend) {
      case 'rising': return <TrendingUpIcon color="success" />
      case 'stable': return <TrendingUpIcon color="action" sx={{ transform: 'rotate(90deg)' }} />
      case 'declining': return <TrendingDownIcon color="error" />
    }
  }

  const getTrendColor = (trend: 'rising' | 'stable' | 'declining') => {
    switch (trend) {
      case 'rising': return 'success'
      case 'stable': return 'warning'
      case 'declining': return 'error'
    }
  }

  return (
    <Box>
      <Typography variant="h6" sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
        <InsightsIcon color="primary" />
        2025 Color Trend Analysis
      </Typography>

      {/* Overall Trend Summary */}
      {analysis && (
        <Card sx={{ mb: 3, background: 'rgba(255, 255, 255, 0.05)' }}>
          <CardContent>
            <Grid container spacing={3}>
              <div style={{ width: '100%', padding: '8px' }}>
                <Box sx={{ textAlign: 'center' }}>
                  <Avatar sx={{ bgcolor: analysis.overallTrend === 'up' ? 'success.main' : analysis.overallTrend === 'down' ? 'error.main' : 'warning.main', mx: 'auto', mb: 2, width: 64, height: 64 }}>
                    {analysis.overallTrend === 'up' ? <TrendingUpIcon sx={{ fontSize: 32 }} /> : 
                     analysis.overallTrend === 'down' ? <TrendingDownIcon sx={{ fontSize: 32 }} /> :
                     <TimelineIcon sx={{ fontSize: 32 }} />}
                  </Avatar>
                  <Typography variant="h6" sx={{ mb: 1 }}>
                    Overall Trend: {analysis.overallTrend.toUpperCase()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {analysis.overallTrend === 'up' ? 'Colors trending upward in 2025' : 
                     analysis.overallTrend === 'down' ? 'Mixed signals with some decline' :
                     'Stable color market with steady growth'}
                  </Typography>
                </Box>
              </div>
              
              <div style={{ width: '100%', padding: '8px' }}>
                <Typography variant="subtitle1" sx={{ mb: 2 }}>Top Rising Colors</Typography>
                <Stack spacing={1}>
                  {analysis.topRising.map((trend, index) => (
                    <Box key={trend.name} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box sx={{ width: 16, height: 16, background: trend.color, borderRadius: '50%' }} />
                      <Typography variant="body2" sx={{ flex: 1 }}>{trend.name}</Typography>
                      <Chip label={`+${trend.change}%`} size="small" color="success" />
                    </Box>
                  ))}
                </Stack>
              </div>
              
              <div style={{ width: '100%', padding: '8px' }}>
                <Typography variant="subtitle1" sx={{ mb: 2 }}>Market Insights</Typography>
                <Stack spacing={1}>
                  {analysis.marketInsights.slice(0, 3).map((insight, index) => (
                    <Alert key={index} severity="info" sx={{ py: 0.5 }}>
                      <Typography variant="caption">{insight}</Typography>
                    </Alert>
                  ))}
                </Stack>
              </div>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Category Breakdown */}
      {analysis && (
        <Card sx={{ mb: 3, background: 'rgba(255, 255, 255, 0.05)' }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
              <PaletteIcon color="primary" />
              Category Market Share
            </Typography>
            
            <Grid container spacing={2}>
              {Object.entries(analysis.categoryBreakdown).map(([category, share]) => (
                <div key={category} style={{ width: '100%', padding: '8px' }}>
                  <Box sx={{ p: 2, background: 'rgba(255, 255, 255, 0.05)', borderRadius: 2 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>{category}</Typography>
                    <LinearProgress 
                      variant="determinate" 
                      value={share} 
                      sx={{ height: 8, borderRadius: 4, mb: 1 }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {share}% market share
                    </Typography>
                  </Box>
                </div>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Color Trends Grid */}
      <Grid container spacing={2}>
        {colorTrendsData.map((trend, index) => (
          <div key={trend.name} style={{ width: '100%', padding: '8px' }}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card
                sx={{
                  cursor: 'pointer',
                  '&:hover': { transform: 'translateY(-4px)' },
                  transition: 'transform 0.2s'
                }}
                onClick={() => {
                  setSelectedTrend(trend)
                  setShowDetails(true)
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <Avatar sx={{ bgcolor: trend.color, width: 48, height: 48 }}>
                      <PaletteIcon />
                    </Avatar>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {trend.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {trend.category}
                      </Typography>
                    </Box>
                    <Box sx={{ textAlign: 'center' }}>
                      {getTrendIcon(trend.trend)}
                      <Typography variant="caption" display="block">
                        {trend.change > 0 ? '+' : ''}{trend.change}%
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                    <Chip
                      label={`Usage: ${trend.usage}%`}
                      size="small"
                      color="primary"
                    />
                    <Chip
                      label={`Access: ${trend.accessibility}%`}
                      size="small"
                      color="success"
                    />
                    <Chip
                      label={`Market: ${trend.marketShare}%`}
                      size="small"
                      variant="outlined"
                    />
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {trend.description}
                  </Typography>
                  
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="caption" color="text.secondary">Emotional Profile</Typography>
                      <LinearProgress
                        variant="determinate"
                        value={trend.emotional.calm}
                        sx={{ height: 4, borderRadius: 2, mb: 0.5 }}
                      />
                      <Typography variant="caption">Calm: {trend.emotional.calm}%</Typography>
                    </Box>
                    <Box sx={{ flex: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={trend.emotional.energetic}
                        sx={{ height: 4, borderRadius: 2, mb: 0.5 }}
                      />
                      <Typography variant="caption">Energy: {trend.emotional.energetic}%</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        ))}
      </Grid>

      {/* Trend Details Dialog */}
      <Dialog open={showDetails} onClose={() => setShowDetails(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ bgcolor: selectedTrend?.color }}>
              <PaletteIcon />
            </Avatar>
            <Box>
              <Typography variant="h6">{selectedTrend?.name}</Typography>
              <Typography variant="caption" color="text.secondary">
                {selectedTrend?.category} • {selectedTrend?.year}
              </Typography>
            </Box>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          {selectedTrend && (
            <Grid container spacing={3}>
              <div style={{ width: '100%', padding: '8px' }}>
                <Typography variant="subtitle1" sx={{ mb: 2 }}>Trend Analysis</Typography>
                <Stack spacing={2}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography>Trend Direction</Typography>
                    <Chip 
                      label={selectedTrend.trend} 
                      color={getTrendColor(selectedTrend.trend)}
                      size="small"
                    />
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography>Change Rate</Typography>
                    <Typography variant="body2" color={selectedTrend.change > 0 ? 'success.main' : 'error.main'}>
                      {selectedTrend.change > 0 ? '+' : ''}{selectedTrend.change}%
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography>Market Share</Typography>
                    <Typography variant="body2">{selectedTrend.marketShare}%</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography>Usage Rate</Typography>
                    <Typography variant="body2">{selectedTrend.usage}%</Typography>
                  </Box>
                </Stack>
              </div>
              
              <div style={{ width: '100%', padding: '8px' }}>
                <Typography variant="subtitle1" sx={{ mb: 2 }}>Emotional Profile</Typography>
                <Stack spacing={2}>
                  {Object.entries(selectedTrend.emotional).map(([emotion, value]) => (
                    <Box key={emotion}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                          {emotion}
                        </Typography>
                        <Typography variant="body2">{value}%</Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={value}
                        sx={{ height: 6, borderRadius: 3 }}
                      />
                    </Box>
                  ))}
                </Stack>
              </div>
              
              <div style={{ width: '100%', padding: '8px' }}>
                <Typography variant="subtitle1" sx={{ mb: 2 }}>Description</Typography>
                <Typography variant="body2" color="text.secondary">
                  {selectedTrend.description}
                </Typography>
              </div>
            </Grid>
          )}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setShowDetails(false)}>Close</Button>
          <Button variant="contained" startIcon={<ShareIcon />}>
            Share Analysis
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
