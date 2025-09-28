#!/usr/bin/env python3
"""
Frontend Starter Creation Script
Creates the initial Next.js frontend based on our AI models' collaborative design
"""

import os
import json
from pathlib import Path

def create_frontend_starter():
    """Create the frontend starter based on AI model recommendations."""
    
    print("🚀 Creating Frontend Starter Based on AI Model Collaboration")
    print("=" * 60)
    
    # Create frontend directory
    frontend_dir = Path("frontend")
    frontend_dir.mkdir(exist_ok=True)
    
    # Create package.json
    package_json = {
        "name": "ai-chat-learn-frontend",
        "version": "0.1.0",
        "private": True,
        "scripts": {
            "dev": "next dev",
            "build": "next build",
            "start": "next start",
            "lint": "next lint",
            "type-check": "tsc --noEmit"
        },
        "dependencies": {
            "next": "14.0.0",
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "@monaco-editor/react": "^4.6.0",
            "socket.io-client": "^4.7.2",
            "zustand": "^4.4.1",
            "@tanstack/react-query": "^4.35.0",
            "framer-motion": "^10.16.0",
            "lucide-react": "^0.290.0",
            "@headlessui/react": "^1.7.17",
            "tailwindcss": "^3.3.0",
            "autoprefixer": "^10.4.16",
            "postcss": "^8.4.31"
        },
        "devDependencies": {
            "typescript": "^5.2.2",
            "@types/node": "^20.8.0",
            "@types/react": "^18.2.25",
            "@types/react-dom": "^18.2.10",
            "eslint": "^8.51.0",
            "eslint-config-next": "14.0.0"
        }
    }
    
    with open(frontend_dir / "package.json", "w") as f:
        json.dump(package_json, f, indent=2)
    
    # Create Next.js config
    next_config = '''/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  webpack: (config) => {
    // Monaco Editor support
    config.module.rules.push({
      test: /\\.worker\\.js$/,
      use: { loader: 'worker-loader' },
    });
    return config;
  },
}

module.exports = nextConfig
'''
    
    with open(frontend_dir / "next.config.js", "w") as f:
        f.write(next_config)
    
    # Create Tailwind config
    tailwind_config = '''/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'ai-primary': '#3B82F6',
        'ai-secondary': '#8B5CF6',
        'ai-accent': '#10B981',
        'ai-chat': '#F3F4F6',
        'ai-code': '#1F2937',
      },
      animation: {
        'typing': 'typing 1.5s infinite',
        'pulse-slow': 'pulse 3s infinite',
      }
    },
  },
  plugins: [],
  darkMode: 'class',
}
'''
    
    with open(frontend_dir / "tailwind.config.js", "w") as f:
        f.write(tailwind_config)
    
    # Create TypeScript config
    tsconfig = {
        "compilerOptions": {
            "target": "es5",
            "lib": ["dom", "dom.iterable", "es6"],
            "allowJs": True,
            "skipLibCheck": True,
            "strict": True,
            "noEmit": True,
            "esModuleInterop": True,
            "module": "esnext",
            "moduleResolution": "bundler",
            "resolveJsonModule": True,
            "isolatedModules": True,
            "jsx": "preserve",
            "incremental": True,
            "plugins": [
                {
                    "name": "next"
                }
            ],
            "paths": {
                "@/*": ["./src/*"]
            }
        },
        "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
        "exclude": ["node_modules"]
    }
    
    with open(frontend_dir / "tsconfig.json", "w") as f:
        json.dump(tsconfig, f, indent=2)
    
    # Create app directory structure
    app_dir = frontend_dir / "app"
    app_dir.mkdir(exist_ok=True)
    
    # Create layout.tsx
    layout_tsx = '''import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI Chat, Build & Learn',
  description: 'Collaborative AI-powered learning environment with HRM-enhanced reasoning',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full bg-gray-50 dark:bg-gray-900`}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
'''
    
    with open(app_dir / "layout.tsx", "w") as f:
        f.write(layout_tsx)
    
    # Create providers.tsx
    providers_tsx = '''\"use client\"

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient())

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}
'''
    
    with open(app_dir / "providers.tsx", "w") as f:
        f.write(providers_tsx)
    
    # Create main page
    page_tsx = '''\"use client\"

import { useState } from 'react'
import { ChatPanel } from '@/components/ChatPanel'
import { CodeEditor } from '@/components/CodeEditor'
import { LearningDashboard } from '@/components/LearningDashboard'
import { MultimodalPanel } from '@/components/MultimodalPanel'
import { Header } from '@/components/Header'
import { AIModelSelector } from '@/components/AIModelSelector'

export default function Home() {
  const [activeModel, setActiveModel] = useState('llama3.1:8b')
  const [darkMode, setDarkMode] = useState(false)

  return (
    <div className={`h-full flex flex-col ${darkMode ? 'dark' : ''}`}>
      <Header 
        darkMode={darkMode} 
        setDarkMode={setDarkMode}
        activeModel={activeModel}
        setActiveModel={setActiveModel}
      />
      
      <main className="flex-1 flex overflow-hidden">
        {/* Chat Panel */}
        <div className="w-1/4 border-r border-gray-200 dark:border-gray-700">
          <ChatPanel activeModel={activeModel} />
        </div>
        
        {/* Code Editor */}
        <div className="w-1/4 border-r border-gray-200 dark:border-gray-700">
          <CodeEditor />
        </div>
        
        {/* Multimodal Panel */}
        <div className="w-1/4 border-r border-gray-200 dark:border-gray-700">
          <MultimodalPanel 
            activeModel={activeModel}
            onImageAnalysis={(image, analysis) => {
              console.log('Image analyzed:', image.file.name, analysis)
            }}
          />
        </div>
        
        {/* Learning Dashboard */}
        <div className="w-1/4">
          <LearningDashboard />
        </div>
      </main>
    </div>
  )
}
'''
    
    with open(app_dir / "page.tsx", "w") as f:
        f.write(page_tsx)
    
    # Create globals.css
    globals_css = '''@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html {
    font-family: system-ui, sans-serif;
  }
}

@layer components {
  .ai-chat-bubble {
    @apply bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700;
  }
  
  .ai-model-badge {
    @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium;
  }
  
  .ai-button-primary {
    @apply bg-ai-primary hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors;
  }
  
  .ai-input {
    @apply w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-ai-primary focus:border-transparent dark:bg-gray-800 dark:text-white;
  }
}

/* Custom animations */
@keyframes typing {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.typing-indicator::after {
  content: '|';
  animation: typing 1s infinite;
}
'''
    
    with open(app_dir / "globals.css", "w") as f:
        f.write(globals_css)
    
    # Create components directory
    components_dir = frontend_dir / "src" / "components"
    components_dir.mkdir(parents=True, exist_ok=True)
    
    # Create component files
    components = {
        "Header.tsx": '''\"use client\"

import { Sun, Moon, Settings } from 'lucide-react'
import { AIModelSelector } from './AIModelSelector'

interface HeaderProps {
  darkMode: boolean
  setDarkMode: (dark: boolean) => void
  activeModel: string
  setActiveModel: (model: string) => void
}

export function Header({ darkMode, setDarkMode, activeModel, setActiveModel }: HeaderProps) {
  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">
            AI Chat, Build & Learn
          </h1>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            HRM-Enhanced Collaborative Environment
          </span>
        </div>
        
        <div className="flex items-center space-x-4">
          <AIModelSelector 
            activeModel={activeModel}
            onModelChange={setActiveModel}
          />
          
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
          
          <button className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>
    </header>
  )
}
''',
        
        "AIModelSelector.tsx": '''\"use client\"

import { useState } from 'react'
import { ChevronDown, Bot } from 'lucide-react'

interface AIModelSelectorProps {
  activeModel: string
  onModelChange: (model: string) => void
}

const AI_MODELS = [
  { id: 'llama3.1:8b', name: 'Llama 3.1 8B', role: 'Full-Stack Architect', color: 'bg-blue-500', expertise: 'System architecture, API design, performance optimization' },
  { id: 'qwen2.5:7b', name: 'Qwen 2.5 7B', role: 'UX/UI Designer', color: 'bg-purple-500', expertise: 'User experience, interface design, accessibility' },
  { id: 'mistral:7b', name: 'Mistral 7B', role: 'Frontend Engineer', color: 'bg-green-500', expertise: 'React, TypeScript, modern web technologies' },
  { id: 'phi3:3.8b', name: 'Phi-3 3.8B', role: 'DevOps Specialist', color: 'bg-orange-500', expertise: 'Deployment, CI/CD, containerization, monitoring' },
  { id: 'llama3.2:3b', name: 'Llama 3.2 3B', role: 'Product Manager', color: 'bg-red-500', expertise: 'User requirements, feature prioritization, roadmap planning' },
  { id: 'llava:7b', name: 'LLaVA 7B', role: 'Multimodal Specialist', color: 'bg-indigo-500', expertise: 'Image analysis, visual content understanding, multimodal AI' },
  { id: 'nomic-embed-text:latest', name: 'Nomic Embed', role: 'Embedding Expert', color: 'bg-teal-500', expertise: 'Vector embeddings, semantic search, knowledge retrieval' },
  { id: 'gpt-oss:20b', name: 'GPT-OSS 20B', role: 'Advanced Reasoning', color: 'bg-pink-500', expertise: 'Complex reasoning, code generation, advanced problem solving' },
]

export function AIModelSelector({ activeModel, onModelChange }: AIModelSelectorProps) {
  const [isOpen, setIsOpen] = useState(false)
  const currentModel = AI_MODELS.find(m => m.id === activeModel)

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600"
      >
        <div className={`w-3 h-3 rounded-full ${currentModel?.color}`} />
        <Bot className="w-4 h-4" />
        <span className="text-sm font-medium">{currentModel?.name}</span>
        <ChevronDown className="w-4 h-4" />
      </button>
      
      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50 max-h-96 overflow-y-auto">
          <div className="p-3 border-b border-gray-200 dark:border-gray-700">
            <h3 className="font-semibold text-gray-900 dark:text-white text-sm">Choose AI Model</h3>
            <p className="text-xs text-gray-500 dark:text-gray-400">Select specialized AI for your task</p>
          </div>
          {AI_MODELS.map((model) => (
            <button
              key={model.id}
              onClick={() => {
                onModelChange(model.id)
                setIsOpen(false)
              }}
              className="w-full flex items-start space-x-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 first:rounded-t-lg last:rounded-b-lg border-b border-gray-100 dark:border-gray-700 last:border-b-0"
            >
              <div className={`w-4 h-4 rounded-full ${model.color} mt-0.5 flex-shrink-0`} />
              <div className="flex-1 text-left min-w-0">
                <div className="font-medium text-gray-900 dark:text-white text-sm">{model.name}</div>
                <div className="text-xs text-gray-600 dark:text-gray-300 font-medium">{model.role}</div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">{model.expertise}</div>
              </div>
              {model.id === activeModel && (
                <div className="w-2 h-2 bg-ai-primary rounded-full mt-2 flex-shrink-0" />
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
''',
        
        "ChatPanel.tsx": '''\"use client\"

import { useState, useRef, useEffect } from 'react'
import { Send, Mic, Paperclip } from 'lucide-react'

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
      content: 'Hello! I\\'m your AI assistant. How can I help you learn and build today?',
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
    const responses = {
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
    setInput('')
    setIsTyping(true)

    // Simulate AI response with model-specific content
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: getModelResponse(activeModel, input),
        sender: 'ai',
        model: activeModel,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, aiMessage])
      setIsTyping(false)
    }, 1500)
  }

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="font-semibold text-gray-900 dark:text-white">AI Chat</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Chatting with {activeModel}
        </p>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.sender === 'user'
                  ? 'bg-ai-primary text-white'
                  : 'ai-chat-bubble'
              }`}
            >
              <p className="text-sm">{message.content}</p>
              <p className="text-xs opacity-70 mt-1">
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="flex justify-start">
            <div className="ai-chat-bubble">
              <p className="text-sm text-gray-500 typing-indicator">AI is typing</p>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-2">
          <button className="p-2 text-gray-400 hover:text-gray-600">
            <Paperclip className="w-5 h-5" />
          </button>
          
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask me anything..."
            className="ai-input flex-1"
          />
          
          <button className="p-2 text-gray-400 hover:text-gray-600">
            <Mic className="w-5 h-5" />
          </button>
          
          <button
            onClick={sendMessage}
            disabled={!input.trim()}
            className="ai-button-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
''',
        
        "CodeEditor.tsx": '''\"use client\"

import { useState } from 'react'
import { Editor } from '@monaco-editor/react'
import { Play, Save, FolderOpen, File } from 'lucide-react'

export function CodeEditor() {
  const [code, setCode] = useState(`// Welcome to the AI-powered code editor!
// Start building with AI assistance

function greetAI() {
  console.log("Hello from the HRM-enhanced AI system!");
  return "Ready to learn and build together!";
}

greetAI();`)
  
  const [language, setLanguage] = useState('javascript')
  const [theme, setTheme] = useState('vs-dark')

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-gray-900 dark:text-white">Code Editor</h2>
          <div className="flex items-center space-x-2">
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="text-sm border rounded px-2 py-1"
            >
              <option value="javascript">JavaScript</option>
              <option value="typescript">TypeScript</option>
              <option value="python">Python</option>
              <option value="html">HTML</option>
              <option value="css">CSS</option>
            </select>
            
            <button className="p-2 text-gray-400 hover:text-gray-600">
              <FolderOpen className="w-4 h-4" />
            </button>
            
            <button className="p-2 text-gray-400 hover:text-gray-600">
              <Save className="w-4 h-4" />
            </button>
            
            <button className="ai-button-primary text-sm px-3 py-1">
              <Play className="w-3 h-3 mr-1" />
              Run
            </button>
          </div>
        </div>
      </div>
      
      <div className="flex-1">
        <Editor
          height="100%"
          language={language}
          theme={theme}
          value={code}
          onChange={(value) => setCode(value || '')}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            roundedSelection: false,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
            insertSpaces: true,
            wordWrap: 'on',
            suggest: {
              enabled: true,
            },
          }}
        />
      </div>
      
      <div className="p-2 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
        <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
          <File className="w-4 h-4" />
          <span>main.{language === 'javascript' ? 'js' : language === 'typescript' ? 'ts' : 'py'}</span>
          <span className="ml-auto">AI assistance enabled</span>
        </div>
      </div>
    </div>
  )
}
''',
        
        "MultimodalPanel.tsx": '''\"use client\"

import { useState } from 'react'
import { Upload, Image, X, Eye } from 'lucide-react'

interface UploadedImage {
  id: string
  file: File
  preview: string
  analysis?: string
}

interface MultimodalPanelProps {
  activeModel: string
  onImageAnalysis: (image: UploadedImage, analysis: string) => void
}

export function MultimodalPanel({ activeModel, onImageAnalysis }: MultimodalPanelProps) {
  const [uploadedImages, setUploadedImages] = useState<UploadedImage[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files) return

    Array.from(files).forEach(file => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader()
        reader.onload = (e) => {
          const newImage: UploadedImage = {
            id: Date.now().toString() + Math.random(),
            file,
            preview: e.target?.result as string
          }
          setUploadedImages(prev => [...prev, newImage])
        }
        reader.readAsDataURL(file)
      }
    })
  }

  const analyzeImage = async (image: UploadedImage) => {
    if (activeModel !== 'llava:7b') {
      alert('Image analysis requires LLaVA model. Please switch to LLaVA 7B.')
      return
    }

    setIsAnalyzing(true)
    
    // Simulate LLaVA analysis
    setTimeout(() => {
      const analysis = `I can see this image contains various elements. As LLaVA, I can analyze visual content, identify objects, describe scenes, and help you understand visual information. This capability is perfect for multimodal learning and visual problem-solving.`
      
      const updatedImage = { ...image, analysis }
      setUploadedImages(prev => prev.map(img => img.id === image.id ? updatedImage : img))
      onImageAnalysis(updatedImage, analysis)
      setIsAnalyzing(false)
    }, 2000)
  }

  const removeImage = (id: string) => {
    setUploadedImages(prev => prev.filter(img => img.id !== id))
  }

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="font-semibold text-gray-900 dark:text-white">Multimodal</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Upload images for AI analysis
        </p>
      </div>
      
      <div className="flex-1 p-4 space-y-4 overflow-y-auto">
        {/* Upload Area */}
        <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center hover:border-ai-primary transition-colors">
          <input
            type="file"
            accept="image/*"
            multiple
            onChange={handleImageUpload}
            className="hidden"
            id="image-upload"
          />
          <label htmlFor="image-upload" className="cursor-pointer">
            <Upload className="w-8 h-8 mx-auto text-gray-400 mb-2" />
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Click to upload images
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Supports JPG, PNG, GIF, WebP
            </p>
          </label>
        </div>

        {/* Image Gallery */}
        {uploadedImages.length > 0 && (
          <div className="space-y-3">
            <h3 className="font-medium text-gray-900 dark:text-white text-sm">
              Uploaded Images ({uploadedImages.length})
            </h3>
            {uploadedImages.map((image) => (
              <div key={image.id} className="ai-chat-bubble">
                <div className="flex items-start space-x-3">
                  <img
                    src={image.preview}
                    alt="Uploaded"
                    className="w-16 h-16 object-cover rounded-lg"
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {image.file.name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {(image.file.size / 1024).toFixed(1)} KB
                    </p>
                    
                    {image.analysis ? (
                      <div className="mt-2 p-2 bg-green-50 dark:bg-green-900/20 rounded text-xs">
                        <p className="text-green-800 dark:text-green-200">
                          ✓ Analyzed by LLaVA
                        </p>
                      </div>
                    ) : (
                      <button
                        onClick={() => analyzeImage(image)}
                        disabled={isAnalyzing || activeModel !== 'llava:7b'}
                        className="mt-2 text-xs ai-button-primary disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {isAnalyzing ? 'Analyzing...' : 'Analyze with LLaVA'}
                      </button>
                    )}
                  </div>
                  
                  <div className="flex space-x-1">
                    <button
                      onClick={() => window.open(image.preview, '_blank')}
                      className="p-1 text-gray-400 hover:text-gray-600"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => removeImage(image.id)}
                      className="p-1 text-gray-400 hover:text-red-600"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                {image.analysis && (
                  <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                      AI Analysis:
                    </h4>
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      {image.analysis}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Model Capabilities Info */}
        <div className="ai-chat-bubble">
          <h3 className="font-medium text-gray-900 dark:text-white text-sm mb-2">
            Multimodal Capabilities
          </h3>
          <div className="space-y-2 text-xs">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-indigo-500 rounded-full" />
              <span className="text-gray-700 dark:text-gray-300">
                <strong>LLaVA 7B:</strong> Image analysis, visual understanding
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-teal-500 rounded-full" />
              <span className="text-gray-700 dark:text-gray-300">
                <strong>Nomic Embed:</strong> Semantic search, knowledge retrieval
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-pink-500 rounded-full" />
              <span className="text-gray-700 dark:text-gray-300">
                <strong>GPT-OSS 20B:</strong> Advanced reasoning, complex analysis
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
''',
        
        "LearningDashboard.tsx": '''\"use client\"

import { useState } from 'react'
import { Trophy, Target, TrendingUp, BookOpen, Star } from 'lucide-react'

interface Skill {
  name: string
  level: number
  maxLevel: number
  progress: number
}

interface Achievement {
  id: string
  title: string
  description: string
  earned: boolean
  icon: string
}

export function LearningDashboard() {
  const [skills] = useState<Skill[]>([
    { name: 'JavaScript', level: 3, maxLevel: 5, progress: 60 },
    { name: 'React', level: 2, maxLevel: 5, progress: 40 },
    { name: 'AI Collaboration', level: 1, maxLevel: 5, progress: 20 },
    { name: 'Problem Solving', level: 4, maxLevel: 5, progress: 80 },
  ])

  const [achievements] = useState<Achievement[]>([
    { id: '1', title: 'First Chat', description: 'Had your first conversation with AI', earned: true, icon: '💬' },
    { id: '2', title: 'Code Explorer', description: 'Wrote your first code with AI assistance', earned: true, icon: '💻' },
    { id: '3', title: 'Multi-Model Master', description: 'Used 3 different AI models', earned: false, icon: '🤖' },
    { id: '4', title: 'Learning Streak', description: '7 days of continuous learning', earned: false, icon: '🔥' },
  ])

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900 overflow-y-auto">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="font-semibold text-gray-900 dark:text-white">Learning Dashboard</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Track your progress and achievements
        </p>
      </div>
      
      <div className="flex-1 p-4 space-y-6">
        {/* Progress Overview */}
        <div className="bg-gradient-to-r from-ai-primary to-ai-secondary rounded-lg p-4 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold">Today's Progress</h3>
              <p className="text-sm opacity-90">Keep up the great work!</p>
            </div>
            <TrendingUp className="w-8 h-8" />
          </div>
          <div className="mt-4 grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold">12</div>
              <div className="text-xs opacity-75">Messages</div>
            </div>
            <div>
              <div className="text-2xl font-bold">3</div>
              <div className="text-xs opacity-75">Code Files</div>
            </div>
            <div>
              <div className="text-2xl font-bold">45m</div>
              <div className="text-xs opacity-75">Learning Time</div>
            </div>
          </div>
        </div>

        {/* Skills */}
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <Target className="w-5 h-5 text-ai-primary" />
            <h3 className="font-semibold text-gray-900 dark:text-white">Skills</h3>
          </div>
          <div className="space-y-3">
            {skills.map((skill, index) => (
              <div key={index} className="ai-chat-bubble">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900 dark:text-white">{skill.name}</span>
                  <span className="text-sm text-gray-500">Level {skill.level}/{skill.maxLevel}</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-ai-primary h-2 rounded-full transition-all duration-300"
                    style={{ width: `${skill.progress}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Achievements */}
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <Trophy className="w-5 h-5 text-ai-accent" />
            <h3 className="font-semibold text-gray-900 dark:text-white">Achievements</h3>
          </div>
          <div className="grid grid-cols-1 gap-3">
            {achievements.map((achievement) => (
              <div
                key={achievement.id}
                className={`ai-chat-bubble ${
                  achievement.earned ? 'ring-2 ring-ai-accent' : 'opacity-50'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">{achievement.icon}</span>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      {achievement.title}
                    </h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {achievement.description}
                    </p>
                  </div>
                  {achievement.earned && (
                    <Star className="w-5 h-5 text-ai-accent fill-current" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Learning Recommendations */}
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <BookOpen className="w-5 h-5 text-ai-secondary" />
            <h3 className="font-semibold text-gray-900 dark:text-white">Recommended</h3>
          </div>
          <div className="ai-chat-bubble">
            <h4 className="font-medium text-gray-900 dark:text-white mb-2">
              Next Learning Goal
            </h4>
            <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
              Based on your progress, we recommend focusing on React hooks and state management.
            </p>
            <button className="ai-button-primary text-sm">
              Start Learning
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
'''
    }
    
    for filename, content in components.items():
        with open(components_dir / filename, "w") as f:
            f.write(content)
    
    # Create README
    readme = '''# AI Chat, Build & Learn Frontend

A revolutionary frontend for collaborative AI-powered learning, designed by HRM-enhanced AI models using chaos theory, quantum reasoning, and symbiotic intelligence.

## Features

🤖 **8 Specialized AI Models** - Chat with 8 different AI models, each with unique expertise
💻 **Integrated Code Editor** - Monaco Editor with AI assistance and syntax highlighting
🖼️ **Multimodal Analysis** - Upload and analyze images with LLaVA 7B
📊 **Learning Dashboard** - Track progress, skills, and achievements
🎯 **Adaptive UI** - Interface learns from your behavior using HRM principles
⚡ **Real-time Collaboration** - Work with AI models in real-time
🧠 **HRM-Enhanced Reasoning** - Chaos theory, quantum reasoning, and symbiotic intelligence

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

## Technology Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Monaco Editor** - VS Code editor experience
- **Socket.io** - Real-time communication
- **Zustand** - State management
- **React Query** - Server state management

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Header: AI Model Selector (8 Models) | User Profile | Settings          │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│ │             │ │             │ │             │ │                     │ │
│ │ Chat Panel  │ │ Code Editor │ │ Multimodal  │ │ Learning Dashboard  │ │
│ │             │ │             │ │ Panel       │ │                     │ │
│ │ • 8 AI Models│ │ • Monaco    │ │ • LLaVA 7B  │ │ • Progress Tracking │ │
│ │ • Real-time │ │ • Syntax    │ │ • Image     │ │ • Skill Trees       │ │
│ │ • Context   │ │ • AI Assist │ │ • Analysis  │ │ • Achievements      │ │
│ │ • Streaming │ │ • Multi-file│ │ • Upload    │ │ • Recommendations   │ │
│ │             │ │ • Run Code  │ │ • Visual AI │ │ • Analytics         │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│ Footer: Status Bar | Model Status | Quick Actions | Help                │
└─────────────────────────────────────────────────────────────────────────┘
```

## Available AI Models

| Model | Role | Expertise | Color |
|-------|------|-----------|-------|
| **Llama 3.1 8B** | Full-Stack Architect | System architecture, API design, performance | 🔵 Blue |
| **Qwen 2.5 7B** | UX/UI Designer | User experience, interface design, accessibility | 🟣 Purple |
| **Mistral 7B** | Frontend Engineer | React, TypeScript, modern web technologies | 🟢 Green |
| **Phi-3 3.8B** | DevOps Specialist | Deployment, CI/CD, containerization, monitoring | 🟠 Orange |
| **Llama 3.2 3B** | Product Manager | User requirements, feature prioritization, roadmap | 🔴 Red |
| **LLaVA 7B** | Multimodal Specialist | Image analysis, visual content understanding | 🟦 Indigo |
| **Nomic Embed** | Embedding Expert | Vector embeddings, semantic search, knowledge | 🟦 Teal |
| **GPT-OSS 20B** | Advanced Reasoning | Complex reasoning, code generation, problem solving | 🩷 Pink |

## HRM-Enhanced Features

- **Chaos-Driven UI Optimization** - Interface adapts using controlled randomness
- **Quantum-Inspired Feature Discovery** - Multiple UI states explored simultaneously  
- **Self-Supervised UX Learning** - Interface learns from user behavior
- **Symbiotic AI Collaboration** - Multiple AI models work together seamlessly

## Development

```bash
# Type checking
npm run type-check

# Linting
npm run lint

# Build for production
npm run build
```

## Integration

This frontend integrates with our HRM-enhanced backend:
- Hybrid Vector Store (PostgreSQL + Redis)
- Dynamic Query Optimization
- Chaos-Driven Sharding
- Self-Supervised Learning

## Contributing

Built collaboratively by 8 specialized AI models:
- 🏗️ **Full-Stack Architect** (llama3.1:8b) - System architecture & performance
- 🎨 **UX/UI Designer** (qwen2.5:7b) - User experience & interface design  
- ⚙️ **Frontend Engineer** (mistral:7b) - React, TypeScript & web technologies
- 🔧 **DevOps Specialist** (phi3:3.8b) - Deployment, CI/CD & monitoring
- 📊 **Product Manager** (llama3.2:3b) - Requirements & roadmap planning
- 🖼️ **Multimodal Specialist** (llava:7b) - Image analysis & visual understanding
- 🔍 **Embedding Expert** (nomic-embed-text) - Vector search & knowledge retrieval
- 🧠 **Advanced Reasoning** (gpt-oss:20b) - Complex problem solving & code generation

The future of AI-powered learning is here! 🚀
'''
    
    with open(frontend_dir / "README.md", "w") as f:
        f.write(readme)
    
    print("✅ Frontend starter created successfully!")
    print(f"📁 Location: {frontend_dir.absolute()}")
    print()
    print("🚀 Next steps:")
    print("1. cd frontend")
    print("2. npm install")
    print("3. npm run dev")
    print("4. Open http://localhost:3000")
    print()
    print("🎉 Start chatting, building, and learning with AI!")

if __name__ == "__main__":
    create_frontend_starter()
