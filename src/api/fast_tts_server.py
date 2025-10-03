#!/usr/bin/env python3
"""
Fast TTS Server using macOS 'say' command for immediate response
"""

import asyncio
import json
import logging
import os
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fast TTS Server", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TTSRequest(BaseModel):
    text: str
    voice: str = "sonia_clean"
    speed: float = 1.0

class TTSResponse(BaseModel):
    success: bool
    audio_file: str = None
    play_command: str = None
    error: str = None
    text: str
    voice: str
    speed: float
    engine: str

# Voice profiles optimized for macOS 'say' command
VOICE_PROFILES = {
    "sonia_clean": {
        "voice": "Samantha",  # British female voice
        "rate": 180,  # Words per minute (faster)
        "pitch": 0.8,  # Slightly higher pitch
        "description": "Sonia - Fast British female voice"
    },
    "assistant": {
        "voice": "Alex",
        "rate": 200,
        "pitch": 1.0,
        "description": "Fast assistant voice"
    },
    "sultry": {
        "voice": "Samantha",
        "rate": 160,
        "pitch": 0.7,
        "description": "Sultry feminine voice"
    }
}

@app.get("/")
async def root():
    return {"message": "Fast TTS Server", "status": "running", "engine": "macos_say"}

@app.get("/status")
async def status():
    return {
        "status": "running",
        "engine": "macos_say",
        "profiles_available": len(VOICE_PROFILES),
        "voices": list(VOICE_PROFILES.keys())
    }

@app.get("/profiles")
async def list_profiles():
    return {"profiles": VOICE_PROFILES}

@app.post("/synthesize", response_model=TTSResponse)
async def synthesize_speech(request: TTSRequest):
    """Generate speech using macOS 'say' command for maximum speed"""
    
    logger.info(f"🎤 Fast TTS request: '{request.text[:50]}...' (voice: {request.voice})")
    
    try:
        # Get voice profile
        profile = VOICE_PROFILES.get(request.voice, VOICE_PROFILES["sonia_clean"])
        
        # Generate unique filename (AIFF first, then convert to WAV)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_base = f"fast_voice_{timestamp}_{uuid.uuid4().hex[:8]}"
        aiff_file = os.path.join(os.getcwd(), f"{filename_base}.aiff")
        output_file = os.path.join(os.getcwd(), f"{filename_base}.wav")
        
        # Build say command for AIFF output
        say_cmd = [
            "say",
            "-v", profile["voice"],
            "-r", str(int(profile["rate"] * request.speed)),
            "-o", aiff_file,
            request.text
        ]
        
        # Execute say command
        import subprocess
        result = subprocess.run(say_cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and os.path.exists(aiff_file):
            # Convert AIFF to WAV using afconvert
            convert_cmd = ["afconvert", "-f", "WAVE", aiff_file, output_file]
            convert_result = subprocess.run(convert_cmd, capture_output=True, text=True, timeout=5)
            
            if convert_result.returncode == 0 and os.path.exists(output_file):
                # Clean up AIFF file
                os.remove(aiff_file)
                file_size = os.path.getsize(output_file) / 1024
                logger.info(f"✅ Fast TTS audio saved: {os.path.basename(output_file)} ({file_size:.1f} KB)")
            else:
                # Fallback: use AIFF file if conversion fails
                output_file = aiff_file
                file_size = os.path.getsize(output_file) / 1024
                logger.info(f"✅ Fast TTS audio saved (AIFF): {os.path.basename(output_file)} ({file_size:.1f} KB)")
            
            return TTSResponse(
                success=True,
                audio_file=output_file,
                play_command=f'afplay "{output_file}"',
                text=request.text,
                voice=request.voice,
                speed=request.speed,
                engine="macos_say"
            )
        else:
            logger.error(f"❌ Say command failed: {result.stderr}")
            return TTSResponse(
                success=False,
                error=f"Say command failed: {result.stderr}",
                text=request.text,
                voice=request.voice,
                speed=request.speed,
                engine="macos_say"
            )
            
    except subprocess.TimeoutExpired:
        logger.error("❌ TTS generation timed out")
        return TTSResponse(
            success=False,
            error="TTS generation timed out",
            text=request.text,
            voice=request.voice,
            speed=request.speed,
            engine="macos_say"
        )
    except Exception as e:
        logger.error(f"❌ TTS generation failed: {e}")
        return TTSResponse(
            success=False,
            error=str(e),
            text=request.text,
            voice=request.voice,
            speed=request.speed,
            engine="macos_say"
        )

if __name__ == "__main__":
    logger.info("🚀 Starting Fast TTS Server on PORT 8087")
    logger.info("⚡ Using macOS 'say' command for maximum speed")
    uvicorn.run(app, host="0.0.0.0", port=8087)
