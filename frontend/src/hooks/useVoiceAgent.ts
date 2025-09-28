import { useState, useCallback, useEffect, useRef } from 'react';
import { useVoiceInput } from './useVoiceInput';
import { useVoiceOutput } from './useVoiceOutput';
import { apiService } from '../services/api';

interface VoiceAgentOptions {
  autoSpeakResponses?: boolean;
  wakeWordEnabled?: boolean;
  wakeWord?: string;
  continuousMode?: boolean;
  voiceModel?: string;
}

interface VoiceAgentReturn {
  // Voice Input
  isListening: boolean;
  isSupported: boolean;
  transcript: string;
  voiceError: string | null;
  startListening: () => void;
  stopListening: () => void;
  clearTranscript: () => void;
  
  // Voice Output
  isSpeaking: boolean;
  speakError: string | null;
  speak: (text: string) => Promise<void>;
  stopSpeaking: () => void;
  
  // Voice Agent Controls
  isActive: boolean;
  wakeWordDetected: boolean;
  processingMessage: boolean;
  lastResponse: string | null;
  
  // Configuration
  setAutoSpeakResponses: (enabled: boolean) => void;
  setWakeWordEnabled: (enabled: boolean) => void;
  setWakeWord: (word: string) => void;
  setContinuousMode: (enabled: boolean) => void;
  setVoiceModel: (model: string) => void;
  
  // Voice Agent Actions
  processVoiceMessage: (message: string) => Promise<void>;
  toggleVoiceAgent: () => void;
  resetVoiceAgent: () => void;
}

export const useVoiceAgent = (options: VoiceAgentOptions = {}): VoiceAgentReturn => {
  const {
    autoSpeakResponses = true,
    wakeWordEnabled = false,
    wakeWord = 'hey assistant',
    continuousMode = false,
    voiceModel = 'qwen2.5:7b'
  } = options;

  // Voice input/output hooks
  const voiceInput = useVoiceInput();
  const voiceOutput = useVoiceOutput();
  
  // Voice agent state
  const [isActive, setIsActive] = useState(false);
  const [wakeWordDetected, setWakeWordDetected] = useState(false);
  const [processingMessage, setProcessingMessage] = useState(false);
  const [lastResponse, setLastResponse] = useState<string | null>(null);
  const [config, setConfig] = useState({
    autoSpeakResponses,
    wakeWordEnabled,
    wakeWord,
    continuousMode,
    voiceModel
  });

  // Refs for managing voice agent
  const wakeWordTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const continuousListeningRef = useRef(false);

  // Wake word detection
  useEffect(() => {
    if (!config.wakeWordEnabled || !voiceInput.transcript) return;

    const transcript = voiceInput.transcript.toLowerCase();
    const wakeWordLower = config.wakeWord.toLowerCase();
    
    if (transcript.includes(wakeWordLower)) {
      setWakeWordDetected(true);
      
      // Clear wake word detection after 3 seconds
      if (wakeWordTimeoutRef.current) {
        clearTimeout(wakeWordTimeoutRef.current);
      }
      
      wakeWordTimeoutRef.current = setTimeout(() => {
        setWakeWordDetected(false);
      }, 3000);
    }
  }, [voiceInput.transcript, config.wakeWordEnabled, config.wakeWord]);

  // Process voice message with LLM
  const processVoiceMessage = useCallback(async (message: string) => {
    if (!message.trim()) return;

    setProcessingMessage(true);
    
    try {
      console.log('🎤 Processing voice message:', message);
      
      // Send message to LLM via API
      const response = await apiService.sendMessage(message, config.voiceModel);
      
      if (response.success && response.data) {
        const aiResponse = response.data.content;
        setLastResponse(aiResponse);
        
        console.log('🤖 LLM Response:', aiResponse);
        
        // Auto-speak the response if enabled
        if (config.autoSpeakResponses && voiceOutput.isSupported) {
          await voiceOutput.speak(aiResponse);
        }
      } else {
        const errorMsg = 'Sorry, I encountered an error processing your request.';
        setLastResponse(errorMsg);
        
        if (config.autoSpeakResponses && voiceOutput.isSupported) {
          await voiceOutput.speak(errorMsg);
        }
      }
    } catch (error) {
      console.error('Voice agent error:', error);
      const errorMsg = 'Sorry, I encountered an error. Please try again.';
      setLastResponse(errorMsg);
      
      if (config.autoSpeakResponses && voiceOutput.isSupported) {
        await voiceOutput.speak(errorMsg);
      }
    } finally {
      setProcessingMessage(false);
    }
  }, [config.autoSpeakResponses, config.voiceModel, voiceOutput]);

  // Handle voice input changes
  useEffect(() => {
    if (!voiceInput.transcript || !isActive) return;

    // If wake word is enabled, only process after wake word detection
    if (config.wakeWordEnabled && !wakeWordDetected) return;

    // Process the transcript
    processVoiceMessage(voiceInput.transcript);
    
    // Clear transcript after processing
    voiceInput.clearTranscript();
  }, [voiceInput.transcript, isActive, wakeWordDetected, config.wakeWordEnabled, processVoiceMessage, voiceInput]);

  // Continuous listening mode
  useEffect(() => {
    if (config.continuousMode && isActive && !voiceInput.isListening) {
      continuousListeningRef.current = true;
      voiceInput.startListening();
    } else if (!config.continuousMode && continuousListeningRef.current) {
      continuousListeningRef.current = false;
      voiceInput.stopListening();
    }
  }, [config.continuousMode, isActive, voiceInput]);

  // Voice agent controls
  const toggleVoiceAgent = useCallback(() => {
    if (isActive) {
      setIsActive(false);
      voiceInput.stopListening();
      voiceOutput.stopSpeaking();
      setWakeWordDetected(false);
    } else {
      setIsActive(true);
      if (config.continuousMode) {
        voiceInput.startListening();
      }
    }
  }, [isActive, voiceInput, voiceOutput, config.continuousMode]);

  const resetVoiceAgent = useCallback(() => {
    setIsActive(false);
    setWakeWordDetected(false);
    setProcessingMessage(false);
    setLastResponse(null);
    voiceInput.stopListening();
    voiceOutput.stopSpeaking();
    voiceInput.clearTranscript();
  }, [voiceInput, voiceOutput]);

  // Configuration setters
  const setAutoSpeakResponses = useCallback((enabled: boolean) => {
    setConfig(prev => ({ ...prev, autoSpeakResponses: enabled }));
  }, []);

  const setWakeWordEnabled = useCallback((enabled: boolean) => {
    setConfig(prev => ({ ...prev, wakeWordEnabled: enabled }));
  }, []);

  const setWakeWord = useCallback((word: string) => {
    setConfig(prev => ({ ...prev, wakeWord: word }));
  }, []);

  const setContinuousMode = useCallback((enabled: boolean) => {
    setConfig(prev => ({ ...prev, continuousMode: enabled }));
  }, []);

  const setVoiceModel = useCallback((model: string) => {
    setConfig(prev => ({ ...prev, voiceModel: model }));
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wakeWordTimeoutRef.current) {
        clearTimeout(wakeWordTimeoutRef.current);
      }
    };
  }, []);

  return {
    // Voice Input
    isListening: voiceInput.isListening,
    isSupported: voiceInput.isSupported,
    transcript: voiceInput.transcript,
    voiceError: voiceInput.error,
    startListening: voiceInput.startListening,
    stopListening: voiceInput.stopListening,
    clearTranscript: voiceInput.clearTranscript,
    
    // Voice Output
    isSpeaking: voiceOutput.isSpeaking,
    speakError: voiceOutput.error,
    speak: voiceOutput.speak,
    stopSpeaking: voiceOutput.stopSpeaking,
    
    // Voice Agent Controls
    isActive,
    wakeWordDetected,
    processingMessage,
    lastResponse,
    
    // Configuration
    setAutoSpeakResponses,
    setWakeWordEnabled,
    setWakeWord,
    setContinuousMode,
    setVoiceModel,
    
    // Voice Agent Actions
    processVoiceMessage,
    toggleVoiceAgent,
    resetVoiceAgent,
  };
};
