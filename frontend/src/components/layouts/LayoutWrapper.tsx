'use client'

import React from 'react'
import { Box } from '@mui/material'
import { motion, AnimatePresence } from 'framer-motion'

interface LayoutWrapperProps {
  activePanel: string
  children: React.ReactNode
}

export function LayoutWrapper({ activePanel, children }: LayoutWrapperProps) {
  return (
    <Box sx={{ height: '100%', overflow: 'hidden' }}>
      <AnimatePresence mode="wait">
        <motion.div
          key={activePanel}
          initial={{ opacity: 0, y: 20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -20, scale: 0.95 }}
          transition={{ 
            duration: 0.4, 
            ease: [0.4, 0, 0.2, 1],
            scale: { duration: 0.3 }
          }}
          style={{ height: '100%' }}
        >
          {children}
        </motion.div>
      </AnimatePresence>
    </Box>
  )
}
