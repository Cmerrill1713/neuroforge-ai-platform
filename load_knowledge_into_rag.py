#!/usr/bin/env python3
"""
Load knowledge base into the SemanticSearchEngine for RAG queries
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.engines.semantic_search import SemanticSearchEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_knowledge_base():
    """Load all knowledge base files into the SemanticSearchEngine"""
    
    # Initialize the search engine
    logger.info("🔍 Initializing SemanticSearchEngine...")
    engine = SemanticSearchEngine(
        model_name="sentence-transformers/all-MiniLM-L6-v2",  # Use a smaller, faster model
        cache_dir="cache/embeddings",
        use_reranker=True,
        enable_parallel=True
    )
    
    if not engine.initialize():
        logger.error("❌ Failed to initialize SemanticSearchEngine")
        return False
    
    # Load all knowledge base files
    knowledge_base_dir = Path("knowledge_base")
    if not knowledge_base_dir.exists():
        logger.error(f"❌ Knowledge base directory not found: {knowledge_base_dir}")
        return False
    
    json_files = list(knowledge_base_dir.glob("*.json"))
    logger.info(f"📚 Found {len(json_files)} JSON files in knowledge base")
    
    loaded_count = 0
    for json_file in json_files:
        try:
            logger.info(f"📄 Loading {json_file.name}...")
            engine.load_knowledge_base(str(json_file))
            loaded_count += 1
        except Exception as e:
            logger.warning(f"⚠️ Failed to load {json_file.name}: {e}")
    
    # Save the cache
    engine._save_cache()
    
    # Get stats
    stats = engine.get_stats()
    logger.info(f"✅ Knowledge base loaded successfully!")
    logger.info(f"   📊 Total documents: {stats['num_documents']}")
    logger.info(f"   🔢 Embedding dimension: {stats['embedding_dimension']}")
    logger.info(f"   📁 Files loaded: {loaded_count}/{len(json_files)}")
    
    # Test search
    logger.info("🧪 Testing search...")
    results = engine.search("machine learning", top_k=3)
    logger.info(f"🔍 Search test: Found {len(results)} results")
    for i, result in enumerate(results[:2]):
        logger.info(f"   {i+1}. {result['document'][:100]}... (score: {result.get('similarity', 0):.3f})")
    
    return True

if __name__ == "__main__":
    success = load_knowledge_base()
    if success:
        logger.info("🎉 Knowledge base successfully loaded into RAG system!")
    else:
        logger.error("❌ Failed to load knowledge base")
        sys.exit(1)
