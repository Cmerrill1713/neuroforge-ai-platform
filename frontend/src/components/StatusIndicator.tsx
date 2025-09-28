'use client'

import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  LinearProgress,
  Fade,
  Collapse
} from '@mui/material'
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon,
  VolumeUp as VolumeUpIcon,
  SmartToy as SmartToyIcon,
  Storage as StorageIcon,
  Speed as SpeedIcon
} from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'

interface SystemStatus {
  frontend: 'online' | 'offline' | 'loading'
  backend: 'online' | 'offline' | 'loading'
  tts: 'online' | 'offline' | 'loading'
  chatterbox: 'loaded' | 'loading' | 'error'
  performance: {
    responseTime: number
    audioGenerationTime: number
    memoryUsage: number
  }
}

interface StatusIndicatorProps {
  compact?: boolean
  showDetails?: boolean
  onRefresh?: () => void
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  compact = false,
  showDetails = false,
  onRefresh
}) => {
  const [status, setStatus] = useState<SystemStatus>({
    frontend: 'loading',
    backend: 'loading',
    tts: 'loading',
    chatterbox: 'loading',
    performance: {
      responseTime: 0,
      audioGenerationTime: 0,
      memoryUsage: 0
    }
  })
  const [expanded, setExpanded] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  const checkSystemStatus = async () => {
    try {
      // Check frontend
      setStatus(prev => ({ ...prev, frontend: 'online' }))

      // Check backend
      try {
        const backendResponse = await fetch('http://localhost:8002/models/status')
        if (backendResponse.ok) {
          setStatus(prev => ({ ...prev, backend: 'online' }))
        } else {
          setStatus(prev => ({ ...prev, backend: 'offline' }))
        }
      } catch {
        setStatus(prev => ({ ...prev, backend: 'offline' }))
      }

      // Check TTS server
      try {
        const ttsResponse = await fetch('http://localhost:8086/status')
        if (ttsResponse.ok) {
          const ttsData = await ttsResponse.json()
          setStatus(prev => ({ 
            ...prev, 
            tts: 'online',
            chatterbox: ttsData.chatterbox_loaded ? 'loaded' : 'loading'
          }))
        } else {
          setStatus(prev => ({ ...prev, tts: 'offline' }))
        }
      } catch {
        setStatus(prev => ({ ...prev, tts: 'offline' }))
      }

      setLastUpdate(new Date())
    } catch (error) {
      console.error('Error checking system status:', error)
    }
  }

  useEffect(() => {
    checkSystemStatus()
    const interval = setInterval(checkSystemStatus, 10000) // Check every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
      case 'loaded':
        return '#4caf50'
      case 'loading':
        return '#ff9800'
      case 'offline':
      case 'error':
        return '#f44336'
      default:
        return '#757575'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
      case 'loaded':
        return <CheckCircleIcon />
      case 'loading':
        return <RefreshIcon />
      case 'offline':
      case 'error':
        return <ErrorIcon />
      default:
        return <WarningIcon />
    }
  }

  const getOverallStatus = () => {
    const statuses = [status.frontend, status.backend, status.tts, status.chatterbox]
    if (statuses.every(s => s === 'online' || s === 'loaded')) return 'online'
    if (statuses.some(s => s === 'offline' || s === 'error')) return 'offline'
    return 'loading'
  }

  const overallStatus = getOverallStatus()

  if (compact) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Tooltip title={`System ${overallStatus}`}>
          <Chip
            icon={getStatusIcon(overallStatus)}
            label={overallStatus.toUpperCase()}
            size="small"
            sx={{
              backgroundColor: getStatusColor(overallStatus),
              color: 'white',
              fontWeight: 600
            }}
          />
        </Tooltip>
        
        {onRefresh && (
          <IconButton size="small" onClick={onRefresh}>
            <RefreshIcon />
          </IconButton>
        )}
      </Box>
    )
  }

  return (
    <Paper
      elevation={2}
      sx={{
        p: 2,
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.1)'
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6" sx={{ color: 'white' }}>
          System Status
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Chip
            icon={getStatusIcon(overallStatus)}
            label={overallStatus.toUpperCase()}
            size="small"
            sx={{
              backgroundColor: getStatusColor(overallStatus),
              color: 'white',
              fontWeight: 600
            }}
          />
          
          {onRefresh && (
            <IconButton size="small" onClick={onRefresh}>
              <RefreshIcon />
            </IconButton>
          )}
          
          <IconButton 
            size="small" 
            onClick={() => setExpanded(!expanded)}
            sx={{ color: 'white' }}
          >
            {expanded ? '▼' : '▶'}
          </IconButton>
        </Box>
      </Box>

      <Collapse in={expanded}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* Service Status */}
          <Box>
            <Typography variant="subtitle2" sx={{ color: 'white', mb: 1 }}>
              Services
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              <Chip
                icon={<SmartToyIcon />}
                label="Frontend"
                size="small"
                sx={{
                  backgroundColor: getStatusColor(status.frontend),
                  color: 'white'
                }}
              />
              <Chip
                icon={<StorageIcon />}
                label="Backend"
                size="small"
                sx={{
                  backgroundColor: getStatusColor(status.backend),
                  color: 'white'
                }}
              />
              <Chip
                icon={<VolumeUpIcon />}
                label="TTS Server"
                size="small"
                sx={{
                  backgroundColor: getStatusColor(status.tts),
                  color: 'white'
                }}
              />
              <Chip
                icon={<SpeedIcon />}
                label="Chatterbox"
                size="small"
                sx={{
                  backgroundColor: getStatusColor(status.chatterbox),
                  color: 'white'
                }}
              />
            </Box>
          </Box>

          {/* Performance Metrics */}
          {showDetails && (
            <Box>
              <Typography variant="subtitle2" sx={{ color: 'white', mb: 1 }}>
                Performance
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Box>
                  <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                    Response Time: {status.performance.responseTime}ms
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={Math.min((status.performance.responseTime / 1000) * 100, 100)}
                    sx={{
                      height: 4,
                      borderRadius: 2,
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: status.performance.responseTime < 500 ? '#4caf50' : '#ff9800'
                      }
                    }}
                  />
                </Box>
                
                <Box>
                  <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                    Audio Generation: {status.performance.audioGenerationTime}ms
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={Math.min((status.performance.audioGenerationTime / 2000) * 100, 100)}
                    sx={{
                      height: 4,
                      borderRadius: 2,
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: status.performance.audioGenerationTime < 1000 ? '#4caf50' : '#ff9800'
                      }
                    }}
                  />
                </Box>
              </Box>
            </Box>
          )}

          <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
            Last updated: {typeof window !== 'undefined' ? lastUpdate.toLocaleTimeString() : 'Loading...'}
          </Typography>
        </Box>
      </Collapse>
    </Paper>
  )
}
