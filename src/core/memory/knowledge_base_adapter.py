"""
Knowledge Base Adapter for ChromaDB

Provides a compatible interface for the API layer to interact with ChromaDB.
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from .vector_chroma import ChromaVectorStore

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)


class SearchResult:
    """Search result compatible with API expectations."""
    def __init__(self, id: str, content: str, metadata: Dict[str, Any], distance: float = 0.0, search_time: float = 0.0):
        self.id = id
        self.content = content
        self.metadata = metadata
        self.distance = distance
        self.search_time = search_time


class KnowledgeBaseAdapter:
    """Adapter to provide API-compatible interface for ChromaDB."""

    def __init__(self, collection_name: str = "ai_knowledge_base", persist_directory: Optional[str] = None):
        """Initialize the knowledge base adapter."""
        if persist_directory is None:
            # Use the known working path
            persist_directory = "/Users/christianmerrill/Prompt Engineering/data/chroma_db"
            logger.info(f"Using ChromaDB path: {persist_directory}")

        self.vector_store = ChromaVectorStore(collection_name, persist_directory)
        self.embedding_model = None

        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                logger.info("✅ Embedding model loaded for knowledge base adapter")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load embedding model: {e}")

    async def search_similar(self, query: str, limit: int = 5, threshold: float = 0.7, use_cache: bool = True) -> List[SearchResult]:
        """Search for similar documents in the knowledge base."""
        try:
            if not self.embedding_model:
                logger.warning("⚠️ No embedding model available for search")
                return []

            # Generate embedding for query
            query_embedding = self.embedding_model.encode(query).tolist()

            # Search ChromaDB
            results = await self.vector_store.search_similar(query_embedding, limit=limit)

            # Convert to SearchResult objects
            search_results = []
            for result in results:
                search_results.append(SearchResult(
                    id=result['id'],
                    content=result['content'],
                    metadata=result['metadata'],
                    distance=result.get('score', 0.0),
                    search_time=0.0  # Not tracking search time for now
                ))

            return search_results

        except Exception as e:
            logger.error(f"❌ Knowledge base search failed: {e}")
            return []

    async def get_database_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        try:
            stats = await self.vector_store.get_collection_stats()
            return {
                'total_documents': stats.get('total_documents', 0),
                'collection_name': stats.get('collection_name', 'unknown'),
                'vector_dimension': stats.get('vector_dimension'),
                'status': 'operational' if stats.get('total_documents', 0) > 0 else 'empty'
            }
        except Exception as e:
            logger.error(f"❌ Failed to get database stats: {e}")
            return {
                'total_documents': 0,
                'collection_name': 'unknown',
                'vector_dimension': None,
                'status': 'error',
                'error': str(e)
            }
