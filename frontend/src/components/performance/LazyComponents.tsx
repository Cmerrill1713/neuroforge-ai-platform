'use client'

import React, { Suspense, lazy, ComponentType } from 'react'
import { Box, CircularProgress, Skeleton } from '@mui/material'
import { motion } from 'framer-motion'

// Loading components
const LoadingSpinner = () => (
  <Box 
    sx={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '200px',
      flexDirection: 'column',
      gap: 2
    }}
  >
    <CircularProgress size={40} />
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      Loading...
    </motion.div>
  </Box>
)

const SkeletonLoader = () => (
  <Box sx={{ p: 3 }}>
    <Skeleton variant="text" width="60%" height={40} sx={{ mb: 2 }} />
    <Skeleton variant="rectangular" width="100%" height={200} sx={{ mb: 2 }} />
    <Skeleton variant="text" width="80%" height={20} sx={{ mb: 1 }} />
    <Skeleton variant="text" width="90%" height={20} />
  </Box>
)

// Lazy load components with error boundaries
export const LazyChatPanel = lazy(() => 
  import('@/components/MuiEnhancedChatPanel').then(module => ({
    default: module.MuiEnhancedChatPanel
  }))
)

export const LazyCodeEditor = lazy(() => 
  import('@/components/CodeEditor').then(module => ({
    default: module.CodeEditor
  }))
)

export const LazyLearningDashboard = lazy(() => 
  import('@/components/LearningDashboard').then(module => ({
    default: module.LearningDashboard
  }))
)

export const LazyMultimodalPanel = lazy(() => 
  import('@/components/MultimodalPanel').then(module => ({
    default: module.MultimodalPanel
  }))
)

export const LazyAgentControlPanel = lazy(() => 
  import('@/components/AgentControlPanel').then(module => ({
    default: module.AgentControlPanel
  }))
)

export const LazySelfOptimizationPanel = lazy(() => 
  import('@/components/SelfOptimizationPanel').then(module => ({
    default: module.SelfOptimizationPanel
  }))
)

// Error boundary component
interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
}

interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ComponentType<{ error?: Error; retry: () => void }>
}

class LazyErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Lazy component error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback
      return (
        <FallbackComponent 
          error={this.state.error} 
          retry={() => this.setState({ hasError: false, error: undefined })}
        />
      )
    }

    return this.props.children
  }
}

const DefaultErrorFallback: React.FC<{ error?: Error; retry: () => void }> = ({ error, retry }) => (
  <Box sx={{ p: 3, textAlign: 'center' }}>
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <h3>Something went wrong</h3>
      <p>Failed to load component. Please try again.</p>
      {error && (
        <details style={{ marginTop: '1rem', textAlign: 'left' }}>
          <summary>Error details</summary>
          <pre>{error.message}</pre>
        </details>
      )}
      <button onClick={retry} style={{ marginTop: '1rem' }}>
        Retry
      </button>
    </motion.div>
  </Box>
)

// Higher-order component for lazy loading with error boundary
export function withLazyLoading<T extends object>(
  Component: ComponentType<T>,
  LoadingComponent: ComponentType = LoadingSpinner,
  ErrorComponent?: ComponentType<{ error?: Error; retry: () => void }>
) {
  return function LazyWrapper(props: T) {
    return (
      <LazyErrorBoundary fallback={ErrorComponent}>
        <Suspense fallback={<LoadingComponent />}>
          <Component {...props} />
        </Suspense>
      </LazyErrorBoundary>
    )
  }
}

// Preload components for better UX
export const preloadComponents = () => {
  // Preload critical components
  import('@/components/MuiEnhancedChatPanel')
  import('@/components/CodeEditor')
  import('@/components/LearningDashboard')
}

// Intersection observer hook for lazy loading
export function useIntersectionObserver(
  ref: React.RefObject<Element>,
  options: IntersectionObserverInit = {}
) {
  const [isIntersecting, setIsIntersecting] = React.useState(false)
  const [hasIntersected, setHasIntersected] = React.useState(false)

  React.useEffect(() => {
    const element = ref.current
    if (!element) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsIntersecting(entry.isIntersecting)
        if (entry.isIntersecting && !hasIntersected) {
          setHasIntersected(true)
        }
      },
      {
        threshold: 0.1,
        rootMargin: '50px',
        ...options
      }
    )

    observer.observe(element)
    return () => observer.unobserve(element)
  }, [ref, hasIntersected, options])

  return { isIntersecting, hasIntersected }
}

// Virtual scrolling hook for large lists
export function useVirtualScrolling<T>(
  items: T[],
  containerHeight: number,
  itemHeight: number
) {
  const [scrollTop, setScrollTop] = React.useState(0)

  const visibleStart = Math.floor(scrollTop / itemHeight)
  const visibleEnd = Math.min(
    visibleStart + Math.ceil(containerHeight / itemHeight) + 1,
    items.length
  )

  const visibleItems = items.slice(visibleStart, visibleEnd).map((item, index) => ({
    item,
    index: visibleStart + index
  }))

  const totalHeight = items.length * itemHeight
  const offsetY = visibleStart * itemHeight

  return {
    visibleItems,
    totalHeight,
    offsetY,
    setScrollTop
  }
}

// Performance monitoring hook
export function usePerformanceMonitor(componentName: string) {
  const renderStart = React.useRef<number>()
  const [metrics, setMetrics] = React.useState({
    renderTime: 0,
    mountTime: 0
  })

  React.useEffect(() => {
    renderStart.current = performance.now()
    
    return () => {
      if (renderStart.current) {
        const renderTime = performance.now() - renderStart.current
        setMetrics(prev => ({ ...prev, renderTime }))
        
        // Log performance metrics in development
        if (process.env.NODE_ENV === 'development') {
          console.log(`${componentName} render time: ${renderTime.toFixed(2)}ms`)
        }
      }
    }
  }, [componentName])

  React.useEffect(() => {
    const mountTime = performance.now()
    setMetrics(prev => ({ ...prev, mountTime }))
  }, [])

  return metrics
}
