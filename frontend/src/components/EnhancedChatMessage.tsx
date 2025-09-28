'use client'

import React, { useState, useRef, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Avatar,
  IconButton,
  Tooltip,
  Chip,
  Fade,
  Collapse,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText
} from '@mui/material'
import {
  ThumbUp as ThumbUpIcon,
  ThumbDown as ThumbDownIcon,
  MoreVert as MoreVertIcon,
  VolumeUp as VolumeUpIcon,
  VolumeOff as VolumeOffIcon,
  ContentCopy as CopyIcon,
  Refresh as RefreshIcon,
  BookmarkBorder as BookmarkIcon,
  Share as ShareIcon,
  SmartToy as SmartToyIcon,
  Person as PersonIcon
} from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'

interface ChatMessageProps {
  id: string
  content: string
  sender: 'user' | 'ai'
  timestamp: Date
  model?: string
  audioFile?: string
  feedback?: 'thumbs_up' | 'thumbs_down' | null
  onFeedback?: (messageId: string, feedback: 'thumbs_up' | 'thumbs_down') => void
  onRegenerate?: (messageId: string) => void
  onCopy?: (content: string) => void
  onBookmark?: (messageId: string) => void
  onShare?: (messageId: string) => void
  isGenerating?: boolean
  showTimestamp?: boolean
}

export const EnhancedChatMessage: React.FC<ChatMessageProps> = ({
  id,
  content,
  sender,
  timestamp,
  model,
  audioFile,
  feedback,
  onFeedback,
  onRegenerate,
  onCopy,
  onBookmark,
  onShare,
  isGenerating = false,
  showTimestamp = true
}) => {
  const [isPlaying, setIsPlaying] = useState(false)
  const [showActions, setShowActions] = useState(false)
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const audioRef = useRef<HTMLAudioElement>(null)

  const isUser = sender === 'user'
  const isAI = sender === 'ai'

  const handlePlayAudio = () => {
    if (audioFile && audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause()
        setIsPlaying(false)
      } else {
        audioRef.current.play()
        setIsPlaying(true)
      }
    }
  }

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleMenuClose = () => {
    setAnchorEl(null)
  }

  const handleFeedback = (type: 'thumbs_up' | 'thumbs_down') => {
    if (onFeedback) {
      onFeedback(id, type)
    }
  }

  const handleCopy = () => {
    if (onCopy) {
      onCopy(content)
    }
    handleMenuClose()
  }

  const handleRegenerate = () => {
    if (onRegenerate) {
      onRegenerate(id)
    }
    handleMenuClose()
  }

  const handleBookmark = () => {
    if (onBookmark) {
      onBookmark(id)
    }
    handleMenuClose()
  }

  const handleShare = () => {
    if (onShare) {
      onShare(id)
    }
    handleMenuClose()
  }

  useEffect(() => {
    if (audioRef.current) {
      const audio = audioRef.current
      const handleEnded = () => setIsPlaying(false)
      const handleError = () => setIsPlaying(false)
      
      audio.addEventListener('ended', handleEnded)
      audio.addEventListener('error', handleError)
      
      return () => {
        audio.removeEventListener('ended', handleEnded)
        audio.removeEventListener('error', handleError)
      }
    }
  }, [audioFile])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      onHoverStart={() => setShowActions(true)}
      onHoverEnd={() => setShowActions(false)}
    >
      <Box
        sx={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          mb: 2,
          px: 2
        }}
      >
        <Paper
          elevation={2}
          sx={{
            maxWidth: '70%',
            p: 2,
            backgroundColor: isUser 
              ? 'rgba(25, 118, 210, 0.1)' 
              : 'rgba(255, 255, 255, 0.05)',
            border: isUser 
              ? '1px solid rgba(25, 118, 210, 0.3)' 
              : '1px solid rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
            borderRadius: isUser ? '20px 20px 4px 20px' : '20px 20px 20px 4px'
          }}
        >
          {/* Message Header */}
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Avatar
              sx={{
                width: 24,
                height: 24,
                mr: 1,
                backgroundColor: isUser ? '#1976d2' : '#4caf50'
              }}
            >
              {isUser ? <PersonIcon fontSize="small" /> : <SmartToyIcon fontSize="small" />}
            </Avatar>
            
            <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              {isUser ? 'You' : (model || 'AI Assistant')}
            </Typography>
            
            {showTimestamp && (
              <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)', ml: 'auto' }}>
                {timestamp.toLocaleTimeString()}
              </Typography>
            )}
          </Box>

          {/* Message Content */}
          <Typography
            variant="body1"
            sx={{
              color: 'white',
              lineHeight: 1.6,
              wordBreak: 'break-word',
              mb: audioFile ? 1 : 0
            }}
          >
            {content}
          </Typography>

          {/* Audio Player */}
          {audioFile && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <IconButton
                size="small"
                onClick={handlePlayAudio}
                sx={{
                  color: '#4caf50',
                  '&:hover': { backgroundColor: 'rgba(76, 175, 80, 0.1)' }
                }}
              >
                {isPlaying ? <VolumeOffIcon /> : <VolumeUpIcon />}
              </IconButton>
              
              <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                {isPlaying ? 'Playing...' : 'Click to play audio'}
              </Typography>
              
              <audio
                ref={audioRef}
                src={`/api/audio?filename=${audioFile}`}
                preload="none"
              />
            </Box>
          )}

          {/* Loading Indicator */}
          {isGenerating && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
              <Box
                sx={{
                  width: 16,
                  height: 16,
                  border: '2px solid rgba(255, 255, 255, 0.3)',
                  borderTop: '2px solid #4caf50',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite',
                  '@keyframes spin': {
                    '0%': { transform: 'rotate(0deg)' },
                    '100%': { transform: 'rotate(360deg)' }
                  }
                }}
              />
              <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                Generating response...
              </Typography>
            </Box>
          )}

          {/* Action Buttons */}
          <AnimatePresence>
            {showActions && isAI && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.2 }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 1 }}>
                  <Tooltip title="Good response">
                    <IconButton
                      size="small"
                      onClick={() => handleFeedback('thumbs_up')}
                      sx={{
                        color: feedback === 'thumbs_up' ? '#4caf50' : 'rgba(255, 255, 255, 0.5)',
                        '&:hover': { backgroundColor: 'rgba(76, 175, 80, 0.1)' }
                      }}
                    >
                      <ThumbUpIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  
                  <Tooltip title="Poor response">
                    <IconButton
                      size="small"
                      onClick={() => handleFeedback('thumbs_down')}
                      sx={{
                        color: feedback === 'thumbs_down' ? '#f44336' : 'rgba(255, 255, 255, 0.5)',
                        '&:hover': { backgroundColor: 'rgba(244, 67, 54, 0.1)' }
                      }}
                    >
                      <ThumbDownIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  
                  <Tooltip title="More options">
                    <IconButton
                      size="small"
                      onClick={handleMenuOpen}
                      sx={{ color: 'rgba(255, 255, 255, 0.5)' }}
                    >
                      <MoreVertIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              </motion.div>
            )}
          </AnimatePresence>
        </Paper>
      </Box>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        PaperProps={{
          sx: {
            backgroundColor: 'rgba(0, 0, 0, 0.9)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }
        }}
      >
        <MenuItem onClick={handleCopy}>
          <ListItemIcon>
            <CopyIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Copy</ListItemText>
        </MenuItem>
        
        <MenuItem onClick={handleRegenerate}>
          <ListItemIcon>
            <RefreshIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Regenerate</ListItemText>
        </MenuItem>
        
        <MenuItem onClick={handleBookmark}>
          <ListItemIcon>
            <BookmarkIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Bookmark</ListItemText>
        </MenuItem>
        
        <MenuItem onClick={handleShare}>
          <ListItemIcon>
            <ShareIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Share</ListItemText>
        </MenuItem>
      </Menu>
    </motion.div>
  )
}
