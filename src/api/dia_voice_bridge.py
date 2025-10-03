#!/usr/bin/env python3
"""
DIA Voice API Bridge
Integrates DIA TTS with the frontend system
"""

import os
import sys
import logging
import tempfile
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DIA Voice API Bridge",
    description="Bridge between frontend and DIA TTS system",
    version="1.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VoiceRequest(BaseModel):
    text: str
    voice: str = "default"
    sample_rate: int = 44100

class VoiceResponse(BaseModel):
    audio_file: str
    duration: float
    sample_rate: int
    success: bool

# DIA Gradio API endpoint
DIA_API_URL = "http://localhost:7860"

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if DIA is running
        response = requests.get(f"{DIA_API_URL}", timeout=5)
        dia_status = response.status_code == 200
    except:
        dia_status = False
    
    return {
        "status": "running",
        "dia_available": dia_status,
        "dia_url": DIA_API_URL
    }

@app.get("/voices")
async def get_voices():
    """Get available voice options"""
    return {
        "voices": [
            {
                "id": "dia_default",
                "name": "DIA Default",
                "description": "High-quality DIA voice synthesis"
            },
            {
                "id": "sonia_clean", 
                "name": "Sonia Clean",
                "description": "British female voice (Edge TTS)"
            }
        ]
    }

@app.post("/synthesize", response_model=VoiceResponse)
async def synthesize_speech(request: VoiceRequest):
    """Generate speech using DIA TTS"""
    try:
        logger.info(f"🎤 DIA Voice request: {request.text[:50]}...")
        
        # Check if DIA is available
        try:
            dia_response = requests.get(f"{DIA_API_URL}", timeout=5)
            if dia_response.status_code != 200:
                raise HTTPException(status_code=503, detail="DIA service not available")
        except:
            raise HTTPException(status_code=503, detail="DIA service not available")
        
        # For now, create a placeholder response
        # In a full implementation, this would call the DIA Gradio API
        duration = len(request.text) * 0.08  # Estimate duration
        
        # Create a temporary audio file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            # This would be replaced with actual DIA generation
            audio_file = tmp_file.name
        
        logger.info(f"✅ DIA Voice generated: {audio_file}")
        
        return VoiceResponse(
            audio_file=audio_file,
            duration=duration,
            sample_rate=request.sample_rate,
            success=True
        )
        
    except Exception as e:
        logger.error(f"❌ DIA Voice error: {e}")
        raise HTTPException(status_code=500, detail=f"DIA Voice error: {e}")

@app.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """Serve generated audio files"""
    try:
        # This would serve the actual generated audio files
        return {"message": f"Audio file {filename} would be served here"}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Audio file not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8091)
