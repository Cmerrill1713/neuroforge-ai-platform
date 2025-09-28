'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'
import { ThemeProvider, createTheme, Theme } from '@mui/material/styles'
import { CssBaseline } from '@mui/material'

export interface ThemeCustomization {
  primaryColor: string
  secondaryColor: string
  backgroundColor: string
  surfaceColor: string
  textColor: string
  borderRadius: number
  spacing: number
  fontFamily: string
  fontSize: {
    small: number
    medium: number
    large: number
  }
  shadows: {
    light: string
    medium: string
    heavy: string
  }
  animations: {
    enabled: boolean
    duration: number
    easing: string
  }
}

export const defaultThemeCustomization: ThemeCustomization = {
  primaryColor: '#1976d2',
  secondaryColor: '#dc004e',
  backgroundColor: '#0a0a0a',
  surfaceColor: '#1a1a1a',
  textColor: '#ffffff',
  borderRadius: 8,
  spacing: 8,
  fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  fontSize: {
    small: 12,
    medium: 14,
    large: 16
  },
  shadows: {
    light: '0 2px 8px rgba(0, 0, 0, 0.1)',
    medium: '0 4px 16px rgba(0, 0, 0, 0.2)',
    heavy: '0 8px 32px rgba(0, 0, 0, 0.3)'
  },
  animations: {
    enabled: true,
    duration: 0.3,
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
  }
}

interface ThemeContextType {
  customization: ThemeCustomization
  updateCustomization: (updates: Partial<ThemeCustomization>) => void
  resetToDefault: () => void
  theme: Theme
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export const useThemeCustomization = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useThemeCustomization must be used within a ThemeCustomizationProvider')
  }
  return context
}

const createCustomTheme = (customization: ThemeCustomization): Theme => {
  return createTheme({
    palette: {
      mode: 'dark',
      primary: {
        main: customization.primaryColor,
        light: `${customization.primaryColor}80`,
        dark: `${customization.primaryColor}CC`
      },
      secondary: {
        main: customization.secondaryColor,
        light: `${customization.secondaryColor}80`,
        dark: `${customization.secondaryColor}CC`
      },
      background: {
        default: customization.backgroundColor,
        paper: customization.surfaceColor
      },
      text: {
        primary: customization.textColor,
        secondary: `${customization.textColor}80`
      }
    },
    typography: {
      fontFamily: customization.fontFamily,
      fontSize: customization.fontSize.medium,
      h1: {
        fontSize: customization.fontSize.large * 2.5
      },
      h2: {
        fontSize: customization.fontSize.large * 2
      },
      h3: {
        fontSize: customization.fontSize.large * 1.75
      },
      h4: {
        fontSize: customization.fontSize.large * 1.5
      },
      h5: {
        fontSize: customization.fontSize.large * 1.25
      },
      h6: {
        fontSize: customization.fontSize.large
      },
      body1: {
        fontSize: customization.fontSize.medium
      },
      body2: {
        fontSize: customization.fontSize.small
      }
    },
    shape: {
      borderRadius: customization.borderRadius
    },
    spacing: customization.spacing,
    shadows: [
      'none',
      customization.shadows.light,
      customization.shadows.medium,
      customization.shadows.heavy,
      customization.shadows.heavy,
      customization.shadows.heavy,
      customization.shadows.heavy,
      customization.shadows.heavy,
      customization.shadows.heavy,
      customization.shadows.heavy,
      customization.shadows.heavy,
      customization.shadows.heavy,
      customization.shadows.heavy,
      customization.shadows.heavy,
      customization.shadows.heavy,
      customization.shadows.heavy,
      customization.shadows.heavy,
      customization.shadows.heavy,
      customization.shadows.heavy,
      customization.shadows.heavy,
      customization.shadows.heavy,
      customization.shadows.heavy,
      customization.shadows.heavy,
      customization.shadows.heavy,
      customization.shadows.heavy
    ],
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: customization.borderRadius,
            textTransform: 'none',
            fontWeight: 500,
            transition: customization.animations.enabled 
              ? `all ${customization.animations.duration}s ${customization.animations.easing}`
              : 'none'
          }
        }
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: customization.borderRadius * 2,
            backgroundColor: customization.surfaceColor,
            border: `1px solid ${customization.primaryColor}20`,
            backdropFilter: 'blur(10px)',
            transition: customization.animations.enabled 
              ? `all ${customization.animations.duration}s ${customization.animations.easing}`
              : 'none'
          }
        }
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundColor: customization.surfaceColor,
            backdropFilter: 'blur(10px)',
            border: `1px solid ${customization.primaryColor}20`
          }
        }
      },
      MuiTextField: {
        styleOverrides: {
          root: {
            '& .MuiOutlinedInput-root': {
              borderRadius: customization.borderRadius,
              backgroundColor: `${customization.surfaceColor}80`,
              transition: customization.animations.enabled 
                ? `all ${customization.animations.duration}s ${customization.animations.easing}`
                : 'none'
            }
          }
        }
      }
    }
  })
}

interface ThemeCustomizationProviderProps {
  children: React.ReactNode
}

export const ThemeCustomizationProvider: React.FC<ThemeCustomizationProviderProps> = ({
  children
}) => {
  const [customization, setCustomization] = useState<ThemeCustomization>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('theme-customization')
      if (saved) {
        try {
          return { ...defaultThemeCustomization, ...JSON.parse(saved) }
        } catch {
          return defaultThemeCustomization
        }
      }
    }
    return defaultThemeCustomization
  })

  const [theme, setTheme] = useState<Theme>(() => createCustomTheme(customization))

  useEffect(() => {
    setTheme(createCustomTheme(customization))
  }, [customization])

  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('theme-customization', JSON.stringify(customization))
    }
  }, [customization])

  const updateCustomization = (updates: Partial<ThemeCustomization>) => {
    setCustomization(prev => ({ ...prev, ...updates }))
  }

  const resetToDefault = () => {
    setCustomization(defaultThemeCustomization)
  }

  return (
    <ThemeContext.Provider value={{ customization, updateCustomization, resetToDefault, theme }}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ThemeContext.Provider>
  )
}

// Theme customization panel component
export const ThemeCustomizationPanel: React.FC = () => {
  const { customization, updateCustomization, resetToDefault } = useThemeCustomization()

  return (
    <div style={{ padding: 24, maxWidth: 400 }}>
      <h3 style={{ marginBottom: 16 }}>Theme Customization</h3>
      
      <div style={{ marginBottom: 16 }}>
        <label style={{ display: 'block', marginBottom: 8 }}>Primary Color</label>
        <input
          type="color"
          value={customization.primaryColor}
          onChange={(e) => updateCustomization({ primaryColor: e.target.value })}
          style={{ width: '100%', height: 40, borderRadius: 8, border: 'none' }}
        />
      </div>

      <div style={{ marginBottom: 16 }}>
        <label style={{ display: 'block', marginBottom: 8 }}>Secondary Color</label>
        <input
          type="color"
          value={customization.secondaryColor}
          onChange={(e) => updateCustomization({ secondaryColor: e.target.value })}
          style={{ width: '100%', height: 40, borderRadius: 8, border: 'none' }}
        />
      </div>

      <div style={{ marginBottom: 16 }}>
        <label style={{ display: 'block', marginBottom: 8 }}>Background Color</label>
        <input
          type="color"
          value={customization.backgroundColor}
          onChange={(e) => updateCustomization({ backgroundColor: e.target.value })}
          style={{ width: '100%', height: 40, borderRadius: 8, border: 'none' }}
        />
      </div>

      <div style={{ marginBottom: 16 }}>
        <label style={{ display: 'block', marginBottom: 8 }}>Border Radius</label>
        <input
          type="range"
          min="0"
          max="20"
          value={customization.borderRadius}
          onChange={(e) => updateCustomization({ borderRadius: Number(e.target.value) })}
          style={{ width: '100%' }}
        />
        <span style={{ fontSize: 12, color: '#666' }}>{customization.borderRadius}px</span>
      </div>

      <div style={{ marginBottom: 16 }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input
            type="checkbox"
            checked={customization.animations.enabled}
            onChange={(e) => updateCustomization({ 
              animations: { ...customization.animations, enabled: e.target.checked }
            })}
          />
          Enable Animations
        </label>
      </div>

      <button
        onClick={resetToDefault}
        style={{
          width: '100%',
          padding: 12,
          backgroundColor: '#f44336',
          color: 'white',
          border: 'none',
          borderRadius: 8,
          cursor: 'pointer',
          fontSize: 14
        }}
      >
        Reset to Default
      </button>
    </div>
  )
}
