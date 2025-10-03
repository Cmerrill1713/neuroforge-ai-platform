#!/usr/bin/env python3
""'
Test script for MCP Transcript Service
""'

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src'))

from mcp_transcript_service import MCPTranscriptService

async def test_transcript_service():
    """Test the MCP transcript service""'

    print("🧪 Testing MCP Transcript Service')
    print("=' * 40)

    # Initialize service
    service = MCPTranscriptService()

    # Test GitHub crawling
    print("\n📊 Testing GitHub repository crawling...')
    github_result = await service.handle_tool_call("crawl_github_repos", {"username": "indydevdan'})
    print(f"GitHub Result: {json.dumps(github_result, indent=2)}')

    # Test stats
    print("\n📈 Testing transcript stats...')
    stats_result = await service.handle_tool_call("get_transcript_stats', {})
    print(f"Stats Result: {json.dumps(stats_result, indent=2)}')

    # Test search (if we have content)
    if stats_result.get("success") and stats_result["data"]["total_entries'] > 0:
        print("\n🔍 Testing transcript search...')
        search_result = await service.handle_tool_call("search_transcripts', {
            "query": "python',
            "source_type": "all'
        })
        print(f"Search Result: {json.dumps(search_result, indent=2)}')

    print("\n✅ MCP Transcript Service test completed!')

if __name__ == "__main__':
    asyncio.run(test_transcript_service())
