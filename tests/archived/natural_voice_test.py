#!/usr/bin/env python3
""'
Chatterbox TTS Natural Voice Test - Python Version
Test voice input/output functionality with Chatterbox TTS and macOS say command
""'

import subprocess
import requests
import json
import time
import os

class ChatterboxVoiceTester:
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    def __init__(self):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.tts_server_url = "http://localhost:8086'
        self.ollama_url = "http://localhost:11434'

        # Chatterbox voice profiles
        self.voice_profiles = [
            {"name": "assistant", "description": "Friendly assistant voice'},
            {"name": "professional", "description": "Professional male voice'},
            {"name": "narrator", "description": "Clear narrator voice'},
            {"name": "excited", "description": "Energetic and excited voice'},
            {"name": "calm", "description": "Calm and soothing voice'},
            {"name": "news", "description": "Authoritative news voice'}
        ]

        # macOS natural voices as fallback
        self.natural_voices = [
            {"name": "Samantha", "accent": "US", "description": "Natural American female'},
            {"name": "Daniel", "accent": "UK", "description": "Natural British male'},
            {"name": "Alex", "accent": "US", "description": "Natural American male'},
            {"name": "Victoria", "accent": "US", "description": "Natural American female'},
        ]

    def test_chatterbox_status(self):
        """TODO: Add docstring."""
        """Test Chatterbox TTS server status""'
        print("🔊 Testing Chatterbox TTS Server Status')
        print("=' * 50)

        try:
            response = requests.get(f"{self.tts_server_url}/status', timeout=10)
            if response.ok:
                status = response.json()
                print("✅ Chatterbox TTS Server Status:')
                print(f"   Status: {status.get("status", "unknown")}')
                print(f"   Chatterbox Loaded: {status.get("chatterbox_loaded", False)}')
                print(f"   Available Profiles: {status.get("profiles_available", 0)}')
                print(f"   Engines: {", ".join(status.get("engines", []))}')
                return True
            else:
                print(f"❌ TTS Server Error: {response.status_code}')
                return False
        except Exception as e:
            print(f"❌ TTS Server Error: {e}')
            return False

    def test_chatterbox_synthesis(self, text, voice_profile="assistant", emotion="neutral", speed="normal'):
        """TODO: Add docstring."""
        """Test Chatterbox TTS synthesis""'
        try:
            print(f"🎭 Testing Chatterbox TTS: {voice_profile} profile')
            print(f"📝 Text: {text}')

            response = requests.post(f"{self.tts_server_url}/synthesize',
                json={
                    "text': text,
                    "voice_profile': voice_profile,
                    "emotion': emotion,
                    "speed': speed,
                    "use_chatterbox': True
                },
                timeout=30
            )

            if response.ok:
                result = response.json()
                print(f"✅ Chatterbox TTS Success:')
                print(f"   Engine: {result.get("engine", "unknown")}')
                print(f"   Voice: {result.get("voice", "unknown")}')
                print(f"   File Size: {result.get("file_size_kb", 0)} KB')
                return True
            else:
                print(f"❌ Chatterbox TTS Failed: {response.status_code}')
                return False

        except Exception as e:
            print(f"❌ Chatterbox TTS Error: {e}')
            return False

    def test_ai_response_with_chatterbox(self, voice_profile="assistant'):
        """TODO: Add docstring."""
        """Get AI response and synthesize with Chatterbox TTS""'
        print(f"\n🤖 AI Response with Chatterbox TTS ({voice_profile})')
        print("=' * 50)

        try:
            # Get AI response
            response = requests.post(f"{self.ollama_url}/api/generate',
                json={
                    "model": "qwen2.5:7b',
                    "prompt": "Please respond with a helpful and friendly message that would sound natural when spoken aloud. Keep it conversational and warm.',
                    "stream': False,
                    "options': {
                        "temperature': 0.8,
                        "num_predict': 100
                    }
                },
                timeout=30
            )

            if response.ok:
                result = response.json()
                ai_response = result.get("response", "No response')

                print(f"🤖 AI Response: {ai_response}')

                # Synthesize with Chatterbox TTS
                success = self.test_chatterbox_synthesis(ai_response, voice_profile, "friendly", "normal')

                if success:
                    print(f"✅ Successfully synthesized AI response with Chatterbox TTS')
                else:
                    print(f"❌ Failed to synthesize AI response')

            else:
                print(f"❌ AI request failed: {response.status_code}')

        except Exception as e:
            print(f"❌ Error: {e}')

    def test_all_chatterbox_profiles(self):
        """TODO: Add docstring."""
        """Test all Chatterbox voice profiles""'
        print("\n🎨 Testing All Chatterbox Voice Profiles')
        print("=' * 50)

        test_texts = [
            "Hello! I am your AI assistant powered by Chatterbox TTS.',
            "The weather is beautiful today! Perfect for a walk outside.',
            "Why did the chicken cross the road? To get to the other side!',
            "I can help you with questions, tasks, and conversations.'
        ]

        for profile in self.voice_profiles:
            print(f"\n🎭 Testing {profile["name"]} profile: {profile["description"]}')

            for i, text in enumerate(test_texts, 1):
                print(f"\n📝 Test {i}: {text}')
                success = self.test_chatterbox_synthesis(text, profile["name'])

                if success:
                    time.sleep(1)  # Brief pause between tests
                else:
                    break

    def test_fallback_voice(self, voice_name="Samantha", text="This is a fallback voice test using macOS say command.'):
        """TODO: Add docstring."""
        """Test fallback voice using macOS say command""'
        try:
            print(f"🎤 Testing Fallback Voice: {voice_name}')
            print(f"📝 Text: {text}')

            result = subprocess.run([
                "say", "-v', voice_name, text
            ], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                print(f"✅ {voice_name} spoke successfully (fallback)')
                return True
            else:
                print(f"❌ {voice_name} failed: {result.stderr}')
                return False

        except subprocess.TimeoutExpired:
            print(f"⏰ {voice_name} timed out')
            return False
        except Exception as e:
            print(f"❌ {voice_name} error: {e}')
            return False

    def test_complete_voice_pipeline(self):
        """TODO: Add docstring."""
        """Test complete voice pipeline: AI → Chatterbox TTS → Fallback""'
        print("\n🎯 Testing Complete Voice Pipeline')
        print("=' * 50)

        # Test 1: Chatterbox TTS
        print("\n1️⃣ Testing Chatterbox TTS Pipeline')
        self.test_ai_response_with_chatterbox("assistant')

        # Test 2: Fallback voice
        print("\n2️⃣ Testing Fallback Voice Pipeline')
        self.test_fallback_voice("Samantha", "This is a fallback voice test using macOS say command.')

        # Test 3: Different Chatterbox profiles
        print("\n3️⃣ Testing Different Chatterbox Profiles')
        self.test_all_chatterbox_profiles()

    def interactive_voice_test(self):
        """TODO: Add docstring."""
        """Interactive voice testing""'
        print("\n🎤 Interactive Chatterbox Voice Test')
        print("=' * 50)

        while True:
            print("\nAvailable options:')
            print("1. Test Chatterbox TTS profiles')
            print("2. Test AI response with Chatterbox')
            print("3. Test fallback voices')
            print("4. Test complete pipeline')
            print("0. Exit')

            try:
                choice = input("\nSelect option (1-4) or 0 to exit: ').strip()

                if choice == "0':
                    break
                elif choice == "1':
                    self.test_all_chatterbox_profiles()
                elif choice == "2':
                    profile = input("Enter voice profile (assistant/professional/narrator/excited/calm/news): ').strip()
                    if profile in [p["name'] for p in self.voice_profiles]:
                        self.test_ai_response_with_chatterbox(profile)
                    else:
                        print("Invalid profile')
                elif choice == "3':
                    voice = input("Enter macOS voice name (Samantha/Daniel/Alex/Victoria): ').strip()
                    text = input("Enter text to speak: ').strip()
                    if text:
                        self.test_fallback_voice(voice, text)
                elif choice == "4':
                    self.test_complete_voice_pipeline()
                else:
                    print("Invalid choice')

            except (ValueError, KeyboardInterrupt):
                break

        print("👋 Goodbye!')

def main():
    """TODO: Add docstring."""
    """Main function""'
    print("🎤 Chatterbox TTS Voice System Test')
    print("=' * 60)

    tester = ChatterboxVoiceTester()

    # Test 1: Check TTS server status
    if not tester.test_chatterbox_status():
        print("\n⚠️  Chatterbox TTS server not available. Testing fallback voices only.')
        tester.test_fallback_voice()
        return

    # Test 2: Test complete voice pipeline
    tester.test_complete_voice_pipeline()

    # Test 3: Interactive testing
    tester.interactive_voice_test()

if __name__ == "__main__':
    main()