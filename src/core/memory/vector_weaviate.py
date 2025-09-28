"""
Weaviate Vector Store Implementation for Agentic LLM Core v0.1

This module provides a Weaviate-based vector store using the existing Docker container.
Leverages the universal-ai-tools-weaviate container running on localhost:8090.

Created: 2024-09-24
Status: Draft
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import aiohttp
from pydantic import BaseModel, Field

from .vector_pg import VectorStore, Document, DocumentType, DocumentStatus, SearchResult


# ============================================================================
# Weaviate Configuration
# ============================================================================

class WeaviateConfig(BaseModel):
    """Weaviate configuration."""
    host: str = Field(default="localhost", description="Weaviate host")
    port: int = Field(default=8090, ge=1, le=65535, description="Weaviate port")
    scheme: str = Field(default="http", description="Connection scheme")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    
    # Class settings
    class_name: str = Field(default="Document", description="Weaviate class name")
    vector_dimension: int = Field(default=1536, ge=1, description="Vector dimension")
    
    # Performance settings
    batch_size: int = Field(default=100, ge=1, le=1000, description="Batch size for operations")
    timeout: float = Field(default=30.0, ge=1.0, description="Request timeout in seconds")
    
    @property
    def base_url(self) -> str:
        """Get base URL for Weaviate."""
        return f"{self.scheme}://{self.host}:{self.port}"


# ============================================================================
# Weaviate Vector Store Implementation
# ============================================================================

class WeaviateVectorStore(VectorStore):
    """Weaviate-based vector store."""
    
    def __init__(self, config: WeaviateConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.total_documents = 0
        self.total_queries = 0
        self.total_indexes = 0
    
    async def initialize(self) -> None:
        """Initialize the Weaviate vector store."""
        try:
            # Create HTTP session
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
            # Test connection
            await self._test_connection()
            
            # Create schema if it doesn't exist
            await self._create_schema()
            
            self.logger.info(f"Weaviate vector store initialized at {self.config.base_url}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Weaviate vector store: {e}")
            raise
    
    async def _test_connection(self) -> None:
        """Test connection to Weaviate."""
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        async with self.session.get(f"{self.config.base_url}/v1/meta") as response:
            if response.status != 200:
                raise ConnectionError(f"Weaviate connection failed: {response.status}")
            
            meta = await response.json()
            self.logger.info(f"Connected to Weaviate version: {meta.get('version', 'unknown')}")
    
    async def _create_schema(self) -> None:
        """Create Weaviate schema if it doesn't exist."""
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        # Check if class exists
        async with self.session.get(f"{self.config.base_url}/v1/schema/{self.config.class_name}") as response:
            if response.status == 200:
                self.logger.info(f"Class {self.config.class_name} already exists")
                return
        
        # Create class schema
        schema = {
            "class": self.config.class_name,
            "description": "Document storage for Agentic LLM Core",
            "vectorizer": "none",  # We provide our own vectors
            "properties": [
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "Document content"
                },
                {
                    "name": "title",
                    "dataType": ["text"],
                    "description": "Document title"
                },
                {
                    "name": "doc_type",
                    "dataType": ["text"],
                    "description": "Document type"
                },
                {
                    "name": "metadata",
                    "dataType": ["object"],
                    "description": "Document metadata"
                },
                {
                    "name": "status",
                    "dataType": ["text"],
                    "description": "Document status"
                },
                {
                    "name": "source",
                    "dataType": ["text"],
                    "description": "Document source"
                },
                {
                    "name": "chunk_index",
                    "dataType": ["int"],
                    "description": "Chunk index"
                },
                {
                    "name": "parent_id",
                    "dataType": ["text"],
                    "description": "Parent document ID"
                },
                {
                    "name": "created_at",
                    "dataType": ["date"],
                    "description": "Creation timestamp"
                },
                {
                    "name": "updated_at",
                    "dataType": ["date"],
                    "description": "Last update timestamp"
                }
            ]
        }
        
        async with self.session.post(
            f"{self.config.base_url}/v1/schema",
            json=schema
        ) as response:
            if response.status == 200:
                self.logger.info(f"Created class {self.config.class_name}")
            else:
                error_text = await response.text()
                raise RuntimeError(f"Failed to create schema: {error_text}")
    
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
            # Process in batches
            for i in range(0, len(documents), self.config.batch_size):
                batch_docs = documents[i:i + self.config.batch_size]
                batch_vectors = vectors[i:i + self.config.batch_size]
                
                batch_ids = await self._index_batch(batch_docs, batch_vectors)
                indexed_ids.extend(batch_ids)
            
            self.total_indexes += len(indexed_ids)
            self.logger.info(f"Indexed {len(indexed_ids)} documents in Weaviate")
            
        except Exception as e:
            self.logger.error(f"Failed to index documents: {e}")
            raise
        
        return indexed_ids
    
    async def _index_batch(self, documents: List[Document], vectors: List[List[float]]) -> List[str]:
        """Index a batch of documents."""
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        # Prepare batch objects
        objects = []
        for doc, vector in zip(documents, vectors):
            obj = {
                "id": doc.id,
                "properties": {
                    "content": doc.content,
                    "title": doc.title or "",
                    "doc_type": doc.doc_type.value,
                    "metadata": doc.metadata,
                    "status": doc.status.value,
                    "source": doc.source or "",
                    "chunk_index": doc.chunk_index,
                    "parent_id": doc.parent_id or "",
                    "created_at": doc.created_at.isoformat(),
                    "updated_at": doc.updated_at.isoformat()
                },
                "vector": vector
            }
            objects.append(obj)
        
        # Send batch to Weaviate
        batch_data = {
            "objects": objects
        }
        
        async with self.session.post(
            f"{self.config.base_url}/v1/batch/objects",
            json=batch_data
        ) as response:
            if response.status == 200:
                result = await response.json()
                indexed_ids = [obj["id"] for obj in result.get("objects", [])]
                return indexed_ids
            else:
                error_text = await response.text()
                raise RuntimeError(f"Failed to index batch: {error_text}")
    
    async def query(self, vector: List[float], limit: int = 10, filter_metadata: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """Query similar vectors."""
        if len(vector) != self.config.vector_dimension:
            raise ValueError(f"Query vector has dimension {len(vector)}, expected {self.config.vector_dimension}")
        
        if limit <= 0:
            raise ValueError("Limit must be positive")
        
        try:
            if not self.session:
                raise RuntimeError("Session not initialized")
            
            # Build where clause for metadata filtering
            where_clause = {
                "path": ["status"],
                "operator": "Equal",
                "valueText": "indexed"
            }
            
            if filter_metadata:
                # Add metadata filters
                metadata_filters = []
                for key, value in filter_metadata.items():
                    if isinstance(value, (list, tuple)):
                        # Array contains
                        metadata_filters.append({
                            "path": ["metadata", key],
                            "operator": "ContainsAny",
                            "valueTextArray": value
                        })
                    else:
                        # Exact match
                        metadata_filters.append({
                            "path": ["metadata", key],
                            "operator": "Equal",
                            "valueText": str(value)
                        })
                
                if metadata_filters:
                    where_clause = {
                        "operator": "And",
                        "operands": [where_clause] + metadata_filters
                    }
            
            # Build query
            query_data = {
                "query": {
                    "nearVector": {
                        "vector": vector,
                        "certainty": 0.0  # We'll calculate similarity ourselves
                    },
                    "where": where_clause,
                    "limit": limit,
                    "withMeta": True
                }
            }
            
            async with self.session.post(
                f"{self.config.base_url}/v1/graphql",
                json={"query": self._build_graphql_query(query_data)}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return self._parse_search_results(result)
                else:
                    error_text = await response.text()
                    raise RuntimeError(f"Failed to query: {error_text}")
                    
        except Exception as e:
            self.logger.error(f"Failed to query vectors: {e}")
            raise
    
    def _build_graphql_query(self, query_data: Dict[str, Any]) -> str:
        """Build GraphQL query for Weaviate."""
        # This is a simplified GraphQL query builder
        # In a production system, you'd want a more robust GraphQL client
        return f"""
        {{
            Get {{
                {self.config.class_name}(
                    nearVector: {{
                        vector: {query_data['query']['nearVector']['vector']}
                        certainty: {query_data['query']['nearVector']['certainty']}
                    }}
                    where: {json.dumps(query_data['query']['where'])}
                    limit: {query_data['query']['limit']}
                ) {{
                    _additional {{
                        id
                        distance
                    }}
                    content
                    title
                    doc_type
                    metadata
                    status
                    source
                    chunk_index
                    parent_id
                    created_at
                    updated_at
                }}
            }}
        }}
        """
    
    def _parse_search_results(self, result: Dict[str, Any]) -> List[SearchResult]:
        """Parse Weaviate search results."""
        results = []
        
        data = result.get("data", {}).get("Get", {}).get(self.config.class_name, [])
        
        for rank, item in enumerate(data, 1):
            additional = item.get("_additional", {})
            
            # Create document
            doc = Document(
                id=additional.get("id", ""),
                content=item.get("content", ""),
                title=item.get("title"),
                doc_type=DocumentType(item.get("doc_type", "text")),
                metadata=item.get("metadata", {}),
                status=DocumentStatus(item.get("status", "pending")),
                source=item.get("source"),
                chunk_index=item.get("chunk_index"),
                parent_id=item.get("parent_id"),
                created_at=datetime.fromisoformat(item.get("created_at", datetime.now(timezone.utc).isoformat())),
                updated_at=datetime.fromisoformat(item.get("updated_at", datetime.now(timezone.utc).isoformat()))
            )
            
            # Calculate similarity score from distance
            distance = additional.get("distance", 1.0)
            similarity_score = max(0.0, 1.0 - distance)
            
            result_obj = SearchResult(
                document=doc,
                similarity_score=similarity_score,
                distance=distance,
                rank=rank
            )
            
            results.append(result_obj)
        
        self.total_queries += 1
        return results
    
    async def get(self, document_ids: List[str]) -> List[Document]:
        """Get documents by IDs."""
        if not document_ids:
            return []
        
        try:
            if not self.session:
                raise RuntimeError("Session not initialized")
            
            # Build GraphQL query for multiple IDs
            ids_str = json.dumps(document_ids)
            query = f"""
            {{
                Get {{
                    {self.config.class_name}(
                        where: {{
                            path: ["id"]
                            operator: ContainsAny
                            valueTextArray: {ids_str}
                        }}
                    ) {{
                        _additional {{
                            id
                        }}
                        content
                        title
                        doc_type
                        metadata
                        status
                        source
                        chunk_index
                        parent_id
                        created_at
                        updated_at
                    }}
                }}
            }}
            """
            
            async with self.session.post(
                f"{self.config.base_url}/v1/graphql",
                json={"query": query}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return self._parse_documents(result)
                else:
                    error_text = await response.text()
                    raise RuntimeError(f"Failed to get documents: {error_text}")
                    
        except Exception as e:
            self.logger.error(f"Failed to get documents: {e}")
            raise
    
    def _parse_documents(self, result: Dict[str, Any]) -> List[Document]:
        """Parse Weaviate documents."""
        documents = []
        
        data = result.get("data", {}).get("Get", {}).get(self.config.class_name, [])
        
        for item in data:
            additional = item.get("_additional", {})
            
            doc = Document(
                id=additional.get("id", ""),
                content=item.get("content", ""),
                title=item.get("title"),
                doc_type=DocumentType(item.get("doc_type", "text")),
                metadata=item.get("metadata", {}),
                status=DocumentStatus(item.get("status", "pending")),
                source=item.get("source"),
                chunk_index=item.get("chunk_index"),
                parent_id=item.get("parent_id"),
                created_at=datetime.fromisoformat(item.get("created_at", datetime.now(timezone.utc).isoformat())),
                updated_at=datetime.fromisoformat(item.get("updated_at", datetime.now(timezone.utc).isoformat()))
            )
            
            documents.append(doc)
        
        return documents
    
    async def delete(self, document_ids: List[str]) -> bool:
        """Delete documents by IDs."""
        if not document_ids:
            return True
        
        try:
            if not self.session:
                raise RuntimeError("Session not initialized")
            
            # Weaviate doesn't have soft delete, so we'll update status
            for doc_id in document_ids:
                mutation = f"""
                {{
                    Update {{
                        {self.config.class_name}(
                            where: {{
                                path: ["id"]
                                operator: Equal
                                valueText: "{doc_id}"
                            }}
                            data: {{
                                status: "deleted"
                                updated_at: "{datetime.now(timezone.utc).isoformat()}"
                            }}
                        ) {{
                            _additional {{
                                id
                            }}
                        }}
                    }}
                }}
                """
                
                async with self.session.post(
                    f"{self.config.base_url}/v1/graphql",
                    json={"query": mutation}
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        self.logger.warning(f"Failed to delete document {doc_id}: {error_text}")
            
            self.logger.info(f"Deleted {len(document_ids)} documents from Weaviate")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete documents: {e}")
            raise
    
    async def update(self, document_id: str, document: Document, vector: Optional[List[float]] = None) -> bool:
        """Update a document and optionally its vector."""
        try:
            if not self.session:
                raise RuntimeError("Session not initialized")
            
            # Build update data
            update_data = {
                "content": document.content,
                "title": document.title or "",
                "doc_type": document.doc_type.value,
                "metadata": document.metadata,
                "status": document.status.value,
                "source": document.source or "",
                "chunk_index": document.chunk_index,
                "parent_id": document.parent_id or "",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            mutation = f"""
            {{
                Update {{
                    {self.config.class_name}(
                        where: {{
                            path: ["id"]
                            operator: Equal
                            valueText: "{document_id}"
                        }}
                        data: {json.dumps(update_data)}
                    ) {{
                        _additional {{
                            id
                        }}
                    }}
                }}
            }}
            """
            
            async with self.session.post(
                f"{self.config.base_url}/v1/graphql",
                json={"query": mutation}
            ) as response:
                if response.status == 200:
                    return True
                else:
                    error_text = await response.text()
                    raise RuntimeError(f"Failed to update document: {error_text}")
                    
        except Exception as e:
            self.logger.error(f"Failed to update document {document_id}: {e}")
            raise
    
    async def search_by_metadata(self, metadata: Dict[str, Any], limit: int = 10) -> List[Document]:
        """Search documents by metadata."""
        if not metadata:
            return []
        
        try:
            if not self.session:
                raise RuntimeError("Session not initialized")
            
            # Build where clause
            metadata_filters = []
            for key, value in metadata.items():
                if isinstance(value, (list, tuple)):
                    metadata_filters.append({
                        "path": ["metadata", key],
                        "operator": "ContainsAny",
                        "valueTextArray": value
                    })
                else:
                    metadata_filters.append({
                        "path": ["metadata", key],
                        "operator": "Equal",
                        "valueText": str(value)
                    })
            
            where_clause = {
                "operator": "And",
                "operands": [
                    {
                        "path": ["status"],
                        "operator": "Equal",
                        "valueText": "indexed"
                    }
                ] + metadata_filters
            }
            
            query = f"""
            {{
                Get {{
                    {self.config.class_name}(
                        where: {json.dumps(where_clause)}
                        limit: {limit}
                        sort: [{{
                            path: ["created_at"]
                            order: desc
                        }}]
                    ) {{
                        _additional {{
                            id
                        }}
                        content
                        title
                        doc_type
                        metadata
                        status
                        source
                        chunk_index
                        parent_id
                        created_at
                        updated_at
                    }}
                }}
            }}
            """
            
            async with self.session.post(
                f"{self.config.base_url}/v1/graphql",
                json={"query": query}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return self._parse_documents(result)
                else:
                    error_text = await response.text()
                    raise RuntimeError(f"Failed to search by metadata: {error_text}")
                    
        except Exception as e:
            self.logger.error(f"Failed to search by metadata: {e}")
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get store statistics."""
        try:
            if not self.session:
                raise RuntimeError("Session not initialized")
            
            # Get class statistics
            query = f"""
            {{
                Aggregate {{
                    {self.config.class_name} {{
                        meta {{
                            count
                        }}
                        groupedBy {{
                            path: ["status"]
                            groups {{
                                value
                                count
                            }}
                        }}
                    }}
                }}
            }}
            """
            
            async with self.session.post(
                f"{self.config.base_url}/v1/graphql",
                json={"query": query}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    data = result.get("data", {}).get("Aggregate", {}).get(self.config.class_name, {})
                    
                    total_count = data.get("meta", {}).get("count", 0)
                    status_groups = data.get("groupedBy", [{}])[0].get("groups", [])
                    
                    status_counts = {group["value"]: group["count"] for group in status_groups}
                    
                    return {
                        "total_documents": total_count,
                        "status_counts": status_counts,
                        "vector_dimension": self.config.vector_dimension,
                        "total_queries": self.total_queries,
                        "total_indexes": self.total_indexes,
                        "weaviate_url": self.config.base_url,
                        "class_name": self.config.class_name
                    }
                else:
                    error_text = await response.text()
                    raise RuntimeError(f"Failed to get stats: {error_text}")
                    
        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            if not self.session:
                return {
                    "status": "unhealthy",
                    "error": "Session not initialized",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Test basic connectivity
            async with self.session.get(f"{self.config.base_url}/v1/meta") as response:
                if response.status == 200:
                    meta = await response.json()
                    return {
                        "status": "healthy",
                        "weaviate_version": meta.get("version", "unknown"),
                        "weaviate_url": self.config.base_url,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "error": f"HTTP {response.status}",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def close(self) -> None:
        """Close the vector store."""
        if self.session:
            await self.session.close()
            self.logger.info("Weaviate vector store closed")


# ============================================================================
# Factory Functions
# ============================================================================

def create_weaviate_vector_store(
    host: str = "localhost",
    port: int = 8090,
    class_name: str = "Document",
    vector_dimension: int = 1536,
    **kwargs
) -> WeaviateVectorStore:
    """Create a Weaviate vector store with default configuration."""
    config = WeaviateConfig(
        host=host,
        port=port,
        class_name=class_name,
        vector_dimension=vector_dimension,
        **kwargs
    )
    return WeaviateVectorStore(config)


async def create_and_initialize_weaviate_store(
    host: str = "localhost",
    port: int = 8090,
    class_name: str = "Document",
    vector_dimension: int = 1536,
    **kwargs
) -> WeaviateVectorStore:
    """Create and initialize a Weaviate vector store."""
    store = create_weaviate_vector_store(
        host=host,
        port=port,
        class_name=class_name,
        vector_dimension=vector_dimension,
        **kwargs
    )
    await store.initialize()
    return store


# ============================================================================
# Export all classes and functions
# ============================================================================

__all__ = [
    # Configuration
    "WeaviateConfig",
    
    # Implementation
    "WeaviateVectorStore",
    
    # Factory functions
    "create_weaviate_vector_store",
    "create_and_initialize_weaviate_store",
]
