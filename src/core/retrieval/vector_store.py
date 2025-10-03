#!/usr/bin/env python3
"""
Abstract Vector Store Interface
Allows swapping between Weaviate, Pinecone, Qdrant, etc. without changing business logic
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class QueryResult:
    """Standardized query result"""
    id: str
    text: str
    score: float
    metadata: Dict[str, Any]


class VectorStore(ABC):
    """Abstract interface for vector stores"""
    
    @abstractmethod
    async def upsert(self, items: List[Dict[str, Any]]) -> None:
        """
        Insert or update items
        
        Args:
            items: List of dicts with keys:
                - id: str (unique identifier)
                - vector: list[float] (embedding)
                - properties: dict (metadata + text)
        """
        pass
    
    @abstractmethod
    async def query(
        self,
        embedding: List[float],
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[QueryResult]:
        """
        Vector similarity search
        
        Args:
            embedding: Query vector
            k: Number of results
            filters: Optional metadata filters
            
        Returns:
            List of QueryResult objects sorted by similarity
        """
        pass
    
    @abstractmethod
    async def delete(self, ids: List[str]) -> None:
        """Delete items by ID"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get store statistics (count, memory, etc.)"""
        pass

