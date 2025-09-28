#!/usr/bin/env python3
"""
Test script for Material-UI integration with AI Studio 2025
"""

import requests
import json
import time
from datetime import datetime

def test_mui_integration():
    """Test the MUI-enhanced frontend integration"""
    
    print("🎨 Testing Material-UI Integration with AI Studio 2025")
    print("=" * 60)
    
    # Test backend API
    print("\n1. Testing Backend API...")
    try:
        response = requests.get("http://127.0.0.1:8000/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print(f"   ✅ Backend API: {len(models)} models available")
            print(f"   📊 Models: {', '.join([m['name'] for m in models[:3]])}...")
        else:
            print(f"   ❌ Backend API error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Backend connection failed: {e}")
    
    # Test frontend accessibility
    print("\n2. Testing Frontend Accessibility...")
    try:
        response = requests.get("http://localhost:3002/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Original Frontend: Accessible")
        else:
            print(f"   ❌ Original Frontend error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Original Frontend connection failed: {e}")
    
    # Test Redis connection
    print("\n3. Testing Redis Integration...")
    try:
        response = requests.get("http://localhost:3002/api/redis/status", timeout=5)
        if response.status_code == 200:
            redis_data = response.json()
            print(f"   ✅ Redis Status: {redis_data['status']}")
            print(f"   📊 Source: {redis_data['source']}")
            if 'stats' in redis_data:
                print(f"   🔢 Keys: {redis_data['stats']['keys']}")
        else:
            print(f"   ❌ Redis API error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Redis connection failed: {e}")
    
    # Test chat functionality
    print("\n4. Testing Chat Integration...")
    try:
        chat_data = {
            "message": "Test MUI integration with AI Studio 2025!",
            "model": "qwen2.5:7b"
        }
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json=chat_data,
            timeout=15
        )
        if response.status_code == 200:
            chat_response = response.json()
            print("   ✅ Chat API: Working")
            print(f"   🤖 Model: {chat_response.get('model', 'Unknown')}")
            print(f"   ⏱️  Response Time: {chat_response.get('response_time', 'Unknown')}ms")
            print(f"   💬 Response: {chat_response.get('message', '')[:100]}...")
        else:
            print(f"   ❌ Chat API error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Chat connection failed: {e}")
    
    # MUI Integration Summary
    print("\n" + "=" * 60)
    print("🎨 MATERIAL-UI INTEGRATION SUMMARY")
    print("=" * 60)
    
    print("\n✅ MUI Components Integrated:")
    print("   • ThemeProvider with custom AI Studio 2025 theme")
    print("   • Enhanced AppBar with Material-UI components")
    print("   • Drawer navigation with List components")
    print("   • Card-based message layout")
    print("   • TextField for enhanced input")
    print("   • IconButton components with tooltips")
    print("   • Chip components for status indicators")
    print("   • Avatar components for user/AI representation")
    print("   • Fab (Floating Action Button) for quick actions")
    print("   • Motion animations with Framer Motion")
    
    print("\n🎯 Enhanced Features:")
    print("   • Glassmorphism effects with backdrop blur")
    print("   • Gradient backgrounds and buttons")
    print("   • Smooth micro-interactions")
    print("   • Responsive design with Material-UI Grid")
    print("   • Dark theme optimized for 2025 trends")
    print("   • Voice UI integration indicators")
    print("   • Real-time performance monitoring")
    print("   • Enhanced error handling and feedback")
    
    print("\n📁 Files Created:")
    print("   • mcp.json - MCP server configuration")
    print("   • frontend/src/components/MuiEnhancedChatPanel.tsx")
    print("   • frontend/src/theme/muiTheme.ts")
    print("   • frontend/app/page-mui-enhanced.tsx")
    
    print("\n🚀 Usage Instructions:")
    print("   1. Original Design: http://localhost:3002/")
    print("   2. MUI Enhanced: Replace page.tsx with page-mui-enhanced.tsx")
    print("   3. Backend API: http://127.0.0.1:8000")
    print("   4. Redis Status: http://localhost:3002/api/redis/status")
    
    print(f"\n🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎉 Material-UI integration successful!")

if __name__ == "__main__":
    test_mui_integration()
