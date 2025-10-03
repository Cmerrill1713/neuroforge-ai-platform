#!/usr/bin/env python3
"""
Test Enhanced RAG System
Tests the new deduplication and hybrid search features
"""

import sys
import asyncio
import requests
import json
from pathlib import Path

def test_enhanced_rag_api():
    """Test the enhanced RAG API endpoints"""
    
    base_url = "http://localhost:8004"
    
    print("🧪 Testing Enhanced RAG System")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/api/rag/enhanced/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health Check: {health_data['status']}")
            print(f"   - Deduplication: {health_data.get('deduplication_enabled', False)}")
            print(f"   - Hybrid Search: {health_data.get('hybrid_search_enabled', False)}")
            print(f"   - Documents: {health_data.get('total_documents', 0)}")
        else:
            print(f"❌ Health Check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check error: {e}")
    
    # Test 2: Enhanced Search
    print("\n2. Testing Enhanced Search...")
    test_queries = [
        "What is machine learning?",
        "How does artificial intelligence work?",
        "Explain deep learning algorithms"
    ]
    
    for query in test_queries:
        try:
            search_request = {
                "query_text": query,
                "top_k": 5,
                "deduplicate": True,
                "use_hybrid_search": True,
                "min_confidence": 0.3,
                "include_metadata": True,
                "include_deduplication_info": True
            }
            
            response = requests.post(
                f"{base_url}/api/rag/enhanced/search",
                json=search_request
            )
            
            if response.status_code == 200:
                search_data = response.json()
                print(f"✅ Search: '{query}'")
                print(f"   - Results: {search_data['unique_results']}/{search_data['total_found']}")
                print(f"   - Duplicates filtered: {search_data['duplicates_filtered']}")
                print(f"   - Latency: {search_data['latency_ms']:.1f}ms")
                print(f"   - Method: {search_data['retrieval_method']}")
                
                # Show confidence stats
                conf_stats = search_data.get('confidence_stats', {})
                if conf_stats:
                    print(f"   - Avg confidence: {conf_stats.get('mean', 0):.3f}")
            else:
                print(f"❌ Search failed for '{query}': {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Search error for '{query}': {e}")
    
    # Test 3: Metrics
    print("\n3. Testing Metrics...")
    try:
        response = requests.get(f"{base_url}/api/rag/enhanced/metrics")
        if response.status_code == 200:
            metrics_data = response.json()
            print("✅ Metrics retrieved")
            
            # System stats
            system_stats = metrics_data.get('system_stats', {})
            print(f"   - Model: {system_stats.get('model_name', 'Unknown')}")
            print(f"   - Documents: {system_stats.get('num_documents', 0)}")
            print(f"   - Embedding dim: {system_stats.get('embedding_dimension', 0)}")
            
            # Enhanced features
            enhanced_features = system_stats.get('enhanced_features', {})
            print(f"   - Deduplication: {enhanced_features.get('deduplication_enabled', False)}")
            print(f"   - Hybrid search: {enhanced_features.get('hybrid_search_enabled', False)}")
            print(f"   - Content hashes: {enhanced_features.get('total_unique_content_hashes', 0)}")
            
            # Deduplication report
            dedup_report = metrics_data.get('deduplication_report', {})
            if dedup_report.get('deduplication_enabled'):
                print(f"   - Duplicate clusters: {dedup_report.get('duplicate_clusters', 0)}")
                print(f"   - Total duplicates: {dedup_report.get('total_duplicates', 0)}")
                print(f"   - Largest cluster: {dedup_report.get('largest_cluster_size', 0)}")
            
            # Search performance
            search_perf = metrics_data.get('search_performance', {})
            print(f"   - Total searches: {search_perf.get('total_searches', 0)}")
            print(f"   - Avg latency: {search_perf.get('avg_latency_ms', 0):.1f}ms")
            print(f"   - Duplicates filtered: {search_perf.get('duplicates_filtered', 0)}")
            
        else:
            print(f"❌ Metrics failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Metrics error: {e}")
    
    # Test 4: Deduplication Report
    print("\n4. Testing Deduplication Report...")
    try:
        response = requests.post(f"{base_url}/api/rag/enhanced/deduplicate")
        if response.status_code == 200:
            dedup_data = response.json()
            report = dedup_data.get('report', {})
            print("✅ Deduplication report:")
            print(f"   - Total hashes: {report.get('total_content_hashes', 0)}")
            print(f"   - Total clusters: {report.get('total_clusters', 0)}")
            print(f"   - Duplicate clusters: {report.get('duplicate_clusters', 0)}")
            print(f"   - Total duplicates: {report.get('total_duplicates', 0)}")
        else:
            print(f"❌ Deduplication report failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Deduplication report error: {e}")
    
    # Test 5: System Test
    print("\n5. Testing System Test...")
    try:
        response = requests.post(f"{base_url}/api/rag/enhanced/test")
        if response.status_code == 200:
            test_data = response.json()
            print("✅ System test completed")
            
            test_results = test_data.get('test_results', [])
            for test in test_results:
                print(f"   - '{test['query']}': {test['results_count']} results, {test['latency_ms']:.1f}ms")
        else:
            print(f"❌ System test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ System test error: {e}")
    
    print("\n" + "=" * 50)
    print("🧪 Enhanced RAG Testing Complete")

def test_comparison():
    """Compare old vs new RAG system performance"""
    
    base_url = "http://localhost:8004"
    
    print("\n🔄 Comparing Old vs Enhanced RAG")
    print("=" * 50)
    
    test_query = "What is machine learning?"
    
    # Test old RAG endpoint
    print("\n1. Testing Old RAG Endpoint...")
    try:
        old_request = {
            "query_text": test_query,
            "k": 5,
            "method": "hybrid",
            "rerank": True
        }
        
        response = requests.post(f"{base_url}/api/rag/query", json=old_request)
        if response.status_code == 200:
            old_data = response.json()
            print(f"✅ Old RAG: {len(old_data.get('results', []))} results, {old_data.get('latency_ms', 0):.1f}ms")
        else:
            print(f"❌ Old RAG failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Old RAG error: {e}")
    
    # Test enhanced RAG endpoint
    print("\n2. Testing Enhanced RAG Endpoint...")
    try:
        enhanced_request = {
            "query_text": test_query,
            "top_k": 5,
            "deduplicate": True,
            "use_hybrid_search": True,
            "min_confidence": 0.3
        }
        
        response = requests.post(f"{base_url}/api/rag/enhanced/search", json=enhanced_request)
        if response.status_code == 200:
            enhanced_data = response.json()
            print(f"✅ Enhanced RAG: {enhanced_data['unique_results']} unique results")
            print(f"   - Total found: {enhanced_data['total_found']}")
            print(f"   - Duplicates filtered: {enhanced_data['duplicates_filtered']}")
            print(f"   - Latency: {enhanced_data['latency_ms']:.1f}ms")
        else:
            print(f"❌ Enhanced RAG failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Enhanced RAG error: {e}")

if __name__ == "__main__":
    print("🚀 Enhanced RAG System Test Suite")
    print("Make sure the API server is running on port 8004")
    
    try:
        # Test enhanced RAG system
        test_enhanced_rag_api()
        
        # Test comparison
        test_comparison()
        
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
