#!/usr/bin/env python3
"""
Weaviate Vector Store Adapter
Production-ready implementation for your live stack
"""

import logging
import os
from typing import List, Dict, Any, Optional
import asyncio

try:
    import weaviate
    from weaviate.classes.query import MetadataQuery
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False
    logging.warning("weaviate-client not installed: pip install weaviate-client")

from .vector_store import VectorStore, QueryResult

logger = logging.getLogger(__name__)


class WeaviateStore(VectorStore):
    """
    Weaviate vector store adapter
    
    Connects to your production Weaviate instance (ports 8080 HTTP, 50051 gRPC)
    """
    
    def __init__(
        self,
        host: str = None,
        http_port: int = 8080,
        grpc_port: int = 50051,
        class_name: str = "DocChunk",
        timeout: int = 30
    ):
        if not WEAVIATE_AVAILABLE:
            raise ImportError("weaviate-client required: pip install weaviate-client")
        
        self.host = host or os.getenv("WEAVIATE_HOST", "weaviate")
        self.http_port = http_port
        self.grpc_port = grpc_port
        self.class_name = class_name
        self.timeout = timeout
        
        # Initialize connection
        self.client = None
        self._connect()
        
        logger.info(f"✅ Weaviate connected: {self.host}:{self.http_port} (class: {self.class_name})")
    
    def _connect(self):
        """Establish connection to Weaviate"""
        try:
            self.client = weaviate.connect_to_custom(
                http_host=self.host,
                http_port=self.http_port,
                http_secure=False,
                grpc_host=self.host,
                grpc_port=self.grpc_port,
                grpc_secure=False,
                skip_init_checks=False
            )
            
            # Verify connection
            if not self.client.is_ready():
                raise ConnectionError(f"Weaviate not ready at {self.host}:{self.http_port}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            raise
    
    async def upsert(self, items: List[Dict[str, Any]]) -> None:
        """
        Batch insert/update items
        
        Args:
            items: [{"id": str, "vector": list[float], "properties": dict}]
        """
        try:
            collection = self.client.collections.get(self.class_name)
            
            # Use dynamic batching for optimal performance
            with collection.batch.dynamic() as batch:
                for item in items:
                    batch.add_object(
                        properties=item["properties"],
                        vector=item["vector"],
                        uuid=item["id"]
                    )
            
            logger.info(f"✅ Upserted {len(items)} items to Weaviate")
            
        except Exception as e:
            logger.error(f"Weaviate upsert failed: {e}")
            raise
    
    async def query(
        self,
        embedding: List[float],
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[QueryResult]:
        """
        Vector similarity search with optional metadata filters
        
        Args:
            embedding: Query vector (normalized)
            k: Top-k results
            filters: Weaviate where filters (e.g., {"path": ["doctype"], "operator": "Equal", "valueText": "WI"})
        
        Returns:
            List of QueryResult objects sorted by distance
        """
        try:
            collection = self.client.collections.get(self.class_name)
            
            # Build query
            query_kwargs = {
                "near_vector": embedding,
                "limit": k,
                "return_metadata": MetadataQuery(distance=True, certainty=True),
                "return_properties": ["content", "title", "url", "source_type", "domain", "keywords"]
            }
            
            # Add filters if provided
            if filters:
                query_kwargs["where"] = filters
            
            # Execute query
            response = collection.query.near_vector(**query_kwargs)
            
            # Convert to QueryResult
            results = []
            for obj in response.objects:
                # Convert distance to similarity score (0 to 1, higher is better)
                distance = obj.metadata.distance if obj.metadata else 1.0
                score = 1.0 / (1.0 + distance)  # Convert distance to similarity
                
                results.append(QueryResult(
                    id=str(obj.uuid),
                    text=obj.properties.get("content", ""),  # ← Changed from "text"
                    score=score,
                    metadata={
                        "title": obj.properties.get("title"),
                        "url": obj.properties.get("url"),
                        "source_type": obj.properties.get("source_type"),
                        "domain": obj.properties.get("domain"),
                        "keywords": obj.properties.get("keywords"),
                        "distance": distance,
                        "certainty": obj.metadata.certainty if obj.metadata else None
                    }
                ))
            
            logger.debug(f"✅ Weaviate query returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Weaviate query failed: {e}")
            raise
    
    async def delete(self, ids: List[str]) -> None:
        """Delete items by UUID"""
        try:
            collection = self.client.collections.get(self.class_name)
            
            for item_id in ids:
                collection.data.delete_by_id(item_id)
            
            logger.info(f"✅ Deleted {len(ids)} items from Weaviate")
            
        except Exception as e:
            logger.error(f"Weaviate delete failed: {e}")
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get Weaviate statistics"""
        try:
            collection = self.client.collections.get(self.class_name)
            
            # Get collection stats
            stats = {
                "class_name": self.class_name,
                "host": self.host,
                "http_port": self.http_port,
                "grpc_port": self.grpc_port,
                "is_ready": self.client.is_ready(),
            }
            
            # Try to get object count
            try:
                # Note: Weaviate v4 doesn't have a direct count method
                # Use aggregate query
                agg = collection.aggregate.over_all()
                stats["total_objects"] = agg.total_count if hasattr(agg, 'total_count') else "unknown"
            except Exception:
                stats["total_objects"] = "unavailable"
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get Weaviate stats: {e}")
            return {"error": str(e)}
    
    def close(self):
        """Close connection"""
        if self.client:
            self.client.close()
            logger.info("✅ Weaviate connection closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

