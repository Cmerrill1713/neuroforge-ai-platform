#!/usr/bin/env python3
"""
Convert LFM2 RAG model to MLX format for Apple GPU acceleration
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_mlx_lm():
    """Check if mlx-lm is installed"""
    try:
        import mlx_lm
        logger.info(f"✅ mlx-lm available: {mlx_lm.__version__}")
        return True
    except ImportError:
        logger.warning("❌ mlx-lm not installed")
        return False

def install_mlx_lm():
    """Install mlx-lm if not available"""
    logger.info("📦 Installing mlx-lm...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "mlx-lm", "--upgrade"
        ], check=True)
        logger.info("✅ mlx-lm installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install mlx-lm: {e}")
        return False

def convert_lfm2_to_mlx():
    """Convert LFM2 model to MLX format"""
    logger.info("🔄 Converting LFM2 RAG model to MLX format...")
    
    # Model details
    model_name = "LiquidAI/LFM2-1.2B-RAG"
    mlx_output_path = "./mlx_models/lfm2-1.2b-rag-mlx"
    
    # Create output directory
    Path(mlx_output_path).mkdir(parents=True, exist_ok=True)
    
    try:
        from mlx_lm import convert
        
        logger.info(f"📥 Converting {model_name} to MLX format...")
        logger.info(f"📤 Output path: {mlx_output_path}")
        
        # Convert the model
        convert(
            hf_path=model_name,
            mlx_path=mlx_output_path,
            quantize=True,  # Quantize for better performance
            q_bits=4,       # 4-bit quantization
            q_group_size=64
        )
        
        logger.info(f"✅ LFM2 model converted to MLX format: {mlx_output_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Conversion failed: {e}")
        return False

def test_mlx_model():
    """Test the converted MLX model"""
    logger.info("🧪 Testing converted MLX model...")
    
    mlx_model_path = "./mlx_models/lfm2-1.2b-rag-mlx"
    
    try:
        from mlx_lm import load, generate
        
        # Load the model
        logger.info(f"📥 Loading MLX model from: {mlx_model_path}")
        model, tokenizer = load(mlx_model_path)
        
        # Test generation
        test_prompt = "What is machine learning?"
        logger.info(f"🔍 Testing with prompt: {test_prompt}")
        
        response = generate(
            model=model,
            tokenizer=tokenizer,
            prompt=test_prompt,
            max_tokens=50,
            temp=0.7
        )
        
        logger.info(f"✅ MLX model test successful!")
        logger.info(f"📝 Response: {response}")
        return True
        
    except Exception as e:
        logger.error(f"❌ MLX model test failed: {e}")
        return False

def create_mlx_rag_service():
    """Create MLX-specific RAG service"""
    logger.info("🔧 Creating MLX RAG service...")
    
    mlx_rag_service_code = '''#!/usr/bin/env python3
"""
MLX RAG Service for Apple GPU acceleration
"""

import logging
import time
import numpy as np
from typing import List, Dict, Any, Optional
import mlx.core as mx
from mlx_lm import load, generate

logger = logging.getLogger(__name__)

class MLXRAGService:
    """MLX-powered RAG service for Apple GPU acceleration"""
    
    def __init__(self, model_path: str = "./mlx_models/lfm2-1.2b-rag-mlx"):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.loaded = False
        
    def load_model(self) -> bool:
        """Load MLX model and tokenizer"""
        try:
            logger.info(f"📥 Loading MLX RAG model from: {self.model_path}")
            self.model, self.tokenizer = load(self.model_path)
            self.loaded = True
            logger.info("✅ MLX RAG model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load MLX model: {e}")
            return False
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using MLX model"""
        if not self.loaded:
            if not self.load_model():
                raise RuntimeError("Failed to load MLX model")
        
        try:
            # For now, use a simple approach - in practice, you'd need
            # to implement proper embedding extraction from the model
            # This is a placeholder implementation
            logger.warning("⚠️ Embedding generation not fully implemented for MLX")
            return [0.0] * 2048  # Placeholder 2048-dim embedding
            
        except Exception as e:
            logger.error(f"❌ Embedding generation failed: {e}")
            raise
    
    def generate_response(self, query: str, context: str = "", max_tokens: int = 512) -> str:
        """Generate RAG response using MLX model"""
        if not self.loaded:
            if not self.load_model():
                raise RuntimeError("Failed to load MLX model")
        
        try:
            # Build prompt with context
            if context:
                prompt = f"Context: {context}\\n\\nQuery: {query}\\n\\nAnswer:"
            else:
                prompt = f"Query: {query}\\n\\nAnswer:"
            
            logger.info(f"🔍 Generating MLX response for: {query[:50]}...")
            
            # Generate response
            response = generate(
                model=self.model,
                tokenizer=self.tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                temp=0.7
            )
            
            logger.info(f"✅ MLX response generated: {response[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"❌ MLX response generation failed: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_path": self.model_path,
            "loaded": self.loaded,
            "framework": "mlx",
            "device": str(mx.default_device()),
            "model_type": "LFM2-1.2B-RAG-MLX"
        }

# Global instance
mlx_rag_service = MLXRAGService()

def get_mlx_rag_service() -> MLXRAGService:
    """Get global MLX RAG service instance"""
    return mlx_rag_service
'''
    
    # Write the MLX RAG service
    mlx_service_path = "src/core/retrieval/mlx_rag_service.py"
    with open(mlx_service_path, 'w') as f:
        f.write(mlx_rag_service_code)
    
    logger.info(f"✅ MLX RAG service created: {mlx_service_path}")
    return True

def main():
    """Main conversion process"""
    logger.info("🚀 Starting LFM2 to MLX conversion process...")
    
    # Step 1: Check/install mlx-lm
    if not check_mlx_lm():
        if not install_mlx_lm():
            logger.error("❌ Cannot proceed without mlx-lm")
            return False
    
    # Step 2: Convert model
    if not convert_lfm2_to_mlx():
        logger.error("❌ Model conversion failed")
        return False
    
    # Step 3: Test converted model
    if not test_mlx_model():
        logger.error("❌ Model test failed")
        return False
    
    # Step 4: Create MLX RAG service
    if not create_mlx_rag_service():
        logger.error("❌ MLX RAG service creation failed")
        return False
    
    logger.info("🎉 LFM2 to MLX conversion completed successfully!")
    logger.info("📁 MLX model saved to: ./mlx_models/lfm2-1.2b-rag-mlx")
    logger.info("🔧 MLX RAG service created: src/core/retrieval/mlx_rag_service.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
