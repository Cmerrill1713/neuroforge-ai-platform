#!/usr/bin/env python3
"""
MCP Agent CLI
Simple command-line interface for agents to use MCP tools
"""

import asyncio
import argparse
import json
import sys
import requests
from typing import Dict, Any

class MCPAgentCLI:
    """CLI for MCP Agent tools"""
    
    def __init__(self, server_url: str = "http://localhost:8002"):
        self.server_url = server_url
    
    def call_tool(self, tool_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Call a tool via HTTP API"""
        try:
            url = f"{self.server_url}/execute"
            payload = {
                "tool_name": tool_name,
                "args": list(args),
                "kwargs": kwargs
            }
            
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools"""
        try:
            response = requests.get(f"{self.server_url}/tools", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_health(self) -> Dict[str, Any]:
        """Get server health"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

def main():
    parser = argparse.ArgumentParser(
        description="MCP Agent CLI - Command-line interface for AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available tools
  python3 mcp_agent_cli.py list
  
  # Execute a tool
  python3 mcp_agent_cli.py execute calculator "15 * 23 + 45"
  python3 mcp_agent_cli.py execute web_search "artificial intelligence"
  python3 mcp_agent_cli.py execute read_file "README.md"
  
  # File operations
  python3 mcp_agent_cli.py file read "README.md"
  python3 mcp_agent_cli.py file list "."
  
  # Web operations
  python3 mcp_agent_cli.py web search "machine learning"
  python3 mcp_agent_cli.py web crawl "https://example.com"
  
  # Knowledge operations
  python3 mcp_agent_cli.py knowledge search "AI research"
  python3 mcp_agent_cli.py knowledge store "New AI technique" "research"
  
  # System operations
  python3 mcp_agent_cli.py system info
  python3 mcp_agent_cli.py command "ls -la"
  
  # Learning operations
  python3 mcp_agent_cli.py learn '{"input": "hello", "output": "world"}'
  python3 mcp_agent_cli.py memory "hello world"
        """
    )
    
    parser.add_argument("--server", "-s", default="http://localhost:8002", help="MCP server URL")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List command
    subparsers.add_parser("list", help="List available tools")
    
    # Health command
    subparsers.add_parser("health", help="Check server health")
    
    # Execute command
    execute_parser = subparsers.add_parser("execute", help="Execute a tool")
    execute_parser.add_argument("tool_name", help="Tool name")
    execute_parser.add_argument("args", nargs="*", help="Tool arguments")
    
    # File operations
    file_parser = subparsers.add_parser("file", help="File operations")
    file_subparsers = file_parser.add_subparsers(dest="file_op")
    file_subparsers.add_parser("list", help="List files")
    file_subparsers.add_parser("read", help="Read file")
    file_subparsers.add_parser("write", help="Write file")
    
    # Web operations
    web_parser = subparsers.add_parser("web", help="Web operations")
    web_subparsers = web_parser.add_subparsers(dest="web_op")
    web_subparsers.add_parser("search", help="Web search")
    web_subparsers.add_parser("crawl", help="Web crawl")
    
    # Knowledge operations
    knowledge_parser = subparsers.add_parser("knowledge", help="Knowledge operations")
    knowledge_subparsers = knowledge_parser.add_subparsers(dest="knowledge_op")
    knowledge_subparsers.add_parser("search", help="Search knowledge")
    knowledge_subparsers.add_parser("store", help="Store knowledge")
    
    # System operations
    system_parser = subparsers.add_parser("system", help="System operations")
    system_subparsers = system_parser.add_subparsers(dest="system_op")
    system_subparsers.add_parser("info", help="System info")
    
    # Command execution
    command_parser = subparsers.add_parser("command", help="Execute command")
    command_parser.add_argument("cmd", help="Command to execute")
    
    # Learning operations
    learn_parser = subparsers.add_parser("learn", help="Learn from example")
    learn_parser.add_argument("example", help="Example data (JSON)")
    
    memory_parser = subparsers.add_parser("memory", help="Retrieve memory")
    memory_parser.add_argument("query", help="Memory query")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = MCPAgentCLI(args.server)
    
    def print_result(result: Dict[str, Any]):
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result.get("success"):
                print("✅ Success")
                if "result" in result:
                    print(f"📊 Result: {result['result']}")
                if "count" in result:
                    print(f"📈 Count: {result['count']}")
                if args.verbose:
                    print(f"🔍 Full result: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    # Execute commands
    if args.command == "list":
        result = cli.list_tools()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result.get("success"):
                print("🔧 Available Tools:")
                for tool in result.get("tools", []):
                    print(f"   • {tool.get('name', 'unknown')}")
                print(f"\n📊 Total: {result.get('count', 0)} tools")
            else:
                print(f"❌ Error: {result.get('error')}")
    
    elif args.command == "health":
        result = cli.get_health()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result.get("status") == "healthy":
                print("✅ MCP Server is healthy")
                print(f"🔧 Tools available: {result.get('tools_count', 0)}")
            else:
                print(f"❌ Server error: {result.get('error', 'Unknown')}")
    
    elif args.command == "execute":
        result = cli.call_tool(args.tool_name, *args.args)
        print_result(result)
    
    elif args.command == "file":
        if args.file_op == "list":
            directory = args.args[0] if args.args else "."
            result = cli.call_tool("list_directory", directory)
            print_result(result)
        elif args.file_op == "read":
            if not args.args:
                print("❌ Error: File path required")
                return
            result = cli.call_tool("read_file", args.args[0])
            print_result(result)
        elif args.file_op == "write":
            if len(args.args) < 2:
                print("❌ Error: File path and content required")
                return
            result = cli.call_tool("write_file", args.args[0], args.args[1])
            print_result(result)
    
    elif args.command == "web":
        if args.web_op == "search":
            if not args.args:
                print("❌ Error: Search query required")
                return
            result = cli.call_tool("web_search", args.args[0])
            print_result(result)
        elif args.web_op == "crawl":
            if not args.args:
                print("❌ Error: URL required")
                return
            result = cli.call_tool("web_crawl", args.args[0])
            print_result(result)
    
    elif args.command == "knowledge":
        if args.knowledge_op == "search":
            if not args.args:
                print("❌ Error: Search query required")
                return
            result = cli.call_tool("search_knowledge", args.args[0])
            print_result(result)
        elif args.knowledge_op == "store":
            if len(args.args) < 2:
                print("❌ Error: Knowledge and category required")
                return
            result = cli.call_tool("store_knowledge", args.args[0], category=args.args[1])
            print_result(result)
    
    elif args.command == "system":
        if args.system_op == "info":
            result = cli.call_tool("get_system_info")
            print_result(result)
    
    elif args.command == "command":
        result = cli.call_tool("execute_command", args.cmd)
        print_result(result)
    
    elif args.command == "learn":
        try:
            example = json.loads(args.example)
            result = cli.call_tool("learn_from_example", example)
            print_result(result)
        except json.JSONDecodeError:
            print("❌ Error: Invalid JSON in example")
    
    elif args.command == "memory":
        result = cli.call_tool("retrieve_memory", args.query)
        print_result(result)

if __name__ == "__main__":
    main()
