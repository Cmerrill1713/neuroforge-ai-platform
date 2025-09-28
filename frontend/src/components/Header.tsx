"use client"

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
            customModelNames={{}}
            onCustomNameChange={() => {}}
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
