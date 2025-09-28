#!/usr/bin/env python3
"""
Chaos Theory Engine
Implements HRM-inspired chaos theory elements for dynamic system behavior
"""

import asyncio
import logging
import random
import time
import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ChaosPattern(Enum):
    """Different chaos patterns for system behavior."""
    LORENZ_ATTRACTOR = "lorenz_attractor"
    LOGISTIC_MAP = "logistic_map"
    MANDELBROT_SET = "mandelbrot_set"
    RANDOM_WALK = "random_walk"
    STOCHASTIC_RESONANCE = "stochastic_resonance"

@dataclass
class ChaosState:
    """Current state of chaos system."""
    pattern: ChaosPattern
    parameters: Dict[str, float]
    current_value: float
    iteration: int
    stability: float
    metadata: Dict[str, Any]

@dataclass
class ChaosDecision:
    """Decision influenced by chaos theory."""
    decision: str
    chaos_factor: float
    stability_score: float
    pattern_used: ChaosPattern
    reasoning: str
    metadata: Dict[str, Any]

class ChaosTheoryEngine:
    """HRM-inspired chaos theory engine for dynamic decision making."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.chaos_states = {}
        self.decision_history = []
        self.stability_threshold = self.config.get("stability_threshold", 0.7)
        self.chaos_intensity = self.config.get("chaos_intensity", 0.3)
        
    def _default_config(self) -> Dict:
        """Default configuration for chaos theory engine."""
        return {
            "stability_threshold": 0.7,
            "chaos_intensity": 0.3,
            "max_iterations": 1000,
            "convergence_threshold": 0.001,
            "patterns": {
                "lorenz_attractor": {
                    "sigma": 10.0,
                    "rho": 28.0,
                    "beta": 8.0/3.0
                },
                "logistic_map": {
                    "r": 3.8,
                    "x0": 0.5
                },
                "random_walk": {
                    "step_size": 0.1,
                    "drift": 0.0
                }
            }
        }
    
    def initialize_chaos_pattern(
        self, 
        pattern: ChaosPattern, 
        parameters: Optional[Dict] = None
    ) -> ChaosState:
        """Initialize a chaos pattern for decision making."""
        
        if parameters is None:
            parameters = self.config["patterns"].get(pattern.value, {})
        
        initial_value = random.random()
        
        chaos_state = ChaosState(
            pattern=pattern,
            parameters=parameters,
            current_value=initial_value,
            iteration=0,
            stability=0.5,
            metadata={"initialized": time.time()}
        )
        
        self.chaos_states[pattern] = chaos_state
        return chaos_state
    
    def evolve_chaos_state(self, pattern: ChaosPattern, steps: int = 1) -> ChaosState:
        """Evolve the chaos state for given number of steps."""
        
        if pattern not in self.chaos_states:
            self.initialize_chaos_pattern(pattern)
        
        state = self.chaos_states[pattern]
        
        for _ in range(steps):
            state.current_value = self._apply_chaos_function(state)
            state.iteration += 1
            state.stability = self._calculate_stability(state)
        
        return state
    
    def _apply_chaos_function(self, state: ChaosState) -> float:
        """Apply the appropriate chaos function based on pattern."""
        
        if state.pattern == ChaosPattern.LORENZ_ATTRACTOR:
            return self._lorenz_attractor_step(state)
        elif state.pattern == ChaosPattern.LOGISTIC_MAP:
            return self._logistic_map_step(state)
        elif state.pattern == ChaosPattern.RANDOM_WALK:
            return self._random_walk_step(state)
        elif state.pattern == ChaosPattern.STOCHASTIC_RESONANCE:
            return self._stochastic_resonance_step(state)
        else:
            # Default to logistic map
            return self._logistic_map_step(state)
    
    def _lorenz_attractor_step(self, state: ChaosState) -> float:
        """Apply Lorenz attractor dynamics."""
        
        sigma = state.parameters.get("sigma", 10.0)
        rho = state.parameters.get("rho", 28.0)
        beta = state.parameters.get("beta", 8.0/3.0)
        
        # Simplified Lorenz attractor (using only x component)
        x = state.current_value
        
        # Lorenz equations (simplified for single variable)
        dx_dt = sigma * (rho - x) - x * beta
        
        # Update with small time step
        dt = 0.01
        new_x = x + dx_dt * dt
        
        # Keep value in reasonable range
        return max(-10.0, min(10.0, new_x))
    
    def _logistic_map_step(self, state: ChaosState) -> float:
        """Apply logistic map dynamics."""
        
        r = state.parameters.get("r", 3.8)
        x = state.current_value
        
        # Logistic map: x_{n+1} = r * x_n * (1 - x_n)
        new_x = r * x * (1 - x)
        
        return new_x
    
    def _random_walk_step(self, state: ChaosState) -> float:
        """Apply random walk dynamics."""
        
        step_size = state.parameters.get("step_size", 0.1)
        drift = state.parameters.get("drift", 0.0)
        
        x = state.current_value
        
        # Random walk with drift
        random_step = random.gauss(drift, step_size)
        new_x = x + random_step
        
        # Keep value in [0, 1] range
        return max(0.0, min(1.0, new_x))
    
    def _stochastic_resonance_step(self, state: ChaosState) -> float:
        """Apply stochastic resonance dynamics."""
        
        # Stochastic resonance combines periodic signal with noise
        t = state.iteration * 0.1
        signal = math.sin(t)  # Periodic signal
        noise = random.gauss(0, 0.1)  # Gaussian noise
        
        # Combine signal and noise
        new_x = signal + noise
        
        # Normalize to [0, 1]
        return (new_x + 1) / 2
    
    def _calculate_stability(self, state: ChaosState) -> float:
        """Calculate stability of the chaos state."""
        
        # Stability is inversely related to chaos
        # Higher iteration count and bounded values indicate stability
        
        iteration_factor = min(1.0, state.iteration / 100.0)
        
        # Check if value is in reasonable bounds
        if 0.0 <= state.current_value <= 1.0:
            bounds_factor = 1.0
        else:
            bounds_factor = 0.5
        
        stability = (iteration_factor + bounds_factor) / 2.0
        return min(1.0, max(0.0, stability))
    
    async def make_chaos_decision(
        self, 
        options: List[str], 
        context: str = "",
        pattern: Optional[ChaosPattern] = None
    ) -> ChaosDecision:
        """Make a decision influenced by chaos theory."""
        
        if not options:
            return ChaosDecision(
                decision="",
                chaos_factor=0.0,
                stability_score=0.0,
                pattern_used=ChaosPattern.RANDOM_WALK,
                reasoning="No options provided",
                metadata={}
            )
        
        # Select chaos pattern
        if pattern is None:
            pattern = self._select_chaos_pattern(context)
        
        # Evolve chaos state
        state = self.evolve_chaos_state(pattern, steps=10)
        
        # Use chaos value to influence decision
        chaos_value = state.current_value
        chaos_factor = abs(chaos_value - 0.5) * 2  # Normalize to [0, 1]
        
        # Select option based on chaos value
        option_index = int(chaos_value * len(options)) % len(options)
        selected_option = options[option_index]
        
        # Generate reasoning
        reasoning = self._generate_chaos_reasoning(
            selected_option, 
            chaos_factor, 
            state, 
            context
        )
        
        decision = ChaosDecision(
            decision=selected_option,
            chaos_factor=chaos_factor,
            stability_score=state.stability,
            pattern_used=pattern,
            reasoning=reasoning,
            metadata={
                "chaos_value": chaos_value,
                "iteration": state.iteration,
                "parameters": state.parameters
            }
        )
        
        self.decision_history.append(decision)
        return decision
    
    def _select_chaos_pattern(self, context: str) -> ChaosPattern:
        """Select appropriate chaos pattern based on context."""
        
        context_lower = context.lower()
        
        if "creative" in context_lower or "innovative" in context_lower:
            return ChaosPattern.LORENZ_ATTRACTOR
        elif "optimization" in context_lower or "efficiency" in context_lower:
            return ChaosPattern.LOGISTIC_MAP
        elif "exploration" in context_lower or "discovery" in context_lower:
            return ChaosPattern.RANDOM_WALK
        elif "resonance" in context_lower or "signal" in context_lower:
            return ChaosPattern.STOCHASTIC_RESONANCE
        else:
            # Default to logistic map
            return ChaosPattern.LOGISTIC_MAP
    
    def _generate_chaos_reasoning(
        self, 
        decision: str, 
        chaos_factor: float, 
        state: ChaosState, 
        context: str
    ) -> str:
        """Generate reasoning explanation for chaos-influenced decision."""
        
        pattern_name = state.pattern.value.replace("_", " ").title()
        
        if chaos_factor > 0.7:
            chaos_level = "high"
            reasoning_style = "unconventional"
        elif chaos_factor > 0.4:
            chaos_level = "moderate"
            reasoning_style = "balanced"
        else:
            chaos_level = "low"
            reasoning_style = "conventional"
        
        reasoning = (
            f"Decision influenced by {pattern_name} chaos pattern. "
            f"Chaos level: {chaos_level} ({chaos_factor:.2f}). "
            f"Reasoning style: {reasoning_style}. "
            f"System stability: {state.stability:.2f}. "
            f"Selected '{decision}' based on chaos dynamics."
        )
        
        return reasoning
    
    def introduce_controlled_randomness(
        self, 
        base_value: float, 
        intensity: Optional[float] = None
    ) -> float:
        """Introduce controlled randomness to a base value."""
        
        if intensity is None:
            intensity = self.chaos_intensity
        
        # Generate random perturbation
        perturbation = random.gauss(0, intensity)
        
        # Apply perturbation to base value
        randomized_value = base_value + perturbation
        
        # Keep value in reasonable bounds
        return max(0.0, min(1.0, randomized_value))
    
    def get_chaos_metrics(self) -> Dict[str, Any]:
        """Get current chaos system metrics."""
        
        metrics = {
            "active_patterns": len(self.chaos_states),
            "total_decisions": len(self.decision_history),
            "average_chaos_factor": 0.0,
            "average_stability": 0.0,
            "pattern_distribution": {}
        }
        
        if self.decision_history:
            metrics["average_chaos_factor"] = sum(
                d.chaos_factor for d in self.decision_history
            ) / len(self.decision_history)
            
            metrics["average_stability"] = sum(
                d.stability_score for d in self.decision_history
            ) / len(self.decision_history)
        
        # Count pattern usage
        for decision in self.decision_history:
            pattern = decision.pattern_used.value
            metrics["pattern_distribution"][pattern] = (
                metrics["pattern_distribution"].get(pattern, 0) + 1
            )
        
        return metrics

# Example usage and testing
async def test_chaos_engine():
    """Test the chaos theory engine."""
    
    engine = ChaosTheoryEngine()
    
    # Test different chaos patterns
    patterns = [
        ChaosPattern.LORENZ_ATTRACTOR,
        ChaosPattern.LOGISTIC_MAP,
        ChaosPattern.RANDOM_WALK,
        ChaosPattern.STOCHASTIC_RESONANCE
    ]
    
    options = ["Option A", "Option B", "Option C", "Option D"]
    context = "creative problem solving"
    
    print("Testing Chaos Theory Engine:")
    print("=" * 50)
    
    for pattern in patterns:
        print(f"\nTesting {pattern.value}:")
        
        # Initialize and evolve pattern
        state = engine.initialize_chaos_pattern(pattern)
        evolved_state = engine.evolve_chaos_state(pattern, steps=50)
        
        print(f"Initial value: {state.current_value:.4f}")
        print(f"Evolved value: {evolved_state.current_value:.4f}")
        print(f"Stability: {evolved_state.stability:.4f}")
        
        # Make decision
        decision = await engine.make_chaos_decision(options, context, pattern)
        print(f"Decision: {decision.decision}")
        print(f"Chaos factor: {decision.chaos_factor:.4f}")
        print(f"Reasoning: {decision.reasoning}")
    
    # Test controlled randomness
    print("\nTesting controlled randomness:")
    base_value = 0.5
    for i in range(5):
        randomized = engine.introduce_controlled_randomness(base_value)
        print(f"Base: {base_value:.2f} -> Randomized: {randomized:.2f}")
    
    # Get metrics
    metrics = engine.get_chaos_metrics()
    print(f"\nChaos metrics: {metrics}")

if __name__ == "__main__":
    asyncio.run(test_chaos_engine())
