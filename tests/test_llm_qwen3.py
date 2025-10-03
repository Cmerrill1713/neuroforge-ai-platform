""'
Tests for Qwen3 LLM Provider

Comprehensive test suite for the Qwen3 LLM provider including:
- Complete mode testing
- Embed mode testing
- Vision-to-text mode testing
- Context and rate limiting
- Local-small fallback functionality

Created: 2024-09-24
Status: Draft
""'

import asyncio
import pytest
from datetime import datetime, timedelta
from typing import List, Dict, Any
from unittest.mock import Mock, AsyncMock, patch

from src.core.providers.llm_qwen3 import (
    # Enums
    Qwen3Mode,
    Qwen3Device,
    Qwen3Precision,

    # Configuration models
    ContextLimits,
    RateLimits,
    Qwen3Config,

    # Request models
    Qwen3CompleteRequest,
    Qwen3EmbedRequest,
    Qwen3VisionRequest,

    # Response models
    Qwen3CompleteResponse,
    Qwen3EmbedResponse,
    Qwen3VisionResponse,

    # Core classes
    RateLimiter,
    ContextManager,
    LocalSmallFallback,
    Qwen3Provider,

    # Factory functions
    create_qwen3_provider,
    create_qwen3_provider_for_apple_silicon,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_context_limits():
    """TODO: Add docstring."""
    """Sample context limits for testing.""'
    return ContextLimits(
        max_tokens=8192,
        max_prompt_tokens=6144,
        max_completion_tokens=2048,
        reserve_tokens=100
    )


@pytest.fixture
def sample_rate_limits():
    """TODO: Add docstring."""
    """Sample rate limits for testing.""'
    return RateLimits(
        requests_per_minute=60,
        tokens_per_minute=100000,
        concurrent_requests=5
    )


@pytest.fixture
def sample_qwen3_config(sample_context_limits, sample_rate_limits):
    """TODO: Add docstring."""
    """Sample Qwen3 configuration for testing.""'
    return Qwen3Config(
        model_path="/models/qwen3-omni',
        model_name="qwen3-omni',
        device=Qwen3Device.MPS,
        precision=Qwen3Precision.FLOAT16,
        context_limits=sample_context_limits,
        rate_limits=sample_rate_limits,
        enable_fallback=True,
        fallback_model_path="/models/local-small'
    )


@pytest.fixture
def sample_complete_request():
    """TODO: Add docstring."""
    """Sample completion request for testing.""'
    return Qwen3CompleteRequest(
        prompt="What is artificial intelligence?',
        system_message="You are a helpful AI assistant.',
        temperature=0.7,
        max_tokens=100
    )


@pytest.fixture
def sample_embed_request():
    """TODO: Add docstring."""
    """Sample embedding request for testing.""'
    return Qwen3EmbedRequest(
        texts=["Hello world", "AI is amazing'],
        normalize=True,
        pooling_strategy="mean'
    )


@pytest.fixture
def sample_vision_request():
    """TODO: Add docstring."""
    """Sample vision request for testing.""'
    return Qwen3VisionRequest(
        image_data=b"fake_image_data',
        prompt="Describe this image',
        max_tokens=512
    )


# ============================================================================
# Configuration Model Tests
# ============================================================================

class TestContextLimits:
    """TODO: Add docstring."""
    """Test ContextLimits model.""'

    def test_valid_context_limits(self, sample_context_limits):
        """TODO: Add docstring."""
        """Test valid context limits creation.""'
        assert sample_context_limits.max_tokens == 8192
        assert sample_context_limits.max_prompt_tokens == 6144
        assert sample_context_limits.max_completion_tokens == 2048
        assert sample_context_limits.reserve_tokens == 100

    def test_context_limits_defaults(self):
        """TODO: Add docstring."""
        """Test context limits with defaults.""'
        limits = ContextLimits()
        assert limits.max_tokens == 8192
        assert limits.max_prompt_tokens == 6144
        assert limits.max_completion_tokens == 2048
        assert limits.reserve_tokens == 100

    def test_context_limits_validation(self):
        """TODO: Add docstring."""
        """Test context limits validation.""'
        # Valid limits
        limits = ContextLimits(max_tokens=16384, max_prompt_tokens=12288)
        assert limits.max_tokens == 16384
        assert limits.max_prompt_tokens == 12288

        # Invalid limits (should raise validation error)
        with pytest.raises(ValueError):
            ContextLimits(max_tokens=0)  # Below minimum

        with pytest.raises(ValueError):
            ContextLimits(max_tokens=50000)  # Above maximum


class TestRateLimits:
    """TODO: Add docstring."""
    """Test RateLimits model.""'

    def test_valid_rate_limits(self, sample_rate_limits):
        """TODO: Add docstring."""
        """Test valid rate limits creation.""'
        assert sample_rate_limits.requests_per_minute == 60
        assert sample_rate_limits.tokens_per_minute == 100000
        assert sample_rate_limits.concurrent_requests == 5

    def test_rate_limits_defaults(self):
        """TODO: Add docstring."""
        """Test rate limits with defaults.""'
        limits = RateLimits()
        assert limits.requests_per_minute == 60
        assert limits.tokens_per_minute == 100000
        assert limits.concurrent_requests == 5

    def test_rate_limits_validation(self):
        """TODO: Add docstring."""
        """Test rate limits validation.""'
        # Valid limits
        limits = RateLimits(requests_per_minute=100)
        assert limits.requests_per_minute == 100

        # Invalid limits
        with pytest.raises(ValueError):
            RateLimits(requests_per_minute=2000)  # Above maximum

        with pytest.raises(ValueError):
            RateLimits(requests_per_minute=0)  # Below minimum


class TestQwen3Config:
    """TODO: Add docstring."""
    """Test Qwen3Config model.""'

    def test_valid_qwen3_config(self, sample_qwen3_config):
        """TODO: Add docstring."""
        """Test valid Qwen3 config creation.""'
        assert sample_qwen3_config.model_path == "/models/qwen3-omni'
        assert sample_qwen3_config.model_name == "qwen3-omni'
        assert sample_qwen3_config.device == Qwen3Device.MPS
        assert sample_qwen3_config.precision == Qwen3Precision.FLOAT16
        assert sample_qwen3_config.enable_fallback is True
        assert sample_qwen3_config.fallback_model_path == "/models/local-small'

    def test_qwen3_config_defaults(self):
        """TODO: Add docstring."""
        """Test Qwen3 config with defaults.""'
        config = Qwen3Config(model_path="/models/qwen3')
        assert config.model_name == "qwen3-omni'
        assert config.device == Qwen3Device.MPS
        assert config.precision == Qwen3Precision.FLOAT16
        assert config.batch_size == 1
        assert config.enable_fallback is True


# ============================================================================
# Request/Response Model Tests
# ============================================================================

class TestQwen3CompleteRequest:
    """TODO: Add docstring."""
    """Test Qwen3CompleteRequest model.""'

    def test_valid_complete_request(self, sample_complete_request):
        """TODO: Add docstring."""
        """Test valid completion request creation.""'
        assert sample_complete_request.mode == Qwen3Mode.COMPLETE
        assert sample_complete_request.prompt == "What is artificial intelligence?'
        assert sample_complete_request.system_message == "You are a helpful AI assistant.'
        assert sample_complete_request.temperature == 0.7
        assert sample_complete_request.max_tokens == 100
        assert sample_complete_request.stop_sequences == []

    def test_complete_request_defaults(self):
        """TODO: Add docstring."""
        """Test completion request with defaults.""'
        request = Qwen3CompleteRequest(prompt="Test prompt')
        assert request.mode == Qwen3Mode.COMPLETE
        assert request.temperature == 0.7
        assert request.top_p == 0.9
        assert request.max_tokens is None
        assert request.stream is False
        assert request.stop_sequences == []

    def test_complete_request_validation(self):
        """TODO: Add docstring."""
        """Test completion request validation.""'
        # Valid parameters
        request = Qwen3CompleteRequest(
            prompt="Test',
            temperature=1.5,
            top_p=0.8,
            frequency_penalty=0.5,
            presence_penalty=-0.5
        )
        assert request.temperature == 1.5
        assert request.top_p == 0.8

        # Invalid parameters
        with pytest.raises(ValueError):
            Qwen3CompleteRequest(prompt="Test', temperature=3.0)  # Above maximum

        with pytest.raises(ValueError):
            Qwen3CompleteRequest(prompt="Test', top_p=1.5)  # Above maximum


class TestQwen3EmbedRequest:
    """TODO: Add docstring."""
    """Test Qwen3EmbedRequest model.""'

    def test_valid_embed_request(self, sample_embed_request):
        """TODO: Add docstring."""
        """Test valid embedding request creation.""'
        assert sample_embed_request.mode == Qwen3Mode.EMBED
        assert sample_embed_request.texts == ["Hello world", "AI is amazing']
        assert sample_embed_request.normalize is True
        assert sample_embed_request.pooling_strategy == "mean'

    def test_embed_request_defaults(self):
        """TODO: Add docstring."""
        """Test embedding request with defaults.""'
        request = Qwen3EmbedRequest(texts=["Test text'])
        assert request.mode == Qwen3Mode.EMBED
        assert request.normalize is True
        assert request.pooling_strategy == "mean'


class TestQwen3VisionRequest:
    """TODO: Add docstring."""
    """Test Qwen3VisionRequest model.""'

    def test_valid_vision_request(self, sample_vision_request):
        """TODO: Add docstring."""
        """Test valid vision request creation.""'
        assert sample_vision_request.mode == Qwen3Mode.VISION_TO_TEXT
        assert sample_vision_request.image_data == b"fake_image_data'
        assert sample_vision_request.prompt == "Describe this image'
        assert sample_vision_request.max_tokens == 512

    def test_vision_request_defaults(self):
        """TODO: Add docstring."""
        """Test vision request with defaults.""'
        request = Qwen3VisionRequest(image_data=b"test')
        assert request.mode == Qwen3Mode.VISION_TO_TEXT
        assert request.prompt is None
        assert request.max_tokens == 1024


# ============================================================================
# Rate Limiter Tests
# ============================================================================

class TestRateLimiter:
    """TODO: Add docstring."""
    """Test RateLimiter class.""'

    @pytest.fixture
    def rate_limiter(self, sample_rate_limits):
        """TODO: Add docstring."""
        """Create rate limiter for testing.""'
        return RateLimiter(sample_rate_limits)

    @pytest.mark.asyncio
    async def test_rate_limiter_acquire_success(self, rate_limiter):
        """Test successful rate limiter acquisition.""'
        result = await rate_limiter.acquire(estimated_tokens=100)
        assert result is True
        assert rate_limiter.active_requests == 1

    @pytest.mark.asyncio
    async def test_rate_limiter_concurrent_limit(self, rate_limiter):
        """Test concurrent request limit.""'
        # Acquire all available slots
        for _ in range(5):  # max concurrent requests
            result = await rate_limiter.acquire(estimated_tokens=100)
            assert result is True

        # Next request should fail
        result = await rate_limiter.acquire(estimated_tokens=100)
        assert result is False

    @pytest.mark.asyncio
    async def test_rate_limiter_release(self, rate_limiter):
        """Test rate limiter release.""'
        await rate_limiter.acquire(estimated_tokens=100)
        assert rate_limiter.active_requests == 1

        await rate_limiter.release(actual_tokens=100)
        assert rate_limiter.active_requests == 0

    @pytest.mark.asyncio
    async def test_rate_limiter_token_limit(self, rate_limiter):
        """Test token rate limit.""'
        # Acquire requests up to token limit
        large_token_count = 50000  # Half of tokens_per_minute
        result = await rate_limiter.acquire(estimated_tokens=large_token_count)
        assert result is True

        # Another large request should fail
        result = await rate_limiter.acquire(estimated_tokens=large_token_count + 1)
        assert result is False


# ============================================================================
# Context Manager Tests
# ============================================================================

class TestContextManager:
    """TODO: Add docstring."""
    """Test ContextManager class.""'

    @pytest.fixture
    def context_manager(self, sample_context_limits):
        """TODO: Add docstring."""
        """Create context manager for testing.""'
        return ContextManager(sample_context_limits)

    def test_validate_context_success(self, context_manager):
        """TODO: Add docstring."""
        """Test successful context validation.""'
        prompt = "A' * 1000  # Small prompt
        result = context_manager.validate_context(prompt, max_completion=100)
        assert result is True

    def test_validate_context_failure(self, context_manager):
        """TODO: Add docstring."""
        """Test failed context validation.""'
        prompt = "A' * 100000  # Very large prompt
        result = context_manager.validate_context(prompt, max_completion=1000)
        assert result is False

    def test_truncate_prompt(self, context_manager):
        """TODO: Add docstring."""
        """Test prompt truncation.""'
        large_prompt = "A' * 50000  # Very large prompt
        truncated = context_manager.truncate_prompt(large_prompt)

        assert len(truncated) < len(large_prompt)
        assert truncated.endswith("...')

    def test_truncate_prompt_no_truncation_needed(self, context_manager):
        """TODO: Add docstring."""
        """Test prompt truncation when not needed.""'
        small_prompt = "A' * 100  # Small prompt
        truncated = context_manager.truncate_prompt(small_prompt)

        assert truncated == small_prompt


# ============================================================================
# Local Small Fallback Tests
# ============================================================================

class TestLocalSmallFallback:
    """TODO: Add docstring."""
    """Test LocalSmallFallback class.""'

    @pytest.fixture
    def fallback(self):
        """TODO: Add docstring."""
        """Create fallback for testing.""'
        return LocalSmallFallback("/models/local-small')

    @pytest.mark.asyncio
    async def test_fallback_load_model(self, fallback):
        """Test fallback model loading.""'
        await fallback.load_model()
        assert fallback.is_loaded is True

    @pytest.mark.asyncio
    async def test_fallback_complete(self, fallback, sample_complete_request):
        """Test fallback completion.""'
        await fallback.load_model()
        response = await fallback.complete(sample_complete_request)

        assert isinstance(response, Qwen3CompleteResponse)
        assert response.success is True
        assert response.mode == Qwen3Mode.COMPLETE
        assert response.text is not None
        assert "Fallback response' in response.text

    @pytest.mark.asyncio
    async def test_fallback_embed(self, fallback, sample_embed_request):
        """Test fallback embedding.""'
        await fallback.load_model()
        response = await fallback.embed(sample_embed_request)

        assert isinstance(response, Qwen3EmbedResponse)
        assert response.success is True
        assert response.mode == Qwen3Mode.EMBED
        assert response.embeddings is not None
        assert len(response.embeddings) == len(sample_embed_request.texts)
        assert response.embedding_dimension == 384


# ============================================================================
# Qwen3 Provider Tests
# ============================================================================

class TestQwen3Provider:
    """TODO: Add docstring."""
    """Test Qwen3Provider class.""'

    @pytest.fixture
    def provider(self, sample_qwen3_config):
        """TODO: Add docstring."""
        """Create Qwen3 provider for testing.""'
        return Qwen3Provider(sample_qwen3_config)

    @pytest.mark.asyncio
    async def test_provider_initialization(self, provider):
        """Test provider initialization.""'
        assert provider.config is not None
        assert provider.rate_limiter is not None
        assert provider.context_manager is not None
        assert provider.fallback is not None
        assert provider.is_loaded is False

    @pytest.mark.asyncio
    async def test_provider_initialize(self, provider):
        """Test provider initialization process.""'
        # Mock the model loading
        with patch.object(provider, "_load_model', new_callable=AsyncMock):
            await provider.initialize()
            assert provider.is_loaded is True

    @pytest.mark.asyncio
    async def test_provider_complete_success(self, provider, sample_complete_request):
        """Test successful text completion.""'
        # Mock the model as loaded
        provider.is_loaded = True

        response = await provider.complete(sample_complete_request)

        assert isinstance(response, Qwen3CompleteResponse)
        assert response.success is True
        assert response.mode == Qwen3Mode.COMPLETE
        assert response.text is not None
        assert response.processing_time > 0
        assert response.tokens_used > 0

    @pytest.mark.asyncio
    async def test_provider_complete_with_fallback(self, provider, sample_complete_request):
        """Test completion with fallback when model not loaded.""'
        provider.is_loaded = False

        response = await provider.complete(sample_complete_request)

        assert isinstance(response, Qwen3CompleteResponse)
        assert response.success is True
        assert "Fallback response' in response.text

    @pytest.mark.asyncio
    async def test_provider_embed_success(self, provider, sample_embed_request):
        """Test successful text embedding.""'
        provider.is_loaded = True

        response = await provider.embed(sample_embed_request)

        assert isinstance(response, Qwen3EmbedResponse)
        assert response.success is True
        assert response.mode == Qwen3Mode.EMBED
        assert response.embeddings is not None
        assert len(response.embeddings) == len(sample_embed_request.texts)
        assert response.embedding_dimension == 1024

    @pytest.mark.asyncio
    async def test_provider_vision_to_text_success(self, provider, sample_vision_request):
        """Test successful vision-to-text conversion.""'
        provider.is_loaded = True

        response = await provider.vision_to_text(sample_vision_request)

        assert isinstance(response, Qwen3VisionResponse)
        assert response.success is True
        assert response.mode == Qwen3Mode.VISION_TO_TEXT
        assert response.text is not None
        assert response.confidence_score is not None

    @pytest.mark.asyncio
    async def test_provider_complete_stream(self, provider, sample_complete_request):
        """Test streaming completion.""'
        provider.is_loaded = True

        chunks = []
        async for chunk in provider.complete_stream(sample_complete_request):
            chunks.append(chunk)

        assert len(chunks) > 0
        assert any("Qwen3 completion' in chunk for chunk in chunks)

    def test_provider_get_stats(self, provider):
        """TODO: Add docstring."""
        """Test provider statistics.""'
        stats = provider.get_stats()

        assert "total_requests' in stats
        assert "successful_requests' in stats
        assert "fallback_requests' in stats
        assert "success_rate' in stats
        assert "total_tokens' in stats
        assert "is_loaded' in stats
        assert "fallback_available' in stats

    @pytest.mark.asyncio
    async def test_provider_health_check(self, provider):
        """Test provider health check.""'
        health = await provider.health_check()

        assert "status' in health
        assert "model_loaded' in health
        assert "fallback_available' in health
        assert "rate_limiter_active' in health
        assert "timestamp' in health


# ============================================================================
# Factory Function Tests
# ============================================================================

class TestFactoryFunctions:
    """TODO: Add docstring."""
    """Test factory functions.""'

    def test_create_qwen3_provider(self):
        """TODO: Add docstring."""
        """Test create_qwen3_provider function.""'
        provider = create_qwen3_provider(
            model_path="/models/qwen3',
            device=Qwen3Device.CPU,
            enable_fallback=False
        )

        assert isinstance(provider, Qwen3Provider)
        assert provider.config.model_path == "/models/qwen3'
        assert provider.config.device == Qwen3Device.CPU
        assert provider.config.enable_fallback is False

    def test_create_qwen3_provider_for_apple_silicon(self):
        """TODO: Add docstring."""
        """Test create_qwen3_provider_for_apple_silicon function.""'
        provider = create_qwen3_provider_for_apple_silicon("/models/qwen3')

        assert isinstance(provider, Qwen3Provider)
        assert provider.config.device == Qwen3Device.MPS
        assert provider.config.precision == Qwen3Precision.FLOAT16
        assert provider.config.use_mps_acceleration is True
        assert provider.config.optimize_for_inference is True


# ============================================================================
# Integration Tests
# ============================================================================

class TestQwen3Integration:
    """TODO: Add docstring."""
    """Integration tests for Qwen3 provider.""'

    @pytest.fixture
    def provider(self):
        """TODO: Add docstring."""
        """Create provider for integration testing.""'
        config = Qwen3Config(
            model_path="/models/qwen3',
            enable_fallback=True,
            fallback_model_path="/models/local-small'
        )
        return Qwen3Provider(config)

    @pytest.mark.asyncio
    async def test_complete_workflow(self, provider):
        """Test complete workflow from request to response.""'
        request = Qwen3CompleteRequest(
            prompt="Explain quantum computing in simple terms.',
            max_tokens=200
        )

        # Mock model as loaded
        provider.is_loaded = True

        response = await provider.complete(request)

        assert response.success is True
        assert response.text is not None
        assert response.processing_time > 0
        assert response.tokens_used > 0

    @pytest.mark.asyncio
    async def test_embed_workflow(self, provider):
        """Test embedding workflow.""'
        request = Qwen3EmbedRequest(
            texts=["Quantum computing", "Machine learning", "Artificial intelligence'],
            normalize=True
        )

        provider.is_loaded = True

        response = await provider.embed(request)

        assert response.success is True
        assert response.embeddings is not None
        assert len(response.embeddings) == 3
        assert all(len(emb) == 1024 for emb in response.embeddings)

    @pytest.mark.asyncio
    async def test_vision_workflow(self, provider):
        """Test vision-to-text workflow.""'
        request = Qwen3VisionRequest(
            image_data=b"fake_image_data_12345',
            prompt="What do you see in this image?',
            max_tokens=100
        )

        provider.is_loaded = True

        response = await provider.vision_to_text(request)

        assert response.success is True
        assert response.text is not None
        assert response.confidence_score is not None
        assert 0.0 <= response.confidence_score <= 1.0

    @pytest.mark.asyncio
    async def test_fallback_workflow(self, provider):
        """Test fallback workflow when main model fails.""'
        request = Qwen3CompleteRequest(
            prompt="Test prompt for fallback',
            max_tokens=50
        )

        # Ensure model is not loaded to trigger fallback
        provider.is_loaded = False

        response = await provider.complete(request)

        assert response.success is True
        assert "Fallback response' in response.text
        assert provider.fallback_requests > 0


# ============================================================================
# Performance Tests
# ============================================================================

class TestQwen3Performance:
    """TODO: Add docstring."""
    """Performance tests for Qwen3 provider.""'

    @pytest.fixture
    def provider(self):
        """TODO: Add docstring."""
        """Create provider for performance testing.""'
        config = Qwen3Config(
            model_path="/models/qwen3',
            batch_size=4,
            enable_fallback=False
        )
        return Qwen3Provider(config)

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, provider):
        """Test concurrent request handling.""'
        provider.is_loaded = True

        requests = [
            Qwen3CompleteRequest(prompt=f"Test prompt {i}', max_tokens=10)
            for i in range(10)
        ]

        # Run requests concurrently
        start_time = datetime.now()
        responses = await asyncio.gather(*[provider.complete(req) for req in requests])
        end_time = datetime.now()

        # All requests should succeed
        assert all(response.success for response in responses)

        # Should complete within reasonable time
        duration = (end_time - start_time).total_seconds()
        assert duration < 5.0  # Should complete within 5 seconds

    @pytest.mark.asyncio
    async def test_rate_limiting_performance(self, provider):
        """Test rate limiting performance.""'
        provider.is_loaded = True

        # Create many requests quickly
        requests = [
            Qwen3CompleteRequest(prompt=f"Rate limit test {i}', max_tokens=5)
            for i in range(100)
        ]

        start_time = datetime.now()
        responses = await asyncio.gather(*[provider.complete(req) for req in requests], return_exceptions=True)
        end_time = datetime.now()

        # Some requests should succeed, some might be rate limited
        successful_responses = [r for r in responses if isinstance(r, Qwen3CompleteResponse) and r.success]
        assert len(successful_responses) > 0

        # Should complete within reasonable time
        duration = (end_time - start_time).total_seconds()
        assert duration < 10.0


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestQwen3ErrorHandling:
    """TODO: Add docstring."""
    """Error handling tests for Qwen3 provider.""'

    @pytest.fixture
    def provider(self):
        """TODO: Add docstring."""
        """Create provider for error testing.""'
        config = Qwen3Config(
            model_path="/models/qwen3',
            enable_fallback=False  # Disable fallback to test error handling
        )
        return Qwen3Provider(config)

    @pytest.mark.asyncio
    async def test_model_not_loaded_error(self, provider, sample_complete_request):
        """Test error handling when model is not loaded.""'
        provider.is_loaded = False

        response = await provider.complete(sample_complete_request)

        assert response.success is False
        assert response.error_message is not None
        assert response.error_code == "COMPLETION_ERROR'

    @pytest.mark.asyncio
    async def test_rate_limit_error(self, provider, sample_complete_request):
        """Test rate limit error handling.""'
        provider.is_loaded = True

        # Exhaust rate limits
        for _ in range(10):
            await provider.rate_limiter.acquire(estimated_tokens=10000)

        response = await provider.complete(sample_complete_request)

        assert response.success is False
        assert "Rate limit' in response.error_message

    @pytest.mark.asyncio
    async def test_context_validation_error(self, provider):
        """Test context validation error handling.""'
        provider.is_loaded = True

        # Create request with very large context
        large_prompt = "A' * 100000  # Very large prompt
        request = Qwen3CompleteRequest(prompt=large_prompt, max_tokens=1000)

        response = await provider.complete(request)

        # Should succeed but with truncated prompt
        assert response.success is True
        assert response.text is not None


if __name__ == "__main__':
    pytest.main([__file__, "-v'])
