#!/usr/bin/env python3
"""
Add documents with BGE embeddings to Weaviate
"""
import sys
sys.path.append('src')

import weaviate
import asyncio
from sentence_transformers import SentenceTransformer

async def add_documents_with_embeddings():
    print("🔄 Adding documents with BGE embeddings...")
    
    # Load BGE model
    print("Loading BGE model...")
    model = SentenceTransformer('BAAI/bge-large-en-v1.5')
    print("✅ BGE model loaded")
    
    # Connect to Weaviate
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
    
    try:
        # Get the collection
        collection = client.collections.get("KnowledgeDocumentBGE")
        
        # Clear existing documents first
        print("Clearing existing documents...")
        try:
            collection.data.delete_many(where={})
        except Exception as e:
            print(f"Note: Could not clear existing documents: {e}")
        
        # Add documents with embeddings
        print("Adding documents with embeddings...")
        with collection.batch.dynamic() as batch:
            for i, doc in enumerate(sample_docs):
                # Generate embedding for the content
                embedding = model.encode(doc["content"], normalize_embeddings=True)
                
                batch.add_object(
                    properties=doc,
                    vector=embedding.tolist()
                )
                print(f"✅ Added document {i+1}: {doc['title']} (embedding: {len(embedding)} dims)")
        
        print(f"\n🎉 Successfully added {len(sample_docs)} documents with embeddings!")
        
        # Test query
        print("\n🧪 Testing query...")
        result = collection.query.near_vector(
            near_vector=model.encode("artificial intelligence", normalize_embeddings=True).tolist(),
            limit=3
        )
        
        print(f"   Found {len(result.objects)} results")
        for obj in result.objects:
            print(f"   - {obj.properties['title']} (score: {obj.metadata.distance:.3f})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_documents_with_embeddings())
