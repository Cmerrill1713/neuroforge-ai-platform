#!/usr/bin/env python3
"""
Production Chatterbox TTS Server with Edge TTS Fallback
Integrates with existing system, replaces DIA completely
"""

import asyncio
import json
import logging
import os
import threading
import time
import torch
import torchaudio as ta
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import edge_tts
from chatterbox.tts import ChatterboxTTS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionTTSManager:
    """Production TTS manager with Chatterbox primary and Edge TTS fallback"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.chatterbox_model = None
        self.chatterbox_loaded = False
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        self._loading = False
        
        # Voice profiles for both systems
        self.voice_profiles = {
            "assistant": {
                "chatterbox": {"exaggeration": 0.5, "cfg_weight": 0.5},
                "edge": {"voice": "en-US-AriaNeural", "rate": "0.9", "pitch": "+0%"},
                "description": "Friendly assistant voice"
            },
            "professional": {
                "chatterbox": {"exaggeration": 0.3, "cfg_weight": 0.7},
                "edge": {"voice": "en-US-GuyNeural", "rate": "0.8", "pitch": "+0%"},
                "description": "Professional male voice"
            },
            "narrator": {
                "chatterbox": {"exaggeration": 0.4, "cfg_weight": 0.6},
                "edge": {"voice": "en-GB-SoniaNeural", "rate": "0.7", "pitch": "-10%"},
                "description": "Clear narrator voice"
            },
            "excited": {
                "chatterbox": {"exaggeration": 0.8, "cfg_weight": 0.3},
                "edge": {"voice": "en-US-JennyNeural", "rate": "1.1", "pitch": "+10%"},
                "description": "Energetic and excited voice"
            },
            "calm": {
                "chatterbox": {"exaggeration": 0.2, "cfg_weight": 0.8},
                "edge": {"voice": "en-US-AriaNeural", "rate": "0.6", "pitch": "-5%"},
                "description": "Calm and soothing voice"
            },
            "news": {
                "chatterbox": {"exaggeration": 0.3, "cfg_weight": 0.9},
                "edge": {"voice": "en-US-GuyNeural", "rate": "0.8", "pitch": "+5%"},
                "description": "Authoritative news voice"
            }
        }
        
        # Load Chatterbox in background
        self._load_chatterbox_async()
        self._initialized = True
    
    def _load_chatterbox_async(self):
        """Load Chatterbox model in background thread"""
        if self._loading or self.chatterbox_loaded:
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
        
        # Get profile configuration
        profile_config = self.voice_profiles.get(voice_profile, self.voice_profiles["assistant"])
        
        # Try Chatterbox first if available and requested
        if use_chatterbox and self.chatterbox_loaded and self.chatterbox_model:
            try:
                logger.info(f"🎤 Generating with Chatterbox TTS: '{text[:50]}...'")
                
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
            logger.info(f"🎤 Generating with Edge TTS: '{text[:50]}...'")
            
            edge_config = profile_config["edge"]
            
            # Create SSML for better control
            ssml_text = f"<speak><prosody rate='{edge_config['rate']}' pitch='{edge_config['pitch']}'>{text}</prosody></speak>"
            
            # Generate with Edge TTS
            communicate = edge_tts.Communicate(ssml_text, edge_config['voice'])
            
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
                "voice": edge_config['voice'],
                "ssml": ssml_text
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

class ProductionTTSRequestHandler(BaseHTTPRequestHandler):
    """Production TTS request handler compatible with existing DIA API"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    @property
    def tts_manager(self):
        """Get TTS manager instance"""
        if not hasattr(self, '_tts_manager'):
            self._tts_manager = ProductionTTSManager()
        return self._tts_manager
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            if self.path == '/':
                self._send_homepage()
            elif self.path == '/status':
                self._send_status()
            elif self.path == '/profiles':
                self._send_profiles()
            else:
                self._send_404()
        except Exception as e:
            logger.error(f"❌ GET request failed: {e}")
            self._send_error(str(e))
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            if self.path == '/generate':
                self._handle_generate()
            else:
                self._send_404()
        except Exception as e:
            logger.error(f"❌ POST request failed: {e}")
            self._send_error(str(e))
    
    def _send_homepage(self):
        """Send homepage HTML"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Production TTS Server</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .method { color: #007bff; font-weight: bold; }
                .url { color: #28a745; font-family: monospace; }
                .status { background: #d4edda; padding: 10px; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎤 Production TTS Server</h1>
                <div class="status">
                    <h3>✅ System Status</h3>
                    <p><strong>Primary:</strong> Chatterbox TTS (GPU accelerated)</p>
                    <p><strong>Backup:</strong> Edge TTS (Microsoft cloud)</p>
                    <p><strong>Replaces:</strong> DIA TTS (deprecated)</p>
                </div>
                
                <h2>Available Endpoints:</h2>
                
                <div class="endpoint">
                    <span class="method">POST</span> <span class="url">/generate</span>
                    <p>Generate speech (compatible with DIA API)</p>
                    <pre>{
  "text": "Hello world!",
  "voice_profile": "assistant",
  "emotion": "neutral",
  "speed": "normal",
  "output_file": "output.mp3"
}</pre>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> <span class="url">/status</span>
                    <p>System status and engine availability</p>
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> <span class="url">/profiles</span>
                    <p>Available voice profiles</p>
                </div>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html_content.encode())
    
    def _send_status(self):
        """Send system status"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        status = self.tts_manager.get_status()
        self.wfile.write(json.dumps(status).encode())
    
    def _send_profiles(self):
        """Send available profiles"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        profiles = {}
        for name, config in self.tts_manager.voice_profiles.items():
            profiles[name] = {
                "description": config["description"],
                "chatterbox_params": config["chatterbox"],
                "edge_config": config["edge"]
            }
        
        self.wfile.write(json.dumps({
            "success": True,
            "profiles": profiles,
            "total_count": len(profiles)
        }).encode())
    
    def _handle_generate(self):
        """Handle speech generation"""
        # Read request data
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self._send_error("Invalid JSON")
            return
        
        # Extract parameters (compatible with DIA API)
        text = data.get('text', '')
        output_file = data.get('output_file', 'production_output.mp3')
        voice_profile = data.get('voice_profile', 'assistant')
        emotion = data.get('emotion', 'neutral')
        speed = data.get('speed', 'normal')
        use_chatterbox = data.get('use_chatterbox', True)
        
        if not text:
            self._send_error("Text is required")
            return
        
        # Generate speech
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                self.tts_manager.generate_speech(
                    text, output_file, voice_profile, emotion, speed, use_chatterbox
                )
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        finally:
            loop.close()
    
    def _send_404(self):
        """Send 404 response"""
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def _send_error(self, message):
        """Send error response"""
        self.send_response(500)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())

def start_production_server(port=8086):
    """Start the production TTS server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, ProductionTTSRequestHandler)
    
    logger.info(f"🎤 Production TTS Server starting on port {port}")
    logger.info(f"🌐 Server URL: http://localhost:{port}")
    logger.info(f"🎯 Primary: Chatterbox TTS (GPU accelerated)")
    logger.info(f"🔄 Backup: Edge TTS (Microsoft cloud)")
    logger.info(f"❌ Replaces: DIA TTS (deprecated)")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
        httpd.shutdown()

if __name__ == "__main__":
    print("🎤 Production TTS Server")
    print("=" * 60)
    print("🎯 Chatterbox TTS (Primary) + Edge TTS (Backup)")
    print("🚀 Replaces DIA completely - no more creepy robot voices!")
    print("=" * 60)
    
    start_production_server()
