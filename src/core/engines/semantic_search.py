#!/usr/bin/env python3
"""
Semantic Search Engine for NeuroForge
Uses SentenceTransformer embeddings for intelligent document retrieval
"""

import logging
import numpy as np
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
from pathlib import Path
import re
from collections import Counter

logger = logging.getLogger(__name__)

class CrossEncoderReranker:
    """
    Cross-encoder reranker for improving search result quality
    Uses cross-encoder/ms-marco-MiniLM-L-6-v2 for reliable reranking performance
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.model = None

    def initialize(self) -> bool:
        """Initialize the cross-encoder model"""
        try:
            logger.info(f"Initializing CrossEncoder reranker: {self.model_name}")
            self.model = CrossEncoder(self.model_name)
            logger.info("CrossEncoder reranker initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize CrossEncoder reranker: {e}")
            return False

    def rerank(self, query: str, documents: List[str], top_k: int = None) -> List[Tuple[int, float]]:
        """
        Rerank documents based on query relevance

        Args:
            query: Search query
            documents: List of document texts
            top_k: Number of top results to return (None for all)

        Returns:
            List of (index, score) tuples sorted by score descending
        """
        if not self.model:
            if not self.initialize():
                logger.warning("CrossEncoder reranker not available, returning original order")
                return [(i, 1.0) for i in range(len(documents))]

        try:
            # Create query-document pairs
            pairs = [(query, doc) for doc in documents]

            # Get reranker scores
            scores = self.model.predict(pairs)

            # Create (index, score) pairs and sort by score
            indexed_scores = list(enumerate(scores))
            indexed_scores.sort(key=lambda x: x[1], reverse=True)

            # Return top_k results if specified
            if top_k:
                indexed_scores = indexed_scores[:top_k]

            return indexed_scores

        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            return [(i, 1.0) for i in range(len(documents))]


class KeywordSearchEngine:
    """
    BM25-style keyword search engine for sparse retrieval
    """

    def __init__(self):
        self.documents = []
        self.doc_freq = {}  # Document frequency for each term
        self.term_freq = []  # Term frequency for each document
        self.doc_lengths = []
        self.avg_doc_length = 0
        self.k1 = 1.5  # BM25 parameter
        self.b = 0.75  # BM25 parameter

    def add_documents(self, documents: List[str]):
        """Add documents and build BM25 index"""
        self.documents = documents
        self.term_freq = []
        self.doc_lengths = []
        self.doc_freq = {}

        # Tokenize and build term frequencies
        for doc in documents:
            # Simple tokenization (lowercase, remove punctuation)
            tokens = re.findall(r'\b\w+\b', doc.lower())
            self.doc_lengths.append(len(tokens))

            # Term frequency for this document
            term_freq_doc = Counter(tokens)
            self.term_freq.append(term_freq_doc)

            # Update document frequency
            for term in set(tokens):
                self.doc_freq[term] = self.doc_freq.get(term, 0) + 1

        # Calculate average document length
        if self.doc_lengths:
            self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """
        Search using BM25 scoring

        Returns:
            List of (doc_index, score) tuples
        """
        if not self.documents:
            return []

        # Tokenize query
        query_tokens = re.findall(r'\b\w+\b', query.lower())

        # Calculate BM25 scores
        scores = []
        for doc_idx in range(len(self.documents)):
            score = 0.0
            doc_length = self.doc_lengths[doc_idx]

            for term in query_tokens:
                if term in self.term_freq[doc_idx]:
                    # BM25 scoring formula
                    tf = self.term_freq[doc_idx][term]
                    df = self.doc_freq.get(term, 0)
                    idf = np.log((len(self.documents) - df + 0.5) / (df + 0.5))

                    numerator = tf * (self.k1 + 1)
                    denominator = tf + self.k1 * (1 - self.b + self.b * doc_length / self.avg_doc_length)

                    score += idf * (numerator / denominator)

            scores.append((doc_idx, score))

        # Sort by score descending and return top_k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


class QueryExpansionEngine:
    """
    Query expansion engine for generating multiple query perspectives
    """

    def __init__(self):
        self.expansion_strategies = [
            self._synonym_expansion,
            self._concept_expansion,
            self._question_expansion
        ]

    def expand_query(self, query: str, num_expansions: int = 3) -> List[str]:
        """
        Generate expanded query variants

        Args:
            query: Original query
            num_expansions: Number of expanded queries to generate

        Returns:
            List of expanded query strings
        """
        expanded_queries = [query]  # Always include original

        # Apply different expansion strategies
        for strategy in self.expansion_strategies:
            try:
                new_queries = strategy(query)
                expanded_queries.extend(new_queries[:num_expansions])
            except Exception as e:
                logger.warning(f"Query expansion strategy failed: {e}")

        # Remove duplicates and limit
        expanded_queries = list(dict.fromkeys(expanded_queries))
        return expanded_queries[:num_expansions + 1]  # +1 for original

    def _synonym_expansion(self, query: str) -> List[str]:
        """Simple synonym-based expansion"""
        # Basic synonym mapping (could be enhanced with WordNet or similar)
        synonyms = {
            'machine learning': ['ML', 'artificial intelligence', 'AI'],
            'deep learning': ['neural networks', 'deep neural networks'],
            'computer vision': ['image recognition', 'visual processing'],
            'natural language': ['NLP', 'text processing', 'linguistic processing'],
            'reinforcement learning': ['RL', 'reward-based learning'],
            'supervised learning': ['labeled learning', 'classification'],
            'unsupervised learning': ['clustering', 'dimensionality reduction']
        }

        expanded = []
        for term, syns in synonyms.items():
            if term in query.lower():
                for syn in syns:
                    expanded.append(query.replace(term, syn))

        return expanded

    def _concept_expansion(self, query: str) -> List[str]:
        """Expand with related concepts"""
        concept_map = {
            'artificial intelligence': ['machine learning', 'neural networks', 'expert systems'],
            'machine learning': ['algorithms', 'training data', 'prediction'],
            'data science': ['statistics', 'machine learning', 'data analysis'],
            'computer vision': ['image processing', 'object detection', 'scene understanding']
        }

        expanded = []
        for concept, related in concept_map.items():
            if concept in query.lower():
                for rel in related:
                    if rel not in query.lower():
                        expanded.append(f"{query} {rel}")

        return expanded

    def _question_expansion(self, query: str) -> List[str]:
        """Convert statements to questions"""
        question_prefixes = [
            "What is",
            "How does",
            "What are the",
            "Explain",
            "Tell me about"
        ]

        expanded = []
        for prefix in question_prefixes:
            expanded.append(f"{prefix} {query}")

        return expanded


class SemanticSearchEngine:
    """
    Semantic search engine using SentenceTransformer embeddings with cross-encoder reranking
    Provides intelligent document retrieval based on meaning, not just keywords

    Features:
    - Persistent vector caching to avoid re-encoding
    - Incremental loading with deduplication
    - Cross-encoder reranking for improved accuracy
    - Fast startup and query performance
    """

    def __init__(self,
                 model_name: str = "Snowflake/snowflake-arctic-embed-m",
                 cache_dir: str = "cache/embeddings",
                 use_reranker: bool = True,
                 enable_parallel: bool = True):
        self.model_name = model_name
        self.model = None
        self.documents = []
        self.embeddings = None
        self.metadata = []
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "embeddings_cache.npz"
        self.loaded_files = set()  # Track which files have been loaded
        self.use_reranker = use_reranker
        self.reranker = CrossEncoderReranker() if use_reranker else None
        self.enable_parallel = enable_parallel
        self.parallel_engine = None
        
    def initialize(self) -> bool:
        """Initialize the SentenceTransformer model and load cached embeddings"""
        try:
            logger.info(f"Initializing SentenceTransformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            
            # Load cached embeddings if available
            if self.cache_file.exists():
                try:
                    logger.info(f"Loading cached embeddings from {self.cache_file}")
                    cache_data = np.load(self.cache_file, allow_pickle=True)
                    self.embeddings = cache_data['embeddings']
                    self.documents = cache_data['documents'].tolist()
                    self.metadata = cache_data['metadata'].tolist()
                    self.loaded_files = set(cache_data.get('loaded_files', []))
                    logger.info(f"Loaded {len(self.documents)} cached documents (skipping re-encoding)")
                except Exception as cache_error:
                    logger.warning(f"Failed to load cache: {cache_error}. Will rebuild.")
            
            logger.info("SentenceTransformer model initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize SentenceTransformer: {e}")
            return False
    
    def add_documents(self, documents: List[str], metadata: List[Dict[str, Any]] = None):
        """
        Add documents to the search index (only if not already added)
        
        Args:
            documents: List of document texts
            metadata: Optional metadata for each document
        """
        if not self.model:
            if not self.initialize():
                raise RuntimeError("Failed to initialize SentenceTransformer model")
        
        try:
            # Filter out duplicate documents
            new_docs = []
            new_meta = []
            for i, doc in enumerate(documents):
                if doc not in self.documents:
                    new_docs.append(doc)
                    new_meta.append(metadata[i] if metadata else {})
            
            if not new_docs:
                logger.info(f"All {len(documents)} documents already in index (skipping)")
                return
            
            # Generate embeddings for new documents only
            new_embeddings = self.model.encode(new_docs)
            
            # Add to existing documents and embeddings
            self.documents.extend(new_docs)
            if self.embeddings is None:
                self.embeddings = new_embeddings
            else:
                self.embeddings = np.vstack([self.embeddings, new_embeddings])
            
            # Add metadata
            self.metadata.extend(new_meta)

            logger.info(f"Added {len(new_docs)} new documents to search index ({len(documents) - len(new_docs)} duplicates skipped)")

            # Initialize parallel engine if enabled
            if self.enable_parallel and self.documents:
                self.parallel_engine = ParallelRetrievalEngine(self)

            # Save cache after adding documents
            self._save_cache()
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def search(self, query: str, top_k: int = 5, min_similarity: float = 0.0, rerank: bool = True) -> List[Dict[str, Any]]:
        """
        Search for documents similar to the query with optional cross-encoder reranking

        Args:
            query: Search query
            top_k: Number of top results to return
            min_similarity: Minimum similarity threshold
            rerank: Whether to use cross-encoder reranking

        Returns:
            List of search results with documents, similarities, and metadata
        """
        if not self.model or len(self.documents) == 0:
            return []

        try:
            # Initial semantic search (get more candidates than needed for reranking)
            candidate_k = min(len(self.documents), top_k * 3)  # Get 3x candidates for reranking

            # Encode the query
            query_embedding = self.model.encode([query])

            # Compute similarities
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]

            # Get initial candidates
            candidate_indices = np.argsort(similarities)[::-1][:candidate_k]

            # Filter by minimum similarity
            candidate_indices = [idx for idx in candidate_indices if similarities[idx] >= min_similarity]

            if not candidate_indices:
                return []

            # If reranking is enabled and we have the reranker, apply it
            if rerank and self.use_reranker and self.reranker and len(candidate_indices) > 1:
                try:
                    # Extract candidate documents
                    candidate_docs = [self.documents[idx] for idx in candidate_indices]

                    # Rerank candidates
                    reranked_indices_scores = self.reranker.rerank(query, candidate_docs, top_k=top_k)

                    # Convert back to original document indices and get final results
                    results = []
                    for candidate_idx, rerank_score in reranked_indices_scores:
                        original_idx = candidate_indices[candidate_idx]
                        semantic_score = similarities[original_idx]

                        results.append({
                            "document": self.documents[original_idx],
                            "similarity": float(semantic_score),
                            "rerank_score": float(rerank_score),
                            "metadata": self.metadata[original_idx],
                            "index": int(original_idx)
                        })

                    logger.info(f"Found {len(results)} reranked results for query: '{query}'")
                    return results

                except Exception as rerank_error:
                    logger.warning(f"Reranking failed, falling back to semantic search: {rerank_error}")

            # Fallback: return semantic search results
            results = []
            for idx in candidate_indices[:top_k]:
                similarity = similarities[idx]
                results.append({
                    "document": self.documents[idx],
                    "similarity": float(similarity),
                    "metadata": self.metadata[idx],
                    "index": int(idx)
                })

            logger.info(f"Found {len(results)} semantic search results for query: '{query}'")
            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def parallel_search(self, query: str, top_k: int = 5, rerank: bool = True) -> List[Dict[str, Any]]:
        """
        Perform R1-inspired parallel retrieval using multiple search strategies

        Args:
            query: Search query
            top_k: Number of final results to return
            rerank: Whether to apply cross-encoder reranking

        Returns:
            List of search results with retrieval method metadata
        """
        if not self.enable_parallel or not self.parallel_engine:
            logger.info("Parallel search not enabled, falling back to regular search")
            return self.search(query, top_k, rerank=rerank)

        try:
            return self.parallel_engine.parallel_search(query, top_k, rerank)
        except Exception as e:
            logger.error(f"Parallel search failed: {e}")
            # Fallback to regular search
            return self.search(query, top_k, rerank=rerank)
    
    def _save_cache(self):
        """Save embeddings to cache file"""
        try:
            np.savez_compressed(
                self.cache_file,
                embeddings=self.embeddings,
                documents=np.array(self.documents, dtype=object),
                metadata=np.array(self.metadata, dtype=object),
                loaded_files=np.array(list(self.loaded_files), dtype=object)
            )
            logger.debug(f"Saved {len(self.documents)} documents to cache")
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def load_knowledge_base(self, file_path: str):
        """Load documents from a JSON knowledge base file (with deduplication)"""
        try:
            # Skip if already loaded
            if file_path in self.loaded_files:
                logger.debug(f"Skipping already loaded file: {file_path}")
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = []
            metadata = []
            
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        documents.append(item.get('content', str(item)))
                        metadata.append(item)
                    else:
                        documents.append(str(item))
                        metadata.append({})
            else:
                # Single document
                documents.append(str(data))
                metadata.append({})
            
            self.add_documents(documents, metadata)
            self.loaded_files.add(file_path)
            logger.info(f"Loaded knowledge base from {file_path}: {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Failed to load knowledge base: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the search engine"""
        return {
            "model_name": self.model_name,
            "num_documents": len(self.documents),
            "embedding_dimension": self.embeddings.shape[1] if self.embeddings is not None else 0,
            "is_initialized": self.model is not None,
            "reranker_enabled": self.use_reranker,
            "reranker_model": self.reranker.model_name if self.reranker else None,
            "reranker_initialized": self.reranker and self.reranker.model is not None
        }

class ParallelRetrievalEngine:
    """
    R1-inspired parallel retrieval engine that combines multiple search strategies
    """

    def __init__(self, semantic_engine: SemanticSearchEngine):
        self.semantic_engine = semantic_engine
        self.keyword_engine = KeywordSearchEngine()
        self.expansion_engine = QueryExpansionEngine()

        # Initialize engines with existing documents
        if semantic_engine.documents:
            self.keyword_engine.add_documents(semantic_engine.documents)

    def parallel_search(self, query: str, top_k: int = 5, rerank: bool = True) -> List[Dict[str, Any]]:
        """
        Perform parallel retrieval using multiple strategies

        Args:
            query: Search query
            top_k: Number of final results to return
            rerank: Whether to apply cross-encoder reranking

        Returns:
            List of search results with metadata about retrieval method
        """
        async def search_semantic():
            """Semantic (dense) search"""
            try:
                results = self.semantic_engine.search(query, top_k=top_k*2, rerank=False)
                return [("semantic", result) for result in results]
            except Exception as e:
                logger.warning(f"Semantic search failed: {e}")
                return []

        async def search_keyword():
            """Keyword (sparse) search"""
            try:
                results = self.keyword_engine.search(query, top_k=top_k*2)
                # Convert to result format
                formatted_results = []
                for doc_idx, score in results:
                    formatted_results.append({
                        "document": self.semantic_engine.documents[doc_idx],
                        "similarity": score,
                        "metadata": self.semantic_engine.metadata[doc_idx],
                        "index": doc_idx
                    })
                return [("keyword", result) for result in formatted_results]
            except Exception as e:
                logger.warning(f"Keyword search failed: {e}")
                return []

        async def search_expanded():
            """Search with query expansion"""
            try:
                expanded_queries = self.expansion_engine.expand_query(query, num_expansions=2)
                all_results = []

                for exp_query in expanded_queries[1:]:  # Skip original (already searched)
                    results = self.semantic_engine.search(exp_query, top_k=top_k, rerank=False)
                    all_results.extend([("expanded", result) for result in results])

                return all_results
            except Exception as e:
                logger.warning(f"Expanded search failed: {e}")
                return []

        # Run all searches in parallel
        async def run_parallel_searches():
            tasks = [
                search_semantic(),
                search_keyword(),
                search_expanded()
            ]
            return await asyncio.gather(*tasks, return_exceptions=True)

        # Execute parallel searches
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            results = loop.run_until_complete(run_parallel_searches())
        finally:
            loop.close()

        # Collect and deduplicate results
        all_results = []
        seen_documents = set()

        for search_results in results:
            if isinstance(search_results, Exception):
                continue

            for method, result in search_results:
                doc_text = result["document"]
                if doc_text not in seen_documents:
                    seen_documents.add(doc_text)
                    result_with_method = result.copy()
                    result_with_method["retrieval_method"] = method
                    all_results.append(result_with_method)

        # Apply R1-inspired verification and synthesis to all results
        if all_results:
            verified_results = self._apply_r1_verification(all_results, query, top_k*2)

            # Apply reranking if enabled (on top of verification)
            if rerank and self.semantic_engine.use_reranker:
                try:
                    # Extract documents for reranking
                    candidate_docs = [r["document"] for r in verified_results[:top_k*2]]

                    # Rerank
                    reranked_indices_scores = self.semantic_engine.reranker.rerank(query, candidate_docs, top_k=top_k)

                    # Reorder verified results based on reranking
                    final_results = []
                    for candidate_idx, rerank_score in reranked_indices_scores:
                        if candidate_idx < len(verified_results):
                            result = verified_results[candidate_idx].copy()
                            result["rerank_score"] = float(rerank_score)
                            final_results.append(result)

                    logger.info(f"Parallel retrieval found {len(final_results)} verified + reranked results for query: '{query}'")
                    return final_results

                except Exception as rerank_error:
                    logger.warning(f"Reranking failed in parallel search: {rerank_error}")
                    return verified_results[:top_k]

            else:
                # Return verified results without reranking
                return verified_results[:top_k]

        else:
            final_results = all_results[:top_k]

        logger.info(f"Parallel retrieval found {len(final_results)} results for query: '{query}'")
        return final_results

    def _apply_r1_verification(self, results: List[Dict[str, Any]], query: str, top_k: int) -> List[Dict[str, Any]]:
        """
        Apply R1-inspired multi-perspective verification and synthesis

        Args:
            results: Raw search results
            query: Original query
            top_k: Number of final results to return

        Returns:
            Verified and synthesized results with confidence scores
        """
        if not results:
            return results

        # Calculate confidence scores based on multiple factors
        verified_results = []
        for result in results:
            confidence_score = self._calculate_confidence_score(result, query, results)
            result_copy = result.copy()
            result_copy["confidence_score"] = confidence_score
            verified_results.append(result_copy)

        # Sort by confidence score (combination of rerank score and verification)
        verified_results.sort(key=lambda x: (
            x.get("rerank_score", x.get("similarity", 0)) +  # Primary ranking
            x.get("confidence_score", 0) * 0.5  # Verification boost
        ), reverse=True)

        # Apply synthesis: merge similar results
        synthesized_results = self._synthesize_similar_results(verified_results, query)

        return synthesized_results[:top_k]

    def _calculate_confidence_score(self, result: Dict[str, Any], query: str, all_results: List[Dict[str, Any]]) -> float:
        """
        Calculate confidence score based on multiple verification factors

        Args:
            result: Individual result to verify
            query: Original query
            all_results: All results for cross-validation

        Returns:
            Confidence score between -1.0 and 1.0
        """
        confidence = 0.0

        # Factor 1: Retrieval method diversity (higher if found by multiple methods)
        method_count = sum(1 for r in all_results
                          if r["document"] == result["document"] and
                          r.get("retrieval_method") != result.get("retrieval_method"))
        confidence += min(method_count * 0.2, 0.6)  # Max 0.6 for method diversity

        # Factor 2: Query term coverage (higher if document contains more query terms)
        query_terms = set(re.findall(r'\b\w+\b', query.lower()))
        doc_terms = set(re.findall(r'\b\w+\b', result["document"].lower()))
        coverage = len(query_terms.intersection(doc_terms)) / len(query_terms) if query_terms else 0
        confidence += coverage * 0.3  # Max 0.3 for term coverage

        # Factor 3: Semantic coherence (higher if semantically consistent with query)
        rerank_score = result.get("rerank_score", 0)
        if rerank_score > 0:
            confidence += 0.3  # Positive rerank indicates high coherence
        elif rerank_score < -5:
            confidence -= 0.2  # Very negative rerank indicates low coherence

        # Factor 4: Metadata quality (higher for AI/ML content)
        metadata = result.get("metadata", {})
        if metadata.get("category") == "AI":
            confidence += 0.1

        # Factor 5: Result position stability (higher if consistently ranked high)
        semantic_score = result.get("similarity", 0)
        if semantic_score > 0.8:
            confidence += 0.2

        return max(-1.0, min(1.0, confidence))  # Clamp to [-1, 1]

    def _synthesize_similar_results(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """
        Synthesize similar results to avoid redundancy

        Args:
            results: Results to synthesize
            query: Original query

        Returns:
            Synthesized results with merged information
        """
        if len(results) <= 1:
            return results

        synthesized = []
        used_indices = set()

        for i, result in enumerate(results):
            if i in used_indices:
                continue

            # Find similar results (high semantic similarity)
            similar_indices = []
            for j, other_result in enumerate(results):
                if (i != j and
                    j not in used_indices and
                    result.get("similarity", 0) > 0.7 and
                    other_result.get("similarity", 0) > 0.7):

                    # Check if documents are semantically similar
                    similarity = self._calculate_document_similarity(result["document"], other_result["document"])
                    if similarity > 0.8:
                        similar_indices.append(j)

            if similar_indices:
                # Merge similar results
                merged_result = self._merge_results([result] + [results[j] for j in similar_indices])

                # Mark all as used
                used_indices.update([i] + similar_indices)

                synthesized.append(merged_result)
            else:
                synthesized.append(result)
                used_indices.add(i)

        return synthesized

    def _calculate_document_similarity(self, doc1: str, doc2: str) -> float:
        """Calculate similarity between two documents"""
        try:
            # Use sentence embeddings for similarity
            if hasattr(self.semantic_engine, 'model') and self.semantic_engine.model:
                emb1 = self.semantic_engine.model.encode([doc1[:512]])  # Limit length
                emb2 = self.semantic_engine.model.encode([doc2[:512]])
                from sklearn.metrics.pairwise import cosine_similarity
                return cosine_similarity(emb1, emb2)[0][0]
            else:
                # Fallback: Jaccard similarity on words
                words1 = set(re.findall(r'\b\w+\b', doc1.lower()))
                words2 = set(re.findall(r'\b\w+\b', doc2.lower()))
                intersection = len(words1.intersection(words2))
                union = len(words1.union(words2))
                return intersection / union if union > 0 else 0.0
        except Exception:
            return 0.0

    def _merge_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple similar results into one"""
        if not results:
            return {}

        # Use the highest-scoring result as base
        base_result = max(results, key=lambda x: (
            x.get("rerank_score", x.get("similarity", 0)) +
            x.get("confidence_score", 0)
        ))

        merged = base_result.copy()

        # Collect all retrieval methods
        all_methods = set()
        for result in results:
            method = result.get("retrieval_method", "unknown")
            all_methods.add(method)

        merged["retrieval_methods"] = list(all_methods)
        merged["merged_count"] = len(results)
        merged["merged_from"] = [r.get("retrieval_method", "unknown") for r in results]

        # Average confidence scores
        confidences = [r.get("confidence_score", 0) for r in results]
        merged["confidence_score"] = sum(confidences) / len(confidences) if confidences else 0

        return merged


# Global search engine instance
_search_engine = None

def get_search_engine() -> SemanticSearchEngine:
    """Get the global search engine instance"""
    global _search_engine
    if _search_engine is None:
        _search_engine = SemanticSearchEngine()
        _search_engine.initialize()
    return _search_engine

def search_documents(query: str, top_k: int = 5, min_similarity: float = 0.0, rerank: bool = True, parallel: bool = False) -> List[Dict[str, Any]]:
    """Convenience function for document search with optional reranking and parallel retrieval"""
    engine = get_search_engine()
    if parallel:
        return engine.parallel_search(query, top_k, rerank)
    else:
        return engine.search(query, top_k, min_similarity, rerank)

def add_documents_to_index(documents: List[str], metadata: List[Dict[str, Any]] = None):
    """Convenience function for adding documents"""
    engine = get_search_engine()
    engine.add_documents(documents, metadata)

def load_knowledge_base(file_path: str):
    """Convenience function for loading knowledge base"""
    engine = get_search_engine()
    engine.load_knowledge_base(file_path)
