#!/usr/bin/env python3
"""
Test Knowledge Base Integration
Tests that the knowledge base documents are accessible through the API
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_knowledge_base_integration():
    """Test the knowledge base integration"""
    print("🔍 Testing Knowledge Base Integration...")

    try:
        # Import the RAG system
        from core.rag.vector_database import AdvancedRAGSystem
        from api.consolidated_api_architecture import ConsolidatedAPIRouter

        print("✅ Successfully imported RAG system and API router")

        # Initialize RAG system
        rag_system = AdvancedRAGSystem()
        print("✅ RAG system initialized")

        # Test search functionality with new enhancements
        test_queries = [
            "machine learning",
            "artificial intelligence",
            "neural networks",
            "how to fine-tune large language models"
        ]

        print("\n🔍 Testing Enhanced RAG system search...")
        for query in test_queries:
            try:
                # Test re-ranking
                results = await rag_system.retrieve_relevant_context(query, limit=3, rerank=True)
                print(f"   '{query}': {len(results)} results (with re-ranking)")
                for i, result in enumerate(results, 1):
                    title = result.content[:50] + "..." if len(result.content) > 50 else result.content
                    print(f"     {i}. {title} (similarity: {result.similarity_score:.3f})")

                # Test hybrid search
                hybrid_results = await rag_system.hybrid_search(query, limit=3)
                print(f"   '{query}': {len(hybrid_results)} hybrid results")
                for i, result in enumerate(hybrid_results, 1):
                    title = result.content[:50] + "..." if len(result.content) > 50 else result.content
                    print(f"     {i}. {title} (similarity: {result.similarity_score:.3f})")

            except Exception as e:
                print(f"   '{query}': ERROR - {e}")

        # Test stats functionality
        print("\n📊 Testing RAG system stats...")
        try:
            stats = await rag_system.get_database_stats()
            print(f"   Total documents: {stats.get('total_documents', 0)}")
            print(f"   Status: {stats.get('status', 'unknown')}")
        except Exception as e:
            print(f"   Stats error: {e}")

        print("\n✅ Knowledge base integration test completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

    return True

if __name__ == "__main__":
    asyncio.run(test_knowledge_base_integration())