'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Box, Card, CardContent, Typography, Chip, IconButton, Tooltip } from '@mui/material'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  AutoAwesome as AutoAwesomeIcon,
  TrendingUp as TrendingUpIcon,
  Psychology as PsychologyIcon,
  Insights as InsightsIcon
} from '@mui/icons-material'

interface UsagePattern {
  panelId: string
  frequency: number
  duration: number
  lastUsed: number
  timeOfDay: number[]
  dayOfWeek: number[]
}

interface AdaptiveLayoutEngineProps {
  panels: any[]
  activePanel: string
  onPanelChange: (panelId: string) => void
}

export function AdaptiveLayoutEngine({ panels, activePanel, onPanelChange }: AdaptiveLayoutEngineProps) {
  const [usagePatterns, setUsagePatterns] = useState<UsagePattern[]>([])
  const [smartSuggestions, setSmartSuggestions] = useState<any[]>([])
  const [isLearning, setIsLearning] = useState(true)
  const [insights, setInsights] = useState<string[]>([])
  const sessionStartTime = useRef(Date.now())

  // Track user behavior
  useEffect(() => {
    const trackUsage = () => {
      const now = Date.now()
      const timeOfDay = new Date().getHours()
      const dayOfWeek = new Date().getDay()
      
      setUsagePatterns(prev => {
        const existing = prev.find(p => p.panelId === activePanel)
        if (existing) {
          return prev.map(p => 
            p.panelId === activePanel 
              ? {
                  ...p,
                  frequency: p.frequency + 1,
                  duration: p.duration + (now - p.lastUsed),
                  lastUsed: now,
                  timeOfDay: [...p.timeOfDay, timeOfDay],
                  dayOfWeek: [...p.dayOfWeek, dayOfWeek]
                }
              : p
          )
        } else {
          return [...prev, {
            panelId: activePanel,
            frequency: 1,
            duration: 0,
            lastUsed: now,
            timeOfDay: [timeOfDay],
            dayOfWeek: [dayOfWeek]
          }]
        }
      })
    }

    trackUsage()
  }, [activePanel])

  // Generate smart suggestions based on patterns
  useEffect(() => {
    const generateSuggestions = () => {
      const now = new Date()
      const currentHour = now.getHours()
      const currentDay = now.getDay()
      
      const suggestions = usagePatterns
        .map(pattern => {
          const panel = panels.find(p => p.id === pattern.panelId)
          if (!panel) return null

          // Calculate relevance score
          let score = pattern.frequency * 0.4
          
          // Time-based scoring
          const avgTimeOfDay = pattern.timeOfDay.reduce((a, b) => a + b, 0) / pattern.timeOfDay.length
          const timeDiff = Math.abs(currentHour - avgTimeOfDay)
          score += (24 - timeDiff) * 0.3
          
          // Day-based scoring
          const dayMatches = pattern.dayOfWeek.filter(d => d === currentDay).length
          score += dayMatches * 0.3

          return {
            ...panel,
            score,
            reason: generateReason(pattern, currentHour, currentDay),
            confidence: Math.min(score / 10, 1)
          }
        })
        .filter(Boolean)
        .sort((a, b) => b.score - a.score)
        .slice(0, 3)

      setSmartSuggestions(suggestions)
    }

    if (usagePatterns.length > 0) {
      generateSuggestions()
    }
  }, [usagePatterns, panels])

  // Generate insights
  useEffect(() => {
    const generateInsights = () => {
      const totalUsage = usagePatterns.reduce((sum, p) => sum + p.frequency, 0)
      const mostUsed = usagePatterns.reduce((max, p) => p.frequency > max.frequency ? p : max, usagePatterns[0])
      const avgSessionTime = usagePatterns.reduce((sum, p) => sum + p.duration, 0) / usagePatterns.length

      const newInsights = []
      
      if (mostUsed) {
        const panel = panels.find(p => p.id === mostUsed.panelId)
        newInsights.push(`You use ${panel?.label} most frequently (${mostUsed.frequency} times)`)
      }

      if (avgSessionTime > 300000) { // 5 minutes
        newInsights.push(`You spend an average of ${Math.round(avgSessionTime / 60000)} minutes per session`)
      }

      if (totalUsage > 10) {
        newInsights.push(`You're a power user! ${totalUsage} interactions today`)
      }

      setInsights(newInsights)
    }

    if (usagePatterns.length > 0) {
      generateInsights()
    }
  }, [usagePatterns, panels])

  const generateReason = (pattern: UsagePattern, currentHour: number, currentDay: number) => {
    const avgTime = pattern.timeOfDay.reduce((a, b) => a + b, 0) / pattern.timeOfDay.length
    const dayMatches = pattern.dayOfWeek.filter(d => d === currentDay).length
    
    if (dayMatches > 0 && Math.abs(currentHour - avgTime) < 2) {
      return `You usually use this around this time`
    } else if (pattern.frequency > 5) {
      return `Your most used feature`
    } else {
      return `Based on your usage patterns`
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence > 0.8) return 'success'
    if (confidence > 0.6) return 'warning'
    return 'default'
  }

  return (
    <Box sx={{ 
      p: 3, 
      background: 'linear-gradient(135deg, rgba(25, 118, 210, 0.2) 0%, rgba(156, 39, 176, 0.2) 100%)',
      backdropFilter: 'blur(10px)',
      borderRadius: 3,
      border: '1px solid rgba(255, 255, 255, 0.1)',
      mb: 2,
      cursor: 'pointer',
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      '&:hover': {
        transform: 'translateY(-1px)',
        background: 'linear-gradient(135deg, rgba(25, 118, 210, 0.3) 0%, rgba(156, 39, 176, 0.3) 100%)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)',
      }
    }}>
      <Typography variant="h6" sx={{ 
        mb: 2, 
        display: 'flex', 
        alignItems: 'center', 
        gap: 1,
        fontSize: '1rem',
        fontWeight: 600,
        color: 'text.primary'
      }}>
        <AutoAwesomeIcon color="primary" />
        AI-Powered Smart Layout
        <Chip 
          label={isLearning ? "Learning" : "Ready"} 
          size="small" 
          color={isLearning ? "warning" : "success"}
          sx={{ ml: 1 }}
        />
      </Typography>

      {/* Smart Suggestions */}
      {smartSuggestions.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1, color: 'white' }}>
            <TrendingUpIcon fontSize="small" />
            Suggested for you
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {smartSuggestions.map((suggestion, index) => (
              <motion.div
                key={suggestion.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Tooltip title={suggestion.reason}>
                  <Chip
                    label={suggestion.label}
                    color={getConfidenceColor(suggestion.confidence)}
                    onClick={() => onPanelChange(suggestion.id)}
                    sx={{ cursor: 'pointer' }}
                    icon={<suggestion.icon />}
                  />
                </Tooltip>
              </motion.div>
            ))}
          </Box>
        </Box>
      )}

      {/* Insights */}
      {insights.length > 0 && (
        <Card sx={{ mb: 2, background: 'rgba(255, 255, 255, 0.05)' }}>
          <CardContent sx={{ p: 2 }}>
            <Typography variant="subtitle2" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1, color: 'white' }}>
              <InsightsIcon fontSize="small" />
              Usage Insights
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {insights.map((insight, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                    • {insight}
                  </Typography>
                </motion.div>
              ))}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Learning Progress */}
      <Card sx={{ background: 'rgba(255, 255, 255, 0.05)' }}>
        <CardContent sx={{ p: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1, color: 'white' }}>
            <PsychologyIcon fontSize="small" />
            AI Learning Progress
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ flex: 1 }}>
              <Box sx={{ 
                width: '100%', 
                height: 8, 
                background: 'rgba(255, 255, 255, 0.1)', 
                borderRadius: 4,
                overflow: 'hidden'
              }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(usagePatterns.length * 10, 100)}%` }}
                  transition={{ duration: 1, ease: "easeOut" }}
                  style={{
                    height: '100%',
                    background: 'linear-gradient(90deg, #1976d2, #42a5f5)',
                    borderRadius: 4
                  }}
                />
              </Box>
            </Box>
            <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
              {usagePatterns.length} patterns learned
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  )
}
