#!/usr/bin/env python3
"""
LFM2 Integration Script
Uses Liquid AI LFM2-1.2B-RAG model via transformers
"""

import torch
import logging
from transformers import AutoTokenizer, AutoModelForCausalLM
import warnings
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LFM2Model:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = None
        self.model_name = "LiquidAI/LFM2-2.6B"
        
    def setup_device(self):
        """Setup the best available device - Use MPS for Apple Silicon acceleration"""
        if torch.backends.mps.is_available():
            self.device = "mps"
            logger.info("⚡ Using MPS (Metal Performance Shaders) for Apple Silicon acceleration")
        else:
            self.device = "cpu"
            logger.info("💻 Using CPU for LFM2")
    
    def load_model(self):
        """Load the LFM2 model"""
        try:
            logger.info(f"🔄 Loading LFM2 model: {self.model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device != "cpu" else torch.float32,
                device_map="auto" if self.device != "cpu" else None,
                trust_remote_code=True
            )
            
            if self.device != "cpu":
                self.model = self.model.to(self.device)
            
            logger.info("✅ LFM2 model loaded successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load LFM2 model: {e}")
            return False
    
    def generate_response(self, prompt, max_length=150, temperature=0.7):
        """Generate a response using LFM2"""
        if not self.model or not self.tokenizer:
            return "LFM2 model not loaded"
        
        try:
            # Tokenize input
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            if self.device != "cpu":
                inputs = inputs.to(self.device)
            
            # Generate response
            with torch.no_grad():
                try:
                    outputs = self.model.generate(
                        inputs,
                        max_new_tokens=max_length,
                        temperature=temperature,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                        num_beams=1,
                        early_stopping=True,
                        repetition_penalty=1.1,
                        no_repeat_ngram_size=2
                    )
                except RuntimeError as mps_error:
                    if "mps" in str(mps_error).lower():
                        logger.warning(f"MPS error, falling back to CPU: {mps_error}")
                        # Fallback to CPU
                        self.device = "cpu"
                        self.model = self.model.to("cpu")
                        inputs = inputs.to("cpu")
                        outputs = self.model.generate(
                            inputs,
                            max_new_tokens=max_length,
                            temperature=temperature,
                            do_sample=True,
                            pad_token_id=self.tokenizer.eos_token_id,
                            eos_token_id=self.tokenizer.eos_token_id,
                            num_beams=1,
                            early_stopping=True,
                            repetition_penalty=1.1,
                            no_repeat_ngram_size=2
                        )
                    else:
                        raise
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the input prompt from response
            if response.startswith(prompt):
                response = response[len(prompt):].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"❌ LFM2 generation failed: {e}")
            return f"Error generating response: {e}"

def test_lfm2():
    """Test the LFM2 model"""
    logger.info("🧪 Testing LFM2 model...")
    
    lfm2 = LFM2Model()
    lfm2.setup_device()
    
    if lfm2.load_model():
        # Test with a simple prompt
        test_prompt = "Hello, how are you?"
        response = lfm2.generate_response(test_prompt)
        
        logger.info(f"📝 Test prompt: {test_prompt}")
        logger.info(f"🤖 LFM2 response: {response}")
        
        return True
    else:
        logger.error("❌ LFM2 test failed")
        return False

if __name__ == "__main__":
    test_lfm2()
