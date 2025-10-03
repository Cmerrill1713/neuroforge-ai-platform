#!/usr/bin/env python3
"""
Dual Backend Integration for Evolutionary Prompt Optimizer
Integrates with BOTH backend systems:
1. Primary FastAPI Backend (Port 8000) - api_server.py
2. Consolidated API (Port 8004) - consolidated_api_architecture.py

Ensures evolutionary optimization works across your entire architecture.
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import evolutionary optimizer
from src.core.prompting.evolutionary_optimizer import (
    EvolutionaryPromptOptimizer,
    Genome,
    ExecutionMetrics,
    PromptSpec,
    ThompsonBandit,
    NL2Prompt
)

# Import existing backend components
try:
    from src.core.engines.ollama_adapter import OllamaAdapter
    from src.core.orchestration.intelligent_orchestrator import IntelligentOrchestrator
    from src.core.agents.enhanced_agent_selector import EnhancedAgentSelector
    from src.core.retrieval.rag_service import create_rag_service  # ← RAG integration
    from src.core.prompting.mipro_optimizer import MIPROPromptOptimizer
    CORE_AVAILABLE = True
except ImportError as e:
    CORE_AVAILABLE = False
    logging.warning(f"Core components not fully available: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DualBackendEvolutionaryIntegration:
    """
    Integrates evolutionary prompt optimization with BOTH backend systems.
    
    Features:
    - Works with Primary API (Port 8000) AND Consolidated API (Port 8004)
    - Connects to existing IntelligentOrchestrator
    - Uses EnhancedAgentSelector for routing
    - Integrates with PostgreSQL vector store
    - Combines MIPROv2 + Evolutionary optimization
    """
    
    def __init__(
        self,
        primary_api_url: str = "http://localhost:8000",
        consolidated_api_url: str = "http://localhost:8004"
    ):
        self.primary_api_url = primary_api_url
        self.consolidated_api_url = consolidated_api_url
        
        # Backend selection
        self.use_primary = True  # Default to primary
        
        # Core components
        self.ollama_adapter = None
        self.orchestrator = None
        self.agent_selector = None
        self.rag_service = None  # ← RAG service (replaces vector_store)
        self.mipro = None
        
        # Evolutionary optimizer
        self.evolutionary = EvolutionaryPromptOptimizer(
            population_size=12,
            survivors=6,
            eval_samples=64
        )
        
        # Production bandit
        self.bandit: Optional[ThompsonBandit] = None
        
        # Metrics tracking
        self.execution_history: List[Dict[str, Any]] = []
        
        logger.info("🔄 Dual Backend Evolutionary Integration initialized")
    
    async def initialize(self):
        """Initialize all backend components"""
        logger.info("🚀 Initializing backend components...")
        
        try:
            # Initialize Ollama adapter for direct model access
            self.ollama_adapter = OllamaAdapter()
            logger.info("✅ Ollama adapter initialized")
            
            # Initialize orchestrator
            if CORE_AVAILABLE:
                self.orchestrator = IntelligentOrchestrator()
                logger.info("✅ Intelligent orchestrator initialized")
                
                # Initialize agent selector
                self.agent_selector = EnhancedAgentSelector()
                logger.info("✅ Enhanced agent selector initialized")
                
                # Initialize RAG service (Weaviate + ES + Redis)
                self.rag_service = create_rag_service(env="development")
                logger.info("✅ RAG service initialized (Weaviate + ES + Reranker)")
                
                # Initialize MIPROv2
                self.mipro = MIPROPromptOptimizer()
                logger.info("✅ MIPROv2 optimizer initialized")
            
            logger.info("✅ All components initialized")
            
        except Exception as e:
            logger.error(f"❌ Initialization error: {e}")
            raise
    
    def set_backend(self, use_primary: bool = True):
        """Switch between primary and consolidated API"""
        self.use_primary = use_primary
        backend = "Primary (8000)" if use_primary else "Consolidated (8004)"
        logger.info(f"🔄 Switched to {backend} backend")
    
    async def executor_primary_api(
        self, 
        spec: PromptSpec, 
        genome: Genome
    ) -> ExecutionMetrics:
        """
        Execute via Primary API (Port 8000) - api_server.py
        Uses direct model access via OllamaAdapter
        """
        start = time.time()
        
        try:
            # Execute using Ollama adapter directly
            response = await self.ollama_adapter.generate_response(
                model_key=genome.model_key,
                prompt=spec.prompt,
                max_tokens=genome.max_tokens,
                temperature=genome.temp
            )
            
            latency_ms = (time.time() - start) * 1000
            
            # Validate response
            schema_ok = self._validate_schema(response, spec)
            safety_flags = self._check_safety(response)
            quality_score = self._calculate_quality(response)
            
            # Calculate tokens and cost
            tokens = response.tokens_used if hasattr(response, 'tokens_used') else len(response.text.split()) * 1.5
            cost = self._calculate_cost(tokens)
            
            return ExecutionMetrics(
                schema_ok=schema_ok,
                safety_flags=safety_flags,
                validator_score=quality_score,
                latency_ms=latency_ms,
                tokens_total=int(tokens),
                repairs=0 if schema_ok else 1,
                accuracy=quality_score,
                cost_usd=cost
            )
            
        except Exception as e:
            logger.error(f"Primary API execution error: {e}")
            return ExecutionMetrics(
                schema_ok=False,
                safety_flags=["execution_error"],
                validator_score=0.0,
                latency_ms=(time.time() - start) * 1000,
                tokens_total=0,
                repairs=1,
                accuracy=0.0,
                cost_usd=0.0
            )
    
    async def executor_consolidated_api(
        self,
        spec: PromptSpec,
        genome: Genome
    ) -> ExecutionMetrics:
        """
        Execute via Consolidated API (Port 8004) - consolidated_api_architecture.py
        Uses EnhancedAgentSelector and full orchestration
        """
        start = time.time()
        
        try:
            # Build task request for agent selector
            task_request = {
                "task_type": spec.intent,
                "content": spec.prompt,
                "latency_requirement": 1000,
                "input_type": "text"
            }
            
            # Use agent selector
            selection_result = await self.agent_selector.select_best_agent_with_reasoning(
                task_request
            )
            
            # Execute with orchestrator if available
            if self.orchestrator:
                result = await self.orchestrator.execute_task({
                    "prompt": spec.prompt,
                    "model": genome.model_key,
                    "temperature": genome.temp,
                    "max_tokens": genome.max_tokens,
                    "use_consensus": genome.use_consensus
                })
            else:
                # Fallback to direct model access
                result = await self.ollama_adapter.generate_response(
                    model_key=genome.model_key,
                    prompt=spec.prompt,
                    max_tokens=genome.max_tokens,
                    temperature=genome.temp
                )
            
            latency_ms = (time.time() - start) * 1000
            
            # Validate and score
            schema_ok = self._validate_schema(result, spec)
            safety_flags = self._check_safety(result)
            quality_score = selection_result.get("confidence", 0.8)
            
            tokens = result.get("tokens_used", len(str(result).split()) * 1.5)
            cost = self._calculate_cost(tokens)
            
            return ExecutionMetrics(
                schema_ok=schema_ok,
                safety_flags=safety_flags,
                validator_score=quality_score,
                latency_ms=latency_ms,
                tokens_total=int(tokens),
                repairs=0 if schema_ok else 1,
                accuracy=quality_score,
                cost_usd=cost
            )
            
        except Exception as e:
            logger.error(f"Consolidated API execution error: {e}")
            return ExecutionMetrics(
                schema_ok=False,
                safety_flags=["execution_error"],
                validator_score=0.0,
                latency_ms=(time.time() - start) * 1000,
                tokens_total=0,
                repairs=1,
                accuracy=0.0,
                cost_usd=0.0
            )
    
    async def executor(self, spec: PromptSpec, genome: Genome) -> ExecutionMetrics:
        """
        Unified executor - routes to appropriate backend
        """
        if self.use_primary:
            return await self.executor_primary_api(spec, genome)
        else:
            return await self.executor_consolidated_api(spec, genome)
    
    def _validate_schema(self, result: Any, spec: PromptSpec) -> bool:
        """Validate result matches expected schema"""
        try:
            if not result:
                return False
            
            # Check based on spec constraints
            if hasattr(result, 'content'):
                content = result.content
            elif isinstance(result, dict):
                content = result.get("content", result.get("response", ""))
            else:
                content = str(result)
            
            # Basic validation
            if len(content) < 10:
                return False
            
            # Check required fields from spec
            required_fields = spec.constraints.get("required_fields", [])
            if isinstance(result, dict):
                return all(field in result for field in required_fields)
            
            return True
            
        except Exception:
            return False
    
    def _check_safety(self, result: Any) -> List[str]:
        """Check for safety issues"""
        flags = []
        
        try:
            content = ""
            if hasattr(result, 'content'):
                content = result.content
            elif isinstance(result, dict):
                content = result.get("content", result.get("response", ""))
            else:
                content = str(result)
            
            content_lower = content.lower()
            
            # Basic safety checks
            if any(word in content_lower for word in ["error", "exception", "failed"]):
                flags.append("error_in_output")
            
            if len(content) < 10:
                flags.append("output_too_short")
            
            if "unsafe" in content_lower or "harmful" in content_lower:
                flags.append("safety_concern")
                
        except Exception:
            flags.append("validation_error")
        
        return flags
    
    def _calculate_quality(self, result: Any) -> float:
        """Calculate quality score"""
        try:
            # Extract quality metrics
            if isinstance(result, dict):
                quality = result.get("quality_metrics", {})
                score = quality.get("overall_score", 0.8)
                confidence = result.get("confidence", 1.0)
                return min(1.0, score * confidence)
            
            # Heuristic: longer responses are generally better (to a point)
            if hasattr(result, 'content'):
                length = len(result.content)
            else:
                length = len(str(result))
            
            # Score based on length (optimal ~500-2000 chars)
            if length < 50:
                return 0.3
            elif length < 200:
                return 0.6
            elif length < 1000:
                return 0.9
            elif length < 3000:
                return 0.95
            else:
                return 0.8  # Too long
                
        except Exception:
            return 0.5
    
    def _calculate_cost(self, tokens: float) -> float:
        """Calculate execution cost in USD"""
        # Ollama is free, but estimate opportunity cost
        # Assume $0.01 per 1K tokens equivalent
        cost_per_1k = 0.01
        return (tokens / 1000) * cost_per_1k
    
    async def optimize_comprehensive(
        self,
        base_prompt: str,
        golden_dataset: List[Dict[str, Any]],
        num_generations: int = 10,
        use_mipro: bool = True
    ) -> Genome:
        """
        Full optimization pipeline:
        1. MIPROv2 optimizes prompt text (optional)
        2. Evolutionary optimizes hyperparameters
        3. Tests on both backends
        4. Returns best genome
        """
        logger.info("🚀 Starting comprehensive dual-backend optimization")
        
        # Phase 1: MIPROv2 (if enabled)
        optimized_prompt_text = base_prompt
        
        if use_mipro and self.mipro:
            logger.info("📝 Phase 1: MIPROv2 prompt optimization")
            try:
                # Convert dataset
                mipro_dataset = self._convert_to_mipro_format(golden_dataset)
                
                mipro_result = await self.mipro.optimize_prompt(
                    prompt=base_prompt,
                    dataset=mipro_dataset
                )
                
                optimized_prompt_text = mipro_result.get("optimized_prompt", base_prompt)
                logger.info(f"✅ MIPROv2 complete")
            except Exception as e:
                logger.warning(f"MIPROv2 failed, using base prompt: {e}")
        
        # Phase 2: Evolutionary optimization on PRIMARY backend
        logger.info("🧬 Phase 2a: Evolutionary optimization (Primary API)")
        self.set_backend(use_primary=True)
        
        base_genome = Genome(
            rubric=optimized_prompt_text,
            cot=True,
            temp=0.7,
            max_tokens=2048,
            retriever_topk=5,
            use_consensus=False,
            model_key="llama3.2:3b"
        )
        
        best_genome_primary = await self.evolutionary.optimize(
            trainset=golden_dataset,
            executor=self.executor,
            num_generations=num_generations,
            base_config=base_genome,
            early_stop_threshold=0.95
        )
        
        primary_score = self.evolutionary.best_genomes[-1][0]
        logger.info(f"✅ Primary API optimization: score={primary_score:.4f}")
        
        # Phase 3: Test on CONSOLIDATED backend
        logger.info("🧬 Phase 2b: Testing on Consolidated API")
        self.set_backend(use_primary=False)
        
        # Re-evaluate best genome on consolidated API
        consolidated_score = await self.evolutionary.evaluate_genome(
            best_genome_primary,
            golden_dataset,
            self.executor
        )
        
        logger.info(f"✅ Consolidated API test: score={consolidated_score:.4f}")
        
        # Choose best
        if consolidated_score > primary_score:
            logger.info("🎉 Consolidated API performed better!")
            final_genome = best_genome_primary
            self.set_backend(use_primary=False)
        else:
            logger.info("🎉 Primary API performed better!")
            final_genome = best_genome_primary
            self.set_backend(use_primary=True)
        
        # Save results
        results_path = Path(f"results/dual_backend_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        results_path.parent.mkdir(exist_ok=True)
        
        self.evolutionary.save_results(results_path)
        
        # Add backend comparison
        comparison = {
            "primary_api_score": primary_score,
            "consolidated_api_score": consolidated_score,
            "best_backend": "primary" if primary_score >= consolidated_score else "consolidated",
            "final_genome": {
                "genome_id": final_genome.genome_id,
                "rubric": final_genome.rubric[:200] + "...",
                "temp": final_genome.temp,
                "max_tokens": final_genome.max_tokens,
                "model_key": final_genome.model_key
            }
        }
        
        comparison_path = results_path.with_name(f"backend_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        comparison_path.write_text(json.dumps(comparison, indent=2))
        
        logger.info(f"💾 Results saved to {results_path}")
        
        return final_genome
    
    def _convert_to_mipro_format(self, golden_dataset: List[Dict]) -> List[Dict]:
        """Convert golden dataset to MIPROv2 format"""
        return [
            {
                "input": ex.get("query", ""),
                "output": ex.get("expected_output", ""),
                "context": ex.get("context", "")
            }
            for ex in golden_dataset
        ]
    
    def deploy_to_production(
        self,
        top_genomes: List[Genome],
        backend: str = "auto"
    ):
        """
        Deploy optimized genomes to production with bandit routing
        
        Args:
            top_genomes: Top N genomes from evolution
            backend: "primary", "consolidated", or "auto"
        """
        logger.info(f"🚀 Deploying {len(top_genomes)} genomes to production")
        
        # Set backend
        if backend == "primary":
            self.set_backend(use_primary=True)
        elif backend == "consolidated":
            self.set_backend(use_primary=False)
        # else: auto (keep current)
        
        # Initialize bandit
        self.bandit = ThompsonBandit(top_genomes)
        
        logger.info(f"✅ Deployed on {backend} backend with bandit routing")
    
    async def production_route(
        self,
        user_query: str,
        context: str = "",
        intent: str = "text_generation"
    ) -> Dict[str, Any]:
        """
        Production routing with bandit learning
        Works with both backends
        """
        if self.bandit is None:
            raise ValueError("Bandit not deployed. Call deploy_to_production() first.")
        
        # Bandit chooses genome
        genome = self.bandit.choose()
        
        backend = "Primary" if self.use_primary else "Consolidated"
        logger.info(f"🎯 Bandit chose genome {genome.genome_id[:8]}... on {backend} backend")
        
        # Create spec
        spec = PromptSpec(
            intent=intent,
            prompt=f"{genome.rubric}\n\nQuery: {user_query}",
            tools=[],
            constraints={"max_tokens": genome.max_tokens},
            metadata={"genome_id": genome.genome_id}
        )
        
        # Execute
        metrics = await self.executor(spec, genome)
        
        # Calculate reward
        reward = self._calculate_reward(metrics)
        
        # Update bandit
        self.bandit.update(genome.genome_id, reward)
        
        # Track history
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "genome_id": genome.genome_id,
            "backend": backend,
            "metrics": metrics.dict(),
            "reward": reward
        })
        
        return {
            "response": "...",  # Your actual response
            "genome_id": genome.genome_id,
            "backend": backend,
            "metrics": metrics.dict(),
            "reward": reward
        }
    
    def _calculate_reward(self, metrics: ExecutionMetrics) -> float:
        """Calculate reward for bandit (0 to 1)"""
        if not metrics.schema_ok or metrics.safety_flags:
            return 0.0
        
        # Multi-objective reward
        reward = metrics.validator_score * 0.4  # Quality
        reward += (1.0 - min(1.0, metrics.latency_ms / 2000)) * 0.3  # Speed
        reward += (1.0 - min(1.0, metrics.cost_usd / 0.05)) * 0.2  # Cost
        reward += (1.0 if metrics.repairs == 0 else 0.0) * 0.1  # Robustness
        
        return max(0.0, min(1.0, reward))
    
    def get_bandit_stats(self) -> Dict[str, Any]:
        """Get bandit statistics across both backends"""
        if not self.bandit:
            return {"error": "Bandit not initialized"}
        
        stats = self.bandit.get_stats()
        
        # Add backend info
        stats["current_backend"] = "primary" if self.use_primary else "consolidated"
        stats["execution_history_count"] = len(self.execution_history)
        
        return stats


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def demo_dual_backend():
    """Demonstrate dual backend integration"""
    
    integration = DualBackendEvolutionaryIntegration()
    
    # Initialize
    await integration.initialize()
    
    # Golden dataset
    golden_dataset = [
        {
            "query": "Write a Python function to sort a list",
            "expected_output": "def sort_list(lst): return sorted(lst)",
            "context": "coding task",
        },
        {
            "query": "Explain quantum computing",
            "expected_output": "Quantum computing uses quantum mechanics...",
            "context": "explanation",
        },
    ] * 10
    
    # Optimize on BOTH backends
    logger.info("\n" + "="*80)
    logger.info("DUAL BACKEND OPTIMIZATION DEMO")
    logger.info("="*80 + "\n")
    
    best_genome = await integration.optimize_comprehensive(
        base_prompt="You are a helpful AI assistant.",
        golden_dataset=golden_dataset,
        num_generations=3,  # Quick demo
        use_mipro=False  # Skip MIPROv2 for speed
    )
    
    logger.info(f"\n✅ Optimization complete!")
    logger.info(f"   Best genome: {best_genome.genome_id}")
    logger.info(f"   Temperature: {best_genome.temp}")
    logger.info(f"   Model: {best_genome.model_key}")
    
    # Deploy
    top_genomes = [
        genome for _, genome in 
        sorted(integration.evolutionary.best_genomes, reverse=True)[:3]
    ]
    
    integration.deploy_to_production(top_genomes, backend="auto")
    
    # Test production routing
    logger.info("\n" + "="*80)
    logger.info("TESTING PRODUCTION ROUTING")
    logger.info("="*80 + "\n")
    
    for i in range(5):
        result = await integration.production_route(
            user_query=f"Test query {i+1}",
            context="test"
        )
        logger.info(f"   Request {i+1}: backend={result['backend']}, reward={result['reward']:.3f}")
    
    # Stats
    stats = integration.get_bandit_stats()
    logger.info(f"\n📊 Final Stats: {len(stats)} genomes tracked")


if __name__ == "__main__":
    asyncio.run(demo_dual_backend())

