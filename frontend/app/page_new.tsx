'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Chat as ChatIcon,
  SmartToy as SmartToyIcon,
  TrendingUp as TrendingUpIcon,
  Code as CodeIcon,
  Visibility as VisibilityIcon,
  School as SchoolIcon
} from '@mui/icons-material'

// Import enhanced components
import { MuiEnhancedChatPanel } from '@/components/MuiEnhancedChatPanel'
import { CodeEditor } from '@/components/CodeEditor'
import { LearningDashboard } from '@/components/LearningDashboard'
import { MultimodalPanel } from '@/components/MultimodalPanel'
import { AgentControlPanel } from '@/components/AgentControlPanel'
import { SelfOptimizationPanel } from "@/components/SelfOptimizationPanel"

// Import new modular layout system
import { ResponsiveLayoutProvider } from '@/components/layouts/ResponsiveLayoutProvider'

const panels = [
  { 
    id: 'chat', 
    label: 'AI Assistant', 
    icon: ChatIcon, 
    color: 'primary' as const,
    description: 'Intelligent conversations with AI + Voice + Advanced features',
    trend: 'Personal AI Assistant'
  },
  { 
    id: 'agents', 
    label: 'AI Agents', 
    icon: SmartToyIcon, 
    color: 'secondary' as const,
    description: 'Prompt-based intelligent agents for productivity and automation',
    trend: 'Smart Automation'
  },
  { 
    id: 'optimization', 
    label: 'Self-Optimization', 
    icon: TrendingUpIcon, 
    color: 'success' as const, 
    description: 'AI-driven task automation and productivity enhancement', 
    trend: 'Autonomous Productivity' 
  },
  { 
    id: 'code', 
    label: 'Code Assistant', 
    icon: CodeIcon, 
    color: 'info' as const,
    description: 'AI-assisted coding and development with intelligent suggestions',
    trend: 'Smart Development'
  },
  { 
    id: 'multimodal', 
    label: 'Vision Assistant', 
    icon: VisibilityIcon, 
    color: 'warning' as const,
    description: 'Upload images for AI analysis and visual understanding',
    trend: 'Visual Intelligence'
  },
  { 
    id: 'learning', 
    label: 'Learning Hub', 
    icon: SchoolIcon, 
    color: 'error' as const,
    description: 'Track your progress and achievements in your personal AI learning journey',
    trend: 'Growth Analytics'
  }
]

export default function PersonalAIAssistant() {
  const [activeModel, setActiveModel] = useState('qwen2.5:7b')

  const renderPanelContent = (panelId: string) => {
    switch (panelId) {
      case 'chat':
        return (
          <MuiEnhancedChatPanel 
            activeModel={activeModel} 
            customModelName="qwen2.5:7b"
            onSwitchPanel={() => {}}
          />
        )
      case 'agents':
        return <AgentControlPanel />
      case 'optimization':
        return <SelfOptimizationPanel />
      case 'code':
        return <CodeEditor />
      case 'multimodal':
        return (
          <MultimodalPanel 
            activeModel={activeModel}
            onImageAnalysis={(image, analysis) => {
              console.log('Image analyzed:', image.file.name, analysis)
            }}
          />
        )
      case 'learning':
        return <LearningDashboard />
      default:
        return (
          <MuiEnhancedChatPanel 
            activeModel={activeModel} 
            customModelName="qwen2.5:7b"
            onSwitchPanel={() => {}}
          />
        )
    }
  }

  return (
    <ResponsiveLayoutProvider panels={panels}>
      <AnimatePresence mode="wait">
        <motion.div
          key={activeModel} // This will be controlled by the layout provider
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.4, ease: "easeInOut" }}
          style={{ height: '100%' }}
        >
          {renderPanelContent('chat')} {/* This will be controlled by the layout provider */}
        </motion.div>
      </AnimatePresence>
    </ResponsiveLayoutProvider>
  )
}
