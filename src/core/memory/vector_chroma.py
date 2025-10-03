"""
ChromaDB Vector Store Implementation
"""

import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)


class ChromaVectorStore:
    """ChromaDB-based vector store for knowledge base."""

    def __init__(self, collection_name: str = "knowledge_base", persist_directory: str = "./data/chroma_db"):
        """Initialize ChromaDB vector store."""
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "AI Agent Knowledge Base"}
        )

        logger.info(f"✅ ChromaDB vector store initialized: {collection_name}")

    async def initialize(self):
        """Initialize the vector store (async compatibility)."""
        # ChromaDB is already initialized in __init__
        pass

    async def add_document(self, document_id: str, content: str, metadata: Dict[str, Any], embedding: List[float]):
        """Add a document with its embedding to the vector store."""
        try:
            self.collection.add(
                ids=[document_id],
                documents=[content],
                metadatas=[metadata],
                embeddings=[embedding]
            )
            logger.debug(f"Added document: {document_id}")
        except Exception as e:
            logger.error(f"Failed to add document {document_id}: {e}")
            raise

    async def search_similar(self, query_embedding: List[float], limit: int = 5, metadata_filter: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for similar documents using vector similarity."""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=metadata_filter
            )

            # Format results
            formatted_results = []
            for i, doc_id in enumerate(results['ids'][0]):
                formatted_results.append({
                    'id': doc_id,
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'score': results['distances'][0][i] if 'distances' in results else 0.0
                })

            return formatted_results

        except Exception as e:
            logger.error(f"Failed to search similar documents: {e}")
            return []

    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID."""
        try:
            result = self.collection.get(ids=[document_id])
            if result['ids']:
                return {
                    'id': result['ids'][0],
                    'content': result['documents'][0],
                    'metadata': result['metadatas'][0]
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get document {document_id}: {e}")
            return None

    async def delete_document(self, document_id: str):
        """Delete a document from the vector store."""
        try:
            self.collection.delete(ids=[document_id])
            logger.debug(f"Deleted document: {document_id}")
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            raise

    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        try:
            count = self.collection.count()
            return {
                'total_documents': count,
                'collection_name': self.collection_name,
                'vector_dimension': None  # ChromaDB doesn't expose this directly
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {'total_documents': 0, 'collection_name': self.collection_name, 'vector_dimension': None}

    def generate_document_id(self) -> str:
        """Generate a unique document ID."""
        return f"doc_{uuid.uuid4().hex[:16]}"
