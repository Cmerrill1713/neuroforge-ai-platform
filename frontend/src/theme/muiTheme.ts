import { createTheme, ThemeOptions } from '@mui/material/styles'

// Custom theme that matches your enhanced design aesthetic
export const aiStudioEnhancedTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#6366f1', // Modern indigo - more sophisticated
      light: '#818cf8',
      dark: '#4f46e5',
      contrastText: '#ffffff'
    },
    secondary: {
      main: '#ec4899', // Modern pink - better contrast
      light: '#f472b6',
      dark: '#db2777',
      contrastText: '#ffffff'
    },
    background: {
      default: '#0f0f23', // Slightly lighter for better readability
      paper: 'rgba(30, 30, 50, 0.8)' // More contrast
    },
    text: {
      primary: '#f8fafc', // Softer white
      secondary: 'rgba(248, 250, 252, 0.7)'
    },
    divider: 'rgba(255, 255, 255, 0.08)', // Subtle divider
    success: {
      main: '#10b981', // Modern emerald
      light: '#34d399',
      dark: '#059669'
    },
    warning: {
      main: '#f59e0b', // Modern amber
      light: '#fbbf24',
      dark: '#d97706'
    },
    error: {
      main: '#ef4444', // Modern red
      light: '#f87171',
      dark: '#dc2626'
    },
    info: {
      main: '#06b6d4', // Modern cyan
      light: '#22d3ee',
      dark: '#0891b2'
    }
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      background: 'linear-gradient(135deg, #ffffff 0%, #e3f2fd 100%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      backgroundClip: 'text'
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      color: '#ffffff'
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
      color: '#ffffff'
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      color: '#ffffff'
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
      color: '#ffffff'
    },
    h6: {
      fontSize: '1.125rem',
      fontWeight: 600,
      color: '#ffffff'
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
      color: '#ffffff'
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
      color: 'rgba(255, 255, 255, 0.7)'
    },
    button: {
      textTransform: 'none',
      fontWeight: 600
    }
  },
  shape: {
    borderRadius: 12
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          background: 'linear-gradient(135deg, #0f0f23 0%, #1e1e3f 25%, #2d1b69 50%, #1e1e3f 75%, #0f0f23 100%)',
          minHeight: '100vh',
          backgroundAttachment: 'fixed'
        }
      }
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: 16
        }
      }
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: 12,
          transition: 'all 0.3s ease-in-out',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 30px rgba(0, 0, 0, 0.2)',
            borderColor: 'rgba(255, 255, 255, 0.2)'
          }
        }
      }
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          textTransform: 'none',
          fontWeight: 600,
          padding: '10px 24px',
          transition: 'all 0.3s ease-in-out',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 25px rgba(0, 0, 0, 0.3)'
          }
        },
        contained: {
          background: 'linear-gradient(135deg, #6366f1 0%, #ec4899 100%)',
          boxShadow: '0 4px 15px rgba(99, 102, 241, 0.4)',
          '&:hover': {
            background: 'linear-gradient(135deg, #4f46e5 0%, #db2777 100%)',
            boxShadow: '0 8px 25px rgba(99, 102, 241, 0.6)'
          }
        },
        outlined: {
          borderColor: 'rgba(255, 255, 255, 0.3)',
          color: '#ffffff',
          '&:hover': {
            borderColor: '#1976d2',
            backgroundColor: 'rgba(25, 118, 210, 0.1)'
          }
        }
      }
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          transition: 'all 0.3s ease-in-out',
          '&:hover': {
            transform: 'scale(1.1)',
            backgroundColor: 'rgba(255, 255, 255, 0.1)'
          }
        }
      }
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 12,
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            transition: 'all 0.3s ease-in-out',
            '& fieldset': {
              borderColor: 'rgba(255, 255, 255, 0.2)'
            },
            '&:hover fieldset': {
              borderColor: 'rgba(255, 255, 255, 0.3)'
            },
            '&.Mui-focused fieldset': {
              borderColor: '#1976d2',
              boxShadow: '0 0 0 2px rgba(25, 118, 210, 0.2)'
            }
          },
          '& .MuiInputLabel-root': {
            color: 'rgba(255, 255, 255, 0.7)',
            '&.Mui-focused': {
              color: '#1976d2'
            }
          },
          '& .MuiInputBase-input': {
            color: '#ffffff'
          }
        }
      }
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 600,
          transition: 'all 0.3s ease-in-out',
          '&:hover': {
            transform: 'scale(1.05)'
          }
        },
        filled: {
          background: 'linear-gradient(135deg, #6366f1 0%, #ec4899 100%)',
          color: '#ffffff'
        },
        outlined: {
          borderColor: 'rgba(255, 255, 255, 0.3)',
          color: '#ffffff',
          '&:hover': {
            borderColor: '#1976d2',
            backgroundColor: 'rgba(25, 118, 210, 0.1)'
          }
        }
      }
    },
    MuiAvatar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #6366f1 0%, #ec4899 100%)',
          boxShadow: '0 4px 15px rgba(99, 102, 241, 0.3)'
        }
      }
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          backdropFilter: 'blur(10px)',
          borderRadius: 8,
          fontSize: '0.75rem',
          fontWeight: 500
        }
      }
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          boxShadow: 'none'
        }
      }
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(20px)',
          borderRight: '1px solid rgba(255, 255, 255, 0.1)'
        }
      }
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          backgroundColor: 'rgba(15, 15, 35, 0.95)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }
      }
    },
    MuiMenu: {
      styleOverrides: {
        paper: {
          backgroundColor: 'rgba(15, 15, 35, 0.95)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }
      }
    },
    MuiCircularProgress: {
      styleOverrides: {
        root: {
          color: '#1976d2'
        }
      }
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
          borderRadius: 4,
          '& .MuiLinearProgress-bar': {
            background: 'linear-gradient(135deg, #6366f1 0%, #ec4899 100%)',
            borderRadius: 4
          }
        }
      }
    }
  }
} as ThemeOptions)
