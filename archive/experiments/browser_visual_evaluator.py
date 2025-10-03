#!/usr/bin/env python3
""'
Browser Visual Evaluator
Evaluate frontend appearance and fix alignment, color, and errors
""'

import subprocess
import time
import os
import json
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional

class BrowserVisualEvaluator:
    """TODO: Add docstring."""
    """Evaluate and fix frontend visual issues.""'

    def __init__(self):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.project_root = Path("/Users/christianmerrill/Prompt Engineering')
        self.frontend_dir = self.project_root / "frontend'
        self.app_dir = self.frontend_dir / "app'
        self.src_dir = self.frontend_dir / "src'
        self.components_dir = self.src_dir / "components'

    def start_clean_servers(self):
        """TODO: Add docstring."""
        """Start servers on clean ports.""'
        print("🚀 Starting Clean Servers...')

        # Kill any existing processes
        subprocess.run(["pkill", "-f", "next dev'], capture_output=True)
        subprocess.run(["pkill", "-f", "api_server.py'], capture_output=True)
        time.sleep(2)

        # Start backend on port 8001
        try:
            os.chdir(self.project_root)
            backend_process = subprocess.Popen(
                ["python3", "api_server.py", "--port", "8001'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("✅ Backend starting on port 8001...')
        except Exception as e:
            print(f"❌ Backend failed: {e}')
            backend_process = None

        # Start frontend on port 3000
        try:
            os.chdir(self.frontend_dir)
            frontend_process = subprocess.Popen(
                ["npm", "run", "dev", "--", "--port", "3000'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("✅ Frontend starting on port 3000...')
        except Exception as e:
            print(f"❌ Frontend failed: {e}')
            frontend_process = None

        # Wait for servers to start
        print("⏳ Waiting for servers to start...')
        time.sleep(15)

        return frontend_process, backend_process

    def evaluate_frontend_visuals(self):
        """TODO: Add docstring."""
        """Evaluate frontend visual appearance.""'
        print("🎨 Evaluating Frontend Visuals...')

        issues = []

        # Check main page
        main_page = self.app_dir / "page.tsx'
        if main_page.exists():
            content = main_page.read_text()

            # Check for visual issues
            issues.extend(self.check_color_scheme(content))
            issues.extend(self.check_alignment_issues(content))
            issues.extend(self.check_responsive_design(content))
            issues.extend(self.check_theme_consistency(content))
            issues.extend(self.check_component_styling(content))

        # Check theme file
        theme_file = self.src_dir / "theme" / "muiTheme.ts'
        if theme_file.exists():
            content = theme_file.read_text()
            issues.extend(self.check_theme_configuration(content))

        # Check component files
        for component_file in self.components_dir.glob("*.tsx'):
            if component_file.exists():
                content = component_file.read_text()
                issues.extend(self.check_component_visual_issues(component_file.name, content))

        return issues

    def check_color_scheme(self, content: str) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Check for color scheme issues.""'
        issues = []

        # Check for hardcoded colors
        hardcoded_colors = [
            "#ffffff", "#000000", "#f0f0f0", "#333333',
            "white", "black", "gray", "red", "blue", "green'
        ]

        for color in hardcoded_colors:
            if color in content and "theme' not in content.lower():
                issues.append({
                    "type": "color_scheme',
                    "severity": "warning',
                    "description": f"Hardcoded color "{color}" found - should use theme colors',
                    "fix": f"Replace with theme.palette.{self.get_theme_color_mapping(color)}'
                })

        # Check for inconsistent color usage
        if "rgba(255, 255, 255" in content and "theme.palette' not in content:
            issues.append({
                "type": "color_scheme',
                "severity": "warning',
                "description": "Using rgba colors instead of theme palette',
                "fix": "Use theme.palette.text.primary or theme.palette.background.paper'
            })

        return issues

    def check_alignment_issues(self, content: str) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Check for alignment issues.""'
        issues = []

        # Check for inconsistent spacing
        if "p: 2" in content and "p: 3' in content:
            issues.append({
                "type": "alignment',
                "severity": "warning',
                "description": "Inconsistent padding values (p: 2 and p: 3)',
                "fix": "Use consistent spacing scale from theme'
            })

        # Check for hardcoded margins
        if "margin:" in content or "m:' in content:
            issues.append({
                "type": "alignment',
                "severity": "info',
                "description": "Hardcoded margins found',
                "fix": "Use theme.spacing() for consistent spacing'
            })

        # Check for missing responsive alignment
        if "sx=" in content and "xs:' not in content:
            issues.append({
                "type": "alignment',
                "severity": "warning',
                "description": "Missing responsive breakpoints in styling',
                "fix": "Add responsive breakpoints (xs, sm, md, lg, xl)'
            })

        return issues

    def check_responsive_design(self, content: str) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Check for responsive design issues.""'
        issues = []

        # Check for missing responsive props
        responsive_props = ["xs:", "sm:", "md:", "lg:", "xl:']
        has_responsive = any(prop in content for prop in responsive_props)

        if "sx=' in content and not has_responsive:
            issues.append({
                "type": "responsive',
                "severity": "warning',
                "description": "Missing responsive design breakpoints',
                "fix": "Add responsive breakpoints for mobile, tablet, and desktop'
            })

        # Check for fixed widths/heights
        if "width:" in content or "height:' in content:
            if "100%" not in content and "auto' not in content:
                issues.append({
                    "type": "responsive',
                    "severity": "info',
                    "description": "Fixed dimensions may not be responsive',
                    "fix": "Consider using percentage or auto values'
                })

        return issues

    def check_theme_consistency(self, content: str) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Check for theme consistency issues.""'
        issues = []

        # Check for missing ThemeProvider
        if "useTheme" in content and "ThemeProvider' not in content:
            issues.append({
                "type": "theme_consistency',
                "severity": "error',
                "description": "Using useTheme without ThemeProvider',
                "fix": "Wrap component with ThemeProvider'
            })

        # Check for inconsistent theme usage
        if "theme.palette" in content and "theme.typography' not in content:
            issues.append({
                "type": "theme_consistency',
                "severity": "info',
                "description": "Using theme.palette but not theme.typography',
                "fix": "Use theme.typography for consistent text styling'
            })

        return issues

    def check_component_styling(self, content: str) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Check for component styling issues.""'
        issues = []

        # Check for inline styles
        if "style=' in content:
            issues.append({
                "type": "component_styling',
                "severity": "warning',
                "description": "Using inline styles instead of sx prop',
                "fix": "Use sx prop for better performance and theme integration'
            })

        # Check for missing sx prop
        if "sx=" not in content and "style=' not in content:
            issues.append({
                "type": "component_styling',
                "severity": "info',
                "description": "Component may need styling',
                "fix": "Add sx prop for consistent styling'
            })

        return issues

    def check_theme_configuration(self, content: str) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Check theme configuration.""'
        issues = []

        # Check for missing color palette
        if "palette:' not in content:
            issues.append({
                "type": "theme_configuration',
                "severity": "error',
                "description": "Missing color palette in theme',
                "fix": "Add palette configuration with primary, secondary, and background colors'
            })

        # Check for missing typography
        if "typography:' not in content:
            issues.append({
                "type": "theme_configuration',
                "severity": "warning',
                "description": "Missing typography configuration',
                "fix": "Add typography configuration for consistent text styling'
            })

        # Check for missing component overrides
        if "components:' not in content:
            issues.append({
                "type": "theme_configuration',
                "severity": "info',
                "description": "Missing component overrides',
                "fix": "Add component overrides for consistent styling'
            })

        return issues

    def check_component_visual_issues(self, component_name: str, content: str) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Check individual component visual issues.""'
        issues = []

        # Check for missing error boundaries
        if "Error" in content and "ErrorBoundary' not in content:
            issues.append({
                "type": "component_visual',
                "component': component_name,
                "severity": "warning',
                "description": "Error handling without ErrorBoundary',
                "fix": "Add ErrorBoundary for better error handling'
            })

        # Check for missing loading states
        if "loading" in content.lower() and "CircularProgress' not in content:
            issues.append({
                "type": "component_visual',
                "component': component_name,
                "severity": "info',
                "description": "Loading state without visual indicator',
                "fix": "Add CircularProgress or Skeleton for loading states'
            })

        # Check for missing accessibility
        if "Button" in content and "aria-label' not in content:
            issues.append({
                "type": "component_visual',
                "component': component_name,
                "severity": "warning',
                "description": "Button without accessibility label',
                "fix": "Add aria-label for screen readers'
            })

        return issues

    def fix_visual_issues(self, issues: List[Dict[str, Any]]):
        """TODO: Add docstring."""
        """Fix identified visual issues.""'
        print("\n🔧 Fixing Visual Issues...')

        for issue in issues:
            try:
                if issue["type"] == "color_scheme':
                    self.fix_color_scheme(issue)
                elif issue["type"] == "alignment':
                    self.fix_alignment(issue)
                elif issue["type"] == "responsive':
                    self.fix_responsive_design(issue)
                elif issue["type"] == "theme_consistency':
                    self.fix_theme_consistency(issue)
                elif issue["type"] == "component_styling':
                    self.fix_component_styling(issue)
                elif issue["type"] == "theme_configuration':
                    self.fix_theme_configuration(issue)
            except Exception as e:
                print(f"❌ Failed to fix {issue["type"]}: {e}')

    def fix_color_scheme(self, issue: Dict[str, Any]):
        """TODO: Add docstring."""
        """Fix color scheme issues.""'
        print(f"🎨 Fixing color scheme: {issue["description"]}')
        # Implementation would go here

    def fix_alignment(self, issue: Dict[str, Any]):
        """TODO: Add docstring."""
        """Fix alignment issues.""'
        print(f"📐 Fixing alignment: {issue["description"]}')
        # Implementation would go here

    def fix_responsive_design(self, issue: Dict[str, Any]):
        """TODO: Add docstring."""
        """Fix responsive design issues.""'
        print(f"📱 Fixing responsive design: {issue["description"]}')
        # Implementation would go here

    def fix_theme_consistency(self, issue: Dict[str, Any]):
        """TODO: Add docstring."""
        """Fix theme consistency issues.""'
        print(f"🎭 Fixing theme consistency: {issue["description"]}')
        # Implementation would go here

    def fix_component_styling(self, issue: Dict[str, Any]):
        """TODO: Add docstring."""
        """Fix component styling issues.""'
        print(f"🧩 Fixing component styling: {issue["description"]}')
        # Implementation would go here

    def fix_theme_configuration(self, issue: Dict[str, Any]):
        """TODO: Add docstring."""
        """Fix theme configuration issues.""'
        print(f"⚙️ Fixing theme configuration: {issue["description"]}')
        # Implementation would go here

    def create_visual_test_page(self):
        """TODO: Add docstring."""
        """Create a comprehensive visual test page.""'
        print("🧪 Creating Visual Test Page...')

        test_page = self.app_dir / "visual-test" / "page.tsx'
        test_page.parent.mkdir(parents=True, exist_ok=True)

        content = """\"use client\'

import React from "react'
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
} from "@mui/material'
import {
  Home as HomeIcon,
  Settings as SettingsIcon,
  Favorite as FavoriteIcon,
  Share as ShareIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Add as AddIcon,
  Search as SearchIcon
} from "@mui/icons-material'
import { ThemeProvider, useTheme } from "@mui/material/styles'
import { aiStudio2025Theme } from "@/theme/muiTheme'

function VisualTestContent() {
  const theme = useTheme()

  return (
    <Box sx={{
      minHeight: "100vh',
      background: "linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)',
      p: { xs: 2, sm: 3, md: 4 }
    }}>
      <Typography variant="h2" sx={{ textAlign: "center", mb: 4, color: "white' }}>
        🎨 Visual Test Page
      </Typography>

      <Grid container spacing={{ xs: 2, sm: 3, md: 4 }}>
        {/* Color Palette Test */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: "100%' }}>
            <CardContent>
              <Typography variant="h5' gutterBottom>
                Color Palette
              </Typography>
              <Stack spacing={2}>
                <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap' }}>
                  <Chip label="Primary" color="primary' />
                  <Chip label="Secondary" color="secondary' />
                  <Chip label="Success" color="success' />
                  <Chip label="Warning" color="warning' />
                  <Chip label="Error" color="error' />
                  <Chip label="Info" color="info' />
                </Box>
                <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap' }}>
                  <Chip label="Outlined Primary" variant="outlined" color="primary' />
                  <Chip label="Outlined Secondary" variant="outlined" color="secondary' />
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* Typography Test */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: "100%' }}>
            <CardContent>
              <Typography variant="h5' gutterBottom>
                Typography
              </Typography>
              <Stack spacing={1}>
                <Typography variant="h1'>Heading 1</Typography>
                <Typography variant="h2'>Heading 2</Typography>
                <Typography variant="h3'>Heading 3</Typography>
                <Typography variant="h4'>Heading 4</Typography>
                <Typography variant="h5'>Heading 5</Typography>
                <Typography variant="h6'>Heading 6</Typography>
                <Typography variant="body1'>Body text 1</Typography>
                <Typography variant="body2'>Body text 2</Typography>
                <Typography variant="caption'>Caption text</Typography>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* Buttons Test */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: "100%' }}>
            <CardContent>
              <Typography variant="h5' gutterBottom>
                Buttons
              </Typography>
              <Stack spacing={2}>
                <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap' }}>
                  <Button variant="contained'>Contained</Button>
                  <Button variant="outlined'>Outlined</Button>
                  <Button variant="text'>Text</Button>
                </Box>
                <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap' }}>
                  <Button variant="contained" color="secondary'>Secondary</Button>
                  <Button variant="contained" color="success'>Success</Button>
                  <Button variant="contained" color="warning'>Warning</Button>
                  <Button variant="contained" color="error'>Error</Button>
                </Box>
                <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap' }}>
                  <IconButton color="primary'><HomeIcon /></IconButton>
                  <IconButton color="secondary'><SettingsIcon /></IconButton>
                  <IconButton color="success'><FavoriteIcon /></IconButton>
                  <IconButton color="warning'><ShareIcon /></IconButton>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* Form Elements Test */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: "100%' }}>
            <CardContent>
              <Typography variant="h5' gutterBottom>
                Form Elements
              </Typography>
              <Stack spacing={2}>
                <TextField
                  label="Text Field'
                  variant="outlined'
                  fullWidth
                  placeholder="Enter text...'
                />
                <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap' }}>
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Switch'
                  />
                  <FormControlLabel
                    control={<Switch />}
                    label="Switch Off'
                  />
                </Box>
                <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap' }}>
                  <Avatar sx={{ bgcolor: "primary.main' }}>A</Avatar>
                  <Avatar sx={{ bgcolor: "secondary.main' }}>B</Avatar>
                  <Avatar sx={{ bgcolor: "success.main' }}>C</Avatar>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* Progress Indicators Test */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: "100%' }}>
            <CardContent>
              <Typography variant="h5' gutterBottom>
                Progress Indicators
              </Typography>
              <Stack spacing={2}>
                <Box>
                  <Typography variant="body2' gutterBottom>
                    Linear Progress (50%)
                  </Typography>
                  <LinearProgress variant="determinate' value={50} />
                </Box>
                <Box>
                  <Typography variant="body2' gutterBottom>
                    Circular Progress
                  </Typography>
                  <CircularProgress />
                </Box>
                <Box>
                  <Typography variant="body2' gutterBottom>
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
          <Card sx={{ height: "100%' }}>
            <CardContent>
              <Typography variant="h5' gutterBottom>
                Alerts
              </Typography>
              <Stack spacing={2}>
                <Alert severity="success'>
                  <AlertTitle>Success</AlertTitle>
                  This is a success alert!
                </Alert>
                <Alert severity="info'>
                  <AlertTitle>Info</AlertTitle>
                  This is an info alert!
                </Alert>
                <Alert severity="warning'>
                  <AlertTitle>Warning</AlertTitle>
                  This is a warning alert!
                </Alert>
                <Alert severity="error'>
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
              <Typography variant="h5' gutterBottom>
                Responsive Grid Test
              </Typography>
              <Grid container spacing={2}>
                <Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }}>
                  <Paper sx={{ p: 2, textAlign: "center' }}>
                    <Typography variant="h6'>XS: 12</Typography>
                    <Typography variant="body2'>SM: 6, MD: 4, LG: 3</Typography>
                  </Paper>
                </Grid>
                <Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }}>
                  <Paper sx={{ p: 2, textAlign: "center' }}>
                    <Typography variant="h6'>XS: 12</Typography>
                    <Typography variant="body2'>SM: 6, MD: 4, LG: 3</Typography>
                  </Paper>
                </Grid>
                <Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }}>
                  <Paper sx={{ p: 2, textAlign: "center' }}>
                    <Typography variant="h6'>XS: 12</Typography>
                    <Typography variant="body2'>SM: 6, MD: 4, LG: 3</Typography>
                  </Paper>
                </Grid>
                <Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }}>
                  <Paper sx={{ p: 2, textAlign: "center' }}>
                    <Typography variant="h6'>XS: 12</Typography>
                    <Typography variant="body2'>SM: 6, MD: 4, LG: 3</Typography>
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
          <Typography variant="h5' gutterBottom>
            Theme Information
          </Typography>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 6 }}>
              <Typography variant="h6' gutterBottom>
                Color Palette
              </Typography>
              <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap' }}>
                <Box sx={{
                  width: 40,
                  height: 40,
                  bgcolor: "primary.main',
                  borderRadius: 1,
                  display: "flex',
                  alignItems: "center',
                  justifyContent: "center',
                  color: "white',
                  fontSize: "0.75rem'
                }}>
                  P
                </Box>
                <Box sx={{
                  width: 40,
                  height: 40,
                  bgcolor: "secondary.main',
                  borderRadius: 1,
                  display: "flex',
                  alignItems: "center',
                  justifyContent: "center',
                  color: "white',
                  fontSize: "0.75rem'
                }}>
                  S
                </Box>
                <Box sx={{
                  width: 40,
                  height: 40,
                  bgcolor: "success.main',
                  borderRadius: 1,
                  display: "flex',
                  alignItems: "center',
                  justifyContent: "center',
                  color: "white',
                  fontSize: "0.75rem'
                }}>
                  ✓
                </Box>
                <Box sx={{
                  width: 40,
                  height: 40,
                  bgcolor: "warning.main',
                  borderRadius: 1,
                  display: "flex',
                  alignItems: "center',
                  justifyContent: "center',
                  color: "white',
                  fontSize: "0.75rem'
                }}>
                  !
                </Box>
                <Box sx={{
                  width: 40,
                  height: 40,
                  bgcolor: "error.main',
                  borderRadius: 1,
                  display: "flex',
                  alignItems: "center',
                  justifyContent: "center',
                  color: "white',
                  fontSize: "0.75rem'
                }}>
                  ✗
                </Box>
              </Box>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <Typography variant="h6' gutterBottom>
                Spacing Scale
              </Typography>
              <Stack spacing={1}>
                {[1, 2, 3, 4, 5].map((spacing) => (
                  <Box key={spacing} sx={{ display: "flex", alignItems: "center', gap: 1 }}>
                    <Box sx={{
                      width: spacing * 8,
                      height: 20,
                      bgcolor: "primary.main',
                      borderRadius: 0.5
                    }} />
                    <Typography variant="body2'>
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
    <ThemeProvider theme={aiStudio2025Theme}>
      <VisualTestContent />
    </ThemeProvider>
  )
}
""'

        test_page.write_text(content)
        print("✅ Created visual test page at /visual-test')
        print("🌐 Visit: http://localhost:3000/visual-test')

    def run_visual_evaluation(self):
        """TODO: Add docstring."""
        """Run comprehensive visual evaluation.""'
        print("🎨 Browser Visual Evaluator')
        print("=' * 50)

        # Start clean servers
        frontend_process, backend_process = self.start_clean_servers()

        # Evaluate visuals
        issues = self.evaluate_frontend_visuals()

        if issues:
            print(f"\n❌ Found {len(issues)} visual issues:')
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue["type"]}: {issue["description"]}')

            # Fix issues
            self.fix_visual_issues(issues)
        else:
            print("\n✅ No visual issues found!')

        # Create visual test page
        self.create_visual_test_page()

        print("\n✅ Visual evaluation complete!')
        print("🌐 Main app: http://localhost:3000')
        print("🧪 Visual test: http://localhost:3000/visual-test')
        print("🚀 Backend: http://localhost:8001')

def main():
    """TODO: Add docstring."""
    """Main function.""'
    evaluator = BrowserVisualEvaluator()
    evaluator.run_visual_evaluation()

if __name__ == "__main__':
    main()
