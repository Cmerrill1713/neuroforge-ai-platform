#!/usr/bin/env python3
""'
Qwen3-Omni Model Analysis

This script analyzes the Qwen3-Omni model configuration and capabilities
without loading the full model weights.
""'

import os
import json
import logging
from pathlib import Path
from transformers import AutoConfig, AutoTokenizer
import torch

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_qwen_model():
    """TODO: Add docstring."""
    """Analyze Qwen3-Omni model configuration""'
    logger.info("🔍 Qwen3-Omni Model Analysis')
    logger.info("=' * 50)

    model_path = "./Qwen3-Omni-30B-A3B-Instruct'

    if not os.path.exists(model_path):
        logger.error(f"❌ Model not found at {model_path}')
        return False

    logger.info(f"✅ Model found at {model_path}')

    try:
        # Analyze model configuration
        logger.info("📥 Loading model configuration...')
        config = AutoConfig.from_pretrained(model_path, trust_remote_code=True)

        logger.info("📊 Model Configuration:')
        logger.info(f"   Model Type: {config.model_type}')
        logger.info(f"   Architecture: {config.architectures}')
        logger.info(f"   Hidden Size: {getattr(config, "hidden_size", "N/A")}')
        logger.info(f"   Intermediate Size: {getattr(config, "intermediate_size", "N/A")}')
        logger.info(f"   Num Layers: {getattr(config, "num_hidden_layers", "N/A")}')
        logger.info(f"   Num Attention Heads: {getattr(config, "num_attention_heads", "N/A")}')
        logger.info(f"   Vocab Size: {getattr(config, "vocab_size", "N/A")}')
        logger.info(f"   Max Position Embeddings: {getattr(config, "max_position_embeddings", "N/A")}')

        # Check for multimodal capabilities
        if hasattr(config, "vision_config'):
            logger.info("   ✅ Vision capabilities detected')
            logger.info(f"   Vision Model: {config.vision_config}')

        if hasattr(config, "audio_config'):
            logger.info("   ✅ Audio capabilities detected')
            logger.info(f"   Audio Model: {config.audio_config}')

        # Analyze tokenizer
        logger.info("\n📥 Loading tokenizer...')
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

        logger.info("📊 Tokenizer Information:')
        logger.info(f"   Vocab Size: {len(tokenizer)}')
        logger.info(f"   Special Tokens: {tokenizer.special_tokens_map}')
        logger.info(f"   Chat Template Available: {tokenizer.chat_template is not None}')

        # Test tokenization
        test_text = "Hello, how are you?'
        tokens = tokenizer.encode(test_text)
        decoded = tokenizer.decode(tokens)

        logger.info(f"   Test Tokenization:')
        logger.info(f"     Input: {test_text}')
        logger.info(f"     Tokens: {tokens[:10]}...')  # Show first 10 tokens
        logger.info(f"     Decoded: {decoded}')

        # Analyze model files
        logger.info("\n📁 Model Files Analysis:')
        model_dir = Path(model_path)
        files = list(model_dir.iterdir())

        total_size = 0
        for file in files:
            if file.is_file():
                size = file.stat().st_size
                total_size += size
                size_gb = size / (1024**3)
                logger.info(f"   {file.name}: {size_gb:.2f} GB')

        total_gb = total_size / (1024**3)
        logger.info(f"   Total Model Size: {total_gb:.2f} GB')

        # Check for sharded files
        shard_files = [f for f in files if "pytorch_model" in f.name and f.suffix == ".bin']
        if shard_files:
            logger.info(f"   Model Shards: {len(shard_files)} files')

        # Test chat template if available
        if tokenizer.chat_template:
            logger.info("\n💬 Chat Template Test:')
            messages = [
                {"role": "user", "content": "What is artificial intelligence?'}
            ]

            try:
                formatted = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
                logger.info(f"   Formatted: {formatted[:100]}...')
            except Exception as e:
                logger.warning(f"   Chat template failed: {e}')

        # Memory estimation
        logger.info("\n💾 Memory Estimation:')
        if hasattr(config, "hidden_size") and hasattr(config, "num_hidden_layers'):
            # Rough estimation: 4 * hidden_size * num_layers * 4 bytes (float32)
            estimated_params = config.hidden_size * config.num_hidden_layers * 4
            estimated_memory_gb = estimated_params * 4 / (1024**3)  # 4 bytes per float32
            logger.info(f"   Estimated Parameters: ~{estimated_params/1e9:.1f}B')
            logger.info(f"   Estimated Memory (FP32): ~{estimated_memory_gb:.1f} GB')
            logger.info(f"   Estimated Memory (FP16): ~{estimated_memory_gb/2:.1f} GB')
            logger.info(f"   Estimated Memory (INT8): ~{estimated_memory_gb/4:.1f} GB')
            logger.info(f"   Estimated Memory (INT4): ~{estimated_memory_gb/8:.1f} GB')

        logger.info("\n🎉 Model analysis completed successfully!')
        return True

    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}')
        import traceback
        traceback.print_exc()
        return False

def main():
    """TODO: Add docstring."""
    """Main analysis function""'
    success = analyze_qwen_model()
    return success

if __name__ == "__main__':
    success = main()
    exit(0 if success else 1)
