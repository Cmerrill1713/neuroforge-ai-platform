'use client'

// Unified Design System for AI Assistant Platform
export const designSystem = {
  // Spacing System (8px base unit)
  spacing: {
    xs: 0.5,    // 4px
    sm: 1,      // 8px
    md: 1.5,    // 12px
    lg: 2,      // 16px
    xl: 3,      // 24px
    xxl: 4,     // 32px
  },

  // Container Padding
  containerPadding: {
    mobile: 2,   // 16px
    tablet: 2.5, // 20px
    desktop: 3,  // 24px
  },

  // Border Radius
  borderRadius: {
    sm: 1,       // 8px
    md: 1.5,     // 12px
    lg: 2,       // 16px
    xl: 3,       // 24px
  },

  // Typography Scale
  typography: {
    h1: { fontSize: '2rem', fontWeight: 700, lineHeight: 1.2 },
    h2: { fontSize: '1.75rem', fontWeight: 600, lineHeight: 1.3 },
    h3: { fontSize: '1.5rem', fontWeight: 600, lineHeight: 1.3 },
    h4: { fontSize: '1.25rem', fontWeight: 600, lineHeight: 1.3 },
    h5: { fontSize: '1.125rem', fontWeight: 600, lineHeight: 1.4 },
    h6: { fontSize: '1rem', fontWeight: 600, lineHeight: 1.4 },
    body1: { fontSize: '1rem', fontWeight: 400, lineHeight: 1.5 },
    body2: { fontSize: '0.875rem', fontWeight: 400, lineHeight: 1.5 },
    caption: { fontSize: '0.75rem', fontWeight: 400, lineHeight: 1.4 },
  },

  // Color Palette
  colors: {
    primary: {
      main: '#6366f1',
      light: '#818cf8',
      dark: '#4f46e5',
    },
    secondary: {
      main: '#ec4899',
      light: '#f472b6',
      dark: '#db2777',
    },
    success: {
      main: '#10b981',
      light: '#34d399',
      dark: '#059669',
    },
    warning: {
      main: '#f59e0b',
      light: '#fbbf24',
      dark: '#d97706',
    },
    error: {
      main: '#ef4444',
      light: '#f87171',
      dark: '#dc2626',
    },
    info: {
      main: '#06b6d4',
      light: '#22d3ee',
      dark: '#0891b2',
    },
  },

  // Background Gradients
  gradients: {
    primary: 'linear-gradient(135deg, #6366f1 0%, #818cf8 100%)',
    secondary: 'linear-gradient(135deg, #ec4899 0%, #f472b6 100%)',
    success: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
    warning: 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)',
    error: 'linear-gradient(135deg, #ef4444 0%, #f87171 100%)',
    info: 'linear-gradient(135deg, #06b6d4 0%, #22d3ee 100%)',
    // Subtle backgrounds
    primarySubtle: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(129, 140, 248, 0.1) 100%)',
    secondarySubtle: 'linear-gradient(135deg, rgba(236, 72, 153, 0.1) 0%, rgba(244, 114, 182, 0.1) 100%)',
    // Header gradients
    headerPrimary: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(236, 72, 153, 0.2) 100%)',
    headerHover: 'linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(236, 72, 153, 0.3) 100%)',
  },

  // Shadows
  shadows: {
    sm: '0 2px 8px rgba(0, 0, 0, 0.1)',
    md: '0 4px 15px rgba(0, 0, 0, 0.15)',
    lg: '0 8px 25px rgba(0, 0, 0, 0.2)',
    xl: '0 12px 40px rgba(0, 0, 0, 0.25)',
    // Glow effects
    glow: '0 0 20px rgba(99, 102, 241, 0.3)',
    glowSecondary: '0 0 20px rgba(236, 72, 153, 0.3)',
  },

  // Transitions
  transitions: {
    fast: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
    normal: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    slow: 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
  },

  // Component Styles
  components: {
    // Panel Container
    panelContainer: {
      height: '100vh',
      width: '100vw',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
    },

    // Panel Header
    panelHeader: {
      p: 3,
      background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(236, 72, 153, 0.2) 100%)',
      backdropFilter: 'blur(10px)',
      borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      '&:hover': {
        background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(236, 72, 153, 0.3) 100%)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
        boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)',
      }
    },

    // Panel Content
    panelContent: {
      flex: 1,
      p: 3,
      overflow: 'auto',
      display: 'flex',
      flexDirection: 'column',
      background: 'rgba(5, 5, 5, 0.95)',
      backdropFilter: 'blur(20px)',
    },

    // Card Styles
    card: {
      background: 'rgba(255, 255, 255, 0.05)',
      backdropFilter: 'blur(10px)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: 2,
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      '&:hover': {
        border: '1px solid rgba(255, 255, 255, 0.2)',
        boxShadow: '0 8px 25px rgba(0, 0, 0, 0.2)',
        transform: 'translateY(-2px)',
      }
    },

    // Button Styles
    button: {
      borderRadius: 1.5,
      textTransform: 'none',
      fontWeight: 600,
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      '&:hover': {
        transform: 'translateY(-1px)',
        boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)',
      }
    },

    // Input Styles
    input: {
      '& .MuiOutlinedInput-root': {
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        borderRadius: 1.5,
        '& fieldset': {
          borderColor: 'rgba(255, 255, 255, 0.2)',
        },
        '&:hover fieldset': {
          borderColor: 'rgba(255, 255, 255, 0.3)',
        },
        '&.Mui-focused fieldset': {
          borderColor: '#6366f1',
        }
      },
      '& .MuiInputBase-input': {
        color: 'white',
        '&::placeholder': {
          color: 'rgba(255, 255, 255, 0.5)',
          opacity: 1
        }
      }
    },

    // Avatar Styles
    avatar: {
      background: 'linear-gradient(135deg, #6366f1 0%, #ec4899 100%)',
      width: 40,
      height: 40,
      fontSize: '1.2rem',
    },

    // Chip Styles
    chip: {
      borderRadius: 1,
      fontWeight: 500,
      fontSize: '0.75rem',
      height: 24,
    },
  },

  // Responsive Breakpoints
  breakpoints: {
    mobile: '0px',
    tablet: '768px',
    desktop: '1024px',
  },
}

// Helper functions
export const getSpacing = (size: keyof typeof designSystem.spacing) => designSystem.spacing[size]
export const getColor = (color: keyof typeof designSystem.colors) => designSystem.colors[color]
export const getGradient = (gradient: keyof typeof designSystem.gradients) => designSystem.gradients[gradient]
export const getShadow = (shadow: keyof typeof designSystem.shadows) => designSystem.shadows[shadow]
export const getTransition = (transition: keyof typeof designSystem.transitions) => designSystem.transitions[transition]

// Responsive padding helper
export const getResponsivePadding = () => ({
  xs: designSystem.containerPadding.mobile,
  sm: designSystem.containerPadding.tablet,
  md: designSystem.containerPadding.desktop,
})

// Component style helpers
export const getPanelStyles = () => ({
  container: designSystem.components.panelContainer,
  header: designSystem.components.panelHeader,
  content: designSystem.components.panelContent,
})

export const getCardStyles = () => designSystem.components.card
export const getButtonStyles = () => designSystem.components.button
export const getInputStyles = () => designSystem.components.input
export const getAvatarStyles = () => designSystem.components.avatar
export const getChipStyles = () => designSystem.components.chip
