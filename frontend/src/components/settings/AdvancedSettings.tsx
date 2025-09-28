'use client'

import React from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Switch,
  Slider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Divider,
  Grid,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert
} from '@mui/material'
import {
  Settings as SettingsIcon,
  Palette as PaletteIcon,
  Speed as SpeedIcon,
  Keyboard as KeyboardIcon,
  Save as SaveIcon,
  Restore as RestoreIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Info as InfoIcon
} from '@mui/icons-material'
import { motion } from 'framer-motion'
import { useLayoutPersistence } from '../../hooks/useLayoutPersistence'
import { useKeyboardNavigation } from '../../hooks/useKeyboardNavigation'
import { themeConfigs } from '../../theme/AdvancedThemes'

interface AdvancedSettingsProps {
  open: boolean
  onClose: () => void
}

export function AdvancedSettings({ open, onClose }: AdvancedSettingsProps) {
  const {
    preferences,
    updatePreference,
    resetPreferences,
    exportPreferences,
    importPreferences
  } = useLayoutPersistence()

  const [importDialogOpen, setImportDialogOpen] = React.useState(false)
  const [fileInputRef, setFileInputRef] = React.useState<HTMLInputElement | null>(null)

  const handleThemeChange = (themeName: string) => {
    updatePreference('theme', themeName as any)
  }

  const handleAnimationSpeedChange = (speed: 'slow' | 'normal' | 'fast') => {
    updatePreference('animationSpeed', speed)
  }

  const handleLayoutDensityChange = (density: 'compact' | 'comfortable' | 'spacious') => {
    updatePreference('layoutDensity', density)
  }

  const handleImportFile = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      try {
        await importPreferences(file)
        setImportDialogOpen(false)
      } catch (error) {
        console.error('Failed to import preferences:', error)
      }
    }
  }

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          background: 'rgba(30, 30, 30, 0.95)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <SettingsIcon />
          <Typography variant="h6">Advanced Settings</Typography>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Grid container spacing={3}>
          {/* Theme Settings */}
          <div style={{ width: '100%', padding: '8px' }}>
            <Card sx={{ background: 'rgba(20, 20, 20, 0.8)' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <PaletteIcon />
                  <Typography variant="h6">Theme & Appearance</Typography>
                </Box>
                
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Theme</InputLabel>
                  <Select
                    value={preferences.theme}
                    onChange={(e) => handleThemeChange(e.target.value)}
                    label="Theme"
                  >
                    {themeConfigs.map((theme) => (
                      <MenuItem key={theme.name} value={theme.name}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <Box
                            sx={{
                              width: 20,
                              height: 20,
                              borderRadius: '50%',
                              background: theme.colors.gradient,
                            }}
                          />
                          <Box>
                            <Typography variant="body1">{theme.displayName}</Typography>
                            <Typography variant="caption" color="text.secondary">
                              {theme.description}
                            </Typography>
                          </Box>
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Typography>Dark Mode</Typography>
                  <Switch
                    checked={preferences.darkMode}
                    onChange={(e) => updatePreference('darkMode', e.target.checked)}
                  />
                </Box>
              </CardContent>
            </Card>
          </div>

          {/* Layout Settings */}
          <div style={{ width: '100%', padding: '8px' }}>
            <Card sx={{ background: 'rgba(20, 20, 20, 0.8)' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <SpeedIcon />
                  <Typography variant="h6">Layout & Performance</Typography>
                </Box>

                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Layout Density</InputLabel>
                  <Select
                    value={preferences.layoutDensity}
                    onChange={(e) => handleLayoutDensityChange(e.target.value as any)}
                    label="Layout Density"
                  >
                    <MenuItem value="compact">Compact</MenuItem>
                    <MenuItem value="comfortable">Comfortable</MenuItem>
                    <MenuItem value="spacious">Spacious</MenuItem>
                  </Select>
                </FormControl>

                <Box sx={{ mb: 2 }}>
                  <Typography gutterBottom>Animation Speed</Typography>
                  <Slider
                    value={preferences.animationSpeed === 'slow' ? 1 : preferences.animationSpeed === 'normal' ? 2 : 3}
                    onChange={(_, value) => {
                      const speed = value === 1 ? 'slow' : value === 2 ? 'normal' : 'fast'
                      handleAnimationSpeedChange(speed as any)
                    }}
                    min={1}
                    max={3}
                    step={1}
                    marks={[
                      { value: 1, label: 'Slow' },
                      { value: 2, label: 'Normal' },
                      { value: 3, label: 'Fast' },
                    ]}
                  />
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Typography>Sidebar Open by Default</Typography>
                  <Switch
                    checked={preferences.sidebarOpen}
                    onChange={(e) => updatePreference('sidebarOpen', e.target.checked)}
                  />
                </Box>
              </CardContent>
            </Card>
          </div>

          {/* Accessibility Settings */}
          <div style={{ width: '100%', padding: '8px' }}>
            <Card sx={{ background: 'rgba(20, 20, 20, 0.8)' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <KeyboardIcon />
                  <Typography variant="h6">Accessibility & Controls</Typography>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                  <Typography>Voice Input</Typography>
                  <Switch
                    checked={preferences.isVoiceEnabled}
                    onChange={(e) => updatePreference('isVoiceEnabled', e.target.checked)}
                  />
                </Box>

                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="body2">
                    Keyboard shortcuts: Arrow keys to navigate, Enter to select, Escape to close
                  </Typography>
                </Alert>
              </CardContent>
            </Card>
          </div>

          {/* Data Management */}
          <div style={{ width: '100%', padding: '8px' }}>
            <Card sx={{ background: 'rgba(20, 20, 20, 0.8)' }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Data Management
                </Typography>

                <Grid container spacing={2}>
                  <div style={{ width: '100%', padding: '8px' }}>
                    <Button
                      variant="outlined"
                      startIcon={<DownloadIcon />}
                      onClick={exportPreferences}
                      fullWidth
                    >
                      Export Settings
                    </Button>
                  </div>
                  <div style={{ width: '100%', padding: '8px' }}>
                    <Button
                      variant="outlined"
                      startIcon={<UploadIcon />}
                      onClick={() => setImportDialogOpen(true)}
                      fullWidth
                    >
                      Import Settings
                    </Button>
                  </div>
                  <div style={{ width: '100%', padding: '8px' }}>
                    <Button
                      variant="outlined"
                      color="warning"
                      startIcon={<RestoreIcon />}
                      onClick={resetPreferences}
                      fullWidth
                    >
                      Reset to Defaults
                    </Button>
                  </div>
                </Grid>
              </CardContent>
            </Card>
          </div>
        </Grid>

        {/* Import Dialog */}
        <Dialog open={importDialogOpen} onClose={() => setImportDialogOpen(false)}>
          <DialogTitle>Import Settings</DialogTitle>
          <DialogContent>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Select a settings file to import your preferences.
            </Typography>
            <input
              ref={setFileInputRef}
              type="file"
              accept=".json"
              onChange={handleImportFile}
              style={{ display: 'none' }}
            />
            <Button
              variant="outlined"
              onClick={() => fileInputRef?.click()}
              fullWidth
            >
              Choose File
            </Button>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setImportDialogOpen(false)}>Cancel</Button>
          </DialogActions>
        </Dialog>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Close</Button>
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          onClick={onClose}
        >
          Save Changes
        </Button>
      </DialogActions>
    </Dialog>
  )
}
