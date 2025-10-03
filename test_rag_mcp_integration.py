#!/usr/bin/env python3
"""
Test RAG-MCP Integration
Validates that the RAG system is properly integrated with MCP tools
"""

import asyncio
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.retrieval.rag_service import create_rag_service
from core.tools.comprehensive_mcp_executor import ComprehensiveMCPExecutor

async def test_rag_service():
    """Test the RAG service directly"""
    print("🧪 Testing RAG Service Directly...")
    
    try:
        # Create RAG service
        rag_service = create_rag_service(env="development")
        
        # Test query
        query = "machine learning"
        response = await rag_service.query(
            query_text=query,
            k=3,
            method="hybrid",
            rerank=True
        )
        
        print(f"✅ RAG Query: '{query}'")
        print(f"   Results: {response.num_results}")
        print(f"   Latency: {response.latency_ms:.0f}ms")
        print(f"   Method: {response.retrieval_method}")
        
        # Show first result
        if response.results:
            first_result = response.results[0]
            print(f"   Top result: {first_result.text[:100]}...")
            print(f"   Score: {first_result.score:.3f}")
        
        # Get metrics
        metrics = await rag_service.get_metrics()
        print(f"   Metrics: {metrics}")
        
        # Close service
        await rag_service.close()
        
        return True
        
    except Exception as e:
        print(f"❌ RAG Service test failed: {e}")
        return False

async def test_mcp_executor():
    """Test the MCP executor with RAG tools"""
    print("\n🧪 Testing MCP Executor with RAG Tools...")
    
    try:
        async with ComprehensiveMCPExecutor() as executor:
            # Test knowledge search
            result = await executor.execute_tool(
                "knowledge_search", 
                "artificial intelligence",
                k=3
            )
            
            if result.get("success"):
                print(f"✅ MCP Knowledge Search successful")
                print(f"   Query: {result.get('query')}")
                print(f"   Results: {result.get('count')}")
                print(f"   Latency: {result.get('latency_ms', 0):.0f}ms")
                
                # Show first result
                results = result.get("results", [])
                if results:
                    first_result = results[0]
                    print(f"   Top result: {first_result.get('text', '')[:100]}...")
                    print(f"   Score: {first_result.get('score', 0):.3f}")
            else:
                print(f"❌ MCP Knowledge Search failed: {result.get('error')}")
                return False
            
            # Test RAG query
            result = await executor.execute_tool(
                "rag_query",
                "machine learning algorithms",
                k=2
            )
            
            if result.get("success"):
                print(f"✅ MCP RAG Query successful")
                print(f"   Results: {result.get('count')}")
            else:
                print(f"❌ MCP RAG Query failed: {result.get('error')}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ MCP Executor test failed: {e}")
        return False

async def test_mcp_server():
    """Test the MCP server (if running)"""
    print("\n🧪 Testing MCP Server...")
    
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            # Test health endpoint
            try:
                async with session.get("http://localhost:8002/health", timeout=5) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        print(f"✅ MCP Server health check passed")
                        print(f"   Status: {health_data.get('status')}")
                        print(f"   Tools: {health_data.get('tools_count', 0)}")
                        return True
                    else:
                        print(f"❌ MCP Server health check failed: HTTP {response.status}")
                        return False
            except aiohttp.ClientConnectorError:
                print("❌ MCP Server not running on localhost:8002")
                return False
                
    except Exception as e:
        print(f"❌ MCP Server test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 RAG-MCP Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("RAG Service", test_rag_service),
        ("MCP Executor", test_mcp_executor),
        ("MCP Server", test_mcp_server)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! RAG-MCP integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

