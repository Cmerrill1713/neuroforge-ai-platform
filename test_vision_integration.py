#!/usr/bin/env python3
"""
Test Vision Integration
Tests the LLaVA vision model integration and image analysis capabilities
"""

import requests
import json
import time
import base64
from pathlib import Path

def test_vision_system():
    """Test the vision system capabilities"""
    
    base_url = "http://localhost:8004"
    
    print("👁️ Testing LLaVA Vision Integration")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Testing Vision System Health Check...")
    try:
        response = requests.get(f"{base_url}/api/vision/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Vision System: {health['status']}")
            print(f"   - Model Available: {health['vision_model_available']}")
            print(f"   - Model Loaded: {health['model_loaded']}")
            print(f"   - Model Name: {health['model_name']}")
            print(f"   - Cache Size: {health['cache_size']}")
            print(f"   - Fallback Available: {health['fallback_available']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Model Information
    print("\n2. Testing Model Information...")
    try:
        response = requests.get(f"{base_url}/api/vision/model/info")
        if response.status_code == 200:
            model_info = response.json()
            print(f"✅ Model Info:")
            print(f"   - Available: {model_info['available']}")
            print(f"   - Model Name: {model_info['model_name']}")
            print(f"   - Status: {model_info['status']}")
            print(f"   - Cache Size: {model_info['cache_size']}")
            
            if model_info.get('model_info'):
                print(f"   - Model Details: {model_info['model_info'].get('name', 'N/A')}")
        else:
            print(f"❌ Model info failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Model info error: {e}")
    
    # Test 3: Initialize Model
    print("\n3. Testing Model Initialization...")
    try:
        response = requests.post(f"{base_url}/api/vision/model/initialize")
        if response.status_code == 200:
            init_result = response.json()
            print(f"✅ Model Initialization:")
            print(f"   - Success: {init_result['success']}")
            print(f"   - Message: {init_result['message']}")
            
            if init_result.get('model_info'):
                print(f"   - Model Info: {init_result['model_info'].get('available', False)}")
        else:
            print(f"❌ Model initialization failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Model initialization error: {e}")
    
    # Test 4: Create Test Image (simple base64 encoded image)
    print("\n4. Creating Test Image...")
    try:
        # Create a simple test image (1x1 pixel red PNG)
        test_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        print(f"✅ Test image created (base64: {len(test_image_data)} chars)")
    except Exception as e:
        print(f"❌ Test image creation error: {e}")
        return
    
    # Test 5: Image Analysis
    print("\n5. Testing Image Analysis...")
    try:
        analysis_request = {
            "image_data": test_image_data,
            "prompt": "Analyze this image in detail. Describe what you see, including objects, people, text, colors, composition, and any other relevant details."
        }
        
        response = requests.post(
            f"{base_url}/api/vision/analyze",
            json=analysis_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Image Analysis:")
            print(f"   - Success: {result['success']}")
            print(f"   - Model Used: {result['model_used']}")
            print(f"   - Processing Time: {result['processing_time']:.2f}s")
            print(f"   - Fallback: {result['fallback']}")
            
            if result.get('analysis'):
                analysis_preview = result['analysis'][:100] + "..." if len(result['analysis']) > 100 else result['analysis']
                print(f"   - Analysis: {analysis_preview}")
            
            if result.get('error'):
                print(f"   - Error: {result['error']}")
        else:
            print(f"❌ Image analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Image analysis error: {e}")
    
    # Test 6: Batch Analysis
    print("\n6. Testing Batch Image Analysis...")
    try:
        batch_request = {
            "images": [
                {
                    "image_data": test_image_data,
                    "prompt": "What color is this image?"
                },
                {
                    "image_data": test_image_data,
                    "prompt": "Describe the composition of this image."
                }
            ],
            "default_prompt": "Analyze this image."
        }
        
        response = requests.post(
            f"{base_url}/api/vision/analyze/batch",
            json=batch_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Batch Analysis:")
            print(f"   - Success: {result['success']}")
            print(f"   - Total Images: {result['total_images']}")
            print(f"   - Successful: {result['successful_analyses']}")
            print(f"   - Failed: {result['failed_analyses']}")
            print(f"   - Processing Time: {result['processing_time']:.2f}s")
            
            for i, analysis_result in enumerate(result['results']):
                print(f"   - Image {i+1}: {'✅' if analysis_result.get('success') else '❌'}")
        else:
            print(f"❌ Batch analysis failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Batch analysis error: {e}")
    
    # Test 7: Cache Operations
    print("\n7. Testing Cache Operations...")
    try:
        # Check cache size
        health_response = requests.get(f"{base_url}/api/vision/health")
        if health_response.status_code == 200:
            cache_size_before = health_response.json().get('cache_size', 0)
            print(f"✅ Cache size before: {cache_size_before}")
            
            # Clear cache
            clear_response = requests.post(f"{base_url}/api/vision/cache/clear")
            if clear_response.status_code == 200:
                clear_result = clear_response.json()
                print(f"✅ Cache cleared:")
                print(f"   - Success: {clear_result['success']}")
                print(f"   - Entries before: {clear_result['cache_size_before']}")
                print(f"   - Entries after: {clear_result['cache_size_after']}")
            else:
                print(f"❌ Cache clear failed: {clear_response.status_code}")
    except Exception as e:
        print(f"❌ Cache operations error: {e}")
    
    # Test 8: Examples
    print("\n8. Testing Analysis Examples...")
    try:
        response = requests.get(f"{base_url}/api/vision/examples")
        if response.status_code == 200:
            examples = response.json()
            print(f"✅ Analysis Examples:")
            print(f"   - Available Examples: {len(examples['examples'])}")
            print(f"   - Tips: {len(examples['tips'])}")
            
            # Show first example
            if examples['examples']:
                first_example = examples['examples'][0]
                print(f"   - First Example: {first_example['description']}")
                print(f"     Prompt: {first_example['prompt'][:60]}...")
        else:
            print(f"❌ Examples failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Examples error: {e}")
    
    print("\n" + "=" * 60)
    print("👁️ Vision Integration Testing Complete")

def test_vision_with_real_image():
    """Test vision system with a real image file if available"""
    
    base_url = "http://localhost:8004"
    
    print("\n🖼️ Testing with Real Image")
    print("=" * 40)
    
    # Look for test images
    test_image_paths = [
        "test_image.png",
        "test_image.jpg",
        "test_image.jpeg",
        "sample.png",
        "sample.jpg"
    ]
    
    test_image = None
    for path in test_image_paths:
        if Path(path).exists():
            test_image = path
            break
    
    if not test_image:
        print("⚠️ No test image found. Create a test_image.png file to test with real images.")
        return
    
    print(f"📷 Found test image: {test_image}")
    
    try:
        # Test file upload
        with open(test_image, 'rb') as f:
            files = {'file': (test_image, f, 'image/png')}
            data = {'prompt': 'Analyze this image in detail. Describe what you see, including objects, people, text, colors, composition, and any other relevant details.'}
            
            response = requests.post(
                f"{base_url}/api/vision/analyze/upload",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Real Image Analysis:")
            print(f"   - Success: {result['success']}")
            print(f"   - Filename: {result['filename']}")
            print(f"   - Model Used: {result['model_used']}")
            print(f"   - Processing Time: {result['processing_time']:.2f}s")
            print(f"   - Fallback: {result['fallback']}")
            
            if result.get('analysis'):
                analysis_preview = result['analysis'][:200] + "..." if len(result['analysis']) > 200 else result['analysis']
                print(f"   - Analysis: {analysis_preview}")
        else:
            print(f"❌ Real image analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Real image test error: {e}")

if __name__ == "__main__":
    print("🚀 Vision Integration Test Suite")
    print("Make sure the API server is running on port 8004")
    print("Make sure Ollama is running for LLaVA model")
    
    try:
        # Test vision system
        test_vision_system()
        
        # Test with real image if available
        test_vision_with_real_image()
        
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
