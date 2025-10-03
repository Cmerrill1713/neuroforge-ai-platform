#!/usr/bin/env python3
"""
Test MLX Integration
Tests the real MLX processing system instead of simulations
"""

import requests
import json
import time
from datetime import datetime

def test_mlx_system():
    """Test the MLX processing system capabilities"""
    
    base_url = "http://localhost:8004"
    
    print("🧠 Testing Real MLX Processing Integration")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Testing MLX System Health Check...")
    try:
        response = requests.get(f"{base_url}/api/mlx/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ MLX System: {health['status']}")
            print(f"   - MLX Available: {health['mlx_available']}")
            print(f"   - Current Model: {health['current_model']}")
            print(f"   - Available Models: {health['available_models']}")
            print(f"   - Processing Status: {health['processing_status']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: MLX Status
    print("\n2. Testing MLX Status...")
    try:
        response = requests.get(f"{base_url}/api/mlx/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ MLX Status:")
            print(f"   - Status: {status['status']}")
            print(f"   - MLX Available: {status['mlx_available']}")
            print(f"   - Current Model: {status['current_model']}")
            print(f"   - Available Models: {len(status['available_models'])}")
            print(f"   - Model Count: {status['model_count']}")
            
            if status['available_models']:
                print(f"   - Models: {', '.join(status['available_models'])}")
        else:
            print(f"❌ MLX status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ MLX status error: {e}")
    
    # Test 3: Initialize MLX
    print("\n3. Testing MLX Initialization...")
    try:
        response = requests.post(f"{base_url}/api/mlx/initialize")
        if response.status_code == 200:
            init_result = response.json()
            print(f"✅ MLX Initialization:")
            print(f"   - Success: {init_result['success']}")
            print(f"   - Message: {init_result['message']}")
            
            if init_result.get('status'):
                print(f"   - Status: {init_result['status']['status']}")
        else:
            print(f"❌ MLX initialization failed: {response.status_code}")
    except Exception as e:
        print(f"❌ MLX initialization error: {e}")
    
    # Test 4: List Available Models
    print("\n4. Testing Available Models...")
    try:
        response = requests.get(f"{base_url}/api/mlx/models")
        if response.status_code == 200:
            models_result = response.json()
            print(f"✅ Available Models:")
            print(f"   - Success: {models_result['success']}")
            print(f"   - Total Count: {models_result['total_count']}")
            print(f"   - Current Model: {models_result['current_model']}")
            
            for model in models_result['models']:
                print(f"   - {model['name']}: {model['status']}")
        else:
            print(f"❌ Models listing failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Models listing error: {e}")
    
    # Test 5: Text Generation
    print("\n5. Testing MLX Text Generation...")
    try:
        generation_request = {
            "text": "Hello, how are you today?",
            "operation": "generate",
            "device": "mps",
            "precision": "float16",
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/mlx/generate",
            json=generation_request
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ MLX Text Generation:")
            print(f"   - Success: {result['success']}")
            print(f"   - Processing Time: {result['processing_time']:.2f}s")
            print(f"   - Tokens Processed: {result['tokens_processed']}")
            print(f"   - Model Used: {result['model_used']}")
            
            if result.get('generated_text'):
                generated_preview = result['generated_text'][:100] + "..." if len(result['generated_text']) > 100 else result['generated_text']
                print(f"   - Generated Text: {generated_preview}")
        else:
            print(f"❌ Text generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Text generation error: {e}")
    
    # Test 6: Text Embedding
    print("\n6. Testing MLX Text Embedding...")
    try:
        embedding_request = {
            "text": "This is a test sentence for embedding generation.",
            "operation": "embed",
            "device": "mps",
            "precision": "float16"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/mlx/embed",
            json=embedding_request
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ MLX Text Embedding:")
            print(f"   - Success: {result['success']}")
            print(f"   - Embedding Dimension: {result['embedding_dimension']}")
            print(f"   - Processing Time: {result['processing_time']:.2f}s")
            print(f"   - Tokens Processed: {result['tokens_processed']}")
            print(f"   - Model Used: {result['model_used']}")
            
            if result.get('embedding'):
                embedding_preview = result['embedding'][:5] + ["..."] if len(result['embedding']) > 5 else result['embedding']
                print(f"   - Embedding Preview: {embedding_preview}")
        else:
            print(f"❌ Text embedding failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Text embedding error: {e}")
    
    # Test 7: Text Classification
    print("\n7. Testing MLX Text Classification...")
    try:
        classification_request = {
            "text": "I love this amazing product! It's fantastic and works perfectly.",
            "operation": "classify",
            "device": "mps",
            "precision": "float16"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/mlx/classify",
            json=classification_request
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ MLX Text Classification:")
            print(f"   - Success: {result['success']}")
            print(f"   - Processing Time: {result['processing_time']:.2f}s")
            print(f"   - Tokens Processed: {result['tokens_processed']}")
            print(f"   - Model Used: {result['model_used']}")
            
            if result.get('classification'):
                classification = result['classification']
                print(f"   - Classification Scores:")
                for category, score in classification.items():
                    print(f"     - {category}: {score:.3f}")
        else:
            print(f"❌ Text classification failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Text classification error: {e}")
    
    # Test 8: Performance Benchmark
    print("\n8. Testing MLX Performance Benchmark...")
    try:
        benchmark_request = {
            "iterations": 5
        }
        
        response = requests.post(
            f"{base_url}/api/mlx/benchmark",
            json=benchmark_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ MLX Performance Benchmark:")
            print(f"   - Iterations: {result['iterations']}")
            print(f"   - Average Time: {result['average_time']:.3f}s")
            print(f"   - Min Time: {result['min_time']:.3f}s")
            print(f"   - Max Time: {result['max_time']:.3f}s")
            print(f"   - Throughput: {result['throughput']:.2f} tokens/s")
            print(f"   - MLX Available: {result['mlx_available']}")
            print(f"   - Model Used: {result['model_used']}")
        else:
            print(f"❌ Performance benchmark failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Performance benchmark error: {e}")
    
    # Test 9: Capabilities
    print("\n9. Testing MLX Capabilities...")
    try:
        response = requests.get(f"{base_url}/api/mlx/capabilities")
        if response.status_code == 200:
            capabilities = response.json()
            print(f"✅ MLX Capabilities:")
            print(f"   - Supported Operations: {len(capabilities['supported_operations'])}")
            for op in capabilities['supported_operations']:
                print(f"     - {op['name']}: {op['description']}")
            print(f"   - Supported Devices: {', '.join(capabilities['supported_devices'])}")
            print(f"   - Supported Precisions: {', '.join(capabilities['supported_precisions'])}")
            print(f"   - Max Sequence Length: {capabilities['max_sequence_length']}")
            print(f"   - Batch Processing: {capabilities['batch_processing']}")
        else:
            print(f"❌ Capabilities failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Capabilities error: {e}")
    
    print("\n" + "=" * 60)
    print("🧠 MLX Integration Testing Complete")

def test_mlx_processing_modes():
    """Test different MLX processing modes"""
    
    base_url = "http://localhost:8004"
    
    print("\n🔄 Testing MLX Processing Modes")
    print("=" * 40)
    
    # Test different devices
    devices = ["mps", "cpu"]
    
    for device in devices:
        print(f"\n📱 Testing Device: {device}")
        try:
            request = {
                "text": f"Testing MLX processing on {device} device.",
                "operation": "generate",
                "device": device,
                "precision": "float16",
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{base_url}/api/mlx/generate",
                json=request
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {device.upper()} Device:")
                print(f"   - Success: {result['success']}")
                print(f"   - Processing Time: {result['processing_time']:.2f}s")
                print(f"   - Model Used: {result['model_used']}")
            else:
                print(f"❌ {device.upper()} device failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {device.upper()} device error: {e}")

if __name__ == "__main__":
    print("🚀 MLX Integration Test Suite")
    print("Make sure the API server is running on port 8004")
    print("Make sure MLX models are available in mlx_models/ directory")
    
    try:
        # Test MLX system
        test_mlx_system()
        
        # Test processing modes
        test_mlx_processing_modes()
        
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
