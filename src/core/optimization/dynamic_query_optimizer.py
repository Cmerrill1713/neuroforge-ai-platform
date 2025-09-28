#!/usr/bin/env python3
"""
Dynamic Query Optimizer
AI-generated query randomization and optimization system
Based on HRM-enhanced AI model suggestions from continuous improvement loop
"""

import asyncio
import logging
import time
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class OptimizationStrategy(str, Enum):
    """Different optimization strategies."""
    RANDOM_VARIATION = "random_variation"
    PATTERN_LEARNING = "pattern_learning"
    CHAOS_DRIVEN = "chaos_driven"
    QUANTUM_SUPERPOSITION = "quantum_superposition"
    ADAPTIVE_LEARNING = "adaptive_learning"

class QueryType(str, Enum):
    """Types of queries to optimize."""
    SIMILARITY_SEARCH = "similarity_search"
    EXACT_MATCH = "exact_match"
    RANGE_QUERY = "range_query"
    COMPLEX_FILTER = "complex_filter"
    AGGREGATION = "aggregation"

@dataclass
class QueryPattern:
    """Represents a learned query pattern."""
    pattern_id: str
    query_type: QueryType
    parameters: Dict[str, Any]
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    success_rate: float = 0.0
    avg_response_time: float = 0.0
    usage_count: int = 0
    last_used: float = field(default_factory=time.time)
    optimization_history: List[Dict] = field(default_factory=list)

@dataclass
class OptimizationResult:
    """Result of a query optimization."""
    original_query: Dict[str, Any]
    optimized_query: Dict[str, Any]
    strategy_used: OptimizationStrategy
    expected_improvement: float
    confidence_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class DynamicQueryOptimizer:
    """
    AI-driven query optimizer that learns from patterns and applies
    various optimization strategies including chaos theory and quantum reasoning.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Pattern storage
        self.query_patterns: Dict[str, QueryPattern] = {}
        self.performance_history = deque(maxlen=self.config.get("max_history", 1000))
        
        # Optimization strategies
        self.strategies = {
            OptimizationStrategy.RANDOM_VARIATION: self._random_variation_optimization,
            OptimizationStrategy.PATTERN_LEARNING: self._pattern_learning_optimization,
            OptimizationStrategy.CHAOS_DRIVEN: self._chaos_driven_optimization,
            OptimizationStrategy.QUANTUM_SUPERPOSITION: self._quantum_superposition_optimization,
            OptimizationStrategy.ADAPTIVE_LEARNING: self._adaptive_learning_optimization,
        }
        
        # Learning parameters
        self.learning_rate = self.config.get("learning_rate", 0.1)
        self.chaos_factor = self.config.get("chaos_factor", 0.15)
        self.quantum_states = self.config.get("quantum_states", 5)
        
        # Performance tracking
        self.optimization_stats = {
            "total_optimizations": 0,
            "successful_optimizations": 0,
            "avg_improvement": 0.0,
            "strategy_performance": defaultdict(list)
        }
    
    def _default_config(self) -> Dict:
        return {
            "max_history": 1000,
            "learning_rate": 0.1,
            "chaos_factor": 0.15,
            "quantum_states": 5,
            "min_pattern_usage": 3,
            "optimization_threshold": 0.1,
            "confidence_threshold": 0.7,
            "enable_chaos_optimization": True,
            "enable_quantum_optimization": True,
            "pattern_decay_factor": 0.95,
            "max_optimization_attempts": 3
        }
    
    async def optimize_query(
        self, 
        query: Dict[str, Any], 
        query_type: QueryType,
        context: Optional[Dict] = None
    ) -> OptimizationResult:
        """
        Optimize a query using AI-driven strategies.
        """
        start_time = time.time()
        context = context or {}
        
        # Generate query signature for pattern matching
        query_signature = self._generate_query_signature(query, query_type)
        
        # Select optimization strategy
        strategy = self._select_optimization_strategy(query_signature, context)
        
        # Apply optimization
        optimized_query = await self.strategies[strategy](query, query_type, context)
        
        # Calculate expected improvement
        expected_improvement = self._estimate_improvement(query, optimized_query, query_type)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence(strategy, query_signature)
        
        # Create optimization result
        result = OptimizationResult(
            original_query=query.copy(),
            optimized_query=optimized_query,
            strategy_used=strategy,
            expected_improvement=expected_improvement,
            confidence_score=confidence_score,
            metadata={
                "query_signature": query_signature,
                "optimization_time": time.time() - start_time,
                "context": context
            }
        )
        
        # Update statistics
        self.optimization_stats["total_optimizations"] += 1
        
        return result
    
    def _generate_query_signature(self, query: Dict[str, Any], query_type: QueryType) -> str:
        """Generate a signature for query pattern matching."""
        # Create a simplified signature based on query structure
        signature_parts = [query_type.value]
        
        # Add key parameters
        if "limit" in query:
            signature_parts.append(f"limit_{query['limit']}")
        if "threshold" in query:
            signature_parts.append(f"threshold_{query['threshold']:.2f}")
        if "filters" in query:
            signature_parts.append(f"filters_{len(query['filters'])}")
        
        # Add vector characteristics if present
        if "vector" in query and isinstance(query["vector"], (list, np.ndarray)):
            vector = np.array(query["vector"])
            signature_parts.append(f"dim_{len(vector)}")
            signature_parts.append(f"norm_{np.linalg.norm(vector):.2f}")
        
        return "_".join(signature_parts)
    
    def _select_optimization_strategy(
        self, 
        query_signature: str, 
        context: Dict
    ) -> OptimizationStrategy:
        """Select the best optimization strategy for a query."""
        
        # Check if we have learned patterns for this query type
        if query_signature in self.query_patterns:
            pattern = self.query_patterns[query_signature]
            
            # Use pattern learning if we have enough data
            if pattern.usage_count >= self.config["min_pattern_usage"]:
                return OptimizationStrategy.PATTERN_LEARNING
        
        # Use chaos-driven optimization for exploration
        if (self.config["enable_chaos_optimization"] and 
            random.random() < self.chaos_factor):
            return OptimizationStrategy.CHAOS_DRIVEN
        
        # Use quantum superposition for complex queries
        if (self.config["enable_quantum_optimization"] and 
            context.get("complexity", "medium") == "high"):
            return OptimizationStrategy.QUANTUM_SUPERPOSITION
        
        # Default to adaptive learning
        return OptimizationStrategy.ADAPTIVE_LEARNING
    
    async def _random_variation_optimization(
        self, 
        query: Dict[str, Any], 
        query_type: QueryType, 
        context: Dict
    ) -> Dict[str, Any]:
        """Apply random variations to query parameters."""
        optimized_query = query.copy()
        
        # Apply random variations based on query type
        if query_type == QueryType.SIMILARITY_SEARCH:
            # Vary threshold slightly
            if "threshold" in optimized_query:
                variation = random.uniform(-0.05, 0.05)
                optimized_query["threshold"] = max(0.0, min(1.0, 
                    optimized_query["threshold"] + variation))
            
            # Vary limit slightly
            if "limit" in optimized_query:
                variation = random.randint(-2, 2)
                optimized_query["limit"] = max(1, optimized_query["limit"] + variation)
        
        elif query_type == QueryType.RANGE_QUERY:
            # Vary range bounds
            if "range" in optimized_query:
                range_val = optimized_query["range"]
                if isinstance(range_val, dict) and "min" in range_val and "max" in range_val:
                    range_size = range_val["max"] - range_val["min"]
                    variation = range_size * 0.1 * random.uniform(-1, 1)
                    optimized_query["range"]["min"] += variation
                    optimized_query["range"]["max"] += variation
        
        return optimized_query
    
    async def _pattern_learning_optimization(
        self, 
        query: Dict[str, Any], 
        query_type: QueryType, 
        context: Dict
    ) -> Dict[str, Any]:
        """Optimize based on learned patterns."""
        query_signature = self._generate_query_signature(query, query_type)
        
        if query_signature not in self.query_patterns:
            # No pattern learned yet, use adaptive learning
            return await self._adaptive_learning_optimization(query, query_type, context)
        
        pattern = self.query_patterns[query_signature]
        optimized_query = query.copy()
        
        # Apply learned optimizations
        for param, optimization in pattern.optimization_history[-3:]:  # Use last 3 optimizations
            if param in optimized_query and "improvement" in optimization:
                if optimization["improvement"] > 0:
                    # Apply successful optimization
                    optimized_query[param] = optimization["optimized_value"]
        
        return optimized_query
    
    async def _chaos_driven_optimization(
        self, 
        query: Dict[str, Any], 
        query_type: QueryType, 
        context: Dict
    ) -> Dict[str, Any]:
        """Apply chaos theory-inspired optimizations."""
        optimized_query = query.copy()
        
        # Apply chaotic variations
        chaos_intensity = self.chaos_factor * random.random()
        
        if query_type == QueryType.SIMILARITY_SEARCH:
            # Chaotic threshold adjustment
            if "threshold" in optimized_query:
                # Use logistic map for chaotic behavior
                x = random.random()
                r = 3.8 + 0.2 * chaos_intensity  # Chaotic parameter
                chaotic_value = r * x * (1 - x)
                
                threshold_adjustment = (chaotic_value - 0.5) * 0.2  # Scale to reasonable range
                optimized_query["threshold"] = max(0.0, min(1.0, 
                    optimized_query["threshold"] + threshold_adjustment))
            
            # Chaotic vector perturbation
            if "vector" in optimized_query:
                vector = np.array(optimized_query["vector"])
                
                # Apply chaotic noise
                noise_scale = chaos_intensity * 0.01
                chaotic_noise = np.random.normal(0, noise_scale, vector.shape)
                
                perturbed_vector = vector + chaotic_noise
                perturbed_vector = perturbed_vector / np.linalg.norm(perturbed_vector)  # Normalize
                
                optimized_query["vector"] = perturbed_vector.tolist()
        
        return optimized_query
    
    async def _quantum_superposition_optimization(
        self, 
        query: Dict[str, Any], 
        query_type: QueryType, 
        context: Dict
    ) -> Dict[str, Any]:
        """Apply quantum superposition-inspired optimization."""
        
        # Generate multiple quantum states (different optimization approaches)
        quantum_states = []
        
        for i in range(self.quantum_states):
            state_query = query.copy()
            
            # Each quantum state represents a different optimization approach
            if query_type == QueryType.SIMILARITY_SEARCH:
                # State 1: Optimize for precision
                if i == 0 and "threshold" in state_query:
                    state_query["threshold"] = min(1.0, state_query["threshold"] + 0.1)
                
                # State 2: Optimize for recall
                elif i == 1 and "threshold" in state_query:
                    state_query["threshold"] = max(0.0, state_query["threshold"] - 0.1)
                
                # State 3: Optimize for speed (reduce limit)
                elif i == 2 and "limit" in state_query:
                    state_query["limit"] = max(1, int(state_query["limit"] * 0.8))
                
                # State 4: Optimize for comprehensiveness (increase limit)
                elif i == 3 and "limit" in state_query:
                    state_query["limit"] = int(state_query["limit"] * 1.2)
                
                # State 5: Balanced optimization
                else:
                    if "threshold" in state_query:
                        state_query["threshold"] = 0.7  # Balanced threshold
                    if "limit" in state_query:
                        state_query["limit"] = min(20, max(5, state_query["limit"]))
            
            quantum_states.append(state_query)
        
        # "Collapse" the quantum superposition by selecting the most promising state
        # For now, we'll use a simple heuristic, but this could be ML-driven
        best_state = self._select_best_quantum_state(quantum_states, query_type, context)
        
        return best_state
    
    def _select_best_quantum_state(
        self, 
        quantum_states: List[Dict], 
        query_type: QueryType, 
        context: Dict
    ) -> Dict[str, Any]:
        """Select the best quantum state based on expected performance."""
        
        # Simple heuristic: score each state
        best_state = quantum_states[0]
        best_score = 0.0
        
        for state in quantum_states:
            score = 0.0
            
            # Score based on query type and context
            if query_type == QueryType.SIMILARITY_SEARCH:
                # Prefer balanced parameters
                if "threshold" in state:
                    # Prefer thresholds around 0.7
                    threshold_score = 1.0 - abs(state["threshold"] - 0.7)
                    score += threshold_score
                
                if "limit" in state:
                    # Prefer reasonable limits (5-20)
                    if 5 <= state["limit"] <= 20:
                        score += 1.0
                    else:
                        score += 0.5
            
            # Consider context preferences
            if context.get("prefer_precision", False) and "threshold" in state:
                if state["threshold"] > 0.8:
                    score += 0.5
            
            if context.get("prefer_speed", False) and "limit" in state:
                if state["limit"] <= 10:
                    score += 0.5
            
            if score > best_score:
                best_score = score
                best_state = state
        
        return best_state
    
    async def _adaptive_learning_optimization(
        self, 
        query: Dict[str, Any], 
        query_type: QueryType, 
        context: Dict
    ) -> Dict[str, Any]:
        """Apply adaptive learning-based optimization."""
        optimized_query = query.copy()
        
        # Learn from recent performance history
        if self.performance_history:
            recent_performance = list(self.performance_history)[-50:]  # Last 50 queries
            
            # Analyze patterns in successful queries
            successful_queries = [
                perf for perf in recent_performance 
                if perf.get("success", False) and perf.get("query_type") == query_type
            ]
            
            if successful_queries:
                # Calculate average parameters of successful queries
                avg_params = {}
                param_counts = {}
                
                for perf in successful_queries:
                    for param, value in perf.get("query_params", {}).items():
                        if isinstance(value, (int, float)):
                            if param not in avg_params:
                                avg_params[param] = 0
                                param_counts[param] = 0
                            avg_params[param] += value
                            param_counts[param] += 1
                
                # Apply learned parameters
                for param, total_value in avg_params.items():
                    if param_counts[param] > 0:
                        avg_value = total_value / param_counts[param]
                        
                        # Apply with learning rate
                        if param in optimized_query:
                            current_value = optimized_query[param]
                            if isinstance(current_value, (int, float)):
                                optimized_value = (
                                    current_value * (1 - self.learning_rate) +
                                    avg_value * self.learning_rate
                                )
                                optimized_query[param] = optimized_value
        
        return optimized_query
    
    def _estimate_improvement(
        self, 
        original_query: Dict[str, Any], 
        optimized_query: Dict[str, Any], 
        query_type: QueryType
    ) -> float:
        """Estimate the expected improvement from optimization."""
        
        # Simple heuristic-based improvement estimation
        improvement_score = 0.0
        
        # Compare key parameters
        for param in ["threshold", "limit"]:
            if param in original_query and param in optimized_query:
                original_val = original_query[param]
                optimized_val = optimized_query[param]
                
                if param == "threshold":
                    # Improvement if threshold is closer to optimal range (0.6-0.8)
                    original_distance = min(abs(original_val - 0.6), abs(original_val - 0.8))
                    optimized_distance = min(abs(optimized_val - 0.6), abs(optimized_val - 0.8))
                    
                    if optimized_distance < original_distance:
                        improvement_score += 0.2
                
                elif param == "limit":
                    # Improvement if limit is in reasonable range
                    if 5 <= optimized_val <= 20 and not (5 <= original_val <= 20):
                        improvement_score += 0.1
        
        # Add base improvement for any optimization
        improvement_score += 0.05
        
        return min(1.0, improvement_score)
    
    def _calculate_confidence(self, strategy: OptimizationStrategy, query_signature: str) -> float:
        """Calculate confidence score for the optimization."""
        
        base_confidence = 0.5
        
        # Higher confidence for pattern-based optimization
        if strategy == OptimizationStrategy.PATTERN_LEARNING:
            if query_signature in self.query_patterns:
                pattern = self.query_patterns[query_signature]
                # Confidence based on pattern usage and success rate
                usage_confidence = min(1.0, pattern.usage_count / 10)
                success_confidence = pattern.success_rate
                base_confidence = 0.3 + 0.4 * usage_confidence + 0.3 * success_confidence
        
        # Lower confidence for chaos-driven optimization
        elif strategy == OptimizationStrategy.CHAOS_DRIVEN:
            base_confidence = 0.3
        
        # Medium confidence for quantum superposition
        elif strategy == OptimizationStrategy.QUANTUM_SUPERPOSITION:
            base_confidence = 0.6
        
        # High confidence for adaptive learning
        elif strategy == OptimizationStrategy.ADAPTIVE_LEARNING:
            base_confidence = 0.7
        
        return base_confidence
    
    async def record_performance(
        self, 
        query: Dict[str, Any], 
        query_type: QueryType,
        optimization_result: OptimizationResult,
        actual_performance: Dict[str, Any]
    ):
        """Record the actual performance of an optimized query."""
        
        # Update performance history
        performance_record = {
            "timestamp": time.time(),
            "query_type": query_type,
            "query_params": query,
            "optimization_strategy": optimization_result.strategy_used,
            "expected_improvement": optimization_result.expected_improvement,
            "actual_improvement": actual_performance.get("improvement", 0.0),
            "response_time": actual_performance.get("response_time", 0.0),
            "success": actual_performance.get("success", False),
            "result_count": actual_performance.get("result_count", 0)
        }
        
        self.performance_history.append(performance_record)
        
        # Update query patterns
        query_signature = optimization_result.metadata["query_signature"]
        await self._update_query_pattern(query_signature, query_type, performance_record)
        
        # Update optimization statistics
        if performance_record["success"]:
            self.optimization_stats["successful_optimizations"] += 1
            
            # Update average improvement
            current_avg = self.optimization_stats["avg_improvement"]
            total_opts = self.optimization_stats["total_optimizations"]
            new_improvement = performance_record["actual_improvement"]
            
            self.optimization_stats["avg_improvement"] = (
                (current_avg * (total_opts - 1) + new_improvement) / total_opts
            )
        
        # Update strategy performance
        strategy = optimization_result.strategy_used
        self.optimization_stats["strategy_performance"][strategy].append(
            performance_record["actual_improvement"]
        )
    
    async def _update_query_pattern(
        self, 
        query_signature: str, 
        query_type: QueryType, 
        performance_record: Dict
    ):
        """Update or create a query pattern based on performance."""
        
        if query_signature not in self.query_patterns:
            self.query_patterns[query_signature] = QueryPattern(
                pattern_id=query_signature,
                query_type=query_type,
                parameters=performance_record["query_params"].copy()
            )
        
        pattern = self.query_patterns[query_signature]
        pattern.usage_count += 1
        pattern.last_used = time.time()
        
        # Update performance metrics
        if performance_record["success"]:
            # Update success rate
            pattern.success_rate = (
                (pattern.success_rate * (pattern.usage_count - 1) + 1.0) / 
                pattern.usage_count
            )
            
            # Update average response time
            response_time = performance_record["response_time"]
            pattern.avg_response_time = (
                (pattern.avg_response_time * (pattern.usage_count - 1) + response_time) / 
                pattern.usage_count
            )
        else:
            # Update success rate (failure)
            pattern.success_rate = (
                (pattern.success_rate * (pattern.usage_count - 1) + 0.0) / 
                pattern.usage_count
            )
        
        # Record optimization in history
        optimization_record = {
            "timestamp": time.time(),
            "strategy": performance_record["optimization_strategy"],
            "improvement": performance_record["actual_improvement"],
            "optimized_value": performance_record["query_params"]
        }
        
        pattern.optimization_history.append(optimization_record)
        
        # Keep only recent history
        if len(pattern.optimization_history) > 20:
            pattern.optimization_history = pattern.optimization_history[-20:]
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics."""
        
        # Calculate strategy performance averages
        strategy_averages = {}
        for strategy, improvements in self.optimization_stats["strategy_performance"].items():
            if improvements:
                strategy_averages[strategy] = sum(improvements) / len(improvements)
            else:
                strategy_averages[strategy] = 0.0
        
        return {
            "total_optimizations": self.optimization_stats["total_optimizations"],
            "successful_optimizations": self.optimization_stats["successful_optimizations"],
            "success_rate": (
                self.optimization_stats["successful_optimizations"] / 
                max(1, self.optimization_stats["total_optimizations"])
            ),
            "avg_improvement": self.optimization_stats["avg_improvement"],
            "strategy_performance": strategy_averages,
            "learned_patterns": len(self.query_patterns),
            "performance_history_size": len(self.performance_history)
        }
    
    async def cleanup_old_patterns(self):
        """Clean up old and unused query patterns."""
        current_time = time.time()
        cutoff_time = current_time - 86400  # 24 hours
        
        old_patterns = [
            pattern_id for pattern_id, pattern in self.query_patterns.items()
            if pattern.last_used < cutoff_time and pattern.usage_count < 5
        ]
        
        for pattern_id in old_patterns:
            del self.query_patterns[pattern_id]
        
        self.logger.info(f"Cleaned up {len(old_patterns)} old query patterns")

# Example usage and testing
async def test_dynamic_query_optimizer():
    """Test the dynamic query optimizer."""
    
    optimizer = DynamicQueryOptimizer()
    
    # Test similarity search optimization
    test_query = {
        "vector": np.random.rand(1536).tolist(),
        "threshold": 0.5,
        "limit": 10,
        "filters": {"category": "test"}
    }
    
    # Optimize the query
    result = await optimizer.optimize_query(
        test_query, 
        QueryType.SIMILARITY_SEARCH,
        context={"prefer_precision": True}
    )
    
    print(f"Original query: {test_query}")
    print(f"Optimized query: {result.optimized_query}")
    print(f"Strategy used: {result.strategy_used}")
    print(f"Expected improvement: {result.expected_improvement:.2f}")
    print(f"Confidence: {result.confidence_score:.2f}")
    
    # Simulate performance feedback
    actual_performance = {
        "improvement": 0.15,
        "response_time": 0.05,
        "success": True,
        "result_count": 8
    }
    
    await optimizer.record_performance(
        test_query, 
        QueryType.SIMILARITY_SEARCH,
        result,
        actual_performance
    )
    
    # Get statistics
    stats = optimizer.get_optimization_stats()
    print(f"Optimization stats: {stats}")

if __name__ == "__main__":
    asyncio.run(test_dynamic_query_optimizer())
