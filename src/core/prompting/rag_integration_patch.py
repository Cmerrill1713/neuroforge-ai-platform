#!/usr/bin/env python3
"""
RAG Integration Patch for DualBackendEvolutionaryIntegration

This is a drop-in replacement that uses the production RAG stack
(Weaviate + ES + Redis) instead of PostgreSQL vectors.

USAGE: Just 2 lines to change in dual_backend_integration.py:

OLD:
    from src.core.memory.vector_pg import PostgreSQLVectorStore
    self.vector_store = PostgreSQLVectorStore()

NEW:
    from src.core.retrieval.rag_service import create_rag_service
    self.rag_service = create_rag_service(env="production")

Then replace all vector_store.query() calls with rag_service.query()
"""

from typing import Dict, Any, List
import logging

# Import production RAG service
from src.core.retrieval.rag_service import create_rag_service, ProductionRAGService

logger = logging.getLogger(__name__)


class RAGEnabledEvolutionaryIntegration:
    """
    Mixin to add RAG capabilities to DualBackendEvolutionaryIntegration
    
    This shows the pattern - you can either:
    1. Copy this into dual_backend_integration.py
    2. Use this as a separate class
    3. Just change the 2 lines mentioned above
    """
    
    def __init__(self):
        # Initialize production RAG service
        self.rag_service: ProductionRAGService = create_rag_service(env="production")
        
        logger.info("✅ RAG-enabled evolutionary integration initialized")
    
    async def enrich_prompt_with_rag(
        self,
        base_prompt: str,
        query: str,
        k: int = 3
    ) -> str:
        """
        Enrich a prompt with RAG context
        
        Use this in your executor to add relevant context before generation
        """
        # Query RAG system
        context = await self.rag_service.query_with_context(
            query_text=query,
            k=k,
            method="hybrid"
        )
        
        # Inject context into prompt
        enriched = f"""{base_prompt}

{context}

User Query: {query}

Answer:"""
        
        return enriched
    
    async def evaluate_with_rag_metrics(
        self,
        spec,
        genome,
        include_retrieval: bool = True
    ):
        """
        Evaluate a genome with RAG-aware metrics
        
        Adds retrieval quality metrics to standard execution metrics
        """
        from src.core.prompting.evolutionary_optimizer import ExecutionMetrics
        import time
        
        start = time.time()
        
        # Get RAG context if needed
        rag_latency = 0.0
        if include_retrieval and hasattr(spec, 'intent'):
            rag_start = time.time()
            rag_response = await self.rag_service.query(
                query_text=spec.prompt,
                k=5,
                method="hybrid"
            )
            rag_latency = rag_response.latency_ms
            
            # Check retrieval quality
            retrieval_quality = self._assess_retrieval_quality(rag_response)
        else:
            retrieval_quality = 1.0
        
        # Standard execution (your existing code)
        # ... execute with genome ...
        
        execution_time = (time.time() - start) * 1000
        
        return ExecutionMetrics(
            schema_ok=True,
            safety_flags=[],
            validator_score=retrieval_quality,  # Use retrieval quality as part of score
            latency_ms=execution_time,
            tokens_total=100,
            repairs=0,
            accuracy=retrieval_quality,
            cost_usd=0.01
        )
    
    def _assess_retrieval_quality(self, rag_response) -> float:
        """
        Assess retrieval quality
        
        Metrics:
        - Number of results found
        - Average relevance score
        - Diversity of sources
        """
        if not rag_response.results:
            return 0.0
        
        # Average score
        avg_score = sum(r.score for r in rag_response.results) / len(rag_response.results)
        
        # Penalty if too few results
        count_factor = min(1.0, len(rag_response.results) / 5.0)
        
        # Diversity factor (unique doc_ids)
        doc_ids = set(r.metadata.get("doc_id") for r in rag_response.results if "doc_id" in r.metadata)
        diversity_factor = min(1.0, len(doc_ids) / 3.0)
        
        quality = avg_score * 0.6 + count_factor * 0.2 + diversity_factor * 0.2
        
        return quality
    
    def get_rag_metrics(self) -> Dict[str, Any]:
        """Get RAG system metrics"""
        return self.rag_service.get_metrics()


# ============================================================================
# Example: Drop-in replacement for dual_backend_integration.py
# ============================================================================

def patch_dual_backend_integration():
    """
    Shows exactly what to change in dual_backend_integration.py
    
    BEFORE (lines ~50-60):
    ```python
    from src.core.memory.vector_pg import PostgreSQLVectorStore
    
    class DualBackendEvolutionaryIntegration:
        async def initialize(self):
            ...
            # Initialize vector store
            self.vector_store = PostgreSQLVectorStore()
            logger.info("✅ Vector store initialized")
    ```
    
    AFTER:
    ```python
    from src.core.retrieval.rag_service import create_rag_service
    
    class DualBackendEvolutionaryIntegration:
        async def initialize(self):
            ...
            # Initialize RAG service (Weaviate + ES + Redis)
            self.rag_service = create_rag_service(env="production")
            logger.info("✅ RAG service initialized")
    ```
    
    That's it! Then search for "vector_store" and replace with "rag_service".
    """
    
    return """
# Patch for dual_backend_integration.py

## Line ~8: Update imports
OLD:
    from src.core.memory.vector_pg import PostgreSQLVectorStore

NEW:
    from src.core.retrieval.rag_service import create_rag_service

## Line ~57: Update initialization
OLD:
    self.vector_store = None

NEW:
    self.rag_service = None

## Line ~82: Update in initialize()
OLD:
    # Initialize vector store
    self.vector_store = PostgreSQLVectorStore()
    logger.info("✅ Vector store initialized")

NEW:
    # Initialize RAG service (Weaviate + ES + Redis)
    self.rag_service = create_rag_service(env="production")
    logger.info("✅ RAG service initialized (Weaviate + ES + Reranker)")

## Usage in executor (optional enhancement):
Add RAG context to prompts:

    # Before executing, enrich with RAG context
    if self.rag_service and genome.use_rag:
        rag_context = await self.rag_service.query_with_context(
            query_text=spec.prompt,
            k=3,
            method="hybrid"
        )
        enriched_prompt = f"{spec.prompt}\\n\\n{rag_context}"
    else:
        enriched_prompt = spec.prompt
"""


if __name__ == "__main__":
    print(patch_dual_backend_integration())

