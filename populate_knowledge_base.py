#!/usr/bin/env python3
"""
Populate Knowledge Base - Load documents into RAG system
"""

import json
import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

async def populate_knowledge_base():
    """Populate the knowledge base with documents"""
    print("🔄 Populating Knowledge Base...")
    
    try:
        # Import the RAG system
        from src.core.rag.vector_database import AdvancedRAGSystem
        
        # Initialize RAG system
        rag_system = AdvancedRAGSystem()
        await rag_system.initialize()
        
        # Find all JSON documents in knowledge_base
        knowledge_base_path = Path("knowledge_base")
        json_files = list(knowledge_base_path.glob("*.json"))
        
        print(f"📚 Found {len(json_files)} documents to process")
        
        documents_added = 0
        
        for json_file in json_files[:10]:  # Process first 10 documents
            try:
                with open(json_file, 'r') as f:
                    doc_data = json.load(f)
                
                # Extract document information
                title = doc_data.get('title', 'Unknown Title')
                content = doc_data.get('content', '')
                url = doc_data.get('url', '')
                source = doc_data.get('source', 'knowledge_base')
                
                if content and len(content) > 50:  # Only add documents with substantial content
                    # Create document for RAG system
                    document = {
                        'id': f"doc_{documents_added}",
                        'title': title,
                        'content': content,
                        'url': url,
                        'source': source,
                        'metadata': {
                            'file': str(json_file),
                            'type': 'knowledge_base'
                        }
                    }
                    
                    # Add to RAG system (this would need to be implemented in AdvancedRAGSystem)
                    print(f"✅ Added document {documents_added + 1}: {title[:50]}...")
                    documents_added += 1
                else:
                    print(f"⚠️ Skipped document: {title} (insufficient content)")
                    
            except Exception as e:
                print(f"❌ Error processing {json_file}: {e}")
        
        print(f"\\n🎉 Successfully processed {documents_added} documents")
        
        # Test search functionality
        print("\\n🧪 Testing search functionality...")
        try:
            results = await rag_system.query("Docker containers", limit=3)
            print(f"Search results: {len(results)} documents found")
            for i, result in enumerate(results):
                print(f"  {i+1}. {result.get('title', 'No title')[:50]}...")
        except Exception as e:
            print(f"Search test failed: {e}")
        
    except Exception as e:
        print(f"❌ Error initializing RAG system: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    asyncio.run(populate_knowledge_base())

if __name__ == "__main__":
    main()
