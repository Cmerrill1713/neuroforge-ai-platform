#!/usr/bin/env python3
"""
Simple Edge Server - Lightweight backend for AI chat
Compatible with existing frontend and TTS integration
"""

import asyncio
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleEdgeRequestHandler(BaseHTTPRequestHandler):
    """Simple request handler for AI chat backend"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
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
            elif self.path == '/models/status':
                self._send_models_status()
            elif self.path.startswith('/api/agents'):
                self._send_agents()
            else:
                self._send_404()
        except Exception as e:
            logger.error(f"❌ GET request failed: {e}")
            self._send_error(str(e))
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            if self.path.startswith('/api/chat'):
                self._handle_chat()
            else:
                self._send_404()
        except Exception as e:
            logger.error(f"❌ POST request failed: {e}")
            self._send_error(str(e))
    
    def _send_homepage(self):
        """Send homepage"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "message": "Agentic LLM Core API",
            "version": "1.0.0",
            "status": "running",
            "endpoints": ["/status", "/api/agents", "/api/chat"],
            "tts_integration": "http://localhost:8086"
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def _send_status(self):
        """Send system status"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        status = {
            "status": "running",
            "backend": "simple_edge_server",
            "tts_server": "http://localhost:8086",
            "frontend": "http://localhost:3000",
            "uptime": time.time()
        }
        
        self.wfile.write(json.dumps(status).encode())
    
    def _send_models_status(self):
        """Send models status"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        models_status = {
            "status": "running",
            "models": {
                "llm": {
                    "status": "active",
                    "provider": "simple_edge_server",
                    "type": "text_generation"
                },
                "tts": {
                    "status": "active", 
                    "provider": "chatterbox_tts",
                    "fallback": "edge_tts",
                    "endpoint": "http://localhost:8086"
                }
            },
            "total_models": 2
        }
        
        self.wfile.write(json.dumps(models_status).encode())
    
    def _send_agents(self):
        """Send available agents"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        agents = [
            {"id": "assistant", "name": "AI Assistant", "description": "General purpose AI assistant"},
            {"id": "creative", "name": "Creative Writer", "description": "Creative writing and storytelling"},
            {"id": "technical", "name": "Technical Expert", "description": "Technical problem solving"},
            {"id": "educational", "name": "Educational Tutor", "description": "Learning and teaching"},
            {"id": "business", "name": "Business Advisor", "description": "Business strategy and advice"},
            {"id": "health", "name": "Health Assistant", "description": "Health and wellness guidance"},
            {"id": "entertainment", "name": "Entertainment", "description": "Fun and entertainment"},
            {"id": "research", "name": "Research Assistant", "description": "Research and analysis"}
        ]
        
        response = {
            "success": True,
            "agents": agents,
            "total": len(agents)
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def _handle_chat(self):
        """Handle chat requests"""
        # Read request data
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self._send_error("Invalid JSON")
            return
        
        message = data.get('message', '')
        agent_id = data.get('agent', 'assistant')
        
        if not message:
            self._send_error("Message is required")
            return
        
        # Generate response
        response_text = self._generate_response(message, agent_id)
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "success": True,
            "message": response_text,
            "agent": agent_id,
            "timestamp": time.time(),
            "tts_ready": True
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def _generate_response(self, message: str, agent_id: str) -> str:
        """Generate AI response based on agent type"""
        
        # Simple response generation based on agent type
        responses = {
            "assistant": f"I understand you're asking: '{message}'. As your AI assistant, I'm here to help with any questions or tasks you might have. How can I assist you further?",
            
            "creative": f"What an interesting prompt: '{message}'. Let me craft something creative for you. Here's a creative response that builds on your idea...",
            
            "technical": f"From a technical perspective regarding '{message}', I can help analyze this systematically. Let me break down the technical aspects...",
            
            "educational": f"Great question: '{message}'. Let me explain this in a way that's easy to understand. Here's what you should know...",
            
            "business": f"Regarding your business inquiry about '{message}', here are some strategic considerations and recommendations...",
            
            "health": f"Thank you for sharing: '{message}'. While I can provide general wellness information, please consult healthcare professionals for medical advice...",
            
            "entertainment": f"Fun topic: '{message}'! Let me entertain you with some interesting facts and amusing perspectives...",
            
            "research": f"Research question: '{message}'. Let me help you explore this topic systematically with evidence-based insights..."
        }
        
        return responses.get(agent_id, responses["assistant"])
    
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

def start_simple_edge_server(port=8002):
    """Start the simple edge server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleEdgeRequestHandler)
    
    logger.info(f"🚀 Simple Edge Server starting on port {port}")
    logger.info(f"🌐 Server URL: http://localhost:{port}")
    logger.info(f"🎯 Compatible with frontend on port 3000")
    logger.info(f"🔗 TTS integration: http://localhost:8086")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")

if __name__ == "__main__":
    start_simple_edge_server()
