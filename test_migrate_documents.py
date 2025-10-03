#!/usr/bin/env python3
"""
Quick migration script to populate BGE collection with sample documents
"""
import sys
sys.path.append('src')

import asyncio
import json
from core.retrieval.rag_service import ProductionRAGService

async def migrate_sample_documents():
    print("🔄 Migrating sample documents to BGE collection...")
    
    # Sample documents to test with
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
        },
        {
            "content": "Natural Language Processing (NLP) is a field of artificial intelligence that focuses on the interaction between computers and humans through natural language. It involves developing algorithms and models that can understand, interpret, and generate human language.",
            "title": "Natural Language Processing",
            "url": "https://example.com/nlp",
            "source_type": "educational",
            "domain": "computer-science"
        },
        {
            "content": "Computer Vision is a field of artificial intelligence that trains computers to interpret and understand visual information from the world. It involves developing algorithms that can process, analyze, and make decisions based on visual data from cameras and other sensors.",
            "title": "Computer Vision Basics",
            "url": "https://example.com/computer-vision",
            "source_type": "educational",
            "domain": "computer-science"
        }
    ]
    
    # Initialize RAG service
    rag = ProductionRAGService()
    print(f"✅ RAG service initialized with {rag.embedder_model_name}")
    
    # Add documents to Weaviate using upsert method
    try:
        await rag.weaviate.upsert(sample_docs)
        print(f"✅ Added {len(sample_docs)} documents to BGE collection")
    except Exception as e:
        print(f"❌ Failed to add documents: {e}")
        return
    
    # Test the collection
    print("\n🧪 Testing the populated collection...")
    metrics = await rag.get_metrics()
    print(f"   Documents: {metrics.get('weaviate_docs', 0)}")
    print(f"   Status: {metrics.get('status', 'unknown')}")
    
    # Test a query
    print("\n🔍 Testing query...")
    response = await rag.query("artificial intelligence machine learning", k=3)
    print(f"   Query results: {len(response.results)} documents")
    
    if response.results:
        for i, result in enumerate(response.results):
            print(f"   Result {i+1}: {result.content[:80]}... (score: {result.score:.3f})")
    
    print("\n🎉 Migration and testing complete!")

if __name__ == "__main__":
    asyncio.run(migrate_sample_documents())
