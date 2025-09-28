'use client'

import { useEffect, useCallback } from 'react'

interface KeyboardShortcutsConfig {
  onSendMessage?: () => void
  onToggleVoiceSelector?: () => void
  onToggleStatusIndicator?: () => void
  onSwitchPanel?: (panelId: string) => void
  onToggleSidebar?: () => void
  onFocusInput?: () => void
  onEscape?: () => void
}

export const useKeyboardShortcuts = (config: KeyboardShortcutsConfig) => {
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    // Don't trigger shortcuts when typing in inputs
    if (
      event.target instanceof HTMLInputElement ||
      event.target instanceof HTMLTextAreaElement ||
      event.target instanceof HTMLSelectElement
    ) {
      return
    }

    const { key, ctrlKey, metaKey, shiftKey, altKey } = event
    const isModifierPressed = ctrlKey || metaKey

    switch (key) {
      case 'Enter':
        if (isModifierPressed && config.onSendMessage) {
          event.preventDefault()
          config.onSendMessage()
        }
        break

      case 'v':
        if (isModifierPressed && shiftKey && config.onToggleVoiceSelector) {
          event.preventDefault()
          config.onToggleVoiceSelector()
        }
        break

      case 's':
        if (isModifierPressed && shiftKey && config.onToggleStatusIndicator) {
          event.preventDefault()
          config.onToggleStatusIndicator()
        }
        break

      case 'b':
        if (isModifierPressed && config.onToggleSidebar) {
          event.preventDefault()
          config.onToggleSidebar()
        }
        break

      case 'i':
        if (isModifierPressed && config.onFocusInput) {
          event.preventDefault()
          config.onFocusInput()
        }
        break

      case 'Escape':
        if (config.onEscape) {
          event.preventDefault()
          config.onEscape()
        }
        break

      // Panel switching shortcuts
      case '1':
        if (isModifierPressed && config.onSwitchPanel) {
          event.preventDefault()
          config.onSwitchPanel('chat')
        }
        break
      case '2':
        if (isModifierPressed && config.onSwitchPanel) {
          event.preventDefault()
          config.onSwitchPanel('agents')
        }
        break
      case '3':
        if (isModifierPressed && config.onSwitchPanel) {
          event.preventDefault()
          config.onSwitchPanel('optimization')
        }
        break
      case '4':
        if (isModifierPressed && config.onSwitchPanel) {
          event.preventDefault()
          config.onSwitchPanel('code')
        }
        break
      case '5':
        if (isModifierPressed && config.onSwitchPanel) {
          event.preventDefault()
          config.onSwitchPanel('multimodal')
        }
        break
      case '6':
        if (isModifierPressed && config.onSwitchPanel) {
          event.preventDefault()
          config.onSwitchPanel('learning')
        }
        break
    }
  }, [config])

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])

  return {
    shortcuts: {
      'Ctrl/Cmd + Enter': 'Send message',
      'Ctrl/Cmd + Shift + V': 'Toggle voice selector',
      'Ctrl/Cmd + Shift + S': 'Toggle status indicator',
      'Ctrl/Cmd + B': 'Toggle sidebar',
      'Ctrl/Cmd + I': 'Focus input',
      'Escape': 'Close panels',
      'Ctrl/Cmd + 1-6': 'Switch panels'
    }
  }
}
