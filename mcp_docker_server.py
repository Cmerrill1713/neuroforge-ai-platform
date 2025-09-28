#!/usr/bin/env python3
"""
MCP Docker Server - Proper MCP Protocol Implementation
Provides Docker container and image management via MCP protocol
"""

import asyncio
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPDockerServer:
    """MCP server for Docker operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tools = {
            "docker_list_containers": {
                "name": "docker_list_containers",
                "description": "List all Docker containers (running and stopped)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "all": {
                            "type": "boolean",
                            "description": "Include stopped containers",
                            "default": True
                        }
                    }
                }
            },
            "docker_list_images": {
                "name": "docker_list_images",
                "description": "List all Docker images",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "docker_container_logs": {
                "name": "docker_container_logs",
                "description": "Get logs from a Docker container",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "container": {
                            "type": "string",
                            "description": "Container name or ID"
                        },
                        "tail": {
                            "type": "integer",
                            "description": "Number of lines to show from end",
                            "default": 100
                        }
                    },
                    "required": ["container"]
                }
            },
            "docker_create_nextjs_container": {
                "name": "docker_create_nextjs_container",
                "description": "Create a new Next.js development container",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Container name",
                            "default": "nextjs-dev"
                        },
                        "port": {
                            "type": "integer",
                            "description": "Port to expose",
                            "default": 3000
                        },
                        "project_path": {
                            "type": "string",
                            "description": "Path to Next.js project",
                            "default": "./frontend"
                        }
                    }
                }
            },
            "docker_system_info": {
                "name": "docker_system_info",
                "description": "Get Docker system information",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": list(self.tools.values())
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_arguments = params.get("arguments", {})
                
                if tool_name not in self.tools:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Tool not found: {tool_name}"
                        }
                    }
                
                result = await self._execute_tool(tool_name, tool_arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        
        except Exception as e:
            self.logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Docker tool."""
        try:
            if tool_name == "docker_list_containers":
                return await self._list_containers(arguments.get("all", True))
            
            elif tool_name == "docker_list_images":
                return await self._list_images()
            
            elif tool_name == "docker_container_logs":
                container = arguments.get("container")
                tail = arguments.get("tail", 100)
                return await self._get_container_logs(container, tail)
            
            elif tool_name == "docker_create_nextjs_container":
                name = arguments.get("name", "nextjs-dev")
                port = arguments.get("port", 3000)
                project_path = arguments.get("project_path", "./frontend")
                return await self._create_nextjs_container(name, port, project_path)
            
            elif tool_name == "docker_system_info":
                return await self._get_system_info()
            
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        
        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": str(e)}
    
    async def _list_containers(self, show_all: bool = True) -> Dict[str, Any]:
        """List Docker containers."""
        try:
            # Check if Docker is available first
            docker_check = subprocess.run(
                ["which", "docker"],
                capture_output=True, text=True, timeout=5
            )
            
            if docker_check.returncode != 0:
                return {
                    "success": False,
                    "error": "Docker is not installed or not in PATH",
                    "containers": [],
                    "help": "Install Docker Desktop from https://docker.com/products/docker-desktop"
                }
            
            cmd = ["docker", "ps", "--format", "json"]
            if show_all:
                cmd.append("-a")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr,
                    "containers": [],
                    "help": "Make sure Docker daemon is running"
                }
            
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        container = json.loads(line)
                        containers.append({
                            "id": container.get("ID", ""),
                            "name": container.get("Names", ""),
                            "image": container.get("Image", ""),
                            "status": container.get("Status", ""),
                            "ports": container.get("Ports", ""),
                            "created": container.get("CreatedAt", ""),
                            "is_nextjs": self._is_nextjs_related(container.get("Image", "") + " " + container.get("Names", ""))
                        })
                    except json.JSONDecodeError:
                        continue
            
            return {
                "success": True,
                "containers": containers,
                "total_count": len(containers),
                "nextjs_containers": [c for c in containers if c.get("is_nextjs")]
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "containers": []
            }
    
    async def _list_images(self) -> Dict[str, Any]:
        """List Docker images."""
        try:
            # Check if Docker is available first
            docker_check = subprocess.run(
                ["which", "docker"],
                capture_output=True, text=True, timeout=5
            )
            
            if docker_check.returncode != 0:
                return {
                    "success": False,
                    "error": "Docker is not installed or not in PATH",
                    "images": [],
                    "help": "Install Docker Desktop from https://docker.com/products/docker-desktop"
                }
            
            result = subprocess.run(
                ["docker", "images", "--format", "json"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr,
                    "images": [],
                    "help": "Make sure Docker daemon is running"
                }
            
            images = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        image = json.loads(line)
                        images.append({
                            "repository": image.get("Repository", ""),
                            "tag": image.get("Tag", ""),
                            "image_id": image.get("ID", ""),
                            "created": image.get("CreatedAt", ""),
                            "size": image.get("Size", ""),
                            "is_nextjs": self._is_nextjs_related(image.get("Repository", "") + ":" + image.get("Tag", ""))
                        })
                    except json.JSONDecodeError:
                        continue
            
            return {
                "success": True,
                "images": images,
                "total_count": len(images),
                "nextjs_images": [i for i in images if i.get("is_nextjs")]
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "images": []
            }
    
    async def _get_container_logs(self, container: str, tail: int = 100) -> Dict[str, Any]:
        """Get container logs."""
        try:
            result = subprocess.run(
                ["docker", "logs", "--tail", str(tail), container],
                capture_output=True, text=True, timeout=10
            )
            
            return {
                "success": result.returncode == 0,
                "container": container,
                "logs": result.stdout if result.returncode == 0 else result.stderr,
                "lines": len(result.stdout.split('\n')) if result.returncode == 0 else 0
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "logs": ""
            }
    
    async def _create_nextjs_container(self, name: str, port: int, project_path: str) -> Dict[str, Any]:
        """Create a Next.js development container."""
        try:
            # Check if container already exists
            check_result = subprocess.run(
                ["docker", "ps", "-a", "--filter", f"name={name}", "--format", "{{.Names}}"],
                capture_output=True, text=True
            )
            
            if name in check_result.stdout:
                return {
                    "success": False,
                    "error": f"Container '{name}' already exists",
                    "suggestion": f"Use 'docker rm {name}' to remove it first"
                }
            
            # Create the container
            cmd = [
                "docker", "run", "-d",
                "--name", name,
                "-p", f"{port}:3000",
                "-v", f"{Path.cwd() / project_path}:/app",
                "-w", "/app",
                "node:18-alpine",
                "sh", "-c", "npm install && npm run dev"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                container_id = result.stdout.strip()
                return {
                    "success": True,
                    "container_id": container_id,
                    "container_name": name,
                    "port": port,
                    "url": f"http://localhost:{port}",
                    "message": "Next.js container created successfully"
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "message": "Failed to create Next.js container"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Error creating Next.js container"
            }
    
    async def _get_system_info(self) -> Dict[str, Any]:
        """Get Docker system information."""
        try:
            # Check if Docker is available
            docker_check = subprocess.run(
                ["which", "docker"],
                capture_output=True, text=True, timeout=5
            )
            
            system_info = {
                "success": True,
                "docker_installed": docker_check.returncode == 0,
                "docker_path": docker_check.stdout.strip() if docker_check.returncode == 0 else None,
                "timestamp": datetime.now().isoformat()
            }
            
            if docker_check.returncode == 0:
                # Get Docker version
                version_result = subprocess.run(
                    ["docker", "version", "--format", "json"],
                    capture_output=True, text=True, timeout=5
                )
                
                system_info["docker_available"] = version_result.returncode == 0
                
                if version_result.returncode == 0:
                    try:
                        version_data = json.loads(version_result.stdout)
                        system_info["version"] = version_data
                    except json.JSONDecodeError:
                        system_info["version"] = "Unable to parse version"
                    
                    # Get Docker system info
                    info_result = subprocess.run(
                        ["docker", "system", "df"],
                        capture_output=True, text=True, timeout=5
                    )
                    
                    if info_result.returncode == 0:
                        system_info["disk_usage_raw"] = info_result.stdout
                else:
                    system_info["docker_available"] = False
                    system_info["docker_error"] = version_result.stderr
            else:
                system_info["docker_available"] = False
                system_info["installation_help"] = {
                    "message": "Docker is not installed",
                    "install_instructions": {
                        "macOS": "Install Docker Desktop from https://docker.com/products/docker-desktop",
                        "linux": "Install using: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh",
                        "windows": "Install Docker Desktop from https://docker.com/products/docker-desktop"
                    }
                }
            
            return system_info
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "docker_available": False,
                "docker_installed": False
            }
    
    def _is_nextjs_related(self, text: str) -> bool:
        """Check if text indicates Next.js relation."""
        text_lower = text.lower()
        indicators = [
            "next", "nextjs", "react", "node", "frontend", "web",
            "nuxt", "gatsby", "vite", "webpack", "npm", "yarn"
        ]
        return any(indicator in text_lower for indicator in indicators)
    
    async def run(self):
        """Run the MCP server."""
        self.logger.info("🐳 Starting MCP Docker Server")
        
        try:
            while True:
                try:
                    # Read request from stdin
                    line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                    if not line:
                        break
                    
                    # Parse JSON request
                    try:
                        request = json.loads(line.strip())
                    except json.JSONDecodeError as e:
                        error_response = {
                            "jsonrpc": "2.0",
                            "id": None,
                            "error": {
                                "code": -32700,
                                "message": f"Parse error: {str(e)}"
                            }
                        }
                        print(json.dumps(error_response))
                        continue
                    
                    # Handle request
                    response = await self.handle_request(request)
                    
                    # Send response
                    print(json.dumps(response))
                    sys.stdout.flush()
                
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.logger.error(f"Error in main loop: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
        finally:
            self.logger.info("🐳 MCP Docker Server stopped")

async def main():
    """Main entry point."""
    server = MCPDockerServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
