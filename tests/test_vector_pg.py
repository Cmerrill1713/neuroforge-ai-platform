""'
Tests for PostgreSQL Vector Store

Comprehensive test suite for the PostgreSQL vector store including:
- Database connection and schema creation
- Document indexing and retrieval
- Vector similarity search
- Metadata filtering and querying
- Performance and error handling
- Integration with existing Docker infrastructure

Created: 2024-09-24
Status: Draft
""'

import asyncio
import pytest
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any
from unittest.mock import Mock, AsyncMock, patch

from src.core.memory.vector_pg import (
    # Enums
    DocumentType,
    DocumentStatus,

    # Models
    Document,
    SearchResult,
    VectorIndex,
    PostgreSQLConfig,

    # Implementation
    PostgreSQLVectorStore,

    # Factory functions
    create_postgresql_vector_store,
    create_and_initialize_vector_store,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_document():
    """TODO: Add docstring."""
    """Sample document for testing.""'
    return Document(
        content="This is a test document about artificial intelligence and machine learning.',
        title="AI Test Document',
        doc_type=DocumentType.TEXT,
        metadata={"category": "technology", "author": "test_user'},
        source="test_source.txt'
    )


@pytest.fixture
def sample_documents():
    """TODO: Add docstring."""
    """Sample documents for testing.""'
    return [
        Document(
            content="Machine learning is a subset of artificial intelligence.',
            title="ML Basics',
            doc_type=DocumentType.TEXT,
            metadata={"category": "technology", "topic": "machine_learning'},
            source="ml_basics.txt'
        ),
        Document(
            content="Natural language processing enables computers to understand human language.',
            title="NLP Overview',
            doc_type=DocumentType.TEXT,
            metadata={"category": "technology", "topic": "nlp'},
            source="nlp_overview.txt'
        ),
        Document(
            content="Computer vision allows machines to interpret visual information.',
            title="CV Introduction',
            doc_type=DocumentType.TEXT,
            metadata={"category": "technology", "topic": "computer_vision'},
            source="cv_intro.txt'
        )
    ]


@pytest.fixture
def sample_vectors():
    """TODO: Add docstring."""
    """Sample vectors for testing.""'
    return [
        [0.1, 0.2, 0.3, 0.4, 0.5] * 307,  # 1535 dimensions + 1 = 1536
        [0.2, 0.3, 0.4, 0.5, 0.6] * 307,
        [0.3, 0.4, 0.5, 0.6, 0.7] * 307
    ]


@pytest.fixture
def postgresql_config():
    """TODO: Add docstring."""
    """PostgreSQL configuration for testing.""'
    return PostgreSQLConfig(
        host="localhost',
        port=5432,
        database="agi_agents',
        username="agi_user',
        password="default_db_password',
        vector_dimension=1536,
        min_connections=1,
        max_connections=5
    )


@pytest.fixture
def vector_store(postgresql_config):
    """TODO: Add docstring."""
    """Create vector store for testing.""'
    return PostgreSQLVectorStore(postgresql_config)


# ============================================================================
# Configuration Tests
# ============================================================================

class TestPostgreSQLConfig:
    """TODO: Add docstring."""
    """Test PostgreSQL configuration.""'

    def test_default_config(self):
        """TODO: Add docstring."""
        """Test default configuration values.""'
        config = PostgreSQLConfig()

        assert config.host == "localhost'
        assert config.port == 5432
        assert config.database == "agi_agents'
        assert config.username == "agi_user'
        assert config.password == "default_db_password'
        assert config.vector_dimension == 1536
        assert config.min_connections == 5
        assert config.max_connections == 20

    def test_custom_config(self):
        """TODO: Add docstring."""
        """Test custom configuration.""'
        config = PostgreSQLConfig(
            host="test_host',
            port=5433,
            database="test_db',
            username="test_user',
            password="test_pass',
            vector_dimension=1024
        )

        assert config.host == "test_host'
        assert config.port == 5433
        assert config.database == "test_db'
        assert config.username == "test_user'
        assert config.password == "test_pass'
        assert config.vector_dimension == 1024

    def test_config_validation(self):
        """TODO: Add docstring."""
        """Test configuration validation.""'
        # Valid config
        config = PostgreSQLConfig(
            port=5432,
            min_connections=1,
            max_connections=10,
            vector_dimension=512
        )
        assert config.port == 5432

        # Invalid port
        with pytest.raises(ValueError):
            PostgreSQLConfig(port=0)

        # Invalid connections
        with pytest.raises(ValueError):
            PostgreSQLConfig(min_connections=0)


# ============================================================================
# Document Model Tests
# ============================================================================

class TestDocument:
    """TODO: Add docstring."""
    """Test Document model.""'

    def test_document_creation(self, sample_document):
        """TODO: Add docstring."""
        """Test document creation.""'
        assert sample_document.content == "This is a test document about artificial intelligence and machine learning.'
        assert sample_document.title == "AI Test Document'
        assert sample_document.doc_type == DocumentType.TEXT
        assert sample_document.metadata == {"category": "technology", "author": "test_user'}
        assert sample_document.source == "test_source.txt'
        assert sample_document.status == DocumentStatus.PENDING

    def test_document_defaults(self):
        """TODO: Add docstring."""
        """Test document defaults.""'
        doc = Document(content="Test content')

        assert doc.content == "Test content'
        assert doc.title is None
        assert doc.doc_type == DocumentType.TEXT
        assert doc.metadata == {}
        assert doc.status == DocumentStatus.PENDING
        assert doc.source is None
        assert doc.chunk_index is None
        assert doc.parent_id is None
        assert isinstance(doc.id, str)
        assert isinstance(doc.created_at, datetime)
        assert isinstance(doc.updated_at, datetime)

    def test_document_validation(self):
        """TODO: Add docstring."""
        """Test document validation.""'
        # Valid document
        doc = Document(content="Valid content')
        assert doc.content == "Valid content'

        # Empty content
        with pytest.raises(ValueError):
            Document(content="')

        # Whitespace only content
        with pytest.raises(ValueError):
            Document(content="   ')

        # Invalid metadata
        with pytest.raises(ValueError):
            Document(content="Test", metadata={"invalid': object()})


class TestSearchResult:
    """TODO: Add docstring."""
    """Test SearchResult model.""'

    def test_search_result_creation(self, sample_document):
        """TODO: Add docstring."""
        """Test search result creation.""'
        result = SearchResult(
            document=sample_document,
            similarity_score=0.95,
            distance=0.05,
            rank=1
        )

        assert result.document == sample_document
        assert result.similarity_score == 0.95
        assert result.distance == 0.05
        assert result.rank == 1

    def test_search_result_validation(self, sample_document):
        """TODO: Add docstring."""
        """Test search result validation.""'
        # Valid result
        result = SearchResult(
            document=sample_document,
            similarity_score=0.5,
            distance=0.5,
            rank=1
        )
        assert result.similarity_score == 0.5

        # Invalid similarity score
        with pytest.raises(ValueError):
            SearchResult(
                document=sample_document,
                similarity_score=1.5,
                distance=0.5,
                rank=1
            )

        # Invalid rank
        with pytest.raises(ValueError):
            SearchResult(
                document=sample_document,
                similarity_score=0.5,
                distance=0.5,
                rank=0
            )


# ============================================================================
# PostgreSQL Vector Store Tests
# ============================================================================

class TestPostgreSQLVectorStore:
    """TODO: Add docstring."""
    """Test PostgreSQL vector store.""'

    @pytest.fixture
    def mock_pool(self):
        """TODO: Add docstring."""
        """Create mock connection pool.""'
        return AsyncMock()

    @pytest.fixture
    def mock_conn(self):
        """TODO: Add docstring."""
        """Create mock connection.""'
        return AsyncMock()

    def test_vector_store_initialization(self, vector_store, postgresql_config):
        """TODO: Add docstring."""
        """Test vector store initialization.""'
        assert vector_store.config == postgresql_config
        assert vector_store.pool is None
        assert vector_store.total_documents == 0
        assert vector_store.total_queries == 0
        assert vector_store.total_indexes == 0

    @pytest.mark.asyncio
    async def test_initialize_success(self, vector_store, mock_pool, mock_conn):
        """Test successful initialization.""'
        with patch("asyncpg.create_pool', return_value=mock_pool):
            mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

            await vector_store.initialize()

            assert vector_store.pool == mock_pool
            mock_conn.execute.assert_called()

    @pytest.mark.asyncio
    async def test_initialize_failure(self, vector_store):
        """Test initialization failure.""'
        with patch("asyncpg.create_pool", side_effect=Exception("Connection failed')):
            with pytest.raises(Exception):
                await vector_store.initialize()

    @pytest.mark.asyncio
    async def test_index_success(self, vector_store, sample_documents, sample_vectors, mock_pool, mock_conn):
        """Test successful document indexing.""'
        vector_store.pool = mock_pool
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.fetchrow.return_value = {"id": "test-id-1'}

        indexed_ids = await vector_store.index(sample_documents, sample_vectors)

        assert len(indexed_ids) == 3
        assert vector_store.total_indexes == 3
        mock_conn.execute.assert_called()

    @pytest.mark.asyncio
    async def test_index_mismatch(self, vector_store, sample_documents, sample_vectors):
        """Test indexing with mismatched documents and vectors.""'
        # Remove one vector to create mismatch
        mismatched_vectors = sample_vectors[:2]

        with pytest.raises(ValueError):
            await vector_store.index(sample_documents, mismatched_vectors)

    @pytest.mark.asyncio
    async def test_index_wrong_dimension(self, vector_store, sample_documents):
        """Test indexing with wrong vector dimension.""'
        wrong_vectors = [[0.1, 0.2, 0.3]] * 3  # Only 3 dimensions instead of 1536

        with pytest.raises(ValueError):
            await vector_store.index(sample_documents, wrong_vectors)

    @pytest.mark.asyncio
    async def test_query_success(self, vector_store, sample_vectors, mock_pool, mock_conn):
        """Test successful vector query.""'
        vector_store.pool = mock_pool
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        # Mock query result
        mock_row = {
            "id": "test-id',
            "content": "Test content',
            "title": "Test title',
            "doc_type": "text',
            "metadata": {"category": "test'},
            "status": "indexed',
            "created_at': datetime.now(timezone.utc),
            "updated_at': datetime.now(timezone.utc),
            "source": "test.txt',
            "chunk_index': None,
            "parent_id': None,
            "similarity_score': 0.95,
            "distance': 0.05
        }
        mock_conn.fetch.return_value = [mock_row]

        query_vector = sample_vectors[0]
        results = await vector_store.query(query_vector, limit=5)

        assert len(results) == 1
        assert results[0].similarity_score == 0.95
        assert results[0].distance == 0.05
        assert results[0].rank == 1
        assert vector_store.total_queries == 1

    @pytest.mark.asyncio
    async def test_query_with_metadata_filter(self, vector_store, sample_vectors, mock_pool, mock_conn):
        """Test query with metadata filtering.""'
        vector_store.pool = mock_pool
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.fetch.return_value = []

        query_vector = sample_vectors[0]
        filter_metadata = {"category": "technology'}

        results = await vector_store.query(query_vector, limit=5, filter_metadata=filter_metadata)

        assert len(results) == 0
        mock_conn.fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_wrong_dimension(self, vector_store):
        """Test query with wrong vector dimension.""'
        wrong_vector = [0.1, 0.2, 0.3]  # Only 3 dimensions

        with pytest.raises(ValueError):
            await vector_store.query(wrong_vector)

    @pytest.mark.asyncio
    async def test_get_success(self, vector_store, mock_pool, mock_conn):
        """Test successful document retrieval.""'
        vector_store.pool = mock_pool
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        # Mock get result
        mock_row = {
            "id": "test-id',
            "content": "Test content',
            "title": "Test title',
            "doc_type": "text',
            "metadata": {"category": "test'},
            "status": "indexed',
            "created_at': datetime.now(timezone.utc),
            "updated_at': datetime.now(timezone.utc),
            "source": "test.txt',
            "chunk_index': None,
            "parent_id': None
        }
        mock_conn.fetch.return_value = [mock_row]

        documents = await vector_store.get(["test-id'])

        assert len(documents) == 1
        assert documents[0].id == "test-id'
        assert documents[0].content == "Test content'

    @pytest.mark.asyncio
    async def test_get_empty_list(self, vector_store):
        """Test getting empty document list.""'
        documents = await vector_store.get([])
        assert documents == []

    @pytest.mark.asyncio
    async def test_delete_success(self, vector_store, mock_pool, mock_conn):
        """Test successful document deletion.""'
        vector_store.pool = mock_pool
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.execute.return_value = "UPDATE 2'

        result = await vector_store.delete(["test-id-1", "test-id-2'])

        assert result is True
        mock_conn.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_empty_list(self, vector_store):
        """Test deleting empty document list.""'
        result = await vector_store.delete([])
        assert result is True

    @pytest.mark.asyncio
    async def test_update_success(self, vector_store, sample_document, sample_vectors, mock_pool, mock_conn):
        """Test successful document update.""'
        vector_store.pool = mock_pool
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.execute.return_value = "UPDATE 1'

        result = await vector_store.update("test-id', sample_document, sample_vectors[0])

        assert result is True
        mock_conn.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_without_vector(self, vector_store, sample_document, mock_pool, mock_conn):
        """Test document update without vector.""'
        vector_store.pool = mock_pool
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.execute.return_value = "UPDATE 1'

        result = await vector_store.update("test-id', sample_document)

        assert result is True
        mock_conn.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_by_metadata_success(self, vector_store, mock_pool, mock_conn):
        """Test successful metadata search.""'
        vector_store.pool = mock_pool
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        # Mock search result
        mock_row = {
            "id": "test-id',
            "content": "Test content',
            "title": "Test title',
            "doc_type": "text',
            "metadata": {"category": "technology'},
            "status": "indexed',
            "created_at': datetime.now(timezone.utc),
            "updated_at': datetime.now(timezone.utc),
            "source": "test.txt',
            "chunk_index': None,
            "parent_id': None
        }
        mock_conn.fetch.return_value = [mock_row]

        metadata = {"category": "technology'}
        documents = await vector_store.search_by_metadata(metadata, limit=5)

        assert len(documents) == 1
        assert documents[0].metadata["category"] == "technology'

    @pytest.mark.asyncio
    async def test_search_by_metadata_empty(self, vector_store):
        """Test metadata search with empty metadata.""'
        documents = await vector_store.search_by_metadata({})
        assert documents == []

    @pytest.mark.asyncio
    async def test_get_stats_success(self, vector_store, mock_pool, mock_conn):
        """Test successful stats retrieval.""'
        vector_store.pool = mock_pool
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        # Mock stats results
        mock_conn.fetch.side_effect = [
            [{"status": "indexed", "count": 10}, {"status": "pending", "count': 2}],
            [{"doc_type": "text", "count": 8}, {"doc_type": "pdf", "count': 2}],
            [{"count': 12}],
            [{"pg_size_pretty": "1.2 MB'}]
        ]

        stats = await vector_store.get_stats()

        assert "total_documents' in stats
        assert "status_counts' in stats
        assert "type_counts' in stats
        assert "index_size' in stats
        assert "vector_dimension' in stats
        assert stats["vector_dimension'] == 1536

    @pytest.mark.asyncio
    async def test_health_check_success(self, vector_store, mock_pool, mock_conn):
        """Test successful health check.""'
        vector_store.pool = mock_pool
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.fetchval.side_effect = [1, None]  # SELECT 1, vector test

        health = await vector_store.health_check()

        assert health["status"] == "healthy'
        assert health["database_connected'] is True
        assert health["vector_extension_available'] is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, vector_store):
        """Test health check failure.""'
        vector_store.pool = None

        health = await vector_store.health_check()

        assert health["status"] == "unhealthy'
        assert health["database_connected'] is False

    @pytest.mark.asyncio
    async def test_close(self, vector_store, mock_pool):
        """Test vector store closing.""'
        vector_store.pool = mock_pool

        await vector_store.close()

        mock_pool.close.assert_called_once()


# ============================================================================
# Factory Function Tests
# ============================================================================

class TestFactoryFunctions:
    """TODO: Add docstring."""
    """Test factory functions.""'

    def test_create_postgresql_vector_store(self):
        """TODO: Add docstring."""
        """Test create_postgresql_vector_store function.""'
        store = create_postgresql_vector_store(
            database="test_db',
            username="test_user',
            password="test_pass',
            host="test_host',
            port=5433,
            vector_dimension=1024
        )

        assert isinstance(store, PostgreSQLVectorStore)
        assert store.config.database == "test_db'
        assert store.config.username == "test_user'
        assert store.config.password == "test_pass'
        assert store.config.host == "test_host'
        assert store.config.port == 5433
        assert store.config.vector_dimension == 1024

    def test_create_postgresql_vector_store_defaults(self):
        """TODO: Add docstring."""
        """Test create_postgresql_vector_store with defaults.""'
        store = create_postgresql_vector_store(
            database="test_db',
            username="test_user',
            password="test_pass'
        )

        assert store.config.host == "localhost'
        assert store.config.port == 5432
        assert store.config.vector_dimension == 1536

    @pytest.mark.asyncio
    async def test_create_and_initialize_vector_store(self):
        """Test create_and_initialize_vector_store function.""'
        with patch("asyncpg.create_pool') as mock_create_pool:
            mock_pool = AsyncMock()
            mock_create_pool.return_value = mock_pool

            store = await create_and_initialize_vector_store(
                database="test_db',
                username="test_user',
                password="test_pass'
            )

            assert isinstance(store, PostgreSQLVectorStore)
            assert store.pool == mock_pool


# ============================================================================
# Integration Tests
# ============================================================================

class TestPostgreSQLIntegration:
    """TODO: Add docstring."""
    """Integration tests for PostgreSQL vector store.""'

    @pytest.mark.asyncio
    async def test_full_workflow(self, postgresql_config):
        """Test full workflow: initialize -> index -> query -> get -> delete.""'
        # Skip if no real database connection
        pytest.skip("Integration test requires real database connection')

        store = PostgreSQLVectorStore(postgresql_config)

        try:
            # Initialize
            await store.initialize()

            # Create test documents and vectors
            documents = [
                Document(
                    content="This is a test document about machine learning.',
                    title="ML Test',
                    metadata={"category": "ai", "topic": "ml'}
                ),
                Document(
                    content="This is another document about natural language processing.',
                    title="NLP Test',
                    metadata={"category": "ai", "topic": "nlp'}
                )
            ]

            vectors = [
                [0.1] * 1536,
                [0.2] * 1536
            ]

            # Index documents
            indexed_ids = await store.index(documents, vectors)
            assert len(indexed_ids) == 2

            # Query similar documents
            query_vector = [0.15] * 1536
            results = await store.query(query_vector, limit=2)
            assert len(results) <= 2

            # Get documents by ID
            retrieved_docs = await store.get(indexed_ids)
            assert len(retrieved_docs) == 2

            # Search by metadata
            metadata_results = await store.search_by_metadata({"category": "ai'})
            assert len(metadata_results) >= 2

            # Delete documents
            delete_result = await store.delete(indexed_ids)
            assert delete_result is True

        finally:
            await store.close()


# ============================================================================
# Performance Tests
# ============================================================================

class TestPostgreSQLPerformance:
    """TODO: Add docstring."""
    """Performance tests for PostgreSQL vector store.""'

    @pytest.mark.asyncio
    async def test_batch_indexing_performance(self, vector_store, mock_pool, mock_conn):
        """Test batch indexing performance.""'
        vector_store.pool = mock_pool
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.fetchrow.return_value = {"id": "test-id'}

        # Create large batch
        documents = [
            Document(content=f"Test document {i}", title=f"Doc {i}')
            for i in range(100)
        ]
        vectors = [[0.1] * 1536 for _ in range(100)]

        start_time = datetime.now()
        indexed_ids = await vector_store.index(documents, vectors)
        end_time = datetime.now()

        assert len(indexed_ids) == 100
        duration = (end_time - start_time).total_seconds()
        assert duration < 5.0  # Should complete within 5 seconds

    @pytest.mark.asyncio
    async def test_concurrent_queries(self, vector_store, mock_pool, mock_conn):
        """Test concurrent query performance.""'
        vector_store.pool = mock_pool
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.fetch.return_value = []

        # Create multiple concurrent queries
        query_vector = [0.1] * 1536
        queries = [
            vector_store.query(query_vector, limit=10)
            for _ in range(10)
        ]

        start_time = datetime.now()
        results = await asyncio.gather(*queries)
        end_time = datetime.now()

        assert len(results) == 10
        duration = (end_time - start_time).total_seconds()
        assert duration < 2.0  # Should complete within 2 seconds


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestPostgreSQLErrorHandling:
    """TODO: Add docstring."""
    """Error handling tests for PostgreSQL vector store.""'

    @pytest.mark.asyncio
    async def test_connection_error(self, vector_store):
        """Test connection error handling.""'
        with patch("asyncpg.create_pool", side_effect=Exception("Connection failed')):
            with pytest.raises(Exception):
                await vector_store.initialize()

    @pytest.mark.asyncio
    async def test_query_error(self, vector_store, mock_pool, mock_conn):
        """Test query error handling.""'
        vector_store.pool = mock_pool
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.fetch.side_effect = Exception("Query failed')

        query_vector = [0.1] * 1536

        with pytest.raises(Exception):
            await vector_store.query(query_vector)

    @pytest.mark.asyncio
    async def test_index_error(self, vector_store, sample_documents, sample_vectors, mock_pool, mock_conn):
        """Test indexing error handling.""'
        vector_store.pool = mock_pool
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.fetchrow.side_effect = Exception("Index failed')

        with pytest.raises(Exception):
            await vector_store.index(sample_documents, sample_vectors)


if __name__ == "__main__':
    pytest.main([__file__, "-v'])
