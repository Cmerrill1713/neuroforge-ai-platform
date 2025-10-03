#!/usr/bin/env python3
"""
Debug RAG Dimensions
Check what's causing the 2048 vs 1024 dimension mismatch
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.retrieval.rag_service import create_rag_service

async def debug_rag_dimensions():
    """Debug the RAG dimension mismatch"""
    print("🔍 Debugging RAG Dimension Mismatch")
    print("=" * 50)
    
    try:
        # Create RAG service
        rag_service = create_rag_service(env="development")
        print(f"✅ RAG service created")
        print(f"   Embedder model: {rag_service.embedder_model_name}")
        
        # Check what type of embedder is loaded
        if hasattr(rag_service, 'model') and hasattr(rag_service, 'tokenizer'):
            print("   Using LFM2 model (2048 dimensions)")
            embedder_type = "LFM2"
        elif hasattr(rag_service, 'embedder'):
            print("   Using SentenceTransformer model (1024 dimensions)")
            embedder_type = "SentenceTransformer"
        else:
            print("   No embedder loaded")
            embedder_type = "None"
        
        # Generate a test embedding
        print("\n🧪 Testing embedding generation...")
        test_query = "machine learning"
        embedding = await rag_service._embed_query(test_query)
        
        print(f"   Query: '{test_query}'")
        print(f"   Embedding dimensions: {len(embedding)}")
        print(f"   Embedding type: {type(embedding)}")
        print(f"   First 5 values: {embedding[:5]}")
        
        # Now try to query Weaviate
        print("\n🔍 Testing Weaviate query...")
        try:
            response = await rag_service.query(
                query_text=test_query,
                k=3,
                method="vector",  # Use vector search only
                rerank=False
            )
            
            print(f"   ✅ Weaviate query successful")
            print(f"   Results: {response.num_results}")
            print(f"   Latency: {response.latency_ms:.0f}ms")
            
            if response.results:
                first_result = response.results[0]
                print(f"   Top result: {first_result.text[:100]}...")
                print(f"   Score: {first_result.score:.3f}")
            
        except Exception as e:
            print(f"   ❌ Weaviate query failed: {e}")
            
            # Check if it's a dimension mismatch
            if "vector lengths don't match" in str(e):
                print(f"   🚨 Dimension mismatch detected!")
                print(f"   Query embedding: {len(embedding)} dimensions")
                print(f"   Expected: 1024 dimensions (BGE-Large)")
                print(f"   Actual: {len(embedding)} dimensions ({embedder_type})")
                
                if len(embedding) == 2048:
                    print(f"   💡 Solution: Use BGE-Large model instead of LFM2")
                elif len(embedding) == 1024:
                    print(f"   💡 Solution: Check Weaviate collection configuration")
        
        # Close service
        try:
            await rag_service.close()
        except:
            pass
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_rag_dimensions())
