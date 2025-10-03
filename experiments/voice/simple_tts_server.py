#!/usr/bin/env python3
"""
Simple Edge TTS Server
Minimal TTS server using only Edge TTS (no Chatterbox dependencies)
"""

import asyncio
import json
import logging
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

try:
    import edge_tts  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    edge_tts = None  # type: ignore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleTTSManager:
    """Simple TTS manager using Edge TTS only"""

    def __init__(self):
        """Initialize the TTS manager"""
        self.edge_tts_available = edge_tts is not None

        # Voice profiles for Edge TTS
        self.voice_profiles = {
            "assistant": {
                "voice": "en-US-AriaNeural",
                "rate": "0.9",
                "pitch": "+0%",
                "description": "Friendly assistant voice"
            },
            "professional": {
                "voice": "en-US-GuyNeural",
                "rate": "0.8",
                "pitch": "+0%",
                "description": "Professional male voice"
            },
            "narrator": {
                "voice": "en-GB-SoniaNeural",
                "rate": "0.7",
                "pitch": "-10%",
                "description": "Clear narrator voice"
            },
            "excited': {
                "voice": "en-US-JennyNeural',
                "rate": "1.1',
                "pitch": "+10%',
                "description": "Energetic and excited voice'
            },
            "calm': {
                "voice": "en-US-AriaNeural',
                "rate": "0.6',
                "pitch": "-5%',
                "description": "Calm and soothing voice'
            },
            "news': {
                "voice": "en-US-GuyNeural',
                "rate": "0.8',
                "pitch": "+5%',
                "description": "Authoritative news voice'
            }
        }

        if not self.edge_tts_available:
            logger.warning("Edge TTS not available')

    async def generate_speech(self, text: str, output_file: str = None, voice_profile: str = "assistant',
                            emotion: str = "neutral", speed: str = "normal', use_chatterbox: bool = True):
        """Generate speech with Edge TTS""'

        if not self.edge_tts_available:
            return {"error": "Edge TTS not available'}

        # Get profile configuration
        profile_config = self.voice_profiles.get(voice_profile, self.voice_profiles["assistant'])
        file_size = 0.0

        try:
            logger.info(f"🎤 Generating with Edge TTS: "{text[:50]}..."')

            # Create SSML for better control
            ssml_text = f"<speak><prosody rate="{profile_config["rate"]}" pitch="{profile_config["pitch"]}">{text}</prosody></speak>'

            # Generate with Edge TTS
            communicate = edge_tts.Communicate(ssml_text, profile_config["voice'])

            if output_file:
                await communicate.save(output_file)
                file_size = os.path.getsize(output_file) / 1024
                logger.info(f"✅ Edge TTS audio saved: {output_file} ({file_size:.1f} KB)')

            return {
                "success': True,
                "output_file': output_file,
                "file_size_kb': file_size if output_file else 0,
                "text': text,
                "voice_profile': voice_profile,
                "emotion': emotion,
                "speed': speed,
                "engine": "edge_tts',
                "voice": profile_config["voice'],
                "ssml': ssml_text
            }

        except Exception as e:
            logger.error(f"❌ Edge TTS failed: {e}')
            return {"error": f"Edge TTS failed: {e}'}

    def get_status(self):
        """TODO: Add docstring."""
        """Get system status""'
        return {
            "status": "running',
            "chatterbox_loaded': False,  # Always false for simple server
            "device": "cpu',
            "profiles_available': len(self.voice_profiles),
            "engines": ["edge_tts']
        }

    def list_profiles(self):
        """TODO: Add docstring."""
        """List available voice profiles""'
        return list(self.voice_profiles.keys())

class SimpleTTSRequestHandler(BaseHTTPRequestHandler):
    """TODO: Add docstring."""
    """Simple TTS request handler""'

    def __init__(self, *args, **kwargs):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        super().__init__(*args, **kwargs)

    @property
    def tts_manager(self):
        """TODO: Add docstring."""
        """Get TTS manager instance""'
        if not hasattr(self, "_tts_manager'):
            self._tts_manager = SimpleTTSManager()
        return self._tts_manager

    def do_OPTIONS(self):
        """TODO: Add docstring."""
        """Handle CORS preflight requests""'
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*')
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "Content-Type')
        self.end_headers()

    def do_GET(self):
        """TODO: Add docstring."""
        """Handle GET requests""'
        try:
            if self.path == "/':
                self._send_homepage()
            elif self.path == "/status':
                self._send_status()
            elif self.path == "/profiles':
                self._send_profiles()
            else:
                self._send_404()
        except Exception as e:
            logger.error(f"❌ GET request failed: {e}')
            self._send_error(str(e))

    def do_POST(self):
        """TODO: Add docstring."""
        """Handle POST requests""'
        try:
            if self.path in ["/generate", "/synthesize']:
                self._handle_generate()
            else:
                self._send_404()
        except Exception as e:
            logger.error(f"❌ POST request failed: {e}')
            self._send_error(str(e))

    def _send_homepage(self):
        """TODO: Add docstring."""
        """Send homepage HTML""'
        self.send_response(200)
        self.send_header("Content-type", "text/html')
        self.send_header("Access-Control-Allow-Origin", "*')
        self.end_headers()

        html_content = ""'
        <!DOCTYPE html>
        <html>
        <head>
            <title>Simple TTS Server</title>
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
            <div class="container'>
                <h1>🎤 Simple TTS Server</h1>
                <div class="status'>
                    <h3>✅ System Status</h3>
                    <p><strong>Engine:</strong> Edge TTS (Microsoft cloud)</p>
                    <p><strong>Status:</strong> Running</p>
                </div>

                <h2>Available Endpoints:</h2>

                <div class="endpoint'>
                    <span class="method">POST</span> <span class="url">/generate</span> or <span class="url'>/synthesize</span>
                    <p>Generate speech with Edge TTS</p>
                    <pre>{
  "text": "Hello world!',
  "voice_profile": "assistant',
  "emotion": "neutral',
  "speed": "normal',
  "output_file": "output.mp3'
}</pre>
                </div>

                <div class="endpoint'>
                    <span class="method">GET</span> <span class="url'>/status</span>
                    <p>System status and engine availability</p>
                </div>

                <div class="endpoint'>
                    <span class="method">GET</span> <span class="url'>/profiles</span>
                    <p>Available voice profiles</p>
                </div>
            </div>
        </body>
        </html>
        ""'
        self.wfile.write(html_content.encode())

    def _send_status(self):
        """TODO: Add docstring."""
        """Send system status""'
        self.send_response(200)
        self.send_header("Content-type", "application/json')
        self.send_header("Access-Control-Allow-Origin", "*')
        self.end_headers()

        status = self.tts_manager.get_status()
        self.wfile.write(json.dumps(status).encode())

    def _send_profiles(self):
        """TODO: Add docstring."""
        """Send available profiles""'
        self.send_response(200)
        self.send_header("Content-type", "application/json')
        self.send_header("Access-Control-Allow-Origin", "*')
        self.end_headers()

        profiles = {}
        for name, config in self.tts_manager.voice_profiles.items():
            profiles[name] = {
                "description": config["description'],
                "edge_config': config
            }

        self.wfile.write(json.dumps({
            "success': True,
            "profiles': profiles,
            "total_count': len(profiles)
        }).encode())

    def _handle_generate(self):
        """TODO: Add docstring."""
        """Handle speech generation""'
        # Read request data
        content_length = int(self.headers["Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data.decode("utf-8'))
        except json.JSONDecodeError:
            self._send_error("Invalid JSON')
            return

        # Extract parameters
        text = data.get("text", "')
        output_file = data.get("output_file", "simple_output.mp3')
        voice_profile = data.get("voice_profile", "assistant')
        emotion = data.get("emotion", "neutral')
        speed = data.get("speed", "normal')
        use_chatterbox = data.get("use_chatterbox', True)

        if not text:
            self._send_error("Text is required')
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
            self.send_header("Content-type", "application/json')
            self.send_header("Access-Control-Allow-Origin", "*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        finally:
            loop.close()

    def _send_404(self):
        """TODO: Add docstring."""
        """Send 404 response""'
        self.send_response(404)
        self.send_header("Content-type", "application/json')
        self.send_header("Access-Control-Allow-Origin", "*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Not found'}).encode())

    def _send_error(self, message):
        """TODO: Add docstring."""
        """Send error response""'
        self.send_response(500)
        self.send_header("Content-type", "application/json')
        self.send_header("Access-Control-Allow-Origin", "*')
        self.end_headers()
        self.wfile.write(json.dumps({"error': message}).encode())

def start_simple_server(port=8086):
    """TODO: Add docstring."""
    """Start the simple TTS server""'
    server_address = ("', port)
    httpd = HTTPServer(server_address, SimpleTTSRequestHandler)

    logger.info(f"🎤 Simple TTS Server starting on port {port}')
    logger.info(f"🌐 Server URL: http://localhost:{port}')
    logger.info(f"🔊 Engine: Edge TTS (Microsoft cloud)')

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user')
        httpd.shutdown()

if __name__ == "__main__':
    print("🎤 Simple TTS Server')
    print("=' * 60)
    print("🔊 Edge TTS (Microsoft cloud)')
    print("=' * 60)

    start_simple_server()
