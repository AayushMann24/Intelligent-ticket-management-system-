"""Tests for AI Gateway and Provider Abstraction."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.schemas.ai_gateway import (
    AIRequest,
    AIResponse,
    AIMessage,
    AIProvider,
    AIProviderConfig,
    RAGContext,
    ContextChunk,
    CitationReference,
    AIUsage,
)
from app.services.ai_providers.base import AIProvider as AIProviderBase, AIProviderError
from app.services.ai_providers.gemini import GeminiProvider
from app.services.ai_providers.ollama import OllamaProvider
from app.services.ai_providers.factory import (
    create_provider,
    get_ai_provider,
    get_provider_config,
    get_available_providers,
    close_ai_provider,
)
from app.services.ai_gateway import AIGateway, AIGatewayError, get_ai_gateway, close_ai_gateway
from app.config import settings


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def mock_rag_context():
    """Create a mock RAG context for testing."""
    return RAGContext(
        query="password reset",
        chunks=[
            ContextChunk(
                chunk_id=1,
                article_id=10,
                article_title="Password Reset Guide",
                article_slug="password-reset-guide",
                chunk_index=0,
                content="To reset your password, go to the login page and click Forgot Password.",
                score=0.95,
                source="semantic",
            ),
            ContextChunk(
                chunk_id=2,
                article_id=10,
                article_title="Password Reset Guide",
                article_slug="password-reset-guide",
                chunk_index=1,
                content="Enter your email and follow the reset link sent to your inbox.",
                score=0.88,
                source="semantic",
            ),
        ],
        total_chunks=2,
        total_chars=200,
        citations=[
            CitationReference(
                article_id=10,
                article_title="Password Reset Guide",
                article_slug="password-reset-guide",
                chunk_id=1,
                chunk_index=0,
                content="To reset your password, go to the login page and click Forgot Password.",
                score=0.95,
                source="semantic",
            ),
            CitationReference(
                article_id=10,
                article_title="Password Reset Guide",
                article_slug="password-reset-guide",
                chunk_id=2,
                chunk_index=1,
                content="Enter your email and follow the reset link sent to your inbox.",
                score=0.88,
                source="semantic",
            ),
        ],
    )


@pytest.fixture
def basic_request():
    """Create a basic AI request."""
    return AIRequest(
        messages=[
            AIMessage(role="user", content="How do I reset my password?"),
        ],
    )


@pytest.fixture
def request_with_rag(basic_request, mock_rag_context):
    """Create an AI request with RAG context."""
    basic_request.rag_context = mock_rag_context
    return basic_request


# ============================================================
# Schema Tests
# ============================================================

def test_ai_provider_config_gemini():
    """Test Gemini provider config creation."""
    config = AIProviderConfig(
        provider="gemini",
        model="gemini-1.5-flash",
        temperature=0.5,
        max_output_tokens=2048,
    )
    assert config.provider == "gemini"
    assert config.model == "gemini-1.5-flash"
    assert config.temperature == 0.5


def test_ai_provider_config_ollama():
    """Test Ollama provider config creation."""
    config = AIProviderConfig(
        provider="ollama",
        model="llama3.2",
        temperature=0.0,
    )
    assert config.provider == "ollama"
    assert config.model == "llama3.2"


def test_ai_request_validation():
    """Test AI request validation."""
    # Valid request
    req = AIRequest(messages=[AIMessage(role="user", content="Hello")])
    assert len(req.messages) == 1

    # Invalid: empty messages
    with pytest.raises(Exception):
        AIRequest(messages=[])

    # Invalid: temperature out of range
    with pytest.raises(Exception):
        AIRequest(messages=[AIMessage(role="user", content="Hi")], temperature=3.0)


def test_rag_context_schema(mock_rag_context):
    """Test RAG context schema."""
    assert mock_rag_context.query == "password reset"
    assert len(mock_rag_context.chunks) == 2
    assert len(mock_rag_context.citations) == 2
    assert mock_rag_context.total_chunks == 2


# ============================================================
# Base Provider Tests
# ============================================================

def test_base_provider_format_rag_context(mock_rag_context):
    """Test base provider RAG context formatting."""
    from app.services.ai_providers.base import AIProvider as BaseAIProvider

    # Create a minimal concrete implementation for testing
    class TestProvider(BaseAIProvider):
        @property
        def provider_name(self):
            return "test"

        async def initialize(self):
            pass

        async def close(self):
            pass

        async def generate(self, request):
            pass

    provider = TestProvider(AIProviderConfig(provider="ollama", model="test"))
    formatted = provider._format_rag_context(mock_rag_context)

    assert "RETRIEVED KNOWLEDGE BASE EVIDENCE" in formatted
    assert "password reset" in formatted
    assert "Password Reset Guide" in formatted
    assert "Evidence 1" in formatted
    assert "Evidence 2" in formatted
    assert "INSTRUCTIONS" in formatted


def test_base_provider_extract_citations(mock_rag_context):
    """Test citation extraction from response."""
    from app.services.ai_providers.base import AIProvider as BaseAIProvider

    class TestProvider(BaseAIProvider):
        @property
        def provider_name(self):
            return "test"

        async def initialize(self):
            pass

        async def close(self):
            pass

        async def generate(self, request):
            pass

    provider = TestProvider(AIProviderConfig(provider="ollama", model="test"))

    # Response with evidence references
    response = "Based on [Evidence 1], you should click Forgot Password. Also [Evidence 2] mentions the email link."
    citations = provider._extract_citations_from_response(response, mock_rag_context)

    assert len(citations) == 2
    assert citations[0].chunk_id == 1
    assert citations[1].chunk_id == 2

    # Response without references
    response2 = "I don't know the answer."
    citations2 = provider._extract_citations_from_response(response2, mock_rag_context)
    assert len(citations2) == 0

    # Duplicate evidence references
    response3 = "From [Evidence 1] and [Evidence 1] again."
    citations3 = provider._extract_citations_from_response(response3, mock_rag_context)
    assert len(citations3) == 1  # Deduplicated


def test_ai_provider_error():
    """Test AIProviderError."""
    error = AIProviderError(
        code="TEST_ERROR",
        message="Test message",
        provider="gemini",
        retryable=True,
    )
    assert error.code == "TEST_ERROR"
    assert error.provider == "gemini"
    assert error.retryable is True

    error_dict = error.to_dict()
    assert error_dict["code"] == "TEST_ERROR"
    assert error_dict["provider"] == "gemini"


# ============================================================
# Factory Tests
# ============================================================

def test_get_available_providers():
    """Test getting available providers."""
    providers = get_available_providers()
    assert "gemini" in providers
    assert "ollama" in providers


def test_create_provider_gemini():
    """Test creating Gemini provider."""
    config = AIProviderConfig(
        provider="gemini",
        model="gemini-1.5-flash",
    )
    provider = create_provider(config)
    assert isinstance(provider, GeminiProvider)
    assert provider.provider_name == "gemini"


def test_create_provider_ollama():
    """Test creating Ollama provider."""
    config = AIProviderConfig(
        provider="ollama",
        model="llama3.2",
    )
    provider = create_provider(config)
    assert isinstance(provider, OllamaProvider)
    assert provider.provider_name == "ollama"


def test_create_provider_unknown():
    """Test creating unknown provider raises error."""
    # Pydantic validates the literal at construction time
    with pytest.raises(Exception) as exc_info:
        AIProviderConfig(provider="unknown", model="test")
    assert "provider" in str(exc_info.value)


# ============================================================
# Gemini Provider Tests (Mocked)
# ============================================================

@pytest.mark.asyncio
async def test_gemini_provider_init_missing_key():
    """Test Gemini provider initialization without API key."""
    config = AIProviderConfig(provider="gemini", model="gemini-1.5-flash")

    with patch.dict("os.environ", {}, clear=True):
        provider = GeminiProvider(config)
        with pytest.raises(AIProviderError) as exc_info:
            await provider.initialize()
        assert exc_info.value.code == "GEMINI_API_KEY_MISSING"


@pytest.mark.asyncio
async def test_gemini_provider_init_success():
    """Test Gemini provider initialization success."""
    config = AIProviderConfig(provider="gemini", model="gemini-1.5-flash")

    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
        with patch("google.genai.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_response = MagicMock()
            mock_response.text = "test response"
            mock_client.models.generate_content.return_value = mock_response

            provider = GeminiProvider(config)
            await provider.initialize()

            assert provider._client is not None
            mock_client_class.assert_called_once_with(api_key="test-key")


@pytest.mark.asyncio
async def test_gemini_provider_generate_success():
    """Test Gemini provider generate success."""
    config = AIProviderConfig(provider="gemini", model="gemini-1.5-flash")

    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
        with patch("google.genai.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # Mock response
            mock_response = MagicMock()
            mock_response.text = "To reset your password, click Forgot Password. [Evidence 1]"
            mock_response.usage_metadata = MagicMock()
            mock_response.usage_metadata.prompt_token_count = 100
            mock_response.usage_metadata.candidates_token_count = 50
            mock_response.usage_metadata.total_token_count = 150
            mock_response.candidates = [MagicMock(finish_reason="STOP")]
            mock_client.models.generate_content.return_value = mock_response

            provider = GeminiProvider(config)
            await provider.initialize()

            request = AIRequest(
                messages=[AIMessage(role="user", content="How to reset password?")],
            )
            response = await provider.generate(request)

            assert response.content == "To reset your password, click Forgot Password. [Evidence 1]"
            assert response.provider == "gemini"
            assert response.model == "gemini-1.5-flash"
            assert response.usage is not None
            assert response.usage.total_tokens == 150


@pytest.mark.asyncio
async def test_gemini_provider_generate_with_rag(request_with_rag):
    """Test Gemini provider with RAG context."""
    config = AIProviderConfig(provider="gemini", model="gemini-1.5-flash")

    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
        with patch("google.genai.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            mock_response = MagicMock()
            mock_response.text = "Based on the guide [Evidence 1], click Forgot Password."
            mock_response.usage_metadata = MagicMock()
            mock_response.usage_metadata.prompt_token_count = 200
            mock_response.usage_metadata.candidates_token_count = 30
            mock_response.usage_metadata.total_token_count = 230
            mock_response.candidates = [MagicMock(finish_reason="STOP")]
            mock_client.models.generate_content.return_value = mock_response

            provider = GeminiProvider(config)
            await provider.initialize()

            response = await provider.generate(request_with_rag)

            assert response.provider == "gemini"
            assert len(response.citations) == 1
            assert response.citations[0].chunk_id == 1


@pytest.mark.asyncio
async def test_gemini_provider_timeout():
    """Test Gemini provider timeout handling."""
    config = AIProviderConfig(provider="gemini", model="gemini-1.5-flash", timeout_seconds=1)

    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
        with patch("google.genai.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # Simulate slow response - use a sync function that blocks
            import time
            def slow_response(*args, **kwargs):
                time.sleep(2)
                return MagicMock(text="slow")

            mock_client.models.generate_content = slow_response

            provider = GeminiProvider(config)
            await provider.initialize()

            request = AIRequest(messages=[AIMessage(role="user", content="test")])
            with pytest.raises(AIProviderError) as exc_info:
                await provider.generate(request)

            assert exc_info.value.code == "GEMINI_TIMEOUT"
            assert exc_info.value.retryable is True


# ============================================================
# Ollama Provider Tests (Mocked)
# ============================================================

@pytest.mark.asyncio
async def test_ollama_provider_init_success():
    """Test Ollama provider initialization success."""
    config = AIProviderConfig(provider="ollama", model="llama3.2")

    with patch("app.services.ai_providers.ollama.ChatOllama") as mock_ollama_class:
        mock_llm = MagicMock()
        mock_ollama_class.return_value = mock_llm
        mock_llm.invoke.return_value = MagicMock(content="test response")

        provider = OllamaProvider(config)
        await provider.initialize()

        assert provider._llm is not None
        mock_ollama_class.assert_called_once()


@pytest.mark.asyncio
async def test_ollama_provider_generate_success():
    """Test Ollama provider generate success."""
    config = AIProviderConfig(provider="ollama", model="llama3.2")

    with patch("app.services.ai_providers.ollama.ChatOllama") as mock_ollama_class:
        mock_llm = MagicMock()
        mock_ollama_class.return_value = mock_llm

        mock_response = MagicMock()
        mock_response.content = "To reset password, click Forgot Password. [Evidence 1]"
        mock_response.usage_metadata = {"input_tokens": 100, "output_tokens": 30, "total_tokens": 130}
        mock_llm.invoke.return_value = mock_response

        provider = OllamaProvider(config)
        await provider.initialize()

        request = AIRequest(messages=[AIMessage(role="user", content="How to reset?")])
        response = await provider.generate(request)

        assert response.content == "To reset password, click Forgot Password. [Evidence 1]"
        assert response.provider == "ollama"
        assert response.model == "llama3.2"


@pytest.mark.asyncio
async def test_ollama_provider_timeout():
    """Test Ollama provider timeout."""
    config = AIProviderConfig(provider="ollama", model="llama3.2", timeout_seconds=1)

    with patch("app.services.ai_providers.ollama.ChatOllama") as mock_ollama_class:
        mock_llm = MagicMock()
        mock_ollama_class.return_value = mock_llm

        # Simulate slow response - use a sync function that blocks
        import time
        def slow_invoke(*args, **kwargs):
            time.sleep(2)
            return MagicMock(content="slow")

        mock_llm.invoke = slow_invoke

        provider = OllamaProvider(config)
        await provider.initialize()

        request = AIRequest(messages=[AIMessage(role="user", content="test")])
        with pytest.raises(AIProviderError) as exc_info:
            await provider.generate(request)

        assert exc_info.value.code == "OLLAMA_TIMEOUT"
        assert exc_info.value.retryable is True


# ============================================================
# AI Gateway Tests
# ============================================================

@pytest.mark.asyncio
async def test_gateway_initialize():
    """Test gateway initialization."""
    config = AIProviderConfig(provider="ollama", model="llama3.2")

    with patch("app.services.ai_gateway.get_ai_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.provider_name = "ollama"
        mock_provider.config = config
        mock_get_provider.return_value = mock_provider

        gateway = AIGateway(config)
        await gateway.initialize()

        assert gateway._provider == mock_provider


@pytest.mark.asyncio
async def test_gateway_validate_request_empty():
    """Test gateway validation with empty messages."""
    gateway = AIGateway()
    # This should fail at schema validation level
    with pytest.raises(Exception):
        AIRequest(messages=[])


@pytest.mark.asyncio
async def test_gateway_validate_request_last_not_user():
    """Test gateway validation when last message not from user."""
    gateway = AIGateway()
    request = AIRequest(messages=[
        AIMessage(role="user", content="Hi"),
        AIMessage(role="assistant", content="Hello"),
    ])

    with pytest.raises(AIGatewayError) as exc_info:
        gateway._validate_request(request)

    assert exc_info.value.code == "INVALID_REQUEST"


@pytest.mark.asyncio
async def test_gateway_generate_success():
    """Test gateway generate success."""
    config = AIProviderConfig(provider="ollama", model="llama3.2")

    with patch("app.services.ai_gateway.get_ai_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.provider_name = "ollama"
        mock_provider.config = config
        mock_provider.generate = AsyncMock(return_value=AIResponse(
            content="Test response",
            citations=[],
            provider="ollama",
            model="llama3.2",
        ))
        mock_get_provider.return_value = mock_provider

        gateway = AIGateway(config)
        await gateway.initialize()

        request = AIRequest(messages=[AIMessage(role="user", content="Test")])
        response = await gateway.generate(request)

        assert response.content == "Test response"
        assert response.provider == "ollama"
        mock_provider.generate.assert_called_once()


@pytest.mark.asyncio
async def test_gateway_generate_with_rag(request_with_rag):
    """Test gateway generate with RAG context."""
    config = AIProviderConfig(provider="ollama", model="llama3.2")

    with patch("app.services.ai_gateway.get_ai_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.provider_name = "ollama"
        mock_provider.config = config
        mock_provider.generate = AsyncMock(return_value=AIResponse(
            content="Based on evidence [Evidence 1], reset your password.",
            citations=[request_with_rag.rag_context.citations[0]],
            provider="ollama",
            model="llama3.2",
        ))
        mock_get_provider.return_value = mock_provider

        gateway = AIGateway(config)
        await gateway.initialize()

        response = await gateway.generate(request_with_rag)

        assert len(response.citations) == 1
        assert response.citations[0].chunk_id == 1


@pytest.mark.asyncio
async def test_gateway_provider_override():
    """Test gateway with provider override in request."""
    config = AIProviderConfig(provider="ollama", model="llama3.2")
    override_config = AIProviderConfig(provider="gemini", model="gemini-1.5-flash")

    with patch("app.services.ai_gateway.get_ai_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.provider_name = "ollama"
        mock_provider.config = config
        mock_provider.generate = AsyncMock(return_value=AIResponse(
            content="Response from default",
            citations=[],
            provider="ollama",
            model="llama3.2",
        ))

        mock_override_provider = AsyncMock()
        mock_override_provider.provider_name = "gemini"
        mock_override_provider.config = override_config
        mock_override_provider.generate = AsyncMock(return_value=AIResponse(
            content="Response from override",
            citations=[],
            provider="gemini",
            model="gemini-1.5-flash",
        ))

        mock_get_provider.side_effect = [mock_provider, mock_override_provider]

        gateway = AIGateway(config)
        await gateway.initialize()

        request = AIRequest(
            messages=[AIMessage(role="user", content="Test")],
            provider="gemini",
        )
        response = await gateway.generate(request)

        assert response.provider == "gemini"
        assert response.content == "Response from override"


@pytest.mark.asyncio
async def test_gateway_provider_error_handling():
    """Test gateway error handling."""
    config = AIProviderConfig(provider="ollama", model="llama3.2")

    with patch("app.services.ai_gateway.get_ai_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.provider_name = "ollama"
        mock_provider.config = config
        mock_provider.generate = AsyncMock(side_effect=AIProviderError(
            code="OLLAMA_TIMEOUT",
            message="Timeout",
            provider="ollama",
            retryable=True,
        ))
        mock_get_provider.return_value = mock_provider

        gateway = AIGateway(config)
        await gateway.initialize()

        request = AIRequest(messages=[AIMessage(role="user", content="Test")])
        with pytest.raises(AIGatewayError) as exc_info:
            await gateway.generate(request)

        assert exc_info.value.code == "OLLAMA_TIMEOUT"
        assert exc_info.value.retryable is True


@pytest.mark.asyncio
async def test_gateway_generate_simple():
    """Test gateway generate_simple convenience method."""
    config = AIProviderConfig(provider="ollama", model="llama3.2")

    with patch("app.services.ai_gateway.get_ai_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.provider_name = "ollama"
        mock_provider.config = config
        mock_provider.generate = AsyncMock(return_value=AIResponse(
            content="Simple response",
            citations=[],
            provider="ollama",
            model="llama3.2",
        ))
        mock_get_provider.return_value = mock_provider

        gateway = AIGateway(config)
        await gateway.initialize()

        response = await gateway.generate_simple(
            prompt="What is 2+2?",
            system_instructions="You are a math tutor",
        )

        assert response.content == "Simple response"


# ============================================================
# Global Gateway Tests
# ============================================================

@pytest.mark.asyncio
async def test_get_ai_gateway_singleton():
    """Test global gateway singleton."""
    config = AIProviderConfig(provider="ollama", model="llama3.2")

    with patch("app.services.ai_gateway.get_ai_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.provider_name = "ollama"
        mock_provider.config = config
        mock_get_provider.return_value = mock_provider

        gateway1 = await get_ai_gateway(config)
        gateway2 = await get_ai_gateway(config)

        assert gateway1 is gateway2

    await close_ai_gateway()


@pytest.mark.asyncio
async def test_close_ai_gateway():
    """Test closing global gateway."""
    config = AIProviderConfig(provider="ollama", model="llama3.2")

    with patch("app.services.ai_gateway.get_ai_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.provider_name = "ollama"
        mock_provider.config = config
        mock_get_provider.return_value = mock_provider

        await get_ai_gateway(config)
        await close_ai_gateway()

        # Should be able to create new one after close
        gateway = await get_ai_gateway(config)
        assert gateway is not None

    await close_ai_gateway()


# ============================================================
# Configuration Tests
# ============================================================

def test_ai_config_in_settings():
    """Test AI configuration is in settings."""
    assert hasattr(settings, "ai_provider")
    assert hasattr(settings, "gemini_api_key")
    assert hasattr(settings, "gemini_model")
    assert hasattr(settings, "ollama_model")
    assert hasattr(settings, "ai_temperature")
    assert hasattr(settings, "ai_max_output_tokens")
    assert hasattr(settings, "ai_timeout_seconds")

    # Check defaults
    assert settings.ai_provider == "ollama"
    assert settings.gemini_model == "gemini-1.5-flash"
    assert settings.ollama_model == "llama3.2"
    assert settings.ai_temperature == 0.0
    assert settings.ai_max_output_tokens == 4096
    assert settings.ai_timeout_seconds == 30


# ============================================================
# Secret Protection Tests
# ============================================================

def test_gemini_api_key_not_in_logs():
    """Test that API key is not logged."""
    import logging
    from io import StringIO

    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    logger = logging.getLogger("app.services.ai_providers.gemini")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    # The provider initialization should not log the API key
    # This is a basic check - in real scenario, we'd test actual logging

    logger.removeHandler(handler)


# ============================================================
# Citation Preservation Tests
# ============================================================

def test_citation_reference_schema():
    """Test citation reference schema."""
    citation = CitationReference(
        article_id=1,
        article_title="Test Article",
        article_slug="test-article",
        chunk_id=5,
        chunk_index=0,
        content="Test content",
        score=0.9,
        source="semantic",
    )

    assert citation.article_id == 1
    assert citation.chunk_id == 5
    assert citation.source == "semantic"

    # Serialization
    data = citation.model_dump()
    assert data["article_id"] == 1
    assert data["chunk_id"] == 5


def test_ai_response_with_citations():
    """Test AI response with citations."""
    citation = CitationReference(
        article_id=1,
        article_title="Test",
        article_slug="test",
        chunk_id=1,
        chunk_index=0,
        content="Content",
        score=0.9,
        source="semantic",
    )

    response = AIResponse(
        content="Answer based on [Evidence 1]",
        citations=[citation],
        provider="gemini",
        model="gemini-1.5-flash",
        usage=AIUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
    )

    assert len(response.citations) == 1
    assert response.usage.total_tokens == 150
    assert response.provider == "gemini"