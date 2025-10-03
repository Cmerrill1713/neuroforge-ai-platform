#!/usr/bin/env python3
""'
Test script for Official Material-UI MCP Server
Based on: https://mui.com/material-ui/getting-started/mcp/
""'

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_mui_mcp_official():
    """Test the official Material-UI MCP server.""'

    print("🎨 Testing Official Material-UI MCP Server')
    print("=' * 60)
    print("📖 Documentation: https://mui.com/material-ui/getting-started/mcp/')
    print()

    # Test requests based on MUI MCP documentation
    test_requests = [
        {
            "jsonrpc": "2.0',
            "id': 1,
            "method": "tools/list'
        },
        {
            "jsonrpc": "2.0',
            "id': 2,
            "method": "tools/call',
            "params': {
                "name": "useMuiDocs',
                "arguments': {
                    "package": "material-ui',
                    "query": "Button component'
                }
            }
        },
        {
            "jsonrpc": "2.0',
            "id': 3,
            "method": "tools/call',
            "params': {
                "name": "fetchDocs',
                "arguments': {
                    "url": "https://mui.com/material-ui/react-button/'
                }
            }
        }
    ]

    try:
        # Start the official MUI MCP server process
        print("🚀 Starting Official MUI MCP Server...')
        server_process = subprocess.Popen(
            ["npx", "-y", "@mui/mcp@latest'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path.cwd()
        )

        print("✅ Official MUI MCP Server started')
        print("📦 Package: @mui/mcp@latest')
        print()

        # Send test requests
        for i, request in enumerate(test_requests, 1):
            print(f"📤 Test {i}: {request["method"]}')
            if request["method"] == "tools/call':
                print(f"   Tool: {request["params"]["name"]}')
                print(f"   Args: {request["params"]["arguments"]}')

            # Send request
            request_json = json.dumps(request) + "\n'
            server_process.stdin.write(request_json)
            server_process.stdin.flush()

            # Read response
            response_line = server_process.stdout.readline()
            if response_line:
                try:
                    response = json.loads(response_line.strip())
                    print(f"📥 Response received')

                    # Handle tools/list response
                    if request["method"] == "tools/list" and "result' in response:
                        tools = response["result"].get("tools', [])
                        print(f"   Available tools: {len(tools)}')
                        for tool in tools:
                            print(f"   - {tool.get("name", "Unknown")}: {tool.get("description", "No description")}')

                    # Handle tool call responses
                    elif request["method"] == "tools/call" and "result' in response:
                        result = response["result']
                        if "content' in result:
                            content = result["content']
                            if isinstance(content, list) and len(content) > 0:
                                first_content = content[0]
                                if "text' in first_content:
                                    text_content = first_content["text']
                                    # Truncate long content for display
                                    if len(text_content) > 200:
                                        print(f"   Content preview: {text_content[:200]}...')
                                    else:
                                        print(f"   Content: {text_content}')
                                else:
                                    print(f"   Content: {first_content}')
                            else:
                                print(f"   Content: {content}')
                        else:
                            print(f"   Result: {result}')

                    # Handle errors
                    elif "error' in response:
                        error = response["error']
                        print(f"   ❌ Error: {error.get("message", "Unknown error")}')
                        if "code' in error:
                            print(f"   Code: {error["code"]}')

                    else:
                        print(f"   Response: {response}')

                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse response: {e}')
                    print(f"   Raw response: {response_line}')
            else:
                print("❌ No response received')

            print()

        # Test MCP Inspector connection info
        print("🔍 MCP Inspector Information:')
        print("   To debug the MCP connection, run:')
        print("   npx @modelcontextprotocol/inspector')
        print("   Then use:')
        print("   - Transport type: Stdio')
        print("   - Command: npx')
        print("   - Arguments: -y @mui/mcp@latest')
        print()

        # Show integration instructions
        print("💡 Integration Instructions:')
        print("   For VS Code/Cursor:')
        print("   1. Settings -> MCP -> Add Server')
        print("   2. Add the configuration from mcp.json')
        print("   3. Enable chat.mcp.enabled: true in settings.json')
        print()
        print("   For Claude Code:')
        print("   claude mcp add mui-mcp -- npx -y @mui/mcp@latest')
        print()

    except FileNotFoundError:
        print("❌ Error: npx not found. Please install Node.js and npm.')
        print("   Download from: https://nodejs.org/')
    except Exception as e:
        print(f"❌ Error testing MUI MCP server: {e}')

    finally:
        # Clean up
        if "server_process' in locals():
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            print("🛑 MUI MCP Server stopped')

    print("=' * 60)
    print("🎯 Official MUI MCP Server Test Complete')
    print()
    print("📚 Benefits of Official MUI MCP:')
    print("   ✅ Real, direct sources in answers')
    print("   ✅ Links to actual documentation (no 404s)')
    print("   ✅ Component code from official registries')
    print("   ✅ Up-to-date Material-UI documentation')
    print()
    print("🔗 Documentation: https://mui.com/material-ui/getting-started/mcp/')

if __name__ == "__main__':
    asyncio.run(test_mui_mcp_official())
