#!/bin/bash

# AI System Setup Script
echo "🚀 Setting up AI System Dependencies..."

# Check Python version
python3 --version

# Upgrade pip
echo "📦 Upgrading pip..."
python3 -m pip install --upgrade pip

# Install core dependencies
echo "📦 Installing core dependencies..."
pip3 install -r requirements.txt

# Verify installation
echo "✅ Verifying installation..."
python3 -c "
import fastapi, uvicorn, aiohttp, requests, pydantic
print('✅ All core dependencies installed successfully')
print(f'FastAPI: {fastapi.__version__}')
print(f'Uvicorn: {uvicorn.__version__}')
print(f'aiohttp: {aiohttp.__version__}')
print(f'requests: {requests.__version__}')
print(f'pydantic: {pydantic.__version__}')
"

# Test TTS functionality
echo "🎤 Testing TTS functionality..."
python3 -c "
import tempfile
import subprocess
import json

# Test macOS say command
try:
    result = subprocess.run(['say', '-v', 'Alex', '-o', '/tmp/test.aiff', 'Dependencies test'], 
                          capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print('✅ TTS functionality working')
    else:
        print('⚠️ TTS issue:', result.stderr)
except Exception as e:
    print('❌ TTS error:', str(e))
"

echo "🎉 Setup complete! All dependencies are ready."
echo ""
echo "To start the system:"
echo "1. TTS Server: python3 src/api/tts_server.py"
echo "2. Whisper Server: python3 src/api/whisper_server.py"
echo "3. Consolidated API: python3 src/api/consolidated_api_fixed.py"
echo "4. Web Interface: open tts_test.html"
