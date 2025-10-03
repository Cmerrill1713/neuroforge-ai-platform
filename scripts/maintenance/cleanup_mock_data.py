#!/usr/bin/env python3
""'
Mock Data Cleanup Script
Remove mock data and prepare for real backend integration
""'

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any

class MockDataCleanup:
    """TODO: Add docstring."""
    """Clean up mock data and prepare for real backend integration.""'

    def __init__(self):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.project_root = Path(".')
        self.frontend_dir = self.project_root / "frontend'
        self.backend_dir = self.project_root

    def cleanup_mock_data(self):
        """TODO: Add docstring."""
        """Remove mock data and prepare for real integration.""'
        print("🧹 Cleaning up mock data...')

        # 1. Fix Material-UI icon imports
        self.fix_mui_imports()

        # 2. Update API configuration
        self.update_api_config()

        # 3. Remove mock data files
        self.remove_mock_files()

        # 4. Update environment configuration
        self.update_environment_config()

        # 5. Prepare for real backend integration
        self.prepare_real_backend()

        print("✅ Mock data cleanup completed!')

    def fix_mui_imports(self):
        """TODO: Add docstring."""
        """Fix Material-UI icon imports.""'
        print("🔧 Fixing Material-UI icon imports...')

        # Fix PerformanceMonitor.tsx
        performance_monitor = self.frontend_dir / "src" / "components" / "PerformanceMonitor.tsx'
        if performance_monitor.exists():
            content = performance_monitor.read_text()

            # Replace problematic imports
            content = content.replace("Memory as CpuIcon,", "Cpu as CpuIcon,')
            content = content.replace("Speed as ActivityIcon", "Activity as ActivityIcon')

            # Add missing imports
            if "Cpu as CpuIcon,' not in content:
                content = content.replace(
                    "Memory as MemoryIcon,',
                    "Memory as MemoryIcon,\n  Cpu as CpuIcon,'
                )

            if "Activity as ActivityIcon,' not in content:
                content = content.replace(
                    "Speed as SpeedIcon,',
                    "Speed as SpeedIcon,\n  Activity as ActivityIcon,'
                )

            performance_monitor.write_text(content)
            print("✅ Fixed PerformanceMonitor.tsx imports')

        # Fix AdvancedChatFeatures.tsx
        advanced_chat = self.frontend_dir / "src" / "components" / "AdvancedChatFeatures.tsx'
        if advanced_chat.exists():
            content = advanced_chat.read_text()
            content = content.replace("Copy as CopyIcon,", "ContentCopy as CopyIcon,')
            advanced_chat.write_text(content)
            print("✅ Fixed AdvancedChatFeatures.tsx imports')

    def update_api_config(self):
        """TODO: Add docstring."""
        """Update API configuration for real backend.""'
        print("🔧 Updating API configuration...')

        # Update API client
        api_client = self.frontend_dir / "src" / "lib" / "api.ts'
        if api_client.exists():
            content = api_client.read_text()

            # Update API base URL
            content = content.replace(
                "const API_BASE_URL = "http://localhost:8000"',
                "const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"'
            )

            # Add environment variable support
            if "process.env.NEXT_PUBLIC_API_URL' not in content:
                content = content.replace(
                    "const API_BASE_URL = "http://localhost:8000"',
                    "const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"'
                )

            api_client.write_text(content)
            print("✅ Updated API client configuration')

        # Create environment file
        env_file = self.frontend_dir / ".env.local'
        env_content = ""'# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Redis Configuration (optional)
NEXT_PUBLIC_REDIS_URL=redis://localhost:6379

# WebSocket Configuration
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/chat

# Development Mode
NODE_ENV=development
""'
        env_file.write_text(env_content)
        print("✅ Created .env.local file')

    def remove_mock_files(self):
        """TODO: Add docstring."""
        """Remove mock data files.""'
        print("🗑️ Removing mock data files...')

        mock_files = [
            "mock_data.json',
            "test_data.json',
            "sample_data.json',
            "dummy_data.json'
        ]

        for mock_file in mock_files:
            file_path = self.project_root / mock_file
            if file_path.exists():
                file_path.unlink()
                print(f"✅ Removed {mock_file}')

        # Remove mock directories
        mock_dirs = [
            "mock_data',
            "test_data',
            "sample_data'
        ]

        for mock_dir in mock_dirs:
            dir_path = self.project_root / mock_dir
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"✅ Removed {mock_dir}/')

    def update_environment_config(self):
        """TODO: Add docstring."""
        """Update environment configuration.""'
        print("🔧 Updating environment configuration...')

        # Update package.json scripts
        package_json = self.frontend_dir / "package.json'
        if package_json.exists():
            content = json.loads(package_json.read_text())

            # Add environment-specific scripts
            if "scripts' not in content:
                content["scripts'] = {}

            content["scripts"]["dev:real"] = "NODE_ENV=development npm run dev'
            content["scripts"]["build:prod"] = "NODE_ENV=production npm run build'
            content["scripts"]["start:prod"] = "NODE_ENV=production npm start'

            package_json.write_text(json.dumps(content, indent=2))
            print("✅ Updated package.json scripts')

        # Create production environment file
        env_prod = self.frontend_dir / ".env.production'
        env_prod_content = ""'# Production API Configuration
NEXT_PUBLIC_API_URL=https://api.agentic-llm-core.com

# Production Redis Configuration
NEXT_PUBLIC_REDIS_URL=redis://redis.agentic-llm-core.com:6379

# Production WebSocket Configuration
NEXT_PUBLIC_WS_URL=wss://api.agentic-llm-core.com/ws/chat

# Production Mode
NODE_ENV=production
""'
        env_prod.write_text(env_prod_content)
        print("✅ Created .env.production file')

    def prepare_real_backend(self):
        """TODO: Add docstring."""
        """Prepare for real backend integration.""'
        print("🔧 Preparing for real backend integration...')

        # Create backend configuration
        backend_config = {
            "api': {
                "host": "0.0.0.0',
                "port': 8000,
                "reload': True,
                "workers': 1
            },
            "redis': {
                "host": "localhost',
                "port': 6379,
                "db': 0,
                "password': None
            },
            "models': {
                "qwen2.5:7b': {
                    "enabled': True,
                    "provider": "ollama',
                    "endpoint": "http://localhost:11434'
                },
                "qwen3-omni': {
                    "enabled': True,
                    "provider": "mlx',
                    "endpoint": "local'
                }
            },
            "features': {
                "chat': True,
                "voice': True,
                "multimodal': True,
                "collaboration': True,
                "learning': True,
                "performance_monitoring': True
            }
        }

        config_file = self.backend_dir / "config" / "backend.json'
        config_file.parent.mkdir(exist_ok=True)
        config_file.write_text(json.dumps(backend_config, indent=2))
        print("✅ Created backend configuration')

        # Create startup script for real backend
        startup_script = self.backend_dir / "start_real_backend.py'
        startup_content = ""'#!/usr/bin/env python3
""'
Real Backend Startup Script
Start the backend with real AI models and services
""'

import subprocess
import sys
import os
from pathlib import Path

def start_real_backend():
    """TODO: Add docstring."""
    """Start the real backend server.""'
    print("🚀 Starting Real Backend Server...')

    # Check if required services are running
    services = {
        "ollama": "http://localhost:11434',
        "redis": "redis://localhost:6379'
    }

    print("🔍 Checking required services...')
    for service, endpoint in services.items():
        print(f"   {service}: {endpoint}')

    # Start the backend
    try:
        subprocess.run([
            sys.executable, "api_server.py'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start backend: {e}')
        return False

    return True

if __name__ == "__main__':
    start_real_backend()
""'
        startup_script.write_text(startup_content)
        startup_script.chmod(0o755)
        print("✅ Created real backend startup script')

    def create_integration_guide(self):
        """TODO: Add docstring."""
        """Create integration guide for real backend.""'
        print("📝 Creating integration guide...')

        guide_content = ""'# 🔧 Real Backend Integration Guide

## Prerequisites

### Required Services
1. **Ollama** - For local AI models
2. **Redis** - For caching and session management
3. **Python 3.8+** - Backend runtime
4. **Node.js 16+** - Frontend runtime

### Installation

#### 1. Install Ollama
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve
```

#### 2. Install Redis
```bash
# macOS
brew install redis
brew services start redis

# Linux
sudo apt-get install redis-server
sudo systemctl start redis
```

#### 3. Install AI Models
```bash
# Install Qwen2.5 7B
ollama pull qwen2.5:7b

# Install Qwen3-Omni (if available)
ollama pull qwen3-omni
```

## Starting the Real Backend

### 1. Start Required Services
```bash
# Start Ollama
ollama serve

# Start Redis
redis-server
```

### 2. Start Backend
```bash
python3 start_real_backend.py
```

### 3. Start Frontend
```bash
cd frontend
npm run dev
```

## Configuration

### Backend Configuration
Edit `config/backend.json` to configure:
- API settings
- Redis connection
- Model endpoints
- Feature flags

### Frontend Configuration
Edit `.env.local` to configure:
- API URL
- Redis URL
- WebSocket URL

## Testing

### 1. Test Backend
```bash
curl http://localhost:8000/status
curl http://localhost:8000/models
```

### 2. Test Frontend
Open http://localhost:3000 and test all features

### 3. Test AI Models
```bash
curl -X POST http://localhost:8000/chat \\
  -H "Content-Type: application/json' \\
  -d "{"message": "Hello, how are you?", "task_type": "text_generation"}'
```

## Troubleshooting

### Common Issues
1. **Ollama not running**: Start with `ollama serve`
2. **Redis connection failed**: Start with `redis-server`
3. **Model not found**: Install with `ollama pull <model>`
4. **Port conflicts**: Change ports in configuration

### Logs
- Backend logs: Console output
- Frontend logs: Browser console
- Service logs: Check service-specific logs

## Production Deployment

### 1. Build Frontend
```bash
cd frontend
npm run build
```

### 2. Configure Production
- Update `.env.production`
- Configure reverse proxy
- Set up SSL certificates
- Configure monitoring

### 3. Deploy
- Use Docker containers
- Set up load balancing
- Configure auto-scaling
- Set up monitoring

## Support

For issues and questions:
1. Check logs for error messages
2. Verify service status
3. Check configuration files
4. Review this guide
""'

        guide_file = self.project_root / "REAL_BACKEND_INTEGRATION.md'
        guide_file.write_text(guide_content)
        print("✅ Created integration guide')

def main():
    """TODO: Add docstring."""
    """Main cleanup function.""'
    print("🧹 Mock Data Cleanup')
    print("=' * 50)

    cleanup = MockDataCleanup()
    cleanup.cleanup_mock_data()
    cleanup.create_integration_guide()

    print("\n🎉 Cleanup completed!')
    print("\n📋 Next steps:')
    print("1. Install required services (Ollama, Redis)')
    print("2. Start real backend: python3 start_real_backend.py')
    print("3. Start frontend: cd frontend && npm run dev')
    print("4. Test all features with real AI models')
    print("\n📖 See REAL_BACKEND_INTEGRATION.md for detailed instructions')

if __name__ == "__main__':
    main()
