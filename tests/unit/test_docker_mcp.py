#!/usr/bin/env python3
""'
Test script for MCP Docker Server
""'

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_docker_mcp_server():
    """Test the Docker MCP server.""'

    print("🐳 Testing MCP Docker Server')
    print("=' * 50)

    # Test requests
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
                "name": "docker_system_info',
                "arguments': {}
            }
        },
        {
            "jsonrpc": "2.0',
            "id': 3,
            "method": "tools/call',
            "params': {
                "name": "docker_list_containers',
                "arguments": {"all': True}
            }
        },
        {
            "jsonrpc": "2.0',
            "id': 4,
            "method": "tools/call',
            "params': {
                "name": "docker_list_images',
                "arguments': {}
            }
        }
    ]

    try:
        # Start the MCP server process
        server_process = subprocess.Popen(
            [sys.executable, "mcp_docker_server.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path.cwd()
        )

        print("✅ MCP Docker Server started')

        # Send test requests
        for i, request in enumerate(test_requests, 1):
            print(f"\n📤 Test {i}: {request["method"]}')

            # Send request
            request_json = json.dumps(request) + "\n'
            server_process.stdin.write(request_json)
            server_process.stdin.flush()

            # Read response
            response_line = server_process.stdout.readline()
            if response_line:
                try:
                    response = json.loads(response_line.strip())
                    print(f"📥 Response: {response.get("result", response.get("error", "No result"))}')

                    # Pretty print for tools/list
                    if request["method"] == "tools/list" and "result' in response:
                        tools = response["result"].get("tools', [])
                        print(f"   Available tools: {len(tools)}')
                        for tool in tools:
                            print(f"   - {tool["name"]}: {tool["description"]}')

                    # Pretty print for system info
                    elif request["method"] == "tools/call" and request["params"]["name"] == "docker_system_info':
                        if "result" in response and "content" in response["result']:
                            content = response["result"]["content"][0]["text']
                            system_info = json.loads(content)
                            print(f"   Docker Available: {system_info.get("docker_available", False)}')
                            if "version' in system_info:
                                version = system_info["version']
                                if isinstance(version, dict) and "Client' in version:
                                    print(f"   Docker Version: {version["Client"].get("Version", "Unknown")}')

                    # Pretty print for containers
                    elif request["method"] == "tools/call" and request["params"]["name"] == "docker_list_containers':
                        if "result" in response and "content" in response["result']:
                            content = response["result"]["content"][0]["text']
                            containers_info = json.loads(content)
                            print(f"   Total Containers: {containers_info.get("total_count", 0)}')
                            nextjs_containers = containers_info.get("nextjs_containers', [])
                            print(f"   Next.js Containers: {len(nextjs_containers)}')
                            for container in nextjs_containers[:3]:  # Show first 3
                                print(f"     - {container.get("name", "Unknown")} ({container.get("status", "Unknown")})')

                    # Pretty print for images
                    elif request["method"] == "tools/call" and request["params"]["name"] == "docker_list_images':
                        if "result" in response and "content" in response["result']:
                            content = response["result"]["content"][0]["text']
                            images_info = json.loads(content)
                            print(f"   Total Images: {images_info.get("total_count", 0)}')
                            nextjs_images = images_info.get("nextjs_images', [])
                            print(f"   Next.js Images: {len(nextjs_images)}')
                            for image in nextjs_images[:3]:  # Show first 3
                                print(f"     - {image.get("repository", "Unknown")}:{image.get("tag", "Unknown")}')

                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse response: {e}')
                    print(f"   Raw response: {response_line}')
            else:
                print("❌ No response received')

        # Test container creation (optional)
        print(f"\n🚀 Testing Next.js container creation...')
        create_request = {
            "jsonrpc": "2.0',
            "id': 5,
            "method": "tools/call',
            "params': {
                "name": "docker_create_nextjs_container',
                "arguments': {
                    "name": "test-nextjs-mcp',
                    "port': 3001,
                    "project_path": "./frontend'
                }
            }
        }

        request_json = json.dumps(create_request) + "\n'
        server_process.stdin.write(request_json)
        server_process.stdin.flush()

        response_line = server_process.stdout.readline()
        if response_line:
            try:
                response = json.loads(response_line.strip())
                if "result" in response and "content" in response["result']:
                    content = response["result"]["content"][0]["text']
                    create_result = json.loads(content)
                    if create_result.get("success'):
                        print(f"✅ Container created: {create_result.get("container_name")}')
                        print(f"   URL: {create_result.get("url")}')
                        print(f"   Container ID: {create_result.get("container_id", "Unknown")[:12]}...')
                    else:
                        print(f"⚠️  Container creation failed: {create_result.get("error", "Unknown error")}')
                        if "suggestion' in create_result:
                            print(f"   Suggestion: {create_result["suggestion"]}')
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse create response: {e}')

    except Exception as e:
        print(f"❌ Error testing MCP server: {e}')

    finally:
        # Clean up
        if "server_process' in locals():
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            print("\n🛑 MCP Docker Server stopped')

    print("\n" + "=' * 50)
    print("🎯 MCP Docker Server Test Complete')
    print("\n💡 Usage:')
    print("   1. Add to your MCP client configuration:')
    print("   2. Use tools: docker_list_containers, docker_list_images, etc.')
    print("   3. Create Next.js containers with docker_create_nextjs_container')

if __name__ == "__main__':
    asyncio.run(test_docker_mcp_server())
