'use client'

import React, { useState } from 'react'
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Typography,
  Paper,
  Grid,
  IconButton,
  Tooltip,
  Avatar,
  Fade
} from '@mui/material'
import {
  Mic as MicIcon,
  VolumeUp as VolumeUpIcon,
  Settings as SettingsIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon
} from '@mui/icons-material'
import { motion } from 'framer-motion'

interface VoiceProfile {
  id: string
  name: string
  description: string
  color: string
  icon: string
  exaggeration: number
  cfgWeight: number
  characteristics: string[]
}

const voiceProfiles: VoiceProfile[] = [
  {
    id: 'assistant',
    name: 'Assistant',
    description: 'Friendly and helpful',
    color: '#4caf50',
    icon: '🤖',
    exaggeration: 0.5,
    cfgWeight: 0.5,
    characteristics: ['Friendly', 'Clear', 'Professional']
  },
  {
    id: 'professional',
    name: 'Professional',
    description: 'Authoritative and clear',
    color: '#2196f3',
    icon: '👔',
    exaggeration: 0.3,
    cfgWeight: 0.7,
    characteristics: ['Authoritative', 'Clear', 'Formal']
  },
  {
    id: 'excited',
    name: 'Excited',
    description: 'Energetic and enthusiastic',
    color: '#ff9800',
    icon: '🎉',
    exaggeration: 0.8,
    cfgWeight: 0.2,
    characteristics: ['Energetic', 'Enthusiastic', 'Dynamic']
  },
  {
    id: 'calm',
    name: 'Calm',
    description: 'Soothing and peaceful',
    color: '#9c27b0',
    icon: '🧘',
    exaggeration: 0.2,
    cfgWeight: 0.8,
    characteristics: ['Soothing', 'Peaceful', 'Relaxed']
  },
  {
    id: 'narrator',
    name: 'Narrator',
    description: 'Clear storytelling voice',
    color: '#607d8b',
    icon: '📚',
    exaggeration: 0.4,
    cfgWeight: 0.6,
    characteristics: ['Clear', 'Storytelling', 'Engaging']
  },
  {
    id: 'news',
    name: 'News',
    description: 'Authoritative news voice',
    color: '#f44336',
    icon: '📰',
    exaggeration: 0.3,
    cfgWeight: 0.9,
    characteristics: ['Authoritative', 'News', 'Formal']
  }
]

interface VoiceProfileSelectorProps {
  selectedProfile: string
  onProfileChange: (profile: string) => void
  onTestVoice?: (profile: string) => void
  compact?: boolean
}

export const VoiceProfileSelector: React.FC<VoiceProfileSelectorProps> = ({
  selectedProfile,
  onProfileChange,
  onTestVoice,
  compact = false
}) => {
  const [isPlaying, setIsPlaying] = useState<string | null>(null)

  const handleTestVoice = async (profileId: string) => {
    if (isPlaying === profileId) {
      setIsPlaying(null)
      return
    }

    setIsPlaying(profileId)
    
    try {
      if (onTestVoice) {
        await onTestVoice(profileId)
      }
    } catch (error) {
      console.error('Error testing voice:', error)
    } finally {
      setTimeout(() => setIsPlaying(null), 2000)
    }
  }

  const selectedProfileData = voiceProfiles.find(p => p.id === selectedProfile)

  if (compact) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Voice</InputLabel>
          <Select
            value={selectedProfile}
            onChange={(e) => onProfileChange(e.target.value)}
            label="Voice"
          >
            {voiceProfiles.map((profile) => (
              <MenuItem key={profile.id} value={profile.id}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <span>{profile.icon}</span>
                  <Typography variant="body2">{profile.name}</Typography>
                </Box>
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        
        {onTestVoice && (
          <Tooltip title="Test Voice">
            <IconButton
              size="small"
              onClick={() => handleTestVoice(selectedProfile)}
              sx={{ 
                color: selectedProfileData?.color,
                '&:hover': { backgroundColor: `${selectedProfileData?.color}20` }
              }}
            >
              {isPlaying === selectedProfile ? <StopIcon /> : <PlayIcon />}
            </IconButton>
          </Tooltip>
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
      <Typography variant="h6" sx={{ mb: 2, color: 'white' }}>
        Voice Profile Selection
      </Typography>
      
      <Grid container spacing={2}>
        {voiceProfiles.map((profile) => (
          <Grid item xs={12} sm={6} md={4} key={profile.id}>
            <motion.div
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Paper
                elevation={selectedProfile === profile.id ? 4 : 1}
                sx={{
                  p: 2,
                  cursor: 'pointer',
                  border: selectedProfile === profile.id ? `2px solid ${profile.color}` : '2px solid transparent',
                  background: selectedProfile === profile.id 
                    ? `${profile.color}20` 
                    : 'rgba(255, 255, 255, 0.05)',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    background: `${profile.color}15`,
                    transform: 'translateY(-2px)'
                  }
                }}
                onClick={() => onProfileChange(profile.id)}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Avatar
                    sx={{
                      bgcolor: profile.color,
                      width: 32,
                      height: 32,
                      mr: 1,
                      fontSize: '1rem'
                    }}
                  >
                    {profile.icon}
                  </Avatar>
                  <Typography variant="subtitle2" sx={{ color: 'white', fontWeight: 600 }}>
                    {profile.name}
                  </Typography>
                </Box>
                
                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                  {profile.description}
                </Typography>
                
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                  {profile.characteristics.map((char) => (
                    <Chip
                      key={char}
                      label={char}
                      size="small"
                      sx={{
                        fontSize: '0.7rem',
                        height: 20,
                        backgroundColor: `${profile.color}30`,
                        color: 'white',
                        border: `1px solid ${profile.color}50`
                      }}
                    />
                  ))}
                </Box>
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                    Exaggeration: {profile.exaggeration} | CFG: {profile.cfgWeight}
                  </Typography>
                  
                  {onTestVoice && (
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleTestVoice(profile.id)
                      }}
                      sx={{ 
                        color: profile.color,
                        '&:hover': { backgroundColor: `${profile.color}20` }
                      }}
                    >
                      {isPlaying === profile.id ? <StopIcon /> : <PlayIcon />}
                    </IconButton>
                  )}
                </Box>
              </Paper>
            </motion.div>
          </Grid>
        ))}
      </Grid>
    </Paper>
  )
}
