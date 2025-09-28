import React, { useState, useCallback, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  IconButton,
  Paper,
  Button,
  CircularProgress,
  Chip,
  Tooltip,
  Alert,
  Fade,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Send as SendIcon,
  Clear as ClearIcon,
  Mic as MicIcon,
  MicOff as MicOffIcon,
  ContentCopy as CopyIcon,
  AttachFile as AttachFileIcon,
  Close as CloseIcon,
  RecordVoiceOver as RecordVoiceOverIcon,
} from '@mui/icons-material';
import { ChatInterfaceProps } from '../../types';
import { useAppContext } from '../../contexts/AppContext';
import { ChatMessage } from './ChatMessage';
import { useVoiceInput } from '../../hooks/useVoiceInput';
import { useVoiceAgent } from '../../hooks/useVoiceAgent';
import { useDragDrop } from '../../hooks/useDragDrop';
import { useCopy } from '../../hooks/useCopy';
import LLMMonitoringDashboard from '../monitoring/LLMMonitoringDashboard';
import SettingsPanel from '../settings/SettingsPanel';
import AgentsManagementPanel from '../agents/AgentsManagementPanel';
import SelfOptimizationPanel from '../Optimization/SelfOptimizationPanel';
import { VoiceAgentControlPanel } from '../voice/VoiceAgentControlPanel';
import { DIALLM } from '../LLM/DIALLM';

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  activePanel,
  onSendMessage,
}) => {
  const [inputValue, setInputValue] = useState('');
  const [isClient, setIsClient] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const { state, sendMessage } = useAppContext();
  const { messages, isLoading } = state;

  // Ensure we're on the client side to prevent hydration mismatches
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Voice agent functionality
  const voiceAgent = useVoiceAgent({
    autoSpeakResponses: true,
    wakeWordEnabled: true,
    wakeWord: 'hey assistant',
    continuousMode: false,
    voiceModel: 'qwen2.5:7b'
  });

  // Legacy voice input functionality (for backward compatibility)
  const {
    isListening: legacyIsListening,
    isSupported: voiceSupported,
    transcript,
    error: voiceError,
    startListening: legacyStartListening,
    stopListening: legacyStopListening,
    clearTranscript,
  } = useVoiceInput();

  // Drag and drop functionality
  const {
    isDragOver,
    droppedItems,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    clearItems,
    removeItem,
  } = useDragDrop();

  // Copy functionality
  const { isCopied, copyMessage, copyCodeBlock } = useCopy();

  // Update input when voice transcript changes
  useEffect(() => {
    if (transcript) {
      setInputValue(transcript);
    }
  }, [transcript]);

  // Handle voice agent messages
  const handleVoiceMessage = useCallback((message: string) => {
    console.log('🎤 Voice message received:', message);
    setInputValue(message);
  }, []);

  const handleVoiceResponse = useCallback((response: string) => {
    console.log('🤖 Voice response:', response);
  }, []);

  const handleSendMessage = useCallback(async () => {
    if (inputValue.trim()) {
      await sendMessage(inputValue.trim());
      onSendMessage(inputValue.trim());
      setInputValue('');
      clearTranscript();
    }
  }, [inputValue, sendMessage, onSendMessage, clearTranscript]);

  const handleClearMessages = useCallback(() => {
    console.log('Clear messages clicked');
  }, []);

  const handleKeyPress = useCallback((event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  }, [handleSendMessage]);

  const handleVoiceToggle = useCallback(() => {
    if (legacyIsListening) {
      legacyStopListening();
    } else {
      legacyStartListening();
    }
  }, [legacyIsListening, legacyStartListening, legacyStopListening]);

  const handleCopyMessage = useCallback(async (message: string) => {
    await copyMessage(message);
  }, [copyMessage]);

  const handleCopyCode = useCallback(async (code: string, language?: string) => {
    await copyCodeBlock(code, language);
  }, [copyCodeBlock]);

  const handleFileUpload = useCallback((files: FileList) => {
    console.log('Files uploaded:', files);
  }, []);

  // Render different panels based on active panel
  if (activePanel === 'monitoring') {
    return <LLMMonitoringDashboard />;
  }
  
  if (activePanel === 'agents') {
    return <AgentsManagementPanel />;
  }
  
  if (activePanel === 'settings') {
    return <SettingsPanel />;
  }
  
  if (activePanel === 'optimization') {
    return <SelfOptimizationPanel />;
  }

  // Voice Agent Panel
  if (activePanel === 'voice') {
    return (
      <VoiceAgentControlPanel
        onVoiceMessage={handleVoiceMessage}
        onVoiceResponse={handleVoiceResponse}
      />
    );
  }

  // DIA LLM Panel
  if (activePanel === 'dia') {
    return <DIALLM />;
  }

  return (
    <Box 
      sx={{
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: 3,
        p: 3,
        background: 'rgba(10, 10, 10, 0.8)',
        backdropFilter: 'blur(20px)',
        flexGrow: 1,
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
        minHeight: 400,
        maxHeight: '90vh',
        resize: 'vertical',
        overflow: 'auto',
        position: 'relative',
        '&:hover': {
          borderColor: 'rgba(255, 255, 255, 0.2)',
        },
        ...(isDragOver && {
          borderColor: '#4caf50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          borderStyle: 'dashed',
        }),
      }}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Drag and Drop Indicator */}
      {isDragOver && (
        <Fade in={isDragOver}>
          <Box sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'rgba(76, 175, 80, 0.1)',
            backdropFilter: 'blur(10px)',
            zIndex: 1000,
            borderRadius: 3,
          }}>
            <Typography variant="h5" sx={{ color: '#4caf50', fontWeight: 600 }}>
              Drop files here to upload
            </Typography>
          </Box>
        </Fade>
      )}

      {/* Voice Error Alert */}
      {voiceError && (
        <Alert severity="error" sx={{ mb: 2, backgroundColor: 'rgba(244, 67, 54, 0.1)', color: 'white' }}>
          {voiceError}
        </Alert>
      )}

      {/* Dropped Files Display */}
      {droppedItems.length > 0 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
            Dropped Files:
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {droppedItems.map((item) => (
              <Chip
                key={item.id}
                label={`${item.name} (${(item.size / 1024).toFixed(1)}KB)`}
                onDelete={() => removeItem(item.id)}
                sx={{
                  backgroundColor: 'rgba(76, 175, 80, 0.2)',
                  color: 'white',
                  '& .MuiChip-deleteIcon': {
                    color: 'rgba(255, 255, 255, 0.7)',
                  },
                }}
              />
            ))}
          </Box>
        </Box>
      )}

      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2, flexShrink: 0 }}>
        <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
          Chat Interface
        </Typography>
        
        {/* Voice Agent Status */}
        {voiceAgent.isActive && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              icon={<RecordVoiceOverIcon />}
              label="Voice Agent Active"
              color="primary"
              size="small"
              sx={{ backgroundColor: 'rgba(25, 118, 210, 0.2)', color: 'white' }}
            />
            {voiceAgent.wakeWordDetected && (
              <Chip
                label="Wake Word Detected"
                color="secondary"
                size="small"
                sx={{ backgroundColor: 'rgba(156, 39, 176, 0.2)', color: 'white' }}
              />
            )}
            {voiceAgent.processingMessage && (
              <Chip
                icon={<CircularProgress size={16} />}
                label="Processing"
                color="warning"
                size="small"
                sx={{ backgroundColor: 'rgba(255, 152, 0, 0.2)', color: 'white' }}
              />
            )}
          </Box>
        )}
        
        <Box sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          color: 'rgba(255, 255, 255, 0.5)',
          fontSize: '0.75rem'
        }}>
          <Box sx={{
            width: '16px',
            height: '16px',
            background: 'repeating-linear-gradient(45deg, rgba(255,255,255,0.1), rgba(255,255,255,0.1) 2px, transparent 2px, transparent 4px)',
            borderRadius: '2px'
          }} />
          <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
            Resize
          </Typography>
        </Box>
      </Box>

      <Paper sx={{ 
        border: '1px solid rgba(255, 255, 255, 0.1)', 
        borderRadius: 2, 
        p: 3, 
        mb: 3,
        flexGrow: 1,
        background: 'rgba(5, 5, 5, 0.6)',
        backdropFilter: 'blur(10px)',
        overflow: 'auto',
        minHeight: 0,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between'
      }}>
        <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
          {messages.length === 0 ? (
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.5)', fontStyle: 'italic' }}>
              Chat messages will appear here...
            </Typography>
          ) : (
            messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))
          )}
        </Box>
        {messages.length > 0 && (
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              startIcon={<ClearIcon />}
              onClick={handleClearMessages}
              size="small"
              sx={{
                color: 'rgba(255, 255, 255, 0.6)',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                },
              }}
            >
              Clear Chat
            </Button>
          </Box>
        )}
      </Paper>

      <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-end', flexShrink: 0 }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask me anything..."
          variant="outlined"
          sx={{
            '& .MuiOutlinedInput-root': {
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              color: 'white',
              '& fieldset': {
                borderColor: 'rgba(255, 255, 255, 0.2)',
              },
              '&:hover fieldset': {
                borderColor: 'rgba(255, 255, 255, 0.3)',
              },
              '&.Mui-focused fieldset': {
                borderColor: '#1976d2',
                boxShadow: '0 0 0 2px rgba(25, 118, 210, 0.2)',
              },
            },
            '& .MuiInputBase-input': {
              color: 'white',
              '&::placeholder': {
                color: 'rgba(255, 255, 255, 0.5)',
                opacity: 1,
              },
            },
          }}
        />
        
        {/* Voice Agent Button */}
        {isClient && voiceSupported && (
          <Tooltip title={voiceAgent.isActive ? "Stop Voice Agent" : "Start Voice Agent"}>
            <IconButton
              onClick={voiceAgent.toggleVoiceAgent}
              sx={{
                padding: '12px',
                background: voiceAgent.isActive 
                  ? 'linear-gradient(135deg, #f44336 0%, #d32f2f 100%)'
                  : 'linear-gradient(135deg, #4caf50 0%, #388e3c 100%)',
                color: 'white',
                borderRadius: '12px',
                transition: 'all 0.3s ease',
                boxShadow: '0 4px 16px rgba(0, 0, 0, 0.2)',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: '0 6px 20px rgba(0, 0, 0, 0.3)',
                },
              }}
            >
              {voiceAgent.isActive ? <MicOffIcon /> : <MicIcon />}
            </IconButton>
          </Tooltip>
        )}

        {/* File Upload Button */}
        <Tooltip title="Upload files">
          <IconButton
            component="label"
            sx={{
              padding: '12px',
              background: 'linear-gradient(135deg, #ff9800 0%, #f57c00 100%)',
              color: 'white',
              borderRadius: '12px',
              transition: 'all 0.3s ease',
              boxShadow: '0 4px 16px rgba(0, 0, 0, 0.2)',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 6px 20px rgba(0, 0, 0, 0.3)',
              },
            }}
          >
            <AttachFileIcon />
            <input
              type="file"
              hidden
              multiple
              onChange={(e) => e.target.files && handleFileUpload(e.target.files)}
            />
          </IconButton>
        </Tooltip>

        <IconButton
          onClick={handleSendMessage}
          disabled={!inputValue.trim() || isLoading}
          sx={{
            backgroundColor: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
            color: 'white',
            width: 56,
            height: 56,
            '&:hover': {
              backgroundColor: 'linear-gradient(135deg, #1565c0 0%, #0d47a1 100%)',
              transform: 'translateY(-2px)',
              boxShadow: '0 6px 20px rgba(25, 118, 210, 0.4)',
            },
            '&:disabled': {
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              color: 'rgba(255, 255, 255, 0.3)',
            },
            transition: 'all 0.3s ease',
            boxShadow: '0 4px 16px rgba(25, 118, 210, 0.3)',
          }}
        >
          {isLoading ? (
            <CircularProgress size={24} color="inherit" />
          ) : (
            <SendIcon />
          )}
        </IconButton>
      </Box>
    </Box>
  );
};