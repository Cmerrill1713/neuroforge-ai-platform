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
  Divider
} from '@mui/material'
import {
  Send as SendIcon,
  Mic as MicIcon,
  AttachFile as AttachFileIcon,
  SmartToy as SmartToyIcon,
  Person as PersonIcon,
  Settings as SettingsIcon,
  History as HistoryIcon,
  BookmarkBorder as BookmarkIcon,
  ThumbUp as ThumbUpIcon,
  ThumbDown as ThumbDownIcon,
  MoreVert as MoreVertIcon,
  Refresh as RefreshIcon,
  Psychology as PsychologyIcon
} from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'
import { apiClient, ChatMessage, ChatRequest } from '@/lib/api'
import { designSystem, getPanelStyles, getResponsivePadding } from '@/design-system'

interface Message {
  id: string
  content: string
  sender: 'user' | 'ai'
  model?: string
  detectedTask?: string
  timestamp: Date
  feedback?: 'thumbs_up' | 'thumbs_down' | null
}

interface MuiEnhancedChatPanelProps {
  activeModel: string
  customModelName?: string
  onSwitchPanel?: (panelId: string) => void
}

export function MuiEnhancedChatPanel({ activeModel, customModelName, onSwitchPanel }: MuiEnhancedChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Hello! I\'m your personal AI assistant, ready to help you with tasks, coding, learning, and productivity. How can I assist you today?',
      sender: 'ai',
      model: activeModel,
      timestamp: new Date('2024-01-01T00:00:00Z')
    }
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [feedbackLoading, setFeedbackLoading] = useState<string | null>(null)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [isClient, setIsClient] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Update timestamp after hydration to avoid SSR mismatch
  useEffect(() => {
    setIsClient(true)
    if (messages.length > 0 && messages[0].id === '1') {
      setMessages(prev => prev.map(msg => 
        msg.id === '1' ? { ...msg, timestamp: new Date() } : msg
      ))
    }
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleFeedback = async (messageId: string, feedback: 'thumbs_up' | 'thumbs_down') => {
    const message = messages.find(m => m.id === messageId)
    if (!message || message.sender !== 'ai') return

    setFeedbackLoading(messageId)

    try {
      // Update local state immediately for better UX
      setMessages(prev => prev.map(m => 
        m.id === messageId ? { ...m, feedback } : m
      ))

      // Send feedback to analysis API
      const feedbackData = {
        messageId,
        feedback,
        message: message.content,
        model: message.model || 'unknown',
        detectedTask: message.detectedTask || 'general',
        timestamp: message.timestamp.toISOString()
      }

      const response = await fetch('/api/feedback/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(feedbackData)
      })

      if (response.ok) {
        const result = await response.json()
        console.log('Feedback analysis:', result.data)
        
        // In a real system, you would:
        // 1. Update model selection algorithms
        // 2. Adjust task detection rules
        // 3. Store learning data
        // 4. Potentially switch models for future requests
        
        if (feedback === 'thumbs_down' && result.data.analysis.modelSuggestion) {
          console.log(`AI Learning: Suggested model change to ${result.data.analysis.modelSuggestion}`)
        }
      }
    } catch (error) {
      console.error('Failed to send feedback:', error)
      // Revert feedback state on error
      setMessages(prev => prev.map(m => 
        m.id === messageId ? { ...m, feedback: null } : m
      ))
    } finally {
      setFeedbackLoading(null)
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const getModelResponse = (model: string, userInput: string): string => {
    const responses: Record<string, string> = {
      'llama3.1:8b': `As your Full-Stack Architect, I'll help you design robust, scalable solutions with Material-UI components. For "${userInput}", I recommend a systematic approach with proper architecture patterns and performance optimization.`,
      'qwen2.5:7b': `From a UX/UI Designer perspective, let's focus on creating an intuitive user experience for "${userInput}" using Material-UI's design system. I'll help you design interfaces that are both beautiful and accessible.`,
      'mistral:7b': `As a Frontend Engineer, I'll help you implement "${userInput}" using modern web technologies with Material-UI components. Let's write clean, efficient code with React and TypeScript.`,
      'phi3:3.8b': `From a DevOps perspective, I'll help you deploy and monitor "${userInput}" effectively with Material-UI dashboards. Let's ensure reliability, scalability, and proper CI/CD practices.`,
      'llama3.2:3b': `As a Product Manager, I'll help you prioritize and plan "${userInput}" based on user needs and business value using Material-UI's design principles. Let's create a roadmap for success.`,
      'llava:7b': `As a Multimodal Specialist, I can analyze images and visual content related to "${userInput}" with Material-UI components. I'll help you understand visual elements and create multimodal experiences.`,
      'nomic-embed-text:latest': `As an Embedding Expert, I'll help you with semantic search and knowledge retrieval for "${userInput}" using Material-UI data display components. I can create vector embeddings and find relevant information.`,
      'gpt-oss:20b': `With advanced reasoning capabilities and Material-UI's comprehensive component library, I'll provide sophisticated analysis of "${userInput}". I can handle complex problem-solving and generate elegant solutions.`
    }
    return responses[model] || `I'll help you with "${userInput}" using my specialized capabilities and Material-UI's powerful components.`
  }

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      sender: 'user',
      timestamp: typeof window !== 'undefined' ? new Date() : new Date('2024-01-01T00:00:00Z')
    }

    setMessages(prev => [...prev, userMessage])
    const currentInput = input
    setInput('')
    setIsTyping(true)

    try {
      const request: ChatRequest = {
        message: currentInput,
        stream: false,
        customModelName: customModelName,
        conversationId: conversationId || undefined // Pass existing conversation ID
      }

      const response = await apiClient.sendMessage(request)

      // Update conversation ID if this is a new conversation
      
      // Handle auto-switching if enabled
      if (response.autoSwitching?.shouldSwitch && onSwitchPanel) {
        console.log(`🔄 Auto-switching to ${response.autoSwitching.targetPanel}: ${response.autoSwitching.reason}`)
        onSwitchPanel(response.autoSwitching.targetPanel)
      }
      if (response.id && response.id !== conversationId) {
        setConversationId(response.id)
      }

      const aiMessage: Message = {
        id: response.messageId || Date.now().toString(),
        content: response.message,
        sender: 'ai',
        model: response.model,
        detectedTask: response.detectedTask,
        timestamp: new Date(response.timestamp),
        feedback: null
      }

      setMessages(prev => [...prev, aiMessage])
      
      // Log enhanced system status
      if (response.conversationPersisted) {
        console.log(`✅ Conversation persisted: ${response.id}`)
      }
      if (response.contextAware) {
        console.log(`🧠 Context-aware response using ${response.model}`)
      }
      if (response.semanticSearch) {
        console.log(`🔍 Semantic search used for enhanced context`)
      }
      
      // Handle auto-switching to code editor
      if (response.autoSwitchToCodeEditor && onSwitchPanel) {
        console.log(`🔄 Auto-switching to code editor for coding task`)
        setTimeout(() => {
          onSwitchPanel('code')
        }, 1000) // Small delay to show the response first
      }
      
      console.log(`Real AI response from ${response.model} (conversation: ${response.id})`)

    } catch (error) {
      console.error('Error sending message:', error)

      const fallbackMessage: Message = {
        id: Date.now().toString(),
        content: `[Fallback] ${getModelResponse(activeModel, currentInput)}`,
        sender: 'ai',
        model: activeModel,
        timestamp: typeof window !== 'undefined' ? new Date() : new Date('2024-01-01T00:00:00Z')
      }

      setMessages(prev => [...prev, fallbackMessage])
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

  const panelStyles = getPanelStyles()
  
  return (
    <Box sx={panelStyles.container}>
      {/* Header */}
      <Paper
        elevation={0}
        sx={panelStyles.header}
      >
        <Stack direction="row" spacing={2} alignItems="center">
          <Avatar sx={designSystem.components.avatar}>
            <SmartToyIcon />
          </Avatar>
          <Box>
            <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
              AI Assistant
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              Your Personal AI • Smart Model Selection • Always Ready
            </Typography>
          </Box>
          <Box sx={{ flexGrow: 1 }} />
          
          {/* Advanced Features */}
          <Stack direction="row" spacing={1} alignItems="center">
            <Tooltip title="Chat History">
              <IconButton size="small" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                <HistoryIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Settings">
              <IconButton size="small" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                <SettingsIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Refresh">
              <IconButton size="small" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                <RefreshIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Stack>
        </Stack>
      </Paper>

      {/* Messages */}
      <Box sx={panelStyles.content}>
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
                      : 'rgba(255, 255, 255, 0.05)',
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
                        {isClient ? new Date(message.timestamp).toLocaleTimeString() : 'Loading...'}
                      </Typography>
                      
                      {message.sender === 'ai' && (
                        <Stack direction="row" spacing={0.5}>
                          <Tooltip title="Bookmark">
                            <IconButton size="small" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                              <BookmarkIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Good response - AI learns from positive feedback">
                            <IconButton 
                              size="small" 
                              disabled={feedbackLoading === message.id}
                              onClick={() => handleFeedback(message.id, 'thumbs_up')}
                              sx={{ 
                                color: message.feedback === 'thumbs_up' ? '#4caf50' : 'rgba(255, 255, 255, 0.5)',
                                '&:hover': { color: '#4caf50' }
                              }}
                            >
                              <ThumbUpIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Poor response - AI learns and improves">
                            <IconButton 
                              size="small" 
                              disabled={feedbackLoading === message.id}
                              onClick={() => handleFeedback(message.id, 'thumbs_down')}
                              sx={{ 
                                color: message.feedback === 'thumbs_down' ? '#f44336' : 'rgba(255, 255, 255, 0.5)',
                                '&:hover': { color: '#f44336' }
                              }}
                            >
                              <ThumbDownIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="More options">
                            <IconButton size="small" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                              <MoreVertIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Stack>
                      )}
                    </Stack>
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

      {/* Input Area */}
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
            placeholder="Ask me anything..."
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
              sx={{
                color: 'rgba(255, 255, 255, 0.7)',
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
    </Box>
  )
}
