#!/usr/bin/env python3
"""
Server Startup Script
Start both backend and frontend servers with proper error handling
"""

import subprocess
import time
import sys
import os
import signal
import threading
from pathlib import Path

class ServerManager:
    """Manages backend and frontend server processes."""
    
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = False
    
    def start_backend(self):
        """Start the backend server."""
        print("🚀 Starting Backend Server...")
        
        try:
            # Check if api_server.py exists
            if not Path("api_server.py").exists():
                print("❌ api_server.py not found")
                return False
            
            # Start backend server
            self.backend_process = subprocess.Popen(
                [sys.executable, "api_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            print("✅ Backend server started (PID: {})".format(self.backend_process.pid))
            return True
            
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the frontend server."""
        print("🌐 Starting Frontend Server...")
        
        try:
            # Check if frontend directory exists
            if not Path("frontend").exists():
                print("❌ Frontend directory not found")
                return False
            
            # Check if package.json exists
            if not Path("frontend/package.json").exists():
                print("❌ Frontend package.json not found")
                return False
            
            # Start frontend server
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd="frontend",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            print("✅ Frontend server started (PID: {})".format(self.frontend_process.pid))
            return True
            
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
    
    def check_servers(self):
        """Check if servers are running."""
        print("\n🔍 Checking server status...")
        
        # Check backend
        if self.backend_process and self.backend_process.poll() is None:
            print("✅ Backend server is running")
        else:
            print("❌ Backend server is not running")
        
        # Check frontend
        if self.frontend_process and self.frontend_process.poll() is None:
            print("✅ Frontend server is running")
        else:
            print("❌ Frontend server is not running")
    
    def stop_servers(self):
        """Stop both servers."""
        print("\n🛑 Stopping servers...")
        
        if self.backend_process:
            self.backend_process.terminate()
            print("✅ Backend server stopped")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            print("✅ Frontend server stopped")
        
        self.running = False
    
    def run(self):
        """Run both servers."""
        print("🌐 Starting Frontend and Backend Servers")
        print("=" * 50)
        
        # Start backend
        if not self.start_backend():
            print("❌ Failed to start backend server")
            return False
        
        # Wait a moment
        time.sleep(2)
        
        # Start frontend
        if not self.start_frontend():
            print("❌ Failed to start frontend server")
            self.stop_servers()
            return False
        
        # Wait for servers to start
        print("\n⏳ Waiting for servers to start...")
        time.sleep(5)
        
        # Check status
        self.check_servers()
        
        # Print URLs
        print("\n🌐 Server URLs:")
        print("   Backend:  http://localhost:8000")
        print("   Frontend: http://localhost:3000")
        print("   API Docs: http://localhost:8000/docs")
        
        print("\n📋 Available Endpoints:")
        print("   GET  /status - Server status")
        print("   GET  /models - Available models")
        print("   POST /chat - Chat endpoint")
        print("   GET  /health - Health check")
        
        print("\n🎯 Frontend Features:")
        print("   • AI Chat with 8 specialized models")
        print("   • Advanced chat features (bookmarks, likes)")
        print("   • Voice integration (speech-to-text, text-to-speech)")
        print("   • Real-time collaboration")
        print("   • Code editor with AI assistance")
        print("   • Multimodal image/document analysis")
        print("   • Learning dashboard with progress tracking")
        print("   • Performance monitoring")
        
        print("\n💡 Usage Instructions:")
        print("   1. Open http://localhost:3000 in your browser")
        print("   2. Navigate through the 7 panels using the sidebar")
        print("   3. Try different AI models and features")
        print("   4. Test voice, collaboration, and multimodal features")
        print("   5. Monitor performance in real-time")
        
        print("\n🛑 Press Ctrl+C to stop both servers")
        
        self.running = True
        
        try:
            # Keep running until interrupted
            while self.running:
                time.sleep(1)
                
                # Check if processes are still running
                if self.backend_process and self.backend_process.poll() is not None:
                    print("❌ Backend server stopped unexpectedly")
                    break
                
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("❌ Frontend server stopped unexpectedly")
                    break
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down servers...")
            self.stop_servers()
            print("✅ Servers stopped successfully")
        
        return True

def main():
    """Main function."""
    # Check if we're in the right directory
    if not Path("api_server.py").exists():
        print("❌ api_server.py not found. Please run from the project root.")
        return False
    
    if not Path("frontend").exists():
        print("❌ Frontend directory not found. Please run from the project root.")
        return False
    
    # Create server manager
    manager = ServerManager()
    
    # Run servers
    return manager.run()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
