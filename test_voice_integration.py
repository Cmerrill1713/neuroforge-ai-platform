#!/usr/bin/env python3
"""
Test Voice System Integration
Tests the integrated voice services (TTS and Whisper)
"""

import requests
import json
import time
import os
from pathlib import Path

def test_voice_system():
    """Test the integrated voice system"""
    
    base_url = "http://localhost:8004"
    
    print("🎤 Testing Integrated Voice System")
    print("=" * 50)
    
    # Test 1: Voice Options
    print("\n1. Testing Voice Options...")
    try:
        response = requests.get(f"{base_url}/api/voice/options")
        if response.status_code == 200:
            options = response.json()
            print(f"✅ Voice Options: {len(options['voices'])} voices available")
            print(f"   - Default: {options['default']}")
            print(f"   - Engines: {', '.join(options['engines'])}")
            
            # List available voices
            for voice in options['voices'][:3]:  # Show first 3
                print(f"   - {voice['id']}: {voice['description']}")
        else:
            print(f"❌ Voice Options failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Voice Options error: {e}")
    
    # Test 2: Voice Health Check
    print("\n2. Testing Voice Health Check...")
    try:
        response = requests.get(f"{base_url}/api/voice/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Voice Health: {health['overall']}")
            print(f"   - TTS Service: {health['tts_service']['status']} (port {health['tts_service']['port']})")
            print(f"   - Whisper Service: {health['whisper_service']['status']} (port {health['whisper_service']['port']})")
        else:
            print(f"❌ Voice Health failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Voice Health error: {e}")
    
    # Test 3: Voice Synthesis
    print("\n3. Testing Voice Synthesis...")
    test_texts = [
        "Hello, this is a test of the voice system.",
        "The quick brown fox jumps over the lazy dog.",
        "Testing different voice profiles and synthesis quality."
    ]
    
    voice_profiles = ["sonia_clean", "assistant", "professional"]
    
    for i, text in enumerate(test_texts[:2]):  # Test first 2 texts
        voice = voice_profiles[i % len(voice_profiles)]
        try:
            synthesis_request = {
                "text": text,
                "voice_profile": voice
            }
            
            print(f"   Testing: '{text[:30]}...' (voice: {voice})")
            
            response = requests.post(
                f"{base_url}/api/voice/synthesize",
                json=synthesis_request,
                timeout=30
            )
            
            if response.status_code == 200:
                # Check if we got audio data
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                if 'audio' in content_type and content_length > 1000:
                    print(f"   ✅ Synthesis successful: {content_length} bytes, {content_type}")
                    
                    # Save audio file for verification
                    audio_filename = f"test_voice_{i+1}_{voice}.wav"
                    with open(audio_filename, 'wb') as f:
                        f.write(response.content)
                    print(f"   📁 Audio saved: {audio_filename}")
                else:
                    print(f"   ⚠️ Unexpected response: {content_type}, {content_length} bytes")
            else:
                print(f"   ❌ Synthesis failed: {response.status_code}")
                print(f"   Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Synthesis error: {e}")
    
    # Test 4: Direct TTS Service
    print("\n4. Testing Direct TTS Service...")
    try:
        response = requests.get("http://localhost:8086/health")
        if response.status_code == 200:
            tts_health = response.json()
            print(f"✅ Direct TTS Service: {tts_health['status']}")
        else:
            print(f"❌ Direct TTS Service failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Direct TTS Service error: {e}")
    
    # Test 5: Direct Whisper Service
    print("\n5. Testing Direct Whisper Service...")
    try:
        response = requests.get("http://localhost:8087/health")
        if response.status_code == 200:
            whisper_health = response.json()
            print(f"✅ Direct Whisper Service: {whisper_health['status']}")
        else:
            print(f"❌ Direct Whisper Service failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Direct Whisper Service error: {e}")
    
    # Test 6: Performance Test
    print("\n6. Testing Voice Synthesis Performance...")
    try:
        test_text = "This is a performance test of the voice synthesis system."
        
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/voice/synthesize",
            json={"text": test_text, "voice_profile": "assistant"},
            timeout=30
        )
        end_time = time.time()
        
        if response.status_code == 200:
            latency = (end_time - start_time) * 1000
            content_length = len(response.content)
            print(f"✅ Performance Test:")
            print(f"   - Latency: {latency:.1f}ms")
            print(f"   - Audio size: {content_length} bytes")
            print(f"   - Quality: {'Good' if content_length > 10000 else 'Low'}")
        else:
            print(f"❌ Performance test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Performance test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎤 Voice System Integration Testing Complete")

def test_voice_comparison():
    """Compare integrated vs direct voice services"""
    
    print("\n🔄 Comparing Integrated vs Direct Voice Services")
    print("=" * 50)
    
    test_text = "This is a comparison test between integrated and direct voice services."
    
    # Test integrated API
    print("\n1. Testing Integrated API...")
    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:8004/api/voice/synthesize",
            json={"text": test_text, "voice_profile": "assistant"},
            timeout=30
        )
        integrated_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            integrated_size = len(response.content)
            print(f"✅ Integrated API: {integrated_time:.1f}ms, {integrated_size} bytes")
        else:
            print(f"❌ Integrated API failed: {response.status_code}")
            integrated_time = None
            integrated_size = None
    except Exception as e:
        print(f"❌ Integrated API error: {e}")
        integrated_time = None
        integrated_size = None
    
    # Test direct TTS service
    print("\n2. Testing Direct TTS Service...")
    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:8086/synthesize",
            json={"text": test_text, "voice_profile": "assistant"},
            timeout=30
        )
        direct_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            direct_data = response.json()
            if direct_data.get("success"):
                direct_size = "N/A (file path)"
                print(f"✅ Direct TTS: {direct_time:.1f}ms, audio file generated")
            else:
                print(f"❌ Direct TTS failed: {direct_data.get('error', 'Unknown error')}")
                direct_time = None
        else:
            print(f"❌ Direct TTS failed: {response.status_code}")
            direct_time = None
    except Exception as e:
        print(f"❌ Direct TTS error: {e}")
        direct_time = None
    
    # Compare results
    print("\n3. Comparison Results...")
    if integrated_time and direct_time:
        overhead = integrated_time - direct_time
        print(f"✅ Performance Comparison:")
        print(f"   - Integrated API: {integrated_time:.1f}ms")
        print(f"   - Direct TTS: {direct_time:.1f}ms")
        print(f"   - Overhead: {overhead:.1f}ms ({overhead/direct_time*100:.1f}%)")
    else:
        print("❌ Could not compare - some tests failed")

def cleanup_test_files():
    """Clean up test audio files"""
    print("\n🧹 Cleaning up test files...")
    test_files = list(Path(".").glob("test_voice_*.wav"))
    for file in test_files:
        try:
            file.unlink()
            print(f"   Deleted: {file.name}")
        except Exception as e:
            print(f"   Failed to delete {file.name}: {e}")

if __name__ == "__main__":
    print("🚀 Voice System Integration Test Suite")
    print("Make sure the API server is running on port 8004")
    print("Make sure TTS and Whisper services are running on ports 8086 and 8087")
    
    try:
        # Test voice system integration
        test_voice_system()
        
        # Test comparison
        test_voice_comparison()
        
        # Clean up
        cleanup_test_files()
        
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
        cleanup_test_files()
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
        cleanup_test_files()
