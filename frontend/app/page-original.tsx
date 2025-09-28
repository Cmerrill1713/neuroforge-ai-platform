"use client"

import React, { useState, useEffect } from 'react'
import { ChatPanel } from '@/components/ChatPanel'
import { CodeEditor } from '@/components/CodeEditor'
import { LearningDashboard } from '@/components/LearningDashboard'
import { MultimodalPanel } from '@/components/MultimodalPanel'
import { Header } from '@/components/Header'
import { AIModelSelector } from '@/components/AIModelSelector'
import { RedisCacheIndicator } from '@/components/RedisCacheIndicator'
import { WebSocketStatus } from '@/components/WebSocketStatus'
import { PerformanceMonitor } from '@/components/PerformanceMonitor'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  MessageCircle, 
  Code, 
  Image, 
  BarChart3, 
  Plus,
  Sparkles,
  Zap,
  Brain,
  Palette,
  Mic,
  MicOff,
  Volume2,
  Settings,
  Wand2,
  Layers,
  Cpu,
  Database
} from 'lucide-react'

export default function Home() {
  const [activeModel, setActiveModel] = useState('qwen2.5:7b')
  const [darkMode, setDarkMode] = useState(true)
  const [activePanel, setActivePanel] = useState('chat')
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(false)
  const [scrollY, setScrollY] = useState(0)
  const [isLoaded, setIsLoaded] = useState(false)

  useEffect(() => {
    setIsLoaded(true)
    
    const handleScroll = () => setScrollY(window.scrollY)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const panels = [
    { 
      id: 'chat', 
      label: 'AI Chat', 
      icon: MessageCircle, 
      color: 'from-blue-500 to-purple-600',
      description: 'Intelligent conversations with AI',
      trend: 'AI-Powered Personalization'
    },
    { 
      id: 'code', 
      label: 'Code Editor', 
      icon: Code, 
      color: 'from-green-500 to-teal-600',
      description: 'AI-assisted development',
      trend: 'Component-Driven Development'
    },
    { 
      id: 'multimodal', 
      label: 'Multimodal', 
      icon: Image, 
      color: 'from-pink-500 to-rose-600',
      description: 'Vision and image analysis',
      trend: 'AR/VR Integration'
    },
    { 
      id: 'learning', 
      label: 'Learning', 
      icon: BarChart3, 
      color: 'from-orange-500 to-red-600',
      description: 'Progress tracking & analytics',
      trend: 'Data Visualization'
    }
  ]

  return (
    <div className={`h-screen flex flex-col ${darkMode ? 'dark' : ''} bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900`}>
      {/* Enhanced Header with 2025 Trends */}
      <motion.header 
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="bg-white/10 backdrop-blur-xl border-b border-white/20 px-6 py-4 relative"
      >
        {/* Animated background gradient */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10 opacity-50" />
        
        <div className="relative flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <motion.div
              whileHover={{ scale: 1.05, rotate: 5 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center space-x-3"
            >
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent">
                  AI Studio 2025
                </h1>
                <p className="text-sm text-white/70">Next-Gen Development Environment</p>
              </div>
            </motion.div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Voice UI Toggle - 2025 Trend */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsVoiceEnabled(!isVoiceEnabled)}
              className={`p-2 rounded-lg transition-all duration-300 ${
                isVoiceEnabled 
                  ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                  : 'bg-white/10 text-white/70 hover:bg-white/20'
              }`}
            >
              {isVoiceEnabled ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
            </motion.button>

            <AIModelSelector 
              activeModel={activeModel} 
              onModelChange={setActiveModel}
                customModelNames={{}}
                onCustomNameChange={() => {}}
            />
            <RedisCacheIndicator />
            <WebSocketStatus />
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setDarkMode(!darkMode)}
              className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
            >
              <Palette className="w-5 h-5 text-white" />
            </motion.button>
          </div>
        </div>
      </motion.header>

      {/* Performance Monitor */}
      <PerformanceMonitor />

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Enhanced Sidebar with 3D Effects */}
        <motion.aside 
          initial={{ x: -300, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          className={`${sidebarCollapsed ? 'w-16' : 'w-64'} bg-white/5 backdrop-blur-xl border-r border-white/10 transition-all duration-300 relative`}
        >
          {/* 3D Background Effect */}
          <div className="absolute inset-0 bg-gradient-to-b from-blue-500/5 to-purple-500/5" />
          
          <div className="relative p-4">
            <div className="space-y-2">
              {panels.map((panel, index) => (
                <motion.button
                  key={panel.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ 
                    scale: 1.02, 
                    x: 5,
                    boxShadow: "0 10px 25px rgba(0,0,0,0.2)"
                  }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setActivePanel(panel.id)}
                  className={`w-full flex items-center space-x-3 p-3 rounded-xl transition-all duration-300 ${
                    activePanel === panel.id
                      ? `bg-gradient-to-r ${panel.color} text-white shadow-lg border border-white/20`
                      : 'text-white/70 hover:text-white hover:bg-white/10 border border-transparent'
                  }`}
                >
                  <panel.icon className="w-5 h-5" />
                  {!sidebarCollapsed && (
                    <div className="flex-1 text-left">
                      <span className="font-medium block">{panel.label}</span>
                      <span className="text-xs opacity-70">{panel.trend}</span>
                    </div>
                  )}
                </motion.button>
              ))}
            </div>
            
            {/* Enhanced Model Status with 3D Card */}
            {!sidebarCollapsed && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-8 p-4 bg-white/5 rounded-xl border border-white/10 backdrop-blur-sm hover:bg-white/10 transition-all duration-300"
              >
                <div className="flex items-center space-x-2 mb-2">
                  <Brain className="w-4 h-4 text-green-400" />
                  <span className="text-sm font-medium text-white">Active Model</span>
                </div>
                <p className="text-xs text-white/60 mb-2">{activeModel}</p>
                <div className="flex items-center space-x-1 mb-3">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="text-xs text-green-400">Online</span>
                </div>
                
                {/* AI Performance Indicators */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-white/60">Performance</span>
                    <span className="text-green-400">Excellent</span>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-1">
                    <div className="bg-gradient-to-r from-green-400 to-blue-500 h-1 rounded-full w-4/5"></div>
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </motion.aside>

        {/* Main Content */}
        <main className="flex-1 flex flex-col">
          {/* Enhanced Panel Header with Micro-interactions */}
          <div className="bg-white/5 backdrop-blur-xl border-b border-white/10 px-6 py-4 relative">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-purple-500/5" />
            
            <div className="relative flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {(() => {
                  const currentPanel = panels.find(p => p.id === activePanel);
                  return currentPanel && (
                    <motion.div 
                      whileHover={{ rotate: 360 }}
                      transition={{ duration: 0.5 }}
                      className={`w-8 h-8 bg-gradient-to-r ${currentPanel.color} rounded-lg flex items-center justify-center shadow-lg`}
                    >
                      <currentPanel.icon className="w-4 h-4 text-white" />
                    </motion.div>
                  );
                })()}
                <div>
                  <h2 className="text-xl font-semibold text-white">
                    {panels.find(p => p.id === activePanel)?.label}
                  </h2>
                  <p className="text-sm text-white/60">
                    {panels.find(p => p.id === activePanel)?.description}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                {/* Voice Status Indicator */}
                {isVoiceEnabled && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="flex items-center space-x-2 px-3 py-1 bg-green-500/20 rounded-full border border-green-500/30"
                  >
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                    <span className="text-xs text-green-400">Voice Active</span>
                  </motion.div>
                )}
                
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
                >
                  <Zap className="w-4 h-4 text-white" />
                </motion.button>
              </div>
            </div>
          </div>

          {/* Enhanced Panel Content with Scroll-triggered Animations */}
          <div className="flex-1 overflow-hidden">
            <AnimatePresence mode="wait">
              <motion.div
                key={activePanel}
                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -20, scale: 0.95 }}
                transition={{ duration: 0.4, ease: "easeInOut" }}
                className="h-full relative"
              >
                {/* 3D Background Effects */}
                <div className="absolute inset-0">
                  <div className="absolute top-0 left-0 w-32 h-32 bg-gradient-to-br from-blue-500/10 to-purple-600/10 rounded-full blur-xl animate-pulse" />
                  <div className="absolute bottom-0 right-0 w-24 h-24 bg-gradient-to-br from-green-500/10 to-teal-600/10 rounded-full blur-lg animate-bounce" />
                </div>

                {activePanel === 'chat' && (
                  <div className="h-full bg-gradient-to-br from-white/5 to-white/10 backdrop-blur-sm relative">
                    <ChatPanel activeModel={activeModel} />
                  </div>
                )}
                {activePanel === 'code' && (
                  <div className="h-full bg-gradient-to-br from-green-500/5 to-teal-500/10 backdrop-blur-sm relative">
                    <CodeEditor />
                  </div>
                )}
                {activePanel === 'multimodal' && (
                  <div className="h-full bg-gradient-to-br from-pink-500/5 to-rose-500/10 backdrop-blur-sm relative">
                    <MultimodalPanel 
                      activeModel={activeModel}
                      onImageAnalysis={(image, analysis) => {
                        console.log('Image analyzed:', image.file.name, analysis)
                      }}
                    />
                  </div>
                )}
                {activePanel === 'learning' && (
                  <div className="h-full bg-gradient-to-br from-orange-500/5 to-red-500/10 backdrop-blur-sm relative">
                    <LearningDashboard />
                  </div>
                )}
              </motion.div>
            </AnimatePresence>
          </div>
        </main>
      </div>

      {/* Enhanced Floating Action Button with 3D Effect */}
      <motion.button
        initial={{ scale: 0, rotate: -180 }}
        animate={{ scale: 1, rotate: 0 }}
        whileHover={{ 
          scale: 1.1, 
          rotate: 90,
          boxShadow: "0 20px 40px rgba(0,0,0,0.3)"
        }}
        whileTap={{ scale: 0.9 }}
        className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full shadow-2xl flex items-center justify-center z-50 border border-white/20"
      >
        <Plus className="w-6 h-6 text-white" />
      </motion.button>

      {/* Enhanced Background Effects with 3D Elements */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 via-purple-600/20 to-pink-600/20"></div>
        
        {/* Floating 3D Elements */}
        <motion.div 
          animate={{ 
            y: [0, -20, 0],
            rotate: [0, 5, 0]
          }}
          transition={{ 
            duration: 6,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute top-20 left-10 w-32 h-32 bg-gradient-to-br from-blue-500/10 to-purple-600/10 rounded-full blur-xl"
        />
        
        <motion.div 
          animate={{ 
            y: [0, 20, 0],
            rotate: [0, -5, 0]
          }}
          transition={{ 
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute bottom-20 right-10 w-24 h-24 bg-gradient-to-br from-green-500/10 to-teal-600/10 rounded-full blur-lg"
        />
        
        <motion.div 
          animate={{ 
            y: [0, -15, 0],
            x: [0, 10, 0]
          }}
          transition={{ 
            duration: 7,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="absolute top-1/2 left-1/4 w-16 h-16 bg-gradient-to-br from-purple-500/10 to-pink-600/10 rounded-full blur-md"
        />
      </div>

      {/* Voice UI Overlay - 2025 Trend */}
      <AnimatePresence>
        {isVoiceEnabled && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="fixed top-20 right-6 bg-white/10 backdrop-blur-xl rounded-2xl p-4 border border-white/20 z-40"
          >
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse" />
              <span className="text-white text-sm">Voice commands active</span>
              <Volume2 className="w-4 h-4 text-green-400" />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}