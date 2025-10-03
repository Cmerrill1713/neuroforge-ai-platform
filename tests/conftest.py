"""
Test configuration and fixtures for the AI Agent Platform.
"""

import asyncio
import os
import pytest
import pytest_asyncio
from typing import Dict, Any, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

# Test configuration
TEST_CONFIG = {
    "api_url": "http://localhost:8000",
    "ws_url": "ws://localhost:8000",
    "database_url": os.getenv("DATABASE_URL", "postgresql://test:test@localhost:5432/test"),
    "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
    "timeout": 30,
}

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Test configuration fixture."""
    return TEST_CONFIG.copy()

@pytest.fixture(scope="function")
async def api_client(test_config):
    """API client fixture for testing."""
    import httpx

    async with httpx.AsyncClient(
        base_url=test_config["api_url"],
        timeout=test_config["timeout"]
    ) as client:
        yield client

@pytest.fixture(scope="function")
async def websocket_client(test_config):
    """WebSocket client fixture for testing."""
    import websockets
    import json

    uri = f"{test_config['ws_url']}/ws"
    connection = None

    try:
        connection = await websockets.connect(uri)
        yield connection
    finally:
        if connection:
            await connection.close()

@pytest.fixture(scope="function")
def mock_agent_selector():
    """Mock agent selector for unit testing."""
    mock = AsyncMock()
    mock.select_agent.return_value = {
        "agent_name": "test_agent",
        "confidence": 0.95,
        "reasoning": "Test reasoning",
        "performance_metrics": {}
    }
    return mock

@pytest.fixture(scope="function")
def mock_rag_system():
    """Mock RAG system for unit testing."""
    mock = AsyncMock()
    mock.search_similar.return_value = [
        {
            "id": "test_chunk_1",
            "content": "Test content",
            "similarity_score": 0.9,
            "metadata": {"source": "test"}
        }
    ]
    mock.get_database_stats.return_value = {
        "total_documents": 100,
        "collection_name": "test_collection",
        "vector_dimension": 384
    }
    return mock

@pytest.fixture(scope="function")
def mock_response_cache():
    """Mock response cache for unit testing."""
    mock = AsyncMock()
    mock.get.return_value = None
    mock.set.return_value = True
    return mock

@pytest.fixture(scope="function")
def sample_chat_request():
    """Sample chat request for testing."""
    return {
        "message": "Hello, how are you?",
        "task_type": "text_generation",
        "input_type": "text",
        "latency_requirement": 1000,
        "max_tokens": 1024,
        "temperature": 0.7,
        "session_id": "test_session_123"
    }

@pytest.fixture(scope="function")
def sample_knowledge_query():
    """Sample knowledge base query for testing."""
    return {
        "query": "What is machine learning?",
        "limit": 5,
        "threshold": 0.8,
        "use_cache": True
    }

@pytest.fixture(scope="function")
def sample_websocket_message():
    """Sample WebSocket message for testing."""
    return {
        "type": "chat",
        "data": {
            "message": "Test message",
            "max_tokens": 100
        },
        "session_id": "test_session_123",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Performance testing fixtures
@pytest.fixture(scope="function")
def performance_timer():
    """Timer fixture for performance testing."""
    import time
    start_time = time.time()
    yield lambda: time.time() - start_time

# Security testing fixtures
@pytest.fixture(scope="function")
def malicious_payload():
    """Malicious payload for security testing."""
    return {
        "message": "<script>alert('xss')</script>",
        "task_type": "text_generation",
        "input_type": "text"
    }

@pytest.fixture(scope="function")
def oversized_payload():
    """Oversized payload for testing limits."""
    return {
        "message": "x" * 100000,  # 100KB message
        "task_type": "text_generation",
        "input_type": "text"
    }

# Database fixtures
@pytest.fixture(scope="session")
async def test_database():
    """Test database fixture."""
    # This would set up a test database
    # For now, return a mock
    mock_db = AsyncMock()
    yield mock_db
    # Cleanup would go here

# Redis fixtures
@pytest.fixture(scope="session")
async def test_redis():
    """Test Redis fixture."""
    # This would set up a test Redis instance
    # For now, return a mock
    mock_redis = AsyncMock()
    yield mock_redis
    # Cleanup would go here

# Custom pytest marks
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )

# Test data fixtures
@pytest.fixture(scope="session")
def test_documents():
    """Test documents for RAG testing."""
    return [
        {
            "title": "Machine Learning Basics",
            "content": "Machine learning is a subset of artificial intelligence...",
            "source": "test_doc_1",
            "category": "education"
        },
        {
            "title": "Neural Networks",
            "content": "Neural networks are computing systems inspired by...",
            "source": "test_doc_2",
            "category": "technical"
        }
    ]

@pytest.fixture(scope="session")
def test_embeddings():
    """Test embeddings for RAG testing."""
    import numpy as np
    return np.random.rand(10, 384).astype(np.float32)
