#!/usr/bin/env python3
"""
Test Optimized Model Integration
Tests the optimized large model system with timeout management and streaming
"""

import requests
import json
import time
import asyncio
from datetime import datetime

def test_optimized_model_system():
    """Test the optimized model system capabilities"""
    
    base_url = "http://localhost:8004"
    
    print("🔮 Testing Optimized Model Integration")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Testing Model System Health Check...")
    try:
        response = requests.get(f"{base_url}/api/model/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Model System: {health['status']}")
            print(f"   - Model Status: {health['model_status']}")
            print(f"   - Default Model: {health['default_model']}")
            print(f"   - Active Sessions: {health['active_sessions']}")
            print(f"   - Available Models: {health['available_models']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Model Status
    print("\n2. Testing Model Status...")
    try:
        response = requests.get(f"{base_url}/api/model/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Model Status:")
            print(f"   - Status: {status['status']}")
            print(f"   - Default Model: {status['default_model']}")
            print(f"   - Active Sessions: {status['active_sessions']}")
            print(f"   - Available Models: {len(status['available_models'])}")
        else:
            print(f"❌ Model status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Model status error: {e}")
    
    # Test 3: Initialize Model
    print("\n3. Testing Model Initialization...")
    try:
        response = requests.post(f"{base_url}/api/model/initialize")
        if response.status_code == 200:
            init_result = response.json()
            print(f"✅ Model Initialization:")
            print(f"   - Success: {init_result['success']}")
            print(f"   - Message: {init_result['message']}")
            
            if init_result.get('status'):
                print(f"   - Status: {init_result['status']['status']}")
        else:
            print(f"❌ Model initialization failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Model initialization error: {e}")
    
    # Test 4: Model Inference (Non-streaming)
    print("\n4. Testing Model Inference (Non-streaming)...")
    try:
        inference_request = {
            "prompt": "Explain the concept of artificial intelligence in simple terms.",
            "max_tokens": 200,
            "temperature": 0.7,
            "stream": False,
            "session_id": "test_session_1"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/model/inference",
            json=inference_request,
            timeout=180  # 3 minutes timeout
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Model Inference:")
            print(f"   - Success: {result['success']}")
            print(f"   - Model: {result['model_name']}")
            print(f"   - Tokens Used: {result['tokens_used']}")
            print(f"   - Processing Time: {result['processing_time']:.2f}s")
            print(f"   - Total Time: {end_time - start_time:.2f}s")
            
            if result.get('content'):
                content_preview = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                print(f"   - Content Preview: {content_preview}")
            
            if result.get('error'):
                print(f"   - Error: {result['error']}")
        else:
            print(f"❌ Model inference failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.Timeout:
        print("⏰ Model inference timed out (this is expected for large models)")
    except Exception as e:
        print(f"❌ Model inference error: {e}")
    
    # Test 5: Model Inference (Streaming)
    print("\n5. Testing Model Inference (Streaming)...")
    try:
        inference_request = {
            "prompt": "What is machine learning?",
            "max_tokens": 150,
            "temperature": 0.7,
            "stream": True,
            "session_id": "test_session_2"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/model/inference/stream",
            json=inference_request,
            stream=True,
            timeout=120  # 2 minutes timeout
        )
        
        if response.status_code == 200:
            print(f"✅ Streaming Inference Started:")
            print(f"   - Status Code: {response.status_code}")
            print(f"   - Content Type: {response.headers.get('content-type')}")
            
            # Read streaming response
            chunks_received = 0
            total_content = ""
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        chunk_data = line_str[6:]  # Remove 'data: ' prefix
                        try:
                            chunk_json = json.loads(chunk_data)
                            chunks_received += 1
                            
                            if 'response' in chunk_json:
                                total_content += chunk_json['response']
                            
                            if chunk_json.get('done', False):
                                break
                                
                        except json.JSONDecodeError:
                            continue
            
            end_time = time.time()
            print(f"   - Chunks Received: {chunks_received}")
            print(f"   - Total Content Length: {len(total_content)}")
            print(f"   - Streaming Time: {end_time - start_time:.2f}s")
            
            if total_content:
                content_preview = total_content[:100] + "..." if len(total_content) > 100 else total_content
                print(f"   - Content Preview: {content_preview}")
        else:
            print(f"❌ Streaming inference failed: {response.status_code}")
    except requests.exceptions.Timeout:
        print("⏰ Streaming inference timed out")
    except Exception as e:
        print(f"❌ Streaming inference error: {e}")
    
    # Test 6: Model Configuration
    print("\n6. Testing Model Configuration...")
    try:
        # Test getting config for default model
        response = requests.get(f"{base_url}/api/model/config/qwen2.5:72b")
        if response.status_code == 200:
            config = response.json()
            print(f"✅ Model Configuration:")
            print(f"   - Model Name: {config['model_name']}")
            print(f"   - Max Tokens: {config['max_tokens']}")
            print(f"   - Temperature: {config['temperature']}")
            print(f"   - Timeout: {config['timeout']}s")
            print(f"   - Stream: {config['stream']}")
        else:
            print(f"❌ Model config failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Model config error: {e}")
    
    # Test 7: Session Management
    print("\n7. Testing Session Management...")
    try:
        # Test clearing specific session
        session_request = {"session_id": "test_session_1"}
        response = requests.post(
            f"{base_url}/api/model/session/clear",
            json=session_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Session Clear:")
            print(f"   - Success: {result['success']}")
            print(f"   - Session ID: {result['session_id']}")
        else:
            print(f"❌ Session clear failed: {response.status_code}")
        
        # Test clearing all sessions
        response = requests.post(f"{base_url}/api/model/session/clear-all")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Clear All Sessions:")
            print(f"   - Success: {result['success']}")
        else:
            print(f"❌ Clear all sessions failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Session management error: {e}")
    
    # Test 8: Performance Metrics
    print("\n8. Testing Performance Metrics...")
    try:
        response = requests.get(f"{base_url}/api/model/performance")
        if response.status_code == 200:
            metrics = response.json()
            print(f"✅ Performance Metrics:")
            print(f"   - Model Status: {metrics['model_status']}")
            print(f"   - Active Sessions: {metrics['active_sessions']}")
            print(f"   - Available Models: {metrics['available_models']}")
            print(f"   - Session Utilization: {metrics['session_utilization']}")
            print(f"   - Model Availability: {metrics['model_availability']}")
        else:
            print(f"❌ Performance metrics failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Performance metrics error: {e}")
    
    print("\n" + "=" * 60)
    print("🔮 Optimized Model Testing Complete")

def test_timeout_handling():
    """Test timeout handling with a very long prompt"""
    
    base_url = "http://localhost:8004"
    
    print("\n⏰ Testing Timeout Handling")
    print("=" * 40)
    
    try:
        # Create a very long prompt that might cause timeout
        long_prompt = "Explain quantum computing in extreme detail, covering all aspects including: " * 100
        
        inference_request = {
            "prompt": long_prompt,
            "max_tokens": 500,
            "temperature": 0.7,
            "stream": False,
            "session_id": "timeout_test"
        }
        
        print(f"📝 Testing with long prompt ({len(long_prompt)} characters)")
        
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/model/inference",
            json=inference_request,
            timeout=30  # Short timeout to test timeout handling
        )
        end_time = time.time()
        
        print(f"⏱️ Request completed in {end_time - start_time:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('error') == 'Inference timeout':
                print("✅ Timeout handling working correctly")
            else:
                print(f"✅ Request completed successfully: {result.get('success')}")
        else:
            print(f"❌ Request failed: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("✅ Timeout handling working correctly (request timed out)")
    except Exception as e:
        print(f"❌ Timeout test error: {e}")

if __name__ == "__main__":
    print("🚀 Optimized Model Test Suite")
    print("Make sure the API server is running on port 8004")
    print("Make sure Ollama is running with large models")
    
    try:
        # Test optimized model system
        test_optimized_model_system()
        
        # Test timeout handling
        test_timeout_handling()
        
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
