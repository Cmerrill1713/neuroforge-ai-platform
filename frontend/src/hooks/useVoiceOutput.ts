import { useState, useCallback, useRef } from 'react';

interface UseVoiceOutputReturn {
  isSpeaking: boolean;
  isSupported: boolean;
  error: string | null;
  speak: (text: string, options?: SpeechSynthesisOptions) => Promise<void>;
  stopSpeaking: () => void;
  pauseSpeaking: () => void;
  resumeSpeaking: () => void;
  setVoice: (voice: SpeechSynthesisVoice | null) => void;
  availableVoices: SpeechSynthesisVoice[];
}

interface SpeechSynthesisOptions {
  rate?: number;
  pitch?: number;
  volume?: number;
  voice?: SpeechSynthesisVoice;
  lang?: string;
}

export const useVoiceOutput = (): UseVoiceOutputReturn => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [availableVoices, setAvailableVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<SpeechSynthesisVoice | null>(null);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  const isSupported = typeof window !== 'undefined' && 'speechSynthesis' in window;

  // Load available voices
  const loadVoices = useCallback(() => {
    if (!isSupported) return;
    
    const voices = speechSynthesis.getVoices();
    setAvailableVoices(voices);
    
    // Set default voice (prefer English voices)
    if (!selectedVoice && voices.length > 0) {
      const englishVoice = voices.find(voice => 
        voice.lang.startsWith('en') || voice.lang.includes('English')
      ) || voices[0];
      setSelectedVoice(englishVoice);
    }
  }, [isSupported, selectedVoice]);

  // Initialize voices
  useState(() => {
    if (isSupported) {
      loadVoices();
      // Some browsers load voices asynchronously
      speechSynthesis.addEventListener('voiceschanged', loadVoices);
    }
  });

  const speak = useCallback(async (text: string, options: SpeechSynthesisOptions = {}): Promise<void> => {
    if (!isSupported) {
      setError('Speech synthesis is not supported in this browser');
      return;
    }

    try {
      // Stop any current speech
      speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      
      // Set voice
      utterance.voice = options.voice || selectedVoice;
      
      // Set speech parameters
      utterance.rate = options.rate || 1;
      utterance.pitch = options.pitch || 1;
      utterance.volume = options.volume || 1;
      utterance.lang = options.lang || 'en-US';

      // Event handlers
      utterance.onstart = () => {
        setIsSpeaking(true);
        setError(null);
      };

      utterance.onend = () => {
        setIsSpeaking(false);
        utteranceRef.current = null;
      };

      utterance.onerror = (event) => {
        setError(`Speech synthesis error: ${event.error}`);
        setIsSpeaking(false);
        utteranceRef.current = null;
      };

      utterance.onpause = () => {
        setIsSpeaking(false);
      };

      utterance.onresume = () => {
        setIsSpeaking(true);
      };

      utteranceRef.current = utterance;
      speechSynthesis.speak(utterance);
    } catch (err) {
      setError('Failed to start speech synthesis');
      setIsSpeaking(false);
    }
  }, [isSupported, selectedVoice]);

  const stopSpeaking = useCallback(() => {
    if (isSupported) {
      speechSynthesis.cancel();
      setIsSpeaking(false);
      utteranceRef.current = null;
    }
  }, [isSupported]);

  const pauseSpeaking = useCallback(() => {
    if (isSupported && isSpeaking) {
      speechSynthesis.pause();
    }
  }, [isSupported, isSpeaking]);

  const resumeSpeaking = useCallback(() => {
    if (isSupported && !isSpeaking) {
      speechSynthesis.resume();
    }
  }, [isSupported, isSpeaking]);

  const setVoice = useCallback((voice: SpeechSynthesisVoice | null) => {
    setSelectedVoice(voice);
  }, []);

  return {
    isSpeaking,
    isSupported,
    error,
    speak,
    stopSpeaking,
    pauseSpeaking,
    resumeSpeaking,
    setVoice,
    availableVoices,
  };
};
