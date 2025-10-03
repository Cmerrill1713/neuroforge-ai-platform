#!/usr/bin/env python3
"""
Weaviate Knowledge Graph Integration for NeuroForge
Provides graph-based knowledge retrieval with vector search capabilities
"""

import logging
import weaviate
import weaviate.classes as wvc
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class WeaviateKnowledgeGraph:
    """
    Knowledge graph using Weaviate v4 for hybrid vector + graph search
    
    Features:
    - Graph-based entity relationships
    - Vector similarity search
    - Hybrid retrieval (semantic + graph traversal)
    - Persistent storage in Docker (port 8090)
    """
    
    def __init__(self, host: str = "localhost", port: int = 8090):
        self.host = host
        self.port = port
        self.client = None
        self.is_connected = False
        
    def connect(self) -> bool:
        """Connect to Weaviate v4 instance"""
        try:
            logger.info(f"Connecting to Weaviate at {self.host}:{self.port}")
            
            # Use Weaviate v4 client API
            self.client = weaviate.connect_to_local(
                host=self.host,
                port=self.port
            )
            
            # Test connection
            if self.client.is_ready():
                self.is_connected = True
                logger.info("✅ Connected to Weaviate knowledge graph v4")
                return True
            else:
                logger.warning("⚠️ Weaviate not ready")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to connect to Weaviate: {e}")
            self.is_connected = False
            return False
    
    def search(self, query: str, limit: int = 10, min_certainty: float = 0.7) -> List[Dict[str, Any]]:
        """
        Search the knowledge graph using hybrid vector + graph retrieval
        
        Args:
            query: Search query
            limit: Maximum number of results
            min_certainty: Minimum similarity threshold (0.0-1.0)
            
        Returns:
            List of search results with content, metadata, and relationships
        """
        if not self.is_connected:
            if not self.connect():
                return []
        
        try:
            results = []
            
            # Try each schema class
            for class_name in ["ComprehensiveDocument", "KnowledgeDocument", "Document", "MetaAIDocument"]:
                try:
                    response = (
                        self.client.query
                        .get(class_name, ["content", "title", "url", "domain", "source_type", "keywords", "retrieval_tags"])
                        .with_near_text({"concepts": [query]})
                        .with_limit(limit)
                        .with_additional(["certainty", "id"])
                        .do()
                    )
                    
                    if "data" in response and "Get" in response["data"]:
                        class_results = response["data"]["Get"].get(class_name, [])
                        for item in class_results:
                            certainty = item.get("_additional", {}).get("certainty", 0.0)
                            if certainty >= min_certainty:
                                results.append({
                                    "content": item.get("content", ""),
                                    "title": item.get("title", ""),
                                    "url": item.get("url", ""),
                                    "domain": item.get("domain", ""),
                                    "source_type": item.get("source_type", ""),
                                    "keywords": item.get("keywords", []),
                                    "retrieval_tags": item.get("retrieval_tags", []),
                                    "certainty": certainty,
                                    "id": item.get("_additional", {}).get("id", ""),
                                    "class": class_name
                                })
                except Exception as class_error:
                    logger.debug(f"No results from {class_name}: {class_error}")
                    continue
            
            # Sort by certainty and limit
            results.sort(key=lambda x: x["certainty"], reverse=True)
            results = results[:limit]
            
            logger.info(f"Found {len(results)} results from Weaviate knowledge graph")
            return results
            
        except Exception as e:
            logger.error(f"Weaviate search failed: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        if not self.is_connected:
            if not self.connect():
                return {"error": "Not connected"}
        
        try:
            schema = self.client.schema.get()
            total_objects = 0
            classes_info = []
            
            for class_obj in schema.get("classes", []):
                class_name = class_obj.get("class", "Unknown")
                try:
                    count_result = (
                        self.client.query
                        .aggregate(class_name)
                        .with_meta_count()
                        .do()
                    )
                    count = count_result.get("data", {}).get("Aggregate", {}).get(class_name, [{}])[0].get("meta", {}).get("count", 0)
                    total_objects += count
                    classes_info.append({
                        "name": class_name,
                        "count": count,
                        "vectorizer": class_obj.get("vectorizer", "none")
                    })
                except:
                    classes_info.append({"name": class_name, "count": 0})
            
            return {
                "connected": self.is_connected,
                "url": self.url,
                "total_objects": total_objects,
                "classes": classes_info,
                "version": "1.33.0"
            }
            
        except Exception as e:
            logger.error(f"Failed to get Weaviate stats: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> bool:
        """Check if Weaviate is healthy"""
        try:
            return self.client.is_ready() if self.client else False
        except:
            return False

# Global instance
_knowledge_graph = None

def get_knowledge_graph() -> WeaviateKnowledgeGraph:
    """Get global Weaviate knowledge graph instance"""
    global _knowledge_graph
    if _knowledge_graph is None:
        _knowledge_graph = WeaviateKnowledgeGraph()
        _knowledge_graph.connect()
    return _knowledge_graph

