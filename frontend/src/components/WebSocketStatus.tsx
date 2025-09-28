"use client"

import { useState, useEffect } from 'react'
import { Wifi, WifiOff, Users, Zap, Activity, MessageCircle } from 'lucide-react'

export function WebSocketStatus() {
  const [isConnected, setIsConnected] = useState(false)
  const [activeUsers, setActiveUsers] = useState(0)
  const [latency, setLatency] = useState(0)
  const [messagesPerSecond, setMessagesPerSecond] = useState(0)
  const [isOptimized, setIsOptimized] = useState(false)

  useEffect(() => {
    // Enhanced WebSocket simulation with optimization detection
    const simulateWebSocket = () => {
      setIsConnected(true)
      const users = Math.floor(Math.random() * 15) + 5 // 5-20 users
      const msLatency = Math.floor(Math.random() * 20) + 5 // 5-25ms
      const mps = Math.floor(Math.random() * 50) + 10 // 10-60 messages/sec
      
      setActiveUsers(users)
      setLatency(msLatency)
      setMessagesPerSecond(mps)
      
      // Optimized if low latency and good throughput
      setIsOptimized(msLatency < 15 && mps > 30 && users > 8)
    }

    simulateWebSocket()
    const interval = setInterval(simulateWebSocket, 3000) // Update every 3 seconds
    return () => clearInterval(interval)
  }, [])

  const getConnectionIcon = () => {
    if (isOptimized) return <Zap className="w-4 h-4 text-emerald-500" />
    return isConnected ? <Wifi className="w-4 h-4 text-green-500" /> : <WifiOff className="w-4 h-4 text-red-500" />
  }

  const getStatusText = () => {
    if (isOptimized) return 'Real-time Optimized'
    return 'Real-time'
  }

  return (
    <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-300 ${
      isOptimized 
        ? 'bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800' 
        : 'bg-gray-100 dark:bg-gray-800'
    }`}>
      {getConnectionIcon()}
      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
        {getStatusText()}
      </span>
      {isConnected && (
        <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
          <div className="flex items-center space-x-1">
            <Users className="w-3 h-3" />
            <span>{activeUsers}</span>
          </div>
          <div className="flex items-center space-x-1">
            <Activity className="w-3 h-3" />
            <span>{latency}ms</span>
          </div>
          <div className="flex items-center space-x-1">
            <MessageCircle className="w-3 h-3" />
            <span>{messagesPerSecond}/s</span>
          </div>
        </div>
      )}
    </div>
  )
}
