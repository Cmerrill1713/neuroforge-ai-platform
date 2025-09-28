import React, { useState, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  Slider,
  IconButton,
  Tooltip,
  Chip,
  Button,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Grid,
  TextField,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  VolumeUp as VolumeUpIcon,
  TextFields as TextIcon,
} from '@mui/icons-material';

interface DIAParameters {
  temperature: number;
  top_p: number;
  top_k: number;
  repeat_penalty: number;
  num_ctx: number;
  num_predict: number;
}

interface DIAState {
  isGenerating: boolean;
  parameters: DIAParameters;
  lastResponse: string | null;
  error: string | null;
  generationTime: number;
  tokensPerSecond: number;
  inputText: string;
  multimodalMode: boolean;
}

export const DIALLM: React.FC = () => {
  const [state, setState] = useState<DIAState>({
    isGenerating: false,
    parameters: {
      temperature: 0.7,
      top_p: 0.9,
      top_k: 40,
      repeat_penalty: 1.1,
      num_ctx: 4096,
      num_predict: 2048,
    },
    lastResponse: null,
    error: null,
    generationTime: 0,
    tokensPerSecond: 0,
    inputText: '',
    multimodalMode: false,
  });

  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);

  const handleParameterChange = useCallback((parameter: keyof DIAParameters, value: number) => {
    setState(prev => ({
      ...prev,
      parameters: {
        ...prev.parameters,
        [parameter]: value,
      },
    }));
  }, []);

  const generateResponse = useCallback(async () => {
    if (!state.inputText.trim()) return;

    setState(prev => ({ 
      ...prev, 
      isGenerating: true, 
      error: null,
      generationTime: 0,
      tokensPerSecond: 0,
    }));

    const startTime = Date.now();

    try {
      // Use DIA MLX Server
      const response = await fetch('http://localhost:11435/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'dia-1.6b-mlx',
          prompt: state.inputText,
          stream: false,
          options: {
            temperature: state.parameters.temperature,
            top_p: state.parameters.top_p,
            top_k: state.parameters.top_k,
            repeat_penalty: state.parameters.repeat_penalty,
            num_ctx: state.parameters.num_ctx,
            num_predict: state.parameters.num_predict,
          }
        }),
      });

      const endTime = Date.now();
      const generationTime = endTime - startTime;

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.response) {
        const tokensPerSecond = data.eval_count / (generationTime / 1000);
        
        setState(prev => ({
          ...prev,
          lastResponse: data.response,
          generationTime,
          tokensPerSecond,
          isGenerating: false,
        }));
      } else {
        throw new Error('No response received from DIA model');
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error occurred';
      setState(prev => ({
        ...prev,
        error: errorMsg,
        isGenerating: false,
      }));
    }
  }, [state.inputText, state.parameters]);

  const stopGeneration = useCallback(() => {
    setState(prev => ({ ...prev, isGenerating: false }));
  }, []);

  const resetParameters = useCallback(() => {
    setState(prev => ({
      ...prev,
      parameters: {
        temperature: 0.7,
        top_p: 0.9,
        top_k: 40,
        repeat_penalty: 1.1,
        num_ctx: 4096,
        num_predict: 2048,
      },
    }));
  }, []);

  const ParameterControl: React.FC<{
    label: string;
    value: number;
    min: number;
    max: number;
    step: number;
    onChange: (value: number) => void;
    icon: React.ReactNode;
    color: string;
    description?: string;
  }> = ({ label, value, min, max, step, onChange, icon, color, description }) => (
    <Card sx={{
      background: 'rgba(10, 10, 10, 0.8)',
      backdropFilter: 'blur(20px)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: 3,
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
    }}>
      <CardContent sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box sx={{ color, mr: 1 }}>{icon}</Box>
          <Typography variant="subtitle2" sx={{ color: 'white', fontWeight: 600 }}>
            {label}
          </Typography>
        </Box>
        
        <Box sx={{ 
          position: 'relative',
          width: 120,
          height: 120,
          mx: 'auto',
          mb: 2,
        }}>
          {/* Circular Progress Background */}
          <Box sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            borderRadius: '50%',
            background: `conic-gradient(${color} 0deg, ${color} ${(value - min) / (max - min) * 360}deg, rgba(255,255,255,0.1) ${(value - min) / (max - min) * 360}deg, rgba(255,255,255,0.1) 360deg)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <Box sx={{
              width: 80,
              height: 80,
              borderRadius: '50%',
              background: 'rgba(10, 10, 10, 0.9)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '2px solid rgba(255, 255, 255, 0.1)',
            }}>
              <Typography variant="h6" sx={{ color: 'white', fontWeight: 700 }}>
                {value.toFixed(step < 1 ? 2 : 0)}
              </Typography>
            </Box>
          </Box>
        </Box>
        
        <Slider
          value={value}
          onChange={(_, newValue) => onChange(newValue as number)}
          min={min}
          max={max}
          step={step}
          sx={{
            color,
            '& .MuiSlider-thumb': {
              backgroundColor: color,
              width: 20,
              height: 20,
              '&:hover': {
                boxShadow: `0 0 0 8px ${color}20`,
              },
            },
            '& .MuiSlider-track': {
              backgroundColor: color,
            },
            '& .MuiSlider-rail': {
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
            },
          }}
        />
        
        {description && (
          <Typography variant="caption" sx={{ 
            color: 'rgba(255, 255, 255, 0.6)', 
            display: 'block',
            textAlign: 'center',
            mt: 1,
          }}>
            {description}
          </Typography>
        )}
      </CardContent>
    </Card>
  );

  return (
    <Paper sx={{
      p: 3,
      background: 'rgba(10, 10, 10, 0.8)',
      backdropFilter: 'blur(20px)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: 3,
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
    }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <PsychologyIcon sx={{ color: '#9C27B0', fontSize: 32 }} />
          <Box>
            <Typography variant="h5" sx={{ color: 'white', fontWeight: 600 }}>
              DIA LLM Controller
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              DIA-1.6B-MLX: Multimodal AI model with text and audio capabilities
            </Typography>
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title="Advanced Settings">
            <IconButton
              onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
              sx={{ color: 'white' }}
            >
              <SettingsIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Reset Parameters">
            <IconButton
              onClick={resetParameters}
              sx={{ color: 'white' }}
            >
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Model Info */}
      <Box sx={{ mb: 3, p: 2, backgroundColor: 'rgba(156, 39, 176, 0.1)', borderRadius: 2 }}>
        <Typography variant="body2" sx={{ color: 'white', mb: 1 }}>
          <strong>DIA-1.6B-MLX</strong>: A multimodal model with encoder-decoder architecture
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 1 }}>
          <Chip label="1.6B Parameters" size="small" sx={{ backgroundColor: 'rgba(156, 39, 176, 0.2)', color: 'white' }} />
          <Chip label="Text + Audio" size="small" sx={{ backgroundColor: 'rgba(156, 39, 176, 0.2)', color: 'white' }} />
          <Chip label="MLX Optimized" size="small" sx={{ backgroundColor: 'rgba(156, 39, 176, 0.2)', color: 'white' }} />
          <Chip label="Apple Silicon" size="small" sx={{ backgroundColor: 'rgba(156, 39, 176, 0.2)', color: 'white' }} />
        </Box>
        <Alert severity="info" sx={{ backgroundColor: 'rgba(33, 150, 243, 0.1)', color: 'white' }}>
          <Typography variant="caption">
            <strong>Status:</strong> DIA MLX Server running on port 11435. Model configuration loaded, ready for MLX integration.
          </Typography>
        </Alert>
      </Box>

      {/* Multimodal Mode Toggle */}
      <Box sx={{ mb: 3 }}>
        <FormControlLabel
          control={
            <Switch
              checked={state.multimodalMode}
              onChange={(e) => setState(prev => ({ ...prev, multimodalMode: e.target.checked }))}
              sx={{
                '& .MuiSwitch-switchBase.Mui-checked': {
                  color: '#9C27B0',
                },
                '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                  backgroundColor: '#9C27B0',
                },
              }}
            />
          }
          label={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <VolumeUpIcon sx={{ color: state.multimodalMode ? '#9C27B0' : 'rgba(255, 255, 255, 0.6)' }} />
              <Typography sx={{ color: 'white' }}>
                Multimodal Mode (Text + Audio)
              </Typography>
            </Box>
          }
        />
      </Box>

      {/* Parameter Controls */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid xs={12} sm={6} md={4}>
          <ParameterControl
            label="Temperature"
            value={state.parameters.temperature}
            min={0}
            max={2}
            step={0.1}
            onChange={(value) => handleParameterChange('temperature', value)}
            icon={<SpeedIcon />}
            color="#4caf50"
            description="Controls randomness"
          />
        </Grid>
        
        <Grid xs={12} sm={6} md={4}>
          <ParameterControl
            label="Top P"
            value={state.parameters.top_p}
            min={0}
            max={1}
            step={0.05}
            onChange={(value) => handleParameterChange('top_p', value)}
            icon={<PsychologyIcon />}
            color="#2196f3"
            description="Nucleus sampling"
          />
        </Grid>
        
        <Grid xs={12} sm={6} md={4}>
          <ParameterControl
            label="Top K"
            value={state.parameters.top_k}
            min={1}
            max={100}
            step={1}
            onChange={(value) => handleParameterChange('top_k', value)}
            icon={<MemoryIcon />}
            color="#ff9800"
            description="Token selection"
          />
        </Grid>
      </Grid>

      {/* Advanced Settings */}
      {showAdvancedSettings && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ color: 'white', mb: 2 }}>
            Advanced Parameters
          </Typography>
          <Grid container spacing={2}>
            <Grid xs={12} sm={6} md={4}>
              <ParameterControl
                label="Repeat Penalty"
                value={state.parameters.repeat_penalty}
                min={0.1}
                max={2}
                step={0.1}
                onChange={(value) => handleParameterChange('repeat_penalty', value)}
                icon={<PsychologyIcon />}
                color="#9c27b0"
                description="Prevents repetition"
              />
            </Grid>
            
            <Grid xs={12} sm={6} md={4}>
              <ParameterControl
                label="Context Length"
                value={state.parameters.num_ctx}
                min={512}
                max={8192}
                step={512}
                onChange={(value) => handleParameterChange('num_ctx', value)}
                icon={<MemoryIcon />}
                color="#e91e63"
                description="Memory window"
              />
            </Grid>
            
            <Grid xs={12} sm={6} md={4}>
              <ParameterControl
                label="Max Tokens"
                value={state.parameters.num_predict}
                min={100}
                max={4096}
                step={100}
                onChange={(value) => handleParameterChange('num_predict', value)}
                icon={<SpeedIcon />}
                color="#f44336"
                description="Response length"
              />
            </Grid>
          </Grid>
        </Box>
      )}

      {/* Input and Controls */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" sx={{ color: 'white', mb: 1 }}>
          {state.multimodalMode ? 'Text + Audio Input:' : 'Text Input:'}
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-end' }}>
          <Box sx={{ flexGrow: 1 }}>
            <TextField
              multiline
              rows={4}
              value={state.inputText}
              onChange={(e) => setState(prev => ({ ...prev, inputText: e.target.value }))}
              placeholder={state.multimodalMode ? "Enter text or describe audio content..." : "Enter your prompt here..."}
              variant="outlined"
              fullWidth
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  color: 'white',
                  '& fieldset': {
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                  },
                  '&:hover fieldset': {
                    borderColor: 'rgba(255, 255, 255, 0.3)',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#9C27B0',
                  },
                },
                '& .MuiInputBase-input': {
                  color: 'white',
                  '&::placeholder': {
                    color: 'rgba(255, 255, 255, 0.5)',
                    opacity: 1,
                  },
                },
              }}
            />
          </Box>
          
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Button
              variant="contained"
              onClick={generateResponse}
              disabled={!state.inputText.trim() || state.isGenerating}
              startIcon={state.isGenerating ? <CircularProgress size={20} /> : <PlayIcon />}
              sx={{
                background: 'linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #7B1FA2 0%, #6A1B9A 100%)',
                },
                minWidth: 120,
              }}
            >
              {state.isGenerating ? 'Generating...' : 'Generate'}
            </Button>
            
            {state.isGenerating && (
              <Button
                variant="outlined"
                onClick={stopGeneration}
                startIcon={<StopIcon />}
                sx={{
                  color: '#f44336',
                  borderColor: '#f44336',
                  '&:hover': {
                    backgroundColor: 'rgba(244, 67, 54, 0.1)',
                    borderColor: '#f44336',
                  },
                }}
              >
                Stop
              </Button>
            )}
          </Box>
        </Box>
      </Box>

      {/* Status and Results */}
      {state.error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {state.error}
        </Alert>
      )}

      {state.lastResponse && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ color: 'white', mb: 1 }}>
            DIA Response:
          </Typography>
          <Paper sx={{ 
            p: 2, 
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }}>
            <Typography variant="body1" sx={{ color: 'white', whiteSpace: 'pre-wrap' }}>
              {state.lastResponse}
            </Typography>
          </Paper>
          
          {/* Performance Metrics */}
          <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
            <Chip
              label={`${state.generationTime}ms`}
              size="small"
              sx={{ backgroundColor: 'rgba(76, 175, 80, 0.2)', color: 'white' }}
            />
            <Chip
              label={`${state.tokensPerSecond.toFixed(1)} tokens/sec`}
              size="small"
              sx={{ backgroundColor: 'rgba(33, 150, 243, 0.2)', color: 'white' }}
            />
            <Chip
              label="DIA-1.6B-MLX"
              size="small"
              sx={{ backgroundColor: 'rgba(156, 39, 176, 0.2)', color: 'white' }}
            />
            {state.multimodalMode && (
              <Chip
                label="Multimodal"
                size="small"
                sx={{ backgroundColor: 'rgba(255, 152, 0, 0.2)', color: 'white' }}
              />
            )}
          </Box>
        </Box>
      )}
    </Paper>
  );
};
