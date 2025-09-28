"""
MCP Connection Manager for Agentic LLM Core v0.1

This module provides secure MCP server connections with policy-based access control.

Created: 2024-09-24
Status: Draft
"""

from __future__ import annotations

import asyncio
import logging
import subprocess
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

import aiohttp
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

class ServerType(str, Enum):
    """MCP server types."""
    SUPABASE_REST = "supabase-rest"
    FILESYSTEM = "filesystem"
    GIT = "git"
    WEB = "web"
    DATABASE = "database"
    CUSTOM = "custom"


class ConnectionStatus(str, Enum):
    """Connection status."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    AUTHENTICATING = "authenticating"


class SecurityPolicy(str, Enum):
    """Security policy types."""
    DENY_BY_DEFAULT = "deny by default"
    ALLOW_BY_DEFAULT = "allow by default"
    ALLOWLIST_TOOLS = "allowlist tools"
    BLOCKLIST_TOOLS = "blocklist tools"


class MCPTool(BaseModel):
    """MCP tool definition."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    server: str = Field(..., description="Server identifier")
    category: str = Field(..., description="Tool category")
    allowed: bool = Field(default=False, description="Whether tool is allowed")
    requires_auth: bool = Field(default=True, description="Whether tool requires authentication")


class MCPServer(BaseModel):
    """MCP server configuration."""
    server_id: str = Field(..., description="Unique server identifier")
    server_type: ServerType = Field(..., description="Server type")
    name: str = Field(..., description="Human-readable server name")
    endpoint: str = Field(..., description="Server endpoint URL or path")
    auth_config: Optional[Dict[str, Any]] = Field(None, description="Authentication configuration")
    tools: List[MCPTool] = Field(default_factory=list, description="Available tools")
    status: ConnectionStatus = Field(default=ConnectionStatus.DISCONNECTED, description="Connection status")
    last_connected: Optional[datetime] = Field(None, description="Last connection timestamp")
    error_message: Optional[str] = Field(None, description="Last error message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SecurityConfig(BaseModel):
    """Security configuration."""
    policy: SecurityPolicy = Field(default=SecurityPolicy.DENY_BY_DEFAULT, description="Security policy")
    allowlist_tools: Set[str] = Field(default_factory=set, description="Allowed tool names")
    blocklist_tools: Set[str] = Field(default_factory=set, description="Blocked tool names")
    allowed_servers: Set[str] = Field(default_factory=set, description="Allowed server IDs")
    blocked_servers: Set[str] = Field(default_factory=set, description="Blocked server IDs")
    require_verification: bool = Field(default=True, description="Require connection verification")
    max_connections: int = Field(default=10, description="Maximum concurrent connections")
    connection_timeout: float = Field(default=30.0, description="Connection timeout in seconds")


class ConnectionResult(BaseModel):
    """Connection result."""
    server_id: str = Field(..., description="Server identifier")
    success: bool = Field(..., description="Whether connection succeeded")
    status: ConnectionStatus = Field(..., description="Connection status")
    message: str = Field(..., description="Result message")
    tools_discovered: int = Field(default=0, description="Number of tools discovered")
    verification_passed: bool = Field(default=False, description="Whether verification passed")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Connection timestamp")


# ============================================================================
# Server Implementations
# ============================================================================

class MCPServerConnector:
    """Base class for MCP server connectors."""
    
    def __init__(self, server: MCPServer):
        self.server = server
        self.logger = logging.getLogger(f"{__name__}.{server.server_id}")
    
    async def connect(self) -> bool:
        """Connect to the server."""
        raise NotImplementedError
    
    async def disconnect(self) -> bool:
        """Disconnect from the server."""
        raise NotImplementedError
    
    async def discover_tools(self) -> List[MCPTool]:
        """Discover available tools."""
        raise NotImplementedError
    
    async def verify_connection(self) -> bool:
        """Verify the connection is working."""
        raise NotImplementedError


class SupabaseRestConnector(MCPServerConnector):
    """Supabase REST API connector."""
    
    async def connect(self) -> bool:
        """Connect to Supabase REST API."""
        try:
            self.server.status = ConnectionStatus.CONNECTING
            self.logger.info(f"Connecting to Supabase REST API: {self.server.endpoint}")
            
            # Parse endpoint
            parsed_url = urlparse(self.server.endpoint)
            if not parsed_url.scheme:
                self.server.endpoint = f"https://{self.server.endpoint}"
            
            # Test connection
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.server.endpoint}/rest/v1/",
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        self.server.status = ConnectionStatus.CONNECTED
                        self.server.last_connected = datetime.now(timezone.utc)
                        self.logger.info("Successfully connected to Supabase REST API")
                        return True
                    else:
                        self.server.status = ConnectionStatus.ERROR
                        self.server.error_message = f"HTTP {response.status}: {await response.text()}"
                        return False
                        
        except Exception as e:
            self.server.status = ConnectionStatus.ERROR
            self.server.error_message = str(e)
            self.logger.error(f"Failed to connect to Supabase REST API: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Supabase REST API."""
        self.server.status = ConnectionStatus.DISCONNECTED
        self.logger.info("Disconnected from Supabase REST API")
        return True
    
    async def discover_tools(self) -> List[MCPTool]:
        """Discover Supabase REST tools."""
        tools = [
            MCPTool(
                name="supabase_query",
                description="Execute SQL queries on Supabase database",
                server=self.server.server_id,
                category="database",
                allowed=False
            ),
            MCPTool(
                name="supabase_insert",
                description="Insert data into Supabase tables",
                server=self.server.server_id,
                category="database",
                allowed=False
            ),
            MCPTool(
                name="supabase_update",
                description="Update data in Supabase tables",
                server=self.server.server_id,
                category="database",
                allowed=False
            ),
            MCPTool(
                name="supabase_delete",
                description="Delete data from Supabase tables",
                server=self.server.server_id,
                category="database",
                allowed=False
            ),
            MCPTool(
                name="supabase_auth",
                description="Authenticate with Supabase Auth",
                server=self.server.server_id,
                category="auth",
                allowed=False
            )
        ]
        self.server.tools = tools
        return tools
    
    async def verify_connection(self) -> bool:
        """Verify Supabase connection."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.server.endpoint}/rest/v1/",
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except Exception:
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.server.auth_config:
            if "api_key" in self.server.auth_config:
                headers["apikey"] = self.server.auth_config["api_key"]
            if "bearer_token" in self.server.auth_config:
                headers["Authorization"] = f"Bearer {self.server.auth_config['bearer_token']}"
        
        return headers


class FilesystemConnector(MCPServerConnector):
    """Filesystem connector."""
    
    async def connect(self) -> bool:
        """Connect to filesystem."""
        try:
            self.server.status = ConnectionStatus.CONNECTING
            self.logger.info(f"Connecting to filesystem: {self.server.endpoint}")
            
            # Verify path exists and is accessible
            path = Path(self.server.endpoint)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
            
            if not path.is_dir():
                self.server.status = ConnectionStatus.ERROR
                self.server.error_message = "Endpoint must be a directory"
                return False
            
            # Test write access
            test_file = path / f".mcp_test_{uuid.uuid4().hex[:8]}"
            try:
                test_file.write_text("test")
                test_file.unlink()
            except PermissionError:
                self.server.status = ConnectionStatus.ERROR
                self.server.error_message = "No write permission to filesystem"
                return False
            
            self.server.status = ConnectionStatus.CONNECTED
            self.server.last_connected = datetime.now(timezone.utc)
            self.logger.info("Successfully connected to filesystem")
            return True
            
        except Exception as e:
            self.server.status = ConnectionStatus.ERROR
            self.server.error_message = str(e)
            self.logger.error(f"Failed to connect to filesystem: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from filesystem."""
        self.server.status = ConnectionStatus.DISCONNECTED
        self.logger.info("Disconnected from filesystem")
        return True
    
    async def discover_tools(self) -> List[MCPTool]:
        """Discover filesystem tools."""
        tools = [
            MCPTool(
                name="fs_read",
                description="Read file contents",
                server=self.server.server_id,
                category="file",
                allowed=False
            ),
            MCPTool(
                name="fs_write",
                description="Write content to file",
                server=self.server.server_id,
                category="file",
                allowed=False
            ),
            MCPTool(
                name="fs_list",
                description="List directory contents",
                server=self.server.server_id,
                category="file",
                allowed=False
            ),
            MCPTool(
                name="fs_create_dir",
                description="Create directory",
                server=self.server.server_id,
                category="file",
                allowed=False
            ),
            MCPTool(
                name="fs_delete",
                description="Delete file or directory",
                server=self.server.server_id,
                category="file",
                allowed=False
            ),
            MCPTool(
                name="fs_move",
                description="Move or rename file/directory",
                server=self.server.server_id,
                category="file",
                allowed=False
            )
        ]
        self.server.tools = tools
        return tools
    
    async def verify_connection(self) -> bool:
        """Verify filesystem connection."""
        try:
            path = Path(self.server.endpoint)
            return path.exists() and path.is_dir()
        except Exception:
            return False


class GitConnector(MCPServerConnector):
    """Git connector."""
    
    async def connect(self) -> bool:
        """Connect to Git repository."""
        try:
            self.server.status = ConnectionStatus.CONNECTING
            self.logger.info(f"Connecting to Git repository: {self.server.endpoint}")
            
            # Verify git repository
            path = Path(self.server.endpoint)
            if not path.exists():
                self.server.status = ConnectionStatus.ERROR
                self.server.error_message = "Git repository path does not exist"
                return False
            
            # Check if it's a git repository
            git_dir = path / ".git"
            if not git_dir.exists():
                self.server.status = ConnectionStatus.ERROR
                self.server.error_message = "Path is not a Git repository"
                return False
            
            # Test git command
            try:
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode != 0:
                    self.server.status = ConnectionStatus.ERROR
                    self.server.error_message = f"Git command failed: {result.stderr}"
                    return False
            except subprocess.TimeoutExpired:
                self.server.status = ConnectionStatus.ERROR
                self.server.error_message = "Git command timed out"
                return False
            
            self.server.status = ConnectionStatus.CONNECTED
            self.server.last_connected = datetime.now(timezone.utc)
            self.logger.info("Successfully connected to Git repository")
            return True
            
        except Exception as e:
            self.server.status = ConnectionStatus.ERROR
            self.server.error_message = str(e)
            self.logger.error(f"Failed to connect to Git repository: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Git repository."""
        self.server.status = ConnectionStatus.DISCONNECTED
        self.logger.info("Disconnected from Git repository")
        return True
    
    async def discover_tools(self) -> List[MCPTool]:
        """Discover Git tools."""
        tools = [
            MCPTool(
                name="git_status",
                description="Get Git repository status",
                server=self.server.server_id,
                category="git",
                allowed=False
            ),
            MCPTool(
                name="git_log",
                description="Get Git commit history",
                server=self.server.server_id,
                category="git",
                allowed=False
            ),
            MCPTool(
                name="git_diff",
                description="Get Git diff",
                server=self.server.server_id,
                category="git",
                allowed=False
            ),
            MCPTool(
                name="git_add",
                description="Stage files for commit",
                server=self.server.server_id,
                category="git",
                allowed=False
            ),
            MCPTool(
                name="git_commit",
                description="Commit staged changes",
                server=self.server.server_id,
                category="git",
                allowed=False
            ),
            MCPTool(
                name="git_push",
                description="Push commits to remote",
                server=self.server.server_id,
                category="git",
                allowed=False
            ),
            MCPTool(
                name="git_pull",
                description="Pull changes from remote",
                server=self.server.server_id,
                category="git",
                allowed=False
            )
        ]
        self.server.tools = tools
        return tools
    
    async def verify_connection(self) -> bool:
        """Verify Git connection."""
        try:
            path = Path(self.server.endpoint)
            git_dir = path / ".git"
            return path.exists() and git_dir.exists()
        except Exception:
            return False


class WebConnector(MCPServerConnector):
    """Web connector."""
    
    async def connect(self) -> bool:
        """Connect to web service."""
        try:
            self.server.status = ConnectionStatus.CONNECTING
            self.logger.info(f"Connecting to web service: {self.server.endpoint}")
            
            # Parse endpoint
            parsed_url = urlparse(self.server.endpoint)
            if not parsed_url.scheme:
                self.server.endpoint = f"https://{self.server.endpoint}"
            
            # Test connection
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.server.endpoint,
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status in [200, 201, 202]:
                        self.server.status = ConnectionStatus.CONNECTED
                        self.server.last_connected = datetime.now(timezone.utc)
                        self.logger.info("Successfully connected to web service")
                        return True
                    else:
                        self.server.status = ConnectionStatus.ERROR
                        self.server.error_message = f"HTTP {response.status}: {await response.text()}"
                        return False
                        
        except Exception as e:
            self.server.status = ConnectionStatus.ERROR
            self.server.error_message = str(e)
            self.logger.error(f"Failed to connect to web service: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from web service."""
        self.server.status = ConnectionStatus.DISCONNECTED
        self.logger.info("Disconnected from web service")
        return True
    
    async def discover_tools(self) -> List[MCPTool]:
        """Discover web tools."""
        tools = [
            MCPTool(
                name="web_get",
                description="Make HTTP GET request",
                server=self.server.server_id,
                category="web",
                allowed=False
            ),
            MCPTool(
                name="web_post",
                description="Make HTTP POST request",
                server=self.server.server_id,
                category="web",
                allowed=False
            ),
            MCPTool(
                name="web_put",
                description="Make HTTP PUT request",
                server=self.server.server_id,
                category="web",
                allowed=False
            ),
            MCPTool(
                name="web_delete",
                description="Make HTTP DELETE request",
                server=self.server.server_id,
                category="web",
                allowed=False
            ),
            MCPTool(
                name="web_scrape",
                description="Scrape web content",
                server=self.server.server_id,
                category="web",
                allowed=False
            )
        ]
        self.server.tools = tools
        return tools
    
    async def verify_connection(self) -> bool:
        """Verify web connection."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.server.endpoint,
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status in [200, 201, 202]
        except Exception:
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        headers = {
            "User-Agent": "Agentic-LLM-Core/0.1.0",
            "Accept": "application/json, text/html, */*"
        }
        
        if self.server.auth_config:
            if "api_key" in self.server.auth_config:
                headers["X-API-Key"] = self.server.auth_config["api_key"]
            if "bearer_token" in self.server.auth_config:
                headers["Authorization"] = f"Bearer {self.server.auth_config['bearer_token']}"
        
        return headers


# ============================================================================
# MCP Connection Manager
# ============================================================================

class MCPConnectionManager:
    """Manages MCP server connections with security policies."""
    
    def __init__(self, security_config: SecurityConfig):
        self.security_config = security_config
        self.servers: Dict[str, MCPServer] = {}
        self.connectors: Dict[str, MCPServerConnector] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_server(self, server: MCPServer) -> bool:
        """Register a server."""
        # Extract server type from server_id for allowlist checking
        server_type = server.server_id.split('_')[0]
        
        if self.security_config.policy == SecurityPolicy.DENY_BY_DEFAULT:
            if server_type not in self.security_config.allowed_servers:
                self.logger.warning(f"Server type {server_type} not in allowlist, denying registration")
                return False
        
        if server_type in self.security_config.blocked_servers:
            self.logger.warning(f"Server type {server_type} is blocked, denying registration")
            return False
        
        self.servers[server.server_id] = server
        self.logger.info(f"Registered server: {server.name} ({server.server_id})")
        return True
    
    def _create_connector(self, server: MCPServer) -> MCPServerConnector:
        """Create appropriate connector for server type."""
        if server.server_type == ServerType.SUPABASE_REST:
            return SupabaseRestConnector(server)
        elif server.server_type == ServerType.FILESYSTEM:
            return FilesystemConnector(server)
        elif server.server_type == ServerType.GIT:
            return GitConnector(server)
        elif server.server_type == ServerType.WEB:
            return WebConnector(server)
        else:
            raise ValueError(f"Unsupported server type: {server.server_type}")
    
    async def connect_server(self, server_id: str) -> ConnectionResult:
        """Connect to a specific server."""
        if server_id not in self.servers:
            return ConnectionResult(
                server_id=server_id,
                success=False,
                status=ConnectionStatus.ERROR,
                message=f"Server {server_id} not registered"
            )
        
        server = self.servers[server_id]
        
        try:
            # Create connector
            connector = self._create_connector(server)
            self.connectors[server_id] = connector
            
            # Connect
            success = await connector.connect()
            
            if success:
                # Discover tools
                tools = await connector.discover_tools()
                
                # Apply security policy to tools
                self._apply_tool_policy(tools)
                
                # Verify connection if required
                verification_passed = True
                if self.security_config.require_verification:
                    verification_passed = await connector.verify_connection()
                
                return ConnectionResult(
                    server_id=server_id,
                    success=True,
                    status=ConnectionStatus.CONNECTED,
                    message=f"Successfully connected to {server.name}",
                    tools_discovered=len(tools),
                    verification_passed=verification_passed
                )
            else:
                return ConnectionResult(
                    server_id=server_id,
                    success=False,
                    status=ConnectionStatus.ERROR,
                    message=f"Failed to connect: {server.error_message}"
                )
                
        except Exception as e:
            self.logger.error(f"Error connecting to server {server_id}: {e}")
            return ConnectionResult(
                server_id=server_id,
                success=False,
                status=ConnectionStatus.ERROR,
                message=f"Connection error: {str(e)}"
            )
    
    async def connect_servers(self, server_ids: List[str]) -> List[ConnectionResult]:
        """Connect to multiple servers."""
        results = []
        
        # Limit concurrent connections
        semaphore = asyncio.Semaphore(self.security_config.max_connections)
        
        async def connect_with_semaphore(server_id: str):
            async with semaphore:
                return await self.connect_server(server_id)
        
        # Connect to all servers concurrently
        tasks = [connect_with_semaphore(server_id) for server_id in server_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(ConnectionResult(
                    server_id=server_ids[i],
                    success=False,
                    status=ConnectionStatus.ERROR,
                    message=f"Connection exception: {str(result)}"
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    def _apply_tool_policy(self, tools: List[MCPTool]):
        """Apply security policy to tools."""
        for tool in tools:
            if self.security_config.policy == SecurityPolicy.DENY_BY_DEFAULT:
                # Deny by default, allow only if in allowlist
                tool.allowed = tool.name in self.security_config.allowlist_tools
            elif self.security_config.policy == SecurityPolicy.ALLOW_BY_DEFAULT:
                # Allow by default, deny only if in blocklist
                tool.allowed = tool.name not in self.security_config.blocklist_tools
            else:
                # Custom policy
                tool.allowed = False
    
    def get_allowed_tools(self) -> List[MCPTool]:
        """Get all allowed tools across all servers."""
        allowed_tools = []
        for server in self.servers.values():
            allowed_tools.extend([tool for tool in server.tools if tool.allowed])
        return allowed_tools
    
    def get_server_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all servers."""
        status = {}
        for server_id, server in self.servers.items():
            status[server_id] = {
                "name": server.name,
                "type": server.server_type.value,
                "status": server.status.value,
                "last_connected": server.last_connected.isoformat() if server.last_connected else None,
                "error_message": server.error_message,
                "tools_count": len(server.tools),
                "allowed_tools_count": len([t for t in server.tools if t.allowed])
            }
        return status
    
    async def disconnect_all(self):
        """Disconnect from all servers."""
        for connector in self.connectors.values():
            await connector.disconnect()
        self.connectors.clear()
        self.logger.info("Disconnected from all servers")


# ============================================================================
# Main Function
# ============================================================================

async def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Connection Manager")
    parser.add_argument("--servers", required=True, help="Comma-separated list of servers to connect")
    parser.add_argument("--policy", default="deny by default", help="Security policy")
    parser.add_argument("--verify", action="store_true", help="Verify connections")
    parser.add_argument("--allowlist", help="Comma-separated list of allowed tools")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Parse servers
    server_list = [s.strip() for s in args.servers.split(",")]
    
    # Create security config
    policy_mapping = {
        "deny by default": SecurityPolicy.DENY_BY_DEFAULT,
        "allow by default": SecurityPolicy.ALLOW_BY_DEFAULT,
        "allowlist tools": SecurityPolicy.ALLOWLIST_TOOLS,
        "blocklist tools": SecurityPolicy.BLOCKLIST_TOOLS
    }
    
    policy = policy_mapping.get(args.policy.lower(), SecurityPolicy.DENY_BY_DEFAULT)
    
    security_config = SecurityConfig(
        policy=policy,
        require_verification=args.verify
    )
    
    if args.allowlist:
        security_config.allowlist_tools = set(s.strip() for s in args.allowlist.split(","))
    
    # Allow all requested servers
    for server_name in server_list:
        security_config.allowed_servers.add(server_name)
    
    # Create connection manager
    manager = MCPConnectionManager(security_config)
    
    # Register servers
    servers_to_connect = []
    for server_name in server_list:
        server_id = f"{server_name}_{uuid.uuid4().hex[:8]}"
        
        if server_name == "supabase-rest":
            server = MCPServer(
                server_id=server_id,
                server_type=ServerType.SUPABASE_REST,
                name="Supabase REST API",
                endpoint="https://your-project.supabase.co",
                auth_config={"api_key": "your-api-key"}
            )
        elif server_name == "filesystem":
            server = MCPServer(
                server_id=server_id,
                server_type=ServerType.FILESYSTEM,
                name="Local Filesystem",
                endpoint="/tmp/mcp_workspace"
            )
        elif server_name == "git":
            server = MCPServer(
                server_id=server_id,
                server_type=ServerType.GIT,
                name="Git Repository",
                endpoint="."
            )
        elif server_name == "web":
            server = MCPServer(
                server_id=server_id,
                server_type=ServerType.WEB,
                name="Web Service",
                endpoint="https://httpbin.org"
            )
        else:
            print(f"Unknown server type: {server_name}")
            continue
        
        if manager.register_server(server):
            servers_to_connect.append(server_id)
    
    # Connect to servers
    print(f"Connecting to {len(servers_to_connect)} servers...")
    results = await manager.connect_servers(servers_to_connect)
    
    # Print results
    print("\n" + "="*80)
    print("MCP CONNECTION RESULTS")
    print("="*80)
    
    for result in results:
        status_emoji = "✅" if result.success else "❌"
        print(f"\n{status_emoji} {result.server_id}")
        print(f"   Status: {result.status.value}")
        print(f"   Message: {result.message}")
        print(f"   Tools Discovered: {result.tools_discovered}")
        if result.verification_passed is not None:
            print(f"   Verification: {'✅ Passed' if result.verification_passed else '❌ Failed'}")
    
    # Print allowed tools
    allowed_tools = manager.get_allowed_tools()
    print(f"\n🔧 Allowed Tools: {len(allowed_tools)}")
    for tool in allowed_tools:
        print(f"   - {tool.name} ({tool.server})")
    
    # Print server status
    print("\n📊 Server Status:")
    status = manager.get_server_status()
    for server_id, info in status.items():
        print(f"   {server_id}: {info['status']} ({info['allowed_tools_count']}/{info['tools_count']} tools allowed)")
    
    # Disconnect
    await manager.disconnect_all()
    print("\n🔌 Disconnected from all servers")


if __name__ == "__main__":
    asyncio.run(main())
