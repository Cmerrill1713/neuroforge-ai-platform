# Personal AI Assistant - Frontend

A modern, polished React/Next.js frontend for an AI-powered personal assistant platform.

## 🚀 Features

- **Modern UI/UX**: Glassmorphism design with smooth animations
- **Real-time Communication**: WebSocket support for live AI interactions
- **Multi-panel Interface**: Chat, Agents, Optimization, Code Editor, and Vision panels
- **Voice Integration**: Text-to-speech and speech-to-text capabilities
- **Performance Monitoring**: Built-in Web Vitals tracking
- **Error Tracking**: Sentry integration for production monitoring
- **Responsive Design**: Mobile-first approach with adaptive layouts
- **Accessibility**: WCAG compliant with keyboard navigation
- **Type Safety**: Full TypeScript coverage
- **Testing**: Comprehensive unit and integration tests

## 🛠️ Tech Stack

- **Framework**: Next.js 14 with App Router
- **UI Library**: Material-UI (MUI) v7
- **Styling**: Emotion CSS-in-JS
- **Animations**: Framer Motion
- **State Management**: React hooks + Context API
- **Type Safety**: TypeScript
- **Testing**: Jest + React Testing Library
- **E2E Testing**: Playwright
- **Error Tracking**: Sentry
- **Performance**: Web Vitals
- **Code Quality**: ESLint + Prettier

## 📋 Prerequisites

- Node.js 18+ and npm
- Backend API server running on port 8000
- TTS server running on port 8086 (optional)

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment variables:**
   ```bash
   cp ENVIRONMENT.md .env.local
   # Edit .env.local with your configuration
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 📜 Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript type checking

# Testing
npm test             # Run unit tests
npm run test:watch   # Run tests in watch mode
npm run test:coverage # Run tests with coverage
npm run test:ci      # Run tests for CI
npm run e2e          # Run E2E tests
npm run e2e:ui       # Run E2E tests with UI

# Quality Assurance
npm run quality      # Run lint + type-check + tests
```

## 🏗️ Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── api/               # API routes
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── src/
│   ├── components/        # React components
│   │   ├── navigation/    # Navigation components
│   │   ├── layouts/       # Layout components
│   │   └── ...
│   ├── services/          # API services
│   ├── utils/             # Utility functions
│   ├── hooks/             # Custom React hooks
│   ├── types/             # TypeScript type definitions
│   └── config/            # Configuration files
├── __tests__/             # Unit tests
├── public/                # Static assets
├── .eslintrc.json        # ESLint configuration
├── .prettierrc           # Prettier configuration
├── jest.config.js        # Jest configuration
├── next.config.js        # Next.js configuration
├── tailwind.config.js    # Tailwind CSS config
└── tsconfig.json         # TypeScript configuration
```

## 🔧 Configuration

### Environment Variables

See [ENVIRONMENT.md](./ENVIRONMENT.md) for detailed configuration options.

### Theme Customization

The app supports dynamic theming. Customize colors, fonts, and animations in:
- `src/theme/AdvancedThemes.ts`
- `src/config/environment.ts`

## 🧪 Testing

### Unit Tests
```bash
npm test
```

### Integration Tests
```bash
npm run test:coverage
```

### E2E Tests
```bash
# Install Playwright browsers
npx playwright install

# Run E2E tests
npm run e2e
```

## 🚀 Deployment

### Development
```bash
npm run build
npm run start
```

### Production
```bash
# Using Docker
docker build -t ai-assistant-frontend .
docker run -p 3000:3000 ai-assistant-frontend

# Using Vercel
npm install -g vercel
vercel --prod
```

## 🔒 Security

- **Content Security Policy**: Configured in `next.config.js`
- **Input Sanitization**: All user inputs are sanitized
- **XSS Protection**: DOMPurify integration
- **Rate Limiting**: Client-side rate limiting
- **Error Tracking**: Sentry integration (optional)

## 📊 Performance

- **Web Vitals Monitoring**: Automatic tracking of Core Web Vitals
- **Bundle Analysis**: Use `npm run build` and check bundle sizes
- **Lazy Loading**: Components are lazy-loaded for better performance
- **Image Optimization**: Next.js Image component with WebP support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Run quality checks: `npm run quality`
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

### Code Quality

- **Pre-commit hooks**: Automatically run linting and formatting
- **TypeScript**: Strict type checking enabled
- **ESLint**: Code quality and consistency
- **Prettier**: Automatic code formatting

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   lsof -i :3000
   kill -9 <PID>
   ```

2. **Backend connection issues:**
   - Ensure backend is running on port 8000
   - Check CORS configuration
   - Verify API endpoints

3. **Build failures:**
   ```bash
   rm -rf node_modules .next
   npm install
   npm run build
   ```

### Debug Mode

Enable debug logging:
```bash
NEXT_PUBLIC_DEBUG_MODE=true npm run dev
```

## 📞 Support

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)
- **Documentation**: [Project Wiki](../../wiki)

---

**Built with ❤️ using Next.js, TypeScript, and Material-UI**