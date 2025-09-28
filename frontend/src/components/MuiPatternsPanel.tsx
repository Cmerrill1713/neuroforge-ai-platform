"use client"

import React, { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Stack,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  TextField,
  InputAdornment,
  Badge,
  Divider
} from '@mui/material'
import {
  ExpandMore as ExpandMoreIcon,
  Search as SearchIcon,
  Code as CodeIcon,
  Palette as PaletteIcon,
  TrendingUp as TrendingUpIcon,
  ContentCopy as CopyIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon
} from '@mui/icons-material'
import { motion } from 'framer-motion'
import { useMuiPatterns } from './MuiPatternsProvider'

interface MuiPatternsPanelProps {
  onPatternSelect?: (pattern: any) => void
}

export function MuiPatternsPanel({ onPatternSelect }: MuiPatternsPanelProps) {
  const { patterns, loading, error, getPatternsByType, incrementUsage } = useMuiPatterns()
  const [searchTerm, setSearchTerm] = useState('')
  const [favorites, setFavorites] = useState<string[]>([])
  const [expandedPattern, setExpandedPattern] = useState<string | false>(false)

  const filteredPatterns = patterns.filter(pattern =>
    pattern.pattern_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    pattern.description.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handlePatternClick = (pattern: any) => {
    incrementUsage(pattern.id)
    onPatternSelect?.(pattern)
  }

  const toggleFavorite = (patternId: string) => {
    setFavorites(prev => 
      prev.includes(patternId) 
        ? prev.filter(id => id !== patternId)
        : [...prev, patternId]
    )
  }

  const copyPatternCode = (pattern: any) => {
    const codeExample = `
// ${pattern.description}
// Pattern: ${pattern.pattern_name}

import { ${pattern.pattern_schema?.properties?.component?.type || 'Component'} } from '@mui/material'

const ${pattern.pattern_name.replace(/[^a-zA-Z0-9]/g, '')} = () => {
  return (
    <${pattern.pattern_schema?.properties?.component?.type || 'Component'}>
      {/* Implementation based on pattern schema */}
    </${pattern.pattern_schema?.properties?.component?.type || 'Component'}>
  )
}

export default ${pattern.pattern_name.replace(/[^a-zA-Z0-9]/g, '')}
    `.trim()
    
    navigator.clipboard.writeText(codeExample)
  }

  if (loading) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="text.secondary">Loading MUI patterns...</Typography>
      </Box>
    )
  }

  if (error) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="error">Error loading patterns: {error}</Typography>
      </Box>
    )
  }

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
        <Stack direction="row" alignItems="center" spacing={2} mb={2}>
          <PaletteIcon color="primary" />
          <Typography variant="h6" color="text.primary">
            MUI Patterns Library
          </Typography>
          <Badge badgeContent={patterns.length} color="primary">
            <Chip label="Patterns" size="small" color="primary" />
          </Badge>
        </Stack>

        <TextField
          fullWidth
          size="small"
          placeholder="Search patterns..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon color="action" />
              </InputAdornment>
            ),
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              bgcolor: 'rgba(255,255,255,0.05)',
              '& fieldset': { borderColor: 'rgba(255,255,255,0.2)' },
            },
          }}
        />
      </Box>

      {/* Patterns List */}
      <Box sx={{ flexGrow: 1, overflowY: 'auto', p: 1 }}>
        {filteredPatterns.length === 0 ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography color="text.secondary">
              {searchTerm ? 'No patterns found matching your search.' : 'No patterns available.'}
            </Typography>
          </Box>
        ) : (
          <Stack spacing={1}>
            {filteredPatterns.map((pattern, index) => (
              <motion.div
                key={pattern.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Accordion
                  expanded={expandedPattern === pattern.id}
                  onChange={(_, isExpanded) => setExpandedPattern(isExpanded ? pattern.id : false)}
                  sx={{
                    bgcolor: 'rgba(255,255,255,0.05)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    '&:before': { display: 'none' },
                    '&.Mui-expanded': {
                      bgcolor: 'rgba(255,255,255,0.08)',
                    },
                  }}
                >
                  <AccordionSummary
                    expandIcon={<ExpandMoreIcon sx={{ color: 'text.secondary' }} />}
                    sx={{
                      '& .MuiAccordionSummary-content': {
                        alignItems: 'center',
                      },
                    }}
                  >
                    <Stack direction="row" alignItems="center" spacing={2} sx={{ width: '100%' }}>
                      <CodeIcon color="primary" fontSize="small" />
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="subtitle2" color="text.primary">
                          {pattern.pattern_name.replace('mui_', '').replace('_pattern', '')}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {pattern.description}
                        </Typography>
                      </Box>
                      <Stack direction="row" spacing={1}>
                        <Chip
                          label={`${pattern.usage_count} uses`}
                          size="small"
                          color="secondary"
                          icon={<TrendingUpIcon />}
                        />
                        <Tooltip title={favorites.includes(pattern.id) ? "Remove from favorites" : "Add to favorites"}>
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation()
                              toggleFavorite(pattern.id)
                            }}
                          >
                            {favorites.includes(pattern.id) ? (
                              <StarIcon color="warning" fontSize="small" />
                            ) : (
                              <StarBorderIcon color="action" fontSize="small" />
                            )}
                          </IconButton>
                        </Tooltip>
                      </Stack>
                    </Stack>
                  </AccordionSummary>
                  
                  <AccordionDetails>
                    <Stack spacing={2}>
                      <Box>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Pattern Schema:
                        </Typography>
                        <Box
                          component="pre"
                          sx={{
                            bgcolor: 'rgba(255,255,255,0.05)',
                            p: 2,
                            borderRadius: 1,
                            fontSize: '0.75rem',
                            overflow: 'auto',
                            color: 'text.secondary',
                          }}
                        >
                          {JSON.stringify(pattern.pattern_schema, null, 2)}
                        </Box>
                      </Box>

                      <Divider />

                      <Stack direction="row" spacing={1} justifyContent="flex-end">
                        <Tooltip title="Copy code example">
                          <IconButton
                            size="small"
                            onClick={() => copyPatternCode(pattern)}
                            sx={{ color: 'text.secondary' }}
                          >
                            <CopyIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Use this pattern">
                          <IconButton
                            size="small"
                            onClick={() => handlePatternClick(pattern)}
                            color="primary"
                          >
                            <PaletteIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Stack>
                    </Stack>
                  </AccordionDetails>
                </Accordion>
              </motion.div>
            ))}
          </Stack>
        )}
      </Box>
    </Box>
  )
}
