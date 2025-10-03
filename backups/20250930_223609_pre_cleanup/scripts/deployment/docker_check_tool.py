#!/usr/bin/env python3
""'
Docker Check Tool for Next.js
Simple tool to check Docker containers and images for Next.js
""'

import subprocess
import json
import logging
from typing import Dict, Any, List
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DockerChecker:
    """TODO: Add docstring."""
    """Simple Docker checker for Next.js resources.""'

    def __init__(self):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.logger = logging.getLogger(__name__)

    def check_docker_resources(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
        """Check Docker containers and images for Next.js.""'

        self.logger.info("🐳 Checking Docker resources for Next.js...')

        results = {
            "containers': self._check_containers(),
            "images': self._check_images(),
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

    def _check_containers(self) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
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

    def _check_images(self) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
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

    def create_nextjs_container(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
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

def main():
    """TODO: Add docstring."""
    """Main function to check Docker resources.""'

    print("🐳 Docker Check Tool for Next.js')
    print("=' * 50)

    # Initialize checker
    checker = DockerChecker()

    # Check Docker resources
    results = checker.check_docker_resources()

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

    # Show existing containers that might be useful
    print(f"\n🔍 Existing Containers Analysis:')
    for container in results["containers']:
        if container["status"].startswith("Up'):
            print(f"   ✅ {container["name"]} - {container["image"]} - {container["status"]}')
        else:
            print(f"   ⚠️  {container["name"]} - {container["image"]} - {container["status"]}')

    # Show available Node.js images
    node_images = [i for i in results["images"] if "node" in i["repository'].lower()]
    if node_images:
        print(f"\n📦 Available Node.js Images:')
        for image in node_images:
            print(f"   - {image["repository"]}:{image["tag"]} ({image["size"]})')

    # If no Next.js found, show how to create one
    if not results["nextjs_found']:
        print(f"\n🚀 To create a Next.js container:')
        print(f"   1. Create frontend directory: mkdir frontend')
        print(f"   2. Initialize Next.js: cd frontend && npx create-next-app@latest . --typescript --tailwind')
        print(f"   3. Create Dockerfile:')
        print(f"      FROM node:18-alpine')
        print(f"      WORKDIR /app')
        print(f"      COPY package*.json ./')
        print(f"      RUN npm install')
        print(f"      COPY . .')
        print(f"      EXPOSE 3000')
        print(f"      CMD [\"npm\", \"run\", \"dev\"]')
        print(f"   4. Build and run: docker build -t agentic-nextjs . && docker run -p 3000:3000 agentic-nextjs')

if __name__ == "__main__':
    main()
