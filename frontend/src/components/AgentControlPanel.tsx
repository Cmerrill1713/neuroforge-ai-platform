"use client"

import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Card,
  CardContent,
  Chip,
  Stack,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Divider,
  Avatar
} from '@mui/material'
import {
  SmartToy as SmartToyIcon,
  Security as SecurityIcon,
  Code as CodeIcon,
  FolderOpen as FolderIcon,
  ExpandMore as ExpandMoreIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon
} from '@mui/icons-material'
import { motion } from 'framer-motion'
import { designSystem, getPanelStyles, getResponsivePadding } from '@/design-system'

interface Agent {
  name: string
  status: {
    isActive: boolean
    capabilities: Array<{
      name: string
      description: string
      examples: string[]
    }>
    activeTasks: number
    completedTasks: number
  }
}

interface AgentResponse {
  agent: string
  prompt: string
  response: {
    taskId: string
    success: boolean
    result?: any
    error?: string
    suggestions?: string[]
    confidence: number
  }
  timestamp: string
}

export function AgentControlPanel() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [selectedAgent, setSelectedAgent] = useState<string>('master')
  const [prompt, setPrompt] = useState<string>('')
  const [context, setContext] = useState<string>('')
  const [isProcessing, setIsProcessing] = useState<boolean>(false)
  const [responses, setResponses] = useState<AgentResponse[]>([])
  const [error, setError] = useState<string>('')

  // Load agents on component mount
  useEffect(() => {
    loadAgents()
  }, [])

  const loadAgents = async () => {
    try {
      const response = await fetch('/api/agents')
      const data = await response.json()
      
      if (data.status === 'success') {
        setAgents(data.data.agents)
      }
    } catch (error) {
      console.error('Failed to load agents:', error)
      setError('Failed to load agents')
    }
  }

  const processPrompt = async () => {
    if (!prompt.trim()) return

    setIsProcessing(true)
    setError('')

    try {
      const response = await fetch('/api/agents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent: selectedAgent,
          prompt: prompt.trim(),
          context: context.trim() ? JSON.parse(context.trim()) : undefined
        })
      })

      const data = await response.json()
      
      if (data.status === 'success') {
        setResponses(prev => [data.data, ...prev])
        setPrompt('') // Clear prompt after successful submission
      } else {
        setError(data.error || 'Failed to process prompt')
      }
    } catch (error) {
      console.error('Failed to process prompt:', error)
      setError('Failed to process prompt')
    } finally {
      setIsProcessing(false)
    }
  }

  const controlAgent = async (action: string) => {
    try {
      const response = await fetch('/api/agents', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent: selectedAgent,
          action
        })
      })

      const data = await response.json()
      
      if (data.status === 'success') {
        loadAgents() // Reload agents to get updated status
      } else {
        setError(data.error || 'Failed to control agent')
      }
    } catch (error) {
      console.error('Failed to control agent:', error)
      setError('Failed to control agent')
    }
  }

  const getAgentIcon = (agentName: string) => {
    switch (agentName.toLowerCase()) {
      case 'tree-watcher':
        return <FolderIcon />
      case 'security':
        return <SecurityIcon />
      case 'quality':
        return <CodeIcon />
      case 'master':
        return <SmartToyIcon />
      default:
        return <SmartToyIcon />
    }
  }

  const getAgentColor = (agentName: string) => {
    switch (agentName.toLowerCase()) {
      case 'tree-watcher':
        return 'primary'
      case 'security':
        return 'error'
      case 'quality':
        return 'success'
      case 'master':
        return 'warning'
      default:
        return 'default'
    }
  }

  const panelStyles = getPanelStyles()
  const responsivePadding = getResponsivePadding()

  return (
    <Box sx={panelStyles.container}>
      {/* Header */}
      <Paper elevation={0} sx={panelStyles.header}>
        <Stack direction="row" spacing={2} alignItems="center">
          <Avatar sx={designSystem.components.avatar}>
            <SmartToyIcon />
          </Avatar>
          <Box>
            <Typography variant="h4" sx={{ color: 'white', fontWeight: 600 }}>
              🤖 Personal AI Agents
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              Deploy intelligent agents for productivity, automation, and personal assistance using natural language.
            </Typography>
          </Box>
        </Stack>
      </Paper>

      {/* Content */}
      <Box sx={panelStyles.content}>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Stack spacing={3}>
        {/* Agent Selection */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Select Agent
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {agents.map((agent) => (
                <Chip
                  key={agent.name}
                  icon={getAgentIcon(agent.name)}
                  label={`${agent.name} ${agent.status.isActive ? '(Active)' : '(Inactive)'}`}
                  color={getAgentColor(agent.name) as any}
                  variant={selectedAgent === agent.name ? 'filled' : 'outlined'}
                  onClick={() => setSelectedAgent(agent.name)}
                  sx={{ mb: 1 }}
                />
              ))}
            </Stack>
          </CardContent>
        </Card>

        {/* Agent Status */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Agent Status
            </Typography>
            {agents.filter(a => a.name === selectedAgent).map((agent) => (
              <Box key={agent.name}>
                <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
                  <Chip
                    icon={agent.status.isActive ? <CheckIcon /> : <ErrorIcon />}
                    label={agent.status.isActive ? 'Active' : 'Inactive'}
                    color={agent.status.isActive ? 'success' : 'error'}
                  />
                  <Typography variant="body2">
                    Active Tasks: {agent.status.activeTasks} | Completed: {agent.status.completedTasks}
                  </Typography>
                </Stack>

                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography>Capabilities</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <List dense>
                      {agent.status.capabilities.map((capability, index) => (
                        <React.Fragment key={index}>
                          <ListItem>
                            <ListItemText
                              primary={capability.name}
                              secondary={capability.description}
                            />
                          </ListItem>
                          <ListItem>
                            <Typography variant="caption" color="text.secondary">
                              Examples: {capability.examples.join(', ')}
                            </Typography>
                          </ListItem>
                          {index < agent.status.capabilities.length - 1 && <Divider />}
                        </React.Fragment>
                      ))}
                    </List>
                  </AccordionDetails>
                </Accordion>
              </Box>
            ))}
          </CardContent>
        </Card>

        {/* Agent Control */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Agent Control
            </Typography>
            <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
              <Button
                variant="contained"
                color="success"
                startIcon={<PlayIcon />}
                onClick={() => controlAgent('activate')}
                size="small"
              >
                Activate
              </Button>
              <Button
                variant="contained"
                color="error"
                startIcon={<StopIcon />}
                onClick={() => controlAgent('deactivate')}
                size="small"
              >
                Deactivate
              </Button>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={loadAgents}
                size="small"
              >
                Refresh
              </Button>
            </Stack>
            <Stack direction="row" spacing={1}>
              <Button
                variant="contained"
                color="primary"
                onClick={() => controlAgent('activate-all')}
                size="small"
              >
                Activate All
              </Button>
              <Button
                variant="outlined"
                color="secondary"
                onClick={() => controlAgent('deactivate-all')}
                size="small"
              >
                Deactivate All
              </Button>
            </Stack>
          </CardContent>
        </Card>

        {/* Prompt Interface */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Natural Language Prompt
            </Typography>
            <Stack spacing={2}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Enter your prompt"
                placeholder="e.g., 'Scan for security vulnerabilities in the codebase' or 'Watch the src directory for changes'"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                disabled={isProcessing}
              />
              <TextField
                fullWidth
                multiline
                rows={2}
                label="Context (Optional JSON)"
                placeholder='{"directories": ["src"], "fileTypes": [".ts", ".tsx"]}'
                value={context}
                onChange={(e) => setContext(e.target.value)}
                disabled={isProcessing}
              />
              <Button
                variant="contained"
                color="primary"
                onClick={processPrompt}
                disabled={isProcessing || !prompt.trim()}
                startIcon={isProcessing ? <CircularProgress size={20} /> : <SmartToyIcon />}
                fullWidth
              >
                {isProcessing ? 'Processing...' : 'Send Prompt'}
              </Button>
            </Stack>
          </CardContent>
        </Card>

        {/* Responses */}
        {responses.length > 0 && (
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Agent Responses
              </Typography>
              <Stack spacing={2}>
                {responses.map((response, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Paper sx={{ p: 2, bgcolor: response.response.success ? 'success.light' : 'error.light' }}>
                      <Stack spacing={1}>
                        <Stack direction="row" spacing={1} alignItems="center">
                          <Chip
                            icon={getAgentIcon(response.agent)}
                            label={response.agent}
                            color={getAgentColor(response.agent) as any}
                            size="small"
                          />
                          <Chip
                            label={response.response.success ? 'Success' : 'Error'}
                            color={response.response.success ? 'success' : 'error'}
                            size="small"
                          />
                          <Chip
                            label={`Confidence: ${Math.round(response.response.confidence * 100)}%`}
                            variant="outlined"
                            size="small"
                          />
                        </Stack>
                        <Typography variant="body2" color="text.secondary">
                          Prompt: {response.prompt}
                        </Typography>
                        <Typography variant="body2">
                          {response.response.success 
                            ? JSON.stringify(response.response.result, null, 2)
                            : response.response.error
                          }
                        </Typography>
                        {response.response.suggestions && response.response.suggestions.length > 0 && (
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              Suggestions:
                            </Typography>
                            <List dense>
                              {response.response.suggestions.map((suggestion, i) => (
                                <ListItem key={i} sx={{ py: 0 }}>
                                  <ListItemText primary={`• ${suggestion}`} />
                                </ListItem>
                              ))}
                            </List>
                          </Box>
                        )}
                        <Typography variant="caption" color="text.secondary">
                          {new Date(response.timestamp).toLocaleString()}
                        </Typography>
                      </Stack>
                    </Paper>
                  </motion.div>
                ))}
              </Stack>
            </CardContent>
          </Card>
        )}
      </Stack>
      </Box>
    </Box>
  )
}
