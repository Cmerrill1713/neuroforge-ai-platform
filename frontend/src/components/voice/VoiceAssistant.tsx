'use client'

import React, { useState, useEffect, useRef } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  IconButton,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  LinearProgress,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material'
import {
  Mic as MicIcon,
  MicOff as MicOffIcon,
  VolumeUp as VolumeUpIcon,
  VolumeOff as VolumeOffIcon,
  SmartToy as SmartToyIcon,
  RecordVoiceOver as RecordVoiceOverIcon,
  PlayArrow as PlayArrowIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  Settings as SettingsIcon,
  History as HistoryIcon,
  Star as StarIcon,
  AutoAwesome as AutoAwesomeIcon
} from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'

interface VoiceCommand {
  id: string
  command: string
  response: string
  timestamp: number
  confidence: number
  executed: boolean
}

interface VoiceAssistantProps {
  onCommand: (command: string, confidence: number) => void
  onResponse: (response: string) => void
}

export function VoiceAssistant({ onCommand, onResponse }: VoiceAssistantProps) {
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [commands, setCommands] = useState<VoiceCommand[]>([])
  const [currentTranscript, setCurrentTranscript] = useState('')
  const [confidence, setConfidence] = useState(0)
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const [showHistory, setShowHistory] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [language, setLanguage] = useState('en-US')
  const [voiceSpeed, setVoiceSpeed] = useState(1)
  const [voicePitch, setVoicePitch] = useState(1)
  
  const recognitionRef = useRef<any>(null)
  const synthesisRef = useRef<SpeechSynthesisUtterance | null>(null)

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = true
      recognitionRef.current.lang = language
      recognitionRef.current.maxAlternatives = 1
      
      recognitionRef.current.onstart = () => {
        setIsListening(true)
        setIsProcessing(false)
      }
      
      recognitionRef.current.onresult = (event: any) => {
        let interimTranscript = ''
        let finalTranscript = ''
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          if (event.results[i].isFinal) {
            finalTranscript += transcript
            setConfidence(event.results[i][0].confidence)
          } else {
            interimTranscript += transcript
          }
        }
        
        setCurrentTranscript(interimTranscript)
        
        if (finalTranscript) {
          processCommand(finalTranscript.trim())
        }
      }
      
      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error)
        setIsListening(false)
        setIsProcessing(false)
      }
      
      recognitionRef.current.onend = () => {
        setIsListening(false)
        setCurrentTranscript('')
      }
    }
  }, [language, processCommand])

  // Process voice commands
  const processCommand = useCallback(async (command: string) => {
    setIsProcessing(true)
    
    const voiceCommand: VoiceCommand = {
      id: Date.now().toString(),
      command,
      response: '',
      timestamp: Date.now(),
      confidence,
      executed: false
    }
    
    setCommands(prev => [voiceCommand, ...prev.slice(0, 19)])
    
    try {
      // AI command processing
      const response = await processAICommand(command)
      voiceCommand.response = response
      voiceCommand.executed = true
      
      // Update commands list
      setCommands(prev => prev.map(cmd => 
        cmd.id === voiceCommand.id ? voiceCommand : cmd
      ))
      
      // Execute command
      onCommand(command, confidence)
      
      // Speak response
      if (voiceEnabled) {
        speak(response)
      }
      
      onResponse(response)
      
    } catch (error) {
      console.error('Command processing error:', error)
      voiceCommand.response = 'Sorry, I didn\'t understand that command.'
      voiceCommand.executed = false
      
      setCommands(prev => prev.map(cmd => 
        cmd.id === voiceCommand.id ? voiceCommand : cmd
      ))
    } finally {
      setIsProcessing(false)
    }
  }, [confidence, voiceEnabled, onCommand, onResponse, speak])

  // AI command processing
  const processAICommand = async (command: string): Promise<string> => {
    const lowerCommand = command.toLowerCase()
    
    // Navigation commands
    if (lowerCommand.includes('go to') || lowerCommand.includes('open') || lowerCommand.includes('switch to')) {
      if (lowerCommand.includes('chat') || lowerCommand.includes('assistant')) {
        return 'Switching to AI Assistant panel'
      } else if (lowerCommand.includes('code') || lowerCommand.includes('programming')) {
        return 'Opening Code Assistant'
      } else if (lowerCommand.includes('vision') || lowerCommand.includes('image')) {
        return 'Opening Vision Assistant'
      } else if (lowerCommand.includes('learning') || lowerCommand.includes('progress')) {
        return 'Opening Learning Hub'
      } else if (lowerCommand.includes('agents') || lowerCommand.includes('automation')) {
        return 'Opening AI Agents panel'
      } else if (lowerCommand.includes('optimization') || lowerCommand.includes('productivity')) {
        return 'Opening Self-Optimization panel'
      }
    }
    
    // Theme commands
    if (lowerCommand.includes('theme') || lowerCommand.includes('color')) {
      if (lowerCommand.includes('dark')) {
        return 'Switching to dark theme'
      } else if (lowerCommand.includes('light')) {
        return 'Switching to light theme'
      } else if (lowerCommand.includes('blue')) {
        return 'Applying blue theme'
      } else if (lowerCommand.includes('purple')) {
        return 'Applying purple theme'
      } else if (lowerCommand.includes('green')) {
        return 'Applying green theme'
      }
    }
    
    // Voice commands
    if (lowerCommand.includes('voice') || lowerCommand.includes('speech')) {
      if (lowerCommand.includes('on') || lowerCommand.includes('enable')) {
        setVoiceEnabled(true)
        return 'Voice feedback enabled'
      } else if (lowerCommand.includes('off') || lowerCommand.includes('disable')) {
        setVoiceEnabled(false)
        return 'Voice feedback disabled'
      }
    }
    
    // Help commands
    if (lowerCommand.includes('help') || lowerCommand.includes('what can you do')) {
      return 'I can help you navigate panels, change themes, control voice settings, and much more. Try saying "go to code assistant" or "switch to dark theme"'
    }
    
    // Default response
    return `I heard: "${command}". I'm processing your request.`
  }

  // Text-to-speech
  const speak = useCallback((text: string) => {
    if ('speechSynthesis' in window) {
      if (synthesisRef.current) {
        speechSynthesis.cancel()
      }
      
      synthesisRef.current = new SpeechSynthesisUtterance(text)
      synthesisRef.current.rate = voiceSpeed
      synthesisRef.current.pitch = voicePitch
      synthesisRef.current.volume = 0.8
      
      synthesisRef.current.onstart = () => setIsSpeaking(true)
      synthesisRef.current.onend = () => setIsSpeaking(false)
      synthesisRef.current.onerror = () => setIsSpeaking(false)
      
      speechSynthesis.speak(synthesisRef.current)
    }
  }, [voiceSpeed, voicePitch])

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      recognitionRef.current.start()
    }
  }

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop()
    }
  }

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      speechSynthesis.cancel()
      setIsSpeaking(false)
    }
  }

  const clearHistory = () => {
    setCommands([])
  }

  const getConfidenceColor = (conf: number) => {
    if (conf > 0.8) return 'success'
    if (conf > 0.6) return 'warning'
    return 'error'
  }

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
        <RecordVoiceOverIcon color="primary" />
        Voice Assistant
        <Chip 
          label={isListening ? "Listening" : isProcessing ? "Processing" : isSpeaking ? "Speaking" : "Ready"} 
          color={isListening ? "success" : isProcessing ? "warning" : isSpeaking ? "info" : "default"}
          size="small"
        />
      </Typography>

      {/* Voice Controls */}
      <Card sx={{ mb: 2, background: 'rgba(255, 255, 255, 0.05)' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <IconButton
              onClick={isListening ? stopListening : startListening}
              sx={{
                background: isListening ? 'rgba(255, 0, 0, 0.2)' : 'rgba(255, 255, 255, 0.1)',
                color: isListening ? 'error.main' : 'text.secondary',
                '&:hover': {
                  background: isListening ? 'rgba(255, 0, 0, 0.3)' : 'rgba(255, 255, 255, 0.2)',
                }
              }}
            >
              {isListening ? <MicOffIcon /> : <MicIcon />}
            </IconButton>
            
            <Box sx={{ flex: 1 }}>
              <Typography variant="body2" color="text.secondary">
                {isListening ? 'Listening...' : 'Click to start voice command'}
              </Typography>
              {currentTranscript && (
                <Typography variant="body1" sx={{ mt: 1, fontStyle: 'italic' }}>
                  &quot;{currentTranscript}&quot;
                </Typography>
              )}
            </Box>
            
            <IconButton onClick={() => setShowHistory(true)}>
              <HistoryIcon />
            </IconButton>
            
            <IconButton onClick={() => setShowSettings(true)}>
              <SettingsIcon />
            </IconButton>
          </Box>

          {/* Voice Status */}
          {isListening && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              <LinearProgress sx={{ flex: 1 }} />
              <Typography variant="caption" color="text.secondary">
                Listening...
              </Typography>
            </Box>
          )}

          {/* Quick Commands */}
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {[
              'Go to Code Assistant',
              'Switch to Dark Theme',
              'Open Learning Hub',
              'Enable Voice Feedback',
              'What can you do?'
            ].map((command) => (
              <Chip
                key={command}
                label={command}
                onClick={() => processCommand(command)}
                sx={{ cursor: 'pointer' }}
                size="small"
              />
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Recent Commands */}
      {commands.length > 0 && (
        <Card sx={{ background: 'rgba(255, 255, 255, 0.05)' }}>
          <CardContent>
            <Typography variant="subtitle1" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
              <HistoryIcon />
              Recent Commands
              <IconButton size="small" onClick={clearHistory}>
                <StopIcon />
              </IconButton>
            </Typography>
            
            <List sx={{ maxHeight: 300, overflow: 'auto' }}>
              <AnimatePresence>
                {commands.slice(0, 5).map((cmd) => (
                  <motion.div
                    key={cmd.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                  >
                    <ListItem sx={{ px: 0 }}>
                      <ListItemIcon>
                        <Avatar sx={{ width: 32, height: 32, bgcolor: cmd.executed ? 'success.main' : 'error.main' }}>
                          <SmartToyIcon fontSize="small" />
                        </Avatar>
                      </ListItemIcon>
                      <ListItemText
                        primary={cmd.command}
                        secondary={
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              {cmd.response}
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                              <Chip
                                label={`${(cmd.confidence * 100).toFixed(0)}%`}
                                color={getConfidenceColor(cmd.confidence)}
                                size="small"
                              />
                              <Chip
                                label={new Date(cmd.timestamp).toLocaleTimeString()}
                                size="small"
                                variant="outlined"
                              />
                            </Box>
                          </Box>
                        }
                      />
                    </ListItem>
                  </motion.div>
                ))}
              </AnimatePresence>
            </List>
          </CardContent>
        </Card>
      )}

      {/* Settings Dialog */}
      <Dialog open={showSettings} onClose={() => setShowSettings(false)}>
        <DialogTitle>Voice Assistant Settings</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, minWidth: 300 }}>
            <Box>
              <Typography gutterBottom>Language</Typography>
              <Button
                variant={language === 'en-US' ? 'contained' : 'outlined'}
                onClick={() => setLanguage('en-US')}
                size="small"
                sx={{ mr: 1 }}
              >
                English
              </Button>
              <Button
                variant={language === 'es-ES' ? 'contained' : 'outlined'}
                onClick={() => setLanguage('es-ES')}
                size="small"
              >
                Spanish
              </Button>
            </Box>
            
            <Box>
              <Typography gutterBottom>Voice Speed: {voiceSpeed}x</Typography>
              <LinearProgress 
                variant="determinate" 
                value={voiceSpeed * 50} 
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
            
            <Box>
              <Typography gutterBottom>Voice Pitch: {voicePitch}x</Typography>
              <LinearProgress 
                variant="determinate" 
                value={voicePitch * 50} 
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSettings(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
