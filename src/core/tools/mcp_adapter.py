"""
MCP (Model Context Protocol) Adapter for Agentic LLM Core v0.1

This module provides an MCP adapter with support for:
- stdin/stdout and socket communication
- Input/output schema validation
- Redaction for keys, secrets, and PII
- Comprehensive error handling and security

Created: 2024-09-24
Status: Draft
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import socket
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union, AsyncGenerator, Callable
from uuid import uuid4

import pydantic
from pydantic import BaseModel, Field, validator

from ..models.contracts import ToolCall, ToolResult, ToolSchema


# ============================================================================
# MCP Protocol Definitions
# ============================================================================

class MCPTransportType(str, Enum):
    """Supported MCP transport types."""
    STDIN_STDOUT = "stdin_stdout"
    SOCKET = "socket"
    WEBSOCKET = "websocket"  # Future support


class MCPMessageType(str, Enum):
    """MCP message types."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class MCPMethod(str, Enum):
    """MCP methods."""
    # Tool methods
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"
    
    # Resource methods
    RESOURCES_LIST = "resources/list"
    RESOURCES_READ = "resources/read"
    
    # Prompt methods
    PROMPTS_LIST = "prompts/list"
    PROMPTS_GET = "prompts/get"
    
    # Completion methods
    COMPLETION = "completion"


# ============================================================================
# MCP Message Models
# ============================================================================

class MCPMessage(BaseModel):
    """Base MCP message model."""
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    id: Optional[Union[str, int]] = Field(None, description="Message ID")
    method: Optional[str] = Field(None, description="Method name")
    params: Optional[Dict[str, Any]] = Field(None, description="Method parameters")
    result: Optional[Any] = Field(None, description="Response result")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information")


class MCPRequest(BaseModel):
    """MCP request message."""
    jsonrpc: str = Field(default="2.0")
    id: Union[str, int] = Field(..., description="Request ID")
    method: str = Field(..., description="Method name")
    params: Dict[str, Any] = Field(default_factory=dict, description="Method parameters")


class MCPResponse(BaseModel):
    """MCP response message."""
    jsonrpc: str = Field(default="2.0")
    id: Union[str, int] = Field(..., description="Request ID")
    result: Optional[Any] = Field(None, description="Response result")
    error: Optional[MCPError] = Field(None, description="Error information")


class MCPNotification(BaseModel):
    """MCP notification message."""
    jsonrpc: str = Field(default="2.0")
    method: str = Field(..., description="Method name")
    params: Dict[str, Any] = Field(default_factory=dict, description="Method parameters")


class MCPError(BaseModel):
    """MCP error information."""
    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    data: Optional[Any] = Field(None, description="Additional error data")


# ============================================================================
# Schema Validation Models
# ============================================================================

class MCPSchemaValidator:
    """Schema validator for MCP messages."""
    
    def __init__(self):
        self.input_schemas: Dict[str, pydantic.BaseModel] = {}
        self.output_schemas: Dict[str, pydantic.BaseModel] = {}
    
    def register_input_schema(self, method: str, schema: pydantic.BaseModel):
        """Register input schema for a method."""
        self.input_schemas[method] = schema
    
    def register_output_schema(self, method: str, schema: pydantic.BaseModel):
        """Register output schema for a method."""
        self.output_schemas[method] = schema
    
    def validate_input(self, method: str, params: Dict[str, Any]) -> pydantic.BaseModel:
        """Validate input parameters against schema."""
        if method not in self.input_schemas:
            raise ValueError(f"No input schema registered for method: {method}")
        
        try:
            return self.input_schemas[method](**params)
        except pydantic.ValidationError as e:
            raise ValueError(f"Input validation failed for {method}: {e}")
    
    def validate_output(self, method: str, result: Any) -> pydantic.BaseModel:
        """Validate output result against schema."""
        if method not in self.output_schemas:
            raise ValueError(f"No output schema registered for method: {method}")
        
        try:
            if isinstance(result, dict):
                return self.output_schemas[method](**result)
            else:
                return self.output_schemas[method](result=result)
        except pydantic.ValidationError as e:
            raise ValueError(f"Output validation failed for {method}: {e}")


# ============================================================================
# Redaction System
# ============================================================================

class RedactionPattern(BaseModel):
    """Pattern for redaction."""
    name: str = Field(..., description="Pattern name")
    regex: str = Field(..., description="Regex pattern")
    replacement: str = Field(default="[REDACTED]", description="Replacement text")
    case_sensitive: bool = Field(default=False, description="Case sensitive matching")


class RedactionConfig(BaseModel):
    """Configuration for redaction system."""
    enable_redaction: bool = Field(default=True, description="Enable redaction")
    redact_keys: bool = Field(default=True, description="Redact API keys")
    redact_secrets: bool = Field(default=True, description="Redact secrets")
    redact_pii: bool = Field(default=True, description="Redact PII")
    custom_patterns: List[RedactionPattern] = Field(default_factory=list, description="Custom patterns")


class MCPRedactor:
    """Redaction system for MCP messages."""
    
    def __init__(self, config: RedactionConfig):
        self.config = config
        self.patterns = self._build_patterns()
    
    def _build_patterns(self) -> List[RedactionPattern]:
        """Build redaction patterns."""
        patterns = []
        
        if self.config.redact_keys:
            patterns.extend([
                RedactionPattern(
                    name="api_key",
                    regex=r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
                    replacement='\\1: [REDACTED_API_KEY]'
                ),
                RedactionPattern(
                    name="bearer_token",
                    regex=r'(?i)(bearer|authorization)\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]{20,})["\']?',
                    replacement='\\1: [REDACTED_TOKEN]'
                ),
                RedactionPattern(
                    name="access_key",
                    regex=r'(?i)(access[_-]?key|accesskey)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
                    replacement='\\1: [REDACTED_ACCESS_KEY]'
                )
            ])
        
        if self.config.redact_secrets:
            patterns.extend([
                RedactionPattern(
                    name="password",
                    regex=r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?([^"\'\s]+)["\']?',
                    replacement='\\1: [REDACTED_PASSWORD]'
                ),
                RedactionPattern(
                    name="secret",
                    regex=r'(?i)(secret|secret[_-]?key)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{16,})["\']?',
                    replacement='\\1: [REDACTED_SECRET]'
                ),
                RedactionPattern(
                    name="private_key",
                    regex=r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----.*?-----END\s+(?:RSA\s+)?PRIVATE\s+KEY-----',
                    replacement='[REDACTED_PRIVATE_KEY]'
                )
            ])
        
        if self.config.redact_pii:
            patterns.extend([
                RedactionPattern(
                    name="email",
                    regex=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                    replacement='[REDACTED_EMAIL]'
                ),
                RedactionPattern(
                    name="phone",
                    regex=r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
                    replacement='[REDACTED_PHONE]'
                ),
                RedactionPattern(
                    name="ssn",
                    regex=r'\b\d{3}-?\d{2}-?\d{4}\b',
                    replacement='[REDACTED_SSN]'
                ),
                RedactionPattern(
                    name="credit_card",
                    regex=r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
                    replacement='[REDACTED_CREDIT_CARD]'
                )
            ])
        
        # Add custom patterns
        patterns.extend(self.config.custom_patterns)
        
        return patterns
    
    def redact_text(self, text: str) -> str:
        """Redact sensitive information from text."""
        if not self.config.enable_redaction:
            return text
        
        redacted = text
        for pattern in self.patterns:
            flags = 0 if pattern.case_sensitive else re.IGNORECASE
            redacted = re.sub(pattern.regex, pattern.replacement, redacted, flags=flags)
        
        return redacted
    
    def redact_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive information from dictionary."""
        if not self.config.enable_redaction:
            return data
        
        redacted = {}
        for key, value in data.items():
            if isinstance(value, str):
                redacted[key] = self.redact_text(value)
            elif isinstance(value, dict):
                redacted[key] = self.redact_dict(value)
            elif isinstance(value, list):
                redacted[key] = [self.redact_dict(item) if isinstance(item, dict) else self.redact_text(item) if isinstance(item, str) else item for item in value]
            else:
                redacted[key] = value
        
        return redacted


# ============================================================================
# Transport Layer
# ============================================================================

class MCPTransport(ABC):
    """Abstract base class for MCP transports."""
    
    @abstractmethod
    async def send_message(self, message: MCPMessage) -> None:
        """Send a message."""
        pass
    
    @abstractmethod
    async def receive_message(self) -> MCPMessage:
        """Receive a message."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the transport."""
        pass


class MCPStdioTransport(MCPTransport):
    """MCP transport using stdin/stdout."""
    
    def __init__(self):
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.is_closed = False
    
    async def send_message(self, message: MCPMessage) -> None:
        """Send message via stdout."""
        if self.is_closed:
            raise ConnectionError("Transport is closed")
        
        try:
            message_str = message.json() + "\n"
            self.stdout.write(message_str)
            self.stdout.flush()
        except Exception as e:
            raise ConnectionError(f"Failed to send message: {e}")
    
    async def receive_message(self) -> MCPMessage:
        """Receive message via stdin."""
        if self.is_closed:
            raise ConnectionError("Transport is closed")
        
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, self.stdin.readline)
            if not line:
                raise ConnectionError("End of input")
            
            message_data = json.loads(line.strip())
            return MCPMessage(**message_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON message: {e}")
        except Exception as e:
            raise ConnectionError(f"Failed to receive message: {e}")
    
    async def close(self) -> None:
        """Close the transport."""
        self.is_closed = True


class MCPSocketTransport(MCPTransport):
    """MCP transport using socket connection."""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.is_connected = False
    
    async def connect(self) -> None:
        """Connect to the socket."""
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            self.is_connected = True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to {self.host}:{self.port}: {e}")
    
    async def send_message(self, message: MCPMessage) -> None:
        """Send message via socket."""
        if not self.is_connected or not self.writer:
            raise ConnectionError("Not connected")
        
        try:
            message_str = message.json() + "\n"
            self.writer.write(message_str.encode())
            await self.writer.drain()
        except Exception as e:
            raise ConnectionError(f"Failed to send message: {e}")
    
    async def receive_message(self) -> MCPMessage:
        """Receive message via socket."""
        if not self.is_connected or not self.reader:
            raise ConnectionError("Not connected")
        
        try:
            line = await self.reader.readline()
            if not line:
                raise ConnectionError("Connection closed")
            
            message_data = json.loads(line.decode().strip())
            return MCPMessage(**message_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON message: {e}")
        except Exception as e:
            raise ConnectionError(f"Failed to receive message: {e}")
    
    async def close(self) -> None:
        """Close the socket connection."""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        self.is_connected = False


# ============================================================================
# Main MCP Adapter
# ============================================================================

class MCPAdapter:
    """Main MCP adapter with validation and redaction."""
    
    def __init__(
        self,
        transport: MCPTransport,
        schema_validator: Optional[MCPSchemaValidator] = None,
        redaction_config: Optional[RedactionConfig] = None
    ):
        self.transport = transport
        self.schema_validator = schema_validator or MCPSchemaValidator()
        self.redactor = MCPRedactor(redaction_config or RedactionConfig())
        
        # Message handlers
        self.message_handlers: Dict[str, Callable] = {}
        self.request_handlers: Dict[str, Callable] = {}
        self.notification_handlers: Dict[str, Callable] = {}
        
        # Statistics
        self.total_messages = 0
        self.successful_messages = 0
        self.failed_messages = 0
        self.redacted_messages = 0
        
        # Logging
        self.logger = logging.getLogger(__name__)
    
    def register_request_handler(self, method: str, handler: Callable):
        """Register a request handler."""
        self.request_handlers[method] = handler
    
    def register_notification_handler(self, method: str, handler: Callable):
        """Register a notification handler."""
        self.notification_handlers[method] = handler
    
    async def send_request(self, method: str, params: Dict[str, Any], request_id: Optional[Union[str, int]] = None) -> MCPResponse:
        """Send a request and wait for response."""
        if request_id is None:
            request_id = str(uuid4())
        
        # Validate input schema
        try:
            validated_params = self.schema_validator.validate_input(method, params)
            params = validated_params.dict() if hasattr(validated_params, 'dict') else params
        except ValueError as e:
            self.logger.warning(f"Input validation failed for {method}: {e}")
        
        # Redact sensitive information
        redacted_params = self.redactor.redact_dict(params)
        if redacted_params != params:
            self.redacted_messages += 1
        
        # Create and send request
        request = MCPRequest(
            id=request_id,
            method=method,
            params=redacted_params
        )
        
        await self.transport.send_message(request)
        self.total_messages += 1
        
        # Wait for response
        response = await self.transport.receive_message()
        
        if not isinstance(response, MCPResponse):
            raise ValueError("Expected response message")
        
        # Validate output schema
        if response.result is not None:
            try:
                validated_result = self.schema_validator.validate_output(method, response.result)
                response.result = validated_result.dict() if hasattr(validated_result, 'dict') else response.result
            except ValueError as e:
                self.logger.warning(f"Output validation failed for {method}: {e}")
        
        if response.error:
            self.failed_messages += 1
        else:
            self.successful_messages += 1
        
        return response
    
    async def send_notification(self, method: str, params: Dict[str, Any]) -> None:
        """Send a notification."""
        # Validate input schema
        try:
            validated_params = self.schema_validator.validate_input(method, params)
            params = validated_params.dict() if hasattr(validated_params, 'dict') else params
        except ValueError as e:
            self.logger.warning(f"Input validation failed for {method}: {e}")
        
        # Redact sensitive information
        redacted_params = self.redactor.redact_dict(params)
        if redacted_params != params:
            self.redacted_messages += 1
        
        # Create and send notification
        notification = MCPNotification(
            method=method,
            params=redacted_params
        )
        
        await self.transport.send_message(notification)
        self.total_messages += 1
    
    async def send_response(self, request_id: Union[str, int], result: Any = None, error: Optional[MCPError] = None) -> None:
        """Send a response to a request."""
        # Validate output schema if result provided
        if result is not None:
            # We need the method to validate output, but we don't have it in the response
            # This is a limitation of the current design
            pass
        
        # Redact sensitive information
        redacted_result = self.redactor.redact_dict(result) if isinstance(result, dict) else result
        if redacted_result != result:
            self.redacted_messages += 1
        
        # Create and send response
        response = MCPResponse(
            id=request_id,
            result=redacted_result,
            error=error
        )
        
        await self.transport.send_message(response)
        self.total_messages += 1
    
    async def handle_message(self, message: MCPMessage) -> None:
        """Handle an incoming message."""
        try:
            if message.method and message.id is not None:
                # This is a request
                await self._handle_request(message)
            elif message.method:
                # This is a notification
                await self._handle_notification(message)
            elif message.result is not None or message.error is not None:
                # This is a response
                await self._handle_response(message)
            else:
                raise ValueError("Invalid message format")
        except Exception as e:
            self.logger.error(f"Failed to handle message: {e}")
            self.failed_messages += 1
    
    async def _handle_request(self, message: MCPRequest) -> None:
        """Handle a request message."""
        method = message.method
        if method not in self.request_handlers:
            error = MCPError(
                code=-32601,
                message=f"Method not found: {method}"
            )
            await self.send_response(message.id, error=error)
            return
        
        try:
            # Validate input schema
            validated_params = self.schema_validator.validate_input(method, message.params)
            
            # Call handler
            handler = self.request_handlers[method]
            result = await handler(validated_params.dict() if hasattr(validated_params, 'dict') else message.params)
            
            # Send response
            await self.send_response(message.id, result=result)
            
        except ValueError as e:
            error = MCPError(
                code=-32602,
                message=f"Invalid params: {str(e)}"
            )
            await self.send_response(message.id, error=error)
        except Exception as e:
            error = MCPError(
                code=-32603,
                message=f"Internal error: {str(e)}"
            )
            await self.send_response(message.id, error=error)
    
    async def _handle_notification(self, message: MCPNotification) -> None:
        """Handle a notification message."""
        method = message.method
        if method in self.notification_handlers:
            try:
                # Validate input schema
                validated_params = self.schema_validator.validate_input(method, message.params)
                
                # Call handler
                handler = self.notification_handlers[method]
                await handler(validated_params.dict() if hasattr(validated_params, 'dict') else message.params)
                
            except ValueError as e:
                self.logger.warning(f"Invalid notification params for {method}: {e}")
            except Exception as e:
                self.logger.error(f"Failed to handle notification {method}: {e}")
    
    async def _handle_response(self, message: MCPResponse) -> None:
        """Handle a response message."""
        # Responses are typically handled by the caller
        # This is a placeholder for future response handling
        pass
    
    async def run_server(self) -> None:
        """Run the MCP server."""
        self.logger.info("Starting MCP server")
        
        try:
            while True:
                try:
                    message = await self.transport.receive_message()
                    await self.handle_message(message)
                except ConnectionError:
                    self.logger.info("Connection closed")
                    break
                except Exception as e:
                    self.logger.error(f"Error in server loop: {e}")
                    continue
        finally:
            await self.transport.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics."""
        success_rate = (self.successful_messages / self.total_messages * 100) if self.total_messages > 0 else 0
        
        return {
            "total_messages": self.total_messages,
            "successful_messages": self.successful_messages,
            "failed_messages": self.failed_messages,
            "redacted_messages": self.redacted_messages,
            "success_rate": success_rate,
            "registered_request_handlers": len(self.request_handlers),
            "registered_notification_handlers": len(self.notification_handlers)
        }
    
    async def close(self) -> None:
        """Close the adapter."""
        await self.transport.close()


# ============================================================================
# Factory Functions
# ============================================================================

def create_stdio_adapter(
    redaction_config: Optional[RedactionConfig] = None,
    schema_validator: Optional[MCPSchemaValidator] = None
) -> MCPAdapter:
    """Create an MCP adapter using stdin/stdout transport."""
    transport = MCPStdioTransport()
    return MCPAdapter(transport, schema_validator, redaction_config)


def create_socket_adapter(
    host: str = "localhost",
    port: int = 8080,
    redaction_config: Optional[RedactionConfig] = None,
    schema_validator: Optional[MCPSchemaValidator] = None
) -> MCPAdapter:
    """Create an MCP adapter using socket transport."""
    transport = MCPSocketTransport(host, port)
    return MCPAdapter(transport, schema_validator, redaction_config)


async def create_connected_socket_adapter(
    host: str = "localhost",
    port: int = 8080,
    redaction_config: Optional[RedactionConfig] = None,
    schema_validator: Optional[MCPSchemaValidator] = None
) -> MCPAdapter:
    """Create and connect an MCP adapter using socket transport."""
    adapter = create_socket_adapter(host, port, redaction_config, schema_validator)
    await adapter.transport.connect()
    return adapter


# ============================================================================
# Export all classes and functions
# ============================================================================

__all__ = [
    # Enums
    "MCPTransportType",
    "MCPMessageType",
    "MCPMethod",
    
    # Message models
    "MCPMessage",
    "MCPRequest",
    "MCPResponse",
    "MCPNotification",
    "MCPError",
    
    # Schema validation
    "MCPSchemaValidator",
    
    # Redaction
    "RedactionPattern",
    "RedactionConfig",
    "MCPRedactor",
    
    # Transport
    "MCPTransport",
    "MCPStdioTransport",
    "MCPSocketTransport",
    
    # Main adapter
    "MCPAdapter",
    
    # Factory functions
    "create_stdio_adapter",
    "create_socket_adapter",
    "create_connected_socket_adapter",
]
