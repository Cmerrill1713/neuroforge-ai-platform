#!/usr/bin/env python3
"""
DIA Voice Integration using Hugging Face Inference API
Natural-sounding voice using DIA-1.6B model
"""

import os
import sys
import logging
import tempfile
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
import requests
import soundfile as sf
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DIA Natural Voice API",
    description="Natural-sounding voice using DIA-1.6B via Hugging Face Inference API",
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
    voice: str = "dia_natural"
    sample_rate: int = 44100

class VoiceResponse(BaseModel):
    success: bool
    audio_file: str
    duration: float
    sample_rate: int
    message: str

def generate_dia_voice(text: str, hf_token: str) -> bytes:
    """Generate voice using DIA-1.6B via Hugging Face Inference API"""
    try:
        logger.info(f"🎤 Generating DIA voice for: {text[:50]}...")
        
        # Use Hugging Face Inference API with fal-ai provider
        url = "https://api-inference.huggingface.co/models/nari-labs/Dia-1.6B"
        headers = {
            "Authorization": f"Bearer {hf_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": text,
            "parameters": {
                "provider": "fal-ai"
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            logger.info("✅ DIA voice generated successfully!")
            return response.content
        else:
            logger.error(f"❌ DIA API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ DIA voice generation failed: {e}")
        return None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    hf_token = os.environ.get("HF_TOKEN")
    return {
        "status": "running",
        "model": "DIA-1.6B",
        "provider": "fal-ai",
        "hf_token_available": hf_token is not None,
        "api": "Hugging Face Inference API"
    }

@app.get("/voices")
async def get_voices():
    """Get available voice options"""
    return {
        "voices": [
            {
                "id": "dia_natural",
                "name": "DIA Natural",
                "description": "Natural-sounding voice using DIA-1.6B model"
            }
        ]
    }

@app.post("/synthesize", response_model=VoiceResponse)
async def synthesize_speech(request: VoiceRequest):
    """Generate natural-sounding speech using DIA"""
    try:
        logger.info(f"🎤 DIA Natural Voice request: {request.text[:50]}...")
        
        # Check for Hugging Face token
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            raise HTTPException(
                status_code=500, 
                detail="HF_TOKEN environment variable not set. Please set your Hugging Face token."
            )
        
        # Generate voice using DIA
        audio_bytes = generate_dia_voice(request.text, hf_token)
        
        if audio_bytes:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(audio_bytes)
                audio_file = tmp_file.name
            
            # Get audio duration
            try:
                audio_data, sample_rate = sf.read(audio_file)
                duration = len(audio_data) / sample_rate
            except:
                duration = len(request.text) * 0.08  # Estimate
            
            logger.info(f"✅ DIA Natural Voice generated: {audio_file}")
            
            return VoiceResponse(
                success=True,
                audio_file=audio_file,
                duration=duration,
                sample_rate=request.sample_rate,
                message="Natural-sounding voice generated successfully"
            )
        else:
            # Fallback: create a simple audio file
            duration = len(request.text) * 0.08
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                # Generate a simple tone as fallback
                t = np.linspace(0, duration, int(request.sample_rate * duration), False)
                frequency = 440  # A4 note
                audio_data = np.sin(2 * np.pi * frequency * t) * 0.1
                sf.write(tmp_file.name, audio_data, request.sample_rate)
                audio_file = tmp_file.name
            
            logger.warning(f"⚠️ Using fallback audio: {audio_file}")
            
            return VoiceResponse(
                success=False,
                audio_file=audio_file,
                duration=duration,
                sample_rate=request.sample_rate,
                message="DIA voice generation failed, using fallback"
            )
        
    except Exception as e:
        logger.error(f"❌ DIA Natural Voice error: {e}")
        raise HTTPException(status_code=500, detail=f"DIA Natural Voice error: {e}")

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
    uvicorn.run(app, host="0.0.0.0", port=8092)


