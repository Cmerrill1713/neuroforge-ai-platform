'use client'

import { useRef, useCallback, useState, useEffect } from 'react'

interface AudioFeedbackConfig {
  enabled: boolean
  volume: number
  sounds: {
    messageSent: string
    messageReceived: string
    error: string
    success: string
    notification: string
    click: string
    hover: string
  }
}

class AudioFeedbackManager {
  private audioContext: AudioContext | null = null
  private config: AudioFeedbackConfig
  private sounds: Map<string, AudioBuffer> = new Map()

  constructor(config: AudioFeedbackConfig) {
    this.config = config
    // Only initialize on client side - completely skip during SSR
    if (typeof window !== 'undefined' && typeof document !== 'undefined') {
      this.initializeAudioContext()
    }
  }

  private async initializeAudioContext() {
    try {
      // Double check window exists (client-side only)
      if (typeof window === 'undefined') return
      
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
      await this.generateSounds()
    } catch (error) {
      console.warn('Audio context not supported:', error)
    }
  }

  private async generateSounds() {
    if (!this.audioContext) return

    // Generate synthetic sounds
    this.sounds.set('messageSent', this.generateTone(800, 0.1, 'sine'))
    this.sounds.set('messageReceived', this.generateTone(600, 0.15, 'sine'))
    this.sounds.set('error', this.generateTone(300, 0.3, 'sawtooth'))
    this.sounds.set('success', this.generateChord([523, 659, 784], 0.2))
    this.sounds.set('notification', this.generateTone(1000, 0.1, 'square'))
    this.sounds.set('click', this.generateTone(1000, 0.05, 'square'))
    this.sounds.set('hover', this.generateTone(1200, 0.03, 'sine'))
  }

  private generateTone(frequency: number, duration: number, type: OscillatorType): AudioBuffer {
    if (!this.audioContext) throw new Error('Audio context not initialized')

    const sampleRate = this.audioContext.sampleRate
    const buffer = this.audioContext.createBuffer(1, sampleRate * duration, sampleRate)
    const data = buffer.getChannelData(0)

    for (let i = 0; i < data.length; i++) {
      const t = i / sampleRate
      let value = 0

      switch (type) {
        case 'sine':
          value = Math.sin(2 * Math.PI * frequency * t)
          break
        case 'square':
          value = Math.sin(2 * Math.PI * frequency * t) > 0 ? 1 : -1
          break
        case 'sawtooth':
          value = 2 * (t * frequency - Math.floor(t * frequency + 0.5))
          break
      }

      // Apply envelope
      const envelope = Math.exp(-t * 5)
      data[i] = value * envelope * 0.3
    }

    return buffer
  }

  private generateChord(frequencies: number[], duration: number): AudioBuffer {
    if (!this.audioContext) throw new Error('Audio context not initialized')

    const sampleRate = this.audioContext.sampleRate
    const buffer = this.audioContext.createBuffer(1, sampleRate * duration, sampleRate)
    const data = buffer.getChannelData(0)

    for (let i = 0; i < data.length; i++) {
      const t = i / sampleRate
      let value = 0

      frequencies.forEach(freq => {
        value += Math.sin(2 * Math.PI * freq * t) / frequencies.length
      })

      // Apply envelope
      const envelope = Math.exp(-t * 3)
      data[i] = value * envelope * 0.2
    }

    return buffer
  }

  async playSound(soundName: keyof AudioFeedbackConfig['sounds']) {
    if (!this.config.enabled || !this.audioContext || typeof window === 'undefined') return

    try {
      const buffer = this.sounds.get(soundName)
      if (!buffer) return

      const source = this.audioContext.createBufferSource()
      const gainNode = this.audioContext.createGain()

      source.buffer = buffer
      gainNode.gain.value = this.config.volume

      source.connect(gainNode)
      gainNode.connect(this.audioContext.destination)

      source.start()
    } catch (error) {
      console.warn('Error playing sound:', error)
    }
  }

  updateConfig(newConfig: Partial<AudioFeedbackConfig>) {
    this.config = { ...this.config, ...newConfig }
  }
}

// Hook for using audio feedback
export const useAudioFeedback = (config: AudioFeedbackConfig) => {
  const audioManagerRef = useRef<AudioFeedbackManager | null>(null)
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    // Only initialize on client side - completely skip during SSR
    if (typeof window !== 'undefined' && typeof document !== 'undefined') {
      setIsClient(true)
      if (!audioManagerRef.current) {
        audioManagerRef.current = new AudioFeedbackManager(config)
      }
    }
  }, [config])

  const playSound = useCallback((soundName: keyof AudioFeedbackConfig['sounds']) => {
    if (isClient && audioManagerRef.current && typeof window !== 'undefined') {
      audioManagerRef.current.playSound(soundName)
    }
  }, [isClient])

  const updateConfig = useCallback((newConfig: Partial<AudioFeedbackConfig>) => {
    if (isClient && audioManagerRef.current && typeof window !== 'undefined') {
      audioManagerRef.current.updateConfig(newConfig)
    }
  }, [isClient])

  return {
    playSound,
    updateConfig,
    sounds: {
      messageSent: () => playSound('messageSent'),
      messageReceived: () => playSound('messageReceived'),
      error: () => playSound('error'),
      success: () => playSound('success'),
      notification: () => playSound('notification'),
      click: () => playSound('click'),
      hover: () => playSound('hover')
    }
  }
}

// Default audio feedback configuration
export const defaultAudioConfig: AudioFeedbackConfig = {
  enabled: true,
  volume: 0.3,
  sounds: {
    messageSent: 'messageSent',
    messageReceived: 'messageReceived',
    error: 'error',
    success: 'success',
    notification: 'notification',
    click: 'click',
    hover: 'hover'
  }
}
