#!/usr/bin/env python3
""'
Setup script for IndyDevDan Content Crawler
""'

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """TODO: Add docstring."""
    """Install required packages""'
    print("📦 Installing crawler requirements...')

    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.crawler.txt'
        ])
        print("✅ Requirements installed successfully!')
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}')
        return False

def setup_environment():
    """TODO: Add docstring."""
    """Setup environment variables""'
    print("🔧 Setting up environment...')

    # Create .env file if it doesn't exist
    env_file = Path(".env')
    if not env_file.exists():
        with open(env_file, "w') as f:
            f.write("# IndyDevDan Crawler Environment Variables\n')
            f.write("# Get your GitHub token from: https://github.com/settings/tokens\n')
            f.write("GITHUB_TOKEN=your_github_token_here\n')

        print("📝 Created .env file - please add your GitHub token')

    print("✅ Environment setup complete!')

def main():
    """TODO: Add docstring."""
    """Main setup function""'
    print("🚀 IndyDevDan Content Crawler Setup')
    print("=' * 40)

    # Install requirements
    if not install_requirements():
        print("❌ Setup failed at requirements installation')
        return

    # Setup environment
    setup_environment()

    print("\n🎉 Setup complete!')
    print("\n📋 Next steps:')
    print("1. Add your GitHub token to the .env file')
    print("2. Run: python indydevdan_content_crawler.py')
    print("3. Enter the YouTube channel URL when prompted')
    print("\n💡 Note: GitHub token is optional but recommended for higher rate limits')

if __name__ == "__main__':
    main()
