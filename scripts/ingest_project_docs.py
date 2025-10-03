#!/usr/bin/env python3
"""
Project Documentation RAG Ingestion Script
Ingests critical project documentation into the RAG system for better context and direction.
"""

import asyncio
import json
import logging
import os
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add src to path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

try:
    from core.retrieval.rag_service import create_rag_service
    RAG_AVAILABLE = True
    print("✅ RAG service imported successfully")
except ImportError as e:
    RAG_AVAILABLE = False
    print(f"⚠️ RAG service not available: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Critical documents to ingest
CRITICAL_DOCUMENTS = {
    # System Architecture & Design
    "system_architecture": [
        "docs/PROJECT_STRUCTURE.md",
        "docs/evolutionary-system/HOW_IT_ALL_WORKS.md",
        "docs/evolutionary-system/INTEGRATION_GUIDE.md",
        "docs/architecture/NEUROFORGE_IMPLEMENTATION_PLAN.md",
        "docs/architecture/OPTIMAL_ARCHITECTURE_BLUEPRINT.md",
    ],
    
    # Frontend & UI
    "frontend_docs": [
        "docs/frontend/FRONTEND_COMPLETE.md",
        "docs/frontend/FRONTEND_BEST_PRACTICES_AND_RECOMMENDATIONS.md",
        "frontend/README.md",
    ],
    
    # Testing & Quality
    "testing_docs": [
        "docs/testing/FUNCTIONAL_TEST_REPORT.md",
        "docs/testing/FUNCTIONAL_TEST_RESULTS.md",
        "docs/testing/EXPERIMENTAL_TESTING_RESULTS.md",
        "docs/archive/COMPREHENSIVE_SYSTEM_AUDIT_REPORT.md",
    ],
    
    # Deployment & Operations
    "deployment_docs": [
        "docs/deployment/PRODUCTION_DEPLOYMENT_README.md",
        "docs/deployment/DOCKER_ARCHITECTURE_COMPLETE.md",
        "docs/deployment/LOCAL_DEVELOPMENT_README.md",
        "docker-compose.yml",
        "Dockerfile",
    ],
    
    # API & Integration
    "api_docs": [
        "docs/evolutionary-system/PRODUCTION_RAG_INTEGRATION.md",
        "docs/evolutionary-system/RAG_STACK_COMPLETE.md",
        "docs/INTEGRATION_GUIDE.md",
        "src/api/consolidated_api_architecture.py",
    ],
    
    # Configuration & Setup
    "config_docs": [
        "README.md",
        "requirements.txt",
        "pytest.ini",
        "env.example",
        "docs/START_SYSTEM.md",
    ],
    
    # Performance & Optimization
    "performance_docs": [
        "PERFORMANCE_OPTIMIZATION_PHASE1_COMPLETE.md",
        "SYSTEM_BASELINE_ANALYSIS.md",
        "docs/archive/COMPREHENSIVE_SYSTEM_EVALUATION_AND_IMPROVEMENT_PLAN.md",
    ],
    
    # Voice & Audio System
    "voice_docs": [
        "VOICE_SYSTEM_COMPLETE.md",
        "VOICE_SYSTEM_TEST_RESULTS.md",
        "docs/SONIA_VOICE_INTEGRATION.md",
    ],
    
    # MCP & Tools
    "mcp_docs": [
        "MCP_AGENT_GUIDE.md",
        "RAG_MCP_INTEGRATION_COMPLETE.md",
        "docs/archive/MCP_TRANSCRIPT_INTEGRATION_GUIDE.md",
    ]
}

def read_file_content(file_path: str) -> Optional[str]:
    """Read file content with error handling."""
    try:
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return None
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if len(content.strip()) == 0:
            logger.warning(f"Empty file: {file_path}")
            return None
            
        return content
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return None

def create_document_metadata(file_path: str, category: str) -> Dict[str, Any]:
    """Create metadata for a document."""
    path = Path(file_path)
    
    return {
        "id": str(uuid.uuid4()),
        "title": path.stem.replace("_", " ").title(),
        "file_path": file_path,
        "category": category,
        "file_type": path.suffix[1:] if path.suffix else "unknown",
        "ingested_at": datetime.now().isoformat(),
        "source_type": "project_documentation",
        "domain": "ai_platform",
        "importance": "high" if category in ["system_architecture", "api_docs", "config_docs"] else "medium"
    }

def chunk_content(content: str, max_chunk_size: int = 1000) -> List[str]:
    """Split content into chunks for better RAG retrieval."""
    if len(content) <= max_chunk_size:
        return [content]
    
    chunks = []
    lines = content.split('\n')
    current_chunk = ""
    
    for line in lines:
        if len(current_chunk) + len(line) + 1 > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = line
        else:
            current_chunk += "\n" + line if current_chunk else line
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

async def ingest_documents_to_rag(rag_service, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Ingest documents into RAG system."""
    results = {
        "total_documents": len(documents),
        "successful": 0,
        "failed": 0,
        "errors": [],
        "categories": {}
    }
    
    # Prepare documents for batch upsert
    items_to_upsert = []
    
    for doc in documents:
        try:
            # Create document entry
            doc_id = doc["metadata"]["id"]
            content = doc["content"]
            metadata = doc["metadata"]
            
            logger.info(f"Preparing: {metadata['title']} ({metadata['category']})")
            
            # Generate embedding for the content
            embedding = await rag_service._embed_query(content)
            
            # Prepare document for Weaviate upsert
            item = {
                "id": doc_id,
                "vector": embedding,
                "properties": {
                    "title": metadata["title"],
                    "content": content,
                    "file_path": metadata["file_path"],
                    "category": metadata["category"],
                    "file_type": metadata["file_type"],
                    "ingested_at": metadata["ingested_at"],
                    "source_type": metadata["source_type"],
                    "domain": metadata["domain"],
                    "importance": metadata["importance"],
                    "chunk_index": metadata.get("chunk_index", 0),
                    "total_chunks": metadata.get("total_chunks", 1)
                }
            }
            
            items_to_upsert.append(item)
            
        except Exception as e:
            logger.error(f"Failed to prepare {doc.get('file_path', 'unknown')}: {e}")
            results["failed"] += 1
            results["errors"].append(f"{doc.get('file_path', 'unknown')}: {str(e)}")
    
    # Batch upsert to Weaviate
    if items_to_upsert:
        try:
            logger.info(f"Batch upserting {len(items_to_upsert)} documents to Weaviate...")
            await rag_service.weaviate.upsert(items_to_upsert)
            
            # Count successful items
            for item in items_to_upsert:
                category = item["properties"]["category"]
                if category not in results["categories"]:
                    results["categories"][category] = 0
                results["categories"][category] += 1
                results["successful"] += 1
                
            logger.info("✅ Batch upsert completed successfully")
            
        except Exception as e:
            logger.error(f"Batch upsert failed: {e}")
            results["failed"] += len(items_to_upsert)
            results["errors"].append(f"Batch upsert failed: {str(e)}")
    
    return results

async def main():
    """Main ingestion process."""
    logger.info("🚀 Starting Project Documentation RAG Ingestion")
    
    # Initialize RAG service
    if not RAG_AVAILABLE:
        logger.error("❌ RAG service not available. Cannot proceed.")
        return
    
    try:
        rag_service = create_rag_service(env="development")
        logger.info("✅ RAG service initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG service: {e}")
        return
    
    # Collect all documents
    all_documents = []
    
    for category, file_paths in CRITICAL_DOCUMENTS.items():
        logger.info(f"📁 Processing category: {category}")
        
        for file_path in file_paths:
            content = read_file_content(file_path)
            if content:
                metadata = create_document_metadata(file_path, category)
                
                # Split into chunks if needed
                chunks = chunk_content(content)
                
                for i, chunk in enumerate(chunks):
                    chunk_metadata = metadata.copy()
                    chunk_metadata["chunk_index"] = i
                    chunk_metadata["total_chunks"] = len(chunks)
                    
                    all_documents.append({
                        "content": chunk,
                        "metadata": chunk_metadata
                    })
    
    logger.info(f"📊 Collected {len(all_documents)} document chunks")
    
    # Ingest into RAG system
    results = await ingest_documents_to_rag(rag_service, all_documents)
    
    # Print summary
    print("\n" + "="*60)
    print("📋 INGESTION SUMMARY")
    print("="*60)
    print(f"Total documents: {results['total_documents']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    
    if results['categories']:
        print("\n📁 By Category:")
        for category, count in results['categories'].items():
            print(f"  {category}: {count} documents")
    
    if results['errors']:
        print("\n❌ Errors:")
        for error in results['errors']:
            print(f"  {error}")
    
    # Save results
    results_file = Path("project_docs_ingestion_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"📄 Results saved to: {results_file}")
    logger.info("✅ Project documentation ingestion complete!")

if __name__ == "__main__":
    asyncio.run(main())
