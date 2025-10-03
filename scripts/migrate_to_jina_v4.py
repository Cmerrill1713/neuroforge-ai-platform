#!/usr/bin/env python3
"""
Migration Script: LFM2 → Jina v4
Migrates all documents from KnowledgeDocumentLFM2 to KnowledgeDocumentJinaV4
with Jina v4 multi-vector embeddings (5x128=640 dimensions)
"""

import logging
import asyncio
import sys
import os
from typing import List, Dict, Any
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.retrieval.jina_v4_embedder import JinaV4Embedder
import weaviate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JinaV4MigrationService:
    """Migrates documents from LFM2 to Jina v4"""
    
    def __init__(self):
        self.source_class = "KnowledgeDocumentLFM2"
        self.target_class = "KnowledgeDocumentJinaV4"
        
        # Initialize Weaviate client
        self.client = weaviate.connect_to_custom(
            http_host='localhost',
            http_port=8090,
            http_secure=False,
            grpc_host='localhost',
            grpc_port=50051,
            grpc_secure=False
        )
        
        # Initialize Jina v4 embedder
        logger.info("Loading Jina v4 embedder...")
        self.jina_embedder = JinaV4Embedder('jinaai/jina-embeddings-v4')
        logger.info("✅ Jina v4 embedder loaded")
    
    def get_document_count(self) -> int:
        """Get total number of documents to migrate"""
        try:
            collection = self.client.collections.get(self.source_class)
            result = collection.query.fetch_objects(limit=1, return_metadata=["count"])
            return result.total
        except Exception as e:
            logger.error(f"Failed to get document count: {e}")
            return 0
    
    def migrate_documents(self, batch_size: int = 5) -> bool:
        """Migrate all documents from LFM2 to Jina v4"""
        try:
            # Get total count
            total_docs = self.get_document_count()
            logger.info(f"📊 Found {total_docs} documents to migrate")
            
            if total_docs == 0:
                logger.warning("No documents found to migrate")
                return True
            
            migrated = 0
            offset = 0
            
            while offset < total_docs:
                logger.info(f"📦 Processing batch {offset//batch_size + 1} (offset: {offset})")
                
                # Fetch batch from source
                source_collection = self.client.collections.get(self.source_class)
                batch_result = source_collection.query.fetch_objects(
                    limit=batch_size,
                    offset=offset
                )
                
                if not batch_result.objects:
                    break
                
                # Process each document
                batch_data = []
                for obj in batch_result.objects:
                    doc_data = {
                        'content': obj.properties.get('content', ''),
                        'title': obj.properties.get('title', ''),
                        'url': obj.properties.get('url', ''),
                        'source_type': obj.properties.get('source_type', ''),
                        'domain': obj.properties.get('domain', ''),
                        'uuid': str(obj.uuid)
                    }
                    
                    # Generate Jina v4 embedding
                    if doc_data['content']:
                        embedding = self.jina_embedder.encode(
                            doc_data['content'],
                            normalize_embeddings=True
                        )
                        doc_data['embedding'] = embedding
                        batch_data.append(doc_data)
                
                # Insert into target collection
                if batch_data:
                    target_collection = self.client.collections.get(self.target_class)
                    target_collection.data.insert_many(objects=batch_data)
                    migrated += len(batch_data)
                    logger.info(f"✅ Migrated {len(batch_data)} documents (total: {migrated}/{total_docs})")
                
                offset += batch_size
                
                # Small delay to avoid overwhelming the system
                time.sleep(0.1)
            
            logger.info(f"🎉 Migration complete! Migrated {migrated} documents")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def verify_migration(self) -> bool:
        """Verify migration was successful"""
        try:
            # Check target collection count
            target_collection = self.client.collections.get(self.target_class)
            target_count = target_collection.query.fetch_objects(
                limit=1,
                return_metadata=["count"]
            )
            
            logger.info(f"📊 Target collection has {target_count.total} documents")
            
            # Test a query
            test_result = target_collection.query.fetch_objects(limit=3)
            
            logger.info(f"🔍 Test query returned {len(test_result.objects)} results")
            
            if test_result.objects:
                logger.info("✅ Migration verification successful!")
                return True
            else:
                logger.warning("⚠️ Test query returned no results")
                return False
                
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return False
    
    def close(self):
        """Close connections"""
        self.client.close()


def main():
    """Main migration process"""
    logger.info("🚀 Starting LFM2 → Jina v4 Migration")
    logger.info("=" * 50)
    
    migration_service = JinaV4MigrationService()
    
    try:
        # Run migration
        start_time = time.time()
        success = migration_service.migrate_documents(batch_size=3)
        migration_time = time.time() - start_time
        
        if success:
            logger.info(f"⏱️ Migration completed in {migration_time:.2f} seconds")
            
            # Verify migration
            logger.info("🔍 Verifying migration...")
            verification_success = migration_service.verify_migration()
            
            if verification_success:
                logger.info("🎉 Migration and verification successful!")
                logger.info("✅ Your RAG system is now using Jina v4!")
            else:
                logger.warning("⚠️ Migration completed but verification failed")
        else:
            logger.error("❌ Migration failed")
            return False
    
    finally:
        migration_service.close()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
