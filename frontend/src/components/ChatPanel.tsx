"use client"

import { useState, useRef, useEffect } from 'react'
import { Send, Mic, Paperclip, MessageCircle } from 'lucide-react'
import { apiClient, ChatMessage, ChatRequest } from '@/lib/api'

interface Message {
  id: string
  content: string
  sender: 'user' | 'ai'
  model?: string
  timestamp: Date
}

interface ChatPanelProps {
  activeModel: string
}

export function ChatPanel({ activeModel }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Hello! I\'m your AI assistant. How can I help you learn and build today?',
      sender: 'ai',
      model: activeModel,
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const getModelResponse = (model: string, userInput: string): string => {
    const responses: Record<string, string> = {
      'llama3.1:8b': `As your Full-Stack Architect, I'll help you design robust, scalable solutions. For "${userInput}", I recommend a systematic approach with proper architecture patterns and performance optimization.`,
      'qwen2.5:7b': `From a UX/UI Designer perspective, let's focus on creating an intuitive user experience for "${userInput}". I'll help you design interfaces that are both beautiful and accessible.`,
      'mistral:7b': `As a Frontend Engineer, I'll help you implement "${userInput}" using modern web technologies. Let's write clean, efficient code with React and TypeScript.`,
      'phi3:3.8b': `From a DevOps perspective, I'll help you deploy and monitor "${userInput}" effectively. Let's ensure reliability, scalability, and proper CI/CD practices.`,
      'llama3.2:3b': `As a Product Manager, I'll help you prioritize and plan "${userInput}" based on user needs and business value. Let's create a roadmap for success.`,
      'llava:7b': `As a Multimodal Specialist, I can analyze images and visual content related to "${userInput}". I'll help you understand visual elements and create multimodal experiences.`,
      'nomic-embed-text:latest': `As an Embedding Expert, I'll help you with semantic search and knowledge retrieval for "${userInput}". I can create vector embeddings and find relevant information.`,
      'gpt-oss:20b': `With advanced reasoning capabilities, I'll provide comprehensive analysis of "${userInput}". I can handle complex problem-solving and generate sophisticated solutions.`
    }
    return responses[model] || `I'll help you with "${userInput}" using my specialized capabilities.`
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
      // Use the real API client
      const request: ChatRequest = {
        message: currentInput,
        model: activeModel,
        stream: false
      }

      const response = await apiClient.sendMessage(request)
      
      const aiMessage: Message = {
        id: Date.now().toString(),
        content: response.message,
        sender: 'ai',
        model: response.model,
        timestamp: response.timestamp
      }
      
      setMessages(prev => [...prev, aiMessage])
      console.log(`Real AI response from ${response.model} (${response.response_time}ms)`)
      
    } catch (error) {
      console.error('Error sending message:', error)
      
      // Fallback to simulated response
      const fallbackMessage: Message = {
        id: Date.now().toString(),
        content: `[Fallback] ${getModelResponse(activeModel, currentInput)}`,
        sender: 'ai',
        model: activeModel,
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, fallbackMessage])
    } finally {
      setIsTyping(false)
    }
  }

  return (
    <div className="h-full flex flex-col bg-transparent">
      <div className="p-6 border-b border-white/10">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <MessageCircle className="w-4 h-4 text-white" />
          </div>
          <div>
            <h2 className="font-semibold text-white">AI Chat</h2>
            <p className="text-sm text-white/60">
              Chatting with {activeModel}
            </p>
          </div>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${
                message.sender === 'user'
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                  : 'bg-white/10 backdrop-blur-md text-white border border-white/20'
              }`}
            >
              <p className="text-sm leading-relaxed">{message.content}</p>
              <p className="text-xs opacity-70 mt-2">
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-white/10 backdrop-blur-md text-white border border-white/20 px-4 py-3 rounded-2xl">
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <p className="text-sm text-white/70">AI is typing...</p>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      <div className="p-6 border-t border-white/10">
        <div className="flex items-center space-x-3">
          <button className="p-3 text-white/60 hover:text-white hover:bg-white/10 rounded-xl transition-colors">
            <Paperclip className="w-5 h-5" />
          </button>
          
          <div className="flex-1 relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask me anything..."
              className="w-full px-4 py-3 bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all"
            />
          </div>
          
          <button className="p-3 text-white/60 hover:text-white hover:bg-white/10 rounded-xl transition-colors">
            <Mic className="w-5 h-5" />
          </button>
          
          <button
            onClick={sendMessage}
            disabled={!input.trim()}
            className="p-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  )
}
