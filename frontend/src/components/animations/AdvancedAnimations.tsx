'use client'

import { motion, Variants } from 'framer-motion'

// Advanced animation variants
export const fadeInUp: Variants = {
  initial: { 
    opacity: 0, 
    y: 20,
    scale: 0.95
  },
  animate: { 
    opacity: 1, 
    y: 0,
    scale: 1,
    transition: {
      duration: 0.4,
      ease: [0.4, 0, 0.2, 1],
      staggerChildren: 0.1
    }
  },
  exit: { 
    opacity: 0, 
    y: -20,
    scale: 0.95,
    transition: {
      duration: 0.3,
      ease: [0.4, 0, 0.2, 1]
    }
  }
}

export const slideInFromRight: Variants = {
  initial: { 
    opacity: 0, 
    x: 100,
    scale: 0.9
  },
  animate: { 
    opacity: 1, 
    x: 0,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: [0.4, 0, 0.2, 1]
    }
  },
  exit: { 
    opacity: 0, 
    x: 100,
    scale: 0.9,
    transition: {
      duration: 0.3,
      ease: [0.4, 0, 0.2, 1]
    }
  }
}

export const scaleIn: Variants = {
  initial: { 
    opacity: 0, 
    scale: 0.8,
    rotateY: -15
  },
  animate: { 
    opacity: 1, 
    scale: 1,
    rotateY: 0,
    transition: {
      duration: 0.6,
      ease: [0.4, 0, 0.2, 1],
      staggerChildren: 0.1
    }
  },
  exit: { 
    opacity: 0, 
    scale: 0.8,
    rotateY: 15,
    transition: {
      duration: 0.3,
      ease: [0.4, 0, 0.2, 1]
    }
  }
}

export const bounceIn: Variants = {
  initial: { 
    opacity: 0, 
    scale: 0.3,
    y: -50
  },
  animate: { 
    opacity: 1, 
    scale: 1,
    y: 0,
    transition: {
      duration: 0.8,
      ease: [0.68, -0.55, 0.265, 1.55],
      type: "spring",
      stiffness: 300,
      damping: 20
    }
  },
  exit: { 
    opacity: 0, 
    scale: 0.3,
    y: -50,
    transition: {
      duration: 0.3,
      ease: [0.4, 0, 0.2, 1]
    }
  }
}

export const shimmer: Variants = {
  initial: { 
    backgroundPosition: '-200% 0'
  },
  animate: { 
    backgroundPosition: '200% 0',
    transition: {
      duration: 2,
      ease: 'linear',
      repeat: Infinity,
      repeatType: 'loop'
    }
  }
}

export const pulse: Variants = {
  animate: {
    scale: [1, 1.05, 1],
    opacity: [0.8, 1, 0.8],
    transition: {
      duration: 2,
      ease: 'easeInOut',
      repeat: Infinity,
      repeatType: 'loop'
    }
  }
}

export const wiggle: Variants = {
  animate: {
    rotate: [0, -5, 5, -5, 0],
    transition: {
      duration: 0.5,
      ease: 'easeInOut',
      repeat: Infinity,
      repeatType: 'loop',
      repeatDelay: 2
    }
  }
}

// Micro-interaction components
export const MicroInteractionButton: React.FC<{
  children: React.ReactNode
  onClick?: () => void
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
  className?: string
}> = ({ 
  children, 
  onClick, 
  variant = 'primary', 
  size = 'medium',
  disabled = false,
  className = ''
}) => {
  const getVariantStyles = () => {
    switch (variant) {
      case 'primary':
        return 'bg-blue-500 hover:bg-blue-600 text-white'
      case 'secondary':
        return 'bg-gray-200 hover:bg-gray-300 text-gray-800'
      case 'ghost':
        return 'bg-transparent hover:bg-gray-100 text-gray-600'
      default:
        return 'bg-blue-500 hover:bg-blue-600 text-white'
    }
  }

  const getSizeStyles = () => {
    switch (size) {
      case 'small':
        return 'px-3 py-1.5 text-sm'
      case 'medium':
        return 'px-4 py-2 text-base'
      case 'large':
        return 'px-6 py-3 text-lg'
      default:
        return 'px-4 py-2 text-base'
    }
  }

  return (
    <motion.button
      className={`
        ${getVariantStyles()} 
        ${getSizeStyles()} 
        rounded-lg font-medium 
        transition-colors duration-200 
        disabled:opacity-50 disabled:cursor-not-allowed
        ${className}
      `}
      onClick={onClick}
      disabled={disabled}
      whileHover={{ 
        scale: disabled ? 1 : 1.02,
        transition: { duration: 0.2 }
      }}
      whileTap={{ 
        scale: disabled ? 1 : 0.98,
        transition: { duration: 0.1 }
      }}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.button>
  )
}

export const FloatingActionButton: React.FC<{
  children: React.ReactNode
  onClick?: () => void
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left'
  color?: string
  size?: number
}> = ({ 
  children, 
  onClick, 
  position = 'bottom-right',
  color = '#3b82f6',
  size = 56
}) => {
  const getPositionStyles = () => {
    switch (position) {
      case 'bottom-right':
        return 'bottom-6 right-6'
      case 'bottom-left':
        return 'bottom-6 left-6'
      case 'top-right':
        return 'top-6 right-6'
      case 'top-left':
        return 'top-6 left-6'
      default:
        return 'bottom-6 right-6'
    }
  }

  return (
    <motion.button
      className={`
        fixed ${getPositionStyles()} z-50
        rounded-full shadow-lg
        flex items-center justify-center
        text-white font-medium
        hover:shadow-xl
        transition-shadow duration-300
      `}
      style={{
        backgroundColor: color,
        width: size,
        height: size
      }}
      onClick={onClick}
      whileHover={{ 
        scale: 1.1,
        rotate: 5,
        transition: { duration: 0.2 }
      }}
      whileTap={{ 
        scale: 0.95,
        transition: { duration: 0.1 }
      }}
      initial={{ opacity: 0, scale: 0 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ 
        duration: 0.5,
        ease: [0.68, -0.55, 0.265, 1.55]
      }}
    >
      {children}
    </motion.button>
  )
}

export const AnimatedCard: React.FC<{
  children: React.ReactNode
  className?: string
  hover?: boolean
  delay?: number
}> = ({ children, className = '', hover = true, delay = 0 }) => {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ 
        duration: 0.5, 
        delay,
        ease: [0.4, 0, 0.2, 1]
      }}
      whileHover={hover ? {
        y: -5,
        scale: 1.02,
        transition: { duration: 0.2 }
      } : {}}
    >
      {children}
    </motion.div>
  )
}

export const LoadingSpinner: React.FC<{
  size?: number
  color?: string
  text?: string
}> = ({ size = 40, color = '#3b82f6', text = 'Loading...' }) => {
  return (
    <motion.div
      className="flex flex-col items-center justify-center gap-3"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <motion.div
        className="rounded-full border-4 border-gray-200 border-t-blue-500"
        style={{
          width: size,
          height: size,
          borderTopColor: color
        }}
        animate={{ rotate: 360 }}
        transition={{
          duration: 1,
          ease: 'linear',
          repeat: Infinity
        }}
      />
      {text && (
        <motion.p
          className="text-sm text-gray-600"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          {text}
        </motion.p>
      )}
    </motion.div>
  )
}

export const ProgressBar: React.FC<{
  progress: number
  color?: string
  height?: number
  animated?: boolean
}> = ({ progress, color = '#3b82f6', height = 4, animated = true }) => {
  return (
    <div
      className="w-full bg-gray-200 rounded-full overflow-hidden"
      style={{ height }}
    >
      <motion.div
        className="h-full rounded-full"
        style={{ backgroundColor: color }}
        initial={{ width: 0 }}
        animate={{ width: `${Math.min(progress, 100)}%` }}
        transition={{ 
          duration: animated ? 0.8 : 0.3,
          ease: 'easeOut'
        }}
      />
    </div>
  )
}

// StaggerContainer component
export const StaggerContainer: React.FC<{
  children: React.ReactNode
  className?: string
}> = ({ children, className = '' }) => {
  return (
    <motion.div
      className={className}
      variants={{
        hidden: { opacity: 0 },
        show: {
          opacity: 1,
          transition: {
            staggerChildren: 0.1
          }
        }
      }}
      initial="hidden"
      animate="show"
    >
      {children}
    </motion.div>
  )
}

// FloatingElement component
export const FloatingElement: React.FC<{
  children: React.ReactNode
  className?: string
  intensity?: number
}> = ({ children, className = '', intensity = 1 }) => {
  return (
    <motion.div
      className={className}
      animate={{
        y: [0, -10 * intensity, 0],
        rotate: [0, 2 * intensity, 0]
      }}
      transition={{
        duration: 3,
        ease: 'easeInOut',
        repeat: Infinity,
        repeatType: 'reverse'
      }}
    >
      {children}
    </motion.div>
  )
}

// MagneticCard component
export const MagneticCard: React.FC<{
  children: React.ReactNode
  className?: string
  intensity?: number
}> = ({ children, className = '', intensity = 0.1 }) => {
  return (
    <motion.div
      className={className}
      whileHover={{
        scale: 1.02,
        transition: { duration: 0.2 }
      }}
      whileTap={{
        scale: 0.98,
        transition: { duration: 0.1 }
      }}
      style={{
        cursor: 'pointer'
      }}
    >
      {children}
    </motion.div>
  )
}