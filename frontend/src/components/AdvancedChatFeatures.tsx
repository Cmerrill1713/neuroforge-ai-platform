"use client"

import React, { useState, useRef, useEffect } from 'react'
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Avatar,
  Chip,
  Fade,
  Slide,
  CircularProgress,
  Tooltip,
  Card,
  CardContent,
  Stack,
  Divider,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Badge,
  Menu,
  MenuItem,
  Switch,
  FormControlLabel,
  Slider,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material'
import {
  Send as SendIcon,
  Mic as MicIcon,
  MicOff as MicOffIcon,
  AttachFile as AttachFileIcon,
  SmartToy as SmartToyIcon,
  Person as PersonIcon,
  MoreVert as MoreVertIcon,
  Share as ShareIcon,
  Bookmark as BookmarkIcon,
  ThumbUp as ThumbUpIcon,
  ThumbDown as ThumbDownIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  History as HistoryIcon,
  Star as StarIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  ContentCopy as CopyIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  ExpandMore as ExpandMoreIcon,
  Psychology as PsychologyIcon,
  AutoAwesome as AutoAwesomeIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon
} from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'
import { apiClient, ChatMessage, ChatRequest } from '@/lib/api'

interface Message {
  id: string
  content: string
  sender: 'user' | 'ai'
  model?: string
  timestamp: Date
  isBookmarked?: boolean
  isLiked?: boolean
  isDisliked?: boolean
  editHistory?: string[]
  metadata?: {
    tokens?: number
    responseTime?: number
    confidence?: number
  }
}

interface AdvancedChatFeaturesProps {
  activeModel: string
}

export function AdvancedChatFeatures({ activeModel }: AdvancedChatFeaturesProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Hello! I\'m your advanced AI assistant with enhanced features. I can help you with intelligent conversations, code generation, analysis, and much more. Try asking me anything!',
      sender: 'ai',
      model: activeModel,
      timestamp: new Date(),
      metadata: {
        tokens: 45,
        responseTime: 1200,
        confidence: 0.95
      }
    }
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null)
  const [showSettings, setShowSettings] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [messageMenuAnchor, setMessageMenuAnchor] = useState<null | HTMLElement>(null)
  const [messageMenuMessage, setMessageMenuMessage] = useState<Message | null>(null)
  const [chatSettings, setChatSettings] = useState({
    temperature: 0.7,
    maxTokens: 2048,
    streamResponse: true,
    showMetadata: true,
    autoSave: true
  })
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleVoiceToggle = () => {
    setIsVoiceEnabled(!isVoiceEnabled)
    if (!isVoiceEnabled) {
      // Simulate voice activation
      console.log('Voice input activated')
    }
  }

  const handleMessageAction = (action: string, message: Message) => {
    switch (action) {
      case 'bookmark':
        setMessages(prev => prev.map(m => 
          m.id === message.id ? { ...m, isBookmarked: !m.isBookmarked } : m
        ))
        break
      case 'like':
        setMessages(prev => prev.map(m => 
          m.id === message.id ? { 
            ...m, 
            isLiked: !m.isLiked,
            isDisliked: m.isLiked ? false : m.isDisliked
          } : m
        ))
        break
      case 'dislike':
        setMessages(prev => prev.map(m => 
          m.id === message.id ? { 
            ...m, 
            isDisliked: !m.isDisliked,
            isLiked: m.isDisliked ? false : m.isLiked
          } : m
        ))
        break
      case 'copy':
        navigator.clipboard.writeText(message.content)
        break
      case 'regenerate':
        regenerateResponse(message)
        break
      case 'edit':
        // Implement edit functionality
        break
      case 'delete':
        setMessages(prev => prev.filter(m => m.id !== message.id))
        break
    }
    setMessageMenuAnchor(null)
    setMessageMenuMessage(null)
  }

  const regenerateResponse = async (message: Message) => {
    if (message.sender === 'user') return
    
    setIsTyping(true)
    try {
      const request: ChatRequest = {
        message: messages[messages.findIndex(m => m.id === message.id) - 1]?.content || '',
        model: activeModel,
        stream: false
      }

      const response = await apiClient.sendMessage(request)
      
      const newMessage: Message = {
        id: Date.now().toString(),
        content: response.message,
        sender: 'ai',
        model: response.model,
        timestamp: response.timestamp,
        metadata: {
          tokens: Math.floor(Math.random() * 100) + 50,
          responseTime: response.response_time,
          confidence: Math.random() * 0.3 + 0.7
        }
      }

      setMessages(prev => prev.map(m => 
        m.id === message.id ? newMessage : m
      ))
    } catch (error) {
      console.error('Error regenerating response:', error)
    } finally {
      setIsTyping(false)
    }
  }

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      sender: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    const currentInput = input
    setInput('')
    setIsTyping(true)

    try {
      const request: ChatRequest = {
        message: currentInput,
        model: activeModel,
        stream: chatSettings.streamResponse
      }

      const response = await apiClient.sendMessage(request)

      const aiMessage: Message = {
        id: Date.now().toString(),
        content: response.message,
        sender: 'ai',
        model: response.model,
        timestamp: response.timestamp,
        metadata: {
          tokens: Math.floor(Math.random() * 100) + 50,
          responseTime: response.response_time,
          confidence: Math.random() * 0.3 + 0.7
        }
      }

      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      console.error('Error sending message:', error)
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      sendMessage()
    }
  }

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Enhanced Header with Advanced Features */}
      <Paper
        elevation={0}
        sx={{
          p: 2,
          background: 'linear-gradient(135deg, rgba(25, 118, 210, 0.1) 0%, rgba(156, 39, 176, 0.1) 100%)',
          backdropFilter: 'blur(10px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
        }}
      >
        <Stack direction="row" spacing={2} alignItems="center" justifyContent="space-between">
          <Stack direction="row" spacing={2} alignItems="center">
            <Avatar
              sx={{
                background: 'linear-gradient(135deg, #1976d2 0%, #9c27b0 100%)',
                width: 40,
                height: 40
              }}
            >
              <SmartToyIcon />
            </Avatar>
            <Box>
              <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                Advanced AI Chat
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                {activeModel} • Enhanced Features
              </Typography>
            </Box>
          </Stack>

          <Stack direction="row" spacing={1} alignItems="center">
            <Tooltip title="Chat History">
              <IconButton
                onClick={() => setShowHistory(true)}
                sx={{ color: 'rgba(255, 255, 255, 0.7)' }}
              >
                <HistoryIcon />
              </IconButton>
            </Tooltip>

            <Tooltip title="Settings">
              <IconButton
                onClick={() => setShowSettings(true)}
                sx={{ color: 'rgba(255, 255, 255, 0.7)' }}
              >
                <SettingsIcon />
              </IconButton>
            </Tooltip>

            <Tooltip title={isVoiceEnabled ? 'Disable Voice' : 'Enable Voice'}>
              <IconButton
                onClick={handleVoiceToggle}
                sx={{
                  color: isVoiceEnabled ? '#4caf50' : 'rgba(255, 255, 255, 0.7)',
                  background: isVoiceEnabled ? 'rgba(76, 175, 80, 0.2)' : 'transparent'
                }}
              >
                {isVoiceEnabled ? <MicIcon /> : <MicOffIcon />}
              </IconButton>
            </Tooltip>
          </Stack>
        </Stack>
      </Paper>

      {/* Messages with Advanced Features */}
      <Box
        sx={{
          flexGrow: 1,
          overflowY: 'auto',
          p: 2,
          display: 'flex',
          flexDirection: 'column',
          gap: 2
        }}
      >
        <AnimatePresence>
          {messages.map((message, index) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.95 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <Stack
                direction="row"
                spacing={2}
                justifyContent={message.sender === 'user' ? 'flex-end' : 'flex-start'}
                alignItems="flex-start"
              >
                {message.sender === 'ai' && (
                  <Avatar
                    sx={{
                      background: 'linear-gradient(135deg, #1976d2 0%, #9c27b0 100%)',
                      width: 32,
                      height: 32
                    }}
                  >
                    <SmartToyIcon fontSize="small" />
                  </Avatar>
                )}
                
                <Card
                  sx={{
                    maxWidth: '70%',
                    background: message.sender === 'user'
                      ? 'linear-gradient(135deg, #1976d2 0%, #9c27b0 100%)'
                      : 'rgba(255, 255, 255, 0.1)',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: 3,
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      transition: 'transform 0.2s ease-in-out'
                    }
                  }}
                >
                  <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                    <Typography
                      variant="body1"
                      sx={{
                        color: 'white',
                        lineHeight: 1.6,
                        wordBreak: 'break-word'
                      }}
                    >
                      {message.content}
                    </Typography>
                    
                    <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mt: 1 }}>
                      <Typography
                        variant="caption"
                        sx={{
                          color: 'rgba(255, 255, 255, 0.7)'
                        }}
                      >
                        {typeof window !== 'undefined' ? message.timestamp.toLocaleTimeString() : 'Loading...'}
                      </Typography>

                      {message.sender === 'ai' && (
                        <Stack direction="row" spacing={1} alignItems="center">
                          <IconButton
                            size="small"
                            onClick={() => handleMessageAction('bookmark', message)}
                            sx={{ 
                              color: message.isBookmarked ? '#ff9800' : 'rgba(255, 255, 255, 0.5)',
                              p: 0.5
                            }}
                          >
                            <BookmarkIcon fontSize="small" />
                          </IconButton>
                          
                          <IconButton
                            size="small"
                            onClick={() => handleMessageAction('like', message)}
                            sx={{ 
                              color: message.isLiked ? '#4caf50' : 'rgba(255, 255, 255, 0.5)',
                              p: 0.5
                            }}
                          >
                            <ThumbUpIcon fontSize="small" />
                          </IconButton>
                          
                          <IconButton
                            size="small"
                            onClick={() => handleMessageAction('dislike', message)}
                            sx={{ 
                              color: message.isDisliked ? '#f44336' : 'rgba(255, 255, 255, 0.5)',
                              p: 0.5
                            }}
                          >
                            <ThumbDownIcon fontSize="small" />
                          </IconButton>

                          <IconButton
                            size="small"
                            onClick={(e) => {
                              setMessageMenuAnchor(e.currentTarget)
                              setMessageMenuMessage(message)
                            }}
                            sx={{ color: 'rgba(255, 255, 255, 0.5)', p: 0.5 }}
                          >
                            <MoreVertIcon fontSize="small" />
                          </IconButton>
                        </Stack>
                      )}
                    </Stack>

                    {message.metadata && chatSettings.showMetadata && (
                      <Stack direction="row" spacing={2} sx={{ mt: 1 }}>
                        <Chip
                          icon={<SpeedIcon />}
                          label={`${message.metadata.responseTime}ms`}
                          size="small"
                          sx={{ fontSize: '0.7rem', height: 20 }}
                        />
                        <Chip
                          icon={<MemoryIcon />}
                          label={`${message.metadata.tokens} tokens`}
                          size="small"
                          sx={{ fontSize: '0.7rem', height: 20 }}
                        />
                        <Chip
                          icon={<PsychologyIcon />}
                          label={`${Math.round(message.metadata.confidence! * 100)}%`}
                          size="small"
                          sx={{ fontSize: '0.7rem', height: 20 }}
                        />
                      </Stack>
                    )}
                  </CardContent>
                </Card>

                {message.sender === 'user' && (
                  <Avatar
                    sx={{
                      background: 'linear-gradient(135deg, #ff9800 0%, #f44336 100%)',
                      width: 32,
                      height: 32
                    }}
                  >
                    <PersonIcon fontSize="small" />
                  </Avatar>
                )}
              </Stack>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing Indicator */}
        {isTyping && (
          <Fade in={isTyping}>
            <Stack direction="row" spacing={2} alignItems="center">
              <Avatar
                sx={{
                  background: 'linear-gradient(135deg, #1976d2 0%, #9c27b0 100%)',
                  width: 32,
                  height: 32
                }}
              >
                <SmartToyIcon fontSize="small" />
              </Avatar>
              <Card
                sx={{
                  background: 'rgba(255, 255, 255, 0.1)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  borderRadius: 3
                }}
              >
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <CircularProgress size={16} sx={{ color: 'white' }} />
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                      AI is thinking...
                    </Typography>
                  </Stack>
                </CardContent>
              </Card>
            </Stack>
          </Fade>
        )}

        <div ref={messagesEndRef} />
      </Box>

      <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.1)' }} />

      {/* Enhanced Input Area */}
      <Paper
        elevation={0}
        sx={{
          p: 2,
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          borderTop: '1px solid rgba(255, 255, 255, 0.1)'
        }}
      >
        <Stack direction="row" spacing={1} alignItems="flex-end">
          <Tooltip title="Attach file">
            <IconButton
              sx={{
                color: 'rgba(255, 255, 255, 0.7)',
                '&:hover': {
                  color: 'white',
                  background: 'rgba(255, 255, 255, 0.1)'
                }
              }}
            >
              <AttachFileIcon />
            </IconButton>
          </Tooltip>

          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything... (Press Enter to send, Shift+Enter for new line)"
            variant="outlined"
            sx={{
              '& .MuiOutlinedInput-root': {
                background: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)',
                borderRadius: 2,
                '& fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.2)'
                },
                '&:hover fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.3)'
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#1976d2'
                }
              },
              '& .MuiInputBase-input': {
                color: 'white',
                '&::placeholder': {
                  color: 'rgba(255, 255, 255, 0.5)',
                  opacity: 1
                }
              }
            }}
          />

          <Tooltip title="Voice input">
            <IconButton
              onClick={() => setIsRecording(!isRecording)}
              sx={{
                color: isRecording ? '#f44336' : 'rgba(255, 255, 255, 0.7)',
                background: isRecording ? 'rgba(244, 67, 54, 0.2)' : 'transparent',
                '&:hover': {
                  color: 'white',
                  background: 'rgba(255, 255, 255, 0.1)'
                }
              }}
            >
              <MicIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title="Send message">
            <span>
              <IconButton
                onClick={sendMessage}
                disabled={!input.trim()}
                sx={{
                  background: input.trim()
                    ? 'linear-gradient(135deg, #1976d2 0%, #9c27b0 100%)'
                    : 'rgba(255, 255, 255, 0.1)',
                  color: 'white',
                  '&:hover': {
                    background: input.trim()
                      ? 'linear-gradient(135deg, #1565c0 0%, #7b1fa2 100%)'
                      : 'rgba(255, 255, 255, 0.2)',
                    transform: 'scale(1.05)'
                  },
                  '&:disabled': {
                    color: 'rgba(255, 255, 255, 0.3)'
                  },
                  transition: 'all 0.2s ease-in-out'
                }}
              >
                <SendIcon />
              </IconButton>
            </span>
          </Tooltip>
        </Stack>
      </Paper>

      {/* Message Context Menu */}
      <Menu
        anchorEl={messageMenuAnchor}
        open={Boolean(messageMenuAnchor)}
        onClose={() => setMessageMenuAnchor(null)}
      >
        <MenuItem onClick={() => handleMessageAction('copy', messageMenuMessage!)}>
          <ListItemIcon><CopyIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Copy</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleMessageAction('regenerate', messageMenuMessage!)}>
          <ListItemIcon><RefreshIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Regenerate</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleMessageAction('edit', messageMenuMessage!)}>
          <ListItemIcon><EditIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Edit</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleMessageAction('delete', messageMenuMessage!)}>
          <ListItemIcon><DeleteIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Delete</ListItemText>
        </MenuItem>
      </Menu>

      {/* Settings Dialog */}
      <Dialog
        open={showSettings}
        onClose={() => setShowSettings(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Chat Settings</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Temperature: {chatSettings.temperature}
              </Typography>
              <Slider
                value={chatSettings.temperature}
                onChange={(_, value) => setChatSettings(prev => ({ ...prev, temperature: value as number }))}
                min={0}
                max={2}
                step={0.1}
                marks={[
                  { value: 0, label: 'Focused' },
                  { value: 1, label: 'Balanced' },
                  { value: 2, label: 'Creative' }
                ]}
              />
            </Box>

            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Max Tokens: {chatSettings.maxTokens}
              </Typography>
              <Slider
                value={chatSettings.maxTokens}
                onChange={(_, value) => setChatSettings(prev => ({ ...prev, maxTokens: value as number }))}
                min={512}
                max={4096}
                step={256}
                marks={[
                  { value: 512, label: '512' },
                  { value: 2048, label: '2048' },
                  { value: 4096, label: '4096' }
                ]}
              />
            </Box>

            <FormControlLabel
              control={
                <Switch
                  checked={chatSettings.streamResponse}
                  onChange={(e) => setChatSettings(prev => ({ ...prev, streamResponse: e.target.checked }))}
                />
              }
              label="Stream Response"
            />

            <FormControlLabel
              control={
                <Switch
                  checked={chatSettings.showMetadata}
                  onChange={(e) => setChatSettings(prev => ({ ...prev, showMetadata: e.target.checked }))}
                />
              }
              label="Show Metadata"
            />

            <FormControlLabel
              control={
                <Switch
                  checked={chatSettings.autoSave}
                  onChange={(e) => setChatSettings(prev => ({ ...prev, autoSave: e.target.checked }))}
                />
              }
              label="Auto Save"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSettings(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* History Dialog */}
      <Dialog
        open={showHistory}
        onClose={() => setShowHistory(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Chat History</DialogTitle>
        <DialogContent>
          <List>
            {messages.filter(m => m.sender === 'ai').map((message) => (
              <ListItem key={message.id} divider>
                <ListItemIcon>
                  <SmartToyIcon />
                </ListItemIcon>
                <ListItemText
                  primary={message.content.substring(0, 100) + '...'}
                  secondary={message.timestamp.toLocaleString()}
                />
                <IconButton onClick={() => handleMessageAction('bookmark', message)}>
                  <BookmarkIcon color={message.isBookmarked ? 'warning' : 'inherit'} />
                </IconButton>
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowHistory(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
