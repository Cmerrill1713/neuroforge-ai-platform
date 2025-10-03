#!/usr/bin/env python3
"""
Migrate knowledge base from local JSON files to Weaviate
Uses the Weaviate v4 client API
"""

import json
import logging
from pathlib import Path
import weaviate
import weaviate.classes as wvc
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_knowledge_to_weaviate():
    """Migrate all knowledge base documents to Weaviate"""
    
    # Connect to Weaviate
    logger.info("Connecting to Weaviate...")
    client = weaviate.connect_to_local(host="localhost", port=8090)
    
    if not client.is_ready():
        logger.error("❌ Weaviate not ready")
        return
    
    logger.info("✅ Connected to Weaviate")
    
    # Initialize embedding model
    logger.info("Loading embedding model...")
    model = SentenceTransformer("Snowflake/snowflake-arctic-embed-m")
    logger.info("✅ Embedding model loaded")
    
    # Ensure schema exists
    try:
        # Check if KnowledgeDocument collection exists
        collections = client.collections.list_all()
        if "KnowledgeDocument" not in [c.name for c in collections]:
            logger.info("Creating KnowledgeDocument collection...")
            client.collections.create(
                name="KnowledgeDocument",
                description="Knowledge base documents with vector embeddings",
                vectorizer_config=wvc.config.Configure.Vectorizer.none(),  # We provide our own vectors
                properties=[
                    wvc.config.Property(name="content", data_type=wvc.config.DataType.TEXT),
                    wvc.config.Property(name="title", data_type=wvc.config.DataType.TEXT),
                    wvc.config.Property(name="url", data_type=wvc.config.DataType.TEXT),
                    wvc.config.Property(name="source_type", data_type=wvc.config.DataType.TEXT),
                    wvc.config.Property(name="domain", data_type=wvc.config.DataType.TEXT),
                    wvc.config.Property(name="keywords", data_type=wvc.config.DataType.TEXT_ARRAY),
                ]
            )
            logger.info("✅ Collection created")
    except Exception as e:
        logger.warning(f"Schema check/creation: {e}")
    
    # Get collection
    collection = client.collections.get("KnowledgeDocument")
    
    # Load and migrate knowledge base files
    knowledge_base_path = Path("knowledge_base")
    files = list(knowledge_base_path.glob("*.json"))
    total_files = len(files)
    total_documents = 0
    
    logger.info(f"Found {total_files} knowledge base files")
    
    for i, file_path in enumerate(files, 1):
        try:
            logger.info(f"[{i}/{total_files}] Processing {file_path.name}...")
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Handle multiple formats:
            # 1. Flat list: [{"content": "...", ...}, ...]
            # 2. Nested documents: {"documents": [...]}
            # 3. Single object: {"id": "...", "content": "...", ...}
            if isinstance(data, list):
                documents = data
            elif isinstance(data, dict):
                if "documents" in data:
                    documents = data["documents"]
                elif "content" in data or "text" in data:
                    # Single document object - wrap in list
                    documents = [data]
                else:
                    logger.warning(f"Unexpected format in {file_path.name}: {list(data.keys())}")
                    continue
            else:
                logger.warning(f"Unexpected data type in {file_path.name}: {type(data)}")
                continue
            
            # Batch insert documents
            batch_size = 50
            for batch_start in range(0, len(documents), batch_size):
                batch = documents[batch_start:batch_start + batch_size]
                
                # Prepare batch data
                objects_to_insert = []
                for doc in batch:
                    # Extract content from various fields
                    content = (
                        doc.get("content") or 
                        doc.get("text") or 
                        doc.get("transcript") or 
                        doc.get("readme_content") or 
                        doc.get("description") or
                        ""
                    )
                    if not content or len(content.strip()) == 0:
                        continue
                    
                    # Generate embedding
                    vector = model.encode(content).tolist()
                    
                    # Prepare object
                    obj = wvc.data.DataObject(
                        properties={
                            "content": content,
                            "title": doc.get("title", "Untitled"),
                            "url": doc.get("url", doc.get("source", "")),
                            "source_type": doc.get("source_type", "unknown"),
                            "domain": doc.get("domain", "general"),
                            "keywords": doc.get("keywords", [])
                        },
                        vector=vector
                    )
                    objects_to_insert.append(obj)
                
                # Insert batch
                if objects_to_insert:
                    collection.data.insert_many(objects_to_insert)
                    total_documents += len(objects_to_insert)
            
            logger.info(f"  ✅ Migrated {len(documents)} documents from {file_path.name}")
            
        except Exception as e:
            logger.error(f"  ❌ Error processing {file_path.name}: {e}")
            continue
    
    # Get final count
    aggregate = collection.aggregate.over_all(total_count=True)
    final_count = aggregate.total_count
    
    logger.info(f"\n{'='*60}")
    logger.info(f"✅ Migration Complete!")
    logger.info(f"  Files processed: {total_files}")
    logger.info(f"  Documents migrated: {total_documents}")
    logger.info(f"  Total in Weaviate: {final_count}")
    logger.info(f"{'='*60}")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    migrate_knowledge_to_weaviate()

