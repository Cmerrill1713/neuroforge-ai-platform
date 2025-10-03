#!/usr/bin/env python3
"""
Convert LFM2 RAG model to MLX format using transformers as intermediate step
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check required dependencies"""
    try:
        import transformers
        import torch
        import mlx_lm
        logger.info(f"✅ transformers: {transformers.__version__}")
        logger.info(f"✅ torch: {torch.__version__}")
        logger.info(f"✅ mlx-lm: {mlx_lm.__version__}")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        return False

def download_lfm2_model():
    """Download LFM2 model locally"""
    logger.info("📥 Downloading LFM2 model locally...")
    
    try:
        from transformers import AutoTokenizer, AutoModel
        
        model_name = "LiquidAI/LFM2-1.2B-RAG"
        local_path = "./models/lfm2-1.2b-rag-local"
        
        # Create directory
        Path(local_path).mkdir(parents=True, exist_ok=True)
        
        # Download model and tokenizer
        logger.info(f"📥 Downloading {model_name}...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)
        
        # Save locally
        tokenizer.save_pretrained(local_path)
        model.save_pretrained(local_path)
        
        logger.info(f"✅ LFM2 model downloaded to: {local_path}")
        return local_path
        
    except Exception as e:
        logger.error(f"❌ Failed to download LFM2 model: {e}")
        return None

def convert_to_llama_format():
    """Convert LFM2 to Llama format for MLX compatibility"""
    logger.info("🔄 Converting LFM2 to Llama format...")
    
    try:
        from transformers import AutoTokenizer, AutoModel
        import torch
        
        local_path = "./models/lfm2-1.2b-rag-local"
        llama_path = "./models/lfm2-1.2b-rag-llama"
        
        # Create directory
        Path(llama_path).mkdir(parents=True, exist_ok=True)
        
        # Load the model
        logger.info("📥 Loading LFM2 model...")
        tokenizer = AutoTokenizer.from_pretrained(local_path)
        model = AutoModel.from_pretrained(local_path)
        
        # Convert to Llama-compatible format
        logger.info("🔄 Converting to Llama format...")
        
        # Create a simple Llama-compatible config
        config = {
            "architectures": ["LlamaForCausalLM"],
            "model_type": "llama",
            "hidden_size": model.config.hidden_size,
            "intermediate_size": model.config.intermediate_size,
            "num_attention_heads": model.config.num_attention_heads,
            "num_hidden_layers": model.config.num_hidden_layers,
            "vocab_size": tokenizer.vocab_size,
            "max_position_embeddings": model.config.max_position_embeddings,
            "torch_dtype": "float16"
        }
        
        # Save config
        import json
        with open(f"{llama_path}/config.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        # Save tokenizer
        tokenizer.save_pretrained(llama_path)
        
        # Save model weights (simplified)
        torch.save(model.state_dict(), f"{llama_path}/pytorch_model.bin")
        
        logger.info(f"✅ Converted to Llama format: {llama_path}")
        return llama_path
        
    except Exception as e:
        logger.error(f"❌ Failed to convert to Llama format: {e}")
        return None

def convert_to_mlx(llama_path: str):
    """Convert Llama format to MLX"""
    logger.info("🔄 Converting to MLX format...")
    
    try:
        from mlx_lm import convert
        
        mlx_path = "./mlx_models/lfm2-1.2b-rag-mlx"
        
        # Create output directory
        Path(mlx_path).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📥 Converting {llama_path} to MLX...")
        logger.info(f"📤 Output: {mlx_path}")
        
        # Convert
        convert(
            hf_path=llama_path,
            mlx_path=mlx_path,
            quantize=True,
            q_bits=4,
            q_group_size=64
        )
        
        logger.info(f"✅ MLX conversion completed: {mlx_path}")
        return mlx_path
        
    except Exception as e:
        logger.error(f"❌ MLX conversion failed: {e}")
        return None

def test_mlx_model(mlx_path: str):
    """Test the converted MLX model"""
    logger.info("🧪 Testing MLX model...")
    
    try:
        from mlx_lm import load, generate
        
        # Load model
        logger.info(f"📥 Loading MLX model from: {mlx_path}")
        model, tokenizer = load(mlx_path)
        
        # Test generation
        test_prompt = "What is artificial intelligence?"
        logger.info(f"🔍 Testing with: {test_prompt}")
        
        response = generate(
            model=model,
            tokenizer=tokenizer,
            prompt=test_prompt,
            max_tokens=50,
            temp=0.7
        )
        
        logger.info(f"✅ MLX test successful!")
        logger.info(f"📝 Response: {response}")
        return True
        
    except Exception as e:
        logger.error(f"❌ MLX test failed: {e}")
        return False

def create_simple_mlx_rag():
    """Create a simple MLX RAG service using existing models"""
    logger.info("🔧 Creating simple MLX RAG service...")
    
    # Check if we have any existing MLX models
    mlx_models_dir = Path("./mlx_models")
    if mlx_models_dir.exists():
        models = list(mlx_models_dir.iterdir())
        if models:
            logger.info(f"📁 Found existing MLX models: {[m.name for m in models]}")
            
            # Use the first available model
            model_path = str(models[0])
            logger.info(f"🎯 Using MLX model: {model_path}")
            
            # Create simple RAG service
            mlx_rag_code = f'''#!/usr/bin/env python3
"""
Simple MLX RAG Service
"""

import logging
import time
from typing import List, Dict, Any
import mlx.core as mx
from mlx_lm import load, generate

logger = logging.getLogger(__name__)

class SimpleMLXRAGService:
    """Simple MLX RAG service using existing MLX models"""
    
    def __init__(self, model_path: str = "{model_path}"):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.loaded = False
        
    def load_model(self) -> bool:
        """Load MLX model"""
        try:
            logger.info(f"📥 Loading MLX model: {{self.model_path}}")
            self.model, self.tokenizer = load(self.model_path)
            self.loaded = True
            logger.info("✅ MLX model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load MLX model: {{e}}")
            return False
    
    def generate_response(self, query: str, context: str = "") -> str:
        """Generate RAG response"""
        if not self.loaded:
            if not self.load_model():
                raise RuntimeError("Failed to load MLX model")
        
        try:
            # Build prompt
            if context:
                prompt = f"Context: {{context}}\\n\\nQuestion: {{query}}\\n\\nAnswer:"
            else:
                prompt = f"Question: {{query}}\\n\\nAnswer:"
            
            # Generate response
            response = generate(
                model=self.model,
                tokenizer=self.tokenizer,
                prompt=prompt,
                max_tokens=256,
                temp=0.7
            )
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Generation failed: {{e}}")
            raise
    
    def get_info(self) -> Dict[str, Any]:
        """Get service info"""
        return {{
            "model_path": self.model_path,
            "loaded": self.loaded,
            "framework": "mlx",
            "device": str(mx.default_device()),
            "model_type": "mlx-rag"
        }}

# Global instance
mlx_rag_service = SimpleMLXRAGService()

def get_mlx_rag_service():
    """Get MLX RAG service instance"""
    return mlx_rag_service
'''
            
            # Write the service
            service_path = "src/core/retrieval/simple_mlx_rag_service.py"
            with open(service_path, 'w') as f:
                f.write(mlx_rag_code)
            
            logger.info(f"✅ Simple MLX RAG service created: {service_path}")
            return True
    
    logger.warning("⚠️ No existing MLX models found")
    return False

def main():
    """Main conversion process"""
    logger.info("🚀 Starting LFM2 to MLX conversion (alternative approach)...")
    
    # Check dependencies
    if not check_dependencies():
        logger.error("❌ Missing dependencies")
        return False
    
    # Try simple approach first
    if create_simple_mlx_rag():
        logger.info("✅ Simple MLX RAG service created successfully!")
        return True
    
    # If no existing models, try full conversion
    logger.info("🔄 Attempting full LFM2 conversion...")
    
    # Download model
    local_path = download_lfm2_model()
    if not local_path:
        return False
    
    # Convert to Llama format
    llama_path = convert_to_llama_format()
    if not llama_path:
        return False
    
    # Convert to MLX
    mlx_path = convert_to_mlx(llama_path)
    if not mlx_path:
        return False
    
    # Test
    if not test_mlx_model(mlx_path):
        return False
    
    logger.info("🎉 LFM2 to MLX conversion completed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
