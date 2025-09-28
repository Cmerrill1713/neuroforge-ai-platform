"use client"

import React from 'react'
import {
  Box,
  Typography,
  Button,
  Paper,
  Card,
  CardContent,
  Grid,
  Stack,
  Chip,
  Avatar,
  IconButton,
  TextField,
  Switch,
  FormControlLabel,
  LinearProgress,
  CircularProgress,
  Alert,
  AlertTitle
} from '@mui/material'
import {
  Home as HomeIcon,
  Settings as SettingsIcon,
  Favorite as FavoriteIcon,
  Share as ShareIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Add as AddIcon,
  Search as SearchIcon
} from '@mui/icons-material'
import { ThemeProvider, useTheme } from '@mui/material/styles'
import { aiStudioEnhancedTheme } from '@/theme/muiTheme'

function VisualTestContent() {
  const theme = useTheme()
  
  return (
    <Box sx={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)',
      p: { xs: 2, sm: 3, md: 4 }
    }}>
      <Typography variant="h2" sx={{ textAlign: 'center', mb: 4, color: 'white' }}>
        🎨 Visual Test Page
      </Typography>
      
      <Grid container spacing={{ xs: 2, sm: 3, md: 4 }}>
        {/* Color Palette Test */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Color Palette
              </Typography>
              <Stack spacing={2}>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip label="Primary" color="primary" />
                  <Chip label="Secondary" color="secondary" />
                  <Chip label="Success" color="success" />
                  <Chip label="Warning" color="warning" />
                  <Chip label="Error" color="error" />
                  <Chip label="Info" color="info" />
                </Box>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip label="Outlined Primary" variant="outlined" color="primary" />
                  <Chip label="Outlined Secondary" variant="outlined" color="secondary" />
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Typography Test */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Typography
              </Typography>
              <Stack spacing={1}>
                <Typography variant="h1">Heading 1</Typography>
                <Typography variant="h2">Heading 2</Typography>
                <Typography variant="h3">Heading 3</Typography>
                <Typography variant="h4">Heading 4</Typography>
                <Typography variant="h5">Heading 5</Typography>
                <Typography variant="h6">Heading 6</Typography>
                <Typography variant="body1">Body text 1</Typography>
                <Typography variant="body2">Body text 2</Typography>
                <Typography variant="caption">Caption text</Typography>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Buttons Test */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Buttons
              </Typography>
              <Stack spacing={2}>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Button variant="contained">Contained</Button>
                  <Button variant="outlined">Outlined</Button>
                  <Button variant="text">Text</Button>
                </Box>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Button variant="contained" color="secondary">Secondary</Button>
                  <Button variant="contained" color="success">Success</Button>
                  <Button variant="contained" color="warning">Warning</Button>
                  <Button variant="contained" color="error">Error</Button>
                </Box>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <IconButton color="primary"><HomeIcon /></IconButton>
                  <IconButton color="secondary"><SettingsIcon /></IconButton>
                  <IconButton color="success"><FavoriteIcon /></IconButton>
                  <IconButton color="warning"><ShareIcon /></IconButton>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Form Elements Test */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Form Elements
              </Typography>
              <Stack spacing={2}>
                <TextField 
                  label="Text Field" 
                  variant="outlined" 
                  fullWidth 
                  placeholder="Enter text..."
                />
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <FormControlLabel 
                    control={<Switch defaultChecked />} 
                    label="Switch" 
                  />
                  <FormControlLabel 
                    control={<Switch />} 
                    label="Switch Off" 
                  />
                </Box>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Avatar sx={{ bgcolor: 'primary.main' }}>A</Avatar>
                  <Avatar sx={{ bgcolor: 'secondary.main' }}>B</Avatar>
                  <Avatar sx={{ bgcolor: 'success.main' }}>C</Avatar>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Progress Indicators Test */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Progress Indicators
              </Typography>
              <Stack spacing={2}>
                <Box>
                  <Typography variant="body2" gutterBottom>
                    Linear Progress (50%)
                  </Typography>
                  <LinearProgress variant="determinate" value={50} />
                </Box>
                <Box>
                  <Typography variant="body2" gutterBottom>
                    Circular Progress
                  </Typography>
                  <CircularProgress />
                </Box>
                <Box>
                  <Typography variant="body2" gutterBottom>
                    Indeterminate Progress
                  </Typography>
                  <LinearProgress />
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Alerts Test */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Alerts
              </Typography>
              <Stack spacing={2}>
                <Alert severity="success">
                  <AlertTitle>Success</AlertTitle>
                  This is a success alert!
                </Alert>
                <Alert severity="info">
                  <AlertTitle>Info</AlertTitle>
                  This is an info alert!
                </Alert>
                <Alert severity="warning">
                  <AlertTitle>Warning</AlertTitle>
                  This is a warning alert!
                </Alert>
                <Alert severity="error">
                  <AlertTitle>Error</AlertTitle>
                  This is an error alert!
                </Alert>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Responsive Grid Test */}
        <Grid size={{ xs: 12 }}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Responsive Grid Test
              </Typography>
              <Grid container spacing={2}>
                <Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6">XS: 12</Typography>
                    <Typography variant="body2">SM: 6, MD: 4, LG: 3</Typography>
                  </Paper>
                </Grid>
                <Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6">XS: 12</Typography>
                    <Typography variant="body2">SM: 6, MD: 4, LG: 3</Typography>
                  </Paper>
                </Grid>
                <Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6">XS: 12</Typography>
                    <Typography variant="body2">SM: 6, MD: 4, LG: 3</Typography>
                  </Paper>
                </Grid>
                <Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h6">XS: 12</Typography>
                    <Typography variant="body2">SM: 6, MD: 4, LG: 3</Typography>
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* Theme Information */}
      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Theme Information
          </Typography>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 6 }}>
              <Typography variant="h6" gutterBottom>
                Color Palette
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Box sx={{ 
                  width: 40, 
                  height: 40, 
                  bgcolor: 'primary.main', 
                  borderRadius: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '0.75rem'
                }}>
                  P
                </Box>
                <Box sx={{ 
                  width: 40, 
                  height: 40, 
                  bgcolor: 'secondary.main', 
                  borderRadius: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '0.75rem'
                }}>
                  S
                </Box>
                <Box sx={{ 
                  width: 40, 
                  height: 40, 
                  bgcolor: 'success.main', 
                  borderRadius: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '0.75rem'
                }}>
                  ✓
                </Box>
                <Box sx={{ 
                  width: 40, 
                  height: 40, 
                  bgcolor: 'warning.main', 
                  borderRadius: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '0.75rem'
                }}>
                  !
                </Box>
                <Box sx={{ 
                  width: 40, 
                  height: 40, 
                  bgcolor: 'error.main', 
                  borderRadius: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '0.75rem'
                }}>
                  ✗
                </Box>
              </Box>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <Typography variant="h6" gutterBottom>
                Spacing Scale
              </Typography>
              <Stack spacing={1}>
                {[1, 2, 3, 4, 5].map((spacing) => (
                  <Box key={spacing} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ 
                      width: spacing * 8, 
                      height: 20, 
                      bgcolor: 'primary.main', 
                      borderRadius: 0.5 
                    }} />
                    <Typography variant="body2">
                      theme.spacing({spacing}) = {spacing * 8}px
                    </Typography>
                  </Box>
                ))}
              </Stack>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  )
}

export default function VisualTestPage() {
  return (
    <ThemeProvider theme={aiStudioEnhancedTheme}>
      <VisualTestContent />
    </ThemeProvider>
  )
}
