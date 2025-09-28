// Environment configuration
export const config = {
  app: {
    name: 'Personal AI Assistant',
    version: '1.0.0',
    environment: process.env.NODE_ENV || 'development',
  },
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    timeout: 10000,
  },
  chat: {
    maxMessages: 100,
    messageHistoryLimit: 50,
    typingIndicatorDelay: 1000,
  },
  ui: {
    theme: 'dark',
    animations: {
      enabled: true,
      duration: 300,
    },
    breakpoints: {
      mobile: 768,
      tablet: 1024,
      desktop: 1200,
    },
  },
  features: {
    errorReporting: process.env.NODE_ENV === 'production',
    analytics: process.env.NODE_ENV === 'production',
    devTools: process.env.NODE_ENV === 'development',
  },
} as const;

export type Config = typeof config;
