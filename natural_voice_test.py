#!/usr/bin/env python3
"""
Natural Voice Test using macOS Say Command
Test real, human-like voices instead of robotic browser TTS
"""

import subprocess
import json
import time
import requests

class NaturalVoiceTester:
    def __init__(self):
        self.natural_voices = [
            {"name": "Samantha", "accent": "US", "description": "Natural American female"},
            {"name": "Daniel", "accent": "UK", "description": "Natural British male"},
            {"name": "Karen", "accent": "AU", "description": "Natural Australian female"},
            {"name": "Moira", "accent": "IE", "description": "Natural Irish female"},
            {"name": "Tessa", "accent": "ZA", "description": "Natural South African female"},
            {"name": "Alex", "accent": "US", "description": "Natural American male"},
            {"name": "Victoria", "accent": "US", "description": "Natural American female"},
            {"name": "Fiona", "accent": "GB", "description": "Natural Scottish female"},
        ]
        
    def test_voice(self, voice_name, text):
        """Test a specific voice"""
        try:
            print(f"🎤 Testing {voice_name}: {text}")
            result = subprocess.run([
                'say', '-v', voice_name, text
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ {voice_name} spoke successfully")
                return True
            else:
                print(f"❌ {voice_name} failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {voice_name} timed out")
            return False
        except Exception as e:
            print(f"❌ {voice_name} error: {e}")
            return False
    
    def test_all_natural_voices(self):
        """Test all natural voices"""
        print("🎤 Testing All Natural Voices")
        print("=" * 50)
        
        test_texts = [
            "Hello! I am your AI assistant. How can I help you today?",
            "The weather is beautiful today! Perfect for a walk outside.",
            "Why did the chicken cross the road? To get to the other side!",
            "I can help you with questions, tasks, and conversations."
        ]
        
        for voice in self.natural_voices:
            print(f"\n🎭 Testing {voice['name']} ({voice['accent']} - {voice['description']})")
            
            for i, text in enumerate(test_texts, 1):
                print(f"\n📝 Test {i}: {text}")
                success = self.test_voice(voice['name'], text)
                
                if success:
                    time.sleep(2)  # Brief pause between tests
                else:
                    break
    
    def test_ai_response_with_voice(self, voice_name="Samantha"):
        """Get AI response and speak it with natural voice"""
        print(f"\n🤖 Getting AI Response with {voice_name} Voice")
        print("=" * 50)
        
        try:
            # Get AI response
            response = requests.post('http://localhost:11435/api/generate', 
                json={
                    "model": "qwen2.5:7b",
                    "prompt": "Please respond with a helpful and friendly message that would sound natural when spoken aloud. Keep it conversational and warm.",
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "num_predict": 100
                    }
                },
                timeout=30
            )
            
            if response.ok:
                result = response.json()
                ai_response = result.response or "No response"
                
                print(f"🤖 AI Response: {ai_response}")
                print(f"🎤 Speaking with {voice_name}...")
                
                # Speak with natural voice
                success = self.test_voice(voice_name, ai_response)
                
                if success:
                    print(f"✅ Successfully spoke AI response with {voice_name}")
                else:
                    print(f"❌ Failed to speak AI response")
                    
            else:
                print(f"❌ AI request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def interactive_voice_test(self):
        """Interactive voice testing"""
        print("\n🎤 Interactive Voice Test")
        print("=" * 50)
        
        while True:
            print("\nAvailable voices:")
            for i, voice in enumerate(self.natural_voices, 1):
                print(f"{i}. {voice['name']} ({voice['accent']}) - {voice['description']}")
            
            print("0. Exit")
            
            try:
                choice = input("\nSelect voice (1-8) or 0 to exit: ").strip()
                
                if choice == "0":
                    break
                    
                voice_index = int(choice) - 1
                if 0 <= voice_index < len(self.natural_voices):
                    voice = self.natural_voices[voice_index]
                    
                    text = input(f"Enter text for {voice['name']} to speak: ").strip()
                    if text:
                        self.test_voice(voice['name'], text)
                else:
                    print("Invalid choice")
                    
            except (ValueError, KeyboardInterrupt):
                break
        
        print("👋 Goodbye!")

def main():
    """Main function"""
    print("🎤 Natural Voice Test - Real Human-Like Voices")
    print("=" * 60)
    
    tester = NaturalVoiceTester()
    
    # Test 1: Test all natural voices
    tester.test_all_natural_voices()
    
    # Test 2: Test AI response with natural voice
    tester.test_ai_response_with_voice("Samantha")
    
    # Test 3: Interactive testing
    tester.interactive_voice_test()

if __name__ == "__main__":
    main()
