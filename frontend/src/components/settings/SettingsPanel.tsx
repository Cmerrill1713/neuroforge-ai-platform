import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  Slider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Divider,
  IconButton,
  Tooltip,
  Chip,
  Alert,
  Grid,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  VolumeUp as VolumeUpIcon,
  VolumeOff as VolumeOffIcon,
  DarkMode as DarkModeIcon,
  LightMode as LightModeIcon,
  Speed as SpeedIcon,
  Language as LanguageIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useAppContext } from '../../contexts/AppContext';

interface Settings {
  voiceEnabled: boolean;
  voiceVolume: number;
  voiceSpeed: number;
  voiceLanguage: string;
  theme: 'dark' | 'light' | 'auto';
  notifications: boolean;
  autoSave: boolean;
  responseSpeed: 'fast' | 'balanced' | 'quality';
  modelPreference: string;
  privacyMode: boolean;
}

const defaultSettings: Settings = {
  voiceEnabled: true,
  voiceVolume: 0.8,
  voiceSpeed: 1.0,
  voiceLanguage: 'en-US',
  theme: 'dark',
  notifications: true,
  autoSave: true,
  responseSpeed: 'balanced',
  modelPreference: 'qwen2.5:7b',
  privacyMode: false,
};

const SettingsPanel: React.FC = () => {
  const { addNotification } = useAppContext();
  const [settings, setSettings] = useState<Settings>(defaultSettings);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    // Load settings from localStorage
    const savedSettings = localStorage.getItem('ai-assistant-settings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setSettings({ ...defaultSettings, ...parsed });
      } catch (error) {
        console.error('Failed to parse saved settings:', error);
      }
    }
  }, []);

  const handleSettingChange = (key: keyof Settings, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const handleSaveSettings = () => {
    try {
      localStorage.setItem('ai-assistant-settings', JSON.stringify(settings));
      setHasChanges(false);
      addNotification({
        id: Date.now().toString(),
        message: 'Settings saved successfully!',
        type: 'success',
      });
    } catch (error) {
      addNotification({
        id: Date.now().toString(),
        message: 'Failed to save settings',
        type: 'error',
      });
    }
  };

  const handleResetSettings = () => {
    setSettings(defaultSettings);
    setHasChanges(true);
    addNotification({
      id: Date.now().toString(),
      message: 'Settings reset to defaults',
      type: 'info',
    });
  };

  return (
    <Box sx={{
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: 3,
      p: 3,
      background: 'rgba(10, 10, 10, 0.8)',
      backdropFilter: 'blur(20px)',
      flexGrow: 1,
      display: 'flex',
      flexDirection: 'column',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
      minHeight: 400,
      maxHeight: '90vh',
      overflow: 'auto',
      position: 'relative',
    }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3, flexShrink: 0 }}>
        <Typography variant="h4" sx={{ color: 'white', fontWeight: 700 }}>
          Settings
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={handleResetSettings}
            sx={{
              color: 'rgba(255, 255, 255, 0.7)',
              borderColor: 'rgba(255, 255, 255, 0.3)',
              '&:hover': {
                borderColor: 'rgba(255, 255, 255, 0.5)',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
            }}
          >
            Reset
          </Button>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSaveSettings}
            disabled={!hasChanges}
            sx={{
              background: hasChanges ? 'linear-gradient(135deg, #4caf50 0%, #388e3c 100%)' : 'rgba(255, 255, 255, 0.1)',
              '&:hover': {
                background: hasChanges ? 'linear-gradient(135deg, #388e3c 0%, #4caf50 100%)' : 'rgba(255, 255, 255, 0.1)',
              },
              color: 'white',
            }}
          >
            Save Changes
          </Button>
        </Box>
      </Box>

      {hasChanges && (
        <Alert severity="info" sx={{ mb: 3, backgroundColor: 'rgba(33, 150, 243, 0.1)', color: 'white' }}>
          You have unsaved changes. Don&apos;t forget to save!
        </Alert>
      )}

      <Grid container spacing={3} sx={{ flexGrow: 1 }}>
        {/* Voice Settings */}
        <Grid item xs={12} md={6}>
          <Card sx={{
            background: 'rgba(10, 10, 10, 0.8)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: 3,
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.2)',
            height: '100%',
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <VolumeUpIcon sx={{ color: '#4caf50' }} />
                <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                  Voice Settings
                </Typography>
              </Box>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.voiceEnabled}
                    onChange={(e) => handleSettingChange('voiceEnabled', e.target.checked)}
                    color="primary"
                  />
                }
                label={<Typography sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>Enable Voice Input</Typography>}
                sx={{ mb: 2 }}
              />

              <Typography variant="subtitle2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                Voice Volume: {Math.round(settings.voiceVolume * 100)}%
              </Typography>
              <Slider
                value={settings.voiceVolume}
                onChange={(_, value) => handleSettingChange('voiceVolume', value)}
                min={0}
                max={1}
                step={0.1}
                sx={{ mb: 2 }}
              />

              <Typography variant="subtitle2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                Voice Speed: {settings.voiceSpeed}x
              </Typography>
              <Slider
                value={settings.voiceSpeed}
                onChange={(_, value) => handleSettingChange('voiceSpeed', value)}
                min={0.5}
                max={2}
                step={0.1}
                sx={{ mb: 2 }}
              />

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Language</InputLabel>
                <Select
                  value={settings.voiceLanguage}
                  onChange={(e) => handleSettingChange('voiceLanguage', e.target.value)}
                  sx={{
                    color: 'white',
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'rgba(255, 255, 255, 0.3)',
                    },
                    '&:hover .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'rgba(255, 255, 255, 0.5)',
                    },
                  }}
                >
                  <MenuItem value="en-US">English (US)</MenuItem>
                  <MenuItem value="en-GB">English (UK)</MenuItem>
                  <MenuItem value="es-ES">Spanish</MenuItem>
                  <MenuItem value="fr-FR">French</MenuItem>
                  <MenuItem value="de-DE">German</MenuItem>
                </Select>
              </FormControl>
            </CardContent>
          </Card>
        </Grid>

        {/* Appearance Settings */}
        <Grid item xs={12} md={6}>
          <Card sx={{
            background: 'rgba(10, 10, 10, 0.8)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: 3,
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.2)',
            height: '100%',
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <DarkModeIcon sx={{ color: '#ff9800' }} />
                <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                  Appearance
                </Typography>
              </Box>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Theme</InputLabel>
                <Select
                  value={settings.theme}
                  onChange={(e) => handleSettingChange('theme', e.target.value)}
                  sx={{
                    color: 'white',
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'rgba(255, 255, 255, 0.3)',
                    },
                  }}
                >
                  <MenuItem value="dark">Dark</MenuItem>
                  <MenuItem value="light">Light</MenuItem>
                  <MenuItem value="auto">Auto</MenuItem>
                </Select>
              </FormControl>

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.notifications}
                    onChange={(e) => handleSettingChange('notifications', e.target.checked)}
                    color="primary"
                  />
                }
                label={<Typography sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>Enable Notifications</Typography>}
                sx={{ mb: 2 }}
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.autoSave}
                    onChange={(e) => handleSettingChange('autoSave', e.target.checked)}
                    color="primary"
                  />
                }
                label={<Typography sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>Auto-save Conversations</Typography>}
                sx={{ mb: 2 }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* AI Settings */}
        <Grid item xs={12} md={6}>
          <Card sx={{
            background: 'rgba(10, 10, 10, 0.8)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: 3,
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.2)',
            height: '100%',
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <SpeedIcon sx={{ color: '#2196f3' }} />
                <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                  AI Settings
                </Typography>
              </Box>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Response Speed</InputLabel>
                <Select
                  value={settings.responseSpeed}
                  onChange={(e) => handleSettingChange('responseSpeed', e.target.value)}
                  sx={{
                    color: 'white',
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'rgba(255, 255, 255, 0.3)',
                    },
                  }}
                >
                  <MenuItem value="fast">Fast</MenuItem>
                  <MenuItem value="balanced">Balanced</MenuItem>
                  <MenuItem value="quality">High Quality</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Preferred Model</InputLabel>
                <Select
                  value={settings.modelPreference}
                  onChange={(e) => handleSettingChange('modelPreference', e.target.value)}
                  sx={{
                    color: 'white',
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'rgba(255, 255, 255, 0.3)',
                    },
                  }}
                >
                  <MenuItem value="qwen2.5:7b">Qwen2.5-7B (Fast)</MenuItem>
                  <MenuItem value="qwen2.5:14b">Qwen2.5-14B (Balanced)</MenuItem>
                  <MenuItem value="qwen2.5:72b">Qwen2.5-72B (Quality)</MenuItem>
                  <MenuItem value="mistral:7b">Mistral-7B</MenuItem>
                  <MenuItem value="llama3.2:3b">Llama3.2-3B</MenuItem>
                </Select>
              </FormControl>
            </CardContent>
          </Card>
        </Grid>

        {/* Privacy Settings */}
        <Grid item xs={12} md={6}>
          <Card sx={{
            background: 'rgba(10, 10, 10, 0.8)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: 3,
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.2)',
            height: '100%',
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <SecurityIcon sx={{ color: '#f44336' }} />
                <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                  Privacy & Security
                </Typography>
              </Box>

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.privacyMode}
                    onChange={(e) => handleSettingChange('privacyMode', e.target.checked)}
                    color="primary"
                  />
                }
                label={<Typography sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>Privacy Mode</Typography>}
                sx={{ mb: 2 }}
              />

              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)', mb: 2 }}>
                When enabled, conversations are not stored or logged for privacy protection.
              </Typography>

              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip label="Local Storage" color="primary" size="small" />
                <Chip label="No Tracking" color="success" size="small" />
                <Chip label="Encrypted" color="info" size="small" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SettingsPanel;