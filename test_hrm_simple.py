#!/usr/bin/env python3
"""
Simple HRM test to isolate issues
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.reasoning.chaos_theory_engine import ChaosTheoryEngine, ChaosPattern

async def test_simple():
    print("🧪 Testing HRM Components Individually")
    print("=" * 50)
    
    # Test 1: Chaos Theory Engine
    print("\n🎲 Testing Chaos Theory Engine:")
    chaos_engine = ChaosTheoryEngine()
    
    options = ["option_a", "option_b", "option_c"]
    decision = await chaos_engine.make_chaos_decision(options, "test context")
    
    print(f"✅ Decision: {decision.decision}")
    print(f"✅ Chaos factor: {decision.chaos_factor:.2f}")
    print(f"✅ Pattern: {decision.pattern_used.value}")
    
    # Test 2: Chaos patterns
    print(f"\n🌀 Testing Chaos Patterns:")
    for pattern in ChaosPattern:
        state = chaos_engine.initialize_chaos_pattern(pattern)
        evolved = chaos_engine.evolve_chaos_state(pattern, steps=10)
        print(f"✅ {pattern.value}: {state.current_value:.3f} -> {evolved.current_value:.3f}")
    
    print(f"\n🎉 Simple HRM test completed!")

if __name__ == "__main__":
    asyncio.run(test_simple())
