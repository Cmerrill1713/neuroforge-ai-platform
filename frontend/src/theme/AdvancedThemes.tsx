'use client'

import { createTheme, Theme } from '@mui/material/styles'

export interface AdvancedThemeConfig {
  name: string
  displayName: string
  description: string
  colors: {
    primary: string
    secondary: string
    background: string
    surface: string
    accent: string
    gradient: string
  }
  effects: {
    blur: boolean
    glow: boolean
    shadows: boolean
    animations: boolean
  }
}

export const themeConfigs: AdvancedThemeConfig[] = [
  {
    name: 'midnight',
    displayName: 'Midnight',
    description: 'Deep dark theme with blue accents',
    colors: {
      primary: '#1976d2',
      secondary: '#9c27b0',
      background: '#0a0a0a',
      surface: 'rgba(255, 255, 255, 0.05)',
      accent: '#00bcd4',
      gradient: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)'
    },
    effects: {
      blur: true,
      glow: true,
      shadows: true,
      animations: true
    }
  },
  {
    name: 'aurora',
    displayName: 'Aurora',
    description: 'Vibrant theme with green and purple accents',
    colors: {
      primary: '#00e676',
      secondary: '#e91e63',
      background: '#0d1117',
      surface: 'rgba(255, 255, 255, 0.08)',
      accent: '#ff6b35',
      gradient: 'linear-gradient(135deg, #0d1117 0%, #1a1a2e 50%, #16213e 100%)'
    },
    effects: {
      blur: true,
      glow: true,
      shadows: true,
      animations: true
    }
  },
  {
    name: 'ocean',
    displayName: 'Ocean',
    description: 'Calming blue theme with ocean vibes',
    colors: {
      primary: '#2196f3',
      secondary: '#00bcd4',
      background: '#0a1929',
      surface: 'rgba(255, 255, 255, 0.06)',
      accent: '#00e5ff',
      gradient: 'linear-gradient(135deg, #0a1929 0%, #001e3c 100%)'
    },
    effects: {
      blur: true,
      glow: false,
      shadows: true,
      animations: true
    }
  },
  {
    name: 'sunset',
    displayName: 'Sunset',
    description: 'Warm orange and red theme',
    colors: {
      primary: '#ff9800',
      secondary: '#f44336',
      background: '#1a0a0a',
      surface: 'rgba(255, 255, 255, 0.05)',
      accent: '#ff5722',
      gradient: 'linear-gradient(135deg, #1a0a0a 0%, #2d1b0a 100%)'
    },
    effects: {
      blur: true,
      glow: true,
      shadows: true,
      animations: true
    }
  },
  {
    name: 'minimal',
    displayName: 'Minimal',
    description: 'Clean and simple theme',
    colors: {
      primary: '#1976d2',
      secondary: '#424242',
      background: '#ffffff',
      surface: 'rgba(0, 0, 0, 0.02)',
      accent: '#1976d2',
      gradient: 'linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)'
    },
    effects: {
      blur: false,
      glow: false,
      shadows: false,
      animations: false
    }
  }
]

export function createAdvancedTheme(config: AdvancedThemeConfig): Theme {
  const isDark = config.name !== 'minimal'
  
  return createTheme({
    palette: {
      mode: isDark ? 'dark' : 'light',
      primary: {
        main: config.colors.primary,
        light: `${config.colors.primary}80`,
        dark: config.colors.primary,
        contrastText: '#fff',
      },
      secondary: {
        main: config.colors.secondary,
        light: `${config.colors.secondary}80`,
        dark: config.colors.secondary,
        contrastText: '#fff',
      },
      background: {
        default: config.colors.background,
        paper: config.colors.surface,
      },
      text: {
        primary: isDark ? '#ffffff' : '#000000',
        secondary: isDark ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.6)',
      },
    },
    typography: {
      fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
      h1: {
        fontSize: '2.5rem',
        fontWeight: 700,
        background: config.colors.gradient,
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        backgroundClip: 'text',
      },
      h2: {
        fontSize: '2rem',
        fontWeight: 600,
      },
      h3: {
        fontSize: '1.75rem',
        fontWeight: 600,
      },
      h4: {
        fontSize: '1.5rem',
        fontWeight: 500,
      },
      h5: {
        fontSize: '1.25rem',
        fontWeight: 500,
      },
      h6: {
        fontSize: '1.125rem',
        fontWeight: 500,
      },
    },
    shape: {
      borderRadius: config.effects.animations ? 12 : 8,
    },
    components: {
      MuiCard: {
        styleOverrides: {
          root: {
            background: config.colors.surface,
            backdropFilter: config.effects.blur ? 'blur(20px)' : 'none',
            border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'}`,
            boxShadow: config.effects.shadows 
              ? (isDark 
                ? '0 8px 32px rgba(0, 0, 0, 0.3)' 
                : '0 8px 32px rgba(0, 0, 0, 0.1)')
              : 'none',
            transition: config.effects.animations 
              ? 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
              : 'none',
            '&:hover': config.effects.animations ? {
              transform: 'translateY(-2px)',
              boxShadow: isDark
                ? '0 12px 40px rgba(0, 0, 0, 0.4)'
                : '0 12px 40px rgba(0, 0, 0, 0.15)',
            } : {},
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            textTransform: 'none',
            fontWeight: 500,
            transition: config.effects.animations 
              ? 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
              : 'none',
            '&:hover': config.effects.animations ? {
              transform: 'translateY(-1px)',
              boxShadow: `0 6px 20px ${config.colors.primary}40`,
            } : {},
          },
          contained: {
            background: config.colors.gradient,
            boxShadow: config.effects.shadows ? '0 4px 14px rgba(0, 0, 0, 0.1)' : 'none',
            '&:hover': {
              background: config.colors.gradient,
              filter: 'brightness(1.1)',
            },
          },
        },
      },
      MuiIconButton: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            transition: config.effects.animations 
              ? 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
              : 'none',
            '&:hover': config.effects.animations ? {
              transform: 'scale(1.05)',
              backgroundColor: `${config.colors.primary}20`,
            } : {},
          },
        },
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            background: config.colors.surface,
            backdropFilter: config.effects.blur ? 'blur(20px)' : 'none',
            borderBottom: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'}`,
            boxShadow: config.effects.shadows ? 'none' : 'none',
          },
        },
      },
      MuiDrawer: {
        styleOverrides: {
          paper: {
            background: config.colors.surface,
            backdropFilter: config.effects.blur ? 'blur(20px)' : 'none',
            border: `1px solid ${isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'}`,
          },
        },
      },
    },
  })
}

export function getThemeByName(name: string): Theme {
  const config = themeConfigs.find(t => t.name === name) || themeConfigs[0]
  return createAdvancedTheme(config)
}

export function getDefaultTheme(): Theme {
  return createAdvancedTheme(themeConfigs[0])
}
