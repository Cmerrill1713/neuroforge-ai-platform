#!/usr/bin/env python3
"""
Document Ingestion Script for Weaviate
Loads markdown files into the RAG system
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
import weaviate
import logging

logging.basicConfig(level=logging.INFO)
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

def read_markdown_file(file_path: Path) -> Dict[str, Any]:
    """Read and parse markdown file"""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Extract title from first heading or filename
        lines = content.split('\n')
        title = file_path.stem.replace('_', ' ').replace('-', ' ').title()
        
        for line in lines[:10]:  # Check first 10 lines for title
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        # Extract keywords from content
        keywords = []
        content_lower = content.lower()
        
        # Common technical terms
        tech_terms = [
            'evolutionary', 'genetic', 'algorithm', 'optimization', 'dspy',
            'rag', 'retrieval', 'weaviate', 'elasticsearch', 'bandit',
            'thompson', 'sampling', 'prompt', 'engineering', 'llm',
            'vector', 'embedding', 'reranking', 'fusion', 'hybrid'
        ]
        
        for term in tech_terms:
            if term in content_lower:
                keywords.append(term)
        
        return {
            "content": content,
            "title": title,
            "url": f"file://{file_path}",
            "source_type": "markdown",
            "domain": "evolutionary-system",
            "keywords": keywords[:10]  # Limit to 10 keywords
        }
    except Exception as e:
        logger.error(f"❌ Failed to read {file_path}: {e}")
        return None

def ingest_documents(client: weaviate.Client, source_dir: Path, batch_size: int = 5):
    """Ingest documents into Weaviate"""
    
    # Get all markdown files
    md_files = list(source_dir.glob("*.md"))
    logger.info(f"📚 Found {len(md_files)} markdown files")
    
    if not md_files:
        logger.warning("⚠️ No markdown files found")
        return
    
    # Process in batches
    total_ingested = 0
    
    for i in range(0, len(md_files), batch_size):
        batch_files = md_files[i:i + batch_size]
        batch_data = []
        
        logger.info(f"📖 Processing batch {i//batch_size + 1}/{(len(md_files) + batch_size - 1)//batch_size}")
        
        for file_path in batch_files:
            logger.info(f"  📄 Reading {file_path.name}")
            doc_data = read_markdown_file(file_path)
            
            if doc_data:
                batch_data.append(doc_data)
        
        # Insert batch into Weaviate
        if batch_data:
            try:
                # Use Weaviate v4 batch API
                with client.batch() as batch:
                    for doc in batch_data:
                        batch.add_data_object(
                            data_object=doc,
                            class_name="KnowledgeDocument"
                        )
                
                total_ingested += len(batch_data)
                logger.info(f"✅ Ingested {len(batch_data)} documents")
                
            except Exception as e:
                logger.error(f"❌ Failed to ingest batch: {e}")
    
    logger.info(f"🎉 Total ingested: {total_ingested} documents")

def main():
    parser = argparse.ArgumentParser(description="Ingest documents into Weaviate")
    parser.add_argument("--source", required=True, help="Source directory with markdown files")
    parser.add_argument("--type", default="markdown", help="Document type")
    parser.add_argument("--batch-size", type=int, default=5, help="Batch size for ingestion")
    
    args = parser.parse_args()
    
    source_dir = Path(args.source)
    if not source_dir.exists():
        logger.error(f"❌ Source directory not found: {source_dir}")
        return
    
    try:
        client = connect_to_weaviate()
        ingest_documents(client, source_dir, args.batch_size)
        
        # Verify ingestion
        result = client.collections.get("KnowledgeDocument").query.fetch_objects(limit=5)
        docs = result.objects
        
        logger.info(f"🔍 Verification: Found {len(docs)} documents in Weaviate")
        for doc in docs:
            logger.info(f"  📄 {doc.get('title', 'Unknown')} ({doc.get('domain', 'Unknown')})")
            
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        raise

if __name__ == "__main__":
    main()
