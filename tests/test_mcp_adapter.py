""'
Tests for MCP Adapter

Comprehensive test suite for the MCP adapter including:
- Transport layer testing (stdio and socket)
- Schema validation testing
- Redaction system testing
- Message handling and protocol testing
- Security and error handling testing

Created: 2024-09-24
Status: Draft
""'

import asyncio
import json
import pytest
import socket
from datetime import datetime
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from src.core.tools.mcp_adapter import (
    # Enums
    MCPTransportType,
    MCPMessageType,
    MCPMethod,

    # Message models
    MCPMessage,
    MCPRequest,
    MCPResponse,
    MCPNotification,
    MCPError,

    # Schema validation
    MCPSchemaValidator,

    # Redaction
    RedactionPattern,
    RedactionConfig,
    MCPRedactor,

    # Transport
    MCPTransport,
    MCPStdioTransport,
    MCPSocketTransport,

    # Main adapter
    MCPAdapter,

    # Factory functions
    create_stdio_adapter,
    create_socket_adapter,
    create_connected_socket_adapter,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_mcp_request():
    """TODO: Add docstring."""
    """Sample MCP request for testing.""'
    return MCPRequest(
        id="test-123',
        method="tools/list',
        params={"limit': 10}
    )


@pytest.fixture
def sample_mcp_response():
    """TODO: Add docstring."""
    """Sample MCP response for testing.""'
    return MCPResponse(
        id="test-123',
        result={"tools": ["tool1", "tool2']}
    )


@pytest.fixture
def sample_mcp_notification():
    """TODO: Add docstring."""
    """Sample MCP notification for testing.""'
    return MCPNotification(
        method="notifications/status',
        params={"status": "ready'}
    )


@pytest.fixture
def sample_mcp_error():
    """TODO: Add docstring."""
    """Sample MCP error for testing.""'
    return MCPError(
        code=-32601,
        message="Method not found'
    )


@pytest.fixture
def sample_redaction_config():
    """TODO: Add docstring."""
    """Sample redaction configuration for testing.""'
    return RedactionConfig(
        enable_redaction=True,
        redact_keys=True,
        redact_secrets=True,
        redact_pii=True,
        custom_patterns=[
            RedactionPattern(
                name="custom_pattern',
                regex=r"custom:\s*(\w+)',
                replacement="custom: [REDACTED]'
            )
        ]
    )


@pytest.fixture
def sample_sensitive_data():
    """TODO: Add docstring."""
    """Sample data with sensitive information for testing.""'
    return {
        "api_key": "sk-1234567890abcdef',
        "password": "secretpassword123',
        "email": "user@example.com',
        "phone": "555-123-4567',
        "ssn": "123-45-6789',
        "credit_card": "4111-1111-1111-1111',
        "custom": "custom: sensitive_value',
        "normal_data": "This is normal data'
    }


# ============================================================================
# Message Model Tests
# ============================================================================

class TestMCPMessageModels:
    """TODO: Add docstring."""
    """Test MCP message models.""'

    def test_mcp_request_creation(self, sample_mcp_request):
        """TODO: Add docstring."""
        """Test MCP request creation.""'
        assert sample_mcp_request.jsonrpc == "2.0'
        assert sample_mcp_request.id == "test-123'
        assert sample_mcp_request.method == "tools/list'
        assert sample_mcp_request.params == {"limit': 10}

    def test_mcp_response_creation(self, sample_mcp_response):
        """TODO: Add docstring."""
        """Test MCP response creation.""'
        assert sample_mcp_response.jsonrpc == "2.0'
        assert sample_mcp_response.id == "test-123'
        assert sample_mcp_response.result == {"tools": ["tool1", "tool2']}
        assert sample_mcp_response.error is None

    def test_mcp_notification_creation(self, sample_mcp_notification):
        """TODO: Add docstring."""
        """Test MCP notification creation.""'
        assert sample_mcp_notification.jsonrpc == "2.0'
        assert sample_mcp_notification.method == "notifications/status'
        assert sample_mcp_notification.params == {"status": "ready'}
        assert sample_mcp_notification.id is None

    def test_mcp_error_creation(self, sample_mcp_error):
        """TODO: Add docstring."""
        """Test MCP error creation.""'
        assert sample_mcp_error.code == -32601
        assert sample_mcp_error.message == "Method not found'
        assert sample_mcp_error.data is None

    def test_message_serialization(self, sample_mcp_request):
        """TODO: Add docstring."""
        """Test message JSON serialization.""'
        json_str = sample_mcp_request.json()
        assert isinstance(json_str, str)

        # Parse back to verify
        parsed = json.loads(json_str)
        assert parsed["jsonrpc"] == "2.0'
        assert parsed["id"] == "test-123'
        assert parsed["method"] == "tools/list'
        assert parsed["params"] == {"limit': 10}


# ============================================================================
# Schema Validation Tests
# ============================================================================

class TestMCPSchemaValidator:
    """TODO: Add docstring."""
    """Test MCP schema validator.""'

    @pytest.fixture
    def schema_validator(self):
        """TODO: Add docstring."""
        """Create schema validator for testing.""'
        return MCPSchemaValidator()

    def test_register_schemas(self, schema_validator):
        """TODO: Add docstring."""
        """Test schema registration.""'
        from pydantic import BaseModel

        class TestInputSchema(BaseModel):
            """TODO: Add docstring."""
            """TODO: Add docstring.""'
            limit: int
            offset: int = 0

        class TestOutputSchema(BaseModel):
            """TODO: Add docstring."""
            """TODO: Add docstring.""'
            tools: List[str]
            total: int

        schema_validator.register_input_schema("tools/list', TestInputSchema)
        schema_validator.register_output_schema("tools/list', TestOutputSchema)

        assert "tools/list' in schema_validator.input_schemas
        assert "tools/list' in schema_validator.output_schemas

    def test_validate_input_success(self, schema_validator):
        """TODO: Add docstring."""
        """Test successful input validation.""'
        from pydantic import BaseModel

        class TestSchema(BaseModel):
            """TODO: Add docstring."""
            """TODO: Add docstring.""'
            limit: int
            offset: int = 0

        schema_validator.register_input_schema("test_method', TestSchema)

        result = schema_validator.validate_input("test_method", {"limit': 10})
        assert result.limit == 10
        assert result.offset == 0

    def test_validate_input_failure(self, schema_validator):
        """TODO: Add docstring."""
        """Test input validation failure.""'
        from pydantic import BaseModel

        class TestSchema(BaseModel):
            """TODO: Add docstring."""
            """TODO: Add docstring.""'
            limit: int

        schema_validator.register_input_schema("test_method', TestSchema)

        with pytest.raises(ValueError):
            schema_validator.validate_input("test_method", {"limit": "invalid'})

    def test_validate_output_success(self, schema_validator):
        """TODO: Add docstring."""
        """Test successful output validation.""'
        from pydantic import BaseModel

        class TestSchema(BaseModel):
            """TODO: Add docstring."""
            """TODO: Add docstring.""'
            tools: List[str]
            total: int

        schema_validator.register_output_schema("test_method', TestSchema)

        result = schema_validator.validate_output("test_method', {
            "tools": ["tool1", "tool2'],
            "total': 2
        })
        assert result.tools == ["tool1", "tool2']
        assert result.total == 2

    def test_validate_output_failure(self, schema_validator):
        """TODO: Add docstring."""
        """Test output validation failure.""'
        from pydantic import BaseModel

        class TestSchema(BaseModel):
            """TODO: Add docstring."""
            """TODO: Add docstring.""'
            tools: List[str]

        schema_validator.register_output_schema("test_method', TestSchema)

        with pytest.raises(ValueError):
            schema_validator.validate_output("test_method", {"tools": "not_a_list'})


# ============================================================================
# Redaction System Tests
# ============================================================================

class TestRedactionPattern:
    """TODO: Add docstring."""
    """Test RedactionPattern model.""'

    def test_redaction_pattern_creation(self):
        """TODO: Add docstring."""
        """Test redaction pattern creation.""'
        pattern = RedactionPattern(
            name="test_pattern',
            regex=r"test:\s*(\w+)',
            replacement="test: [REDACTED]',
            case_sensitive=False
        )

        assert pattern.name == "test_pattern'
        assert pattern.regex == r"test:\s*(\w+)'
        assert pattern.replacement == "test: [REDACTED]'
        assert pattern.case_sensitive is False

    def test_redaction_pattern_defaults(self):
        """TODO: Add docstring."""
        """Test redaction pattern defaults.""'
        pattern = RedactionPattern(
            name="test_pattern',
            regex=r"test:\s*(\w+)'
        )

        assert pattern.replacement == "[REDACTED]'
        assert pattern.case_sensitive is False


class TestRedactionConfig:
    """TODO: Add docstring."""
    """Test RedactionConfig model.""'

    def test_redaction_config_creation(self, sample_redaction_config):
        """TODO: Add docstring."""
        """Test redaction config creation.""'
        assert sample_redaction_config.enable_redaction is True
        assert sample_redaction_config.redact_keys is True
        assert sample_redaction_config.redact_secrets is True
        assert sample_redaction_config.redact_pii is True
        assert len(sample_redaction_config.custom_patterns) == 1

    def test_redaction_config_defaults(self):
        """TODO: Add docstring."""
        """Test redaction config defaults.""'
        config = RedactionConfig()

        assert config.enable_redaction is True
        assert config.redact_keys is True
        assert config.redact_secrets is True
        assert config.redact_pii is True
        assert config.custom_patterns == []


class TestMCPRedactor:
    """TODO: Add docstring."""
    """Test MCP redaction system.""'

    @pytest.fixture
    def redactor(self, sample_redaction_config):
        """TODO: Add docstring."""
        """Create redactor for testing.""'
        return MCPRedactor(sample_redaction_config)

    def test_redact_text_api_key(self, redactor):
        """TODO: Add docstring."""
        """Test API key redaction.""'
        text = "api_key: sk-1234567890abcdef'
        redacted = redactor.redact_text(text)
        assert "[REDACTED_API_KEY]' in redacted
        assert "sk-1234567890abcdef' not in redacted

    def test_redact_text_password(self, redactor):
        """TODO: Add docstring."""
        """Test password redaction.""'
        text = "password: secretpassword123'
        redacted = redactor.redact_text(text)
        assert "[REDACTED_PASSWORD]' in redacted
        assert "secretpassword123' not in redacted

    def test_redact_text_email(self, redactor):
        """TODO: Add docstring."""
        """Test email redaction.""'
        text = "Contact: user@example.com for more info'
        redacted = redactor.redact_text(text)
        assert "[REDACTED_EMAIL]' in redacted
        assert "user@example.com' not in redacted

    def test_redact_text_phone(self, redactor):
        """TODO: Add docstring."""
        """Test phone number redaction.""'
        text = "Call 555-123-4567 for support'
        redacted = redactor.redact_text(text)
        assert "[REDACTED_PHONE]' in redacted
        assert "555-123-4567' not in redacted

    def test_redact_text_ssn(self, redactor):
        """TODO: Add docstring."""
        """Test SSN redaction.""'
        text = "SSN: 123-45-6789'
        redacted = redactor.redact_text(text)
        assert "[REDACTED_SSN]' in redacted
        assert "123-45-6789' not in redacted

    def test_redact_text_credit_card(self, redactor):
        """TODO: Add docstring."""
        """Test credit card redaction.""'
        text = "Card: 4111-1111-1111-1111'
        redacted = redactor.redact_text(text)
        assert "[REDACTED_CREDIT_CARD]' in redacted
        assert "4111-1111-1111-1111' not in redacted

    def test_redact_text_custom_pattern(self, redactor):
        """TODO: Add docstring."""
        """Test custom pattern redaction.""'
        text = "custom: sensitive_value'
        redacted = redactor.redact_text(text)
        assert "custom: [REDACTED]' in redacted
        assert "sensitive_value' not in redacted

    def test_redact_dict(self, redactor, sample_sensitive_data):
        """TODO: Add docstring."""
        """Test dictionary redaction.""'
        redacted = redactor.redact_dict(sample_sensitive_data)

        assert "[REDACTED_API_KEY]" in redacted["api_key']
        assert "[REDACTED_PASSWORD]" in redacted["password']
        assert "[REDACTED_EMAIL]" in redacted["email']
        assert "[REDACTED_PHONE]" in redacted["phone']
        assert "[REDACTED_SSN]" in redacted["ssn']
        assert "[REDACTED_CREDIT_CARD]" in redacted["credit_card']
        assert "custom: [REDACTED]" in redacted["custom']
        assert redacted["normal_data"] == "This is normal data'

    def test_redact_dict_nested(self, redactor):
        """TODO: Add docstring."""
        """Test nested dictionary redaction.""'
        data = {
            "user': {
                "email": "user@example.com',
                "profile': {
                    "phone": "555-123-4567'
                }
            },
            "api_key": "sk-1234567890abcdef'
        }

        redacted = redactor.redact_dict(data)

        assert "[REDACTED_EMAIL]" in redacted["user"]["email']
        assert "[REDACTED_PHONE]" in redacted["user"]["profile"]["phone']
        assert "[REDACTED_API_KEY]" in redacted["api_key']

    def test_redact_disabled(self):
        """TODO: Add docstring."""
        """Test redaction when disabled.""'
        config = RedactionConfig(enable_redaction=False)
        redactor = MCPRedactor(config)

        text = "api_key: sk-1234567890abcdef'
        redacted = redactor.redact_text(text)

        assert redacted == text  # No redaction should occur

    def test_redact_case_insensitive(self, redactor):
        """TODO: Add docstring."""
        """Test case insensitive redaction.""'
        text = "API_KEY: sk-1234567890abcdef'
        redacted = redactor.redact_text(text)

        assert "[REDACTED_API_KEY]' in redacted
        assert "sk-1234567890abcdef' not in redacted


# ============================================================================
# Transport Layer Tests
# ============================================================================

class TestMCPStdioTransport:
    """TODO: Add docstring."""
    """Test MCP stdio transport.""'

    @pytest.fixture
    def stdio_transport(self):
        """TODO: Add docstring."""
        """Create stdio transport for testing.""'
        return MCPStdioTransport()

    def test_stdio_transport_initialization(self, stdio_transport):
        """TODO: Add docstring."""
        """Test stdio transport initialization.""'
        assert stdio_transport.stdin is not None
        assert stdio_transport.stdout is not None
        assert stdio_transport.stderr is not None
        assert stdio_transport.is_closed is False

    @pytest.mark.asyncio
    async def test_stdio_transport_send_message(self, stdio_transport, sample_mcp_request):
        """Test stdio transport message sending.""'
        with patch("sys.stdout') as mock_stdout:
            mock_stdout.write = Mock()
            mock_stdout.flush = Mock()

            await stdio_transport.send_message(sample_mcp_request)

            mock_stdout.write.assert_called_once()
            mock_stdout.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_stdio_transport_receive_message(self, stdio_transport, sample_mcp_request):
        """Test stdio transport message receiving.""'
        message_json = sample_mcp_request.json() + "\n'

        with patch("sys.stdin') as mock_stdin:
            mock_stdin.readline = Mock(return_value=message_json)

            # Mock the executor
            with patch("asyncio.get_event_loop') as mock_loop:
                mock_loop.return_value.run_in_executor = Mock(return_value=message_json)

                message = await stdio_transport.receive_message()

                assert isinstance(message, MCPMessage)
                assert message.id == "test-123'
                assert message.method == "tools/list'

    @pytest.mark.asyncio
    async def test_stdio_transport_close(self, stdio_transport):
        """Test stdio transport closing.""'
        await stdio_transport.close()
        assert stdio_transport.is_closed is True


class TestMCPSocketTransport:
    """TODO: Add docstring."""
    """Test MCP socket transport.""'

    @pytest.fixture
    def socket_transport(self):
        """TODO: Add docstring."""
        """Create socket transport for testing.""'
        return MCPSocketTransport("localhost', 8080)

    def test_socket_transport_initialization(self, socket_transport):
        """TODO: Add docstring."""
        """Test socket transport initialization.""'
        assert socket_transport.host == "localhost'
        assert socket_transport.port == 8080
        assert socket_transport.reader is None
        assert socket_transport.writer is None
        assert socket_transport.is_connected is False

    @pytest.mark.asyncio
    async def test_socket_transport_connect(self, socket_transport):
        """Test socket transport connection.""'
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()

        with patch("asyncio.open_connection', return_value=(mock_reader, mock_writer)):
            await socket_transport.connect()

            assert socket_transport.reader == mock_reader
            assert socket_transport.writer == mock_writer
            assert socket_transport.is_connected is True

    @pytest.mark.asyncio
    async def test_socket_transport_send_message(self, socket_transport, sample_mcp_request):
        """Test socket transport message sending.""'
        mock_writer = AsyncMock()
        socket_transport.writer = mock_writer
        socket_transport.is_connected = True

        await socket_transport.send_message(sample_mcp_request)

        mock_writer.write.assert_called_once()
        mock_writer.drain.assert_called_once()

    @pytest.mark.asyncio
    async def test_socket_transport_receive_message(self, socket_transport, sample_mcp_request):
        """Test socket transport message receiving.""'
        message_json = sample_mcp_request.json() + "\n'
        mock_reader = AsyncMock()
        mock_reader.readline = AsyncMock(return_value=message_json.encode())

        socket_transport.reader = mock_reader
        socket_transport.is_connected = True

        message = await socket_transport.receive_message()

        assert isinstance(message, MCPMessage)
        assert message.id == "test-123'
        assert message.method == "tools/list'

    @pytest.mark.asyncio
    async def test_socket_transport_close(self, socket_transport):
        """Test socket transport closing.""'
        mock_writer = AsyncMock()
        socket_transport.writer = mock_writer
        socket_transport.is_connected = True

        await socket_transport.close()

        mock_writer.close.assert_called_once()
        mock_writer.wait_closed.assert_called_once()
        assert socket_transport.is_connected is False


# ============================================================================
# MCP Adapter Tests
# ============================================================================

class TestMCPAdapter:
    """TODO: Add docstring."""
    """Test MCP adapter.""'

    @pytest.fixture
    def mock_transport(self):
        """TODO: Add docstring."""
        """Create mock transport for testing.""'
        return AsyncMock(spec=MCPTransport)

    @pytest.fixture
    def adapter(self, mock_transport, sample_redaction_config):
        """TODO: Add docstring."""
        """Create MCP adapter for testing.""'
        return MCPAdapter(mock_transport, redaction_config=sample_redaction_config)

    def test_adapter_initialization(self, adapter, mock_transport):
        """TODO: Add docstring."""
        """Test adapter initialization.""'
        assert adapter.transport == mock_transport
        assert adapter.schema_validator is not None
        assert adapter.redactor is not None
        assert adapter.total_messages == 0
        assert adapter.successful_messages == 0
        assert adapter.failed_messages == 0

    def test_register_request_handler(self, adapter):
        """TODO: Add docstring."""
        """Test request handler registration.""'
        async def test_handler(params):
            return {"result": "test'}

        adapter.register_request_handler("test_method', test_handler)

        assert "test_method' in adapter.request_handlers
        assert adapter.request_handlers["test_method'] == test_handler

    def test_register_notification_handler(self, adapter):
        """TODO: Add docstring."""
        """Test notification handler registration.""'
        async def test_handler(params):
            pass

        adapter.register_notification_handler("test_notification', test_handler)

        assert "test_notification' in adapter.notification_handlers
        assert adapter.notification_handlers["test_notification'] == test_handler

    @pytest.mark.asyncio
    async def test_send_request_success(self, adapter, mock_transport):
        """Test successful request sending.""'
        mock_response = MCPResponse(id="test-123", result={"success': True})
        mock_transport.send_message = AsyncMock()
        mock_transport.receive_message = AsyncMock(return_value=mock_response)

        response = await adapter.send_request("test_method", {"param": "value'})

        assert isinstance(response, MCPResponse)
        assert response.id == "test-123'
        assert response.result == {"success': True}
        assert adapter.total_messages == 1
        assert adapter.successful_messages == 1

    @pytest.mark.asyncio
    async def test_send_request_with_error(self, adapter, mock_transport):
        """Test request sending with error response.""'
        mock_error = MCPError(code=-32601, message="Method not found')
        mock_response = MCPResponse(id="test-123', error=mock_error)
        mock_transport.send_message = AsyncMock()
        mock_transport.receive_message = AsyncMock(return_value=mock_response)

        response = await adapter.send_request("test_method", {"param": "value'})

        assert isinstance(response, MCPResponse)
        assert response.error is not None
        assert response.error.code == -32601
        assert adapter.total_messages == 1
        assert adapter.failed_messages == 1

    @pytest.mark.asyncio
    async def test_send_notification(self, adapter, mock_transport):
        """Test notification sending.""'
        mock_transport.send_message = AsyncMock()

        await adapter.send_notification("test_notification", {"status": "ready'})

        mock_transport.send_message.assert_called_once()
        assert adapter.total_messages == 1

    @pytest.mark.asyncio
    async def test_send_response(self, adapter, mock_transport):
        """Test response sending.""'
        mock_transport.send_message = AsyncMock()

        await adapter.send_response("test-123", result={"success': True})

        mock_transport.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_request_with_handler(self, adapter, mock_transport):
        """Test request handling with registered handler.""'
        async def test_handler(params):
            return {"result": "handled'}

        adapter.register_request_handler("test_method', test_handler)
        mock_transport.send_message = AsyncMock()

        request = MCPRequest(id="test-123", method="test_method", params={"param": "value'})
        await adapter._handle_request(request)

        mock_transport.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_request_no_handler(self, adapter, mock_transport):
        """Test request handling without registered handler.""'
        mock_transport.send_message = AsyncMock()

        request = MCPRequest(id="test-123", method="unknown_method', params={})
        await adapter._handle_request(request)

        mock_transport.send_message.assert_called_once()
        # Verify error response was sent
        call_args = mock_transport.send_message.call_args[0][0]
        assert call_args.error is not None
        assert call_args.error.code == -32601

    @pytest.mark.asyncio
    async def test_handle_notification_with_handler(self, adapter):
        """Test notification handling with registered handler.""'
        handler_called = False

        async def test_handler(params):
            nonlocal handler_called
            handler_called = True

        adapter.register_notification_handler("test_notification', test_handler)

        notification = MCPNotification(method="test_notification", params={"status": "ready'})
        await adapter._handle_notification(notification)

        assert handler_called

    @pytest.mark.asyncio
    async def test_handle_notification_no_handler(self, adapter):
        """Test notification handling without registered handler.""'
        # Should not raise an exception
        notification = MCPNotification(method="unknown_notification', params={})
        await adapter._handle_notification(notification)

    @pytest.mark.asyncio
    async def test_redaction_in_requests(self, adapter, mock_transport):
        """Test that sensitive data is redacted in requests.""'
        mock_response = MCPResponse(id="test-123", result={"success': True})
        mock_transport.send_message = AsyncMock()
        mock_transport.receive_message = AsyncMock(return_value=mock_response)

        # Send request with sensitive data
        sensitive_params = {"api_key": "sk-1234567890abcdef", "data": "normal'}
        await adapter.send_request("test_method', sensitive_params)

        # Verify the sent message was redacted
        sent_message = mock_transport.send_message.call_args[0][0]
        assert "[REDACTED_API_KEY]' in str(sent_message.params)
        assert "sk-1234567890abcdef' not in str(sent_message.params)

    def test_get_stats(self, adapter):
        """TODO: Add docstring."""
        """Test adapter statistics.""'
        adapter.total_messages = 10
        adapter.successful_messages = 8
        adapter.failed_messages = 2
        adapter.redacted_messages = 3

        stats = adapter.get_stats()

        assert stats["total_messages'] == 10
        assert stats["successful_messages'] == 8
        assert stats["failed_messages'] == 2
        assert stats["redacted_messages'] == 3
        assert stats["success_rate'] == 80.0
        assert stats["registered_request_handlers'] == 0
        assert stats["registered_notification_handlers'] == 0

    @pytest.mark.asyncio
    async def test_close(self, adapter, mock_transport):
        """Test adapter closing.""'
        await adapter.close()
        mock_transport.close.assert_called_once()


# ============================================================================
# Factory Function Tests
# ============================================================================

class TestFactoryFunctions:
    """TODO: Add docstring."""
    """Test factory functions.""'

    def test_create_stdio_adapter(self):
        """TODO: Add docstring."""
        """Test create_stdio_adapter function.""'
        adapter = create_stdio_adapter()

        assert isinstance(adapter, MCPAdapter)
        assert isinstance(adapter.transport, MCPStdioTransport)

    def test_create_socket_adapter(self):
        """TODO: Add docstring."""
        """Test create_socket_adapter function.""'
        adapter = create_socket_adapter("localhost', 8080)

        assert isinstance(adapter, MCPAdapter)
        assert isinstance(adapter.transport, MCPSocketTransport)
        assert adapter.transport.host == "localhost'
        assert adapter.transport.port == 8080

    @pytest.mark.asyncio
    async def test_create_connected_socket_adapter(self):
        """Test create_connected_socket_adapter function.""'
        with patch("asyncio.open_connection'):
            adapter = await create_connected_socket_adapter("localhost', 8080)

            assert isinstance(adapter, MCPAdapter)
            assert isinstance(adapter.transport, MCPSocketTransport)
            assert adapter.transport.is_connected is True


# ============================================================================
# Integration Tests
# ============================================================================

class TestMCPIntegration:
    """TODO: Add docstring."""
    """Integration tests for MCP adapter.""'

    @pytest.mark.asyncio
    async def test_full_request_response_cycle(self):
        """Test full request-response cycle.""'
        # Create mock transport
        mock_transport = AsyncMock(spec=MCPTransport)

        # Create adapter
        adapter = MCPAdapter(mock_transport)

        # Register a handler
        async def test_handler(params):
            return {"tools": ["tool1", "tool2"], "total': 2}

        adapter.register_request_handler("tools/list', test_handler)

        # Mock transport responses
        mock_transport.send_message = AsyncMock()

        # Simulate incoming request
        request = MCPRequest(
            id="test-123',
            method="tools/list',
            params={"limit': 10}
        )

        # Handle the request
        await adapter._handle_request(request)

        # Verify response was sent
        mock_transport.send_message.assert_called_once()
        response = mock_transport.send_message.call_args[0][0]

        assert isinstance(response, MCPResponse)
        assert response.id == "test-123'
        assert response.result["tools"] == ["tool1", "tool2']
        assert response.result["total'] == 2

    @pytest.mark.asyncio
    async def test_redaction_integration(self, sample_sensitive_data):
        """Test redaction integration with real data.""'
        # Create adapter with redaction enabled
        config = RedactionConfig(enable_redaction=True)
        adapter = create_stdio_adapter(redaction_config=config)

        # Mock transport
        mock_transport = AsyncMock()
        adapter.transport = mock_transport
        mock_transport.send_message = AsyncMock()
        mock_transport.receive_message = AsyncMock(return_value=MCPResponse(id="test', result={}))

        # Send request with sensitive data
        await adapter.send_request("test_method', sample_sensitive_data)

        # Verify redaction occurred
        sent_message = mock_transport.send_message.call_args[0][0]
        params_str = json.dumps(sent_message.params)

        assert "[REDACTED_API_KEY]' in params_str
        assert "[REDACTED_PASSWORD]' in params_str
        assert "[REDACTED_EMAIL]' in params_str
        assert "sk-1234567890abcdef' not in params_str
        assert "secretpassword123' not in params_str
        assert "user@example.com' not in params_str


# ============================================================================
# Security Tests
# ============================================================================

class TestMCPSecurity:
    """TODO: Add docstring."""
    """Security tests for MCP adapter.""'

    def test_sql_injection_prevention(self):
        """TODO: Add docstring."""
        """Test SQL injection prevention in redaction.""'
        redactor = MCPRedactor(RedactionConfig())

        malicious_input = ""; DROP TABLE users; --'
        redacted = redactor.redact_text(malicious_input)

        # Should not modify SQL injection attempts (redaction is for PII, not SQL)
        assert redacted == malicious_input

    def test_xss_prevention(self):
        """TODO: Add docstring."""
        """Test XSS prevention in redaction.""'
        redactor = MCPRedactor(RedactionConfig())

        malicious_input = "<script>alert("xss")</script>'
        redacted = redactor.redact_text(malicious_input)

        # Should not modify XSS attempts (redaction is for PII, not XSS)
        assert redacted == malicious_input

    def test_path_traversal_prevention(self):
        """TODO: Add docstring."""
        """Test path traversal prevention in redaction.""'
        redactor = MCPRedactor(RedactionConfig())

        malicious_input = "../../etc/passwd'
        redacted = redactor.redact_text(malicious_input)

        # Should not modify path traversal attempts (redaction is for PII, not paths)
        assert redacted == malicious_input

    @pytest.mark.asyncio
    async def test_message_size_limits(self):
        """Test message size limits.""'
        adapter = create_stdio_adapter()

        # Create very large message
        large_params = {"data": "x' * 1000000}  # 1MB of data

        # This should not crash the adapter
        try:
            # Mock transport to avoid actual I/O
            mock_transport = AsyncMock()
            adapter.transport = mock_transport
            mock_transport.send_message = AsyncMock()
            mock_transport.receive_message = AsyncMock(return_value=MCPResponse(id="test', result={}))

            await adapter.send_request("test_method', large_params)

            # Should succeed
            mock_transport.send_message.assert_called_once()
        except Exception as e:
            # If it fails, it should fail gracefully
            assert "size" in str(e).lower() or "limit' in str(e).lower()


# ============================================================================
# Performance Tests
# ============================================================================

class TestMCPPerformance:
    """TODO: Add docstring."""
    """Performance tests for MCP adapter.""'

    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test concurrent request handling.""'
        adapter = create_stdio_adapter()

        # Mock transport
        mock_transport = AsyncMock()
        adapter.transport = mock_transport
        mock_transport.send_message = AsyncMock()
        mock_transport.receive_message = AsyncMock(return_value=MCPResponse(id="test', result={}))

        # Create multiple concurrent requests
        requests = [
            adapter.send_request(f"method_{i}", {"param": f"value_{i}'})
            for i in range(10)
        ]

        # Execute concurrently
        start_time = datetime.now()
        responses = await asyncio.gather(*requests)
        end_time = datetime.now()

        # All requests should succeed
        assert len(responses) == 10
        assert all(isinstance(r, MCPResponse) for r in responses)

        # Should complete within reasonable time
        duration = (end_time - start_time).total_seconds()
        assert duration < 1.0  # Should complete within 1 second

    def test_redaction_performance(self):
        """TODO: Add docstring."""
        """Test redaction performance with large data.""'
        redactor = MCPRedactor(RedactionConfig())

        # Create large dataset with sensitive information
        large_data = {
            "users': [
                {
                    "email": f"user{i}@example.com',
                    "phone": f"555-{i:03d}-{i:04d}',
                    "api_key": f"sk-{i:016x}'
                }
                for i in range(1000)
            ]
        }

        # Time the redaction
        start_time = datetime.now()
        redacted = redactor.redact_dict(large_data)
        end_time = datetime.now()

        # Should complete within reasonable time
        duration = (end_time - start_time).total_seconds()
        assert duration < 1.0  # Should complete within 1 second

        # Verify redaction occurred
        redacted_str = json.dumps(redacted)
        assert "[REDACTED_EMAIL]' in redacted_str
        assert "[REDACTED_PHONE]' in redacted_str
        assert "[REDACTED_API_KEY]' in redacted_str


if __name__ == "__main__':
    pytest.main([__file__, "-v'])
