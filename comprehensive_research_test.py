#!/usr/bin/env python3
"""
Comprehensive test of the intelligent research and learning system
"""

import requests
import json
import time

def test_research_system():
    """Test the complete research and learning system."""
    base_url = "http://localhost:8004"
    
    print("🔬 Comprehensive Research System Test")
    print("=" * 60)
    
    # Test cases for unknown issues
    unknown_errors = [
        {
            "name": "Missing Class Import",
            "error": "cannot import name DatabaseConnection from src.database.connection_manager",
            "expected": "Should research and find solution"
        },
        {
            "name": "Missing Method Error", 
            "error": "AttributeError: CacheManager object has no attribute clear_all_entries",
            "expected": "Should identify as missing method"
        },
        {
            "name": "Module Not Found",
            "error": "ModuleNotFoundError: No module named 'advanced_analytics'",
            "expected": "Should suggest installation or path fix"
        },
        {
            "name": "Complex Import Error",
            "error": "ImportError: cannot import name 'ComplexAlgorithm' from 'src.algorithms.ml_models'",
            "expected": "Should analyze codebase structure"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(unknown_errors, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print(f"   Error: {test_case['error'][:50]}...")
        print(f"   Expected: {test_case['expected']}")
        print("-" * 60)
        
        try:
            # Research the unknown error
            response = requests.post(
                f"{base_url}/api/healing/research-unknown-error",
                json={"error_message": test_case['error']},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data['success'] and data['solution_found']:
                    solution = data['solution']
                    print(f"✅ Research successful!")
                    print(f"   Solution Type: {solution.get('solution_type', 'unknown')}")
                    print(f"   Research Method: {solution.get('research_method', 'unknown')}")
                    print(f"   Confidence: {solution.get('confidence', 0):.2f}")
                    print(f"   Execution Time: {data['execution_time_ms']:.2f}ms")
                    
                    if data.get('fix_implementation'):
                        print(f"   Fix Code Generated: {len(data['fix_implementation'])} chars")
                    
                    results.append({
                        "test": test_case['name'],
                        "success": True,
                        "solution_type": solution.get('solution_type'),
                        "confidence": solution.get('confidence', 0),
                        "method": solution.get('research_method')
                    })
                else:
                    print(f"❌ No solution found")
                    results.append({
                        "test": test_case['name'],
                        "success": False,
                        "reason": "No solution found"
                    })
            else:
                print(f"❌ API Error: {response.status_code}")
                results.append({
                    "test": test_case['name'],
                    "success": False,
                    "reason": f"API Error: {response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append({
                "test": test_case['name'],
                "success": False,
                "reason": str(e)
            })
        
        time.sleep(1)  # Brief pause between tests
    
    # Test the enhanced analyze-and-heal with research
    print(f"\n🔧 Testing Enhanced Analyze-and-Heal with Research")
    print("-" * 60)
    
    test_error = "cannot import name ResearchEngine from src.research.intelligence"
    
    try:
        response = requests.post(
            f"{base_url}/api/healing/analyze-and-heal",
            json={"error_message": test_error},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                print(f"✅ Enhanced healing successful!")
            else:
                print(f"❌ Enhanced healing failed: {data.get('error_analysis', {}).get('error_type', 'unknown')}")
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Enhanced healing test failed: {e}")
    
    # Get final research statistics
    print(f"\n📊 Final Research Statistics")
    print("-" * 60)
    
    try:
        response = requests.get(f"{base_url}/api/healing/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"Research Stats: {json.dumps(stats.get('research_stats', {}), indent=2)}")
        else:
            print(f"Could not get research stats: {response.status_code}")
    except Exception as e:
        print(f"Error getting research stats: {e}")
    
    # Summary
    print(f"\n📋 Test Summary")
    print("=" * 60)
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    print(f"Success Rate: {successful/total*100:.1f}%")
    
    print(f"\nDetailed Results:")
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {result['test']}")
        if result['success']:
            print(f"     Solution: {result.get('solution_type', 'unknown')}")
            print(f"     Method: {result.get('method', 'unknown')}")
            print(f"     Confidence: {result.get('confidence', 0):.2f}")
        else:
            print(f"     Reason: {result.get('reason', 'unknown')}")

if __name__ == "__main__":
    test_research_system()
