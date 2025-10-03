# Environment Variables

This document describes the environment variables used by the Personal AI Assistant frontend.

## Required Variables

### API Configuration
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```
The URL of the backend API server.

### Application Info
```bash
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_APP_NAME="Personal AI Assistant"
```

## Optional Variables

### TTS (Text-to-Speech)
```bash
NEXT_PUBLIC_TTS_SERVER_URL=http://localhost:8086
NEXT_PUBLIC_TTS_ENABLED=true
NEXT_PUBLIC_DEFAULT_VOICE_PROFILE=assistant
```

### Error Tracking (Sentry)
```bash
NEXT_PUBLIC_SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_AUTH_TOKEN=your-sentry-auth-token
```

### Feature Flags
```bash
NEXT_PUBLIC_ENABLE_VOICE=true
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_ERROR_TRACKING=false
NEXT_PUBLIC_DEBUG_MODE=false
```

## Development Setup

1. Copy this file to `.env.local`:
   ```bash
   cp ENVIRONMENT.md .env.local
   ```

2. Update the values according to your environment.

3. For production deployment, set the appropriate values in your hosting platform's environment variables.

## Security Notes

- Never commit `.env.local` or any file containing real secrets to version control
- Use different values for development, staging, and production
- Rotate API keys and tokens regularly
- Use environment-specific Sentry DSNs
