#!/usr/bin/env python3
"""
Test Chatterbox TTS Audio Generation
Generate actual audio files you can play to hear Chatterbox TTS
"""

import os
import logging
import torch
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_chatterbox_audio():
    """Generate actual audio files with Chatterbox TTS"""
    print("🎤 Testing Chatterbox TTS Audio Generation")
    print("=" * 50)
    
    try:
        # Initialize Chatterbox TTS
        print("🔄 Loading Chatterbox TTS...")
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"🎯 Using device: {device}")
        model = ChatterboxTTS.from_pretrained(device=device)
        print("✅ Chatterbox TTS loaded successfully!")
        
        # Test cases with feminine, sultry voice characteristics
        test_cases = [
            {
                "text": "Hello darling. This is a sultry, feminine voice that's smooth and alluring.",
                "filename": "chatterbox_sultry.wav",
                "exaggeration": 0.4,
                "cfg_weight": 0.4,
                "description": "Sultry feminine voice"
            },
            {
                "text": "I have a seductive tone that draws you in. My voice is smooth, warm, and captivating.",
                "filename": "chatterbox_seductive.wav", 
                "exaggeration": 0.5,
                "cfg_weight": 0.3,
                "description": "Seductive feminine voice"
            },
            {
                "text": "This is my intimate whisper. Soft, breathy, and irresistibly charming.",
                "filename": "chatterbox_intimate.wav",
                "exaggeration": 0.6,
                "cfg_weight": 0.2,
                "description": "Intimate whisper voice"
            },
            {
                "text": "I speak with confidence and allure. My voice commands attention while remaining elegant.",
                "filename": "chatterbox_confident.wav",
                "exaggeration": 0.3,
                "cfg_weight": 0.5,
                "description": "Confident feminine voice"
            },
            {
                "text": "My voice flows like honey, smooth and sweet. Every word is delivered with grace and charm.",
                "filename": "chatterbox_honey.wav",
                "exaggeration": 0.4,
                "cfg_weight": 0.4,
                "description": "Honey-smooth feminine voice"
            }
        ]
        
        print(f"\n🎭 Generating {len(test_cases)} unique voice samples...")
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n📝 Test {i}: {test['description']}")
            print(f"   Text: \"{test['text'][:60]}...\"")
            print(f"   Parameters: exaggeration={test['exaggeration']}, cfg_weight={test['cfg_weight']}")
            
            try:
                # Generate with Chatterbox's unique parameters
                wav = model.generate(
                    test["text"],
                    exaggeration=test["exaggeration"],
                    cfg_weight=test["cfg_weight"]
                )
                
                # Save audio file
                ta.save(test["filename"], wav, model.sr)
                
                file_size = os.path.getsize(test["filename"]) / 1024
                print(f"✅ Generated: {test['filename']} ({file_size:.1f} KB)")
                
                # Play the audio
                print(f"🔊 Playing {test['description']}...")
                os.system(f"afplay \"{test['filename']}\"")
                print(f"✅ {test['description']} played successfully!")
                
            except Exception as e:
                print(f"❌ Test {i} failed: {e}")
        
        print(f"\n🎉 Chatterbox TTS audio generation complete!")
        print(f"📁 Generated files:")
        for test in test_cases:
            if os.path.exists(test["filename"]):
                size = os.path.getsize(test["filename"])
                print(f"   {test['filename']} ({size} bytes) - {test['description']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Chatterbox TTS test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎤 Chatterbox TTS Audio Test Suite")
    print("=" * 60)
    print("🎯 Goal: Generate actual audio files you can hear")
    print("🔊 Testing unique Chatterbox voice characteristics")
    print("=" * 60)
    
    success = test_chatterbox_audio()
    
    if success:
        print("\n✅ All tests completed successfully!")
        print("🔊 You can now hear Chatterbox TTS in action!")
    else:
        print("\n❌ Tests failed. Check the error messages above.")
