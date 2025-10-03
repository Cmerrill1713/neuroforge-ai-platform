#!/usr/bin/env python3
"""
Simple TTS Server - GitHub Documentation Compliant
Based on FastAPI best practices and macOS say command
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging
import subprocess
import tempfile
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Simple TTS Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TTSRequest(BaseModel):
    text: str
    voice: str = "Alex"
    speed: float = 1.0
    pitch: float = 1.0

class TTSResponse(BaseModel):
    success: bool
    audio_file: str = None
    error: str = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "simple_tts", "port": 8087}

@app.post("/synthesize", response_model=TTSResponse)
async def synthesize_speech(request: TTSRequest):
    """Synthesize speech from text using macOS say command"""
    try:
        logger.info(f"Synthesizing speech for: {request.text[:50]}...")
        
        # Create temporary file for audio output (AIFF format)
        with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Use macOS built-in TTS (say command)
        cmd = [
            "say",
            "-v", request.voice,
            "-r", str(int(200 * request.speed)),  # Rate in words per minute
            "-o", temp_path,
            request.text
        ]
        
        # Execute TTS command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Read the generated audio file
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            # Clean up temp file
            os.unlink(temp_path)
            
            return TTSResponse(
                success=True,
                audio_file=f"data:audio/aiff;base64,{audio_data.hex()}"
            )
        else:
            logger.error(f"TTS command failed: {result.stderr}")
            return TTSResponse(
                success=False,
                error=f"TTS synthesis failed: {result.stderr}"
            )
            
    except subprocess.TimeoutExpired:
        logger.error("TTS synthesis timed out")
        return TTSResponse(
            success=False,
            error="TTS synthesis timed out"
        )
    except Exception as e:
        logger.error(f"TTS synthesis error: {e}")
        return TTSResponse(
            success=False,
            error=f"TTS synthesis error: {str(e)}"
        )

@app.get("/voices")
async def get_voices():
    """Get available voices"""
    try:
        # Get available voices using say command
        result = subprocess.run(["say", "-v", "?"], capture_output=True, text=True)
        
        voices = []
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        voice_name = parts[0]
                        voice_desc = ' '.join(parts[1:])
                        voices.append({
                            "id": voice_name,
                            "name": voice_name,
                            "description": voice_desc
                        })
        
        return {"voices": voices}
    except Exception as e:
        logger.error(f"Error getting voices: {e}")
        return {"voices": [{"id": "Alex", "name": "Alex", "description": "Default voice"}]}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Simple TTS Server",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "synthesize": "/synthesize",
            "voices": "/voices"
        }
    }

if __name__ == "__main__":
    import sys
    port = 8087  # Default port
    if len(sys.argv) > 2 and sys.argv[1] == "--port":
        port = int(sys.argv[2])
    logger.info(f"🚀 Starting Simple TTS Server on PORT {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
