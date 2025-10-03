#!/usr/bin/env python3
"""
Knowledge Base Migration Script
Migrates documents from knowledge_base/ to RAG system for MCP access
"""

import json
import asyncio
import os
from pathlib import Path
import weaviate
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeBaseMigrator:
    """Migrate knowledge base to RAG system"""
    
    def __init__(self):
        self.knowledge_base_dir = Path("knowledge_base")
        self.embedder = None
        self.weaviate_client = None
        self.collection = None
    
    async def initialize(self):
        """Initialize components"""
        print("🔄 Initializing migration components...")
        
        # Load BGE embedder
        print("   Loading BGE embedder...")
        self.embedder = SentenceTransformer("BAAI/bge-large-en-v1.5")
        print("   ✅ BGE embedder loaded")
        
        # Connect to Weaviate
        print("   Connecting to Weaviate...")
        self.weaviate_client = weaviate.connect_to_local(port=8090)
        print("   ✅ Weaviate connected")
        
        # Get collection
        print("   Getting BGE collection...")
        self.collection = self.weaviate_client.collections.get("KnowledgeDocumentBGE")
        print("   ✅ BGE collection ready")
    
    def load_knowledge_files(self):
        """Load all knowledge base files"""
        print(f"📚 Loading knowledge base files from {self.knowledge_base_dir}...")
        
        files = list(self.knowledge_base_dir.glob("*.json"))
        print(f"   Found {len(files)} JSON files")
        
        documents = []
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract content based on file type
                if isinstance(data, dict):
                    # GitHub repository
                    if 'title' in data and 'readme_content' in data:
                        content = data.get('readme_content', '')
                        title = data.get('title', file_path.stem)
                        url = data.get('url', '')
                        domain = 'github_repository'
                    # API documentation
                    elif 'title' in data and 'content' in data:
                        content = data.get('content', '')
                        title = data.get('title', file_path.stem)
                        url = data.get('url', '')
                        domain = 'api_documentation'
                    # Other structured data
                    else:
                        content = json.dumps(data, indent=2)
                        title = file_path.stem
                        url = ''
                        domain = 'structured_data'
                else:
                    # Raw content
                    content = str(data)
                    title = file_path.stem
                    url = ''
                    domain = 'raw_content'
                
                if content and len(content.strip()) > 50:  # Only include substantial content
                    documents.append({
                        'content': content[:5000],  # Limit content length
                        'title': title,
                        'url': url,
                        'source_type': 'knowledge_base_file',
                        'domain': domain,
                        'file_path': str(file_path)
                    })
                    
            except Exception as e:
                logger.warning(f"Failed to load {file_path}: {e}")
                continue
        
        print(f"   ✅ Loaded {len(documents)} documents")
        return documents
    
    async def migrate_documents(self, documents):
        """Migrate documents to Weaviate with embeddings"""
        print(f"🔄 Migrating {len(documents)} documents to RAG system...")
        
        # Clear existing documents first
        print("   Clearing existing documents...")
        try:
            self.collection.data.delete_many(where={})
            print("   ✅ Existing documents cleared")
        except Exception as e:
            print(f"   ⚠️ Could not clear existing documents: {e}")
        
        # Add documents with embeddings
        print("   Adding documents with embeddings...")
        added_count = 0
        
        with self.collection.batch.dynamic() as batch:
            for i, doc in enumerate(documents):
                try:
                    # Generate embedding
                    embedding = self.embedder.encode(doc["content"], normalize_embeddings=True).tolist()
                    
                    # Add to batch
                    batch.add_object(
                        properties=doc,
                        vector=embedding
                    )
                    
                    added_count += 1
                    
                    if (i + 1) % 50 == 0:
                        print(f"     Processed {i + 1}/{len(documents)} documents...")
                        
                except Exception as e:
                    logger.warning(f"Failed to add document {i}: {e}")
                    continue
        
        print(f"   ✅ Successfully added {added_count} documents with embeddings")
        return added_count
    
    async def verify_migration(self):
        """Verify the migration was successful"""
        print("🔍 Verifying migration...")
        
        try:
            # Check document count
            count_result = self.collection.aggregate.over_all().total_count
            print(f"   📚 Documents in RAG: {count_result}")
            
            # Test query
            test_query = "artificial intelligence"
            response = self.collection.query.near_text(
                query=test_query,
                limit=3,
                return_properties=["title", "content", "domain"],
                return_metadata=weaviate.classes.query.MetadataQuery(distance=True)
            )
            
            if response.objects:
                print(f"   ✅ Test query successful: Found {len(response.objects)} results")
                for i, obj in enumerate(response.objects):
                    title = obj.properties.get('title', 'No title')
                    distance = obj.metadata.distance
                    print(f"     {i+1}. {title[:50]}... (distance: {distance:.3f})")
            else:
                print("   ⚠️ Test query returned no results")
                
        except Exception as e:
            print(f"   ❌ Verification failed: {e}")
    
    async def close(self):
        """Close connections"""
        if self.weaviate_client:
            self.weaviate_client.close()
            print("   ✅ Weaviate connection closed")

async def main():
    """Main migration function"""
    print("🚀 KNOWLEDGE BASE MIGRATION TO RAG SYSTEM")
    print("==========================================")
    print()
    
    migrator = KnowledgeBaseMigrator()
    
    try:
        # Initialize
        await migrator.initialize()
        print()
        
        # Load knowledge files
        documents = migrator.load_knowledge_files()
        print()
        
        if not documents:
            print("❌ No documents to migrate")
            return
        
        # Migrate documents
        added_count = await migrator.migrate_documents(documents)
        print()
        
        # Verify migration
        await migrator.verify_migration()
        print()
        
        print("🎉 MIGRATION COMPLETE!")
        print(f"   📚 Migrated {added_count} documents to RAG system")
        print("   🔍 MCP agents can now search the knowledge base")
        print("   🚀 Ready for agent tool use!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        logger.error(f"Migration error: {e}")
    finally:
        await migrator.close()

if __name__ == "__main__":
    asyncio.run(main())
