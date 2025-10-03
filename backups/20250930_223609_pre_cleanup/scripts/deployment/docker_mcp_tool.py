#!/usr/bin/env python3
""'
Docker MCP Tool for Checking Next.js Containers and Images
Uses our existing MCP framework to check Docker resources
""'

import asyncio
import logging
import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src'))

from src.core.tools.mcp_adapter import MCPAdapter, create_stdio_adapter
from src.core.mcp.connection_manager import MCPConnectionManager

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DockerMCPTool:
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    ""'
    Docker MCP tool for checking containers and images.
    Integrates with our existing MCP framework.
    ""'

    def __init__(self):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.logger = logging.getLogger(__name__)
        self.mcp_adapter = None

    async def initialize(self):
        """Initialize MCP adapter.""'
        try:
            self.mcp_adapter = create_stdio_adapter()
            self.logger.info("✅ Docker MCP Tool initialized')
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize MCP adapter: {e}')
            return False

    async def check_docker_resources(self) -> Dict[str, Any]:
        """Check Docker containers and images for Next.js.""'

        self.logger.info("🐳 Checking Docker resources for Next.js...')

        results = {
            "containers': await self._check_containers(),
            "images': await self._check_images(),
            "nextjs_found': False,
            "recommendations': []
        }

        # Analyze results
        nextjs_containers = [c for c in results["containers'] if self._is_nextjs_container(c)]
        nextjs_images = [i for i in results["images'] if self._is_nextjs_image(i)]

        if nextjs_containers or nextjs_images:
            results["nextjs_found'] = True
            results["recommendations"].append("✅ Next.js containers/images found - can be reused')
        else:
            results["recommendations"].append("📦 No Next.js found - recommend creating new Next.js container')

        return results

    async def _check_containers(self) -> List[Dict[str, Any]]:
        """Check running and stopped containers.""'

        try:
            # Get all containers
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "json'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                self.logger.error(f"Docker ps failed: {result.stderr}')
                return []

            containers = []
            for line in result.stdout.strip().split("\n'):
                if line.strip():
                    try:
                        container = json.loads(line)
                        containers.append({
                            "id": container.get("ID", "'),
                            "name": container.get("Names", "'),
                            "image": container.get("Image", "'),
                            "status": container.get("Status", "'),
                            "ports": container.get("Ports", "'),
                            "created": container.get("CreatedAt", "'),
                            "is_nextjs': self._is_nextjs_container(container)
                        })
                    except json.JSONDecodeError:
                        continue

            self.logger.info(f"Found {len(containers)} containers')
            return containers

        except Exception as e:
            self.logger.error(f"Error checking containers: {e}')
            return []

    async def _check_images(self) -> List[Dict[str, Any]]:
        """Check Docker images.""'

        try:
            # Get all images
            result = subprocess.run(
                ["docker", "images", "--format", "json'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                self.logger.error(f"Docker images failed: {result.stderr}')
                return []

            images = []
            for line in result.stdout.strip().split("\n'):
                if line.strip():
                    try:
                        image = json.loads(line)
                        images.append({
                            "repository": image.get("Repository", "'),
                            "tag": image.get("Tag", "'),
                            "image_id": image.get("ID", "'),
                            "created": image.get("CreatedAt", "'),
                            "size": image.get("Size", "'),
                            "is_nextjs': self._is_nextjs_image(image)
                        })
                    except json.JSONDecodeError:
                        continue

            self.logger.info(f"Found {len(images)} images')
            return images

        except Exception as e:
            self.logger.error(f"Error checking images: {e}')
            return []

    def _is_nextjs_container(self, container: Dict[str, Any]) -> bool:
        """TODO: Add docstring."""
        """Check if container is Next.js related.""'

        name = container.get("name", "').lower()
        image = container.get("image", "').lower()

        nextjs_indicators = [
            "next", "nextjs", "react", "node", "frontend", "web',
            "nuxt", "gatsby", "vite", "webpack'
        ]

        return any(indicator in name or indicator in image for indicator in nextjs_indicators)

    def _is_nextjs_image(self, image: Dict[str, Any]) -> bool:
        """TODO: Add docstring."""
        """Check if image is Next.js related.""'

        repository = image.get("repository", "').lower()
        tag = image.get("tag", "').lower()

        nextjs_indicators = [
            "next", "nextjs", "react", "node", "frontend", "web',
            "nuxt", "gatsby", "vite", "webpack'
        ]

        return any(indicator in repository or indicator in tag for indicator in nextjs_indicators)

    async def create_nextjs_container(self) -> Dict[str, Any]:
        """Create a new Next.js container if none found.""'

        self.logger.info("🚀 Creating Next.js container...')

        try:
            # Create Next.js container using official Node.js image
            cmd = [
                "docker", "run", "-d',
                "--name", "agentic-nextjs-frontend',
                "-p", "3000:3000',
                "-v", f"{Path.cwd()}/frontend:/app',
                "-w", "/app',
                "node:18-alpine',
                "sh", "-c", "npm install && npm run dev'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                container_id = result.stdout.strip()
                return {
                    "success': True,
                    "container_id': container_id,
                    "message": "Next.js container created successfully',
                    "url": "http://localhost:3000'
                }
            else:
                return {
                    "success': False,
                    "error': result.stderr,
                    "message": "Failed to create Next.js container'
                }

        except Exception as e:
            return {
                "success': False,
                "error': str(e),
                "message": "Error creating Next.js container'
            }

    async def get_container_logs(self, container_name: str) -> str:
        """Get logs from a specific container.""'

        try:
            result = subprocess.run(
                ["docker", "logs', container_name],
                capture_output=True,
                text=True,
                timeout=10
            )

            return result.stdout if result.returncode == 0 else result.stderr

        except Exception as e:
            return f"Error getting logs: {e}'

# Example usage and testing
async def test_docker_mcp():
    """Test the Docker MCP tool.""'

    print("🐳 Docker MCP Tool Test')
    print("=' * 50)

    # Initialize tool
    docker_tool = DockerMCPTool()

    if not await docker_tool.initialize():
        print("❌ Failed to initialize Docker MCP tool')
        return

    # Check Docker resources
    results = await docker_tool.check_docker_resources()

    print(f"\n📊 Docker Resources Analysis:')
    print(f"   Containers: {len(results["containers"])}')
    print(f"   Images: {len(results["images"])}')
    print(f"   Next.js Found: {results["nextjs_found"]}')

    # Show Next.js related containers
    nextjs_containers = [c for c in results["containers"] if c.get("is_nextjs')]
    if nextjs_containers:
        print(f"\n✅ Next.js Containers Found:')
        for container in nextjs_containers:
            print(f"   - {container["name"]} ({container["image"]}) - {container["status"]}')
    else:
        print(f"\n❌ No Next.js containers found')

    # Show Next.js related images
    nextjs_images = [i for i in results["images"] if i.get("is_nextjs')]
    if nextjs_images:
        print(f"\n✅ Next.js Images Found:')
        for image in nextjs_images:
            print(f"   - {image["repository"]}:{image["tag"]}')
    else:
        print(f"\n❌ No Next.js images found')

    # Show recommendations
    print(f"\n💡 Recommendations:')
    for rec in results["recommendations']:
        print(f"   {rec}')

    # If no Next.js found, offer to create one
    if not results["nextjs_found']:
        print(f"\n🚀 Would you like to create a Next.js container?')
        print(f"   Run: python3 docker_mcp_tool.py --create-nextjs')

if __name__ == "__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Docker MCP Tool for Next.js')
    parser.add_argument("--create-nextjs", action="store_true", help="Create Next.js container')
    parser.add_argument("--check-only", action="store_true", help="Only check existing resources')

    args = parser.parse_args()

    if args.create_nextjs:
        async def create_nextjs():
            docker_tool = DockerMCPTool()
            await docker_tool.initialize()
            result = await docker_tool.create_nextjs_container()
            print(f"🚀 Next.js Container Creation:')
            print(f"   Success: {result["success"]}')
            print(f"   Message: {result["message"]}')
            if result["success']:
                print(f"   Container ID: {result["container_id"]}')
                print(f"   URL: {result["url"]}')
            else:
                print(f"   Error: {result.get("error", "Unknown error")}')

        asyncio.run(create_nextjs())
    else:
        asyncio.run(test_docker_mcp())
