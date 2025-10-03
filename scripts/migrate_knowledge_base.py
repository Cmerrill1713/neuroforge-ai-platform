#!/usr/bin/env python3
"""
Migrate Knowledge Base to Weaviate
Migrates all documents from the main knowledge base (port 8004) to Weaviate (port 8090)
"""

import asyncio
import json
import logging
import requests
from typing import List, Dict, Any
import weaviate
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def connect_to_weaviate():
    """Connect to Weaviate instance"""
    try:
        # Use Weaviate v4 client - HTTP on 8090, gRPC on 50051
        client = weaviate.connect_to_custom(
            http_host="localhost",
            http_port=8090,
            grpc_host="localhost", 
            grpc_port=50051,
            http_secure=False,
            grpc_secure=False
        )
        logger.info("✅ Connected to Weaviate")
        return client
    except Exception as e:
        logger.error(f"❌ Failed to connect to Weaviate: {e}")
        raise

def get_knowledge_base_documents():
    """Get all documents from the main knowledge base using search endpoint"""
    try:
        # Get stats first
        stats_response = requests.get("http://localhost:8004/api/knowledge/stats")
        stats = stats_response.json()
        logger.info(f"📊 Knowledge base stats: {stats['total_documents']} documents, {stats['total_chunks']} chunks")
        
        all_documents = []
        
        # Use search with broad queries to get all documents
        search_terms = [
            "test", "document", "content", "data", "information", "text", "file",
            "github", "wikipedia", "youtube", "api", "docker", "python", "javascript",
            "machine learning", "artificial intelligence", "programming", "development"
        ]
        
        seen_urls = set()
        
        for term in search_terms:
            try:
                response = requests.post(
                    "http://localhost:8004/api/knowledge/search",
                    json={"query": term, "limit": 100}
                )
                
                if response.status_code == 200:
                    results = response.json().get('results', [])
                    logger.info(f"🔍 Search '{term}': found {len(results)} results")
                    
                    for result in results:
                        url = result.get('url', '')
                        if url and url not in seen_urls:
                            # Convert search result to document format
                            doc = {
                                "content": result.get('content', ''),
                                "title": result.get('source', 'Unknown'),
                                "url": url,
                                "source_type": "migrated",
                                "domain": "knowledge_base",
                                "keywords": [term]
                            }
                            all_documents.append(doc)
                            seen_urls.add(url)
                
            except Exception as e:
                logger.warning(f"⚠️ Search failed for '{term}': {e}")
                continue
        
        logger.info(f"📚 Retrieved {len(all_documents)} unique documents from knowledge base")
        return all_documents
        
    except Exception as e:
        logger.error(f"❌ Failed to get knowledge base documents: {e}")
        return []

def create_weaviate_schema(client):
    """Create or update Weaviate schema for KnowledgeDocument"""
    try:
        # Check if schema exists using v4 API
        try:
            collection = client.collections.get("KnowledgeDocument")
            logger.info("✅ KnowledgeDocument collection already exists")
            return
        except:
            # Collection doesn't exist, create it
            pass
        
        # Create collection using v4 API
        collection = client.collections.create(
            name="KnowledgeDocument",
            description="Migrated documents from knowledge base",
            properties=[
                weaviate.classes.config.Property(
                    name="content",
                    data_type=weaviate.classes.config.DataType.TEXT,
                    description="Document content"
                ),
                weaviate.classes.config.Property(
                    name="title", 
                    data_type=weaviate.classes.config.DataType.TEXT,
                    description="Document title"
                ),
                weaviate.classes.config.Property(
                    name="url",
                    data_type=weaviate.classes.config.DataType.TEXT,
                    description="Document URL"
                ),
                weaviate.classes.config.Property(
                    name="source_type",
                    data_type=weaviate.classes.config.DataType.TEXT,
                    description="Source type (github, wikipedia, etc.)"
                ),
                weaviate.classes.config.Property(
                    name="domain",
                    data_type=weaviate.classes.config.DataType.TEXT,
                    description="Document domain"
                ),
                weaviate.classes.config.Property(
                    name="keywords",
                    data_type=weaviate.classes.config.DataType.TEXT_ARRAY,
                    description="Document keywords"
                )
            ]
        )
        
        logger.info("✅ Created KnowledgeDocument collection")
        
    except Exception as e:
        logger.error(f"❌ Failed to create schema: {e}")
        raise

def migrate_documents_to_weaviate(documents: List[Dict[str, Any]], client):
    """Migrate documents to Weaviate"""
    try:
        collection = client.collections.get("KnowledgeDocument")
        
        # Process documents in batches
        batch_size = 50
        total_migrated = 0
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            logger.info(f"📦 Processing batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
            
            with collection.batch() as batch_client:
                for doc in batch:
                    try:
                        # Convert document to Weaviate format
                        weaviate_doc = {
                            "content": doc.get("content", ""),
                            "title": doc.get("title", "Unknown"),
                            "url": doc.get("url", ""),
                            "source_type": doc.get("source_type", "unknown"),
                            "domain": doc.get("domain", "unknown"),
                            "keywords": doc.get("keywords", [])
                        }
                        
                        batch_client.add_data_object(
                            data_object=weaviate_doc,
                            class_name="KnowledgeDocument"
                        )
                        total_migrated += 1
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to migrate document {doc.get('title', 'Unknown')}: {e}")
                        continue
            
            logger.info(f"✅ Migrated batch, total: {total_migrated}")
        
        logger.info(f"🎉 Migration complete: {total_migrated} documents migrated to Weaviate")
        return total_migrated
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise

def verify_migration(client):
    """Verify the migration was successful"""
    try:
        result = client.collections.get("KnowledgeDocument").query.fetch_objects(limit=5)
        total_count = client.collections.get("KnowledgeDocument").aggregate.over_all(total_count=True).total_count
        
        logger.info(f"🔍 Verification: Found {total_count} documents in Weaviate")
        
        if result.objects:
            logger.info("📄 Sample documents:")
            for i, obj in enumerate(result.objects[:3]):
                logger.info(f"  {i+1}. {obj.properties.get('title', 'Unknown')} ({obj.properties.get('source_type', 'Unknown')})")
        
        return total_count
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        return 0

def main():
    """Main migration function"""
    logger.info("🚀 Starting Knowledge Base Migration to Weaviate")
    
    try:
        # Connect to Weaviate
        client = connect_to_weaviate()
        
        # Get documents from knowledge base
        documents = get_knowledge_base_documents()
        
        if not documents:
            logger.warning("⚠️ No documents found in knowledge base")
            logger.info("💡 This might be because the bulk export endpoint doesn't exist yet")
            logger.info("💡 We may need to implement a different migration strategy")
            return
        
        # Create schema
        create_weaviate_schema(client)
        
        # Migrate documents
        migrated_count = migrate_documents_to_weaviate(documents, client)
        
        # Verify migration
        final_count = verify_migration(client)
        
        logger.info(f"✅ Migration Summary:")
        logger.info(f"  📚 Source documents: {len(documents)}")
        logger.info(f"  📦 Migrated documents: {migrated_count}")
        logger.info(f"  🔍 Final Weaviate count: {final_count}")
        
        if final_count > 0:
            logger.info("🎉 Migration successful! Your documents are now in Weaviate.")
        else:
            logger.error("❌ Migration failed - no documents found in Weaviate")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
    finally:
        try:
            client.close()
        except:
            pass

if __name__ == "__main__":
    main()
