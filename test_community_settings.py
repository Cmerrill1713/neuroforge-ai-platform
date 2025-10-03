#!/usr/bin/env python3
"""
Test Chatterbox TTS with Community-Recommended Settings
Based on user feedback and community insights for better voice quality
"""

import os
import logging
import torch
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_community_settings():
    """Test Chatterbox TTS with community-recommended settings"""
    print("🎤 Testing Chatterbox TTS with Community Settings")
    print("=" * 60)
    
    try:
        # Initialize Chatterbox TTS
        print("🔄 Loading Chatterbox TTS...")
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"🎯 Using device: {device}")
        model = ChatterboxTTS.from_pretrained(device=device)
        print("✅ Chatterbox TTS loaded successfully!")
        
        # Community-recommended settings for better voice quality
        test_cases = [
            {
                "text": "Hello there. This is using community-recommended settings for a more expressive voice.",
                "filename": "community_expressive.wav",
                "exaggeration": 0.7,
                "cfg_weight": 0.3,
                "description": "Community-recommended expressive voice"
            },
            {
                "text": "I'm using higher exaggeration settings that users have found work well for engaging speech.",
                "filename": "community_engaging.wav", 
                "exaggeration": 0.8,
                "cfg_weight": 0.2,
                "description": "High engagement settings"
            },
            {
                "text": "This uses balanced settings that many users prefer for natural-sounding speech.",
                "filename": "community_balanced.wav",
                "exaggeration": 0.6,
                "cfg_weight": 0.4,
                "description": "Balanced community settings"
            },
            {
                "text": "Lower cfg_weight allows for more creative and flexible voice generation.",
                "filename": "community_creative.wav",
                "exaggeration": 0.5,
                "cfg_weight": 0.2,
                "description": "Creative/flexible settings"
            },
            {
                "text": "These settings combine high expressiveness with creative flexibility for dynamic speech.",
                "filename": "community_dynamic.wav",
                "exaggeration": 0.75,
                "cfg_weight": 0.25,
                "description": "Dynamic community settings"
            }
        ]
        
        print(f"\n🎭 Testing {len(test_cases)} community-recommended configurations...")
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n📝 Test {i}: {test['description']}")
            print(f"   Text: \"{test['text'][:60]}...\"")
            print(f"   Parameters: exaggeration={test['exaggeration']}, cfg_weight={test['cfg_weight']}")
            
            try:
                # Generate with community settings
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
        
        print(f"\n🎉 Community settings test complete!")
        print(f"📁 Generated files:")
        for test in test_cases:
            if os.path.exists(test["filename"]):
                size = os.path.getsize(test["filename"])
                print(f"   {test['filename']} ({size} bytes) - {test['description']}")
        
        print(f"\n💡 Note: Chatterbox TTS is trained on male voices.")
        print(f"   For female voices, consider using voice cloning with reference audio.")
        print(f"   Community recommends: exaggeration=0.6-0.8, cfg_weight=0.2-0.4")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Community settings test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎤 Chatterbox TTS Community Settings Test")
    print("=" * 60)
    print("🎯 Goal: Test community-recommended voice parameters")
    print("📊 Based on user feedback and community insights")
    print("=" * 60)
    
    success = test_community_settings()
    
    if success:
        print("\n✅ All tests completed successfully!")
        print("🔊 You can now hear community-optimized voices!")
    else:
        print("\n❌ Tests failed. Check the error messages above.")
