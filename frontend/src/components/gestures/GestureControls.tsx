'use client'

import React, { useEffect, useRef, useState } from 'react'
import { Box, IconButton, Tooltip, Badge, Typography } from '@mui/material'
import { motion, PanInfo, useMotionValue, useTransform } from 'framer-motion'
import {
  TouchApp as TouchAppIcon,
  Swipe as SwipeIcon,
  Gesture as GestureIcon,
  VolumeUp as VolumeUpIcon,
  VolumeOff as VolumeOffIcon
} from '@mui/icons-material'

interface GestureControlsProps {
  onSwipeLeft: () => void
  onSwipeRight: () => void
  onSwipeUp: () => void
  onSwipeDown: () => void
  onPinch: (scale: number) => void
  onDoubleTap: () => void
  onLongPress: () => void
  onVoiceCommand: () => void
}

export function GestureControls({
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  onPinch,
  onDoubleTap,
  onLongPress,
  onVoiceCommand
}: GestureControlsProps) {
  const [gestureActive, setGestureActive] = useState(false)
  const [currentGesture, setCurrentGesture] = useState<string>('')
  const [voiceEnabled, setVoiceEnabled] = useState(false)
  const [touchCount, setTouchCount] = useState(0)
  const [showControls, setShowControls] = useState(false)
  
  const gestureAreaRef = useRef<HTMLDivElement>(null)
  const longPressTimer = useRef<NodeJS.Timeout>()
  const lastTouchTime = useRef(0)
  const hideControlsTimer = useRef<NodeJS.Timeout>()
  
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  const scale = useMotionValue(1)
  
  const rotateX = useTransform(y, [-300, 300], [30, -30])
  const rotateY = useTransform(x, [-300, 300], [-30, 30])

  // Auto-hide controls after 3 seconds
  useEffect(() => {
    if (showControls) {
      hideControlsTimer.current = setTimeout(() => {
        setShowControls(false)
      }, 3000)
    }
    return () => {
      if (hideControlsTimer.current) {
        clearTimeout(hideControlsTimer.current)
      }
    }
  }, [showControls])

  // Touch event handlers
  const handleTouchStart = (event: React.TouchEvent) => {
    setTouchCount(event.touches.length)
    
    if (event.touches.length === 1) {
      const now = Date.now()
      if (now - lastTouchTime.current < 300) {
        // Double tap
        onDoubleTap()
        setCurrentGesture('Double Tap')
      }
      lastTouchTime.current = now
      
      // Long press detection
      longPressTimer.current = setTimeout(() => {
        onLongPress()
        setCurrentGesture('Long Press')
      }, 500)
    }
  }

  const handleTouchMove = (event: React.TouchEvent) => {
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current)
    }
    
    if (event.touches.length === 2) {
      // Pinch gesture
      const touch1 = event.touches[0]
      const touch2 = event.touches[1]
      const distance = Math.sqrt(
        Math.pow(touch2.clientX - touch1.clientX, 2) +
        Math.pow(touch2.clientY - touch1.clientY, 2)
      )
      const scaleValue = Math.max(0.5, Math.min(2, distance / 100))
      scale.set(scaleValue)
      onPinch(scaleValue)
      setCurrentGesture(`Pinch: ${scaleValue.toFixed(1)}x`)
    }
  }

  const handleTouchEnd = () => {
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current)
    }
    scale.set(1)
    x.set(0)
    y.set(0)
    setCurrentGesture('')
  }

  // Pan gesture handlers
  const handlePan = (event: any, info: PanInfo) => {
    x.set(info.offset.x)
    y.set(info.offset.y)
    
    const threshold = 50
    if (Math.abs(info.offset.x) > threshold) {
      if (info.offset.x > 0) {
        onSwipeRight()
        setCurrentGesture('Swipe Right')
      } else {
        onSwipeLeft()
        setCurrentGesture('Swipe Left')
      }
      setShowControls(true)
    }
    
    if (Math.abs(info.offset.y) > threshold) {
      if (info.offset.y > 0) {
        onSwipeDown()
        setCurrentGesture('Swipe Down')
      } else {
        onSwipeUp()
        setCurrentGesture('Swipe Up')
      }
      setShowControls(true)
    }
  }

  const handlePanEnd = () => {
    x.set(0)
    y.set(0)
    setTimeout(() => setCurrentGesture(''), 1000)
  }

  // Voice command handler
  const handleVoiceCommand = () => {
    setVoiceEnabled(!voiceEnabled)
    onVoiceCommand()
    
    if (!voiceEnabled) {
      // Start voice recognition
      if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition
        const recognition = new SpeechRecognition()
        
        recognition.continuous = false
        recognition.interimResults = false
        recognition.lang = 'en-US'
        
        recognition.onstart = () => {
          setCurrentGesture('Listening...')
        }
        
        recognition.onresult = (event: any) => {
          const command = event.results[0][0].transcript.toLowerCase()
          setCurrentGesture(`Voice: "${command}"`)
          
          // Process voice commands
          if (command.includes('next') || command.includes('right')) {
            onSwipeRight()
          } else if (command.includes('previous') || command.includes('left')) {
            onSwipeLeft()
          } else if (command.includes('up') || command.includes('top')) {
            onSwipeUp()
          } else if (command.includes('down') || command.includes('bottom')) {
            onSwipeDown()
          }
        }
        
        recognition.onerror = () => {
          setCurrentGesture('Voice error')
        }
        
        recognition.onend = () => {
          setTimeout(() => setCurrentGesture(''), 2000)
        }
        
        recognition.start()
      }
    }
  }

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      switch (event.key) {
        case 'ArrowLeft':
          onSwipeLeft()
          setCurrentGesture('← Keyboard')
          break
        case 'ArrowRight':
          onSwipeRight()
          setCurrentGesture('→ Keyboard')
          break
        case 'ArrowUp':
          onSwipeUp()
          setCurrentGesture('↑ Keyboard')
          break
        case 'ArrowDown':
          onSwipeDown()
          setCurrentGesture('↓ Keyboard')
          break
        case ' ':
          event.preventDefault()
          onDoubleTap()
          setCurrentGesture('Space - Double Tap')
          break
      }
      
      setTimeout(() => setCurrentGesture(''), 1000)
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onSwipeLeft, onSwipeRight, onSwipeUp, onSwipeDown, onDoubleTap])

  return (
    <Box sx={{ position: 'relative', height: '100%', width: '100%' }}>
      {/* Gesture Detection Area */}
      <motion.div
        ref={gestureAreaRef}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          zIndex: 1000,
          cursor: 'grab'
        }}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        onPan={handlePan}
        onPanEnd={handlePanEnd}
        whileTap={{ cursor: 'grabbing' }}
      />

      {/* Gesture Controls Overlay */}
      <Box
        sx={{
          position: 'fixed',
          top: 16,
          right: 16,
          zIndex: 1100,
          display: 'flex',
          flexDirection: 'column',
          gap: 1
        }}
      >
        {/* Voice Command Button */}
        <Tooltip title={voiceEnabled ? "Voice Commands Active" : "Enable Voice Commands"}>
          <Badge
            color="error"
            variant="dot"
            invisible={!voiceEnabled}
          >
            <IconButton
              onClick={handleVoiceCommand}
              sx={{
                background: voiceEnabled ? 'rgba(255, 0, 0, 0.1)' : 'rgba(255, 255, 255, 0.1)',
                color: voiceEnabled ? 'error.main' : 'text.secondary',
                '&:hover': {
                  background: voiceEnabled ? 'rgba(255, 0, 0, 0.2)' : 'rgba(255, 255, 255, 0.2)',
                }
              }}
            >
              {voiceEnabled ? <VolumeUpIcon /> : <VolumeOffIcon />}
            </IconButton>
          </Badge>
        </Tooltip>

        {/* Gesture Indicator */}
        {currentGesture && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            style={{
              background: 'rgba(0, 0, 0, 0.8)',
              color: 'white',
              padding: '8px 12px',
              borderRadius: '8px',
              fontSize: '12px',
              fontWeight: 500,
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <GestureIcon fontSize="small" />
            {currentGesture}
          </motion.div>
        )}
      </Box>

      {/* Gesture Instructions - Only show when needed */}
      {showControls && (
        <Box
          sx={{
            position: 'fixed',
            bottom: 16,
            left: 16,
            zIndex: 1100,
            background: 'rgba(0, 0, 0, 0.8)',
            color: 'white',
            padding: 2,
            borderRadius: 2,
            maxWidth: 300
          }}
        >
          <Typography variant="caption" sx={{ display: 'block', mb: 1, fontWeight: 600 }}>
            Gesture Controls
          </Typography>
          <Typography variant="caption" sx={{ display: 'block' }}>
            • Swipe: Navigate panels
          </Typography>
          <Typography variant="caption" sx={{ display: 'block' }}>
            • Double tap: Quick action
          </Typography>
          <Typography variant="caption" sx={{ display: 'block' }}>
            • Long press: Context menu
          </Typography>
          <Typography variant="caption" sx={{ display: 'block' }}>
            • Pinch: Zoom in/out
          </Typography>
          <Typography variant="caption" sx={{ display: 'block' }}>
            • Arrow keys: Navigate
          </Typography>
          <Typography variant="caption" sx={{ display: 'block' }}>
            • Voice: Say "next", "previous", etc.
          </Typography>
        </Box>
      )}

      {/* 3D Gesture Preview */}
      <motion.div
        style={{
          position: 'fixed',
          top: '50%',
          left: '50%',
          width: 100,
          height: 100,
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: 20,
          border: '2px solid rgba(255, 255, 255, 0.2)',
          transform: 'translate(-50%, -50%)',
          rotateX,
          rotateY,
          scale,
          zIndex: 1050,
          pointerEvents: 'none',
          opacity: gestureActive ? 1 : 0
        }}
      />
    </Box>
  )
}
