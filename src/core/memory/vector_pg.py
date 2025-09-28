"""
PostgreSQL Vector Store Implementation for Agentic LLM Core v0.1

This module provides a PostgreSQL-based vector store with support for:
- Vector indexing and similarity search
- Document storage and retrieval
- Metadata filtering and querying
- Batch operations and performance optimization
- Apple Silicon optimization with pgvector

Created: 2024-09-24
Status: Draft
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Tuple, AsyncGenerator
from uuid import UUID

import asyncpg
import numpy as np
from pydantic import BaseModel, Field, field_validator

from ..models.contracts import ProcessedInput, UnifiedContext


# ============================================================================
# Vector Store Interface
# ============================================================================

class VectorStore(ABC):
    """Abstract base class for vector stores."""
    
    @abstractmethod
    async def index(self, documents: List[Document], vectors: List[List[float]]) -> List[str]:
        """Index documents with their vectors."""
        pass
    
    @abstractmethod
    async def query(self, vector: List[float], limit: int = 10, filter_metadata: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """Query similar vectors."""
        pass
    
    @abstractmethod
    async def get(self, document_ids: List[str]) -> List[Document]:
        """Get documents by IDs."""
        pass
    
    @abstractmethod
    async def delete(self, document_ids: List[str]) -> bool:
        """Delete documents by IDs."""
        pass
    
    @abstractmethod
    async def update(self, document_id: str, document: Document, vector: Optional[List[float]] = None) -> bool:
        """Update a document and optionally its vector."""
        pass
    
    @abstractmethod
    async def search_by_metadata(self, metadata: Dict[str, Any], limit: int = 10) -> List[Document]:
        """Search documents by metadata."""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get store statistics."""
        pass


# ============================================================================
# Data Models
# ============================================================================

class DocumentType(str, Enum):
    """Types of documents."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    PDF = "pdf"
    CODE = "code"
    STRUCTURED = "structured"


class DocumentStatus(str, Enum):
    """Document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"
    DELETED = "deleted"


class Document(BaseModel):
    """Document model for vector store."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique document ID")
    content: str = Field(..., description="Document content")
    title: Optional[str] = Field(None, description="Document title")
    doc_type: DocumentType = Field(default=DocumentType.TEXT, description="Document type")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    status: DocumentStatus = Field(default=DocumentStatus.PENDING, description="Processing status")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last update timestamp")
    source: Optional[str] = Field(None, description="Source of the document")
    chunk_index: Optional[int] = Field(None, description="Chunk index for chunked documents")
    parent_id: Optional[str] = Field(None, description="Parent document ID for chunks")
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Document content cannot be empty")
        return v.strip()
    
    @field_validator('metadata')
    @classmethod
    def validate_metadata(cls, v):
        # Ensure metadata is JSON serializable
        try:
            json.dumps(v)
        except (TypeError, ValueError):
            raise ValueError("Metadata must be JSON serializable")
        return v


class SearchResult(BaseModel):
    """Search result model."""
    document: Document = Field(..., description="Matched document")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    distance: float = Field(..., ge=0.0, description="Vector distance")
    rank: int = Field(..., ge=1, description="Result rank")


class VectorIndex(BaseModel):
    """Vector index information."""
    id: str = Field(..., description="Index ID")
    name: str = Field(..., description="Index name")
    dimension: int = Field(..., ge=1, description="Vector dimension")
    document_count: int = Field(default=0, ge=0, description="Number of documents in index")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Index metadata")


# ============================================================================
# PostgreSQL Configuration
# ============================================================================

class PostgreSQLConfig(BaseModel):
    """PostgreSQL configuration."""
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, ge=1, le=65535, description="Database port")
    database: str = Field(default="agi_agents", description="Database name")
    username: str = Field(default="agi_user", description="Database username")
    password: str = Field(default="default_db_password", description="Database password")
    
    # Connection pool settings
    min_connections: int = Field(default=5, ge=1, description="Minimum connections")
    max_connections: int = Field(default=20, ge=1, description="Maximum connections")
    connection_timeout: float = Field(default=30.0, ge=1.0, description="Connection timeout in seconds")
    
    # Vector settings
    vector_dimension: int = Field(default=1536, ge=1, description="Vector dimension")
    index_name: str = Field(default="documents_vector_idx", description="Vector index name")
    
    # Performance settings
    batch_size: int = Field(default=1000, ge=1, le=10000, description="Batch size for operations")
    enable_parallel_indexing: bool = Field(default=True, description="Enable parallel indexing")
    
    # Apple Silicon optimization
    use_native_compilation: bool = Field(default=True, description="Use native compilation on Apple Silicon")
    optimize_for_m1: bool = Field(default=True, description="Optimize for M1/M2/M3 chips")


# ============================================================================
# PostgreSQL Vector Store Implementation
# ============================================================================

class PostgreSQLVectorStore(VectorStore):
    """PostgreSQL-based vector store using pgvector extension."""
    
    def __init__(self, config: PostgreSQLConfig):
        self.config = config
        self.pool: Optional[asyncpg.Pool] = None
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.total_documents = 0
        self.total_queries = 0
        self.total_indexes = 0
        self.cache_hits = 0
        self.cache_misses = 0
    
    async def initialize(self) -> None:
        """Initialize the vector store."""
        try:
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                min_size=self.config.min_connections,
                max_size=self.config.max_connections,
                command_timeout=self.config.connection_timeout
            )
            
            # Initialize database schema
            await self._create_schema()
            
            self.logger.info(f"PostgreSQL vector store initialized on {self.config.host}:{self.config.port}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize PostgreSQL vector store: {e}")
            raise
    
    async def _create_schema(self) -> None:
        """Create database schema and indexes."""
        async with self.pool.acquire() as conn:
            # Enable pgvector extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            # Create documents table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    content TEXT NOT NULL,
                    title TEXT,
                    doc_type VARCHAR(50) NOT NULL DEFAULT 'text',
                    metadata JSONB DEFAULT '{}',
                    status VARCHAR(50) NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    source TEXT,
                    chunk_index INTEGER,
                    parent_id UUID,
                    embedding VECTOR(%d)
                )
            """ % self.config.vector_dimension)
            
            # Create indexes
            await conn.execute(f"""
                CREATE INDEX IF NOT EXISTS {self.config.index_name}
                ON documents USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS documents_status_idx ON documents (status)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS documents_type_idx ON documents (doc_type)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS documents_created_at_idx ON documents (created_at)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS documents_metadata_idx ON documents USING GIN (metadata)
            """)
            
            # Create updated_at trigger
            await conn.execute("""
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = NOW();
                    RETURN NEW;
                END;
                $$ language 'plpgsql';
            """)
            
            await conn.execute("""
                DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;
                CREATE TRIGGER update_documents_updated_at
                    BEFORE UPDATE ON documents
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column();
            """)
    
    async def index(self, documents: List[Document], vectors: List[List[float]]) -> List[str]:
        """Index documents with their vectors."""
        if len(documents) != len(vectors):
            raise ValueError("Number of documents must match number of vectors")
        
        if not documents:
            return []
        
        # Validate vector dimensions
        for i, vector in enumerate(vectors):
            if len(vector) != self.config.vector_dimension:
                raise ValueError(f"Vector {i} has dimension {len(vector)}, expected {self.config.vector_dimension}")
        
        indexed_ids = []
        
        try:
            if self.config.enable_parallel_indexing and len(documents) > self.config.batch_size:
                # Process in parallel batches
                indexed_ids = await self._index_parallel(documents, vectors)
            else:
                # Process in single batch
                indexed_ids = await self._index_batch(documents, vectors)
            
            self.total_indexes += len(indexed_ids)
            self.logger.info(f"Indexed {len(indexed_ids)} documents")
            
        except Exception as e:
            self.logger.error(f"Failed to index documents: {e}")
            raise
        
        return indexed_ids
    
    async def _index_batch(self, documents: List[Document], vectors: List[List[float]]) -> List[str]:
        """Index documents in a single batch."""
        async with self.pool.acquire() as conn:
            indexed_ids = []
            
            for doc, vector in zip(documents, vectors):
                # Update document status
                doc.status = DocumentStatus.PROCESSING
                doc.updated_at = datetime.now(timezone.utc)
                
                # Insert document with vector
                result = await conn.fetchrow("""
                    INSERT INTO documents (
                        id, content, title, doc_type, metadata, status,
                        created_at, updated_at, source, chunk_index, parent_id, embedding
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                    RETURNING id
                """, 
                    doc.id, doc.content, doc.title, doc.doc_type.value,
                    json.dumps(doc.metadata), doc.status.value,
                    doc.created_at, doc.updated_at, doc.source,
                    doc.chunk_index, doc.parent_id, vector
                )
                
                indexed_ids.append(str(result['id']))
            
            # Update status to indexed
            await conn.execute("""
                UPDATE documents 
                SET status = 'indexed', updated_at = NOW()
                WHERE id = ANY($1)
            """, indexed_ids)
            
            return indexed_ids
    
    async def _index_parallel(self, documents: List[Document], vectors: List[List[float]]) -> List[str]:
        """Index documents in parallel batches."""
        batch_size = self.config.batch_size
        batches = [
            (documents[i:i + batch_size], vectors[i:i + batch_size])
            for i in range(0, len(documents), batch_size)
        ]
        
        # Process batches in parallel
        tasks = [self._index_batch(docs, vecs) for docs, vecs in batches]
        results = await asyncio.gather(*tasks)
        
        # Flatten results
        indexed_ids = []
        for batch_ids in results:
            indexed_ids.extend(batch_ids)
        
        return indexed_ids
    
    async def query(self, vector: List[float], limit: int = 10, filter_metadata: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """Query similar vectors."""
        if len(vector) != self.config.vector_dimension:
            raise ValueError(f"Query vector has dimension {len(vector)}, expected {self.config.vector_dimension}")
        
        if limit <= 0:
            raise ValueError("Limit must be positive")
        
        try:
            async with self.pool.acquire() as conn:
                # Build query with optional metadata filtering
                if filter_metadata:
                    metadata_conditions = []
                    params = [vector, limit]
                    param_count = 2
                    
                    for key, value in filter_metadata.items():
                        param_count += 1
                        if isinstance(value, (list, tuple)):
                            # Array contains
                            metadata_conditions.append(f"metadata->>'{key}' = ANY(${param_count})")
                            params.append(value)
                        else:
                            # Exact match
                            metadata_conditions.append(f"metadata->>'{key}' = ${param_count}")
                            params.append(value)
                    
                    where_clause = "WHERE " + " AND ".join(metadata_conditions)
                else:
                    where_clause = ""
                    params = [vector, limit]
                
                # Execute similarity search
                query = f"""
                    SELECT 
                        id, content, title, doc_type, metadata, status,
                        created_at, updated_at, source, chunk_index, parent_id,
                        1 - (embedding <=> $1) as similarity_score,
                        embedding <-> $1 as distance
                    FROM documents
                    {where_clause}
                    AND status = 'indexed'
                    ORDER BY embedding <-> $1
                    LIMIT $2
                """
                
                rows = await conn.fetch(query, *params)
                
                # Convert to SearchResult objects
                results = []
                for rank, row in enumerate(rows, 1):
                    doc = Document(
                        id=str(row['id']),
                        content=row['content'],
                        title=row['title'],
                        doc_type=DocumentType(row['doc_type']),
                        metadata=row['metadata'],
                        status=DocumentStatus(row['status']),
                        created_at=row['created_at'],
                        updated_at=row['updated_at'],
                        source=row['source'],
                        chunk_index=row['chunk_index'],
                        parent_id=str(row['parent_id']) if row['parent_id'] else None
                    )
                    
                    result = SearchResult(
                        document=doc,
                        similarity_score=float(row['similarity_score']),
                        distance=float(row['distance']),
                        rank=rank
                    )
                    
                    results.append(result)
                
                self.total_queries += 1
                self.logger.debug(f"Query returned {len(results)} results")
                
                return results
                
        except Exception as e:
            self.logger.error(f"Failed to query vectors: {e}")
            raise
    
    async def get(self, document_ids: List[str]) -> List[Document]:
        """Get documents by IDs."""
        if not document_ids:
            return []
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT id, content, title, doc_type, metadata, status,
                           created_at, updated_at, source, chunk_index, parent_id
                    FROM documents
                    WHERE id = ANY($1)
                """, document_ids)
                
                documents = []
                for row in rows:
                    doc = Document(
                        id=str(row['id']),
                        content=row['content'],
                        title=row['title'],
                        doc_type=DocumentType(row['doc_type']),
                        metadata=row['metadata'],
                        status=DocumentStatus(row['status']),
                        created_at=row['created_at'],
                        updated_at=row['updated_at'],
                        source=row['source'],
                        chunk_index=row['chunk_index'],
                        parent_id=str(row['parent_id']) if row['parent_id'] else None
                    )
                    documents.append(doc)
                
                return documents
                
        except Exception as e:
            self.logger.error(f"Failed to get documents: {e}")
            raise
    
    async def delete(self, document_ids: List[str]) -> bool:
        """Delete documents by IDs."""
        if not document_ids:
            return True
        
        try:
            async with self.pool.acquire() as conn:
                # Soft delete by updating status
                result = await conn.execute("""
                    UPDATE documents 
                    SET status = 'deleted', updated_at = NOW()
                    WHERE id = ANY($1) AND status != 'deleted'
                """, document_ids)
                
                deleted_count = int(result.split()[-1])
                self.logger.info(f"Deleted {deleted_count} documents")
                
                return deleted_count > 0
                
        except Exception as e:
            self.logger.error(f"Failed to delete documents: {e}")
            raise
    
    async def update(self, document_id: str, document: Document, vector: Optional[List[float]] = None) -> bool:
        """Update a document and optionally its vector."""
        try:
            async with self.pool.acquire() as conn:
                if vector is not None:
                    if len(vector) != self.config.vector_dimension:
                        raise ValueError(f"Vector has dimension {len(vector)}, expected {self.config.vector_dimension}")
                    
                    # Update document with vector
                    result = await conn.execute("""
                        UPDATE documents 
                        SET content = $2, title = $3, doc_type = $4, metadata = $5,
                            status = $6, source = $7, chunk_index = $8, parent_id = $9,
                            embedding = $10, updated_at = NOW()
                        WHERE id = $1
                    """, 
                        document_id, document.content, document.title, document.doc_type.value,
                        json.dumps(document.metadata), document.status.value,
                        document.source, document.chunk_index, document.parent_id, vector
                    )
                else:
                    # Update document without vector
                    result = await conn.execute("""
                        UPDATE documents 
                        SET content = $2, title = $3, doc_type = $4, metadata = $5,
                            status = $6, source = $7, chunk_index = $8, parent_id = $9,
                            updated_at = NOW()
                        WHERE id = $1
                    """, 
                        document_id, document.content, document.title, document.doc_type.value,
                        json.dumps(document.metadata), document.status.value,
                        document.source, document.chunk_index, document.parent_id
                    )
                
                updated_count = int(result.split()[-1])
                return updated_count > 0
                
        except Exception as e:
            self.logger.error(f"Failed to update document {document_id}: {e}")
            raise
    
    async def search_by_metadata(self, metadata: Dict[str, Any], limit: int = 10) -> List[Document]:
        """Search documents by metadata."""
        if not metadata:
            return []
        
        try:
            async with self.pool.acquire() as conn:
                conditions = []
                params = [limit]
                param_count = 1
                
                for key, value in metadata.items():
                    param_count += 1
                    if isinstance(value, (list, tuple)):
                        # Array contains
                        conditions.append(f"metadata->>'{key}' = ANY(${param_count})")
                        params.append(value)
                    else:
                        # Exact match
                        conditions.append(f"metadata->>'{key}' = ${param_count}")
                        params.append(value)
                
                where_clause = "WHERE " + " AND ".join(conditions)
                
                query = f"""
                    SELECT id, content, title, doc_type, metadata, status,
                           created_at, updated_at, source, chunk_index, parent_id
                    FROM documents
                    {where_clause}
                    AND status = 'indexed'
                    ORDER BY created_at DESC
                    LIMIT $1
                """
                
                rows = await conn.fetch(query, *params)
                
                documents = []
                for row in rows:
                    doc = Document(
                        id=str(row['id']),
                        content=row['content'],
                        title=row['title'],
                        doc_type=DocumentType(row['doc_type']),
                        metadata=row['metadata'],
                        status=DocumentStatus(row['status']),
                        created_at=row['created_at'],
                        updated_at=row['updated_at'],
                        source=row['source'],
                        chunk_index=row['chunk_index'],
                        parent_id=str(row['parent_id']) if row['parent_id'] else None
                    )
                    documents.append(doc)
                
                return documents
                
        except Exception as e:
            self.logger.error(f"Failed to search by metadata: {e}")
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get store statistics."""
        try:
            async with self.pool.acquire() as conn:
                # Get document counts by status
                status_counts = await conn.fetch("""
                    SELECT status, COUNT(*) as count
                    FROM documents
                    GROUP BY status
                """)
                
                # Get document counts by type
                type_counts = await conn.fetch("""
                    SELECT doc_type, COUNT(*) as count
                    FROM documents
                    WHERE status = 'indexed'
                    GROUP BY doc_type
                """)
                
                # Get total document count
                total_docs = await conn.fetchval("SELECT COUNT(*) FROM documents")
                
                # Get index size
                index_size = await conn.fetchval("""
                    SELECT pg_size_pretty(pg_relation_size('documents'))
                """)
                
                stats = {
                    "total_documents": total_docs,
                    "status_counts": {row['status']: row['count'] for row in status_counts},
                    "type_counts": {row['doc_type']: row['count'] for row in type_counts},
                    "index_size": index_size,
                    "vector_dimension": self.config.vector_dimension,
                    "total_queries": self.total_queries,
                    "total_indexes": self.total_indexes,
                    "cache_hits": self.cache_hits,
                    "cache_misses": self.cache_misses,
                    "connection_pool_size": self.pool.get_size() if self.pool else 0,
                    "connection_pool_idle": self.pool.get_idle_size() if self.pool else 0
                }
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            async with self.pool.acquire() as conn:
                # Test basic connectivity
                await conn.fetchval("SELECT 1")
                
                # Test vector operations
                test_vector = [0.1] * self.config.vector_dimension
                await conn.fetchval("SELECT $1::vector", test_vector)
                
                return {
                    "status": "healthy",
                    "database_connected": True,
                    "vector_extension_available": True,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "database_connected": False,
                "vector_extension_available": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def close(self) -> None:
        """Close the vector store."""
        if self.pool:
            await self.pool.close()
            self.logger.info("PostgreSQL vector store closed")


# ============================================================================
# Factory Functions
# ============================================================================

def create_postgresql_vector_store(
    database: str,
    username: str,
    password: str,
    host: str = "localhost",
    port: int = 5432,
    vector_dimension: int = 1536,
    **kwargs
) -> PostgreSQLVectorStore:
    """Create a PostgreSQL vector store with default configuration."""
    config = PostgreSQLConfig(
        host=host,
        port=port,
        database=database,
        username=username,
        password=password,
        vector_dimension=vector_dimension,
        **kwargs
    )
    return PostgreSQLVectorStore(config)


async def create_and_initialize_vector_store(
    database: str,
    username: str,
    password: str,
    host: str = "localhost",
    port: int = 5432,
    vector_dimension: int = 1536,
    **kwargs
) -> PostgreSQLVectorStore:
    """Create and initialize a PostgreSQL vector store."""
    store = create_postgresql_vector_store(
        database=database,
        username=username,
        password=password,
        host=host,
        port=port,
        vector_dimension=vector_dimension,
        **kwargs
    )
    await store.initialize()
    return store


# ============================================================================
# Export all classes and functions
# ============================================================================

__all__ = [
    # Interface
    "VectorStore",
    
    # Enums
    "DocumentType",
    "DocumentStatus",
    
    # Models
    "Document",
    "SearchResult",
    "VectorIndex",
    "PostgreSQLConfig",
    
    # Implementation
    "PostgreSQLVectorStore",
    
    # Factory functions
    "create_postgresql_vector_store",
    "create_and_initialize_vector_store",
]
