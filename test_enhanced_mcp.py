#!/usr/bin/env python3
"""
Test Enhanced MCP Tools
Tests the functional MCP tools instead of simulated responses
"""

import requests
import json
import time

def test_enhanced_mcp_tools():
    """Test the enhanced MCP tools"""
    
    base_url = "http://localhost:8004"
    
    print("🔧 Testing Enhanced MCP Tools")
    print("=" * 50)
    
    # Test 1: List Available Tools
    print("\n1. Testing Available Tools...")
    try:
        response = requests.get(f"{base_url}/api/mcp/tools")
        if response.status_code == 200:
            tools_data = response.json()
            print(f"✅ Available Tools: {tools_data['total_tools']} tools")
            
            # Group by category
            categories = {}
            for tool in tools_data['tools']:
                category = tool['category']
                if category not in categories:
                    categories[category] = []
                categories[category].append(tool['name'])
            
            for category, tools in categories.items():
                print(f"   - {category}: {', '.join(tools)}")
        else:
            print(f"❌ Tools list failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Tools list error: {e}")
    
    # Test 2: Health Check
    print("\n2. Testing MCP Health Check...")
    try:
        response = requests.get(f"{base_url}/api/mcp/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ MCP Health: {health_data['status']}")
            print(f"   - Total Tools: {health_data['total_tools']}")
            print(f"   - Executor Status: {health_data['executor_status']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 3: Calculator Tool
    print("\n3. Testing Calculator Tool...")
    test_calculations = [
        "Calculate 15 * 23 + 45",
        "What is 100 / 4?",
        "Compute 2^8",
        "Solve 50 + 25 * 2"
    ]
    
    for calc in test_calculations[:2]:  # Test first 2
        try:
            response = requests.post(
                f"{base_url}/api/mcp/execute",
                json={"message": calc}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print(f"   ✅ {calc}")
                    print(f"      Result: {result['result']}")
                    print(f"      Time: {result['execution_time_ms']:.1f}ms")
                else:
                    print(f"   ❌ {calc}: {result.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ {calc}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {calc}: {e}")
    
    # Test 4: File Operations
    print("\n4. Testing File Operations...")
    try:
        # Test file listing
        response = requests.post(
            f"{base_url}/api/mcp/execute",
            json={"message": "List files in current directory"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"   ✅ File listing successful")
                print(f"      Result: {result['result'][:100]}...")
            else:
                print(f"   ❌ File listing failed: {result.get('error')}")
        else:
            print(f"   ❌ File listing: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ File operations error: {e}")
    
    # Test 5: System Information
    print("\n5. Testing System Information...")
    try:
        response = requests.post(
            f"{base_url}/api/mcp/execute",
            json={"message": "Get system information"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"   ✅ System info successful")
                # Extract key info from result
                result_text = result['result']
                if "Platform:" in result_text:
                    platform_line = [line for line in result_text.split('\n') if 'Platform:' in line][0]
                    print(f"      {platform_line}")
                if "CPU Count:" in result_text:
                    cpu_line = [line for line in result_text.split('\n') if 'CPU Count:' in line][0]
                    print(f"      {cpu_line}")
            else:
                print(f"   ❌ System info failed: {result.get('error')}")
        else:
            print(f"   ❌ System info: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ System info error: {e}")
    
    # Test 6: Knowledge Search
    print("\n6. Testing Knowledge Search...")
    try:
        response = requests.post(
            f"{base_url}/api/mcp/execute",
            json={"message": "Search for machine learning in knowledge base"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"   ✅ Knowledge search successful")
                print(f"      Result length: {len(result['result'])} characters")
                print(f"      Time: {result['execution_time_ms']:.1f}ms")
            else:
                print(f"   ❌ Knowledge search failed: {result.get('error')}")
        else:
            print(f"   ❌ Knowledge search: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Knowledge search error: {e}")
    
    # Test 7: Intent Detection
    print("\n7. Testing Intent Detection...")
    test_messages = [
        "Calculate 10 + 5",
        "List files in directory",
        "Search for AI news",
        "Get system status",
        "What is the weather like?"
    ]
    
    for message in test_messages[:3]:  # Test first 3
        try:
            response = requests.post(
                f"{base_url}/api/mcp/detect-intent",
                params={"message": message}
            )
            
            if response.status_code == 200:
                intent_data = response.json()
                tool = intent_data.get('detected_tool', 'none')
                has_intent = intent_data.get('has_intent', False)
                print(f"   '{message[:30]}...' → {tool} ({'✅' if has_intent else '❌'})")
            else:
                print(f"   ❌ Intent detection failed for: {message[:30]}...")
                
        except Exception as e:
            print(f"   ❌ Intent detection error for '{message[:30]}...': {e}")
    
    # Test 8: Tool Test Suite
    print("\n8. Testing Complete Tool Suite...")
    try:
        response = requests.post(f"{base_url}/api/mcp/test")
        
        if response.status_code == 200:
            test_data = response.json()
            total_tests = test_data['total_tests']
            successful_tests = test_data['successful_tests']
            
            print(f"   ✅ Tool Test Suite Results:")
            print(f"      Total Tests: {total_tests}")
            print(f"      Successful: {successful_tests}")
            print(f"      Success Rate: {successful_tests/total_tests*100:.1f}%")
            
            # Show individual test results
            for test_result in test_data['test_results']:
                status = "✅" if test_result['success'] else "❌"
                tool = test_result['tool']
                error = test_result.get('error', '')
                print(f"      {status} {tool}: {error[:50] if error else 'OK'}")
                
        else:
            print(f"   ❌ Tool test suite failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Tool test suite error: {e}")
    
    print("\n" + "=" * 50)
    print("🔧 Enhanced MCP Tools Testing Complete")

def test_mcp_performance():
    """Test MCP tools performance"""
    
    base_url = "http://localhost:8004"
    
    print("\n⚡ Testing MCP Tools Performance")
    print("=" * 50)
    
    # Test different tools with performance measurement
    performance_tests = [
        ("calculator", "Calculate 123 * 456 + 789"),
        ("system_info", "Get system information"),
        ("knowledge_search", "Search for artificial intelligence"),
        ("file_list", "List files in current directory")
    ]
    
    for tool_name, message in performance_tests:
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/api/mcp/execute",
                json={"message": message},
                timeout=10
            )
            end_time = time.time()
            
            total_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                result = response.json()
                api_time = result.get('execution_time_ms', 0)
                success = result.get('success', False)
                
                status = "✅" if success else "❌"
                print(f"{status} {tool_name}:")
                print(f"   Total Time: {total_time:.1f}ms")
                print(f"   API Time: {api_time:.1f}ms")
                print(f"   Overhead: {total_time - api_time:.1f}ms")
                
            else:
                print(f"❌ {tool_name}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {tool_name}: {e}")

def compare_old_vs_new_mcp():
    """Compare old simulated vs new functional MCP tools"""
    
    base_url = "http://localhost:8004"
    
    print("\n🔄 Comparing Old vs New MCP Tools")
    print("=" * 50)
    
    test_message = "Calculate 25 * 4 + 10"
    
    # Test new enhanced MCP
    print("\n1. Testing Enhanced MCP...")
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/mcp/execute",
            json={"message": test_message}
        )
        enhanced_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"✅ Enhanced MCP: {result['result']}")
                print(f"   Time: {enhanced_time:.1f}ms")
                print(f"   Tool Used: {result['tool_used']}")
            else:
                print(f"❌ Enhanced MCP failed: {result.get('error')}")
        else:
            print(f"❌ Enhanced MCP: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Enhanced MCP error: {e}")
    
    # Test old chat endpoint (if available)
    print("\n2. Testing Old Chat Endpoint...")
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/chat/",
            json={"message": test_message}
        )
        old_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Old Chat: {result.get('response', 'No response')[:100]}...")
            print(f"   Time: {old_time:.1f}ms")
            print(f"   Agent: {result.get('agent_used', 'Unknown')}")
        else:
            print(f"❌ Old Chat: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Old Chat error: {e}")

if __name__ == "__main__":
    print("🚀 Enhanced MCP Tools Test Suite")
    print("Make sure the API server is running on port 8004")
    
    try:
        # Test enhanced MCP tools
        test_enhanced_mcp_tools()
        
        # Test performance
        test_mcp_performance()
        
        # Test comparison
        compare_old_vs_new_mcp()
        
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
