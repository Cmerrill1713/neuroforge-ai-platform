#!/usr/bin/env python3
"""
Test DIA Gradio Interface
"""

import requests
import json

def test_dia_interface():
    """Test the DIA Gradio interface"""
    base_url = "http://localhost:7860"
    
    print("🔍 Testing DIA Gradio Interface")
    print("=" * 50)
    
    # Test basic connectivity
    try:
        response = requests.get(base_url, timeout=10)
        print(f"✅ DIA accessible: {response.status_code}")
        print(f"📄 Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        # Look for API endpoints in the HTML
        if 'api' in response.text.lower():
            print("🔗 API endpoints found in HTML")
        else:
            print("❌ No API endpoints found")
            
    except Exception as e:
        print(f"❌ DIA not accessible: {e}")
        return
    
    # Test common Gradio API endpoints
    api_endpoints = [
        "/api/info",
        "/api/predict", 
        "/api/queue/status",
        "/api/queue/join",
        "/api/queue/leave"
    ]
    
    for endpoint in api_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"📡 {endpoint}: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   📊 Response: {str(data)[:100]}...")
                except:
                    print(f"   📄 Response: {response.text[:100]}...")
        except Exception as e:
            print(f"📡 {endpoint}: Error - {e}")

if __name__ == "__main__":
    test_dia_interface()
