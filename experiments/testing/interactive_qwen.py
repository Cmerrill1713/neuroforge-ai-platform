#!/usr/bin/env python3
""'
Interactive Qwen3-Omni Testing Interface

Simple interactive interface for testing the model with custom prompts.
""'

import torch
import time
from transformers import AutoTokenizer, AutoModelForCausalLM
from pathlib import Path
import argparse

class InteractiveQwen:
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    def __init__(self, model_path: str, device: str = "auto'):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.model_path = model_path
        self.device = device
        self.model = None
        self.tokenizer = None
        self.conversation_history = []

    def load_model(self):
        """TODO: Add docstring."""
        """Load the model and tokenizer""'
        print(f"Loading model from {self.model_path}...')

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                torch_dtype=torch.float16,
                device_map=self.device,
                low_cpu_mem_usage=True
            )

            print("✅ Model loaded successfully!')
            return True

        except Exception as e:
            print(f"❌ Failed to load model: {e}')
            return False

    def generate_response(self, prompt: str, **kwargs):
        """TODO: Add docstring."""
        """Generate a response for the given prompt""'
        # Default generation parameters
        generation_params = {
            "max_new_tokens': 512,
            "temperature': 0.7,
            "top_p': 0.9,
            "do_sample': True,
            "pad_token_id': self.tokenizer.eos_token_id,
            "eos_token_id': self.tokenizer.eos_token_id,
        }
        generation_params.update(kwargs)

        try:
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt')

            # Generate response
            start_time = time.time()
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    **generation_params
                )
            generation_time = time.time() - start_time

            # Decode response
            full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = full_response[len(prompt):].strip()

            # Calculate tokens per second
            input_tokens = inputs.input_ids.shape[1]
            output_tokens = outputs.shape[1] - input_tokens
            tokens_per_second = output_tokens / generation_time if generation_time > 0 else 0

            return {
                "response': response,
                "generation_time': generation_time,
                "tokens_per_second': tokens_per_second,
                "input_tokens': input_tokens,
                "output_tokens': output_tokens
            }

        except Exception as e:
            return {"error': str(e)}

    def interactive_session(self):
        """TODO: Add docstring."""
        """Run an interactive session""'
        print("\n🤖 Interactive Qwen3-Omni Session')
        print("=' * 50)
        print("Commands:')
        print("  /help     - Show this help')
        print("  /history  - Show conversation history')
        print("  /clear    - Clear conversation history')
        print("  /params   - Show current generation parameters')
        print("  /set <param> <value> - Set generation parameter')
        print("  /quit     - Exit the session')
        print("=' * 50)

        # Current generation parameters
        params = {
            "max_new_tokens': 512,
            "temperature': 0.7,
            "top_p': 0.9,
            "do_sample': True
        }

        while True:
            try:
                user_input = input("\n💬 You: ').strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith("/'):
                    if user_input == "/help':
                        print("Available commands: /help, /history, /clear, /params, /set, /quit')

                    elif user_input == "/history':
                        if self.conversation_history:
                            print("\n📜 Conversation History:')
                            for i, entry in enumerate(self.conversation_history, 1):
                                print(f"{i}. You: {entry["prompt"][:100]}...')
                                print(f"   Bot: {entry["response"][:100]}...')
                        else:
                            print("No conversation history.')

                    elif user_input == "/clear':
                        self.conversation_history = []
                        print("Conversation history cleared.')

                    elif user_input == "/params':
                        print("\n⚙️ Current Generation Parameters:')
                        for key, value in params.items():
                            print(f"  {key}: {value}')

                    elif user_input.startswith("/set '):
                        try:
                            parts = user_input[5:].split(" ', 1)
                            if len(parts) == 2:
                                param, value = parts
                                # Try to convert value to appropriate type
                                if param in ["max_new_tokens']:
                                    value = int(value)
                                elif param in ["temperature", "top_p']:
                                    value = float(value)
                                elif param in ["do_sample']:
                                    value = value.lower() in ["true", "1", "yes']

                                params[param] = value
                                print(f"✅ Set {param} = {value}')
                            else:
                                print("Usage: /set <parameter> <value>')
                        except Exception as e:
                            print(f"❌ Error setting parameter: {e}')

                    elif user_input == "/quit':
                        print("👋 Goodbye!')
                        break

                    else:
                        print("Unknown command. Type /help for available commands.')
                    continue

                # Generate response
                print("🤔 Thinking...')
                result = self.generate_response(user_input, **params)

                if "error' in result:
                    print(f"❌ Error: {result["error"]}')
                else:
                    print(f"🤖 Qwen: {result["response"]}')
                    print(f"⏱️  Generated {result["output_tokens"]} tokens in {result["generation_time"]:.2f}s '
                          f"({result["tokens_per_second"]:.2f} tok/s)')

                    # Add to conversation history
                    self.conversation_history.append({
                        "prompt': user_input,
                        "response": result["response'],
                        "timestamp': time.time(),
                        "params': params.copy()
                    })

                    # Keep only last 10 interactions
                    if len(self.conversation_history) > 10:
                        self.conversation_history = self.conversation_history[-10:]

            except KeyboardInterrupt:
                print("\n👋 Goodbye!')
                break
            except EOFError:
                print("\n👋 Goodbye!')
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}')

def main():
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    parser = argparse.ArgumentParser(description="Interactive Qwen3-Omni Testing')
    parser.add_argument("--model_path", default="./Qwen3-Omni-30B-A3B-Instruct',
                       help="Path to the model directory')
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda", "mps'],
                       help="Device to run the model on')

    args = parser.parse_args()

    # Check if model exists
    if not Path(args.model_path).exists():
        print(f"❌ Model not found at {args.model_path}')
        return 1

    # Initialize and load model
    qwen = InteractiveQwen(args.model_path, args.device)

    if not qwen.load_model():
        return 1

    # Start interactive session
    qwen.interactive_session()

    return 0

if __name__ == "__main__':
    exit(main())
