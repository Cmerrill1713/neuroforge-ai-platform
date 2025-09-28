'use client'

import React from 'react'
import { 
  Card, 
  CardContent, 
  CardActionArea,
  Typography, 
  Box,
  Chip,
  Avatar,
  Tooltip,
  IconButton
} from '@mui/material'
import { motion } from 'framer-motion'
import { AnimatedCard, MagneticCard, FloatingElement } from '../animations/AdvancedAnimations'

interface NavigationCardProps {
  id: string
  label: string
  icon: React.ComponentType<any>
  color: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info'
  description: string
  trend: string
  isActive: boolean
  onClick: () => void
  variant?: 'desktop' | 'mobile'
}

const colorValues = {
  primary: { main: '#6366f1', light: '#818cf8' },
  secondary: { main: '#ec4899', light: '#f472b6' },
  success: { main: '#10b981', light: '#34d399' },
  warning: { main: '#f59e0b', light: '#fbbf24' },
  error: { main: '#ef4444', light: '#f87171' },
  info: { main: '#06b6d4', light: '#22d3ee' },
}

export function NavigationCard({
  id,
  label,
  icon: IconComponent,
  color,
  description,
  trend,
  isActive,
  onClick,
  variant = 'desktop'
}: NavigationCardProps) {
  if (variant === 'mobile') {
    return (
      <AnimatedCard>
        <Tooltip title={description} placement="top">
          <Card
            sx={{
              background: isActive 
                ? `linear-gradient(135deg, ${colorValues[color].main} 0%, ${colorValues[color].light} 100%)`
                : `linear-gradient(135deg, ${colorValues[color].main}20 0%, ${colorValues[color].light}20 100%)`,
              backdropFilter: 'blur(10px)',
              border: isActive ? 'none' : '1px solid rgba(255, 255, 255, 0.1)',
              boxShadow: isActive ? '0 8px 32px rgba(0, 0, 0, 0.3)' : 'none',
              minHeight: 'auto',
              cursor: 'pointer',
              position: 'relative',
              overflow: 'hidden',
              '&:hover': {
                transform: 'translateY(-2px) scale(1.02)',
                boxShadow: isActive 
                  ? '0 12px 40px rgba(0, 0, 0, 0.4)' 
                  : '0 8px 25px rgba(0, 0, 0, 0.25)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              },
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: '-100%',
                width: '100%',
                height: '100%',
                background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
                transition: 'left 0.5s ease',
              },
              '&:hover::before': {
                left: '100%',
              }
            }}
          >
            <CardActionArea onClick={onClick}>
              <CardContent sx={{ p: 2, textAlign: 'center', position: 'relative' }}>
                <FloatingElement intensity={0.1}>
                  <Box sx={{ 
                    fontSize: '1.8rem',
                    mb: 1,
                    color: isActive ? 'white' : 'text.secondary',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center'
                  }}>
                    <IconComponent fontSize="inherit" />
                  </Box>
                </FloatingElement>
                <Typography 
                  variant="caption" 
                  sx={{ 
                    fontSize: '0.7rem',
                    fontWeight: isActive ? 600 : 400,
                    color: 'white',
                    display: 'block'
                  }}
                >
                  {label.split(' ')[0]}
                </Typography>
              </CardContent>
            </CardActionArea>
          </Card>
        </Tooltip>
      </AnimatedCard>
    )
  }

  return (
    <MagneticCard strength={0.2}>
      <Card
        sx={{
          background: isActive 
            ? `linear-gradient(135deg, ${colorValues[color].main} 0%, ${colorValues[color].light} 100%)`
            : `linear-gradient(135deg, ${colorValues[color].main}20 0%, ${colorValues[color].light}20 100%)`,
          backdropFilter: 'blur(10px)',
          border: isActive ? 'none' : '1px solid rgba(255, 255, 255, 0.1)',
          boxShadow: isActive ? '0 8px 32px rgba(0, 0, 0, 0.3)' : '0 2px 8px rgba(0, 0, 0, 0.1)',
          cursor: 'pointer',
          position: 'relative',
          overflow: 'hidden',
          opacity: isActive ? 1 : 0.8,
          '&:hover': {
            transform: 'translateY(-2px) scale(1.02)',
            boxShadow: isActive 
              ? '0 12px 40px rgba(0, 0, 0, 0.4)' 
              : '0 8px 25px rgba(0, 0, 0, 0.25)',
            opacity: 1,
            border: '1px solid rgba(255, 255, 255, 0.2)',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          },
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: '-100%',
            width: '100%',
            height: '100%',
            background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
            transition: 'left 0.5s ease',
          },
          '&:hover::before': {
            left: '100%',
          }
        }}
      >
        <CardActionArea onClick={onClick}>
          <CardContent sx={{ p: 2, position: 'relative' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <FloatingElement intensity="low">
                <Avatar
                  sx={{
                    background: isActive 
                      ? 'rgba(255, 255, 255, 0.2)' 
                      : `${color}.main`,
                    width: 44,
                    height: 44,
                    fontSize: '1.1rem',
                    position: 'relative',
                    '&::after': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      borderRadius: '50%',
                      background: isActive 
                        ? 'rgba(255, 255, 255, 0.1)' 
                        : 'rgba(255, 255, 255, 0.05)',
                      animation: isActive ? 'pulse 2s infinite' : 'none',
                    }
                  }}
                >
                  <IconComponent />
                </Avatar>
              </FloatingElement>
              
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography 
                  variant="h6" 
                  sx={{ 
                    fontWeight: 600,
                    color: 'white',
                    mb: 0.5,
                    fontSize: '0.95rem',
                    lineHeight: 1.2
                  }}
                >
                  {label}
                </Typography>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    color: 'rgba(255, 255, 255, 0.9)',
                    mb: 1,
                    fontSize: '0.8rem',
                    lineHeight: 1.3,
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden'
                  }}
                >
                  {description}
                </Typography>
                <Chip
                  label={trend}
                  size="small"
                  sx={{
                    background: isActive 
                      ? 'rgba(255, 255, 255, 0.2)' 
                      : `${color}.main`,
                    color: isActive ? 'white' : 'white',
                    fontSize: '0.65rem',
                    height: 18,
                    animation: isActive ? 'pulse 2s infinite' : 'none'
                  }}
                />
              </Box>
            </Box>
          </CardContent>
        </CardActionArea>
      </Card>
    </MagneticCard>
  )
}
