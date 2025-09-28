"use client"

import { useState, useEffect } from 'react'
import { ChevronDown, Bot, Edit2, Save, X, Database, Code, GitBranch } from 'lucide-react'

interface AIModelSelectorProps {
  activeModel: string
  onModelChange: (model: string) => void
  customModelNames: Record<string, string>
  onCustomNameChange: (names: Record<string, string>) => void
}

interface CodebaseInfo {
  name: string
  path: string
  branch: string
  lastCommit: string
  connected: boolean
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

export function AIModelSelector({ activeModel, onModelChange, customModelNames, onCustomNameChange }: AIModelSelectorProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [editingModel, setEditingModel] = useState<string | null>(null)
  const [editingName, setEditingName] = useState('')
  
  const currentModel = AI_MODELS.find(m => m.id === activeModel)
  
  // Real codebase info - fetched from API
  const [codebaseInfo, setCodebaseInfo] = useState<CodebaseInfo>({
    name: 'AI Studio Enhanced',
    path: '/Users/christianmerrill/Prompt Engineering/frontend',
    branch: 'main',
    lastCommit: '2 hours ago',
    connected: false
  });

  useEffect(() => {
    // Fetch real codebase info from API
    const fetchCodebaseInfo = async () => {
      try {
        const response = await fetch('/api/codebase/info');
        if (response.ok) {
          const data = await response.json();
          setCodebaseInfo(data);
        }
      } catch (error) {
        console.error('Failed to fetch codebase info:', error);
      }
    };

    fetchCodebaseInfo();
  }, []);

  const getModelCapabilities = (modelId: string): string => {
    const capabilities: Record<string, string> = {
      'llama3.1:8b': 'Best for: System design, architecture decisions, performance optimization',
      'qwen2.5:7b': 'Best for: UI/UX design, accessibility, user experience',
      'mistral:7b': 'Best for: Frontend coding, React/TypeScript, web development',
      'phi3:3.8b': 'Best for: DevOps, deployment, CI/CD, monitoring',
      'llama3.2:3b': 'Best for: Product strategy, requirements, roadmap planning',
      'llava:7b': 'Best for: Image analysis, visual content understanding',
      'nomic-embed-text:latest': 'Best for: Semantic search, knowledge retrieval',
      'gpt-oss:20b': 'Best for: Complex reasoning, advanced problem solving'
    }
    return capabilities[modelId] || 'Specialized AI capabilities'
  }

  const getDisplayName = (modelId: string): string => {
    return customModelNames[modelId] || AI_MODELS.find(m => m.id === modelId)?.name || modelId
  }

  const handleRenameStart = (modelId: string) => {
    setEditingModel(modelId)
    setEditingName(getDisplayName(modelId))
  }

  const handleRenameSave = () => {
    if (editingModel && editingName.trim()) {
      const newCustomNames = {
        ...customModelNames,
        [editingModel]: editingName.trim()
      }
      onCustomNameChange(newCustomNames)
    }
    setEditingModel(null)
    setEditingName('')
  }

  const handleRenameCancel = () => {
    setEditingModel(null)
    setEditingName('')
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 relative group"
      >
        <div className={`w-3 h-3 rounded-full ${currentModel?.color}`} />
        <Bot className="w-4 h-4" />
        <span className="text-sm font-medium">{getDisplayName(activeModel)}</span>
        {codebaseInfo.connected && (
          <Database className="w-3 h-3 text-green-500"  />
        )}
        <ChevronDown className="w-4 h-4" />
        
        {/* Codebase connection indicator */}
        {codebaseInfo.connected && (
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white dark:border-gray-800">
            <div className="w-full h-full bg-green-400 rounded-full animate-pulse"></div>
          </div>
        )}
      </button>
      
      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50 max-h-96 overflow-y-auto">
          <div className="p-3 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-gray-900 dark:text-white text-sm">Choose AI Model</h3>
              {codebaseInfo.connected && (
                <div className="flex items-center space-x-1 text-xs text-green-600 dark:text-green-400">
                  <Database className="w-3 h-3" />
                  <span>Connected</span>
                </div>
              )}
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">Select specialized AI for your task</p>
            
            {/* Codebase info */}
            {codebaseInfo.connected && (
              <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-2 border border-green-200 dark:border-green-800">
                <div className="flex items-center space-x-2 mb-1">
                  <Code className="w-3 h-3 text-green-600 dark:text-green-400" />
                  <span className="text-xs font-medium text-green-800 dark:text-green-200">{codebaseInfo.name}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <GitBranch className="w-3 h-3 text-green-600 dark:text-green-400" />
                  <span className="text-xs text-green-700 dark:text-green-300">{codebaseInfo.branch} • {codebaseInfo.lastCommit}</span>
                </div>
              </div>
            )}
          </div>
          {AI_MODELS.map((model) => (
            <div
              key={model.id}
              className="w-full flex items-start space-x-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 first:rounded-t-lg last:rounded-b-lg border-b border-gray-100 dark:border-gray-700 last:border-b-0 group"
            >
              <div className={`w-4 h-4 rounded-full ${model.color} mt-0.5 flex-shrink-0`} />
              <div className="flex-1 text-left min-w-0">
                {editingModel === model.id ? (
                  <div className="flex items-center space-x-2 mb-2">
                    <input
                      type="text"
                      value={editingName}
                      onChange={(e) => setEditingName(e.target.value)}
                      className="text-sm font-medium bg-transparent border-b border-blue-500 text-gray-900 dark:text-white focus:outline-none"
                      autoFocus
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleRenameSave()
                        if (e.key === 'Escape') handleRenameCancel()
                      }}
                    />
                    <button
                      onClick={handleRenameSave}
                      className="p-1 hover:bg-green-100 dark:hover:bg-green-900 rounded"
                    >
                      <Save className="w-3 h-3 text-green-600 dark:text-green-400" />
                    </button>
                    <button
                      onClick={handleRenameCancel}
                      className="p-1 hover:bg-red-100 dark:hover:bg-red-900 rounded"
                    >
                      <X className="w-3 h-3 text-red-600 dark:text-red-400" />
                    </button>
                  </div>
                ) : (
                  <div className="flex items-center justify-between mb-1">
                    <div className="font-medium text-gray-900 dark:text-white text-sm">
                      {getDisplayName(model.id)}
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleRenameStart(model.id)
                      }}
                      className="opacity-0 group-hover:opacity-100 p-1 hover:bg-blue-100 dark:hover:bg-blue-900 rounded transition-opacity"
                    >
                      <Edit2 className="w-3 h-3 text-blue-600 dark:text-blue-400" />
                    </button>
                  </div>
                )}
                <div className="text-xs text-gray-600 dark:text-gray-300 font-medium">{model.role}</div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">{model.expertise}</div>
                <div className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                  {getModelCapabilities(model.id)}
                </div>
                {codebaseInfo.connected && (
                  <div className="flex items-center space-x-1 mt-2">
                    <Database className="w-3 h-3 text-green-500" />
                    <span className="text-xs text-green-600 dark:text-green-400">Codebase Aware</span>
                  </div>
                )}
              </div>
              <button
                onClick={() => {
                  onModelChange(model.id)
                  setIsOpen(false)
                }}
                className="flex-shrink-0"
              >
                {model.id === activeModel && (
                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2" />
                )}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
