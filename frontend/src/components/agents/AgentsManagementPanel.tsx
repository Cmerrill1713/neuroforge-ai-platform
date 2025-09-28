import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  Button,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Switch,
  FormControlLabel,
  Divider,
  LinearProgress,
  Badge,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Grid,
} from '@mui/material';
import {
  Add as AddIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Settings as SettingsIcon,
  MoreVert as MoreVertIcon,
  Psychology as PsychologyIcon,
  AutoAwesome as AutoAwesomeIcon,
  Code as CodeIcon,
  Security as SecurityIcon,
  BugReport as BugReportIcon,
  Analytics as AnalyticsIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  CloudUpload as CloudUploadIcon,
} from '@mui/icons-material';

interface Agent {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'inactive' | 'error' | 'loading';
  description: string;
  capabilities: string[];
  lastActivity: Date;
  performance: {
    successRate: number;
    avgResponseTime: number;
    totalRequests: number;
  };
  configuration: {
    enabled: boolean;
    priority: number;
    timeout: number;
    retries: number;
  };
}

const AgentsManagementPanel: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([
    {
      id: '1',
      name: 'Code Assistant Agent',
      type: 'Code Generation',
      status: 'active',
      description: 'AI agent specialized in code generation and debugging',
      capabilities: ['Code Generation', 'Debugging', 'Refactoring', 'Documentation'],
      lastActivity: new Date(),
      performance: {
        successRate: 94.5,
        avgResponseTime: 1.2,
        totalRequests: 1250,
      },
      configuration: {
        enabled: true,
        priority: 1,
        timeout: 30,
        retries: 3,
      },
    },
    {
      id: '2',
      name: 'Security Analyzer',
      type: 'Security',
      status: 'active',
      description: 'Automated security vulnerability detection and analysis',
      capabilities: ['Vulnerability Detection', 'Security Scanning', 'Compliance Check', 'Threat Analysis'],
      lastActivity: new Date(Date.now() - 300000),
      performance: {
        successRate: 98.2,
        avgResponseTime: 2.1,
        totalRequests: 890,
      },
      configuration: {
        enabled: true,
        priority: 2,
        timeout: 45,
        retries: 2,
      },
    },
    {
      id: '3',
      name: 'Performance Optimizer',
      type: 'Optimization',
      status: 'inactive',
      description: 'AI agent for system performance monitoring and optimization',
      capabilities: ['Performance Monitoring', 'Resource Optimization', 'Bottleneck Detection', 'Auto-scaling'],
      lastActivity: new Date(Date.now() - 600000),
      performance: {
        successRate: 91.8,
        avgResponseTime: 0.8,
        totalRequests: 2100,
      },
      configuration: {
        enabled: false,
        priority: 3,
        timeout: 20,
        retries: 5,
      },
    },
    {
      id: '4',
      name: 'Data Analyzer',
      type: 'Analytics',
      status: 'error',
      description: 'Advanced data analysis and insights generation',
      capabilities: ['Data Processing', 'Pattern Recognition', 'Predictive Analytics', 'Reporting'],
      lastActivity: new Date(Date.now() - 900000),
      performance: {
        successRate: 87.3,
        avgResponseTime: 3.5,
        totalRequests: 650,
      },
      configuration: {
        enabled: true,
        priority: 4,
        timeout: 60,
        retries: 1,
      },
    },
  ]);

  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [menuAgent, setMenuAgent] = useState<Agent | null>(null);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#4caf50';
      case 'inactive': return '#9e9e9e';
      case 'error': return '#f44336';
      case 'loading': return '#ff9800';
      default: return '#9e9e9e';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <PlayIcon />;
      case 'inactive': return <StopIcon />;
      case 'error': return <StopIcon />;
      case 'loading': return <StopIcon />;
      default: return <StopIcon />;
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'Code Generation': return <CodeIcon />;
      case 'Security': return <SecurityIcon />;
      case 'Optimization': return <AutoAwesomeIcon />;
      case 'Analytics': return <AnalyticsIcon />;
      default: return <PsychologyIcon />;
    }
  };

  const handleAgentAction = (agent: Agent, action: string) => {
    switch (action) {
      case 'start':
        setAgents(prev => prev.map(a => 
          a.id === agent.id ? { ...a, status: 'loading' as const } : a
        ));
        // Simulate starting agent
        setTimeout(() => {
          setAgents(prev => prev.map(a => 
            a.id === agent.id ? { ...a, status: 'active' as const, lastActivity: new Date() } : a
          ));
        }, 2000);
        break;
      case 'stop':
        setAgents(prev => prev.map(a => 
          a.id === agent.id ? { ...a, status: 'inactive' as const } : a
        ));
        break;
      case 'edit':
        setSelectedAgent(agent);
        setDialogOpen(true);
        break;
      case 'delete':
        setAgents(prev => prev.filter(a => a.id !== agent.id));
        break;
    }
    setAnchorEl(null);
    setMenuAgent(null);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, agent: Agent) => {
    setAnchorEl(event.currentTarget);
    setMenuAgent(agent);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setMenuAgent(null);
  };

  const handleToggleAgent = (agentId: string) => {
    setAgents(prev => prev.map(agent => {
      if (agent.id === agentId) {
        const newStatus = agent.status === 'active' ? 'inactive' : 'loading';
        if (newStatus === 'loading') {
          // Simulate starting
          setTimeout(() => {
            setAgents(prev => prev.map(a => 
              a.id === agentId ? { ...a, status: 'active' as const, lastActivity: new Date() } : a
            ));
          }, 2000);
        }
        return { ...agent, status: newStatus as any };
      }
      return agent;
    }));
  };

  return (
    <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" sx={{ color: 'white', fontWeight: 700 }}>
          AI Agents Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setDialogOpen(true)}
          sx={{
            background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #1565c0 0%, #1976d2 100%)',
            },
          }}
        >
          Add Agent
        </Button>
      </Box>

      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { 
          xs: '1fr', 
          md: 'repeat(2, 1fr)', 
          lg: 'repeat(3, 1fr)' 
        }, 
        gap: 3 
      }}>
        {agents.map((agent) => (
          <Box key={agent.id}>
            <Card sx={{
              background: 'rgba(10, 10, 10, 0.8)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 3,
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 12px 40px rgba(0, 0, 0, 0.4)',
              },
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {getTypeIcon(agent.type)}
                    <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                      {agent.name}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip
                      icon={getStatusIcon(agent.status)}
                      label={agent.status.toUpperCase()}
                      size="small"
                      sx={{
                        backgroundColor: getStatusColor(agent.status),
                        color: 'white',
                        fontWeight: 600,
                      }}
                    />
                    <IconButton
                      onClick={(e) => handleMenuOpen(e, agent)}
                      sx={{ color: 'white' }}
                    >
                      <MoreVertIcon />
                    </IconButton>
                  </Box>
                </Box>

                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 2 }}>
                  {agent.description}
                </Typography>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)', mb: 1, display: 'block' }}>
                    Capabilities
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {agent.capabilities.map((capability) => (
                      <Chip
                        key={capability}
                        label={capability}
                        size="small"
                        sx={{
                          backgroundColor: 'rgba(25, 118, 210, 0.2)',
                          color: 'white',
                          fontSize: '0.7rem',
                        }}
                      />
                    ))}
                  </Box>
                </Box>

                <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.1)', my: 2 }} />

                <Box sx={{ mb: 2 }}>
                  <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)', mb: 1, display: 'block' }}>
                    Performance
                  </Typography>
                  <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1 }}>
                    <Box>
                      <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                        Success Rate
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'white', fontWeight: 600 }}>
                        {agent.performance.successRate}%
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                        Avg Response
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'white', fontWeight: 600 }}>
                        {agent.performance.avgResponseTime}s
                      </Typography>
                    </Box>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={agent.performance.successRate}
                    sx={{
                      mt: 1,
                      height: 4,
                      borderRadius: 2,
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: getStatusColor(agent.status),
                      },
                    }}
                  />
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={agent.status === 'active'}
                        onChange={() => handleToggleAgent(agent.id)}
                        disabled={agent.status === 'loading'}
                        sx={{
                          '& .MuiSwitch-switchBase.Mui-checked': {
                            color: getStatusColor(agent.status),
                          },
                          '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                            backgroundColor: getStatusColor(agent.status),
                          },
                        }}
                      />
                    }
                    label={agent.status === 'active' ? 'Active' : 'Inactive'}
                    sx={{ color: 'white', margin: 0 }}
                  />
                  <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                    {agent.lastActivity.toLocaleTimeString()}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Box>
        ))}
      </Box>

      {/* Agent Actions Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        sx={{
          '& .MuiPaper-root': {
            backgroundColor: 'rgba(10, 10, 10, 0.95)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          },
        }}
      >
        <MenuItem onClick={() => handleAgentAction(menuAgent!, 'start')} disabled={menuAgent?.status === 'active'}>
          <ListItemIcon>
            <PlayIcon sx={{ color: 'white' }} />
          </ListItemIcon>
          <ListItemText sx={{ color: 'white' }}>Start Agent</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleAgentAction(menuAgent!, 'stop')} disabled={menuAgent?.status !== 'active'}>
          <ListItemIcon>
            <StopIcon sx={{ color: 'white' }} />
          </ListItemIcon>
          <ListItemText sx={{ color: 'white' }}>Stop Agent</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleAgentAction(menuAgent!, 'edit')}>
          <ListItemIcon>
            <EditIcon sx={{ color: 'white' }} />
          </ListItemIcon>
          <ListItemText sx={{ color: 'white' }}>Edit Agent</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleAgentAction(menuAgent!, 'delete')} sx={{ color: '#f44336' }}>
          <ListItemIcon>
            <DeleteIcon sx={{ color: '#f44336' }} />
          </ListItemIcon>
          <ListItemText sx={{ color: '#f44336' }}>Delete Agent</ListItemText>
        </MenuItem>
      </Menu>

      {/* Agent Configuration Dialog */}
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
          {selectedAgent ? 'Edit Agent' : 'Add New Agent'}
        </DialogTitle>
        <DialogContent sx={{ pt: 3 }}>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Agent Name"
                defaultValue={selectedAgent?.name || ''}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    color: 'white',
                    '& fieldset': {
                      borderColor: 'rgba(255, 255, 255, 0.2)',
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: 'white',
                  },
                }}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Agent Type"
                defaultValue={selectedAgent?.type || ''}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    color: 'white',
                    '& fieldset': {
                      borderColor: 'rgba(255, 255, 255, 0.2)',
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: 'white',
                  },
                }}
              />
            </Grid>
            <Grid size={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Description"
                defaultValue={selectedAgent?.description || ''}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    color: 'white',
                    '& fieldset': {
                      borderColor: 'rgba(255, 255, 255, 0.2)',
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: 'white',
                  },
                }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 3, borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <Button
            onClick={() => setDialogOpen(false)}
            sx={{ color: 'rgba(255, 255, 255, 0.7)' }}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={() => setDialogOpen(false)}
            sx={{
              background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #1565c0 0%, #1976d2 100%)',
              },
            }}
          >
            {selectedAgent ? 'Update Agent' : 'Create Agent'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AgentsManagementPanel;
