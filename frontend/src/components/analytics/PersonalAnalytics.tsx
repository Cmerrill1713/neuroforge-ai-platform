'use client'

import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Tooltip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Switch,
  FormControlLabel
} from '@mui/material'
import {
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  Timer as TimerIcon,
  CheckCircle as CheckCircleIcon,
  Code as CodeIcon,
  Chat as ChatIcon,
  School as SchoolIcon,
  Visibility as VisibilityIcon,
  SmartToy as SmartToyIcon,
  TrendingDown as TrendingDownIcon,
  Star as StarIcon,
  Insights as InsightsIcon,
  Psychology as PsychologyIcon,
  AutoAwesome as AutoAwesomeIcon
} from '@mui/icons-material'
import { motion } from 'framer-motion'

interface UsageMetric {
  id: string
  name: string
  value: number
  unit: string
  trend: 'up' | 'down' | 'stable'
  change: number
  icon: React.ComponentType
  color: string
}

interface ActivityLog {
  id: string
  action: string
  panel: string
  timestamp: number
  duration: number
  success: boolean
}

interface PersonalInsight {
  id: string
  type: 'productivity' | 'learning' | 'efficiency' | 'pattern'
  title: string
  description: string
  recommendation: string
  confidence: number
  actionable: boolean
}

export function PersonalAnalytics() {
  const [metrics, setMetrics] = useState<UsageMetric[]>([])
  const [activities, setActivities] = useState<ActivityLog[]>([])
  const [insights, setInsights] = useState<PersonalInsight[]>([])
  const [showInsights, setShowInsights] = useState(false)
  const [privacyEnabled, setPrivacyEnabled] = useState(true)

  // Generate sample analytics data
  useEffect(() => {
    const generateMetrics = (): UsageMetric[] => [
      {
        id: '1',
        name: 'Total Sessions',
        value: 47,
        unit: 'sessions',
        trend: 'up',
        change: 12,
        icon: AnalyticsIcon,
        color: '#1976d2'
      },
      {
        id: '2',
        name: 'Average Session',
        value: 24,
        unit: 'minutes',
        trend: 'up',
        change: 8,
        icon: TimerIcon,
        color: '#388e3c'
      },
      {
        id: '3',
        name: 'Tasks Completed',
        value: 156,
        unit: 'tasks',
        trend: 'up',
        change: 23,
        icon: CheckCircleIcon,
        color: '#f57c00'
      },
      {
        id: '4',
        name: 'Learning Progress',
        value: 78,
        unit: '%',
        trend: 'up',
        change: 5,
        icon: SchoolIcon,
        color: '#7b1fa2'
      },
      {
        id: '5',
        name: 'Code Lines Written',
        value: 2847,
        unit: 'lines',
        trend: 'up',
        change: 156,
        icon: CodeIcon,
        color: '#d32f2f'
      },
      {
        id: '6',
        name: 'AI Interactions',
        value: 234,
        unit: 'chats',
        trend: 'up',
        change: 34,
        icon: ChatIcon,
        color: '#00796b'
      }
    ]

    const generateActivities = (): ActivityLog[] => [
      {
        id: '1',
        action: 'Code Review',
        panel: 'Code Assistant',
        timestamp: Date.now() - 300000,
        duration: 15,
        success: true
      },
      {
        id: '2',
        action: 'Learning Module',
        panel: 'Learning Hub',
        timestamp: Date.now() - 600000,
        duration: 25,
        success: true
      },
      {
        id: '3',
        action: 'Image Analysis',
        panel: 'Vision Assistant',
        timestamp: Date.now() - 900000,
        duration: 8,
        success: true
      },
      {
        id: '4',
        action: 'AI Chat',
        panel: 'AI Assistant',
        timestamp: Date.now() - 1200000,
        duration: 12,
        success: true
      },
      {
        id: '5',
        action: 'Agent Automation',
        panel: 'AI Agents',
        timestamp: Date.now() - 1800000,
        duration: 20,
        success: false
      }
    ]

    const generateInsights = (): PersonalInsight[] => [
      {
        id: '1',
        type: 'productivity',
        title: 'Peak Productivity Hours',
        description: 'You\'re most productive between 9-11 AM and 2-4 PM',
        recommendation: 'Schedule important tasks during these peak hours',
        confidence: 0.85,
        actionable: true
      },
      {
        id: '2',
        type: 'learning',
        title: 'Learning Pattern Detected',
        description: 'You learn best with 25-minute focused sessions',
        recommendation: 'Use the Pomodoro technique for optimal learning',
        confidence: 0.78,
        actionable: true
      },
      {
        id: '3',
        type: 'efficiency',
        title: 'Code Assistant Usage',
        description: 'You use Code Assistant 40% more than other panels',
        recommendation: 'Consider exploring other features for balanced learning',
        confidence: 0.92,
        actionable: true
      },
      {
        id: '4',
        type: 'pattern',
        title: 'Session Length Optimization',
        description: 'Your most effective sessions are 20-30 minutes long',
        recommendation: 'Take breaks every 25 minutes for maximum efficiency',
        confidence: 0.73,
        actionable: true
      }
    ]

    setMetrics(generateMetrics())
    setActivities(generateActivities())
    setInsights(generateInsights())
  }, [])

  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up': return <TrendingUpIcon sx={{ color: 'success.main' }} />
      case 'down': return <TrendingDownIcon sx={{ color: 'error.main' }} />
      default: return <TrendingUpIcon sx={{ color: 'text.secondary' }} />
    }
  }

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'productivity': return <TrendingUpIcon />
      case 'learning': return <SchoolIcon />
      case 'efficiency': return <AutoAwesomeIcon />
      case 'pattern': return <PsychologyIcon />
      default: return <InsightsIcon />
    }
  }

  const getInsightColor = (type: string) => {
    switch (type) {
      case 'productivity': return '#4caf50'
      case 'learning': return '#2196f3'
      case 'efficiency': return '#ff9800'
      case 'pattern': return '#9c27b0'
      default: return '#607d8b'
    }
  }

  const getPanelIcon = (panel: string) => {
    switch (panel) {
      case 'Code Assistant': return <CodeIcon />
      case 'Learning Hub': return <SchoolIcon />
      case 'Vision Assistant': return <VisibilityIcon />
      case 'AI Assistant': return <ChatIcon />
      case 'AI Agents': return <SmartToyIcon />
      default: return <AnalyticsIcon />
    }
  }

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
        <AnalyticsIcon color="primary" />
        Personal Analytics
        <Chip 
          label={privacyEnabled ? "Privacy Protected" : "Full Analytics"} 
          color={privacyEnabled ? "success" : "warning"}
          size="small"
        />
      </Typography>

      {/* Key Metrics */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {metrics.map((metric, index) => (
          <div key={metric.id} style={{ width: '100%', padding: '8px' }}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card sx={{ 
                background: 'rgba(20, 20, 20, 0.8)',
                '&:hover': { transform: 'translateY(-2px)' },
                transition: 'transform 0.2s'
              }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                    <Avatar sx={{ bgcolor: metric.color, width: 40, height: 40 }}>
                      <metric.icon />
                    </Avatar>
                    {getTrendIcon(metric.trend)}
                  </Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                    {metric.value.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    {metric.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {metric.trend === 'up' ? '+' : metric.trend === 'down' ? '-' : ''}{metric.change}% from last week
                  </Typography>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        ))}
      </Grid>

      {/* Activity Timeline */}
      <Card sx={{ mb: 3, background: 'rgba(255, 255, 255, 0.05)' }}>
        <CardContent>
          <Typography variant="subtitle1" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
            <TimerIcon />
            Recent Activity
          </Typography>
          <List>
            {activities.map((activity, index) => (
              <motion.div
                key={activity.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <ListItem sx={{ px: 0 }}>
                  <ListItemIcon>
                    <Avatar sx={{ 
                      bgcolor: activity.success ? 'success.main' : 'error.main',
                      width: 32,
                      height: 32
                    }}>
                      {getPanelIcon(activity.panel)}
                    </Avatar>
                  </ListItemIcon>
                  <ListItemText
                    primary={activity.action}
                    secondary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 0.5 }}>
                        <Typography variant="caption" color="text.secondary">
                          {activity.panel}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {activity.duration} minutes
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {new Date(activity.timestamp).toLocaleTimeString()}
                        </Typography>
                        <Chip
                          label={activity.success ? 'Success' : 'Failed'}
                          color={activity.success ? 'success' : 'error'}
                          size="small"
                        />
                      </Box>
                    }
                  />
                </ListItem>
              </motion.div>
            ))}
          </List>
        </CardContent>
      </Card>

      {/* AI Insights */}
      <Card sx={{ background: 'rgba(255, 255, 255, 0.05)' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="subtitle1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <PsychologyIcon />
              AI-Powered Insights
            </Typography>
            <Button
              variant="outlined"
              size="small"
              onClick={() => setShowInsights(true)}
            >
              View All
            </Button>
          </Box>
          
          <Grid container spacing={2}>
            {insights.slice(0, 2).map((insight, index) => (
              <div key={insight.id} style={{ width: '100%', padding: '8px' }}>
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card sx={{ 
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: `1px solid ${getInsightColor(insight.type)}20`
                  }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <Avatar sx={{ 
                          bgcolor: getInsightColor(insight.type),
                          width: 32,
                          height: 32
                        }}>
                          {getInsightIcon(insight.type)}
                        </Avatar>
                        <Typography variant="subtitle2">
                          {insight.title}
                        </Typography>
                        <Chip
                          label={`${(insight.confidence * 100).toFixed(0)}%`}
                          size="small"
                          color={insight.confidence > 0.8 ? 'success' : insight.confidence > 0.6 ? 'warning' : 'error'}
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        {insight.description}
                      </Typography>
                      {insight.actionable && (
                        <Typography variant="caption" sx={{ 
                          color: 'primary.main',
                          fontWeight: 500
                        }}>
                          💡 {insight.recommendation}
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              </div>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Insights Dialog */}
      <Dialog open={showInsights} onClose={() => setShowInsights(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <PsychologyIcon />
            AI Insights & Recommendations
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
            {insights.map((insight, index) => (
              <div key={insight.id} style={{ width: '100%', padding: '8px' }}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card sx={{ mb: 2 }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                        <Avatar sx={{ 
                          bgcolor: getInsightColor(insight.type),
                          width: 40,
                          height: 40
                        }}>
                          {getInsightIcon(insight.type)}
                        </Avatar>
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="h6">
                            {insight.title}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {insight.type.charAt(0).toUpperCase() + insight.type.slice(1)} Insight
                          </Typography>
                        </Box>
                        <Chip
                          label={`${(insight.confidence * 100).toFixed(0)}% confidence`}
                          color={insight.confidence > 0.8 ? 'success' : insight.confidence > 0.6 ? 'warning' : 'error'}
                        />
                      </Box>
                      <Typography variant="body1" sx={{ mb: 2 }}>
                        {insight.description}
                      </Typography>
                      {insight.actionable && (
                        <Box sx={{ 
                          p: 2, 
                          background: 'rgba(25, 118, 210, 0.1)',
                          borderRadius: 1,
                          border: '1px solid rgba(25, 118, 210, 0.2)'
                        }}>
                          <Typography variant="subtitle2" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <AutoAwesomeIcon fontSize="small" />
                            Recommendation
                          </Typography>
                          <Typography variant="body2">
                            {insight.recommendation}
                          </Typography>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              </div>
            ))}
          </Grid>
        </DialogContent>
        <DialogActions>
          <FormControlLabel
            control={
              <Switch
                checked={privacyEnabled}
                onChange={(e) => setPrivacyEnabled(e.target.checked)}
              />
            }
            label="Privacy Mode"
          />
          <Button onClick={() => setShowInsights(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
