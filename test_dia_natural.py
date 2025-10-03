#!/usr/bin/env python3
"""
Test DIA Natural Voice using Hugging Face Inference API
"""

import os
import requests
import json

def test_dia_natural_voice():
    """Test DIA natural voice generation"""
    
    # Check if HF_TOKEN is set
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("❌ HF_TOKEN environment variable not set!")
        print("Please set your Hugging Face token:")
        print("export HF_TOKEN='your_token_here'")
        return False
    
    print("🎤 Testing DIA Natural Voice...")
    print("=" * 50)
    
    # Test the DIA Natural Voice API
    url = "http://localhost:8092/synthesize"
    data = {
        "text": "Hello! I am DIA, your natural-sounding voice assistant. I speak with clarity and naturalness.",
        "voice": "dia_natural"
    }
    
    try:
        response = requests.post(url, json=data, timeout=60)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', False)}")
            print(f"Message: {result.get('message', 'No message')}")
            print(f"Audio file: {result.get('audio_file', 'None')}")
            print(f"Duration: {result.get('duration', 0):.2f} seconds")
            
            if result.get('success'):
                print("✅ DIA Natural Voice generated successfully!")
                return True
            else:
                print("❌ DIA Natural Voice generation failed")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_hf_inference_direct():
    """Test Hugging Face Inference API directly"""
    
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("❌ HF_TOKEN not set")
        return False
    
    print("\n🔗 Testing Hugging Face Inference API directly...")
    print("=" * 50)
    
    try:
        url = "https://api-inference.huggingface.co/models/nari-labs/Dia-1.6B"
        headers = {
            "Authorization": f"Bearer {hf_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": "Hello! This is a test of DIA natural voice.",
            "parameters": {
                "provider": "fal-ai"
            }
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Direct API call successful!")
            print(f"Audio size: {len(response.content)} bytes")
            
            # Save the audio
            with open("dia_direct_test.wav", "wb") as f:
                f.write(response.content)
            print("✅ Audio saved as 'dia_direct_test.wav'")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 DIA Natural Voice Test Suite")
    print("=" * 50)
    
    # Test direct HF API first
    direct_success = test_hf_inference_direct()
    
    # Test our API (if it's running)
    if direct_success:
        print("\n🚀 Starting DIA Natural Voice API...")
        print("Run: python3 src/api/dia_natural_voice_api.py")
        print("Then test with: python3 test_dia_natural.py")
    
    print("\n📋 Setup Instructions:")
    print("1. Set your Hugging Face token:")
    print("   export HF_TOKEN='your_token_here'")
    print("2. Start the DIA Natural Voice API:")
    print("   python3 src/api/dia_natural_voice_api.py")
    print("3. Test voice generation:")
    print("   python3 test_dia_natural.py")


