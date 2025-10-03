#!/usr/bin/env python3
"""
DIA Voice API Bridge - Full Integration
Integrates DIA TTS with the frontend system using actual DIA API calls
"""

import os
import sys
import logging
import tempfile
import requests
import json
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import soundfile as sf
import numpy as np

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

def call_dia_gradio_api(text: str, voice: str = "default") -> str:
    """Call the DIA Gradio API to generate speech"""
    try:
        # Prepare the request for Gradio API
        payload = {
            "data": [text],
            "fn_index": 0  # This might need to be adjusted based on the actual Gradio interface
        }
        
        logger.info(f"🎤 Calling DIA Gradio API with text: {text[:50]}...")
        
        # Make request to Gradio API
        response = requests.post(
            f"{DIA_API_URL}/api/predict",
            json=payload,
            timeout=60  # DIA can take time to generate
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ DIA API response received")
            
            # Extract audio data from response
            # The exact format depends on how Gradio returns the audio
            if "data" in result and len(result["data"]) > 0:
                audio_data = result["data"][0]
                
                # Save audio to temporary file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                    # Handle different audio formats that Gradio might return
                    if isinstance(audio_data, str) and audio_data.startswith("data:audio"):
                        # Base64 encoded audio
                        import base64
                        audio_bytes = base64.b64decode(audio_data.split(",")[1])
                        tmp_file.write(audio_bytes)
                    elif isinstance(audio_data, list):
                        # Raw audio data as array
                        sf.write(tmp_file.name, np.array(audio_data), 44100)
                    else:
                        # Try to write as-is
                        tmp_file.write(audio_data)
                    
                    return tmp_file.name
            else:
                logger.warning("No audio data in DIA response")
                return None
        else:
            logger.error(f"DIA API error: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"DIA API call failed: {e}")
        return None

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
        
        # Call DIA Gradio API
        audio_file = call_dia_gradio_api(request.text, request.voice)
        
        if audio_file and os.path.exists(audio_file):
            # Get audio duration
            try:
                audio_data, sample_rate = sf.read(audio_file)
                duration = len(audio_data) / sample_rate
            except:
                duration = len(request.text) * 0.08  # Estimate
            
            logger.info(f"✅ DIA Voice generated: {audio_file}")
            
            return VoiceResponse(
                audio_file=audio_file,
                duration=duration,
                sample_rate=request.sample_rate,
                success=True
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
                audio_file=audio_file,
                duration=duration,
                sample_rate=request.sample_rate,
                success=False
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
