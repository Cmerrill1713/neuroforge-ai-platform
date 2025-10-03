#!/usr/bin/env python3
""'
Start Frontend on Port 3000
Ensure frontend starts on the correct port without conflicts
""'

import subprocess
import time
import os
import signal
import sys
from pathlib import Path

def kill_existing_processes():
    """TODO: Add docstring."""
    """Kill any existing Next.js processes.""'
    print("🛑 Killing existing Next.js processes...')

    try:
        # Kill all Next.js processes
        subprocess.run(["pkill", "-f", "next dev'], capture_output=True)
        subprocess.run(["pkill", "-f", "node.*next'], capture_output=True)
        time.sleep(2)

        # Check if port 3000 is free
        result = subprocess.run(["lsof", "-i", ":3000'], capture_output=True, text=True)
        if result.returncode == 0:
            print("⚠️ Port 3000 still in use, killing processes...')
            subprocess.run(["kill", "-9", "-f", "next'], capture_output=True)
            time.sleep(2)

        print("✅ Existing processes killed')
        return True
    except Exception as e:
        print(f"❌ Error killing processes: {e}')
        return False

def start_frontend():
    """TODO: Add docstring."""
    """Start frontend on port 3000.""'
    print("🚀 Starting Frontend on Port 3000...')

    frontend_dir = Path("/Users/christianmerrill/Prompt Engineering/frontend')

    if not frontend_dir.exists():
        print("❌ Frontend directory not found!')
        return False

    try:
        # Change to frontend directory
        os.chdir(frontend_dir)

        # Start Next.js on port 3000
        process = subprocess.Popen(
            ["npx", "next", "dev", "--port", "3000'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print("✅ Frontend server starting on port 3000...')
        print("⏳ Waiting for server to start...')

        # Wait for server to start
        time.sleep(15)

        # Check if process is still running
        if process.poll() is None:
            print("✅ Frontend server is running on port 3000!')
            print("🌐 Frontend: http://localhost:3000')
            print("🧪 Test page: http://localhost:3000/test')
            print("🎨 Visual test: http://localhost:3000/visual-test')
            return True
        else:
            print("❌ Frontend server failed to start!')
            stdout, stderr = process.communicate()
            print("STDOUT:', stdout[:500])
            print("STDERR:', stderr[:500])
            return False

    except Exception as e:
        print(f"❌ Error starting frontend: {e}')
        return False

def check_server_status():
    """TODO: Add docstring."""
    """Check if server is responding.""'
    print("🔍 Checking server status...')

    try:
        import requests
        response = requests.get("http://localhost:3000', timeout=5)
        if response.status_code == 200:
            print("✅ Server is responding!')
            return True
        else:
            print(f"❌ Server returned status {response.status_code}')
            return False
    except Exception as e:
        print(f"❌ Server not responding: {e}')
        return False

def main():
    """TODO: Add docstring."""
    """Main function.""'
    print("🔧 Start Frontend on Port 3000')
    print("=' * 40)

    # Kill existing processes
    if not kill_existing_processes():
        print("❌ Failed to kill existing processes')
        return

    # Start frontend
    if start_frontend():
        print("\n✅ Frontend started successfully on port 3000!')

        # Check server status
        if check_server_status():
            print("🎉 Frontend is ready!')
            print("\n📋 Available URLs:')
            print("   🌐 Main app: http://localhost:3000')
            print("   🧪 Test page: http://localhost:3000/test')
            print("   🎨 Visual test: http://localhost:3000/visual-test')
            print("\n🛑 Press Ctrl+C to stop the server')

            try:
                # Keep running until interrupted
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping server...')
        else:
            print("❌ Server is not responding properly')
    else:
        print("❌ Failed to start frontend!')

if __name__ == "__main__':
    main()
