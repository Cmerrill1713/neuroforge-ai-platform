'use client'

import { useState, useRef, useEffect } from 'react'
import { ChatMessage, VoiceOptionsResponse } from '@/types/api'
import { apiClient } from '@/lib/api'
import { Send, Bot, User, Paperclip, Mic, X, MicOff, Volume2, Image as ImageIcon, AlertTriangle } from 'lucide-react'

interface ChatInterfaceProps {
}

export function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [loadingStartTime, setLoadingStartTime] = useState<number | null>(null)
  const [showTimeoutWarning, setShowTimeoutWarning] = useState(false)
  const [attachment, setAttachment] = useState<File | null>(null)
  const [attachmentPreview, setAttachmentPreview] = useState<string | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [audioChunks, setAudioChunks] = useState<Blob[]>([]);
  const [recordingTime, setRecordingTime] = useState(0);
  const [voiceOptions, setVoiceOptions] = useState<Array<{id: string, name: string, description: string}>>([]);
  const [selectedVoice, setSelectedVoice] = useState<string>('neutral');
  const [voiceEnabled, setVoiceEnabled] = useState<boolean>(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('voiceEnabled') !== 'false'
    }
    return true
  });
  const [micError, setMicError] = useState<string | null>(null);
  const [speakingMessageId, setSpeakingMessageId] = useState<string | null>(null);
  const [showBrowserWindows, setShowBrowserWindows] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('showBrowserWindows') === 'true'
    }
    return false
  });
  const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Handle browser window toggle
  const handleBrowserWindowToggle = (checked: boolean) => {
    setShowBrowserWindows(checked)
    localStorage.setItem('showBrowserWindows', checked.toString())
  }

  // Handle voice toggle
  const handleVoiceToggle = (checked: boolean) => {
    setVoiceEnabled(checked)
    localStorage.setItem('voiceEnabled', checked.toString())
  }

  // Intelligence: Always use best tools, no toggles needed
  const useRAG = true  // Always retrieve context when relevant
  const useEvolution = true  // Always use optimal parameters

  // Conversation persistence
  const [conversationId, setConversationId] = useState<string | null>(null)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    const loadVoiceOptions = async () => {
      try {
        const response: VoiceOptionsResponse = await apiClient.getVoiceOptions();
        setVoiceOptions(response.voices);
        if (response.voices.length > 0) {
          // Prioritize DIA voice if available, otherwise use first voice
          const diaVoice = response.voices.find(voice => voice.id === 'dia_default');
          setSelectedVoice(diaVoice ? diaVoice.id : response.voices[0].id);
        }
      } catch (error) {
        console.error("Error loading voice options:", error);
      }
    };
    loadVoiceOptions();
  }, []);

  // Monitor loading timeouts
  useEffect(() => {
    let timeoutId: NodeJS.Timeout

    if (isLoading && loadingStartTime) {
      // Show warning after 10 seconds
      timeoutId = setTimeout(() => {
        setShowTimeoutWarning(true)
      }, 10000)
    } else {
      setShowTimeoutWarning(false)
    }

    return () => {
      if (timeoutId) clearTimeout(timeoutId)
    }
  }, [isLoading, loadingStartTime])

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      setAttachment(file);

      // Create a preview URL for images
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onloadend = () => {
          setAttachmentPreview(reader.result as string);
        };
        reader.readAsDataURL(file);
      } else {
        setAttachmentPreview(null);
      }
    }
  };

  const removeAttachment = () => {
    setAttachment(null);
    setAttachmentPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      setMediaRecorder(recorder);
      recorder.ondataavailable = (event) => {
        setAudioChunks((prev) => [...prev, event.data]);
      };
      recorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime(prevTime => prevTime + 1);
      }, 1000);
      setMicError(null);
    } catch (error) {
      console.error("Error accessing microphone:", error);
      if (error instanceof Error && error.name === 'NotAllowedError') {
          setMicError("Microphone access was denied. Please enable it in your browser settings.");
      } else {
          setMicError("Could not access the microphone. Please check your hardware and permissions.");
      }
    }
  };

  const stopRecording = () => {
    if (mediaRecorder) {
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        setAudioChunks([]);
        try {
          const response = await apiClient.transcribeAudio(audioBlob);
          setInput(response.transcription);
        } catch (error) {
          console.error("Error transcribing audio:", error);
        }
        setIsRecording(false);
      };
      mediaRecorder.stop();
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
      setRecordingTime(0);
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const shouldUseRAG = (query: string): boolean => {
    /**
     * Intelligent decision: Does this query need RAG context?
     * 
     * Use RAG for:
     * - Specific factual questions
     * - Technical queries
     * - "What is..." "How does..." "Explain..."
     * 
     * Skip RAG for:
     * - Greetings (hi, hello)
     * - Simple math
     * - General conversation
     */
    const lowerQuery = query.toLowerCase()
    
    // Skip RAG for simple greetings
    if (/^(hi|hello|hey|thanks|thank you|bye|goodbye)[\s!.]*$/i.test(lowerQuery)) {
      return false
    }
    
    // Skip RAG for simple math
    if (/^\d+[\s+\-*/]\d+/.test(query)) {
      return false
    }
    
    // Use RAG for knowledge questions
    if (/\b(what|how|why|explain|describe|tell me about|guide|tutorial|best practice)\b/i.test(lowerQuery)) {
      return true
    }
    
    // Use RAG for longer, specific queries (likely need context)
    if (query.split(' ').length > 5) {
      return true
    }
    
    // Default: don't use RAG for short, casual queries
    return false
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if ((!input.trim() && !attachment) || isLoading) return

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      content: input.trim(),
      sender: 'user',
      timestamp: new Date().toISOString(),
      attachment: attachment ? { name: attachment.name, type: attachment.type, size: attachment.size } : undefined
    }

    setMessages(prev => [...prev, userMessage])
    const originalInput = input.trim()
    setInput('')
    setAttachment(null)
    setAttachmentPreview(null)
    setIsLoading(true)
    setLoadingStartTime(Date.now())
    if (fileInputRef.current) {
        fileInputRef.current.value = '';
    }

    try {
      let enhancedPrompt = originalInput
      let enhancementMetadata: any = {}
      
      // Intelligence: Decide if query needs RAG context
      const needsRAG = shouldUseRAG(originalInput)
      
      // Step 1: RAG Enhancement (intelligent, automatic)
      if (useRAG && needsRAG) {
        try {
          const ragResponse = await apiClient.ragQuery(originalInput, 3, 'hybrid')
          if (ragResponse.results.length > 0 && ragResponse.results[0].score > 0.7) {
            // Only use RAG if we found relevant results (score > 0.7)
            const context = ragResponse.results
              .filter((r: any) => r.score > 0.7)
              .slice(0, 2) // Top 2 most relevant only
              .map((r: any) => r.text.slice(0, 200))
              .join('\n\n')
            
            enhancedPrompt = `Context: ${context}\n\nQ: ${originalInput}\n\nA: Be concise and direct.`
            enhancementMetadata.rag_used = true
          }
        } catch (error) {
          console.error('RAG enhancement failed, continuing without:', error)
        }
      }
      
      // Add conciseness instruction to all prompts
      if (!enhancementMetadata.rag_used) {
        enhancedPrompt = `${originalInput}\n\nBe concise, intelligent, and avoid rambling.`
      }
      
      // Step 2: Evolution Enhancement (if enabled)
      if (useEvolution) {
        try {
          const evolutionStats = await apiClient.getEvolutionStats()
          enhancementMetadata.temperature = 0.65
          enhancementMetadata.max_tokens = 1024
          enhancementMetadata.genome_score = evolutionStats.best_score
        } catch (error) {
          console.error('Evolution enhancement failed, continuing without:', error)
        }
      }
      
      // Send request
      let response;
      if (attachment) {
        response = await apiClient.sendChatWithAttachment(enhancedPrompt, attachment);
      } else {
        response = await apiClient.sendChat(enhancedPrompt, {
          temperature: enhancementMetadata.temperature,
          max_tokens: enhancementMetadata.max_tokens
        });
      }

      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        content: response.response, // Correctly access the response message
        sender: 'assistant',
        timestamp: response.timestamp,
        model: response.agent_used, // Use agent_used as the model name
        agent_used: response.agent_used,
        confidence: response.confidence,
        reasoning: response.reasoning,
        performance_metrics: {
          ...response.performance_metrics,
          rag_used: enhancementMetadata.rag_used,
          evolution_params: enhancementMetadata.temperature ? {
            temperature: enhancementMetadata.temperature,
            max_tokens: enhancementMetadata.max_tokens
          } : undefined
        },
        cache_hit: response.cache_hit,
        response_time: response.response_time,
      }

      setMessages(prev => [...prev, assistantMessage])

      // Save both messages to database (automatic persistence)
      await saveMessagesToDatabase(userMessage, assistantMessage, enhancementMetadata)
      
      // Add a small delay to prevent NotFoundError due to rapid DOM updates
      setTimeout(() => {
        setIsLoading(false);
        setLoadingStartTime(null);
        setShowTimeoutWarning(false);
      }, 50);
    } catch (error) {
      console.error('Chat error:', error)

      // Provide user-friendly error messages based on error type
      let errorContent = 'Sorry, I encountered an error. Please try again.'
      if (error instanceof Error) {
        if (error.message.includes('Failed to fetch')) {
          errorContent = 'Network error: Unable to connect to the server. Please check your connection and try again.'
        } else if (error.message.includes('timeout')) {
          errorContent = 'Request timed out. The server is taking too long to respond. Please try again.'
        } else if (error.message.includes('500')) {
          errorContent = 'Server error: Something went wrong on our end. Please try again in a moment.'
        } else if (error.message.includes('400')) {
          errorContent = 'Invalid request: Please check your message and try again.'
        }
      }

      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        content: errorContent,
        sender: 'assistant',
        timestamp: new Date().toISOString(),
        error: true,
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      // setIsLoading(false) // This line is now handled by the setTimeout
    }
  }

  const saveMessagesToDatabase = async (
    userMsg: ChatMessage,
    aiMsg: ChatMessage,
    metadata: any
  ) => {
    /**
     * Automatically saves conversation to PostgreSQL
     * Creates new conversation on first message
     */
    try {
      // Save user message
      const savedUser = await apiClient.saveMessage({
        conversation_id: conversationId || undefined,
        content: userMsg.content,
        sender: 'user',
        metadata: {
          attachment: userMsg.attachment,
          timestamp: userMsg.timestamp
        }
      })
      
      // Update conversation ID from first save
      if (savedUser && savedUser.conversation_id && !conversationId) {
        setConversationId(savedUser.conversation_id)
      }
      
      // Save AI message
      await apiClient.saveMessage({
        conversation_id: savedUser?.conversation_id || conversationId || undefined,
        content: aiMsg.content,
        sender: 'assistant',
        model: aiMsg.model,
        metadata: {
          ...metadata,
          confidence: aiMsg.confidence,
          reasoning: aiMsg.reasoning,
          performance_metrics: aiMsg.performance_metrics
        }
      })
      
      // Silent success - no UI notification needed
      
    } catch (error) {
      // Silent failure - don't interrupt UX if persistence fails
      console.error('Failed to save conversation:', error)
    }
  }

  const handleSpeak = async (message: ChatMessage) => {
    if (!voiceEnabled) {
      return; // Don't speak if voice is disabled
    }
    
    if (speakingMessageId === message.id) {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }
      setSpeakingMessageId(null);
      return;
    }

    try {
      const audioBlob = await apiClient.synthesizeSpeech(message.content, selectedVoice);
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      audio.onplay = () => {
        setSpeakingMessageId(message.id);
      };

      audio.onended = () => {
        setSpeakingMessageId(null);
      };

      audio.play();
    } catch (error) {
      console.error("Error synthesizing speech:", error);
      alert("Failed to speak message. Please try again.");
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-card rounded-lg border shadow-sm">
        {/* Header */}
        <div className="p-4 border-b">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">AI Chat</h2>
            <div className="flex items-center space-x-3">
              {/* Voice Toggle */}
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="voiceEnabled"
                  checked={voiceEnabled}
                  onChange={(e) => handleVoiceToggle(e.target.checked)}
                  className="rounded border-gray-300"
                />
                <label htmlFor="voiceEnabled" className="text-sm text-muted-foreground">
                  Voice Response
                </label>
              </div>
              
              {/* Voice Selection */}
              <select
                value={selectedVoice}
                onChange={(e) => setSelectedVoice(e.target.value)}
                className="px-3 py-1 text-sm border rounded-md bg-background"
                aria-label="Select voice for synthesis"
                disabled={!voiceEnabled}
              >
                {voiceOptions.map((voice) => (
                  <option key={voice.id} value={voice.id}>
                    {voice.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          {/* Browser Window Toggle */}
          <div className="mt-3 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="showBrowserWindows"
                checked={showBrowserWindows}
                onChange={(e) => handleBrowserWindowToggle(e.target.checked)}
                className="rounded border-gray-300"
              />
              <label htmlFor="showBrowserWindows" className="text-sm text-muted-foreground">
                Show browser windows for web operations
              </label>
            </div>
            <div className="text-xs text-muted-foreground">
              {showBrowserWindows ? 'Visible' : 'Hidden'}
            </div>
          </div>
        </div>
        {/* Messages */}
        <div className="h-96 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-muted-foreground py-8">
              <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>Start a conversation with your AI assistant</p>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex items-start space-x-3 ${
                message.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {message.sender === 'assistant' && (
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  message.error
                    ? 'bg-red-500'
                    : 'bg-primary'
                }`}>
                  {message.error ? (
                    <AlertTriangle className="w-4 h-4 text-white" />
                  ) : (
                    <Bot className="w-4 h-4 text-primary-foreground" />
                  )}
                </div>
              )}

              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.sender === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : message.error
                    ? 'bg-red-50 border border-red-200 text-red-800 dark:bg-red-900 dark:border-red-700 dark:text-red-200'
                    : 'bg-muted'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                
                {message.sender === 'assistant' && (
                  <div className="flex items-center gap-2 mt-2">
                    {message.error && (
                      <button
                        onClick={() => {
                          // Find the last user message and retry
                          const lastUserMessage = [...messages].reverse().find(m => m.sender === 'user');
                          if (lastUserMessage) {
                            setInput(lastUserMessage.content);
                            setMessages(prev => prev.filter(m => m.id !== message.id));
                          }
                        }}
                        className="text-xs px-2 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded transition-colors"
                      >
                        Retry
                      </button>
                    )}
                    {message.content && (
                      <button 
                        onClick={() => handleSpeak(message)}
                        disabled={!voiceEnabled}
                        className={`p-1 rounded-full hover:bg-muted-foreground/20 text-muted-foreground ${speakingMessageId === message.id ? 'text-primary' : ''} ${!voiceEnabled ? 'opacity-50 cursor-not-allowed' : ''}`}
                        aria-label="Speak message"
                      >
                        <Volume2 className={`w-4 h-4 ${speakingMessageId === message.id ? 'animate-pulse' : ''}`} />
                      </button>
                    )}
                    {message.model && (
                      <span className="text-xs opacity-50">
                        {message.model}
                      </span>
                    )}
                  </div>
                )}
              </div>

              {message.sender === 'user' && (
                <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-secondary-foreground" />
                </div>
              )}
            </div>
          ))}

          {/* Always render loading indicator, but conditionally visible */}
          <div className={`flex items-start space-x-3 ${isLoading ? '' : 'hidden'}`}>
            <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
              <Bot className="w-4 h-4 text-primary-foreground" />
            </div>
            <div className="bg-muted px-4 py-2 rounded-lg">
              <div className="flex space-x-1 mb-1">
                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
              {showTimeoutWarning && (
                <div className="text-xs text-yellow-600 flex items-center space-x-1">
                  <AlertTriangle className="w-3 h-3" />
                  <span>Taking longer than usual...</span>
                </div>
              )}
            </div>
          </div>

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          {micError && (
              <div className="mb-2 text-sm text-red-500 bg-red-500/10 p-2 rounded-md">
                  {micError}
              </div>
          )}
          {attachment && (
            <div className="mb-2 flex items-center justify-between bg-muted p-2 rounded-md">
              <div className="flex items-center gap-2">
                {attachmentPreview ? (
                    <img src={attachmentPreview} alt="Preview" className="w-10 h-10 rounded-md object-cover" />
                ) : (
                    <ImageIcon className="w-6 h-6" />
                )}
                <span className="text-sm">{attachment.name}</span>
              </div>
              <button onClick={removeAttachment} className="p-1 hover:bg-muted-foreground/20 rounded-full">
                <X className="w-4 h-4" />
              </button>
            </div>
          )}
          <form onSubmit={handleSubmit} className="relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything..."
              className="w-full resize-none border-0 bg-transparent p-2 pr-28 focus-within:outline-none"
              rows={1}
              disabled={isLoading}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  handleSubmit(e);
                }
              }}
            />
            <div className="absolute top-1/2 right-2 -translate-y-1/2 flex items-center gap-2">
              <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" />
              <button type="button" onClick={() => fileInputRef.current?.click()} className="p-2 hover:bg-muted rounded-full" disabled={isLoading || isRecording}>
                <Paperclip className="w-5 h-5" />
              </button>
              <div className="flex items-center">
                {isRecording && (
                    <span className="text-sm text-red-500 mr-2 tabular-nums">
                        {Math.floor(recordingTime / 60).toString().padStart(2, '0')}:
                        {(recordingTime % 60).toString().padStart(2, '0')}
                    </span>
                )}
                <button type="button" onClick={toggleRecording} className={`p-2 hover:bg-muted rounded-full ${isRecording ? 'bg-red-500 text-white' : ''}`} disabled={isLoading}>
                  {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                </button>
              </div>
              <button
                type="submit"
                disabled={(!input.trim() && !attachment) || isLoading}
                className="p-2 bg-primary text-primary-foreground rounded-full hover:bg-primary/90 disabled:opacity-50"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}