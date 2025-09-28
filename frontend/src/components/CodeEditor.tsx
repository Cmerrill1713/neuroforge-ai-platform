"use client"

import React, { useState } from 'react'
import { Editor } from '@monaco-editor/react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Stack,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  Divider,
  Grid,
  Avatar,
  CircularProgress,
  Paper
} from '@mui/material'
import { designSystem, getPanelStyles } from '@/design-system'
import {
  PlayArrow as PlayIcon,
  Save as SaveIcon,
  FolderOpen as FolderOpenIcon,
  FileCopy as FileIcon,
  Code as CodeIcon,
  AutoAwesome as AIIcon,
  FormatListBulleted as FormatIcon,
  BugReport as DebugIcon,
  Terminal as TerminalIcon
} from '@mui/icons-material'
import { motion } from 'framer-motion'

export function CodeEditor() {
  const [code, setCode] = useState(`// Welcome to the AI-powered code editor!
// Start building with AI assistance

function greetAI() {
  console.log("Hello from the Personal AI Assistant!");
  return "Ready to learn and build together!";
}

// Example function with AI assistance
function calculateSum(a, b) {
  return a + b;
}

// Test the functions
console.log(greetAI());
console.log("Sum of 5 + 3 =", calculateSum(5, 3));`)
  
  const [language, setLanguage] = useState('javascript')
  const [theme, setTheme] = useState('vs-dark')
  const [isRunning, setIsRunning] = useState(false)
  const [output, setOutput] = useState('')
  const [fileName, setFileName] = useState('main.js')

  const handleRun = async () => {
    setIsRunning(true)
    setOutput('')
    
    try {
      // Real code execution using the backend API
      const response = await fetch('/api/execute-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: code,
          language: language,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setOutput(result.output || result.error || 'Code executed successfully');
    } catch (error) {
      setOutput(`Error: ${error instanceof Error ? error.message : 'Unknown error occurred'}`);
    } finally {
      setIsRunning(false)
    }
  }

  const handleSave = async () => {
    try {
      const response = await fetch('/api/save-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: code,
          fileName: fileName,
          language: language,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to save: ${response.status}`);
      }

      const result = await response.json();
      console.log('Code saved successfully:', result);
    } catch (error) {
      console.error('Save error:', error);
    }
  }

  const handleFormat = async () => {
    try {
      const response = await fetch('/api/format-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: code,
          language: language,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to format: ${response.status}`);
      }

      const result = await response.json();
      setCode(result.formattedCode || code);
    } catch (error) {
      console.error('Format error:', error);
    }
  }

  const languageOptions = [
    { value: 'javascript', label: 'JavaScript' },
    { value: 'typescript', label: 'TypeScript' },
    { value: 'python', label: 'Python' },
    { value: 'html', label: 'HTML' },
    { value: 'css', label: 'CSS' },
    { value: 'json', label: 'JSON' }
  ]

  const aiFeatures = [
    { name: 'Code Completion', description: 'AI-powered suggestions', icon: <AIIcon /> },
    { name: 'Error Detection', description: 'Real-time error checking', icon: <DebugIcon /> },
    { name: 'Code Formatting', description: 'Automatic code formatting', icon: <FormatIcon /> },
    { name: 'Terminal Integration', description: 'Built-in terminal', icon: <TerminalIcon /> }
  ]

  const panelStyles = getPanelStyles()

  return (
    <Box sx={panelStyles.container}>
      {/* Header */}
      <Paper elevation={0} sx={panelStyles.header}>
        <Stack direction="row" spacing={2} alignItems="center">
          <Avatar sx={designSystem.components.avatar}>
            <CodeIcon />
          </Avatar>
          <Box>
            <Typography variant="h4" sx={{ color: 'white', fontWeight: 600 }}>
              💻 Code Assistant
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              AI-assisted coding and development with intelligent suggestions and real-time assistance
            </Typography>
          </Box>
        </Stack>
      </Paper>

      {/* Content */}
      <Box sx={panelStyles.content}>

      {/* Editor Controls */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Language</InputLabel>
                <Select
                  value={language}
                  label="Language"
                  onChange={(e) => setLanguage(e.target.value)}
                >
                  {languageOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              <Chip 
                icon={<FileIcon />}
                label={fileName}
                variant="outlined"
                color="primary"
              />
              
              <Box sx={{ flexGrow: 1 }} />
              
              <Stack direction="row" spacing={1}>
                <Tooltip title="Save file">
                  <IconButton onClick={handleSave} color="primary">
                    <SaveIcon />
                  </IconButton>
                </Tooltip>
                
                <Tooltip title="Format code">
                  <IconButton onClick={handleFormat} color="secondary">
                    <FormatIcon />
                  </IconButton>
                </Tooltip>
                
                <Tooltip title="Open folder">
                  <IconButton color="info">
                    <FolderOpenIcon />
                  </IconButton>
                </Tooltip>
                
                <Button
                  variant="contained"
                  startIcon={isRunning ? <CircularProgress size={16} /> : <PlayIcon />}
                  onClick={handleRun}
                  disabled={isRunning}
                  color="success"
                >
                  {isRunning ? 'Running...' : 'Run'}
                </Button>
              </Stack>
            </Stack>
            
            <Alert severity="info" sx={{ mb: 2 }}>
              <Stack direction="row" alignItems="center" spacing={1}>
                <AIIcon />
                <Typography variant="body2">
                  AI assistance enabled - Get intelligent code suggestions and error detection
                </Typography>
              </Stack>
            </Alert>
          </CardContent>
        </Card>
      </motion.div>

      {/* Code Editor */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Card sx={{ mb: 3 }}>
          <CardContent sx={{ p: 0 }}>
            <Box sx={{ height: 400, position: 'relative' }}>
              <Editor
                height="100%"
                language={language}
                value={code}
                onChange={(value) => setCode(value || '')}
                theme={theme}
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  roundedSelection: false,
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                  suggest: {
                    showKeywords: true,
                    showSnippets: true
                  }
                }}
              />
            </Box>
          </CardContent>
        </Card>
      </motion.div>

      {/* Output Terminal */}
      {output && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
                <TerminalIcon color="primary" />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Output
                </Typography>
              </Stack>
              
              <Box
                sx={{
                  bgcolor: '#1e1e1e',
                  color: '#d4d4d4',
                  p: 2,
                  borderRadius: 1,
                  fontFamily: 'monospace',
                  fontSize: '0.875rem',
                  whiteSpace: 'pre-wrap',
                  minHeight: 100,
                  maxHeight: 200,
                  overflow: 'auto'
                }}
              >
                {output}
              </Box>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* AI Features */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <Card>
          <CardContent>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 3 }}>
              <AIIcon color="primary" />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                AI-Powered Features
              </Typography>
            </Stack>
            
            <Grid container spacing={2}>
              {aiFeatures.map((feature, index) => (
                <div key={index} style={{ width: '100%', padding: '8px' }}>
                  <Card variant="outlined" sx={{ height: '100%' }}>
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Avatar sx={{ bgcolor: 'primary.main', mx: 'auto', mb: 1 }}>
                        {feature.icon}
                      </Avatar>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5 }}>
                        {feature.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {feature.description}
                      </Typography>
                    </CardContent>
                  </Card>
                </div>
              ))}
            </Grid>
          </CardContent>
        </Card>
      </motion.div>
      </Box>
    </Box>
  )
}