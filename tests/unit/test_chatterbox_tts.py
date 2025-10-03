#!/usr/bin/env python3
""'
Test Chatterbox TTS - Better Voice Generation
Using the correct API from Hugging Face documentation
""'

import os
import logging
import torch
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_chatterbox_tts():
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    print("🎤 Testing Chatterbox TTS (Resemble AI)')
    print("=' * 60)
    print("🎯 Goal: Test Chatterbox as DIA alternative')

    try:
        # Initialize Chatterbox TTS using correct API
        print("🔄 Initializing Chatterbox TTS...')
        device = "mps" if torch.backends.mps.is_available() else "cpu'
        print(f"🎯 Using device: {device}')
        model = ChatterboxTTS.from_pretrained(device=device)

        # Test text
        test_text = "Hello! I am Chatterbox TTS, and I should sound much more natural than DIA.'

        print(f"🎭 Generating speech for: "{test_text}"')

        # Generate speech using correct API
        wav = model.generate(test_text)

        # Save audio using torchaudio
        output_file = "chatterbox_test.wav'
        ta.save(output_file, wav, model.sr)

        file_size = os.path.getsize(output_file) / 1024
        print(f"✅ Audio generated: {output_file} ({file_size:.1f} KB)')

        # Play the audio
        print("🔊 Playing Chatterbox TTS audio...')
        try:
            os.system(f"afplay "{output_file}"')
            print("✅ Chatterbox TTS audio played successfully!')
        except Exception as e:
            print(f"⚠️  Could not play audio: {e}')

        return True

    except Exception as e:
        logger.error(f"❌ Chatterbox TTS test failed: {e}')
        return False

def test_emotional_control():
    """TODO: Add docstring."""
    """Test Chatterbox"s unique emotion exaggeration control""'
    print("\n🎭 Testing Emotion Exaggeration Control')
    print("=' * 50)
    print("🎯 Testing Chatterbox"s unique emotion control features')

    try:
        device = "mps" if torch.backends.mps.is_available() else "cpu'
        print(f"🎯 Using device: {device}')
        model = ChatterboxTTS.from_pretrained(device=device)

        # Test different exaggeration levels
        test_cases = [
            {
                "text": "This is a calm and professional voice test.',
                "exaggeration': 0.3,
                "cfg_weight': 0.5,
                "filename": "chatterbox_calm.wav'
            },
            {
                "text": "This is an excited and energetic voice test!',
                "exaggeration': 0.7,
                "cfg_weight': 0.3,
                "filename": "chatterbox_excited.wav'
            },
            {
                "text": "This is a dramatic and expressive voice test.',
                "exaggeration': 0.8,
                "cfg_weight': 0.2,
                "filename": "chatterbox_dramatic.wav'
            }
        ]

        for i, test in enumerate(test_cases, 1):
            print(f"\n📝 Emotional Test {i}: exaggeration={test["exaggeration"]}, cfg_weight={test["cfg_weight"]}')
            print(f"   Text: "{test["text"]}"')

            try:
                # Generate with emotion control parameters
                wav = model.generate(
                    test["text'],
                    exaggeration=test["exaggeration'],
                    cfg_weight=test["cfg_weight']
                )

                # Save audio
                ta.save(test["filename'], wav, model.sr)

                file_size = os.path.getsize(test["filename']) / 1024
                print(f"✅ Generated: {test["filename"]} ({file_size:.1f} KB)')

                # Play audio
                print(f"🔊 Playing emotional test {i}...')
                os.system(f"afplay "{test["filename"]}"')
                print(f"✅ Emotional test {i} played!')

            except Exception as e:
                print(f"❌ Emotional test {i} failed: {e}')

        return True

    except Exception as e:
        logger.error(f"❌ Emotional control test failed: {e}')
        return False

if __name__ == "__main__':
    print("🎤 Chatterbox TTS Test Suite')
    print("=' * 60)

    # Test basic functionality
    success = test_chatterbox_tts()

    if success:
        print("\n✅ Basic test passed! Testing emotion control...')
        test_emotional_control()
    else:
        print("\n❌ Basic test failed. Check the error messages above.')

    print(f"\n🎉 Chatterbox TTS testing completed!')
    print(f"📁 Generated files:')
    for file in os.listdir(".'):
        if file.startswith("chatterbox_test") and file.endswith((".wav", ".mp3')):
            size = os.path.getsize(file)
            print(f"   {file} ({size} bytes)')
