#!/usr/bin/env python3
"""
Migration Script: LFM2 → BGE-Large
Migrates all documents from KnowledgeDocumentLFM2 to KnowledgeDocumentBGE
with BGE-Large embeddings (1024 dimensions)
"""

import logging
import asyncio
import sys
import os
from typing import List, Dict, Any
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.retrieval.weaviate_store import WeaviateStore
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BGEMigrationService:
    """Migrates documents from LFM2 to BGE-Large"""
    
    def __init__(self):
        self.source_class = "KnowledgeDocumentLFM2"
        self.target_class = "KnowledgeDocumentBGE"
        
        # Initialize Weaviate stores
        self.source_store = WeaviateStore(
            class_name=self.source_class,
            http_port=8090
        )
        
        self.target_store = WeaviateStore(
            class_name=self.target_class,
            http_port=8090
        )
        
        # Initialize BGE-Large model
        logger.info("Loading BGE-Large model...")
        self.bge_model = SentenceTransformer('BAAI/bge-large-en-v1.5')
        logger.info("✅ BGE-Large model loaded")
    
    async def get_document_count(self) -> int:
        """Get total number of documents to migrate"""
        try:
            result = await self.source_store.client.collections.get(self.source_class).query.fetch_objects(
                limit=1,
                return_metadata=["count"]
            )
            return result.total
        except Exception as e:
            logger.error(f"Failed to get document count: {e}")
            return 0
    
    async def migrate_documents(self, batch_size: int = 10) -> bool:
        """Migrate all documents from LFM2 to BGE-Large"""
        try:
            # Get total count
            total_docs = await self.get_document_count()
            logger.info(f"📊 Found {total_docs} documents to migrate")
            
            if total_docs == 0:
                logger.warning("No documents found to migrate")
                return True
            
            migrated = 0
            offset = 0
            
            while offset < total_docs:
                logger.info(f"📦 Processing batch {offset//batch_size + 1} (offset: {offset})")
                
                # Fetch batch from source
                batch_result = await self.source_store.client.collections.get(self.source_class).query.fetch_objects(
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
                        'source': obj.properties.get('source', ''),
                        'metadata': obj.properties.get('metadata', {}),
                        'uuid': str(obj.uuid)
                    }
                    
                    # Generate BGE-Large embedding
                    if doc_data['content']:
                        embedding = self.bge_model.encode(doc_data['content'])
                        doc_data['embedding'] = embedding.tolist()
                        batch_data.append(doc_data)
                
                # Insert into target collection
                if batch_data:
                    await self.target_store.client.collections.get(self.target_class).data.insert_many(
                        objects=batch_data
                    )
                    migrated += len(batch_data)
                    logger.info(f"✅ Migrated {len(batch_data)} documents (total: {migrated}/{total_docs})")
                
                offset += batch_size
                
                # Small delay to avoid overwhelming the system
                await asyncio.sleep(0.1)
            
            logger.info(f"🎉 Migration complete! Migrated {migrated} documents")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def verify_migration(self) -> bool:
        """Verify migration was successful"""
        try:
            # Check target collection count
            target_count = await self.target_store.client.collections.get(self.target_class).query.fetch_objects(
                limit=1,
                return_metadata=["count"]
            )
            
            logger.info(f"📊 Target collection has {target_count.total} documents")
            
            # Test a query
            test_result = await self.target_store.query(
                query="machine learning",
                limit=3
            )
            
            logger.info(f"🔍 Test query returned {len(test_result)} results")
            
            if test_result:
                logger.info("✅ Migration verification successful!")
                return True
            else:
                logger.warning("⚠️ Test query returned no results")
                return False
                
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return False


async def main():
    """Main migration process"""
    logger.info("🚀 Starting LFM2 → BGE-Large Migration")
    logger.info("=" * 50)
    
    migration_service = BGEMigrationService()
    
    # Run migration
    start_time = time.time()
    success = await migration_service.migrate_documents(batch_size=20)
    migration_time = time.time() - start_time
    
    if success:
        logger.info(f"⏱️ Migration completed in {migration_time:.2f} seconds")
        
        # Verify migration
        logger.info("🔍 Verifying migration...")
        verification_success = await migration_service.verify_migration()
        
        if verification_success:
            logger.info("🎉 Migration and verification successful!")
            logger.info("✅ Your RAG system is now using BGE-Large!")
        else:
            logger.warning("⚠️ Migration completed but verification failed")
    else:
        logger.error("❌ Migration failed")
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
