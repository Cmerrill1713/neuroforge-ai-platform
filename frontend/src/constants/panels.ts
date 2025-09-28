import React from 'react';
import { 
  Chat as ChatIcon,
  Code as CodeIcon,
  Psychology as PsychologyIcon,
  AutoAwesome as AutoAwesomeIcon,
  Visibility as VisibilityIcon,
  School as SchoolIcon,
  Gavel as GavelIcon,
  Monitor as MonitorIcon
} from '@mui/icons-material';
import { Panel } from '../types';

export const PANELS: Panel[] = [
  { id: 'chat', name: 'AI Assistant', icon: <ChatIcon />, color: '#1976d2' },
  { id: 'agents', name: 'AI Agents', icon: <PsychologyIcon />, color: '#388e3c' },
  { id: 'optimization', name: 'Self-Optimization', icon: <AutoAwesomeIcon />, color: '#f57c00' },
  { id: 'code', name: 'Code Assistant', icon: <CodeIcon />, color: '#7b1fa2' },
  { id: 'vision', name: 'Vision Assistant', icon: <VisibilityIcon />, color: '#d32f2f' },
  { id: 'learning', name: 'Learning Hub', icon: <SchoolIcon />, color: '#0288d1' },
  { id: 'devil', name: "Devil's Advocate", icon: <GavelIcon />, color: '#5d4037' },
  { id: 'monitoring', name: 'LLM Monitoring', icon: <MonitorIcon />, color: '#e91e63' }
];
