#!/usr/bin/env python3
"""
Comprehensive CLI Tool Suite for MCP System
Command-line interface for all MCP tools and system operations
"""

import asyncio
import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.tools.comprehensive_mcp_executor import ComprehensiveMCPExecutor

class MCPCLI:
    """Comprehensive CLI for MCP tools"""
    
    def __init__(self):
        self.executor = ComprehensiveMCPExecutor()
        self.available_tools = [
            # Web & Search Tools
            "web_search", "web_crawl", "news_search",
            
            # File & System Tools
            "file_read", "file_write", "file_list", "system_info",
            
            # Math & Calculation Tools
            "calculator", "statistics",
            
            # Data & Analysis Tools
            "json_parser", "csv_analyzer",
            
            # Code & Development Tools
            "code_executor", "git_operations",
            
            # Knowledge & RAG Tools
            "knowledge_search", "rag_query",
            
            # Utility Tools
            "password_generator", "timezone_converter"
        ]
    
    async def run_tool(self, tool_name: str, message: str, **kwargs) -> Dict[str, Any]:
        """Run a specific tool"""
        async with self.executor as executor:
            return await executor.execute_tool(tool_name, message, **kwargs)
    
    async def detect_and_run(self, message: str) -> Dict[str, Any]:
        """Detect tool intent and run automatically"""
        async with self.executor as executor:
            tool_name = await executor.detect_tool_intent(message)
            if tool_name:
                result = await executor.execute_tool(tool_name, message)
                return {
                    "success": True,
                    "detected_tool": tool_name,
                    "result": result
                }
            else:
                return {
                    "success": False,
                    "message": "No tool intent detected",
                    "available_tools": self.available_tools
                }
    
    def print_result(self, result: Dict[str, Any], verbose: bool = False):
        """Print formatted result"""
        if result.get("success"):
            print(f"✅ {result.get('tool', 'Tool')} executed successfully")
            
            if verbose:
                print(f"📊 Full result: {json.dumps(result, indent=2)}")
            else:
                # Print key information
                if "result" in result:
                    print(f"📝 Result: {result['result']}")
                if "count" in result:
                    print(f"📊 Count: {result['count']}")
                if "query" in result:
                    print(f"🔍 Query: {result['query']}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")

def main():
    parser = argparse.ArgumentParser(
        description="MCP CLI Tool Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect and run tools
  python3 mcp_cli.py "Calculate 15 * 23 + 45"
  python3 mcp_cli.py "Search for AI news"
  python3 mcp_cli.py "List files in current directory"
  
  # Run specific tools
  python3 mcp_cli.py --tool calculator "15 * 23 + 45"
  python3 mcp_cli.py --tool web_search "artificial intelligence"
  python3 mcp_cli.py --tool file_list --directory .
  
  # Interactive mode
  python3 mcp_cli.py --interactive
  
  # System information
  python3 mcp_cli.py --tool system_info
  
  # Generate password
  python3 mcp_cli.py --tool password_generator --length 16
  
  # Knowledge search
  python3 mcp_cli.py --tool knowledge_search "machine learning"
        """
    )
    
    parser.add_argument("message", nargs="?", help="Message or query to process")
    parser.add_argument("--tool", "-t", choices=[
        "web_search", "web_crawl", "news_search",
        "file_read", "file_write", "file_list", "system_info",
        "calculator", "statistics",
        "json_parser", "csv_analyzer",
        "code_executor", "git_operations",
        "knowledge_search", "rag_query",
        "password_generator", "timezone_converter"
    ], help="Specific tool to use")
    
    # Tool-specific arguments
    parser.add_argument("--directory", "-d", help="Directory for file operations")
    parser.add_argument("--file-path", "-f", help="File path for file operations")
    parser.add_argument("--content", "-c", help="Content for file write operations")
    parser.add_argument("--length", "-l", type=int, default=16, help="Password length")
    parser.add_argument("--url", "-u", help="URL for web operations")
    parser.add_argument("--data", help="Data for analysis tools")
    
    # Output options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    async def run_cli():
        cli = MCPCLI()
        
        if args.interactive:
            print("🚀 MCP CLI Interactive Mode")
            print("Type 'help' for available commands, 'quit' to exit")
            print("=" * 50)
            
            while True:
                try:
                    user_input = input("\n💬 Enter command: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        print("👋 Goodbye!")
                        break
                    
                    if user_input.lower() == 'help':
                        print("\n📋 Available tools:")
                        for tool in cli.available_tools:
                            print(f"   • {tool}")
                        print("\n💡 Examples:")
                        print("   • Calculate 15 * 23 + 45")
                        print("   • Search for AI news")
                        print("   • List files in current directory")
                        print("   • Generate password")
                        continue
                    
                    if not user_input:
                        continue
                    
                    result = await cli.detect_and_run(user_input)
                    
                    if args.json:
                        print(json.dumps(result, indent=2))
                    else:
                        cli.print_result(result, args.verbose)
                        
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        elif args.tool:
            # Run specific tool
            kwargs = {}
            if args.directory:
                kwargs['directory'] = args.directory
            if args.file_path:
                kwargs['file_path'] = args.file_path
            if args.content:
                kwargs['content'] = args.content
            if args.length:
                kwargs['length'] = args.length
            if args.url:
                kwargs['url'] = args.url
            if args.data:
                kwargs['data'] = args.data
            
            result = await cli.run_tool(args.tool, args.message or "", **kwargs)
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                cli.print_result(result, args.verbose)
        
        elif args.message:
            # Auto-detect and run
            result = await cli.detect_and_run(args.message)
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                cli.print_result(result, args.verbose)
        
        else:
            parser.print_help()
    
    # Run the CLI
    try:
        asyncio.run(run_cli())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
