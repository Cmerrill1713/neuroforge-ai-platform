import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  Grid,
  Button,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Switch,
  FormControlLabel,
  Divider,
  CircularProgress,
  Alert,
  AlertTitle,
} from '@mui/material';
import {
  AutoAwesome as AutoAwesomeIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Code as CodeIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Storage as StorageIcon,
  Timeline as TimelineIcon,
  BugReport as BugReportIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';

interface OptimizationTask {
  id: string;
  name: string;
  type: 'performance' | 'security' | 'code_quality' | 'resource_usage';
  status: 'pending' | 'running' | 'completed' | 'failed';
  priority: 'low' | 'medium' | 'high' | 'critical';
  progress: number;
  description: string;
  estimatedTime: string;
  startTime?: Date;
  endTime?: Date;
  results?: {
    improvements: string[];
    issues: string[];
    metrics: Record<string, number>;
  };
}

interface OptimizationMetrics {
  performance: {
    score: number;
    improvements: number;
    issues: number;
  };
  security: {
    score: number;
    vulnerabilities: number;
    fixes: number;
  };
  codeQuality: {
    score: number;
    complexity: number;
    maintainability: number;
  };
  resourceUsage: {
    cpu: number;
    memory: number;
    storage: number;
  };
}

const SelfOptimizationPanel: React.FC = () => {
  const [tasks, setTasks] = useState<OptimizationTask[]>([
    {
      id: '1',
      name: 'Code Performance Analysis',
      type: 'performance',
      status: 'completed',
      priority: 'high',
      progress: 100,
      description: 'Analyze and optimize code performance bottlenecks',
      estimatedTime: '5 min',
      startTime: new Date(Date.now() - 300000),
      endTime: new Date(Date.now() - 240000),
      results: {
        improvements: ['Reduced response time by 40%', 'Optimized database queries', 'Improved caching strategy'],
        issues: ['Memory leak in component A', 'Inefficient loop in function B'],
        metrics: { responseTime: -40, memoryUsage: -15, cpuUsage: -25 }
      }
    },
    {
      id: '2',
      name: 'Security Vulnerability Scan',
      type: 'security',
      status: 'running',
      priority: 'critical',
      progress: 65,
      description: 'Scan for security vulnerabilities and potential threats',
      estimatedTime: '10 min',
      startTime: new Date(Date.now() - 180000),
      results: {
        improvements: ['Fixed XSS vulnerability', 'Updated authentication tokens'],
        issues: ['SQL injection risk in API endpoint', 'Weak password policy'],
        metrics: { vulnerabilities: -3, securityScore: 85 }
      }
    },
    {
      id: '3',
      name: 'Resource Usage Optimization',
      type: 'resource_usage',
      status: 'pending',
      priority: 'medium',
      progress: 0,
      description: 'Optimize memory and CPU usage across the system',
      estimatedTime: '15 min'
    },
    {
      id: '4',
      name: 'Code Quality Assessment',
      type: 'code_quality',
      status: 'pending',
      priority: 'low',
      progress: 0,
      description: 'Assess and improve code maintainability and complexity',
      estimatedTime: '8 min'
    }
  ]);

  const [metrics, setMetrics] = useState<OptimizationMetrics>({
    performance: { score: 87, improvements: 12, issues: 3 },
    security: { score: 92, vulnerabilities: 2, fixes: 8 },
    codeQuality: { score: 78, complexity: 6.2, maintainability: 8.1 },
    resourceUsage: { cpu: 45, memory: 62, storage: 78 }
  });

  const [isOptimizing, setIsOptimizing] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<OptimizationTask | null>(null);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#4caf50';
      case 'running': return '#ff9800';
      case 'pending': return '#9e9e9e';
      case 'failed': return '#f44336';
      default: return '#9e9e9e';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircleIcon />;
      case 'running': return <CircularProgress size={16} />;
      case 'pending': return <PlayIcon />;
      case 'failed': return <ErrorIcon />;
      default: return <PlayIcon />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return '#f44336';
      case 'high': return '#ff9800';
      case 'medium': return '#2196f3';
      case 'low': return '#4caf50';
      default: return '#9e9e9e';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'performance': return <SpeedIcon />;
      case 'security': return <SecurityIcon />;
      case 'code_quality': return <CodeIcon />;
      case 'resource_usage': return <MemoryIcon />;
      default: return <AutoAwesomeIcon />;
    }
  };

  const handleStartOptimization = () => {
    setIsOptimizing(true);
    // Simulate optimization process
    setTimeout(() => {
      setIsOptimizing(false);
      // Update tasks with simulated results
      setTasks(prev => prev.map(task => {
        if (task.status === 'running') {
          return {
            ...task,
            status: 'completed' as const,
            progress: 100,
            endTime: new Date(),
            results: {
              improvements: ['Optimization completed successfully'],
              issues: [],
              metrics: { score: Math.floor(Math.random() * 20) + 80 }
            }
          };
        }
        return task;
      }));
    }, 5000);
  };

  const handleTaskClick = (task: OptimizationTask) => {
    setSelectedTask(task);
    setDialogOpen(true);
  };

  const handleStartTask = (taskId: string) => {
    setTasks(prev => prev.map(task => {
      if (task.id === taskId && task.status === 'pending') {
        return {
          ...task,
          status: 'running' as const,
          startTime: new Date(),
          progress: 0
        };
      }
      return task;
    }));

    // Simulate task progress
    const interval = setInterval(() => {
      setTasks(prev => prev.map(task => {
        if (task.id === taskId && task.status === 'running') {
          const newProgress = Math.min(task.progress + Math.random() * 20, 100);
          if (newProgress >= 100) {
            clearInterval(interval);
            return {
              ...task,
              status: 'completed' as const,
              progress: 100,
              endTime: new Date(),
              results: {
                improvements: ['Task completed successfully'],
                issues: [],
                metrics: { score: Math.floor(Math.random() * 20) + 80 }
              }
            };
          }
          return { ...task, progress: newProgress };
        }
        return task;
      }));
    }, 1000);
  };

  return (
    <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" sx={{ color: 'white', fontWeight: 700 }}>
          Self-Optimization Engine
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh Status">
            <IconButton onClick={() => window.location.reload()} sx={{ color: 'white' }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={isOptimizing ? <CircularProgress size={16} color="inherit" /> : <AutoAwesomeIcon />}
            onClick={handleStartOptimization}
            disabled={isOptimizing}
            sx={{
              background: 'linear-gradient(135deg, #ff9800 0%, #f57c00 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #f57c00 0%, #ff9800 100%)',
              },
            }}
          >
            {isOptimizing ? 'Optimizing...' : 'Start Full Optimization'}
          </Button>
        </Box>
      </Box>

      {/* Optimization Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{
            background: 'rgba(10, 10, 10, 0.8)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: 3,
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <SpeedIcon sx={{ color: '#4caf50' }} />
                <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                  Performance
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ color: 'white', fontWeight: 700, mb: 1 }}>
                {metrics.performance.score}%
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                {metrics.performance.improvements} improvements, {metrics.performance.issues} issues
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{
            background: 'rgba(10, 10, 10, 0.8)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: 3,
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <SecurityIcon sx={{ color: '#f44336' }} />
                <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                  Security
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ color: 'white', fontWeight: 700, mb: 1 }}>
                {metrics.security.score}%
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                {metrics.security.vulnerabilities} vulnerabilities, {metrics.security.fixes} fixes
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{
            background: 'rgba(10, 10, 10, 0.8)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: 3,
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <CodeIcon sx={{ color: '#2196f3' }} />
                <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                  Code Quality
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ color: 'white', fontWeight: 700, mb: 1 }}>
                {metrics.codeQuality.score}%
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                Complexity: {metrics.codeQuality.complexity}, Maintainability: {metrics.codeQuality.maintainability}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{
            background: 'rgba(10, 10, 10, 0.8)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: 3,
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <MemoryIcon sx={{ color: '#ff9800' }} />
                <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                  Resources
                </Typography>
              </Box>
              <Typography variant="h3" sx={{ color: 'white', fontWeight: 700, mb: 1 }}>
                {Math.round((metrics.resourceUsage.cpu + metrics.resourceUsage.memory) / 2)}%
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                CPU: {metrics.resourceUsage.cpu}%, Memory: {metrics.resourceUsage.memory}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Optimization Tasks */}
      <Paper sx={{
        background: 'rgba(10, 10, 10, 0.8)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: 3,
        overflow: 'hidden',
      }}>
        <Box sx={{ p: 3, borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <Typography variant="h5" sx={{ color: 'white', fontWeight: 600 }}>
            Optimization Tasks
          </Typography>
        </Box>
        <List sx={{ p: 0 }}>
          {tasks.map((task, index) => (
            <React.Fragment key={task.id}>
              <ListItem
                sx={{
                  cursor: 'pointer',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  },
                }}
                onClick={() => handleTaskClick(task)}
              >
                <ListItemIcon>
                  {getTypeIcon(task.type)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <Typography variant="body1" sx={{ color: 'white', fontWeight: 600 }}>
                        {task.name}
                      </Typography>
                      <Chip
                        icon={getStatusIcon(task.status)}
                        label={task.status.toUpperCase()}
                        size="small"
                        sx={{
                          backgroundColor: getStatusColor(task.status),
                          color: 'white',
                          fontWeight: 600,
                        }}
                      />
                      <Chip
                        label={task.priority.toUpperCase()}
                        size="small"
                        sx={{
                          backgroundColor: getPriorityColor(task.priority),
                          color: 'white',
                          fontWeight: 600,
                        }}
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                        {task.description}
                      </Typography>
                      {task.status === 'running' && (
                        <LinearProgress
                          variant="determinate"
                          value={task.progress}
                          sx={{
                            height: 6,
                            borderRadius: 3,
                            backgroundColor: 'rgba(255, 255, 255, 0.1)',
                            '& .MuiLinearProgress-bar': {
                              backgroundColor: getStatusColor(task.status),
                            },
                          }}
                        />
                      )}
                      <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)', display: 'block', mt: 1 }}>
                        Estimated time: {task.estimatedTime}
                        {task.startTime && ` • Started: ${typeof window !== 'undefined' ? task.startTime.toLocaleTimeString() : 'Loading...'}`}
                      </Typography>
                    </Box>
                  }
                />
                <ListItemSecondaryAction>
                  {task.status === 'pending' && (
                    <IconButton
                      onClick={(e) => {
                        e.stopPropagation();
                        handleStartTask(task.id);
                      }}
                      sx={{ color: '#4caf50' }}
                    >
                      <PlayIcon />
                    </IconButton>
                  )}
                  {task.status === 'running' && (
                    <IconButton
                      onClick={(e) => {
                        e.stopPropagation();
                        // Handle stop task
                      }}
                      sx={{ color: '#f44336' }}
                    >
                      <StopIcon />
                    </IconButton>
                  )}
                </ListItemSecondaryAction>
              </ListItem>
              {index < tasks.length - 1 && <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.1)' }} />}
            </React.Fragment>
          ))}
        </List>
      </Paper>

      {/* Task Details Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            backgroundColor: 'rgba(10, 10, 10, 0.95)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          },
        }}
      >
        <DialogTitle sx={{ color: 'white', borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
          {selectedTask?.name}
        </DialogTitle>
        <DialogContent sx={{ pt: 3 }}>
          {selectedTask && (
            <Box>
              <Typography variant="body1" sx={{ color: 'white', mb: 2 }}>
                {selectedTask.description}
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="h6" sx={{ color: 'white', mb: 1 }}>
                  Status: {selectedTask.status.toUpperCase()}
                </Typography>
                {selectedTask.status === 'running' && (
                  <LinearProgress
                    variant="determinate"
                    value={selectedTask.progress}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: getStatusColor(selectedTask.status),
                      },
                    }}
                  />
                )}
              </Box>

              {selectedTask.results && (
                <Box>
                  <Typography variant="h6" sx={{ color: 'white', mb: 2 }}>
                    Results
                  </Typography>
                  
                  {selectedTask.results.improvements.length > 0 && (
                    <Alert severity="success" sx={{ mb: 2, backgroundColor: 'rgba(76, 175, 80, 0.1)', border: '1px solid rgba(76, 175, 80, 0.3)' }}>
                      <AlertTitle sx={{ color: 'white' }}>Improvements</AlertTitle>
                      {selectedTask.results.improvements.map((improvement, index) => (
                        <Typography key={index} variant="body2" sx={{ color: 'white' }}>
                          • {improvement}
                        </Typography>
                      ))}
                    </Alert>
                  )}

                  {selectedTask.results.issues.length > 0 && (
                    <Alert severity="warning" sx={{ mb: 2, backgroundColor: 'rgba(255, 152, 0, 0.1)', border: '1px solid rgba(255, 152, 0, 0.3)' }}>
                      <AlertTitle sx={{ color: 'white' }}>Issues Found</AlertTitle>
                      {selectedTask.results.issues.map((issue, index) => (
                        <Typography key={index} variant="body2" sx={{ color: 'white' }}>
                          • {issue}
                        </Typography>
                      ))}
                    </Alert>
                  )}

                  <Typography variant="h6" sx={{ color: 'white', mb: 1 }}>
                    Metrics
                  </Typography>
                  <Grid container spacing={2}>
                    {Object.entries(selectedTask.results.metrics).map(([key, value]) => (
                      <Grid size={{ xs: 6, sm: 4 }} key={key}>
                        <Card sx={{ backgroundColor: 'rgba(255, 255, 255, 0.05)' }}>
                          <CardContent sx={{ p: 2, textAlign: 'center' }}>
                            <Typography variant="h6" sx={{ color: 'white', fontWeight: 700 }}>
                              {typeof value === 'number' && value < 0 ? value : `+${value}`}%
                            </Typography>
                            <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)', textTransform: 'capitalize' }}>
                              {key.replace(/([A-Z])/g, ' $1')}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 3, borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <Button
            onClick={() => setDialogOpen(false)}
            sx={{ color: 'rgba(255, 255, 255, 0.7)' }}
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SelfOptimizationPanel;
