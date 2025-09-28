"use client"

import React, { useState, useEffect } from 'react'
import { Box, Chip, Tooltip, Typography } from '@mui/material'
import { Brain, Code, MessageSquare, Image, Settings } from 'lucide-react'

interface TaskType {
  id: string
  name: string
  icon: React.ComponentType<{ className?: string }>
  color: string
  description: string
  recommendedModel: string
}

interface IntelligentModelSelectorProps {
  currentTask: string
  onTaskChange: (task: string) => void
}

const TASK_TYPES: TaskType[] = [
  { 
    id: 'general', 
    name: 'General Chat', 
    icon: MessageSquare, 
    color: 'bg-blue-500',
    description: 'Conversational AI assistance',
    recommendedModel: 'qwen2.5:7b'
  },
  { 
    id: 'coding', 
    name: 'Code Generation', 
    icon: Code, 
    color: 'bg-green-500',
    description: 'Programming and development tasks',
    recommendedModel: 'qwen2.5:7b'
  },
  { 
    id: 'analysis', 
    name: 'Analysis', 
    icon: Brain, 
    color: 'bg-purple-500',
    description: 'Complex reasoning and analysis',
    recommendedModel: 'qwen2.5:14b'
  },
  { 
    id: 'multimodal', 
    name: 'Multimodal', 
    icon: Image, 
    color: 'bg-orange-500',
    description: 'Image and visual content processing',
    recommendedModel: 'llava:7b'
  },
  { 
    id: 'system', 
    name: 'System Tasks', 
    icon: Settings, 
    color: 'bg-red-500',
    description: 'System administration and DevOps',
    recommendedModel: 'llama3.2:3b'
  }
]

export function IntelligentModelSelector({ currentTask, onTaskChange }: IntelligentModelSelectorProps) {
  const [detectedTask, setDetectedTask] = useState(currentTask)
  const [confidence, setConfidence] = useState(0.95)

  // Auto-detect task type based on context (this would be enhanced with actual AI analysis)
  useEffect(() => {
    // In a real implementation, this would analyze the conversation context
    // For now, we'll start with general chat and let the AI determine the task
    setDetectedTask('general')
    setConfidence(0.85)
  }, [])

  const currentTaskInfo = TASK_TYPES.find(task => task.id === detectedTask) || TASK_TYPES[0]

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <Tooltip title={`Task: ${currentTaskInfo.description}`}>
        <Chip
          icon={<currentTaskInfo.icon className="w-4 h-4" />}
          label={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="caption" sx={{ color: 'white', fontWeight: 600 }}>
                {currentTaskInfo.name}
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                ({Math.round(confidence * 100)}% confidence)
              </Typography>
            </Box>
          }
          sx={{
            background: currentTaskInfo.color,
            color: 'white',
            '& .MuiChip-icon': { color: 'white' },
            height: 32,
            '& .MuiChip-label': { px: 1 }
          }}
        />
      </Tooltip>
    </Box>
  )
}
