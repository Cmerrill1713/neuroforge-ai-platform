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
  
  IconButton,
  Tooltip
} from '@mui/material'
import {
  Computer as ComputerIcon,
  Terminal as TerminalIcon,
  Folder as FolderIcon,
  Settings as SettingsIcon,
  ExpandMore as ExpandMoreIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Code as CodeIcon,
  NetworkCheck as NetworkIcon,
  Memory as MemoryIcon
} from '@mui/icons-material'
import { motion } from 'framer-motion'

interface SystemCapability {
  name: string
  description: string
  commands: string[]
  examples: string[]
  category: string
}

interface SystemInfo {
  current_directory: string
  disk_usage?: any
  permissions?: any
}

interface SystemOperation {
  id: string
  operation: string
  command?: string
  parameters: any
  result?: any
  status: string
  timestamp: string
  error?: string
}

export function SystemControlPanel() {
  const [capabilities, setCapabilities] = useState<SystemCapability[]>([])
  const [systemInfo, setSystemInfo] = useState<SystemInfo>({ current_directory: '' })
  const [command, setCommand] = useState<string>('')
  const [isExecuting, setIsExecuting] = useState<boolean>(false)
  const [operations, setOperations] = useState<SystemOperation[]>([])
  const [error, setError] = useState<string>('')
  const [systemAware, setSystemAware] = useState<boolean>(false)

  // Load system information on component mount
  useEffect(() => {
    loadSystemInfo()
  }, [])

  const loadSystemInfo = async () => {
    try {
      const response = await fetch('/api/system')
      const data = await response.json()
      
      if (data.status === 'success') {
        setSystemInfo(data.data.systemInfo)
        setCapabilities(data.data.capabilities)
        setSystemAware(data.data.systemAware)
      }
    } catch (error) {
      console.error('Failed to load system info:', error)
      setError('Failed to load system information')
    }
  }

  const executeCommand = async () => {
    if (!command.trim()) return

    setIsExecuting(true)
    setError('')

    try {
      const response = await fetch('/api/system', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          command: command.trim()
        })
      })

      const data = await response.json()
      
      if (data.status === 'success') {
        setOperations(prev => [data.data.result, ...prev])
        setCommand('') // Clear command after successful execution
      } else {
        setError(data.error || 'Failed to execute command')
      }
    } catch (error) {
      console.error('Failed to execute command:', error)
      setError('Failed to execute command')
    } finally {
      setIsExecuting(false)
    }
  }

  const getCapabilityIcon = (category: string) => {
    switch (category) {
      case 'file_system':
        return <FolderIcon />
      case 'process_management':
        return <SettingsIcon />
      case 'development':
        return <CodeIcon />
      case 'network':
        return <NetworkIcon />
      case 'monitoring':
        return <MemoryIcon />
      default:
        return <TerminalIcon />
    }
  }

  const getCapabilityColor = (category: string) => {
    switch (category) {
      case 'file_system':
        return 'primary'
      case 'process_management':
        return 'warning'
      case 'development':
        return 'success'
      case 'network':
        return 'info'
      case 'monitoring':
        return 'error'
      default:
        return 'default'
    }
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ 
        background: 'linear-gradient(135deg, #1976d2 0%, #9c27b0 100%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        fontWeight: 700
      }}>
        🖥️ System Control Panel
      </Typography>

      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Direct system access and control through CLI commands and file operations
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Stack spacing={3}>
        {/* System Status */}
        <Card>
          <CardContent>
            <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
              <Chip
                icon={systemAware ? <CheckIcon /> : <ErrorIcon />}
                label={systemAware ? 'System Aware' : 'Not System Aware'}
                color={systemAware ? 'success' : 'error'}
              />
              <IconButton onClick={loadSystemInfo} >
                <RefreshIcon />
              </IconButton>
            </Stack>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="col-span-1">
                <Typography variant="subtitle2" color="text.secondary">
                  Current Directory
                </Typography>
                <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                  {systemInfo.current_directory}
                </Typography>
              </div>
              <div className="col-span-1">
                <Typography variant="subtitle2" color="text.secondary">
                  Capabilities Available
                </Typography>
                <Typography variant="body2">
                  {capabilities.length} categories
                </Typography>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Command Execution */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Execute System Command
            </Typography>
            <Stack spacing={2}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label="Enter system command"
                placeholder="ls -la, mkdir new_folder, npm install package, git status, etc."
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                disabled={isExecuting}
                sx={{ fontFamily: 'monospace' }}
              />
              <Button
                variant="contained"
                color="primary"
                onClick={executeCommand}
                disabled={isExecuting || !command.trim()}
                startIcon={isExecuting ? <CircularProgress size={20} /> : <TerminalIcon />}
                fullWidth
              >
                {isExecuting ? 'Executing...' : 'Execute Command'}
              </Button>
            </Stack>
          </CardContent>
        </Card>

        {/* System Capabilities */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              System Capabilities
            </Typography>
            <Stack spacing={1}>
              {capabilities.map((capability, index) => (
                <Accordion key={index}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Chip
                        icon={getCapabilityIcon(capability.category)}
                        label={capability.name}
                        color={getCapabilityColor(capability.category) as any}
                        
                      />
                      <Typography variant="body2" color="text.secondary">
                        {capability.description}
                      </Typography>
                    </Stack>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Stack spacing={2}>
                      <Box>
                        <Typography variant="subtitle2" gutterBottom>
                          Available Commands:
                        </Typography>
                        <Stack direction="row" spacing={1} flexWrap="wrap">
                          {capability.commands.map((cmd, i) => (
                            <Chip
                              key={i}
                              label={cmd}
                              
                              variant="outlined"
                              sx={{ fontFamily: 'monospace' }}
                            />
                          ))}
                        </Stack>
                      </Box>
                      <Box>
                        <Typography variant="subtitle2" gutterBottom>
                          Examples:
                        </Typography>
                        <List dense>
                          {capability.examples.map((example, i) => (
                            <ListItem key={i} sx={{ py: 0 }}>
                              <ListItemText primary={`• ${example}`} />
                            </ListItem>
                          ))}
                        </List>
                      </Box>
                    </Stack>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Stack>
          </CardContent>
        </Card>

        {/* Operation Results */}
        {operations.length > 0 && (
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Command Results
              </Typography>
              <Stack spacing={2}>
                {operations.map((operation, index) => (
                  <motion.div
                    key={operation.id || index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Paper sx={{ p: 2, bgcolor: operation.status === 'completed' ? 'success.light' : 'error.light' }}>
                      <Stack spacing={1}>
                        <Stack direction="row" spacing={1} alignItems="center">
                          <Chip
                            label={operation.operation}
                            color={operation.status === 'completed' ? 'success' : 'error'}
                            
                          />
                          {operation.command && (
                            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                              {operation.command}
                            </Typography>
                          )}
                        </Stack>
                        {operation.result && (
                          <Box>
                            <Typography variant="subtitle2">
                              Output:
                            </Typography>
                            <Paper sx={{ p: 1, bgcolor: 'background.paper', fontFamily: 'monospace', fontSize: '0.875rem' }}>
                              <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                                {operation.result.stdout || operation.result.stderr || JSON.stringify(operation.result, null, 2)}
                              </pre>
                            </Paper>
                          </Box>
                        )}
                        {operation.error && (
                          <Alert severity="error" >
                            {operation.error}
                          </Alert>
                        )}
                        <Typography variant="caption" color="text.secondary">
                          {new Date(operation.timestamp).toLocaleString()}
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
  )
}
