import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Switch,
  FormControlLabel,
  TextField,
  Button,
  Chip,
  IconButton,
  Tooltip,
  Slider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Divider,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Mic as MicIcon,
  MicOff as MicOffIcon,
  VolumeUp as VolumeUpIcon,
  VolumeOff as VolumeOffIcon,
  Settings as SettingsIcon,
  Refresh as RefreshIcon,
  RecordVoiceOver as RecordVoiceOverIcon,
  SmartToy as SmartToyIcon,
} from '@mui/icons-material';
import { useVoiceAgent } from '../../hooks/useVoiceAgent';

interface VoiceAgentControlPanelProps {
  onVoiceMessage?: (message: string) => void;
  onVoiceResponse?: (response: string) => void;
}

export const VoiceAgentControlPanel: React.FC<VoiceAgentControlPanelProps> = ({
  onVoiceMessage,
  onVoiceResponse,
}) => {
  const [showSettings, setShowSettings] = useState(false);
  const [speechRate, setSpeechRate] = useState(1);
  const [speechPitch, setSpeechPitch] = useState(1);
  const [speechVolume, setSpeechVolume] = useState(1);

  const voiceAgent = useVoiceAgent({
    autoSpeakResponses: true,
    wakeWordEnabled: true,
    wakeWord: 'hey assistant',
    continuousMode: false,
    voiceModel: 'qwen2.5:7b'
  });

  const {
    isActive,
    isListening,
    isSpeaking,
    wakeWordDetected,
    processingMessage,
    lastResponse,
    transcript,
    voiceError,
    speakError,
    availableVoices,
    toggleVoiceAgent,
    resetVoiceAgent,
    setAutoSpeakResponses,
    setWakeWordEnabled,
    setWakeWord,
    setContinuousMode,
    setVoiceModel,
    speak,
  } = voiceAgent;

  const handleVoiceMessage = (message: string) => {
    onVoiceMessage?.(message);
  };

  const handleVoiceResponse = (response: string) => {
    onVoiceResponse?.(response);
  };

  const handleSpeak = async (text: string) => {
    await speak(text);
    handleVoiceResponse(text);
  };

  const getStatusColor = () => {
    if (processingMessage) return '#ff9800';
    if (isSpeaking) return '#4caf50';
    if (isListening) return '#2196f3';
    if (wakeWordDetected) return '#9c27b0';
    if (isActive) return '#00bcd4';
    return '#9e9e9e';
  };

  const getStatusText = () => {
    if (processingMessage) return 'Processing...';
    if (isSpeaking) return 'Speaking';
    if (isListening) return 'Listening';
    if (wakeWordDetected) return 'Wake Word Detected';
    if (isActive) return 'Voice Agent Active';
    return 'Voice Agent Inactive';
  };

  return (
    <Paper sx={{
      p: 3,
      background: 'rgba(10, 10, 10, 0.8)',
      backdropFilter: 'blur(20px)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: 3,
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
    }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <SmartToyIcon sx={{ color: getStatusColor(), fontSize: 32 }} />
          <Box>
            <Typography variant="h5" sx={{ color: 'white', fontWeight: 600 }}>
              Voice Agent
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              {getStatusText()}
            </Typography>
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title="Settings">
            <IconButton
              onClick={() => setShowSettings(!showSettings)}
              sx={{ color: 'white' }}
            >
              <SettingsIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Reset Voice Agent">
            <IconButton
              onClick={resetVoiceAgent}
              sx={{ color: 'white' }}
            >
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Status Indicators */}
      <Box sx={{ display: 'flex', gap: 1, mb: 3, flexWrap: 'wrap' }}>
        <Chip
          icon={<MicIcon />}
          label={isListening ? 'Listening' : 'Not Listening'}
          color={isListening ? 'success' : 'default'}
          size="small"
        />
        <Chip
          icon={<VolumeUpIcon />}
          label={isSpeaking ? 'Speaking' : 'Silent'}
          color={isSpeaking ? 'success' : 'default'}
          size="small"
        />
        {wakeWordDetected && (
          <Chip
            icon={<RecordVoiceOverIcon />}
            label="Wake Word Detected"
            color="secondary"
            size="small"
          />
        )}
        {processingMessage && (
          <Chip
            icon={<CircularProgress size={16} />}
            label="Processing"
            color="warning"
            size="small"
          />
        )}
      </Box>

      {/* Main Control */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
        <Button
          variant="contained"
          size="large"
          onClick={toggleVoiceAgent}
          startIcon={isActive ? <MicOffIcon /> : <MicIcon />}
          sx={{
            minWidth: 200,
            height: 60,
            background: isActive 
              ? 'linear-gradient(135deg, #f44336 0%, #d32f2f 100%)'
              : 'linear-gradient(135deg, #4caf50 0%, #388e3c 100%)',
            '&:hover': {
              background: isActive 
                ? 'linear-gradient(135deg, #d32f2f 0%, #b71c1c 100%)'
                : 'linear-gradient(135deg, #388e3c 0%, #2e7d32 100%)',
            },
            fontSize: '1.1rem',
            fontWeight: 600,
            borderRadius: 3,
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.3)',
          }}
        >
          {isActive ? 'Stop Voice Agent' : 'Start Voice Agent'}
        </Button>
      </Box>

      {/* Current Transcript */}
      {transcript && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
            Current Transcript:
          </Typography>
          <Paper sx={{ p: 2, backgroundColor: 'rgba(255, 255, 255, 0.05)' }}>
            <Typography variant="body1" sx={{ color: 'white' }}>
              {transcript}
            </Typography>
          </Paper>
        </Box>
      )}

      {/* Last Response */}
      {lastResponse && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
            Last Response:
          </Typography>
          <Paper sx={{ p: 2, backgroundColor: 'rgba(255, 255, 255, 0.05)' }}>
            <Typography variant="body1" sx={{ color: 'white', mb: 2 }}>
              {lastResponse}
            </Typography>
            <Button
              variant="outlined"
              size="small"
              startIcon={<VolumeUpIcon />}
              onClick={() => handleSpeak(lastResponse)}
              sx={{ color: 'white', borderColor: 'rgba(255, 255, 255, 0.3)' }}
            >
              Speak Response
            </Button>
          </Paper>
        </Box>
      )}

      {/* Error Messages */}
      {(voiceError || speakError) && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {voiceError || speakError}
        </Alert>
      )}

      {/* Settings Panel */}
      {showSettings && (
        <Box sx={{ mt: 3 }}>
          <Divider sx={{ mb: 3, borderColor: 'rgba(255, 255, 255, 0.1)' }} />
          
          <Typography variant="h6" sx={{ color: 'white', mb: 2 }}>
            Voice Agent Settings
          </Typography>

          {/* Basic Settings */}
          <Box sx={{ mb: 3 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={voiceAgent.config?.autoSpeakResponses || false}
                  onChange={(e) => setAutoSpeakResponses(e.target.checked)}
                  sx={{
                    '& .MuiSwitch-switchBase.Mui-checked': {
                      color: '#1976d2',
                    },
                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                      backgroundColor: '#1976d2',
                    },
                  }}
                />
              }
              label="Auto-speak responses"
              sx={{ color: 'white' }}
            />
          </Box>

          <Box sx={{ mb: 3 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={voiceAgent.config?.wakeWordEnabled || false}
                  onChange={(e) => setWakeWordEnabled(e.target.checked)}
                  sx={{
                    '& .MuiSwitch-switchBase.Mui-checked': {
                      color: '#1976d2',
                    },
                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                      backgroundColor: '#1976d2',
                    },
                  }}
                />
              }
              label="Wake word detection"
              sx={{ color: 'white' }}
            />
          </Box>

          <Box sx={{ mb: 3 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={voiceAgent.config?.continuousMode || false}
                  onChange={(e) => setContinuousMode(e.target.checked)}
                  sx={{
                    '& .MuiSwitch-switchBase.Mui-checked': {
                      color: '#1976d2',
                    },
                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                      backgroundColor: '#1976d2',
                    },
                  }}
                />
              }
              label="Continuous listening"
              sx={{ color: 'white' }}
            />
          </Box>

          {/* Wake Word Setting */}
          <Box sx={{ mb: 3 }}>
            <TextField
              label="Wake Word"
              value={voiceAgent.config?.wakeWord || 'hey assistant'}
              onChange={(e) => setWakeWord(e.target.value)}
              fullWidth
              size="small"
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  color: 'white',
                  '& fieldset': {
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                  },
                },
                '& .MuiInputLabel-root': {
                  color: 'rgba(255, 255, 255, 0.7)',
                },
              }}
            />
          </Box>

          {/* Voice Model Selection */}
          <Box sx={{ mb: 3 }}>
            <FormControl fullWidth size="small">
              <InputLabel sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Voice Model</InputLabel>
              <Select
                value={voiceAgent.config?.voiceModel || 'qwen2.5:7b'}
                onChange={(e) => setVoiceModel(e.target.value)}
                sx={{
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  color: 'white',
                  '& .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                  },
                }}
              >
                <MenuItem value="qwen2.5:7b">Qwen2.5-7B</MenuItem>
                <MenuItem value="qwen2.5:14b">Qwen2.5-14B</MenuItem>
                <MenuItem value="mistral:7b">Mistral-7B</MenuItem>
                <MenuItem value="llama3.2:3b">Llama3.2-3B</MenuItem>
              </Select>
            </FormControl>
          </Box>

          {/* Speech Settings */}
          <Typography variant="subtitle2" sx={{ color: 'white', mb: 2 }}>
            Speech Settings
          </Typography>

          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
              Speech Rate: {speechRate}
            </Typography>
            <Slider
              value={speechRate}
              onChange={(_, value) => setSpeechRate(value as number)}
              min={0.5}
              max={2}
              step={0.1}
              sx={{
                color: '#1976d2',
                '& .MuiSlider-thumb': {
                  backgroundColor: '#1976d2',
                },
              }}
            />
          </Box>

          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
              Speech Pitch: {speechPitch}
            </Typography>
            <Slider
              value={speechPitch}
              onChange={(_, value) => setSpeechPitch(value as number)}
              min={0.5}
              max={2}
              step={0.1}
              sx={{
                color: '#1976d2',
                '& .MuiSlider-thumb': {
                  backgroundColor: '#1976d2',
                },
              }}
            />
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
              Speech Volume: {speechVolume}
            </Typography>
            <Slider
              value={speechVolume}
              onChange={(_, value) => setSpeechVolume(value as number)}
              min={0}
              max={1}
              step={0.1}
              sx={{
                color: '#1976d2',
                '& .MuiSlider-thumb': {
                  backgroundColor: '#1976d2',
                },
              }}
            />
          </Box>
        </Box>
      )}
    </Paper>
  );
};
