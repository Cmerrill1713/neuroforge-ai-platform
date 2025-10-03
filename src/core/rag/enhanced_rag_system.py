#!/usr/bin/env python3
"""
Enhanced RAG System with Advanced Deduplication and Hybrid Search
Fixes the issues identified in the RAG evaluation report
"""

import logging
import hashlib
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Set
from pathlib import Path
import json
import time
from collections import defaultdict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Enhanced search result with deduplication metadata"""
    id: str
    content: str
    score: float
    metadata: Dict[str, Any]
    content_hash: str
    retrieval_method: str
    confidence_score: float = 0.0
    deduplication_info: Dict[str, Any] = None

class ContentDeduplicator:
    """Advanced content deduplication system"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.content_hashes: Set[str] = set()
        self.content_clusters: Dict[str, List[str]] = defaultdict(list)
        
    def generate_content_hash(self, content: str) -> str:
        """Generate a hash for content deduplication"""
        # Normalize content for hashing
        normalized = content.lower().strip()
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def is_duplicate(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Check if content is a duplicate
        
        Returns:
            (is_duplicate, existing_hash)
        """
        content_hash = self.generate_content_hash(content)
        
        if content_hash in self.content_hashes:
            return True, content_hash
        
        return False, None
    
    def add_content(self, content: str, doc_id: str) -> str:
        """Add content and return its hash"""
        content_hash = self.generate_content_hash(content)
        self.content_hashes.add(content_hash)
        self.content_clusters[content_hash].append(doc_id)
        return content_hash
    
    def get_cluster_info(self, content_hash: str) -> Dict[str, Any]:
        """Get information about content cluster"""
        if content_hash not in self.content_clusters:
            return {"cluster_size": 1, "documents": []}
        
        cluster_docs = self.content_clusters[content_hash]
        return {
            "cluster_size": len(cluster_docs),
            "documents": cluster_docs,
            "is_duplicate": len(cluster_docs) > 1
        }

class HybridSearchEngine:
    """Enhanced hybrid search with BM25 + Vector + Graph search"""
    
    def __init__(self, vector_engine, bm25_engine, graph_engine=None):
        self.vector_engine = vector_engine
        self.bm25_engine = bm25_engine
        self.graph_engine = graph_engine
        
    def hybrid_search(self, query: str, top_k: int = 10, 
                     vector_weight: float = 0.6,
                     bm25_weight: float = 0.3,
                     graph_weight: float = 0.1) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining multiple retrieval methods
        
        Args:
            query: Search query
            top_k: Number of results to return
            vector_weight: Weight for vector similarity scores
            bm25_weight: Weight for BM25 keyword scores
            graph_weight: Weight for graph-based scores
            
        Returns:
            List of search results with hybrid scores
        """
        results = []
        
        # Get vector search results
        vector_results = self.vector_engine.search(query, top_k=top_k*2)
        
        # Get BM25 results
        bm25_results = self.bm25_engine.search(query, top_k=top_k*2)
        
        # Get graph results (if available)
        graph_results = []
        if self.graph_engine:
            graph_results = self.graph_engine.search(query, top_k=top_k*2)
        
        # Create result index
        result_index = {}
        
        # Index vector results
        for i, result in enumerate(vector_results):
            doc_id = result.get('id', f"doc_{i}")
            if doc_id not in result_index:
                result_index[doc_id] = {
                    'id': doc_id,
                    'content': result.get('document', ''),
                    'metadata': result.get('metadata', {}),
                    'vector_score': result.get('similarity', 0.0),
                    'bm25_score': 0.0,
                    'graph_score': 0.0,
                    'retrieval_methods': []
                }
            result_index[doc_id]['vector_score'] = result.get('similarity', 0.0)
            result_index[doc_id]['retrieval_methods'].append('vector')
        
        # Index BM25 results
        for i, (doc_idx, score) in enumerate(bm25_results):
            doc_id = f"doc_{doc_idx}"
            if doc_id not in result_index:
                result_index[doc_id] = {
                    'id': doc_id,
                    'content': self.bm25_engine.documents[doc_idx] if doc_idx < len(self.bm25_engine.documents) else '',
                    'metadata': {},
                    'vector_score': 0.0,
                    'bm25_score': score,
                    'graph_score': 0.0,
                    'retrieval_methods': []
                }
            result_index[doc_id]['bm25_score'] = score
            result_index[doc_id]['retrieval_methods'].append('bm25')
        
        # Index graph results
        for result in graph_results:
            doc_id = result.get('id', '')
            if doc_id not in result_index:
                result_index[doc_id] = {
                    'id': doc_id,
                    'content': result.get('content', ''),
                    'metadata': result.get('metadata', {}),
                    'vector_score': 0.0,
                    'bm25_score': 0.0,
                    'graph_score': result.get('score', 0.0),
                    'retrieval_methods': []
                }
            result_index[doc_id]['graph_score'] = result.get('score', 0.0)
            result_index[doc_id]['retrieval_methods'].append('graph')
        
        # Calculate hybrid scores
        for doc_id, result in result_index.items():
            hybrid_score = (
                result['vector_score'] * vector_weight +
                result['bm25_score'] * bm25_weight +
                result['graph_score'] * graph_weight
            )
            result['hybrid_score'] = hybrid_score
        
        # Sort by hybrid score and return top_k
        sorted_results = sorted(
            result_index.values(),
            key=lambda x: x['hybrid_score'],
            reverse=True
        )
        
        return sorted_results[:top_k]

class EnhancedRAGSystem:
    """Enhanced RAG system with advanced deduplication and hybrid search"""
    
    def __init__(self, base_engine, use_deduplication: bool = True, 
                 use_hybrid_search: bool = True):
        self.base_engine = base_engine
        self.deduplicator = ContentDeduplicator() if use_deduplication else None
        self.use_hybrid_search = use_hybrid_search
        self.hybrid_engine = None
        
        # Performance metrics
        self.search_stats = {
            'total_searches': 0,
            'total_results': 0,
            'duplicates_filtered': 0,
            'avg_latency_ms': 0.0,
            'cache_hits': 0
        }
        
    def initialize(self) -> bool:
        """Initialize the enhanced RAG system"""
        try:
            if not self.base_engine.initialize():
                return False
            
            # Initialize hybrid search if enabled
            if self.use_hybrid_search:
                from .keyword_search import KeywordSearchEngine
                bm25_engine = KeywordSearchEngine()
                if hasattr(self.base_engine, 'documents') and self.base_engine.documents:
                    bm25_engine.add_documents(self.base_engine.documents)
                
                self.hybrid_engine = HybridSearchEngine(
                    vector_engine=self.base_engine,
                    bm25_engine=bm25_engine
                )
            
            logger.info("Enhanced RAG system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize enhanced RAG system: {e}")
            return False
    
    def search(self, query: str, top_k: int = 10, 
               deduplicate: bool = True,
               use_hybrid: bool = True) -> List[SearchResult]:
        """
        Enhanced search with deduplication and hybrid retrieval
        
        Args:
            query: Search query
            top_k: Number of results to return
            deduplicate: Whether to apply deduplication
            use_hybrid: Whether to use hybrid search
            
        Returns:
            List of enhanced search results
        """
        start_time = time.time()
        
        try:
            # Perform search
            if use_hybrid and self.hybrid_engine:
                raw_results = self.hybrid_engine.hybrid_search(query, top_k=top_k*2)
            else:
                raw_results = self.base_engine.search(query, top_k=top_k*2)
            
            # Convert to SearchResult objects
            search_results = []
            seen_hashes = set()
            
            for i, result in enumerate(raw_results):
                content = result.get('content', result.get('document', ''))
                
                # Generate content hash
                content_hash = self.deduplicator.generate_content_hash(content) if self.deduplicator else f"hash_{i}"
                
                # Apply deduplication if enabled
                if deduplicate and self.deduplicator:
                    if content_hash in seen_hashes:
                        self.search_stats['duplicates_filtered'] += 1
                        continue
                    seen_hashes.add(content_hash)
                
                # Create enhanced search result
                search_result = SearchResult(
                    id=result.get('id', f"result_{i}"),
                    content=content,
                    score=result.get('hybrid_score', result.get('similarity', result.get('score', 0.0))),
                    metadata=result.get('metadata', {}),
                    content_hash=content_hash,
                    retrieval_method=','.join(result.get('retrieval_methods', ['vector'])),
                    confidence_score=self._calculate_confidence_score(result, query)
                )
                
                # Add deduplication info
                if self.deduplicator:
                    cluster_info = self.deduplicator.get_cluster_info(content_hash)
                    search_result.deduplication_info = cluster_info
                
                search_results.append(search_result)
            
            # Update statistics
            latency_ms = (time.time() - start_time) * 1000
            self._update_stats(len(search_results), latency_ms)
            
            logger.info(f"Enhanced search completed: {len(search_results)} results in {latency_ms:.1f}ms")
            
            return search_results[:top_k]
            
        except Exception as e:
            logger.error(f"Enhanced search failed: {e}")
            return []
    
    def _calculate_confidence_score(self, result: Dict[str, Any], query: str) -> float:
        """Calculate confidence score for a search result"""
        confidence = 0.0
        
        # Base score from similarity
        score = result.get('hybrid_score', result.get('similarity', result.get('score', 0.0)))
        confidence += score * 0.6
        
        # Boost for multiple retrieval methods
        methods = result.get('retrieval_methods', [])
        if len(methods) > 1:
            confidence += 0.2
        
        # Boost for high-quality metadata
        metadata = result.get('metadata', {})
        if metadata.get('category') in ['AI', 'ML', 'technical']:
            confidence += 0.1
        
        # Boost for recent content
        if metadata.get('timestamp'):
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _update_stats(self, num_results: int, latency_ms: float):
        """Update search statistics"""
        self.search_stats['total_searches'] += 1
        self.search_stats['total_results'] += num_results
        
        # Update average latency
        total_searches = self.search_stats['total_searches']
        current_avg = self.search_stats['avg_latency_ms']
        self.search_stats['avg_latency_ms'] = (
            (current_avg * (total_searches - 1) + latency_ms) / total_searches
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get enhanced RAG system statistics"""
        base_stats = self.base_engine.get_stats() if hasattr(self.base_engine, 'get_stats') else {}
        
        enhanced_stats = {
            **base_stats,
            'enhanced_features': {
                'deduplication_enabled': self.deduplicator is not None,
                'hybrid_search_enabled': self.use_hybrid_search,
                'total_unique_content_hashes': len(self.deduplicator.content_hashes) if self.deduplicator else 0,
                'content_clusters': len(self.deduplicator.content_clusters) if self.deduplicator else 0
            },
            'search_performance': self.search_stats
        }
        
        return enhanced_stats
    
    def add_documents(self, documents: List[str], metadata: List[Dict[str, Any]] = None):
        """Add documents with deduplication"""
        if not documents:
            return
        
        # Filter duplicates before adding
        unique_docs = []
        unique_metadata = []
        
        for i, doc in enumerate(documents):
            if self.deduplicator:
                is_dup, existing_hash = self.deduplicator.is_duplicate(doc)
                if is_dup:
                    logger.debug(f"Skipping duplicate document: {doc[:50]}...")
                    continue
            
            unique_docs.append(doc)
            unique_metadata.append(metadata[i] if metadata else {})
            
            # Add to deduplicator
            if self.deduplicator:
                doc_id = f"doc_{len(unique_docs)}"
                self.deduplicator.add_content(doc, doc_id)
        
        # Add unique documents to base engine
        if unique_docs:
            self.base_engine.add_documents(unique_docs, unique_metadata)
            logger.info(f"Added {len(unique_docs)} unique documents ({len(documents) - len(unique_docs)} duplicates filtered)")
    
    def get_deduplication_report(self) -> Dict[str, Any]:
        """Get detailed deduplication report"""
        if not self.deduplicator:
            return {"deduplication_enabled": False}
        
        # Analyze clusters
        cluster_sizes = [len(docs) for docs in self.deduplicator.content_clusters.values()]
        
        return {
            "deduplication_enabled": True,
            "total_content_hashes": len(self.deduplicator.content_hashes),
            "total_clusters": len(self.deduplicator.content_clusters),
            "duplicate_clusters": sum(1 for size in cluster_sizes if size > 1),
            "total_duplicates": sum(size - 1 for size in cluster_sizes if size > 1),
            "largest_cluster_size": max(cluster_sizes) if cluster_sizes else 0,
            "average_cluster_size": np.mean(cluster_sizes) if cluster_sizes else 0
        }

# Convenience functions for backward compatibility
def create_enhanced_rag_system(base_engine, **kwargs) -> EnhancedRAGSystem:
    """Create an enhanced RAG system with the given base engine"""
    return EnhancedRAGSystem(base_engine, **kwargs)

def search_with_deduplication(query: str, top_k: int = 10, **kwargs) -> List[SearchResult]:
    """Search with enhanced deduplication and hybrid retrieval"""
    # This would need to be implemented with a global enhanced engine instance
    pass
