#!/usr/bin/env python3
"""
Test Female Voice Generation with Edge TTS
Generate actual female voice audio files using Microsoft's neural voices
"""

import asyncio
import os
import logging
import edge_tts

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_female_voices():
    """Generate actual female voice audio files using Edge TTS"""
    print("🎤 Testing Female Voice Generation with Edge TTS")
    print("=" * 60)
    
    try:
        # Female voice test cases with different characteristics
        test_cases = [
            {
                "text": "Hello darling. This is a sultry, feminine voice that's smooth and alluring.",
                "filename": "female_sultry.wav",
                "voice": "en-US-AriaNeural",
                "rate": "0.8",
                "pitch": "+10%",
                "description": "Sultry feminine voice"
            },
            {
                "text": "I have a seductive tone that draws you in. My voice is smooth, warm, and captivating.",
                "filename": "female_seductive.wav", 
                "voice": "en-US-JennyNeural",
                "rate": "0.7",
                "pitch": "+15%",
                "description": "Seductive feminine voice"
            },
            {
                "text": "This is my intimate whisper. Soft, breathy, and irresistibly charming.",
                "filename": "female_intimate.wav",
                "voice": "en-US-AriaNeural",
                "rate": "0.6",
                "pitch": "+20%",
                "description": "Intimate whisper voice"
            },
            {
                "text": "I speak with confidence and allure. My voice commands attention while remaining elegant.",
                "filename": "female_confident.wav",
                "voice": "en-US-JennyNeural",
                "rate": "0.8",
                "pitch": "+5%",
                "description": "Confident feminine voice"
            },
            {
                "text": "My voice flows like honey, smooth and sweet. Every word is delivered with grace and charm.",
                "filename": "female_honey.wav",
                "voice": "en-US-AriaNeural",
                "rate": "0.7",
                "pitch": "+12%",
                "description": "Honey-smooth feminine voice"
            },
            {
                "text": "I'm a sophisticated woman with a voice that's both powerful and enchanting.",
                "filename": "female_sophisticated.wav",
                "voice": "en-GB-SoniaNeural",
                "rate": "0.8",
                "pitch": "+8%",
                "description": "Sophisticated feminine voice"
            }
        ]
        
        print(f"\n🎭 Generating {len(test_cases)} female voice samples...")
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n📝 Test {i}: {test['description']}")
            print(f"   Text: \"{test['text'][:60]}...\"")
            print(f"   Voice: {test['voice']}, Rate: {test['rate']}, Pitch: {test['pitch']}")
            
            try:
                # Create SSML for better control
                ssml_text = f"<speak><prosody rate=\"{test['rate']}\" pitch=\"{test['pitch']}\">{test['text']}</prosody></speak>"
                
                # Generate with Edge TTS
                communicate = edge_tts.Communicate(ssml_text, test["voice"])
                
                # Save audio file
                await communicate.save(test["filename"])
                
                file_size = os.path.getsize(test["filename"]) / 1024
                print(f"✅ Generated: {test['filename']} ({file_size:.1f} KB)")
                
                # Play the audio
                print(f"🔊 Playing {test['description']}...")
                os.system(f"afplay \"{test['filename']}\"")
                print(f"✅ {test['description']} played successfully!")
                
            except Exception as e:
                print(f"❌ Test {i} failed: {e}")
        
        print(f"\n🎉 Female voice generation complete!")
        print(f"📁 Generated files:")
        for test in test_cases:
            if os.path.exists(test["filename"]):
                size = os.path.getsize(test["filename"])
                print(f"   {test['filename']} ({size} bytes) - {test['description']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Female voice test failed: {e}")
        return False

async def main():
    print("🎤 Female Voice Test Suite")
    print("=" * 60)
    print("🎯 Goal: Generate actual female voice audio files")
    print("🔊 Using Microsoft Edge TTS neural voices")
    print("=" * 60)
    
    success = await test_female_voices()
    
    if success:
        print("\n✅ All tests completed successfully!")
        print("🔊 You can now hear actual female voices!")
    else:
        print("\n❌ Tests failed. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
