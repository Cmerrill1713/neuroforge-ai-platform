#!/usr/bin/env python3
"""
Comprehensive Test for Enhanced Research System with Parallel Crawling
"""

import asyncio
import json
import requests
import time
from datetime import datetime

def test_enhanced_research_system():
    """Test the enhanced research system with parallel crawling"""
    print("🔬 Enhanced Research System Test")
    print("=" * 60)
    
    # Test cases for different error types
    test_cases = [
        {
            "name": "Import Error",
            "error": "cannot import name DatabaseConnection from src.database.connection_manager",
            "expected": "Should research and find solution with parallel crawling"
        },
        {
            "name": "Attribute Error", 
            "error": "AttributeError: CacheManager object has no attribute clear_all_entries",
            "expected": "Should identify as missing method and provide fix"
        },
        {
            "name": "Module Not Found",
            "error": "ModuleNotFoundError: No module named 'advanced_analytics'",
            "expected": "Should suggest installation or path fix"
        },
        {
            "name": "Dimension Mismatch",
            "error": "Incompatible dimension for X and Y matrices: X.shape[1] == 384 while Y.shape[1] == 768",
            "expected": "Should analyze codebase structure and find dimension fixes"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print(f"   Error: {test_case['error'][:50]}...")
        print(f"   Expected: {test_case['expected']}")
        print("-" * 50)
        
        try:
            # Test the research endpoint
            response = requests.post(
                "http://localhost:8004/api/healing/research-unknown-error",
                json={
                    "error_message": test_case["error"],
                    "context": {"test_case": test_case["name"]}
                },
                timeout=60  # Allow more time for parallel crawling
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    if data.get("solution_found"):
                        print(f"✅ Enhanced research successful!")
                        print(f"   Solution Type: {data.get('solution', {}).get('solution_type', 'unknown')}")
                        print(f"   Research Method: {data.get('research_method', 'unknown')}")
                        print(f"   Confidence: {data.get('confidence', 0):.2f}")
                        print(f"   Execution Time: {data.get('execution_time_ms', 0):.2f}ms")
                        
                        # Check for enhanced features
                        solution = data.get("solution", {})
                        if solution.get("sources_analyzed", 0) > 0:
                            print(f"   Sources Analyzed: {solution.get('sources_analyzed', 0)}")
                        if solution.get("content_analyzed", 0) > 0:
                            print(f"   Content Analyzed: {solution.get('content_analyzed', 0)}")
                        
                        results.append({
                            "test": test_case["name"],
                            "status": "success",
                            "solution_type": solution.get("solution_type", "unknown"),
                            "confidence": data.get("confidence", 0),
                            "execution_time": data.get("execution_time_ms", 0),
                            "sources_analyzed": solution.get("sources_analyzed", 0),
                            "content_analyzed": solution.get("content_analyzed", 0)
                        })
                    else:
                        print(f"⚠️ Research completed but no solution found")
                        results.append({
                            "test": test_case["name"],
                            "status": "no_solution",
                            "execution_time": data.get("execution_time_ms", 0)
                        })
                else:
                    print(f"❌ Research failed: {data.get('error', 'Unknown error')}")
                    results.append({
                        "test": test_case["name"],
                        "status": "failed",
                        "error": data.get("error", "Unknown error")
                    })
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                results.append({
                    "test": test_case["name"],
                    "status": "http_error",
                    "status_code": response.status_code
                })
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append({
                "test": test_case["name"],
                "status": "exception",
                "error": str(e)
            })
    
    # Test analyze-and-heal with enhanced research
    print(f"\n🔧 Testing Enhanced Analyze-and-Heal with Research")
    print("-" * 50)
    
    try:
        response = requests.post(
            "http://localhost:8004/api/healing/analyze-and-heal",
            json={
                "error_message": "cannot import name ResearchEngine from src.research.intelligence",
                "auto_heal": True
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print("Response:", json.dumps(data, indent=2))
            
            if data.get("error_analysis", {}).get("error_type") == "unknown_researched":
                print("✅ Enhanced healing successful!")
            else:
                print(f"❌ Enhanced healing failed: {data.get('error_analysis', {}).get('error_type', 'unknown')}")
        else:
            print(f"❌ Analyze-and-heal failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Analyze-and-heal test failed: {e}")
    
    # Print final statistics
    print(f"\n📊 Final Enhanced Research Statistics")
    print("-" * 50)
    
    successful_tests = [r for r in results if r["status"] == "success"]
    print(f"Total Tests: {len(results)}")
    print(f"Successful: {len(successful_tests)}")
    print(f"Failed: {len(results) - len(successful_tests)}")
    print(f"Success Rate: {len(successful_tests)/len(results)*100:.1f}%")
    
    if successful_tests:
        print(f"\nDetailed Results:")
        for result in successful_tests:
            print(f"  ✅ {result['test']}")
            print(f"     Solution: {result['solution_type']}")
            print(f"     Confidence: {result['confidence']:.2f}")
            print(f"     Execution Time: {result['execution_time']:.2f}ms")
            if result.get('sources_analyzed', 0) > 0:
                print(f"     Sources: {result['sources_analyzed']}")
            if result.get('content_analyzed', 0) > 0:
                print(f"     Content: {result['content_analyzed']}")
    
    return results

if __name__ == "__main__":
    test_enhanced_research_system()
