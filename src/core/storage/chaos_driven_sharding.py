#!/usr/bin/env python3
"""
Chaos-Driven Dynamic Sharding Strategy
Adaptive data distribution based on chaos theory and real-time patterns
Based on HRM-enhanced AI model suggestions from continuous improvement loop
"""

import asyncio
import json
import logging
import time
import math
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class ShardingStrategy(str, Enum):
    """Different sharding strategies."""
    HASH_BASED = "hash_based"
    RANGE_BASED = "range_based"
    CHAOS_DRIVEN = "chaos_driven"
    ADAPTIVE_LEARNING = "adaptive_learning"
    QUANTUM_DISTRIBUTION = "quantum_distribution"

class DataDistributionPattern(str, Enum):
    """Patterns of data distribution."""
    UNIFORM = "uniform"
    SKEWED = "skewed"
    CLUSTERED = "clustered"
    TEMPORAL = "temporal"
    CHAOTIC = "chaotic"

@dataclass
class ShardMetrics:
    """Metrics for a single shard."""
    shard_id: str
    data_count: int = 0
    storage_size: int = 0  # in bytes
    query_load: int = 0
    avg_response_time: float = 0.0
    last_accessed: float = field(default_factory=time.time)
    hotness_score: float = 0.0  # How "hot" (frequently accessed) the shard is
    chaos_factor: float = 0.0  # Chaos-driven randomness factor

@dataclass
class ShardingDecision:
    """Result of a sharding decision."""
    target_shard: str
    strategy_used: ShardingStrategy
    confidence_score: float
    expected_load_balance: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class ChaosTheoryShardingEngine:
    """
    Chaos theory engine for dynamic sharding decisions.
    Uses various chaotic systems to introduce controlled randomness.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Lorenz attractor parameters
        self.lorenz_state = {"x": 0.1, "y": 0, "z": 0}
        self.lorenz_params = {
            "sigma": self.config.get("lorenz_sigma", 10.0),
            "rho": self.config.get("lorenz_rho", 28.0),
            "beta": self.config.get("lorenz_beta", 8.0/3.0)
        }
        
        # Logistic map parameters
        self.logistic_state = {"x": 0.5}
        self.logistic_r = self.config.get("logistic_r", 3.9)  # Chaotic regime
        
        # Henon map parameters
        self.henon_state = {"x": 0.1, "y": 0.1}
        self.henon_params = {
            "a": self.config.get("henon_a", 1.4),
            "b": self.config.get("henon_b", 0.3)
        }
    
    def get_chaos_value(self, chaos_type: str = "lorenz") -> float:
        """Get a chaotic value from the specified system."""
        
        if chaos_type == "lorenz":
            return self._lorenz_step()
        elif chaos_type == "logistic":
            return self._logistic_step()
        elif chaos_type == "henon":
            return self._henon_step()
        else:
            return np.random.random()  # Fallback to random
    
    def _lorenz_step(self) -> float:
        """Perform one step of the Lorenz attractor."""
        dt = 0.01
        x, y, z = self.lorenz_state["x"], self.lorenz_state["y"], self.lorenz_state["z"]
        sigma, rho, beta = self.lorenz_params["sigma"], self.lorenz_params["rho"], self.lorenz_params["beta"]
        
        dx = sigma * (y - x) * dt
        dy = (x * (rho - z) - y) * dt
        dz = (x * y - beta * z) * dt
        
        self.lorenz_state["x"] += dx
        self.lorenz_state["y"] += dy
        self.lorenz_state["z"] += dz
        
        # Normalize to [0, 1]
        return (self.lorenz_state["x"] + 30) / 60  # Approximate normalization
    
    def _logistic_step(self) -> float:
        """Perform one step of the logistic map."""
        x = self.logistic_state["x"]
        new_x = self.logistic_r * x * (1 - x)
        self.logistic_state["x"] = new_x
        return new_x
    
    def _henon_step(self) -> float:
        """Perform one step of the Henon map."""
        x, y = self.henon_state["x"], self.henon_state["y"]
        a, b = self.henon_params["a"], self.henon_params["b"]
        
        new_x = 1 - a * x * x + y
        new_y = b * x
        
        self.henon_state["x"] = new_x
        self.henon_state["y"] = new_y
        
        # Normalize to [0, 1]
        return (new_x + 2) / 4  # Approximate normalization

class ChaosDrivenSharding:
    """
    Dynamic sharding system that adapts to changing data distribution patterns
    using chaos theory and machine learning principles.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Shard management
        self.shards: Dict[str, ShardMetrics] = {}
        self.shard_count = self.config.get("initial_shard_count", 4)
        
        # Initialize shards
        for i in range(self.shard_count):
            shard_id = f"shard_{i:03d}"
            self.shards[shard_id] = ShardMetrics(shard_id=shard_id)
        
        # Chaos theory engine
        self.chaos_engine = ChaosTheoryShardingEngine(self.config.get("chaos_config", {}))
        
        # Distribution pattern tracking
        self.distribution_history = deque(maxlen=self.config.get("max_history", 1000))
        self.pattern_detector = DataPatternDetector()
        
        # Adaptive parameters
        self.chaos_intensity = self.config.get("chaos_intensity", 0.2)
        self.adaptation_rate = self.config.get("adaptation_rate", 0.1)
        self.rebalance_threshold = self.config.get("rebalance_threshold", 0.3)
        
        # Performance tracking
        self.sharding_stats = {
            "total_decisions": 0,
            "rebalance_operations": 0,
            "avg_load_balance": 0.0,
            "strategy_usage": defaultdict(int)
        }
    
    def _default_config(self) -> Dict:
        return {
            "initial_shard_count": 4,
            "max_shard_count": 16,
            "min_shard_count": 2,
            "chaos_intensity": 0.2,
            "adaptation_rate": 0.1,
            "rebalance_threshold": 0.3,
            "max_history": 1000,
            "load_balance_weight": 0.4,
            "response_time_weight": 0.3,
            "chaos_weight": 0.3,
            "enable_auto_scaling": True,
            "scaling_threshold": 0.8
        }
    
    async def determine_shard(
        self, 
        data_key: str, 
        data_metadata: Optional[Dict] = None,
        context: Optional[Dict] = None
    ) -> ShardingDecision:
        """
        Determine the optimal shard for a piece of data using chaos-driven strategy.
        """
        data_metadata = data_metadata or {}
        context = context or {}
        
        # Detect current distribution pattern
        current_pattern = self.pattern_detector.detect_pattern(
            self.shards, self.distribution_history
        )
        
        # Select sharding strategy based on pattern and chaos
        strategy = self._select_sharding_strategy(current_pattern, context)
        
        # Apply the selected strategy
        if strategy == ShardingStrategy.CHAOS_DRIVEN:
            decision = await self._chaos_driven_sharding(data_key, data_metadata, context)
        elif strategy == ShardingStrategy.ADAPTIVE_LEARNING:
            decision = await self._adaptive_learning_sharding(data_key, data_metadata, context)
        elif strategy == ShardingStrategy.QUANTUM_DISTRIBUTION:
            decision = await self._quantum_distribution_sharding(data_key, data_metadata, context)
        elif strategy == ShardingStrategy.RANGE_BASED:
            decision = await self._range_based_sharding(data_key, data_metadata, context)
        else:  # HASH_BASED
            decision = await self._hash_based_sharding(data_key, data_metadata, context)
        
        # Update statistics
        self.sharding_stats["total_decisions"] += 1
        self.sharding_stats["strategy_usage"][strategy] += 1
        
        # Record decision in history
        self._record_sharding_decision(decision, data_key, data_metadata)
        
        return decision
    
    def _select_sharding_strategy(
        self, 
        distribution_pattern: DataDistributionPattern, 
        context: Dict
    ) -> ShardingStrategy:
        """Select the optimal sharding strategy based on current conditions."""
        
        # Get chaos value to introduce controlled randomness
        chaos_value = self.chaos_engine.get_chaos_value("lorenz")
        
        # Use chaos-driven strategy if chaos intensity is high
        if chaos_value < self.chaos_intensity:
            return ShardingStrategy.CHAOS_DRIVEN
        
        # Strategy selection based on distribution pattern
        if distribution_pattern == DataDistributionPattern.UNIFORM:
            return ShardingStrategy.HASH_BASED
        elif distribution_pattern == DataDistributionPattern.SKEWED:
            return ShardingStrategy.ADAPTIVE_LEARNING
        elif distribution_pattern == DataDistributionPattern.CLUSTERED:
            return ShardingStrategy.RANGE_BASED
        elif distribution_pattern == DataDistributionPattern.TEMPORAL:
            return ShardingStrategy.QUANTUM_DISTRIBUTION
        else:  # CHAOTIC
            return ShardingStrategy.CHAOS_DRIVEN
    
    async def _chaos_driven_sharding(
        self, 
        data_key: str, 
        data_metadata: Dict, 
        context: Dict
    ) -> ShardingDecision:
        """Apply chaos-driven sharding strategy."""
        
        # Use multiple chaotic systems for decision making
        lorenz_value = self.chaos_engine.get_chaos_value("lorenz")
        logistic_value = self.chaos_engine.get_chaos_value("logistic")
        henon_value = self.chaos_engine.get_chaos_value("henon")
        
        # Combine chaotic values with load balancing
        shard_scores = {}
        
        for shard_id, shard_metrics in self.shards.items():
            # Base score from chaos
            chaos_score = (lorenz_value + logistic_value + henon_value) / 3
            
            # Load balancing factor (prefer less loaded shards)
            load_factor = 1.0 - (shard_metrics.data_count / max(1, self._get_max_shard_load()))
            
            # Response time factor (prefer faster shards)
            response_factor = 1.0 - min(1.0, shard_metrics.avg_response_time / 1.0)  # Normalize to 1s
            
            # Combine factors
            combined_score = (
                self.config["chaos_weight"] * chaos_score +
                self.config["load_balance_weight"] * load_factor +
                self.config["response_time_weight"] * response_factor
            )
            
            shard_scores[shard_id] = combined_score
        
        # Select shard with highest score
        target_shard = max(shard_scores.keys(), key=lambda k: shard_scores[k])
        
        # Calculate confidence based on score distribution
        scores = list(shard_scores.values())
        max_score = max(scores)
        score_variance = np.var(scores)
        confidence = max_score - score_variance  # Higher confidence if clear winner
        
        return ShardingDecision(
            target_shard=target_shard,
            strategy_used=ShardingStrategy.CHAOS_DRIVEN,
            confidence_score=min(1.0, max(0.0, confidence)),
            expected_load_balance=self._calculate_expected_load_balance(target_shard),
            metadata={
                "chaos_values": {
                    "lorenz": lorenz_value,
                    "logistic": logistic_value,
                    "henon": henon_value
                },
                "shard_scores": shard_scores
            }
        )
    
    async def _adaptive_learning_sharding(
        self, 
        data_key: str, 
        data_metadata: Dict, 
        context: Dict
    ) -> ShardingDecision:
        """Apply adaptive learning-based sharding strategy."""
        
        # Learn from historical sharding decisions
        if len(self.distribution_history) < 10:
            # Not enough history, fall back to hash-based
            return await self._hash_based_sharding(data_key, data_metadata, context)
        
        # Analyze recent successful sharding decisions
        recent_decisions = list(self.distribution_history)[-50:]
        successful_decisions = [
            decision for decision in recent_decisions
            if decision.get("success_score", 0) > 0.7
        ]
        
        if not successful_decisions:
            # No successful patterns, use chaos-driven
            return await self._chaos_driven_sharding(data_key, data_metadata, context)
        
        # Find patterns in successful decisions
        shard_preferences = defaultdict(float)
        for decision in successful_decisions:
            shard_id = decision.get("target_shard")
            success_score = decision.get("success_score", 0)
            if shard_id:
                shard_preferences[shard_id] += success_score
        
        # Normalize preferences
        total_preference = sum(shard_preferences.values())
        if total_preference > 0:
            for shard_id in shard_preferences:
                shard_preferences[shard_id] /= total_preference
        
        # Select shard based on learned preferences and current load
        best_shard = None
        best_score = -1
        
        for shard_id, shard_metrics in self.shards.items():
            preference_score = shard_preferences.get(shard_id, 0.1)  # Default small preference
            load_score = 1.0 - (shard_metrics.data_count / max(1, self._get_max_shard_load()))
            
            combined_score = 0.7 * preference_score + 0.3 * load_score
            
            if combined_score > best_score:
                best_score = combined_score
                best_shard = shard_id
        
        return ShardingDecision(
            target_shard=best_shard or list(self.shards.keys())[0],
            strategy_used=ShardingStrategy.ADAPTIVE_LEARNING,
            confidence_score=best_score,
            expected_load_balance=self._calculate_expected_load_balance(best_shard),
            metadata={
                "shard_preferences": dict(shard_preferences),
                "successful_decisions_count": len(successful_decisions)
            }
        )
    
    async def _quantum_distribution_sharding(
        self, 
        data_key: str, 
        data_metadata: Dict, 
        context: Dict
    ) -> ShardingDecision:
        """Apply quantum-inspired distribution strategy."""
        
        # Create quantum superposition of possible shard assignments
        quantum_states = []
        
        for shard_id in self.shards.keys():
            # Each quantum state represents a different optimization goal
            state_score = 0.0
            
            # State 1: Optimize for load balance
            load_balance_score = 1.0 - (self.shards[shard_id].data_count / max(1, self._get_max_shard_load()))
            
            # State 2: Optimize for response time
            response_time_score = 1.0 - min(1.0, self.shards[shard_id].avg_response_time / 1.0)
            
            # State 3: Optimize for data locality (based on metadata similarity)
            locality_score = self._calculate_data_locality_score(shard_id, data_metadata)
            
            # Quantum superposition: all states exist simultaneously
            superposition_score = (load_balance_score + response_time_score + locality_score) / 3
            
            quantum_states.append((shard_id, superposition_score))
        
        # "Collapse" the quantum superposition by selecting the best state
        quantum_states.sort(key=lambda x: x[1], reverse=True)
        target_shard, best_score = quantum_states[0]
        
        # Calculate confidence based on quantum coherence
        scores = [score for _, score in quantum_states]
        coherence = best_score - np.std(scores)  # Higher coherence = higher confidence
        
        return ShardingDecision(
            target_shard=target_shard,
            strategy_used=ShardingStrategy.QUANTUM_DISTRIBUTION,
            confidence_score=min(1.0, max(0.0, coherence)),
            expected_load_balance=self._calculate_expected_load_balance(target_shard),
            metadata={
                "quantum_states": quantum_states,
                "quantum_coherence": coherence
            }
        )
    
    async def _range_based_sharding(
        self, 
        data_key: str, 
        data_metadata: Dict, 
        context: Dict
    ) -> ShardingDecision:
        """Apply range-based sharding strategy."""
        
        # Use hash of data key to determine range
        key_hash = int(hashlib.md5(data_key.encode()).hexdigest(), 16)
        
        # Divide hash space into ranges based on current shard count
        hash_range = 2**128  # MD5 hash space
        range_size = hash_range // len(self.shards)
        
        # Find target shard based on range
        shard_index = key_hash // range_size
        shard_index = min(shard_index, len(self.shards) - 1)  # Ensure within bounds
        
        target_shard = list(self.shards.keys())[shard_index]
        
        return ShardingDecision(
            target_shard=target_shard,
            strategy_used=ShardingStrategy.RANGE_BASED,
            confidence_score=0.8,  # High confidence for deterministic strategy
            expected_load_balance=self._calculate_expected_load_balance(target_shard),
            metadata={
                "key_hash": key_hash,
                "range_size": range_size,
                "shard_index": shard_index
            }
        )
    
    async def _hash_based_sharding(
        self, 
        data_key: str, 
        data_metadata: Dict, 
        context: Dict
    ) -> ShardingDecision:
        """Apply traditional hash-based sharding strategy."""
        
        # Simple hash-based sharding
        key_hash = hash(data_key)
        shard_index = key_hash % len(self.shards)
        target_shard = list(self.shards.keys())[shard_index]
        
        return ShardingDecision(
            target_shard=target_shard,
            strategy_used=ShardingStrategy.HASH_BASED,
            confidence_score=0.9,  # Very high confidence for deterministic strategy
            expected_load_balance=self._calculate_expected_load_balance(target_shard),
            metadata={
                "key_hash": key_hash,
                "shard_index": shard_index
            }
        )
    
    def _calculate_data_locality_score(self, shard_id: str, data_metadata: Dict) -> float:
        """Calculate data locality score for a shard."""
        # This is a simplified implementation
        # In practice, this would analyze metadata similarity with existing data in the shard
        
        # For now, return a random score influenced by chaos
        chaos_value = self.chaos_engine.get_chaos_value("logistic")
        base_score = 0.5
        
        # Add some metadata-based scoring
        if "category" in data_metadata:
            # Prefer shards that already have similar categories
            # This is a placeholder - real implementation would track shard contents
            category_hash = hash(data_metadata["category"])
            shard_hash = hash(shard_id)
            similarity = 1.0 - abs((category_hash % 100) - (shard_hash % 100)) / 100.0
            base_score += 0.3 * similarity
        
        return min(1.0, base_score + 0.2 * chaos_value)
    
    def _get_max_shard_load(self) -> int:
        """Get the maximum data count across all shards."""
        return max(shard.data_count for shard in self.shards.values()) if self.shards else 1
    
    def _calculate_expected_load_balance(self, target_shard: str) -> float:
        """Calculate expected load balance after adding data to target shard."""
        if not self.shards:
            return 1.0
        
        # Simulate adding one item to target shard
        simulated_loads = {}
        for shard_id, shard_metrics in self.shards.items():
            if shard_id == target_shard:
                simulated_loads[shard_id] = shard_metrics.data_count + 1
            else:
                simulated_loads[shard_id] = shard_metrics.data_count
        
        # Calculate load balance (1.0 = perfect balance, 0.0 = completely unbalanced)
        loads = list(simulated_loads.values())
        if not loads:
            return 1.0
        
        avg_load = sum(loads) / len(loads)
        if avg_load == 0:
            return 1.0
        
        # Calculate coefficient of variation (lower is better)
        std_dev = np.std(loads)
        cv = std_dev / avg_load if avg_load > 0 else 0
        
        # Convert to balance score (higher is better)
        balance_score = 1.0 / (1.0 + cv)
        return balance_score
    
    def _record_sharding_decision(
        self, 
        decision: ShardingDecision, 
        data_key: str, 
        data_metadata: Dict
    ):
        """Record a sharding decision in the history."""
        
        record = {
            "timestamp": time.time(),
            "data_key": data_key,
            "target_shard": decision.target_shard,
            "strategy": decision.strategy_used,
            "confidence": decision.confidence_score,
            "expected_load_balance": decision.expected_load_balance,
            "metadata": data_metadata,
            "decision_metadata": decision.metadata
        }
        
        self.distribution_history.append(record)
        
        # Update shard metrics
        if decision.target_shard in self.shards:
            shard = self.shards[decision.target_shard]
            shard.data_count += 1
            shard.last_accessed = time.time()
            
            # Update chaos factor for the shard
            chaos_value = self.chaos_engine.get_chaos_value("henon")
            shard.chaos_factor = 0.9 * shard.chaos_factor + 0.1 * chaos_value
    
    async def update_shard_performance(
        self, 
        shard_id: str, 
        response_time: float, 
        success: bool
    ):
        """Update shard performance metrics."""
        
        if shard_id not in self.shards:
            return
        
        shard = self.shards[shard_id]
        shard.query_load += 1
        shard.last_accessed = time.time()
        
        # Update average response time
        if shard.avg_response_time == 0:
            shard.avg_response_time = response_time
        else:
            # Exponential moving average
            alpha = 0.1
            shard.avg_response_time = (
                alpha * response_time + (1 - alpha) * shard.avg_response_time
            )
        
        # Update hotness score
        current_time = time.time()
        time_factor = 1.0 / (1.0 + (current_time - shard.last_accessed) / 3600)  # Decay over hours
        shard.hotness_score = 0.9 * shard.hotness_score + 0.1 * time_factor
        
        # Update success score in history
        if self.distribution_history:
            recent_record = self.distribution_history[-1]
            if recent_record.get("target_shard") == shard_id:
                success_score = 1.0 if success else 0.0
                if response_time < 0.1:  # Fast response
                    success_score += 0.2
                recent_record["success_score"] = min(1.0, success_score)
    
    async def rebalance_shards(self) -> Dict[str, Any]:
        """Perform shard rebalancing if needed."""
        
        # Calculate current load balance
        current_balance = self._calculate_current_load_balance()
        
        if current_balance > self.rebalance_threshold:
            # No rebalancing needed
            return {
                "rebalanced": False,
                "current_balance": current_balance,
                "threshold": self.rebalance_threshold
            }
        
        # Perform rebalancing
        rebalance_plan = self._create_rebalance_plan()
        
        # Execute rebalancing (in practice, this would involve data migration)
        self.logger.info(f"Executing rebalance plan: {rebalance_plan}")
        
        # Update statistics
        self.sharding_stats["rebalance_operations"] += 1
        
        return {
            "rebalanced": True,
            "previous_balance": current_balance,
            "rebalance_plan": rebalance_plan,
            "expected_improvement": rebalance_plan.get("expected_improvement", 0.0)
        }
    
    def _calculate_current_load_balance(self) -> float:
        """Calculate current load balance across all shards."""
        if not self.shards:
            return 1.0
        
        loads = [shard.data_count for shard in self.shards.values()]
        avg_load = sum(loads) / len(loads) if loads else 0
        
        if avg_load == 0:
            return 1.0
        
        std_dev = np.std(loads)
        cv = std_dev / avg_load
        
        return 1.0 / (1.0 + cv)
    
    def _create_rebalance_plan(self) -> Dict[str, Any]:
        """Create a plan for rebalancing shards."""
        
        # Find overloaded and underloaded shards
        loads = [(shard_id, shard.data_count) for shard_id, shard in self.shards.items()]
        loads.sort(key=lambda x: x[1])
        
        avg_load = sum(load for _, load in loads) / len(loads)
        
        underloaded = [(shard_id, load) for shard_id, load in loads if load < avg_load * 0.8]
        overloaded = [(shard_id, load) for shard_id, load in loads if load > avg_load * 1.2]
        
        # Create migration plan
        migrations = []
        for over_shard, over_load in overloaded:
            for under_shard, under_load in underloaded:
                if over_load > avg_load and under_load < avg_load:
                    # Calculate how much to migrate
                    migrate_amount = min(
                        over_load - avg_load,
                        avg_load - under_load
                    ) // 2
                    
                    if migrate_amount > 0:
                        migrations.append({
                            "from_shard": over_shard,
                            "to_shard": under_shard,
                            "amount": migrate_amount
                        })
        
        # Calculate expected improvement
        expected_improvement = len(migrations) * 0.1  # Rough estimate
        
        return {
            "migrations": migrations,
            "expected_improvement": expected_improvement,
            "overloaded_shards": len(overloaded),
            "underloaded_shards": len(underloaded)
        }
    
    def get_sharding_stats(self) -> Dict[str, Any]:
        """Get comprehensive sharding statistics."""
        
        current_balance = self._calculate_current_load_balance()
        
        # Calculate shard utilization
        shard_utilization = {}
        for shard_id, shard in self.shards.items():
            shard_utilization[shard_id] = {
                "data_count": shard.data_count,
                "query_load": shard.query_load,
                "avg_response_time": shard.avg_response_time,
                "hotness_score": shard.hotness_score,
                "chaos_factor": shard.chaos_factor
            }
        
        return {
            "total_shards": len(self.shards),
            "current_load_balance": current_balance,
            "total_decisions": self.sharding_stats["total_decisions"],
            "rebalance_operations": self.sharding_stats["rebalance_operations"],
            "strategy_usage": dict(self.sharding_stats["strategy_usage"]),
            "shard_utilization": shard_utilization,
            "chaos_intensity": self.chaos_intensity,
            "distribution_history_size": len(self.distribution_history)
        }

class DataPatternDetector:
    """Detects patterns in data distribution."""
    
    def detect_pattern(
        self, 
        shards: Dict[str, ShardMetrics], 
        history: deque
    ) -> DataDistributionPattern:
        """Detect the current data distribution pattern."""
        
        if not shards or len(history) < 10:
            return DataDistributionPattern.UNIFORM
        
        # Analyze shard load distribution
        loads = [shard.data_count for shard in shards.values()]
        
        if not loads:
            return DataDistributionPattern.UNIFORM
        
        # Calculate distribution metrics
        mean_load = np.mean(loads)
        std_load = np.std(loads)
        cv = std_load / mean_load if mean_load > 0 else 0
        
        # Analyze temporal patterns
        recent_history = list(history)[-50:]
        time_variance = self._calculate_temporal_variance(recent_history)
        
        # Pattern classification
        if cv < 0.1:
            return DataDistributionPattern.UNIFORM
        elif cv > 0.5:
            if time_variance > 0.3:
                return DataDistributionPattern.CHAOTIC
            else:
                return DataDistributionPattern.SKEWED
        elif time_variance > 0.4:
            return DataDistributionPattern.TEMPORAL
        else:
            return DataDistributionPattern.CLUSTERED
    
    def _calculate_temporal_variance(self, history: List[Dict]) -> float:
        """Calculate variance in temporal access patterns."""
        
        if len(history) < 5:
            return 0.0
        
        # Extract timestamps and calculate intervals
        timestamps = [record.get("timestamp", 0) for record in history]
        timestamps.sort()
        
        intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        
        if not intervals:
            return 0.0
        
        # Calculate coefficient of variation for intervals
        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        return std_interval / mean_interval if mean_interval > 0 else 0.0

# Example usage and testing
async def test_chaos_driven_sharding():
    """Test the chaos-driven sharding system."""
    
    sharding_system = ChaosDrivenSharding()
    
    # Test sharding decisions
    test_data = [
        ("user_123", {"category": "user", "type": "profile"}),
        ("product_456", {"category": "product", "type": "catalog"}),
        ("order_789", {"category": "order", "type": "transaction"}),
        ("user_124", {"category": "user", "type": "profile"}),
        ("product_457", {"category": "product", "type": "catalog"}),
    ]
    
    decisions = []
    for data_key, metadata in test_data:
        decision = await sharding_system.determine_shard(data_key, metadata)
        decisions.append(decision)
        
        print(f"Data: {data_key}")
        print(f"  Target Shard: {decision.target_shard}")
        print(f"  Strategy: {decision.strategy_used}")
        print(f"  Confidence: {decision.confidence_score:.2f}")
        print(f"  Expected Balance: {decision.expected_load_balance:.2f}")
        print()
        
        # Simulate performance feedback
        await sharding_system.update_shard_performance(
            decision.target_shard,
            response_time=np.random.uniform(0.01, 0.1),
            success=True
        )
    
    # Test rebalancing
    rebalance_result = await sharding_system.rebalance_shards()
    print(f"Rebalance result: {rebalance_result}")
    
    # Get statistics
    stats = sharding_system.get_sharding_stats()
    print(f"Sharding stats: {stats}")

if __name__ == "__main__":
    asyncio.run(test_chaos_driven_sharding())
