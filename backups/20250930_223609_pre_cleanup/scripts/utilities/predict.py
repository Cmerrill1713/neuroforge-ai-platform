#!/usr/bin/env python3
"""
Resource-Conscious Vision Model Prediction Script for NeuroForge
Uses the API server instead of loading models locally to save memory.
"""

import argparse
import sys
import requests
from pathlib import Path
from PIL import Image
import io

def predict_via_api(image_path: str, prompt: str = None, api_url: str = "http://localhost:8004"):
    """Generate prediction using the API server instead of loading models locally."""
    try:
        # Load and validate image
        image = Image.open(image_path).convert('RGB')
        print(f"Loaded image: {image_path} ({image.size})")
        
        # Prepare the request
        message = prompt or "Describe this image in detail."
        
        # Convert image to bytes for multipart upload
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Send request to API server
        print(f"Sending request to {api_url}/api/chat/upload...")
        files = {
            'file': (image_path, img_bytes, 'image/png')
        }
        data = {
            'message': message
        }
        
        response = requests.post(f"{api_url}/api/chat/upload", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result['response']}")
            print(f"Agent Used: {result['agent_used']}")
            print(f"Confidence: {result['confidence']}")
            print(f"Response Time: {result['response_time']:.2f}s")
            return result
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def check_server_status(api_url: str = "http://localhost:8004"):
    """Check if the API server is running."""
    try:
        response = requests.get(f"{api_url}/api/chat/", timeout=5)
        # Method Not Allowed (405) means server is running but endpoint expects POST
        return response.status_code in [200, 404, 405]
    except:
        return False

def main():
    parser = argparse.ArgumentParser(description="Resource-Conscious Vision Model Prediction Script")
    parser.add_argument("--image-file", required=True,
                      help="Path to input image file")
    parser.add_argument("--prompt", 
                      help="Optional prompt/question for the image")
    parser.add_argument("--api-url", default="http://localhost:8004",
                      help="API server URL")
    
    args = parser.parse_args()
    
    # Validate image file
    if not Path(args.image_file).exists():
        print(f"Error: Image file '{args.image_file}' not found")
        sys.exit(1)
    
    # Check if server is running
    if not check_server_status(args.api_url):
        print(f"Error: API server at {args.api_url} is not running")
        print("Please start the server first with:")
        print("  python3 -m uvicorn src.api.consolidated_api_architecture:create_consolidated_app --host 0.0.0.0 --port 8004")
        sys.exit(1)
    
    print("✅ Using API server - no local model loading required!")
    print("💾 This saves ~7GB of memory by reusing the server's loaded model")
    
    # Generate prediction via API
    result = predict_via_api(args.image_file, args.prompt, args.api_url)
    
    if result is None:
        sys.exit(1)

if __name__ == "__main__":
    main()
