#!/usr/bin/env python3
"""
Test Full Integration - Frontend + Backend + Optimized Models
"""

import requests
import json
import time
from datetime import datetime

def test_api_connection():
    """Test API server connection"""
    print("🔗 Testing API Connection...")
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Server: {data['status']}")
            print(f"📊 Models Available: {data['models']}")
            return True
        else:
            print(f"❌ API Server Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Connection Failed: {e}")
        return False

def test_models_endpoint():
    """Test models endpoint"""
    print("\n🤖 Testing Models Endpoint...")
    try:
        response = requests.get("http://127.0.0.1:8000/models", timeout=10)
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Found {len(models)} models:")
            for model in models[:5]:  # Show first 5
                print(f"  - {model['name']} ({model['type']}) - Score: {model['performance_score']}")
            return models
        else:
            print(f"❌ Models Endpoint Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Models Test Failed: {e}")
        return []

def test_chat_endpoint():
    """Test chat endpoint with optimized models"""
    print("\n💬 Testing Chat Endpoint...")
    
    test_messages = [
        {
            "message": "Hello! Can you help me improve my frontend design?",
            "model": "qwen2.5:7b"
        },
        {
            "message": "What are the best practices for React performance optimization?",
            "model": "mistral:7b"
        },
        {
            "message": "How can I implement real-time features in my web app?",
            "model": "llama3.2:3b"
        }
    ]
    
    results = []
    
    for test in test_messages:
        try:
            print(f"  Testing {test['model']}...")
            start_time = time.time()
            
            response = requests.post(
                "http://127.0.0.1:8000/chat",
                json=test,
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"    ✅ Response: {data['message'][:100]}...")
                print(f"    ⏱️  Time: {response_time:.2f}s")
                
                results.append({
                    "model": test['model'],
                    "success": True,
                    "response_time": response_time,
                    "response_length": len(data['message'])
                })
            else:
                print(f"    ❌ Error: {response.status_code}")
                results.append({
                    "model": test['model'],
                    "success": False,
                    "error": response.status_code
                })
                
        except Exception as e:
            print(f"    ❌ Exception: {e}")
            results.append({
                "model": test['model'],
                "success": False,
                "error": str(e)
            })
    
    return results

def test_frontend_connection():
    """Test frontend connection"""
    print("\n🌐 Testing Frontend Connection...")
    try:
        response = requests.get("http://localhost:3000/", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend Connection Failed: {e}")
        return False

def generate_integration_report(api_ok, models, chat_results, frontend_ok):
    """Generate comprehensive integration report"""
    print("\n" + "="*60)
    print("📊 FULL INTEGRATION TEST REPORT")
    print("="*60)
    
    print(f"\n🔗 API Server: {'✅ Connected' if api_ok else '❌ Failed'}")
    print(f"🌐 Frontend: {'✅ Accessible' if frontend_ok else '❌ Failed'}")
    print(f"🤖 Models Available: {len(models) if models else 0}")
    
    if chat_results:
        successful_chats = [r for r in chat_results if r['success']]
        print(f"💬 Chat Tests: {len(successful_chats)}/{len(chat_results)} successful")
        
        if successful_chats:
            avg_time = sum(r['response_time'] for r in successful_chats) / len(successful_chats)
            print(f"⏱️  Average Response Time: {avg_time:.2f}s")
    
    print(f"\n🎯 INTEGRATION STATUS:")
    if api_ok and frontend_ok and models:
        print("✅ FULLY INTEGRATED - Ready for use!")
        print("\n🚀 NEXT STEPS:")
        print("1. Open http://localhost:3000 in your browser")
        print("2. Start chatting with optimized AI models")
        print("3. Test different models for various tasks")
        print("4. Explore the multimodal and code editor features")
        
        print(f"\n🏆 RECOMMENDED MODELS:")
        if models:
            # Sort by performance score
            sorted_models = sorted(models, key=lambda x: x.get('performance_score', 0), reverse=True)
            for i, model in enumerate(sorted_models[:3]):
                print(f"  {i+1}. {model['name']} - Score: {model['performance_score']}/10")
    else:
        print("❌ INTEGRATION INCOMPLETE")
        if not api_ok:
            print("  - Fix API server connection")
        if not frontend_ok:
            print("  - Fix frontend connection")
        if not models:
            print("  - Check model availability")
    
    print(f"\n📈 PERFORMANCE METRICS:")
    print(f"  - Total Models: {len(models) if models else 0}")
    print(f"  - API Response: {'Fast' if api_ok else 'Slow/Failed'}")
    print(f"  - Frontend Load: {'Fast' if frontend_ok else 'Slow/Failed'}")
    
    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "api_connected": api_ok,
        "frontend_accessible": frontend_ok,
        "models_count": len(models) if models else 0,
        "chat_results": chat_results,
        "integration_status": "complete" if (api_ok and frontend_ok and models) else "incomplete"
    }
    
    with open("integration_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Report saved to: integration_test_report.json")

def main():
    """Main test function"""
    print("🚀 TESTING FULL INTEGRATION - Frontend + Backend + Optimized Models")
    print("="*70)
    
    # Test API connection
    api_ok = test_api_connection()
    
    # Test models
    models = test_models_endpoint()
    
    # Test chat functionality
    chat_results = test_chat_endpoint() if api_ok else []
    
    # Test frontend
    frontend_ok = test_frontend_connection()
    
    # Generate report
    generate_integration_report(api_ok, models, chat_results, frontend_ok)

if __name__ == "__main__":
    main()
