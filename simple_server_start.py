#!/usr/bin/env python3
"""
Simple Server Starter
Start frontend and backend servers with proper error handling
"""

import subprocess
import time
import os
import signal
import sys
from pathlib import Path

class SimpleServerStarter:
    def __init__(self):
        self.project_root = Path("/Users/christianmerrill/Prompt Engineering")
        self.frontend_dir = self.project_root / "frontend"
        self.frontend_process = None
        self.backend_process = None
    
    def start_frontend(self):
        """Start the frontend development server."""
        print("🌐 Starting Frontend Server...")
        
        try:
            os.chdir(self.frontend_dir)
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("✅ Frontend server started (PID: {})".format(self.frontend_process.pid))
            return True
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
    
    def start_backend(self):
        """Start the backend API server."""
        print("🚀 Starting Backend Server...")
        
        try:
            os.chdir(self.project_root)
            self.backend_process = subprocess.Popen(
                ["python3", "api_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("✅ Backend server started (PID: {})".format(self.backend_process.pid))
            return True
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def check_servers(self):
        """Check if servers are running."""
        print("🔍 Checking servers...")
        
        # Check frontend
        if self.frontend_process and self.frontend_process.poll() is None:
            print("✅ Frontend is running")
        else:
            print("❌ Frontend is not running")
            if self.frontend_process:
                stdout, stderr = self.frontend_process.communicate(timeout=1)
                print(f"Frontend stdout: {stdout[:200]}")
                print(f"Frontend stderr: {stderr[:200]}")
        
        # Check backend
        if self.backend_process and self.backend_process.poll() is None:
            print("✅ Backend is running")
        else:
            print("❌ Backend is not running")
            if self.backend_process:
                stdout, stderr = self.backend_process.communicate(timeout=1)
                print(f"Backend stdout: {stdout[:200]}")
                print(f"Backend stderr: {stderr[:200]}")
    
    def stop_servers(self):
        """Stop all servers."""
        print("🛑 Stopping servers...")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            print("✅ Frontend stopped")
        
        if self.backend_process:
            self.backend_process.terminate()
            print("✅ Backend stopped")
    
    def run(self):
        """Run the server starter."""
        print("🔧 Simple Server Starter")
        print("=" * 40)
        
        # Start servers
        frontend_ok = self.start_frontend()
        time.sleep(2)
        backend_ok = self.start_backend()
        
        # Wait for servers to start
        print("⏳ Waiting for servers to start...")
        time.sleep(10)
        
        # Check servers
        self.check_servers()
        
        if frontend_ok or backend_ok:
            print("\n✅ Servers started!")
            print("🌐 Frontend: http://localhost:3000")
            print("🧪 Test page: http://localhost:3000/test")
            print("🚀 Backend: http://localhost:8000")
            print("📚 API docs: http://localhost:8000/docs")
            print("\nPress Ctrl+C to stop servers...")
            
            try:
                # Keep running until interrupted
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping servers...")
                self.stop_servers()
        else:
            print("\n❌ Failed to start servers!")

def main():
    starter = SimpleServerStarter()
    starter.run()

if __name__ == "__main__":
    main()
