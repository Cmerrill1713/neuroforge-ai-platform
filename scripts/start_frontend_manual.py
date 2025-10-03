#!/usr/bin/env python3
""'
Manual Frontend Startup Script
Start the frontend server and check for issues
""'

import subprocess
import time
import os
import sys
from pathlib import Path

def start_frontend():
    """TODO: Add docstring."""
    """Start the frontend server manually.""'
    print("🚀 Starting Frontend Server...')

    frontend_dir = Path("frontend')

    if not frontend_dir.exists():
        print("❌ Frontend directory not found!')
        return False

    # Change to frontend directory
    os.chdir(frontend_dir)

    try:
        # Start the development server
        process = subprocess.Popen(
            ["npm", "run", "dev'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print("✅ Frontend server starting...')
        print("⏳ Waiting for server to start...')

        # Wait a bit for the server to start
        time.sleep(10)

        # Check if the process is still running
        if process.poll() is None:
            print("✅ Frontend server is running!')
            print("🌐 Frontend should be available at: http://localhost:3000')
            return True
        else:
            print("❌ Frontend server failed to start!')
            stdout, stderr = process.communicate()
            print("STDOUT:', stdout)
            print("STDERR:', stderr)
            return False

    except Exception as e:
        print(f"❌ Error starting frontend: {e}')
        return False

def check_dependencies():
    """TODO: Add docstring."""
    """Check if dependencies are installed.""'
    print("📦 Checking dependencies...')

    frontend_dir = Path("frontend')
    node_modules = frontend_dir / "node_modules'

    if not node_modules.exists():
        print("❌ node_modules not found! Installing dependencies...')
        try:
            subprocess.run(["npm", "install'], cwd=frontend_dir, check=True)
            print("✅ Dependencies installed!')
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}')
            return False

    return True

def main():
    """TODO: Add docstring."""
    """Main function.""'
    print("🔧 Manual Frontend Startup')
    print("=' * 40)

    # Check dependencies
    if not check_dependencies():
        return

    # Start frontend
    if start_frontend():
        print("\n✅ Frontend started successfully!')
        print("🌐 Open http://localhost:3000 in your browser')
    else:
        print("\n❌ Failed to start frontend!')
        print("Check the error messages above for details.')

if __name__ == "__main__':
    main()
