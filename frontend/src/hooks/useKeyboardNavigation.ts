'use client'

import { useEffect, useCallback } from 'react'

interface UseKeyboardNavigationProps {
  onNext: () => void
  onPrevious: () => void
  onSelect: () => void
  onEscape: () => void
  disabled?: boolean
}

export function useKeyboardNavigation({
  onNext,
  onPrevious,
  onSelect,
  onEscape,
  disabled = false
}: UseKeyboardNavigationProps) {
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (disabled) return

    switch (event.key) {
      case 'ArrowDown':
      case 'ArrowRight':
        event.preventDefault()
        onNext()
        break
      case 'ArrowUp':
      case 'ArrowLeft':
        event.preventDefault()
        onPrevious()
        break
      case 'Enter':
      case ' ':
        event.preventDefault()
        onSelect()
        break
      case 'Escape':
        event.preventDefault()
        onEscape()
        break
    }
  }, [onNext, onPrevious, onSelect, onEscape, disabled])

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])
}

interface UseFocusManagementProps {
  items: any[]
  activeIndex: number
  onIndexChange: (index: number) => void
  containerRef: React.RefObject<HTMLElement>
}

export function useFocusManagement({
  items,
  activeIndex,
  onIndexChange,
  containerRef
}: UseFocusManagementProps) {
  const focusNext = useCallback(() => {
    const nextIndex = (activeIndex + 1) % items.length
    onIndexChange(nextIndex)
  }, [activeIndex, items.length, onIndexChange])

  const focusPrevious = useCallback(() => {
    const prevIndex = activeIndex === 0 ? items.length - 1 : activeIndex - 1
    onIndexChange(prevIndex)
  }, [activeIndex, items.length, onIndexChange])

  const focusItem = useCallback((index: number) => {
    onIndexChange(index)
  }, [onIndexChange])

  // Auto-focus the active item
  useEffect(() => {
    if (containerRef.current) {
      const focusableElement = containerRef.current.querySelector(
        `[data-navigation-index="${activeIndex}"]`
      ) as HTMLElement
      
      if (focusableElement) {
        focusableElement.focus()
      }
    }
  }, [activeIndex, containerRef])

  return {
    focusNext,
    focusPrevious,
    focusItem
  }
}

interface UseKeyboardShortcutsProps {
  shortcuts: Record<string, () => void>
  disabled?: boolean
}

export function useKeyboardShortcuts({
  shortcuts,
  disabled = false
}: UseKeyboardShortcutsProps) {
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (disabled) return

    // Check for modifier keys
    const modifiers = []
    if (event.ctrlKey) modifiers.push('ctrl')
    if (event.metaKey) modifiers.push('meta')
    if (event.altKey) modifiers.push('alt')
    if (event.shiftKey) modifiers.push('shift')

    const key = modifiers.length > 0 
      ? `${modifiers.join('+')}+${event.key.toLowerCase()}`
      : event.key.toLowerCase()

    if (shortcuts[key]) {
      event.preventDefault()
      shortcuts[key]()
    }
  }, [shortcuts, disabled])

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])
}
