'use client'

import React, { useState, useEffect, useCallback } from 'react'
import {
  Snackbar,
  Alert,
  AlertTitle,
  IconButton,
  Collapse,
  Box,
  Typography,
  Button,
  Chip
} from '@mui/material'
import {
  Close as CloseIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  CheckCircle as SuccessIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon
} from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'

export interface NotificationData {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  details?: string
  action?: {
    label: string
    onClick: () => void
  }
  duration?: number
  persistent?: boolean
  timestamp: Date
}

interface NotificationCenterProps {
  notifications: NotificationData[]
  onRemove: (id: string) => void
  onClearAll: () => void
  maxNotifications?: number
}

export const NotificationCenter: React.FC<NotificationCenterProps> = ({
  notifications,
  onRemove,
  onClearAll,
  maxNotifications = 5
}) => {
  const [expanded, setExpanded] = useState<string | null>(null)

  const getIcon = (type: NotificationData['type']) => {
    switch (type) {
      case 'success':
        return <SuccessIcon />
      case 'error':
        return <ErrorIcon />
      case 'warning':
        return <WarningIcon />
      case 'info':
        return <InfoIcon />
    }
  }

  const getColor = (type: NotificationData['type']) => {
    switch (type) {
      case 'success':
        return 'success'
      case 'error':
        return 'error'
      case 'warning':
        return 'warning'
      case 'info':
        return 'info'
    }
  }

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 80,
        right: 20,
        zIndex: 1400,
        maxWidth: 400,
        maxHeight: '80vh',
        overflow: 'auto'
      }}
    >
      <AnimatePresence>
        {notifications.slice(0, maxNotifications).map((notification) => (
          <motion.div
            key={notification.id}
            initial={{ opacity: 0, x: 300, scale: 0.8 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 300, scale: 0.8 }}
            transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
            style={{ marginBottom: 8 }}
          >
            <Alert
              severity={getColor(notification.type)}
              icon={getIcon(notification.type)}
              action={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {notification.details && (
                    <IconButton
                      size="small"
                      onClick={() => setExpanded(
                        expanded === notification.id ? null : notification.id
                      )}
                    >
                      {expanded === notification.id ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                    </IconButton>
                  )}
                  <IconButton
                    size="small"
                    onClick={() => onRemove(notification.id)}
                  >
                    <CloseIcon />
                  </IconButton>
                </Box>
              }
              sx={{
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
              }}
            >
              <AlertTitle sx={{ fontWeight: 600 }}>
                {notification.title}
              </AlertTitle>
              <Typography variant="body2" sx={{ mb: 1 }}>
                {notification.message}
              </Typography>
              
              <Collapse in={expanded === notification.id}>
                <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                  {notification.details}
                </Typography>
              </Collapse>

              {notification.action && (
                <Box sx={{ mt: 1 }}>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={notification.action.onClick}
                    sx={{ fontSize: '0.75rem' }}
                  >
                    {notification.action.label}
                  </Button>
                </Box>
              )}

              <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip
                  label={typeof window !== 'undefined' ? notification.timestamp.toLocaleTimeString() : 'Loading...'}
                  size="small"
                  variant="outlined"
                  sx={{ fontSize: '0.65rem', height: 20 }}
                />
                {notification.persistent && (
                  <Chip
                    label="Persistent"
                    size="small"
                    color="warning"
                    sx={{ fontSize: '0.65rem', height: 20 }}
                  />
                )}
              </Box>
            </Alert>
          </motion.div>
        ))}
      </AnimatePresence>

      {notifications.length > maxNotifications && (
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Button
            size="small"
            variant="outlined"
            onClick={onClearAll}
            startIcon={<RefreshIcon />}
          >
            Clear All ({notifications.length})
          </Button>
        </Box>
      )}
    </Box>
  )
}

// Hook for managing notifications
export const useNotifications = () => {
  const [notifications, setNotifications] = useState<NotificationData[]>([])

  const addNotification = useCallback((notification: Omit<NotificationData, 'id' | 'timestamp'>) => {
    const id = `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    const newNotification: NotificationData = {
      ...notification,
      id,
      timestamp: new Date()
    }

    setNotifications(prev => [newNotification, ...prev])

    // Auto-remove non-persistent notifications
    if (!notification.persistent) {
      const duration = notification.duration || 5000
      setTimeout(() => {
        removeNotification(id)
      }, duration)
    }
  }, [])

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }, [])

  const clearAll = useCallback(() => {
    setNotifications([])
  }, [])

  const showSuccess = useCallback((title: string, message: string, options?: Partial<NotificationData>) => {
    addNotification({
      type: 'success',
      title,
      message,
      ...options
    })
  }, [addNotification])

  const showError = useCallback((title: string, message: string, options?: Partial<NotificationData>) => {
    addNotification({
      type: 'error',
      title,
      message,
      persistent: true,
      ...options
    })
  }, [addNotification])

  const showWarning = useCallback((title: string, message: string, options?: Partial<NotificationData>) => {
    addNotification({
      type: 'warning',
      title,
      message,
      ...options
    })
  }, [addNotification])

  const showInfo = useCallback((title: string, message: string, options?: Partial<NotificationData>) => {
    addNotification({
      type: 'info',
      title,
      message,
      ...options
    })
  }, [addNotification])

  return {
    notifications,
    addNotification,
    removeNotification,
    clearAll,
    showSuccess,
    showError,
    showWarning,
    showInfo
  }
}

// Error boundary component
interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
  errorInfo?: React.ErrorInfo
}

export class ErrorBoundary extends React.Component<
  React.PropsWithChildren<{}>,
  ErrorBoundaryState
> {
  constructor(props: React.PropsWithChildren<{}>) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState({ error, errorInfo })
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '50vh',
            p: 4,
            textAlign: 'center'
          }}
        >
          <ErrorIcon sx={{ fontSize: 64, color: 'error.main', mb: 2 }} />
          <Typography variant="h5" sx={{ mb: 2 }}>
            Something went wrong
          </Typography>
          <Typography variant="body1" sx={{ mb: 3, color: 'text.secondary' }}>
            We're sorry, but something unexpected happened. Please try refreshing the page.
          </Typography>
          <Button
            variant="contained"
            onClick={() => window.location.reload()}
            startIcon={<RefreshIcon />}
          >
            Refresh Page
          </Button>
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.100', borderRadius: 1, maxWidth: 600 }}>
              <Typography variant="caption" component="pre" sx={{ textAlign: 'left' }}>
                {this.state.error.toString()}
              </Typography>
            </Box>
          )}
        </Box>
      )
    }

    return this.props.children
  }
}
