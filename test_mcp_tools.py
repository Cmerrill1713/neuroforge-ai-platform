#!/usr/bin/env python3
"""
Test Comprehensive MCP Tool Suite
"""

import asyncio
import sys
import os
sys.path.append('src')

from core.tools.comprehensive_mcp_executor import ComprehensiveMCPExecutor

async def test_mcp_tools():
    print("🧪 TESTING COMPREHENSIVE MCP TOOL SUITE")
    print("=====================================")
    
    async with ComprehensiveMCPExecutor() as executor:
        # Test tool detection
        print("\n1. Testing tool detection...")
        test_messages = [
            "Calculate 15 * 23 + 45",
            "Search for artificial intelligence news",
            "List files in current directory",
            "Generate a secure password",
            "What's the current time in Tokyo?"
        ]
        
        for message in test_messages:
            tool = await executor.detect_tool_intent(message)
            print(f"   '{message}' → {tool}")
        
        # Test calculator
        print("\n2. Testing calculator...")
        result = await executor.execute_tool("calculator", "Calculate 15 * 23 + 45")
        print(f"   Result: {result}")
        
        # Test file operations
        print("\n3. Testing file operations...")
        result = await executor.execute_tool("file_list", "List files", directory=".")
        print(f"   Files found: {result.get('count', 0)}")
        
        # Test system info
        print("\n4. Testing system info...")
        result = await executor.execute_tool("system_info", "Get system information")
        print(f"   Platform: {result.get('platform', 'unknown')}")
        print(f"   CPU count: {result.get('cpu_count', 'unknown')}")
        
        # Test password generator
        print("\n5. Testing password generator...")
        result = await executor.execute_tool("password_generator", "Generate password", length=12)
        print(f"   Generated password: {result.get('password', 'failed')}")
        
        print("\n🎉 MCP Tool Suite Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
