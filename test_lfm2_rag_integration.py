#!/usr/bin/env python3
"""
LFM2 RAG Integration Script
Uses Liquid AI LFM2-2.6B-RAG model for retrieval-augmented generation
"""

import torch
import logging
from transformers import AutoTokenizer, AutoModelForCausalLM
import warnings
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LFM2RAGModel:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = None
        self.model_name = "LiquidAI/LFM2-1.2B-RAG"
        
    def setup_device(self):
        """Setup the best available device - Force CPU for LFM2 compatibility"""
        self.device = "cpu"  # Force CPU due to MPS compatibility issues
        logger.info("💻 Using CPU for LFM2 RAG (MPS compatibility issues)")
    
    def load_model(self):
        """Load the LFM2 RAG model"""
        try:
            logger.info(f"🔄 Loading LFM2 RAG model: {self.model_name}")
            
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
            
            logger.info("✅ LFM2 RAG model loaded successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load LFM2 RAG model: {e}")
            return False
    
    def generate_rag_response(self, query, context="", max_length=200, temperature=0.7):
        """Generate a RAG response using LFM2 with context"""
        if not self.model or not self.tokenizer:
            return "LFM2 RAG model not loaded"
        
        try:
            # Format prompt with context for RAG
            if context:
                prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"
            else:
                prompt = f"Question: {query}\n\nAnswer:"
            
            # Tokenize input
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            if self.device != "cpu":
                inputs = inputs.to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=max_length,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract just the answer part
            if "Answer:" in response:
                response = response.split("Answer:")[-1].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"❌ LFM2 RAG generation failed: {e}")
            return f"Error generating RAG response: {e}"

def test_lfm2_rag():
    """Test the LFM2 RAG model"""
    logger.info("🧪 Testing LFM2 RAG model...")
    
    lfm2_rag = LFM2RAGModel()
    lfm2_rag.setup_device()
    
    if lfm2_rag.load_model():
        # Test with a RAG-style prompt
        test_query = "What is artificial intelligence?"
        test_context = "Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals."
        
        response = lfm2_rag.generate_rag_response(test_query, test_context)
        
        logger.info(f"📝 Test query: {test_query}")
        logger.info(f"📚 Context: {test_context}")
        logger.info(f"🤖 LFM2 RAG response: {response}")
        
        return True
    else:
        logger.error("❌ LFM2 RAG test failed")
        return False

if __name__ == "__main__":
    test_lfm2_rag()
