#!/usr/bin/env python3
"""
Knowledge Base Ingestion Script

Ingests all documents from the knowledge_base directory into ChromaDB.
Direct ChromaDB integration for reliable knowledge base setup.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.memory.vector_chroma import ChromaVectorStore

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️ sentence-transformers not available, embeddings will be limited")

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class KnowledgeBaseIngester:
    """Ingest knowledge base documents into ChromaDB."""

    def __init__(self):
        self.vector_store = None
        self.embedding_model = None
        self.knowledge_base_dir = Path("knowledge_base")
        self.processed_count = 0
        self.error_count = 0

    async def initialize(self):
        """Initialize ChromaDB and embedding model."""
        try:
            logger.info("Initializing ChromaDB vector store...")
            self.vector_store = ChromaVectorStore(
                collection_name="ai_knowledge_base",
                persist_directory="./data/chroma_db"
            )

            if SENTENCE_TRANSFORMERS_AVAILABLE:
                logger.info("Initializing sentence transformer model...")
                self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                logger.info("✅ Embedding model loaded")
            else:
                logger.warning("⚠️ No embedding model available - documents will be stored without embeddings")

            logger.info("✅ Knowledge base ingestion system initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize system: {e}")
            raise

    def load_json_document(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load a JSON document from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Failed to load {file_path}: {e}")
            return None

    def extract_document_info(self, data: Dict[str, Any], source_type: str) -> Dict[str, Any]:
        """Extract standardized document information from various formats."""
        doc_info = {
            'title': '',
            'content': '',
            'source': '',
            'category': 'unknown',
            'keywords': [],
            'tags': [],
            'document_type': 'knowledge_base'
        }

        # Handle different document formats
        if source_type == 'github':
            doc_info.update({
                'title': data.get('full_name', data.get('name', 'GitHub Repository')),
                'content': data.get('readme_content', data.get('description', '')),
                'source': data.get('html_url', data.get('url', '')),
                'category': 'github',
                'keywords': data.get('topics', []),
                'tags': data.get('language', '').split() if data.get('language') else []
            })

        elif source_type == 'arxiv':
            doc_info.update({
                'title': data.get('title', 'ArXiv Paper'),
                'content': data.get('abstract', data.get('summary', '')),
                'source': data.get('url', ''),
                'category': 'research',
                'keywords': data.get('categories', []),
                'tags': ['paper', 'research', 'arxiv']
            })

        elif source_type == 'youtube':
            doc_info.update({
                'title': data.get('title', 'YouTube Video'),
                'content': data.get('description', ''),
                'source': data.get('url', ''),
                'category': 'video',
                'keywords': data.get('tags', []),
                'tags': ['video', 'youtube']
            })

        elif source_type == 'wikipedia':
            doc_info.update({
                'title': data.get('title', 'Wikipedia Article'),
                'content': data.get('extract', data.get('content', '')),
                'source': data.get('url', ''),
                'category': 'reference',
                'keywords': data.get('categories', []),
                'tags': ['wikipedia', 'reference']
            })

        else:
            # Generic format
            doc_info.update({
                'title': data.get('title', file_path.stem),
                'content': data.get('content', data.get('text', data.get('description', ''))),
                'source': data.get('source', data.get('url', '')),
                'category': data.get('category', 'unknown'),
                'keywords': data.get('keywords', data.get('tags', [])),
                'tags': data.get('tags', data.get('keywords', []))
            })

        # Ensure content is a string
        if isinstance(doc_info['content'], list):
            doc_info['content'] = ' '.join(str(item) for item in doc_info['content'])

        # Ensure keywords and tags are lists of strings
        doc_info['keywords'] = [str(k) for k in doc_info['keywords']] if doc_info['keywords'] else []
        doc_info['tags'] = [str(t) for t in doc_info['tags']] if doc_info['tags'] else []

        return doc_info

    def determine_source_type(self, filename: str) -> str:
        """Determine the source type from filename."""
        if 'github' in filename:
            return 'github'
        elif 'arxiv' in filename:
            return 'arxiv'
        elif 'youtube' in filename:
            return 'youtube'
        elif 'wikipedia' in filename:
            return 'wikipedia'
        else:
            return 'generic'

    async def ingest_document(self, file_path: Path) -> bool:
        """Ingest a single document into ChromaDB."""
        try:
            # Load document
            data = self.load_json_document(file_path)
            if not data:
                self.error_count += 1
                return False

            # Determine source type
            source_type = self.determine_source_type(file_path.name)

            # Extract document info
            doc_info = self.extract_document_info(data, source_type)

            # Skip if no meaningful content
            if not doc_info['content'] or len(doc_info['content'].strip()) < 50:
                logger.warning(f"⚠️ Skipping {file_path.name}: insufficient content")
                return False

            # Generate document ID
            doc_id = self.vector_store.generate_document_id()

            # Prepare metadata
            metadata = {
                'title': doc_info['title'],
                'category': doc_info['category'],
                'source_type': source_type,
                'source': doc_info['source'],
                'keywords': ','.join(doc_info['keywords']),
                'tags': ','.join(doc_info['tags']),
                'ingested_at': datetime.now().isoformat(),
                'file_path': str(file_path)
            }

            # Generate embedding
            embedding = None
            if self.embedding_model:
                try:
                    # Create a combined text for embedding
                    embedding_text = f"{doc_info['title']} {doc_info['content']}"
                    embedding = self.embedding_model.encode(embedding_text).tolist()
                except Exception as e:
                    logger.warning(f"⚠️ Failed to generate embedding for {file_path.name}: {e}")

            # Add to ChromaDB
            await self.vector_store.add_document(
                document_id=doc_id,
                content=doc_info['content'],
                metadata=metadata,
                embedding=embedding
            )

            self.processed_count += 1
            logger.info(f"✅ Ingested: {doc_info['title'][:50]}... ({len(doc_info['content'])} chars)")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to ingest {file_path.name}: {e}")
            self.error_count += 1
            return False

    async def ingest_all_documents(self) -> Dict[str, Any]:
        """Ingest all documents from the knowledge base directory."""
        logger.info(f"📚 Starting knowledge base ingestion from {self.knowledge_base_dir}")

        if not self.knowledge_base_dir.exists():
            raise FileNotFoundError(f"Knowledge base directory not found: {self.knowledge_base_dir}")

        # Get all JSON files
        json_files = list(self.knowledge_base_dir.glob("*.json"))
        logger.info(f"Found {len(json_files)} JSON files to process")

        # Process each file
        processed_files = []
        failed_files = []

        for file_path in json_files:
            success = await self.ingest_document(file_path)
            if success:
                processed_files.append(file_path.name)
            else:
                failed_files.append(file_path.name)

        # Get final statistics
        stats = await self.vector_store.get_collection_stats()

        result = {
            'total_files': len(json_files),
            'processed_files': len(processed_files),
            'failed_files': len(failed_files),
            'database_stats': stats,
            'processed_files_list': processed_files,
            'failed_files_list': failed_files
        }

        logger.info("🎉 Knowledge base ingestion completed!")
        logger.info(f"📊 Processed: {result['processed_files']}/{result['total_files']} files")
        logger.info(f"📈 Database contains: {stats.get('total_documents', 0)} documents")

        return result


async def main():
    """Main ingestion function."""
    ingester = KnowledgeBaseIngester()

    try:
        # Initialize
        await ingester.initialize()

        # Ingest all documents
        result = await ingester.ingest_all_documents()

        # Print final summary
        print("\n" + "="*60)
        print("📊 KNOWLEDGE BASE INGESTION SUMMARY")
        print("="*60)
        print(f"Total files processed: {result['total_files']}")
        print(f"Successfully ingested: {result['processed_files']}")
        print(f"Failed to ingest: {result['failed_files']}")
        print(f"Database documents: {result['database_stats'].get('total_documents', 0)}")
        print("="*60)

    except Exception as e:
        logger.error(f"❌ Knowledge base ingestion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
