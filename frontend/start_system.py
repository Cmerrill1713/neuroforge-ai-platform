#!/usr/bin/env python3
"""
NeuroForge System Startup Script
Ensures correct processes are running and prevents conflicts
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

class SystemManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.processes = {}
        
    def kill_existing_processes(self):
        """Kill existing conflicting processes"""
        print("🧹 Cleaning up existing processes...")
        
        # Kill any Python backends
        subprocess.run(["pkill", "-f", "consolidated_api_architecture.py"], 
                      capture_output=True)
        subprocess.run(["pkill", "-f", "fixed_chat_backend.py"], 
                      capture_output=True)
        subprocess.run(["pkill", "-f", "evolutionary_api_server_8005.py"], 
                      capture_output=True)
        subprocess.run(["pkill", "-f", "simple_tts_server.py"], 
                      capture_output=True)
        
        # Kill Next.js processes
        subprocess.run(["pkill", "-f", "next"], capture_output=True)
        
        time.sleep(2)
        
    def start_backend(self):
        """Start the correct backend"""
        print("🚀 Starting backend...")
        backend_cmd = [
            sys.executable, 
            str(self.project_root / "fixed_chat_backend.py")
        ]
        
        self.processes['backend'] = subprocess.Popen(
            backend_cmd, 
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for backend to start
        time.sleep(3)
        
        # Check if it's running
        if self.processes['backend'].poll() is None:
            print("✅ Backend started successfully")
        else:
            print("❌ Backend failed to start")
            stdout, stderr = self.processes['backend'].communicate()
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return False
        return True
    
    def start_rag_service(self):
        """Start RAG/Evolutionary service"""
        print("🧠 Starting RAG service...")
        rag_cmd = [
            sys.executable, 
            str(self.project_root / "src" / "api" / "evolutionary_api_server_8005.py")
        ]
        
        self.processes['rag'] = subprocess.Popen(
            rag_cmd, 
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(2)
        if self.processes['rag'].poll() is None:
            print("✅ RAG service started successfully")
            return True
        else:
            print("❌ RAG service failed to start")
            return False
    
    def start_tts_service(self):
        """Start TTS service"""
        print("🗣️  Starting TTS service...")
        tts_cmd = [
            sys.executable, 
            str(self.project_root / "src" / "api" / "simple_tts_server.py")
        ]
        
        self.processes['tts'] = subprocess.Popen(
            tts_cmd, 
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(2)
        if self.processes['tts'].poll() is None:
            print("✅ TTS service started successfully")
            return True
        else:
            print("❌ TTS service failed to start")
            return False
    
    def start_frontend(self):
        """Start frontend"""
        print("🌐 Starting frontend...")
        frontend_cmd = ["npm", "run", "dev", "--", "-p", "3000"]
        
        self.processes['frontend'] = subprocess.Popen(
            frontend_cmd, 
            cwd=self.project_root / "frontend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(5)
        if self.processes['frontend'].poll() is None:
            print("✅ Frontend started successfully")
            return True
        else:
            print("❌ Frontend failed to start")
            return False
    
    def check_services(self):
        """Check if all services are responding"""
        print("🔍 Checking service health...")
        
        services = {
            'Backend': ('http://localhost:8004/api/system/health', 8004),
            'RAG': ('http://localhost:8005/health', 8005),
            'TTS': ('http://localhost:8087/health', 8087),
            'Frontend': ('http://localhost:3000/', 3000)
        }
        
        import requests
        
        for name, (url, port) in services.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {name} (port {port}): OK")
                else:
                    print(f"⚠️  {name} (port {port}): HTTP {response.status_code}")
            except:
                print(f"❌ {name} (port {port}): Not responding")
    
    def cleanup(self, signum, frame):
        """Cleanup on exit"""
        print("\n🛑 Shutting down services...")
        for name, process in self.processes.items():
            if process.poll() is None:
                print(f"Stopping {name}...")
                process.terminate()
        
        # Force kill after timeout
        time.sleep(2)
        for name, process in self.processes.items():
            if process.poll() is None:
                process.kill()
        
        sys.exit(0)
    
    def run(self):
        """Main startup sequence"""
        print("🚀 NeuroForge System Startup")
        print("=" * 50)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)
        
        try:
            # Clean up existing processes
            self.kill_existing_processes()
            
            # Start services in order
            success = True
            
            success &= self.start_rag_service()
            success &= self.start_tts_service()
            success &= self.start_backend()
            success &= self.start_frontend()
            
            if success:
                print("\n🎉 All services started successfully!")
                self.check_services()
                
                print("\n📋 Service URLs:")
                print("  Frontend: http://localhost:3000")
                print("  Backend:  http://localhost:8004")
                print("  RAG API:  http://localhost:8005")
                print("  TTS API:  http://localhost:8087")
                
                print("\n💡 Press Ctrl+C to stop all services")
                
                # Keep running
                while True:
                    time.sleep(1)
                    
                    # Check if any process died
                    for name, process in self.processes.items():
                        if process.poll() is not None:
                            print(f"⚠️  {name} process died (exit code: {process.returncode})")
                            stdout, stderr = process.communicate()
                            if stderr:
                                print(f"Error output: {stderr.decode()[:200]}...")
            
            else:
                print("\n❌ Some services failed to start")
                sys.exit(1)
                
        except KeyboardInterrupt:
            self.cleanup(None, None)

if __name__ == "__main__":
    manager = SystemManager()
    manager.run()
