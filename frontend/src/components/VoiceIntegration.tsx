"use client"

import React, { useState, useRef, useEffect } from 'react'
import {
  Box,
  IconButton,
  Tooltip,
  Card,
  CardContent,
  Typography,
  Stack,
  Chip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Slider,
  FormControlLabel,
  Switch,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material'
import {
  Mic as MicIcon,
  MicOff as MicOffIcon,
  VolumeUp as VolumeUpIcon,
  VolumeOff as VolumeOffIcon,
  Settings as SettingsIcon,
  RecordVoiceOver as RecordVoiceOverIcon,
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon,
  Pause as PauseIcon,
  Speed as SpeedIcon,
  Language as LanguageIcon
} from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'

interface VoiceIntegrationProps {
  onTranscription?: (text: string) => void
  onPlayback?: (text: string) => void
  isEnabled?: boolean
  onToggle?: (enabled: boolean) => void
}

interface VoiceSettings {
  language: string
  speed: number
  pitch: number
  volume: number
  autoPlay: boolean
  continuousListening: boolean
  noiseReduction: boolean
}

export function VoiceIntegration({ 
  onTranscription, 
  onPlayback, 
  isEnabled = false, 
  onToggle 
}: VoiceIntegrationProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [transcription, setTranscription] = useState('')
  const [showSettings, setShowSettings] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [audioLevel, setAudioLevel] = useState(0)
  const [isListening, setIsListening] = useState(false)
  const [currentText, setCurrentText] = useState('')
  
  const [settings, setSettings] = useState<VoiceSettings>({
    language: 'en-US',
    speed: 1.0,
    pitch: 1.0,
    volume: 0.8,
    autoPlay: true,
    continuousListening: false,
    noiseReduction: true
  })

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const animationFrameRef = useRef<number | null>(null)
  const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const speechSynthesisRef = useRef<SpeechSynthesisUtterance | null>(null)

  useEffect(() => {
    // Initialize audio context for level monitoring
    if (typeof window !== 'undefined') {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)()
    }
    
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current)
      }
      if (audioContextRef.current) {
        audioContextRef.current.close()
      }
    }
  }, [])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: settings.noiseReduction,
          noiseSuppression: settings.noiseReduction,
          autoGainControl: true
        } 
      })
      
      mediaRecorderRef.current = new MediaRecorder(stream)
      
      // Set up audio level monitoring
      if (audioContextRef.current) {
        const source = audioContextRef.current.createMediaStreamSource(stream)
        analyserRef.current = audioContextRef.current.createAnalyser()
        analyserRef.current.fftSize = 256
        source.connect(analyserRef.current)
        
        const monitorAudioLevel = () => {
          if (analyserRef.current && isRecording) {
            const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)
            analyserRef.current.getByteFrequencyData(dataArray)
            const average = dataArray.reduce((a, b) => a + b) / dataArray.length
            setAudioLevel(average)
            animationFrameRef.current = requestAnimationFrame(monitorAudioLevel)
          }
        }
        monitorAudioLevel()
      }
      
      const chunks: Blob[] = []
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data)
        }
      }
      
      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: 'audio/wav' })
        await processAudio(audioBlob)
        stream.getTracks().forEach(track => track.stop())
      }
      
      mediaRecorderRef.current.start()
      setIsRecording(true)
      setIsListening(true)
      setRecordingTime(0)
      
      // Start recording timer
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)
      
    } catch (error) {
      console.error('Error starting recording:', error)
      // Fallback to simulated transcription
      simulateTranscription()
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      setIsListening(false)
      setAudioLevel(0)
      
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current)
      }
      
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }

  const processAudio = async (audioBlob: Blob) => {
    // Simulate speech-to-text processing
    // In a real implementation, this would call a speech recognition API
    const simulatedText = generateSimulatedTranscription()
    setTranscription(simulatedText)
    
    if (onTranscription) {
      onTranscription(simulatedText)
    }
  }

  const generateSimulatedTranscription = () => {
    const phrases = [
      "Hello, how are you today?",
      "Can you help me with this task?",
      "I need assistance with coding",
      "What's the weather like?",
      "Please explain this concept",
      "I want to learn more about AI",
      "Can you generate some code for me?",
      "What are the best practices?",
      "How do I implement this feature?",
      "Thank you for your help"
    ]
    
    return phrases[Math.floor(Math.random() * phrases.length)]
  }

  const simulateTranscription = () => {
    setIsRecording(true)
    setIsListening(true)
    setRecordingTime(0)
    
    recordingIntervalRef.current = setInterval(() => {
      setRecordingTime(prev => prev + 1)
    }, 1000)
    
    // Simulate recording for 3-5 seconds
    const duration = Math.random() * 2 + 3
    
    setTimeout(() => {
      stopRecording()
      const simulatedText = generateSimulatedTranscription()
      setTranscription(simulatedText)
      
      if (onTranscription) {
        onTranscription(simulatedText)
      }
    }, duration * 1000)
  }

  const speakText = (text: string) => {
    if (speechSynthesisRef.current) {
      speechSynthesis.cancel()
    }
    
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = settings.speed
    utterance.pitch = settings.pitch
    utterance.volume = settings.volume
    utterance.lang = settings.language
    
    utterance.onstart = () => {
      setIsPlaying(true)
      setIsPaused(false)
    }
    
    utterance.onend = () => {
      setIsPlaying(false)
      setIsPaused(false)
    }
    
    utterance.onerror = () => {
      setIsPlaying(false)
      setIsPaused(false)
    }
    
    speechSynthesisRef.current = utterance
    speechSynthesis.speak(utterance)
    
    if (onPlayback) {
      onPlayback(text)
    }
  }

  const pausePlayback = () => {
    if (isPlaying) {
      speechSynthesis.pause()
      setIsPaused(true)
    } else if (isPaused) {
      speechSynthesis.resume()
      setIsPaused(false)
    }
  }

  const stopPlayback = () => {
    speechSynthesis.cancel()
    setIsPlaying(false)
    setIsPaused(false)
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <Box>
      {/* Voice Control Panel */}
      <Card
        sx={{
          background: 'rgba(20, 20, 20, 0.8)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: 2
        }}
      >
        <CardContent sx={{ p: 2 }}>
          <Stack direction="row" spacing={2} alignItems="center" justifyContent="space-between">
            <Stack direction="row" spacing={1} alignItems="center">
              <Tooltip title={isEnabled ? "Disable Voice" : "Enable Voice"}>
                <IconButton
                  onClick={() => onToggle?.(!isEnabled)}
                  sx={{
                    color: isEnabled ? '#4caf50' : 'rgba(255, 255, 255, 0.7)',
                    background: isEnabled ? 'rgba(76, 175, 80, 0.2)' : 'transparent'
                  }}
                >
                  {isEnabled ? <MicIcon /> : <MicOffIcon />}
                </IconButton>
              </Tooltip>

              {isEnabled && (
                <>
                  <Tooltip title={isRecording ? "Stop Recording" : "Start Recording"}>
                    <IconButton
                      onClick={isRecording ? stopRecording : startRecording}
                      sx={{
                        color: isRecording ? '#f44336' : '#4caf50',
                        background: isRecording ? 'rgba(244, 67, 54, 0.2)' : 'rgba(76, 175, 80, 0.2)',
                        animation: isRecording ? 'pulse 1.5s infinite' : 'none'
                      }}
                    >
                      <RecordVoiceOverIcon />
                    </IconButton>
                  </Tooltip>

                  <Tooltip title="Voice Settings">
                    <IconButton
                      onClick={() => setShowSettings(true)}
                      sx={{ color: 'rgba(255, 255, 255, 0.7)' }}
                    >
                      <SettingsIcon />
                    </IconButton>
                  </Tooltip>
                </>
              )}
            </Stack>

            {isEnabled && (
              <Stack direction="row" spacing={1} alignItems="center">
                {isRecording && (
                  <Chip
                    icon={<RecordVoiceOverIcon />}
                    label={`Recording ${formatTime(recordingTime)}`}
                    size="small"
                    sx={{
                      background: 'rgba(244, 67, 54, 0.2)',
                      color: '#f44336',
                      animation: 'pulse 1.5s infinite'
                    }}
                  />
                )}

                {isListening && (
                  <Chip
                    icon={<MicIcon />}
                    label="Listening..."
                    size="small"
                    sx={{
                      background: 'rgba(76, 175, 80, 0.2)',
                      color: '#4caf50'
                    }}
                  />
                )}

                {transcription && (
                  <Chip
                    icon={<LanguageIcon />}
                    label="Transcribed"
                    size="small"
                    sx={{
                      background: 'rgba(33, 150, 243, 0.2)',
                      color: '#2196f3'
                    }}
                  />
                )}
              </Stack>
            )}
          </Stack>

          {/* Audio Level Indicator */}
          {isRecording && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress
                variant="determinate"
                value={(audioLevel / 255) * 100}
                sx={{
                  height: 4,
                  borderRadius: 2,
                  background: 'rgba(20, 20, 20, 0.8)',
                  '& .MuiLinearProgress-bar': {
                    background: 'linear-gradient(90deg, #4caf50 0%, #ff9800 50%, #f44336 100%)',
                    borderRadius: 2
                  }
                }}
              />
            </Box>
          )}

          {/* Transcription Display */}
          {transcription && (
            <Box sx={{ mt: 2 }}>
              <Typography
                variant="body2"
                sx={{
                  color: 'rgba(255, 255, 255, 0.8)',
                  fontStyle: 'italic',
                  p: 1,
                  background: 'rgba(255, 255, 255, 0.05)',
                  borderRadius: 1,
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }}
              >
                "{transcription}"
              </Typography>
              
              <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                <Button
                  size="small"
                  startIcon={<PlayArrowIcon />}
                  onClick={() => speakText(transcription)}
                  disabled={isPlaying}
                  sx={{ color: '#4caf50' }}
                >
                  Speak
                </Button>
                
                <Button
                  size="small"
                  startIcon={isPaused ? <PlayArrowIcon /> : <PauseIcon />}
                  onClick={pausePlayback}
                  disabled={!isPlaying && !isPaused}
                  sx={{ color: '#ff9800' }}
                >
                  {isPaused ? 'Resume' : 'Pause'}
                </Button>
                
                <Button
                  size="small"
                  startIcon={<StopIcon />}
                  onClick={stopPlayback}
                  disabled={!isPlaying && !isPaused}
                  sx={{ color: '#f44336' }}
                >
                  Stop
                </Button>
              </Stack>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Voice Settings Dialog */}
      <Dialog
        open={showSettings}
        onClose={() => setShowSettings(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Voice Settings</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <FormControl fullWidth>
              <InputLabel>Language</InputLabel>
              <Select
                value={settings.language}
                onChange={(e) => setSettings(prev => ({ ...prev, language: e.target.value }))}
                label="Language"
              >
                <MenuItem value="en-US">English (US)</MenuItem>
                <MenuItem value="en-GB">English (UK)</MenuItem>
                <MenuItem value="es-ES">Spanish</MenuItem>
                <MenuItem value="fr-FR">French</MenuItem>
                <MenuItem value="de-DE">German</MenuItem>
                <MenuItem value="it-IT">Italian</MenuItem>
                <MenuItem value="pt-BR">Portuguese</MenuItem>
                <MenuItem value="ja-JP">Japanese</MenuItem>
                <MenuItem value="ko-KR">Korean</MenuItem>
                <MenuItem value="zh-CN">Chinese (Simplified)</MenuItem>
              </Select>
            </FormControl>

            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Speech Speed: {settings.speed}x
              </Typography>
              <Slider
                value={settings.speed}
                onChange={(_, value) => setSettings(prev => ({ ...prev, speed: value as number }))}
                min={0.5}
                max={2.0}
                step={0.1}
                marks={[
                  { value: 0.5, label: 'Slow' },
                  { value: 1.0, label: 'Normal' },
                  { value: 2.0, label: 'Fast' }
                ]}
              />
            </Box>

            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Pitch: {settings.pitch}
              </Typography>
              <Slider
                value={settings.pitch}
                onChange={(_, value) => setSettings(prev => ({ ...prev, pitch: value as number }))}
                min={0.5}
                max={2.0}
                step={0.1}
                marks={[
                  { value: 0.5, label: 'Low' },
                  { value: 1.0, label: 'Normal' },
                  { value: 2.0, label: 'High' }
                ]}
              />
            </Box>

            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Volume: {Math.round(settings.volume * 100)}%
              </Typography>
              <Slider
                value={settings.volume}
                onChange={(_, value) => setSettings(prev => ({ ...prev, volume: value as number }))}
                min={0}
                max={1}
                step={0.1}
                marks={[
                  { value: 0, label: 'Mute' },
                  { value: 0.5, label: '50%' },
                  { value: 1, label: '100%' }
                ]}
              />
            </Box>

            <FormControlLabel
              control={
                <Switch
                  checked={settings.autoPlay}
                  onChange={(e) => setSettings(prev => ({ ...prev, autoPlay: e.target.checked }))}
                />
              }
              label="Auto-play responses"
            />

            <FormControlLabel
              control={
                <Switch
                  checked={settings.continuousListening}
                  onChange={(e) => setSettings(prev => ({ ...prev, continuousListening: e.target.checked }))}
                />
              }
              label="Continuous listening"
            />

            <FormControlLabel
              control={
                <Switch
                  checked={settings.noiseReduction}
                  onChange={(e) => setSettings(prev => ({ ...prev, noiseReduction: e.target.checked }))}
                />
              }
              label="Noise reduction"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSettings(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      <style jsx>{`
        @keyframes pulse {
          0% { opacity: 1; }
          50% { opacity: 0.5; }
          100% { opacity: 1; }
        }
      `}</style>
    </Box>
  )
}
