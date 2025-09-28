'use client'

import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Chip,
  LinearProgress,
  Tabs,
  Tab,
  Card,
  CardContent,
  CardHeader,
  Alert,
  Stack,
  
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material'
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  AccessTime as TimeIcon,
  Code as CodeIcon,
  Science as TestIcon,
  TrendingUp as TrendingUpIcon,
  Security as SecurityIcon,
  Memory as MemoryIcon
} from '@mui/icons-material'

interface OptimizationTask {
  id: string
  description: string
  requirements: string[]
  constraints: string[]
  successCriteria: string[]
  status: 'pending' | 'generating' | 'testing' | 'optimizing' | 'completed' | 'failed'
  iterations: OptimizationIteration[]
  currentIteration: number
  maxIterations: number
  createdAt: string
  updatedAt: string
}

interface OptimizationIteration {
  id: string
  iterationNumber: number
  code: string
  tests: TestCase[]
  results: TestResult[]
  performance: PerformanceMetrics
  feedback: string
  improvements: string[]
  timestamp: string
}

interface TestCase {
  id: string
  description: string
  input: any
  expectedOutput: any
  type: 'unit' | 'integration' | 'performance' | 'security'
}

interface TestResult {
  testId: string
  passed: boolean
  actualOutput: any
  error?: string
  executionTime: number
  memoryUsage: number
}

interface PerformanceMetrics {
  executionTime: number
  memoryUsage: number
  cpuUsage: number
  codeQuality: number
  testCoverage: number
  securityScore: number
}

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`optimization-tabpanel-${index}`}
      aria-labelledby={`optimization-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

export function SelfOptimizationPanel() {
  const [tasks, setTasks] = useState<OptimizationTask[]>([])
  const [activeTasks, setActiveTasks] = useState<OptimizationTask[]>([])
  const [selectedTask, setSelectedTask] = useState<OptimizationTask | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [tabValue, setTabValue] = useState(0)

  // New task form
  const [newTask, setNewTask] = useState({
    description: '',
    requirements: [''],
    constraints: [''],
    successCriteria: [''],
    maxIterations: 10
  })

  useEffect(() => {
    loadTasks()
    loadActiveTasks()
    
    // Poll for updates every 5 seconds
    const interval = setInterval(() => {
      loadActiveTasks()
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const loadTasks = async () => {
    try {
      const response = await fetch('/api/self-optimization?type=tasks')
      const data = await response.json()
      if (data.status === 'success') {
        setTasks(data.data.tasks)
      }
    } catch (err) {
      console.error('Failed to load tasks:', err)
    }
  }

  const loadActiveTasks = async () => {
    try {
      const response = await fetch('/api/self-optimization?type=active')
      const data = await response.json()
      if (data.status === 'success') {
        setActiveTasks(data.data.tasks)
      }
    } catch (err) {
      console.error('Failed to load active tasks:', err)
    }
  }

  const createTask = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/self-optimization', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'create_task',
          description: newTask.description,
          requirements: newTask.requirements.filter(req => req.trim()),
          constraints: newTask.constraints.filter(constraint => constraint.trim()),
          successCriteria: newTask.successCriteria.filter(criteria => criteria.trim()),
          maxIterations: newTask.maxIterations
        })
      })

      const data = await response.json()
      if (data.status === 'success') {
        setNewTask({
          description: '',
          requirements: [''],
          constraints: [''],
          successCriteria: [''],
          maxIterations: 10
        })
        loadTasks()
      } else {
        setError(data.error || 'Failed to create task')
      }
    } catch (err) {
      setError('Failed to create task')
    } finally {
      setIsLoading(false)
    }
  }

  const executeTask = async (taskId: string) => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/self-optimization', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'execute_task',
          taskId
        })
      })

      const data = await response.json()
      if (data.status === 'success') {
        setSelectedTask(data.data.task)
        loadTasks()
        loadActiveTasks()
      } else {
        setError(data.error || 'Failed to execute task')
      }
    } catch (err) {
      setError('Failed to execute task')
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircleIcon color="success" />
      case 'failed': return <CancelIcon color="error" />
      case 'generating': case 'testing': case 'optimizing': return <RefreshIcon color="primary" className="animate-spin" />
      default: return <TimeIcon color="action" />
    }
  }

  const getStatusColor = (status: string): 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' => {
    switch (status) {
      case 'completed': return 'success'
      case 'failed': return 'error'
      case 'generating': case 'testing': case 'optimizing': return 'primary'
      default: return 'default'
    }
  }

  const addRequirement = () => {
    setNewTask(prev => ({
      ...prev,
      requirements: [...prev.requirements, '']
    }))
  }

  const updateRequirement = (index: number, value: string) => {
    setNewTask(prev => ({
      ...prev,
      requirements: prev.requirements.map((req, i) => i === index ? value : req)
    }))
  }

  const removeRequirement = (index: number) => {
    setNewTask(prev => ({
      ...prev,
      requirements: prev.requirements.filter((_, i) => i !== index)
    }))
  }

  return (
    <Box sx={{ p: { xs: 2, sm: 3, md: 4 }, height: '100%', overflow: 'auto' }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Self-Optimization System
        </Typography>
        <Typography variant="body1" color="text.secondary">
          AI-driven code generation with iterative improvement and sandboxed testing
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Overview" />
          <Tab label="Create Task" />
          <Tab label="All Tasks" />
          <Tab label="Active Tasks" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="col-span-1">
            <Card>
              <CardContent>
                <Stack direction="row" alignItems="center" spacing={2}>
                  <MemoryIcon color="primary" />
                  <Box>
                    <Typography variant="h6">Total Tasks</Typography>
                    <Typography variant="h4">{tasks.length}</Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </div>

          <div className="col-span-1">
            <Card>
              <CardContent>
                <Stack direction="row" alignItems="center" spacing={2}>
                  <RefreshIcon color="primary" />
                  <Box>
                    <Typography variant="h6">Active Tasks</Typography>
                    <Typography variant="h4">{activeTasks.length}</Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </div>

          <div className="col-span-1">
            <Card>
              <CardContent>
                <Stack direction="row" alignItems="center" spacing={2}>
                  <CheckCircleIcon color="success" />
                  <Box>
                    <Typography variant="h6">Completed</Typography>
                    <Typography variant="h4">
                      {tasks.filter(t => t.status === 'completed').length}
                    </Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </div>
        </div>

        {activeTasks.length > 0 && (
          <Card sx={{ mt: 3 }}>
            <CardHeader title="Active Optimization Tasks" />
            <CardContent>
              <List>
                {activeTasks.map((task) => (
                  <React.Fragment key={task.id}>
                    <ListItem>
                      <ListItemIcon>
                        {getStatusIcon(task.status)}
                      </ListItemIcon>
                      <ListItemText
                        primary={task.description}
                        secondary={`Iteration ${task.currentIteration}/${task.maxIterations}`}
                      />
                      <Chip
                        label={task.status}
                        color={getStatusColor(task.status)}
                        size="small"
                      />
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        )}
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Card>
          <CardHeader title="Create Optimization Task" />
          <CardContent>
            <Stack spacing={3}>
              <TextField
                label="Description"
                multiline
                rows={3}
                placeholder="Describe what you want the AI to optimize..."
                value={newTask.description}
                onChange={(e) => setNewTask(prev => ({ ...prev, description: e.target.value }))}
                fullWidth
              />

              <Box>
                <Typography variant="h6" gutterBottom>Requirements</Typography>
                {newTask.requirements.map((req, index) => (
                  <Stack key={index} direction="row" spacing={1} sx={{ mb: 1 }}>
                    <TextField
                      placeholder="Enter requirement..."
                      value={req}
                      onChange={(e) => updateRequirement(index, e.target.value)}
                      fullWidth
                    />
                    <IconButton onClick={() => removeRequirement(index)}>
                      <CancelIcon />
                    </IconButton>
                  </Stack>
                ))}
                <Button variant="outlined" onClick={addRequirement}>
                  Add Requirement
                </Button>
              </Box>

              <TextField
                label="Max Iterations"
                type="number"
                value={newTask.maxIterations}
                onChange={(e) => setNewTask(prev => ({ 
                  ...prev, 
                  maxIterations: parseInt(e.target.value) || 10 
                }))}
                inputProps={{ min: 1, max: 50 }}
              />

              <Button
                variant="contained"
                onClick={createTask}
                disabled={isLoading || !newTask.description.trim()}
                fullWidth
              >
                {isLoading ? 'Creating...' : 'Create Task'}
              </Button>
            </Stack>
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Stack spacing={2}>
          {tasks.map((task) => (
            <Card key={task.id}>
              <CardContent>
                <Stack direction="row" alignItems="center" justifyContent="space-between">
                  <Stack direction="row" alignItems="center" spacing={2}>
                    {getStatusIcon(task.status)}
                    <Box>
                      <Typography variant="h6">{task.description}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Iterations: {task.currentIteration}/{task.maxIterations}
                      </Typography>
                    </Box>
                  </Stack>
                  <Stack direction="row" alignItems="center" spacing={2}>
                    <Chip
                      label={task.status}
                      color={getStatusColor(task.status)}
                    />
                    {task.status === 'pending' && (
                      <Button
                        variant="contained"
                        startIcon={<PlayIcon />}
                        onClick={() => executeTask(task.id)}
                        disabled={isLoading}
                      >
                        Execute
                      </Button>
                    )}
                  </Stack>
                </Stack>
              </CardContent>
            </Card>
          ))}
        </Stack>
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        <Stack spacing={2}>
          {activeTasks.map((task) => (
            <Card key={task.id}>
              <CardContent>
                <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
                  <Stack direction="row" alignItems="center" spacing={2}>
                    <RefreshIcon color="primary" className="animate-spin" />
                    <Typography variant="h6">{task.description}</Typography>
                  </Stack>
                  <Chip
                    label={task.status}
                    color={getStatusColor(task.status)}
                  />
                </Stack>

                <Box sx={{ mb: 2 }}>
                  <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 1 }}>
                    <Typography variant="body2">Progress</Typography>
                    <Typography variant="body2">
                      {task.currentIteration}/{task.maxIterations}
                    </Typography>
                  </Stack>
                  <LinearProgress 
                    variant="determinate" 
                    value={(task.currentIteration / task.maxIterations) * 100} 
                  />
                </Box>

                {task.iterations.length > 0 && (
                  <Box>
                    <Typography variant="h6" gutterBottom>Latest Iteration Metrics</Typography>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      <div className="col-span-1">
                        <Stack alignItems="center">
                          <CodeIcon color="primary" />
                          <Typography variant="body2">Quality</Typography>
                          <Typography variant="h6">
                            {task.iterations[task.iterations.length - 1].performance.codeQuality}%
                          </Typography>
                        </Stack>
                      </div>
                      <div className="col-span-1">
                        <Stack alignItems="center">
                          <TestIcon color="primary" />
                          <Typography variant="body2">Tests</Typography>
                          <Typography variant="h6">
                            {task.iterations[task.iterations.length - 1].performance.testCoverage.toFixed(1)}%
                          </Typography>
                        </Stack>
                      </div>
                      <div className="col-span-1">
                        <Stack alignItems="center">
                          <TrendingUpIcon color="primary" />
                          <Typography variant="body2">Performance</Typography>
                          <Typography variant="h6">
                            {task.iterations[task.iterations.length - 1].performance.executionTime}ms
                          </Typography>
                        </Stack>
                      </div>
                      <div className="col-span-1">
                        <Stack alignItems="center">
                          <SecurityIcon color="primary" />
                          <Typography variant="body2">Security</Typography>
                          <Typography variant="h6">
                            {task.iterations[task.iterations.length - 1].performance.securityScore}%
                          </Typography>
                        </Stack>
                      </div>
                    </div>
                  </Box>
                )}
              </CardContent>
            </Card>
          ))}
        </Stack>
      </TabPanel>
    </Box>
  )
}
