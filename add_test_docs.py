#!/usr/bin/env python3
"""
Direct Weaviate document insertion for testing
"""
import weaviate
import asyncio
import json

async def add_test_documents():
    print("🔄 Adding test documents directly to Weaviate...")
    
    # Connect to Weaviate v4
    client = weaviate.connect_to_local(port=8090)
    
    # Sample documents
    sample_docs = [
        {
            "content": "Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines that can perform tasks that typically require human intelligence. These tasks include learning, reasoning, problem-solving, perception, and language understanding.",
            "title": "Introduction to Artificial Intelligence",
            "url": "https://example.com/ai-intro",
            "source_type": "educational",
            "domain": "computer-science"
        },
        {
            "content": "Machine Learning is a subset of artificial intelligence that focuses on algorithms and statistical models that enable computer systems to improve their performance on a specific task through experience, without being explicitly programmed.",
            "title": "Machine Learning Fundamentals",
            "url": "https://example.com/ml-fundamentals",
            "source_type": "educational",
            "domain": "computer-science"
        },
        {
            "content": "Deep Learning is a subset of machine learning that uses artificial neural networks with multiple layers to model and understand complex patterns in data. It has revolutionized fields like computer vision, natural language processing, and speech recognition.",
            "title": "Deep Learning Overview",
            "url": "https://example.com/deep-learning",
            "source_type": "educational",
            "domain": "computer-science"
        }
    ]
    
    try:
        # Get the collection
        collection = client.collections.get("KnowledgeDocumentBGE")
        
        # Add documents
        with collection.batch.dynamic() as batch:
            for i, doc in enumerate(sample_docs):
                batch.add_object(
                    properties=doc
                )
                print(f"✅ Added document {i+1}: {doc['title']}")
        
        print(f"\n🎉 Successfully added {len(sample_docs)} documents!")
        
        # Test query
        print("\n🧪 Testing query...")
        result = collection.query.near_text(
            query="artificial intelligence",
            limit=3
        )
        
        print(f"   Found {len(result.objects)} results")
        for obj in result.objects:
            print(f"   - {obj.properties['title']} (score: {obj.metadata.distance:.3f})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_test_documents())
