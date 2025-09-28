'use client'

import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  Stack,
  Avatar,
  IconButton,
  Collapse,
  Alert,
  LinearProgress,
  Tooltip,
  Fade,
  Slide
} from '@mui/material'
import {
  Psychology as PsychologyIcon,
  Warning as WarningIcon,
  ThumbDown as ThumbDownIcon,
  ThumbUp as ThumbUpIcon,
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  QuestionMark as QuestionMarkIcon,
  Lightbulb as LightbulbIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'

interface DevilsAdvocateChallenge {
  id: string
  type: 'warning' | 'question' | 'alternative' | 'risk' | 'bias'
  title: string
  message: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  confidence: number
  alternatives?: string[]
  risks?: string[]
  timestamp: Date
}

interface DevilsAdvocateOverlayProps {
  isVisible: boolean
  currentAction: string
  currentResponse?: string
  onDismiss: () => void
  onAcceptChallenge: (challengeId: string) => void
  onRejectChallenge: (challengeId: string) => void
}

const challengeTemplates = {
  warning: {
    title: "⚠️ Potential Issue Detected",
    icon: <WarningIcon />,
    color: "warning"
  },
  question: {
    title: "🤔 Critical Question",
    icon: <QuestionMarkIcon />,
    color: "info"
  },
  alternative: {
    title: "💡 Alternative Approach",
    icon: <LightbulbIcon />,
    color: "primary"
  },
  risk: {
    title: "🚨 Risk Assessment",
    icon: <ErrorIcon />,
    color: "error"
  },
  bias: {
    title: "🎭 Bias Detection",
    icon: <PsychologyIcon />,
    color: "secondary"
  }
}

export default function DevilsAdvocateOverlay({
  isVisible,
  currentAction,
  currentResponse,
  onDismiss,
  onAcceptChallenge,
  onRejectChallenge
}: DevilsAdvocateOverlayProps) {
  const [challenges, setChallenges] = useState<DevilsAdvocateChallenge[]>([])
  const [isExpanded, setIsExpanded] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)

  // Generate challenges based on current action
  useEffect(() => {
    if (isVisible && currentAction) {
      setIsGenerating(true)
      generateChallenges(currentAction, currentResponse)
    }
  }, [isVisible, currentAction, currentResponse])

  const generateChallenges = async (action: string, response?: string) => {
    // Simulate AI thinking time
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const newChallenges: DevilsAdvocateChallenge[] = []
    
    // Generate different types of challenges based on action
    if (action.includes('code') || action.includes('programming')) {
      newChallenges.push({
        id: 'code-security',
        type: 'risk',
        title: 'Security Vulnerability Risk',
        message: 'This code approach might introduce security vulnerabilities. Have you considered input validation and sanitization?',
        severity: 'high',
        confidence: 0.85,
        risks: ['SQL Injection', 'XSS Attacks', 'Buffer Overflow'],
        timestamp: new Date()
      })
      
      newChallenges.push({
        id: 'code-performance',
        type: 'alternative',
        title: 'Performance Optimization',
        message: 'There might be a more efficient algorithm. Consider time complexity and memory usage.',
        severity: 'medium',
        confidence: 0.72,
        alternatives: ['Dynamic Programming', 'Memoization', 'Caching'],
        timestamp: new Date()
      })
    }
    
    if (action.includes('decision') || action.includes('choice')) {
      newChallenges.push({
        id: 'decision-bias',
        type: 'bias',
        title: 'Cognitive Bias Detected',
        message: 'This decision might be influenced by confirmation bias. Have you considered alternative viewpoints?',
        severity: 'medium',
        confidence: 0.68,
        timestamp: new Date()
      })
      
      newChallenges.push({
        id: 'decision-consequences',
        type: 'warning',
        title: 'Unintended Consequences',
        message: 'What are the potential long-term effects of this decision? Consider second and third-order effects.',
        severity: 'high',
        confidence: 0.78,
        timestamp: new Date()
      })
    }
    
    if (action.includes('analysis') || action.includes('data')) {
      newChallenges.push({
        id: 'data-quality',
        type: 'question',
        title: 'Data Quality Concerns',
        message: 'Is the data source reliable? Have you verified the accuracy and completeness of the dataset?',
        severity: 'medium',
        confidence: 0.75,
        timestamp: new Date()
      })
      
      newChallenges.push({
        id: 'correlation-causation',
        type: 'bias',
        title: 'Correlation vs Causation',
        message: 'Are you confusing correlation with causation? Correlation does not imply causation.',
        severity: 'high',
        confidence: 0.82,
        timestamp: new Date()
      })
    }
    
    // Always add a general critical thinking challenge
    newChallenges.push({
      id: 'general-critical',
      type: 'question',
      title: 'Critical Thinking Check',
      message: 'What assumptions are you making? What evidence supports your conclusion?',
      severity: 'medium',
      confidence: 0.70,
      timestamp: new Date()
    })
    
    setChallenges(newChallenges)
    setIsGenerating(false)
  }

  const getSeverityColor = (severity: string) => {
    const colors = {
      low: 'success',
      medium: 'warning', 
      high: 'error',
      critical: 'error'
    }
    return colors[severity as keyof typeof colors] || 'default'
  }

  const getSeverityIcon = (severity: string) => {
    if (severity === 'critical' || severity === 'high') return <ErrorIcon />
    if (severity === 'medium') return <WarningIcon />
    return <CheckCircleIcon />
  }

  if (!isVisible) return null

  return (
    <Fade in={isVisible} timeout={500}>
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          bgcolor: 'rgba(0, 0, 0, 0.7)',
          zIndex: 9999,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: 2
        }}
      >
        <Slide direction="up" in={isVisible} timeout={300}>
          <Card
            sx={{
              maxWidth: 600,
              width: '100%',
              maxHeight: '80vh',
              overflow: 'auto',
              bgcolor: 'background.paper',
              boxShadow: 24
            }}
          >
            <CardContent>
              {/* Header */}
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Avatar sx={{ bgcolor: 'error.main', mr: 2 }}>
                  <PsychologyIcon />
                </Avatar>
                <Box sx={{ flexGrow: 1 }}>
                  <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                    🎭 Devil's Advocate Analysis
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Critical thinking challenges for: {currentAction}
                  </Typography>
                </Box>
                <IconButton onClick={onDismiss} size="small">
                  <CloseIcon />
                </IconButton>
              </Box>

              {/* Current Action */}
              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                  Current Action: {currentAction}
                </Typography>
                {currentResponse && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Response: {currentResponse.substring(0, 100)}...
                  </Typography>
                )}
              </Alert>

              {/* Generating State */}
              {isGenerating && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    🤔 Devil's Advocate is analyzing...
                  </Typography>
                  <LinearProgress />
                </Box>
              )}

              {/* Challenges */}
              <AnimatePresence>
                {challenges.map((challenge, index) => (
                  <motion.div
                    key={challenge.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Card
                      sx={{
                        mb: 2,
                        border: `2px solid`,
                        borderColor: `${getSeverityColor(challenge.severity)}.main`,
                        bgcolor: `${getSeverityColor(challenge.severity)}.light`,
                        '&:hover': {
                          boxShadow: 4
                        }
                      }}
                    >
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                          <Avatar
                            sx={{
                              bgcolor: `${getSeverityColor(challenge.severity)}.main`,
                              mr: 2,
                              width: 40,
                              height: 40
                            }}
                          >
                            {challengeTemplates[challenge.type].icon}
                          </Avatar>
                          <Box sx={{ flexGrow: 1 }}>
                            <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                              {challengeTemplates[challenge.type].title}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {challenge.title}
                            </Typography>
                          </Box>
                          <Chip
                            icon={getSeverityIcon(challenge.severity)}
                            label={challenge.severity.toUpperCase()}
                            color={getSeverityColor(challenge.severity) as any}
                            size="small"
                            sx={{ ml: 1 }}
                          />
                        </Box>

                        <Typography variant="body1" sx={{ mb: 2 }}>
                          {challenge.message}
                        </Typography>

                        {/* Confidence Score */}
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="body2" sx={{ mb: 1 }}>
                            Confidence: {Math.round(challenge.confidence * 100)}%
                          </Typography>
                          <LinearProgress
                            variant="determinate"
                            value={challenge.confidence * 100}
                            color={getSeverityColor(challenge.severity) as any}
                            sx={{ height: 6, borderRadius: 3 }}
                          />
                        </Box>

                        {/* Alternatives */}
                        {challenge.alternatives && (
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="subtitle2" sx={{ mb: 1 }}>
                              Alternative Approaches:
                            </Typography>
                            <Stack direction="row" spacing={1} flexWrap="wrap">
                              {challenge.alternatives.map((alt, idx) => (
                                <Chip key={idx} label={alt} size="small" variant="outlined" />
                              ))}
                            </Stack>
                          </Box>
                        )}

                        {/* Risks */}
                        {challenge.risks && (
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="subtitle2" sx={{ mb: 1 }}>
                              Potential Risks:
                            </Typography>
                            <Stack direction="row" spacing={1} flexWrap="wrap">
                              {challenge.risks.map((risk, idx) => (
                                <Chip key={idx} label={risk} size="small" color="error" variant="outlined" />
                              ))}
                            </Stack>
                          </Box>
                        )}

                        {/* Actions */}
                        <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                          <Tooltip title="Accept this challenge and reconsider">
                            <IconButton
                              size="small"
                              color="success"
                              onClick={() => onAcceptChallenge(challenge.id)}
                            >
                              <ThumbUpIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Reject this challenge">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => onRejectChallenge(challenge.id)}
                            >
                              <ThumbDownIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </AnimatePresence>

              {/* Summary */}
              {challenges.length > 0 && !isGenerating && (
                <Alert severity="warning" sx={{ mt: 2 }}>
                  <Typography variant="body2">
                    <strong>Devil's Advocate Summary:</strong> {challenges.length} critical challenges identified. 
                    Consider each carefully before proceeding.
                  </Typography>
                </Alert>
              )}

              {/* Actions */}
              <Box sx={{ display: 'flex', gap: 2, mt: 3, justifyContent: 'flex-end' }}>
                <Tooltip title="Dismiss all challenges">
                  <IconButton onClick={onDismiss} color="error">
                    <CloseIcon />
                  </IconButton>
                </Tooltip>
              </Box>
            </CardContent>
          </Card>
        </Slide>
      </Box>
    </Fade>
  )
}
