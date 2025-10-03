#!/usr/bin/env python3
"""
TTS Server - Text-to-Speech using Chatterbox TTS with Edge TTS fallback
Production-ready TTS server with Chatterbox primary and Edge TTS backup
"""

import asyncio
import json
import logging
import os
import threading
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

try:
    import torch  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    torch = None  # type: ignore

try:
    import torchaudio as ta  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    ta = None  # type: ignore

try:
    import edge_tts  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    edge_tts = None  # type: ignore

try:
    from chatterbox.tts import ChatterboxTTS  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    ChatterboxTTS = None  # type: ignore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TTS Server", description="Text-to-Speech using Chatterbox TTS with Edge TTS fallback")

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
    voice: str = "assistant"
    speed: float = 1.0
    emotion: Optional[str] = "neutral"
    use_chatterbox: Optional[bool] = True

class TTSResponse(BaseModel):
    success: bool
    audio_file: Optional[str] = None
    play_command: Optional[str] = None
    error: Optional[str] = None
    text: str
    voice: str
    speed: float
    engine: Optional[str] = None

class ChatterboxTTSManager:
    """Chatterbox TTS manager with Edge TTS fallback"""
    _instance = None
    _initialized = False

    def __new__(cls):
        """Create singleton instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the TTS manager"""
        if self._initialized:
            return

        self.chatterbox_model = None
        self.chatterbox_loaded = False
        if torch and hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            self.device = "mps"
        else:
            self.device = "cpu"
        self._loading = False
        self.chatterbox_supported = all(dep is not None for dep in (ChatterboxTTS, torch, ta))

        # Voice profiles for both systems - feminine, sultry tones
        self.voice_profiles = {
            "assistant": {
                "chatterbox": {"exaggeration": 0.4, "cfg_weight": 0.4},
                "edge": {"voice": "en-US-AriaNeural", "rate": "0.9", "pitch": "+0%"},
                "description": "Sultry feminine assistant voice"
            },
            "sultry": {
                "chatterbox": {"exaggeration": 0.4, "cfg_weight": 0.4},
                "edge": {"voice": "en-US-AriaNeural", "rate": "0.8", "pitch": "+5%"},
                "description": "Sultry feminine voice"
            },
            "seductive": {
                "chatterbox": {"exaggeration": 0.5, "cfg_weight": 0.3},
                "edge": {"voice": "en-US-AriaNeural", "rate": "0.7", "pitch": "+10%"},
                "description": "Seductive feminine voice"
            },
            "intimate": {
                "chatterbox": {"exaggeration": 0.6, "cfg_weight": 0.2},
                "edge": {"voice": "en-US-AriaNeural", "rate": "0.6", "pitch": "+15%"},
                "description": "Intimate whisper voice"
            },
            "confident": {
                "chatterbox": {"exaggeration": 0.3, "cfg_weight": 0.5},
                "edge": {"voice": "en-US-AriaNeural", "rate": "0.8", "pitch": "+5%"},
                "description": "Confident feminine voice"
            },
            "honey": {
                "chatterbox": {"exaggeration": 0.4, "cfg_weight": 0.4},
                "edge": {"voice": "en-US-AriaNeural", "rate": "0.7", "pitch": "+8%"},
                "description": "Honey-smooth feminine voice"
            },
            "sonia_clean": {
                "chatterbox": {"exaggeration": 0.3, "cfg_weight": 0.6},  # More natural, feminine settings
                "edge": {"voice": "en-GB-SoniaNeural", "rate": "1.2", "pitch": "+5%"},  # Faster rate for speed
                "description": "Sonia - Fast local Chatterbox voice with feminine characteristics"
            }
        }

        # Load Chatterbox in background
        if self.chatterbox_supported:
            self._load_chatterbox_async()
        else:
            logger.info("Chatterbox dependencies unavailable; using Edge TTS only")
        self._initialized = True

    def _load_chatterbox_async(self):
        """Load Chatterbox model in background thread"""
        if not self.chatterbox_supported or self._loading or self.chatterbox_loaded:
            return

        self._loading = True

        def load_model():
            try:
                logger.info(f"🔄 Loading Chatterbox TTS on {self.device}...")
                self.chatterbox_model = ChatterboxTTS.from_pretrained(device=self.device)
                self.chatterbox_loaded = True
                logger.info("✅ Chatterbox TTS loaded successfully!")
            except Exception as e:
                logger.error(f"❌ Failed to load Chatterbox TTS: {e}")
                logger.info("🔄 Will use Edge TTS as primary")
            finally:
                self._loading = False

        thread = threading.Thread(target=load_model, daemon=True)
        thread.start()

    async def generate_speech(self, text: str, output_file: str = None, voice_profile: str = "assistant",
                            emotion: str = "neutral", speed: str = "normal", use_chatterbox: bool = True):
        """Generate speech with Chatterbox primary, Edge TTS fallback"""
        
        # Use Chatterbox for fast local processing (it's already loaded)
        if voice_profile == "sonia_clean":
            use_chatterbox = True
            logger.info("🎭 Using Chatterbox TTS for fast local Sonia voice generation")

        # Get profile configuration
        profile_config = self.voice_profiles.get(voice_profile, self.voice_profiles["assistant"])
        file_size = 0.0

        # Try Chatterbox first if available and requested
        if use_chatterbox and self.chatterbox_loaded and self.chatterbox_model and ta is not None:
            try:
                logger.info(f"🎤 Generating with Chatterbox TTS: \"{text[:50]}...\"")

                # Adjust parameters based on emotion and speed
                chatterbox_params = profile_config["chatterbox"].copy()

                # Emotion adjustments
                if emotion == "excited":
                    chatterbox_params["exaggeration"] = min(0.9, chatterbox_params["exaggeration"] + 0.3)
                    chatterbox_params["cfg_weight"] = max(0.2, chatterbox_params["cfg_weight"] - 0.2)
                elif emotion == "calm":
                    chatterbox_params["exaggeration"] = max(0.1, chatterbox_params["exaggeration"] - 0.2)
                    chatterbox_params["cfg_weight"] = min(0.9, chatterbox_params["cfg_weight"] + 0.2)

                # Speed adjustments
                if speed == "fast":
                    chatterbox_params["cfg_weight"] = max(0.2, chatterbox_params["cfg_weight"] - 0.1)
                elif speed == "slow":
                    chatterbox_params["cfg_weight"] = min(0.9, chatterbox_params["cfg_weight"] + 0.1)

                # Generate with Chatterbox
                wav = self.chatterbox_model.generate(
                    text,
                    exaggeration=chatterbox_params["exaggeration"],
                    cfg_weight=chatterbox_params["cfg_weight"]
                )

                if output_file:
                    ta.save(output_file, wav, self.chatterbox_model.sr)
                    file_size = os.path.getsize(output_file) / 1024
                    logger.info(f"✅ Chatterbox audio saved: {output_file} ({file_size:.1f} KB)")

                return {
                    "success": True,
                    "output_file": output_file,
                    "file_size_kb": file_size if output_file else 0,
                    "text": text,
                    "voice_profile": voice_profile,
                    "emotion": emotion,
                    "speed": speed,
                    "engine": "chatterbox",
                    "parameters": chatterbox_params
                }

            except Exception as e:
                logger.warning(f"⚠️ Chatterbox failed: {e}")
                logger.info("🔄 Falling back to Edge TTS...")

        # Fallback to Edge TTS
        try:
            if edge_tts is None:
                raise RuntimeError("Edge TTS dependency not available")
            logger.info(f"🎤 Generating with Edge TTS: \"{text[:50]}...\"")

            edge_config = profile_config["edge"]

            # Generate with Edge TTS (no SSML to avoid "prosody" being spoken)
            communicate = edge_tts.Communicate(text, edge_config["voice"])

            if output_file:
                await communicate.save(output_file)
                file_size = os.path.getsize(output_file) / 1024
                logger.info(f"✅ Edge TTS audio saved: {output_file} ({file_size:.1f} KB)")

            return {
                "success": True,
                "output_file": output_file,
                "file_size_kb": file_size if output_file else 0,
                "text": text,
                "voice_profile": voice_profile,
                "emotion": emotion,
                "speed": speed,
                "engine": "edge_tts",
                "voice": edge_config["voice"]
            }

        except Exception as e:
            logger.error(f"❌ Edge TTS also failed: {e}")
            return {"error": f"Both TTS engines failed: {e}"}

    def get_status(self):
        """Get system status"""
        return {
            "status": "running",
            "chatterbox_loaded": self.chatterbox_loaded,
            "device": self.device,
            "profiles_available": len(self.voice_profiles),
            "engines": ["chatterbox", "edge_tts"]
        }

    def list_profiles(self):
        """List available voice profiles"""
        return list(self.voice_profiles.keys())

# Initialize TTS manager
tts_manager = ChatterboxTTSManager()

@app.get("/")
async def root():
    """Root endpoint with server info"""
    return {
        "service": "TTS Server",
        "description": "Text-to-Speech using Chatterbox TTS with Edge TTS fallback",
        "endpoints": {
            "POST /synthesize": "Generate speech from text",
            "GET /voices": "List available voices",
            "GET /health": "Health check",
            "GET /status": "System status",
            "GET /profiles": "Available voice profiles"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "TTS Server"}

@app.get("/status")
async def get_status():
    """Get system status"""
    return tts_manager.get_status()

@app.get("/voices")
async def get_voices():
    """Get available voices"""
    profiles = {}
    for name, config in tts_manager.voice_profiles.items():
        profiles[name] = {
            "id": name,
            "name": name.title(),
            "description": config["description"]
        }
    
    return {"voices": list(profiles.values())}

@app.get("/profiles")
async def get_profiles():
    """Get available voice profiles with details"""
    profiles = {}
    for name, config in tts_manager.voice_profiles.items():
        profiles[name] = {
            "description": config["description"],
            "chatterbox_params": config["chatterbox"],
            "edge_config": config["edge"]
        }

    return {
        "success": True,
        "profiles": profiles,
        "total_count": len(profiles)
    }

@app.post("/synthesize", response_model=TTSResponse)
async def synthesize_speech(request: TTSRequest):
    """Generate speech from text using Chatterbox TTS with Edge TTS fallback"""
    try:
        logger.info(f"Generating speech for: {request.text[:50]}...")
        
        # Convert speed to string for compatibility
        speed_str = "normal"
        if request.speed > 1.2:
            speed_str = "fast"
        elif request.speed < 0.8:
            speed_str = "slow"
        
        # Generate speech with actual audio file
        import tempfile
        import os
        from datetime import datetime
        
        # Create a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"female_voice_{timestamp}.wav"
        
        result = await tts_manager.generate_speech(
            text=request.text,
            output_file=output_file,
            voice_profile=request.voice,
            emotion=request.emotion or "neutral",
            speed=speed_str,
            use_chatterbox=request.use_chatterbox
        )
        
        if "error" in result:
            logger.error(f"TTS generation failed: {result['error']}")
            return TTSResponse(
                success=False,
                error=result["error"],
                text=request.text,
                voice=request.voice,
                speed=request.speed
            )
        
        # Return success with audio file information
        logger.info(f"Successfully generated speech using {result['engine']}")
        
        return TTSResponse(
            success=True,
            text=request.text,
            voice=request.voice,
            speed=request.speed,
            engine=result["engine"],
            audio_file=output_file if result.get("success") else None,
            play_command=f"afplay \"{output_file}\"" if result.get("success") and os.path.exists(output_file) else None
        )
        
    except Exception as e:
        logger.error(f"TTS synthesis error: {e}")
        return TTSResponse(
            success=False,
            error=f"TTS synthesis error: {str(e)}",
            text=request.text,
            voice=request.voice,
            speed=request.speed
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8087)