import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  LinearProgress,
  Alert,
  Button,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Paper,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  ExpandMore as ExpandMoreIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  Lightbulb as LightbulbIcon,
  Shield as ShieldIcon,
  TrendingUp as TrendingUpIcon,
  Memory as MemoryIcon,
  Speed as SpeedIcon,
} from '@mui/icons-material';

interface ModelCapability {
  model_id: string;
  capability: 'tiny' | 'small' | 'medium' | 'large' | 'xlarge';
  parameter_count: number;
  reasoning_level: 'basic' | 'intermediate' | 'advanced' | 'expert';
  hallucination_risk: number;
  context_window: number;
  strengths: string[];
  weaknesses: string[];
  needs_reasoning_assistance: boolean;
  needs_knowledge_injection: boolean;
  needs_hallucination_prevention: boolean;
}

interface AdaptationResult {
  original_prompt: string;
  enhanced_prompt: string;
  adaptation_strategy: string;
  reasoning_assistance: string | null;
  hallucination_prevention: string | null;
  confidence_threshold: number;
  verification_required: boolean;
  model_recommendations: string[];
  success_indicators: string[];
}

interface ResponseAnalysis {
  original_response: string;
  enhanced_response: string;
  hallucination_detected: boolean;
  confidence_score: number;
  reasoning_quality: number;
  factual_accuracy: number;
  improvement_suggestions: string[];
  verification_needed: boolean;
}

const AdaptiveModelSystem: React.FC = () => {
  const [selectedModel, setSelectedModel] = useState<string>('llama3.2:3b');
  const [taskType, setTaskType] = useState<string>('general');
  const [prompt, setPrompt] = useState<string>('');
  const [adaptationResult, setAdaptationResult] = useState<AdaptationResult | null>(null);
  const [responseAnalysis, setResponseAnalysis] = useState<ResponseAnalysis | null>(null);
  const [modelCapabilities, setModelCapabilities] = useState<ModelCapability[]>([]);
  const [loading, setLoading] = useState(false);
  const [autoAdapt, setAutoAdapt] = useState(true);

  // Mock model capabilities data
  useEffect(() => {
    setModelCapabilities([
      {
        model_id: 'llama3.2:3b',
        capability: 'tiny',
        parameter_count: 3000000000,
        reasoning_level: 'basic',
        hallucination_risk: 0.8,
        context_window: 8192,
        strengths: ['fast', 'efficient', 'lightweight'],
        weaknesses: ['reasoning', 'factual_accuracy', 'complex_tasks'],
        needs_reasoning_assistance: true,
        needs_knowledge_injection: true,
        needs_hallucination_prevention: true,
      },
      {
        model_id: 'mistral:7b',
        capability: 'small',
        parameter_count: 7000000000,
        reasoning_level: 'intermediate',
        hallucination_risk: 0.6,
        context_window: 32768,
        strengths: ['coding', 'reasoning', 'instruction_following'],
        weaknesses: ['creative_writing', 'complex_reasoning'],
        needs_reasoning_assistance: true,
        needs_knowledge_injection: true,
        needs_hallucination_prevention: true,
      },
      {
        model_id: 'llama3.1:8b',
        capability: 'medium',
        parameter_count: 8000000000,
        reasoning_level: 'advanced',
        hallucination_risk: 0.4,
        context_window: 128000,
        strengths: ['reasoning', 'coding', 'math', 'general_knowledge'],
        weaknesses: ['creative_writing', 'specialized_domains'],
        needs_reasoning_assistance: false,
        needs_knowledge_injection: true,
        needs_hallucination_prevention: true,
      },
      {
        model_id: 'gpt-4-turbo',
        capability: 'large',
        parameter_count: 70000000000,
        reasoning_level: 'expert',
        hallucination_risk: 0.2,
        context_window: 128000,
        strengths: ['reasoning', 'coding', 'math', 'creative', 'general'],
        weaknesses: ['real_time_info', 'specialized_domains'],
        needs_reasoning_assistance: false,
        needs_knowledge_injection: false,
        needs_hallucination_prevention: false,
      },
    ]);
  }, []);

  const handleAdaptPrompt = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('/api/adaptation/adapt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model_id: selectedModel,
          prompt: prompt,
          task_type: taskType,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setAdaptationResult(result);
      }
    } catch (error) {
      console.error('Failed to adapt prompt:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeResponse = async (response: string) => {
    setLoading(true);
    try {
      const apiResponse = await fetch('/api/adaptation/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model_id: selectedModel,
          response: response,
          task_type: taskType,
        }),
      });

      if (apiResponse.ok) {
        const analysis = await apiResponse.json();
        setResponseAnalysis(analysis);
      }
    } catch (error) {
      console.error('Failed to analyze response:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCapabilityColor = (capability: string) => {
    switch (capability) {
      case 'tiny': return '#f44336';
      case 'small': return '#ff9800';
      case 'medium': return '#2196f3';
      case 'large': return '#4caf50';
      case 'xlarge': return '#9c27b0';
      default: return '#9e9e9e';
    }
  };

  const getCapabilityIcon = (capability: string) => {
    switch (capability) {
      case 'tiny': return <ErrorIcon />;
      case 'small': return <WarningIcon />;
      case 'medium': return <CheckCircleIcon />;
      case 'large': return <TrendingUpIcon />;
      case 'xlarge': return <PsychologyIcon />;
      default: return <ErrorIcon />;
    }
  };

  const selectedModelCapability = modelCapabilities.find(m => m.model_id === selectedModel);

  return (
    <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" sx={{ color: 'white', fontWeight: 700 }}>
          Adaptive Model System
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={autoAdapt}
                onChange={(e) => setAutoAdapt(e.target.checked)}
                sx={{
                  '& .MuiSwitch-switchBase.Mui-checked': {
                    color: '#1976d2',
                  },
                  '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                    backgroundColor: '#1976d2',
                  },
                }}
              />
            }
            label="Auto Adapt"
            sx={{ color: 'white' }}
          />
          <Tooltip title="Refresh">
            <IconButton sx={{ color: 'white' }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 3 }}>
        {/* Model Selection */}
        <Box sx={{ flex: { xs: 1, md: '0 0 33.333%' } }}>
          <Card sx={{
            background: 'rgba(10, 10, 10, 0.8)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: 3,
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
          }}>
            <CardContent>
              <Typography variant="h6" sx={{ color: 'white', mb: 2 }}>
                Model Selection
              </Typography>
              
              {modelCapabilities.map((model) => (
                <Card
                  key={model.model_id}
                  sx={{
                    mb: 2,
                    cursor: 'pointer',
                    backgroundColor: selectedModel === model.model_id ? 'rgba(25, 118, 210, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                    border: selectedModel === model.model_id ? '2px solid #1976d2' : '1px solid rgba(255, 255, 255, 0.1)',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    },
                  }}
                  onClick={() => setSelectedModel(model.model_id)}
                >
                  <CardContent sx={{ p: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Box sx={{ color: getCapabilityColor(model.capability), mr: 1 }}>
                        {getCapabilityIcon(model.capability)}
                      </Box>
                      <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 600 }}>
                        {model.model_id}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                      <Chip
                        label={model.capability.toUpperCase()}
                        size="small"
                        sx={{
                          backgroundColor: getCapabilityColor(model.capability),
                          color: 'white',
                          fontWeight: 600,
                        }}
                      />
                      <Chip
                        label={`${(model.parameter_count / 1000000000).toFixed(1)}B`}
                        size="small"
                        sx={{ backgroundColor: 'rgba(255, 255, 255, 0.2)', color: 'white' }}
                      />
                    </Box>
                    
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                      Reasoning: {model.reasoning_level} | Risk: {(model.hallucination_risk * 100).toFixed(0)}%
                    </Typography>
                    
                    <LinearProgress
                      variant="determinate"
                      value={model.hallucination_risk * 100}
                      sx={{
                        height: 6,
                        borderRadius: 3,
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: getCapabilityColor(model.capability),
                        },
                      }}
                    />
                  </CardContent>
                </Card>
              ))}
            </CardContent>
          </Card>
        </Box>

        {/* Prompt Input and Adaptation */}
        <Box sx={{ flex: { xs: 1, md: '0 0 66.666%' } }}>
          <Card sx={{
            background: 'rgba(10, 10, 10, 0.8)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: 3,
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
            mb: 3,
          }}>
            <CardContent>
              <Typography variant="h6" sx={{ color: 'white', mb: 2 }}>
                Prompt Adaptation
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                  Task Type
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {['general', 'programming', 'mathematics', 'logic', 'analysis'].map((type) => (
                    <Chip
                      key={type}
                      label={type}
                      onClick={() => setTaskType(type)}
                      sx={{
                        backgroundColor: taskType === type ? '#1976d2' : 'rgba(255, 255, 255, 0.1)',
                        color: 'white',
                        cursor: 'pointer',
                      }}
                    />
                  ))}
                </Box>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                  Original Prompt
                </Typography>
                <Box
                  component="textarea"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Enter your prompt here..."
                  sx={{
                    width: '100%',
                    minHeight: 100,
                    p: 2,
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: 2,
                    color: 'white',
                    fontSize: '14px',
                    fontFamily: 'monospace',
                    resize: 'vertical',
                    '&::placeholder': {
                      color: 'rgba(255, 255, 255, 0.5)',
                    },
                    '&:focus': {
                      outline: 'none',
                      borderColor: '#1976d2',
                    },
                  }}
                />
              </Box>
              
              <Button
                variant="contained"
                onClick={handleAdaptPrompt}
                disabled={!prompt.trim() || loading}
                startIcon={<LightbulbIcon />}
                sx={{
                  backgroundColor: '#1976d2',
                  '&:hover': {
                    backgroundColor: '#1565c0',
                  },
                }}
              >
                {loading ? 'Adapting...' : 'Adapt Prompt'}
              </Button>
            </CardContent>
          </Card>

          {/* Adaptation Result */}
          {adaptationResult && (
            <Card sx={{
              background: 'rgba(10, 10, 10, 0.8)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 3,
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
            }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: 'white', mb: 2 }}>
                  Adaptation Result
                </Typography>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                    Strategy: {adaptationResult.adaptation_strategy}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                    Confidence Threshold: {(adaptationResult.confidence_threshold * 100).toFixed(0)}%
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 2 }}>
                    Verification Required: {adaptationResult.verification_required ? 'Yes' : 'No'}
                  </Typography>
                </Box>
                
                <Accordion sx={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', mb: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: 'white' }} />}>
                    <Typography sx={{ color: 'white' }}>Enhanced Prompt</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box
                      component="pre"
                      sx={{
                        backgroundColor: 'rgba(0, 0, 0, 0.3)',
                        p: 2,
                        borderRadius: 2,
                        color: 'white',
                        fontSize: '12px',
                        fontFamily: 'monospace',
                        whiteSpace: 'pre-wrap',
                        overflow: 'auto',
                        maxHeight: 300,
                      }}
                    >
                      {adaptationResult.enhanced_prompt}
                    </Box>
                  </AccordionDetails>
                </Accordion>
                
                {adaptationResult.reasoning_assistance && (
                  <Accordion sx={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', mb: 2 }}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: 'white' }} />}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <PsychologyIcon sx={{ color: '#2196f3', mr: 1 }} />
                        <Typography sx={{ color: 'white' }}>Reasoning Assistance</Typography>
                      </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Box
                        component="pre"
                        sx={{
                          backgroundColor: 'rgba(0, 0, 0, 0.3)',
                          p: 2,
                          borderRadius: 2,
                          color: 'white',
                          fontSize: '12px',
                          fontFamily: 'monospace',
                          whiteSpace: 'pre-wrap',
                          overflow: 'auto',
                          maxHeight: 300,
                        }}
                      >
                        {adaptationResult.reasoning_assistance}
                      </Box>
                    </AccordionDetails>
                  </Accordion>
                )}
                
                {adaptationResult.hallucination_prevention && (
                  <Accordion sx={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', mb: 2 }}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: 'white' }} />}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <ShieldIcon sx={{ color: '#f44336', mr: 1 }} />
                        <Typography sx={{ color: 'white' }}>Hallucination Prevention</Typography>
                      </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Box
                        component="pre"
                        sx={{
                          backgroundColor: 'rgba(0, 0, 0, 0.3)',
                          p: 2,
                          borderRadius: 2,
                          color: 'white',
                          fontSize: '12px',
                          fontFamily: 'monospace',
                          whiteSpace: 'pre-wrap',
                          overflow: 'auto',
                          maxHeight: 300,
                        }}
                      >
                        {adaptationResult.hallucination_prevention}
                      </Box>
                    </AccordionDetails>
                  </Accordion>
                )}
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                    Success Indicators
                  </Typography>
                  <List dense>
                    {adaptationResult.success_indicators.map((indicator, index) => (
                      <ListItem key={index} sx={{ py: 0.5 }}>
                        <ListItemIcon>
                          <CheckCircleIcon sx={{ color: '#4caf50', fontSize: 16 }} />
                        </ListItemIcon>
                        <ListItemText
                          primary={indicator}
                          primaryTypographyProps={{ fontSize: '12px', color: 'rgba(255, 255, 255, 0.8)' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                    Recommended Models
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {adaptationResult.model_recommendations.map((model) => (
                      <Chip
                        key={model}
                        label={model}
                        size="small"
                        sx={{
                          backgroundColor: 'rgba(25, 118, 210, 0.2)',
                          color: 'white',
                          border: '1px solid #1976d2',
                        }}
                      />
                    ))}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default AdaptiveModelSystem;
