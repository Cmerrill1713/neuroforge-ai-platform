#!/usr/bin/env python3
"""
Test the intelligent research functionality
"""

import sys
import os
sys.path.append('.')

from src.core.self_healing.intelligent_researcher import IntelligentResearcher

def test_research():
    """Test the research functionality."""
    print("🔬 Testing Intelligent Research Functionality")
    print("=" * 50)
    
    researcher = IntelligentResearcher()
    
    # Test cases
    test_errors = [
        "cannot import name SimpleKnowledgeBase from src.core.knowledge.simple_knowledge_base",
        "AttributeError: SomeNewClass object has no attribute some_missing_method",
        "No module named 'some_unknown_module'",
        "Incompatible dimension for X and Y matrices: X.shape[1] == 384 while Y.shape[1] == 768"
    ]
    
    for i, error in enumerate(test_errors, 1):
        print(f"\n🧪 Test {i}: {error[:60]}...")
        print("-" * 60)
        
        # Research the solution
        solution = researcher.research_solution(error)
        
        if solution:
            print(f"✅ Solution found!")
            print(f"   Type: {solution.get('solution_type', 'unknown')}")
            print(f"   Method: {solution.get('research_method', 'unknown')}")
            print(f"   Confidence: {solution.get('confidence', 0):.2f}")
            print(f"   Instructions: {len(solution.get('fix_instructions', []))} steps")
            
            # Generate fix implementation
            fix_code = researcher.generate_fix_implementation(solution)
            if fix_code:
                print(f"   Fix Code: {len(fix_code)} characters")
            else:
                print(f"   Fix Code: None")
        else:
            print(f"❌ No solution found")
    
    # Get research stats
    stats = researcher.get_research_stats()
    print(f"\n📊 Research Statistics:")
    print(f"   Total entries: {stats['total_research_entries']}")
    print(f"   Methods used: {', '.join(stats['research_methods'])}")
    print(f"   Solution types: {', '.join(stats['solution_types'])}")
    print(f"   Average confidence: {stats['average_confidence']:.2f}")

if __name__ == "__main__":
    test_research()
