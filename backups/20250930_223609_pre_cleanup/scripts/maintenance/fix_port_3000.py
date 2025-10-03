#!/usr/bin/env python3
""'
Fix Port 3000 Configuration
Comprehensive port management and frontend startup
""'

import subprocess
import time
import os
import signal
import sys
from pathlib import Path

def kill_all_node_processes():
    """TODO: Add docstring."""
    """Kill all Node.js processes.""'
    print("🛑 Killing all Node.js processes...')

    try:
        # Kill all node processes
        subprocess.run(["killall", "node'], capture_output=True)
        subprocess.run(["pkill", "-f", "next'], capture_output=True)
        subprocess.run(["pkill", "-f", "node'], capture_output=True)
        time.sleep(3)
        print("✅ All Node.js processes killed')
        return True
    except Exception as e:
        print(f"❌ Error killing processes: {e}')
        return False

def check_port_3000():
    """TODO: Add docstring."""
    """Check if port 3000 is free.""'
    print("🔍 Checking port 3000...')

    try:
        result = subprocess.run(["lsof", "-i", ":3000'], capture_output=True, text=True)
        if result.returncode == 0:
            print("⚠️ Port 3000 is still in use:')
            print(result.stdout)
            return False
        else:
            print("✅ Port 3000 is free')
            return True
    except Exception as e:
        print(f"❌ Error checking port: {e}')
        return False

def start_frontend_on_3000():
    """TODO: Add docstring."""
    """Start frontend on port 3000.""'
    print("🚀 Starting frontend on port 3000...')

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

        print("✅ Frontend server starting...')

        # Wait and check output
        time.sleep(5)

        # Check if process is still running
        if process.poll() is None:
            print("✅ Frontend server is running!')
            return True
        else:
            stdout, stderr = process.communicate()
            print("❌ Frontend server failed to start!')
            print("STDOUT:', stdout[:500])
            print("STDERR:', stderr[:500])
            return False

    except Exception as e:
        print(f"❌ Error starting frontend: {e}')
        return False

def test_frontend_connection():
    """TODO: Add docstring."""
    """Test if frontend is responding.""'
    print("🔍 Testing frontend connection...')

    try:
        import requests
        response = requests.get("http://localhost:3000', timeout=10)
        if response.status_code == 200:
            print("✅ Frontend is responding!')
            return True
        else:
            print(f"❌ Frontend returned status {response.status_code}')
            return False
    except Exception as e:
        print(f"❌ Frontend not responding: {e}')
        return False

def main():
    """TODO: Add docstring."""
    """Main function.""'
    print("🔧 Fix Port 3000 Configuration')
    print("=' * 40)

    # Step 1: Kill all Node.js processes
    if not kill_all_node_processes():
        print("❌ Failed to kill processes')
        return

    # Step 2: Check port 3000
    if not check_port_3000():
        print("❌ Port 3000 is still in use')
        return

    # Step 3: Start frontend
    if start_frontend_on_3000():
        print("✅ Frontend started successfully!')

        # Step 4: Test connection
        time.sleep(10)  # Wait for server to fully start
        if test_frontend_connection():
            print("\n🎉 Frontend is ready on port 3000!')
            print("🌐 Main app: http://localhost:3000')
            print("🧪 Test page: http://localhost:3000/test')
            print("🎨 Visual test: http://localhost:3000/visual-test')
        else:
            print("❌ Frontend is not responding')
    else:
        print("❌ Failed to start frontend')

if __name__ == "__main__':
    main()
