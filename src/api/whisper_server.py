#!/usr/bin/env python3
"""
Whisper Server for Speech Recognition
Runs on port 8087
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging
import asyncio
import subprocess
import tempfile
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Whisper Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranscriptionResponse(BaseModel):
    success: bool
    text: str = None
    error: str = None
    confidence: float = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "whisper", "port": 8087}

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe audio file to text"""
    try:
        logger.info(f"Transcribing audio file: {file.filename}")
        
        # Create temporary file for audio input
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
            
            # Write uploaded file to temp file
            content = await file.read()
            temp_file.write(content)
        
        # Use Whisper via ollama (if available) or fallback to system
        try:
            # Try using ollama whisper first
            cmd = [
                "ollama", "run", "whisper",
                "--file", temp_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                transcribed_text = result.stdout.strip()
                confidence = 0.85  # Mock confidence
            else:
                # Fallback to system whisper if available
                cmd = ["whisper", temp_path, "--output_format", "txt"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    # Read the output file
                    output_file = temp_path.replace('.wav', '.txt')
                    if os.path.exists(output_file):
                        with open(output_file, 'r') as f:
                            transcribed_text = f.read().strip()
                        os.unlink(output_file)
                        confidence = 0.80
                    else:
                        transcribed_text = result.stdout.strip()
                        confidence = 0.75
                else:
                    # Final fallback - mock transcription
                    transcribed_text = "Audio transcription not available (whisper not installed)"
                    confidence = 0.0
                    
        except Exception as e:
            logger.warning(f"Whisper command failed: {e}")
            transcribed_text = "Audio transcription not available"
            confidence = 0.0
        
        # Clean up temp file
        os.unlink(temp_path)
        
        return TranscriptionResponse(
            success=True,
            text=transcribed_text,
            confidence=confidence
        )
        
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return TranscriptionResponse(
            success=False,
            error=f"Transcription failed: {str(e)}"
        )

@app.post("/transcribe-text", response_model=TranscriptionResponse)
async def transcribe_text(request: dict):
    """Mock transcription for text input (for testing)"""
    try:
        # Extract text from request
        text = request.get("text", "")
        logger.info(f"Mock transcribing text: {text[:50]}...")
        
        # Mock transcription - just return the input text
        return TranscriptionResponse(
            success=True,
            text=f"Transcribed: {text}",
            confidence=0.95
        )
        
    except Exception as e:
        logger.error(f"Mock transcription error: {e}")
        return TranscriptionResponse(
            success=False,
            error=f"Mock transcription failed: {str(e)}"
        )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Whisper Server",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "transcribe": "/transcribe",
            "transcribe-text": "/transcribe-text"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8087)
