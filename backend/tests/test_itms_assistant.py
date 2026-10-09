"""Tests for ITMS AI Assistant Service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.orm import Session

from app.services.itms_assistant import (
    ITMSAssistant,
    ask_assistant,
    AssistantResponse,
    InsufficientEvidenceError,
)
from app.schemas.ai_gateway import (
    AIResponse,
    CitationReference,
    AIUsage,
)
from app.schemas.retrieval import ContextChunk, AIContext
from app.services.ai_gateway import AIGatewayError


class TestITMSAssistant:
    """Tests for ITMSAssistant class."""

    @pytest.fixture
    def mock_db(self):
        return MagicMock(spec=Session)

    @pytest.fixture
    def assistant(self, mock_db):
        return ITMSAssistant(db=mock_db)

    @pytest.fixture
    def mock_ai_context(self):
        """Create a mock AIContext with citations."""
        from app.schemas.retrieval import AIContext
        return AIContext(
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

    @pytest.mark.asyncio
    async def test_ask_empty_question_raises(self, assistant):
        """Test that empty question raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            await assistant.ask("")

        with pytest.raises(ValueError, match="cannot be empty"):
            await assistant.ask("   ")

    @pytest.mark.asyncio
    async def test_ask_oversized_question_raises(self, assistant):
        """Test that oversized question raises ValueError."""
        long_question = "a" * 2001
        with pytest.raises(ValueError, match="exceeds maximum length"):
            await assistant.ask(long_question)

    @pytest.mark.asyncio
    async def test_ask_success_with_evidence(self, assistant, mock_ai_context):
        """Test successful question answering with evidence."""
        with patch("app.services.itms_assistant.retrieve_and_build_context") as mock_retrieve:
            mock_retrieve.return_value = mock_ai_context

            with patch("app.services.itms_assistant.get_ai_gateway") as mock_get_gateway:
                mock_gateway = AsyncMock()
                mock_gateway.generate = AsyncMock(return_value=AIResponse(
                    content="To reset your password, click Forgot Password on the login page. [Evidence 1]",
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
                    ],
                    provider="ollama",
                    model="llama3.2",
                    usage=AIUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
                    metadata={"elapsed_seconds": 1.5},
                ))
                mock_get_gateway.return_value = mock_gateway

                response = await assistant.ask("How do I reset my password?")

                assert response.answer == "To reset your password, click Forgot Password on the login page. [Evidence 1]"
                assert response.evidence_found is True
                assert response.grounded is True
                assert response.provider == "ollama"
                assert response.model == "llama3.2"
                assert len(response.citations) == 1
                assert response.citations[0].chunk_id == 1
                mock_retrieve.assert_called_once()

    @pytest.mark.asyncio
    async def test_ask_no_evidence_found(self, assistant):
        """Test handling when no evidence is found."""
        from app.schemas.retrieval import AIContext
        empty_context = AIContext(
            query="unknown question",
            chunks=[],
            total_chunks=0,
            total_chars=0,
            citations=[],
        )

        with patch("app.services.itms_assistant.retrieve_and_build_context") as mock_retrieve:
            mock_retrieve.return_value = empty_context

            response = await assistant.ask("Unknown question?")

            assert response.evidence_found is False
            assert response.grounded is False
            assert "couldn't find sufficient information" in response.answer.lower()
            assert len(response.citations) == 0

    @pytest.mark.asyncio
    async def test_ask_retrieval_failure(self, assistant):
        """Test handling of retrieval failure."""
        with patch("app.services.itms_assistant.retrieve_and_build_context") as mock_retrieve:
            mock_retrieve.side_effect = Exception("Database error")

            with pytest.raises(AIGatewayError) as exc_info:
                await assistant.ask("How do I reset?")

            assert exc_info.value.code == "RETRIEVAL_FAILED"
            assert exc_info.value.retryable is True

    @pytest.mark.asyncio
    async def test_ask_gateway_error_propagates(self, assistant, mock_ai_context):
        """Test that gateway errors are propagated."""
        with patch("app.services.itms_assistant.retrieve_and_build_context") as mock_retrieve:
            mock_retrieve.return_value = mock_ai_context

            with patch("app.services.itms_assistant.get_ai_gateway") as mock_get_gateway:
                mock_gateway = AsyncMock()
                mock_gateway.generate = AsyncMock(side_effect=AIGatewayError(
                    code="OLLAMA_TIMEOUT",
                    message="Timeout",
                    provider="ollama",
                    retryable=True,
                ))
                mock_get_gateway.return_value = mock_gateway

                with pytest.raises(AIGatewayError) as exc_info:
                    await assistant.ask("How do I reset?")

                assert exc_info.value.code == "OLLAMA_TIMEOUT"
                assert exc_info.value.retryable is True

    @pytest.mark.asyncio
    async def test_validate_citations_filters_fabricated(self, assistant, mock_ai_context):
        """Test that fabricated citations are filtered out."""
        with patch("app.services.itms_assistant.retrieve_and_build_context") as mock_retrieve:
            mock_retrieve.return_value = mock_ai_context

            with patch("app.services.itms_assistant.get_ai_gateway") as mock_get_gateway:
                mock_gateway = AsyncMock()
                # Response includes a fabricated citation (chunk_id=999)
                mock_gateway.generate = AsyncMock(return_value=AIResponse(
                    content="Answer with fabricated citation [Evidence 3]",
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
                            article_id=999,
                            article_title="Fake Article",
                            article_slug="fake-article",
                            chunk_id=999,
                            chunk_index=0,
                            content="Fake content",
                            score=0.5,
                            source="semantic",
                        ),
                    ],
                    provider="ollama",
                    model="llama3.2",
                ))
                mock_get_gateway.return_value = mock_gateway

                response = await assistant.ask("How do I reset?")

                # Should only have the valid citation
                assert len(response.citations) == 1
                assert response.citations[0].chunk_id == 1

    @pytest.mark.asyncio
    async def test_validate_citations_article_id_mismatch(self, assistant, mock_ai_context):
        """Test that citation with mismatched article_id is rejected."""
        with patch("app.services.itms_assistant.retrieve_and_build_context") as mock_retrieve:
            mock_retrieve.return_value = mock_ai_context

            with patch("app.services.itms_assistant.get_ai_gateway") as mock_get_gateway:
                mock_gateway = AsyncMock()
                # Response includes citation with correct chunk_id but wrong article_id
                mock_gateway.generate = AsyncMock(return_value=AIResponse(
                    content="Answer with mismatched citation",
                    citations=[
                        CitationReference(
                            article_id=999,  # Wrong article_id
                            article_title="Password Reset Guide",
                            article_slug="password-reset-guide",
                            chunk_id=1,
                            chunk_index=0,
                            content="To reset your password...",
                            score=0.95,
                            source="semantic",
                        ),
                    ],
                    provider="ollama",
                    model="llama3.2",
                ))
                mock_get_gateway.return_value = mock_gateway

                response = await assistant.ask("How do I reset?")

                # Should reject the mismatched citation
                assert len(response.citations) == 0

    @pytest.mark.asyncio
    async def test_ask_deduplicates_citations(self, assistant, mock_ai_context):
        """Test that duplicate citations are deduplicated."""
        with patch("app.services.itms_assistant.retrieve_and_build_context") as mock_retrieve:
            mock_retrieve.return_value = mock_ai_context

            with patch("app.services.itms_assistant.get_ai_gateway") as mock_get_gateway:
                mock_gateway = AsyncMock()
                # Response includes duplicate citation
                mock_gateway.generate = AsyncMock(return_value=AIResponse(
                    content="Answer with duplicate [Evidence 1] [Evidence 1]",
                    citations=[
                        CitationReference(
                            article_id=10,
                            article_title="Password Reset Guide",
                            article_slug="password-reset-guide",
                            chunk_id=1,
                            chunk_index=0,
                            content="To reset your password...",
                            score=0.95,
                            source="semantic",
                        ),
                        CitationReference(
                            article_id=10,
                            article_title="Password Reset Guide",
                            article_slug="password-reset-guide",
                            chunk_id=1,
                            chunk_index=0,
                            content="To reset your password...",
                            score=0.95,
                            source="semantic",
                        ),
                    ],
                    provider="ollama",
                    model="llama3.2",
                ))
                mock_get_gateway.return_value = mock_gateway

                response = await assistant.ask("How do I reset?")

                # Should deduplicate
                assert len(response.citations) == 1

    @pytest.mark.asyncio
    async def test_ask_low_score_evidence_filtered(self, assistant):
        """Test that low-score evidence is filtered out."""
        from app.schemas.retrieval import AIContext
        low_score_context = AIContext(
            query="question",
            chunks=[
                ContextChunk(
                    chunk_id=1,
                    article_id=10,
                    article_title="Article",
                    article_slug="article",
                    chunk_index=0,
                    content="Low relevance content",
                    score=0.05,  # Below default min_evidence_score of 0.1
                    source="semantic",
                ),
            ],
            total_chunks=1,
            total_chars=20,
            citations=[
                CitationReference(
                    article_id=10,
                    article_title="Article",
                    article_slug="article",
                    chunk_id=1,
                    chunk_index=0,
                    content="Low relevance content",
                    score=0.05,
                    source="semantic",
                ),
            ],
        )

        with patch("app.services.itms_assistant.retrieve_and_build_context") as mock_retrieve:
            mock_retrieve.return_value = low_score_context

            response = await assistant.ask("Question?")

            # Should treat as no evidence found
            assert response.evidence_found is False
            assert response.grounded is False


class TestAskAssistantConvenience:
    """Tests for the ask_assistant convenience function."""

    @pytest.fixture
    def mock_db(self):
        return MagicMock(spec=Session)

    @pytest.mark.asyncio
    async def test_ask_assistant_calls_service(self, mock_db):
        """Test that convenience function calls the service."""
        with patch("app.services.itms_assistant.ITMSAssistant") as mock_assistant_class:
            mock_assistant = AsyncMock()
            mock_assistant.ask = AsyncMock(return_value=AssistantResponse(
                answer="Test answer",
                citations=[],
                evidence_found=True,
                grounded=True,
                provider="ollama",
                model="llama3.2",
            ))
            mock_assistant_class.return_value = mock_assistant

            response = await ask_assistant(
                db=mock_db,
                question="Test question",
                user_role="Employee",
            )

            assert response.answer == "Test answer"
            mock_assistant.ask.assert_called_once_with(
                question="Test question",
                user_role="Employee",
                provider_override=None,
            )


class TestAssistantResponse:
    """Tests for AssistantResponse dataclass."""

    def test_to_dict(self):
        """Test serialization to dict."""
        citation = CitationReference(
            article_id=10,
            article_title="Test Article",
            article_slug="test-article",
            chunk_id=1,
            chunk_index=0,
            content="Test content",
            score=0.9,
            source="semantic",
        )

        response = AssistantResponse(
            answer="Test answer",
            citations=[citation],
            evidence_found=True,
            grounded=True,
            provider="ollama",
            model="llama3.2",
            usage={"prompt_tokens": 100, "completion_tokens": 50},
            metadata={"elapsed": 1.0},
        )

        data = response.to_dict()

        assert data["answer"] == "Test answer"
        assert len(data["citations"]) == 1
        assert data["citations"][0]["article_id"] == 10
        assert data["evidence_found"] is True
        assert data["grounded"] is True
        assert data["provider"] == "ollama"
        assert data["model"] == "llama3.2"
        assert data["usage"]["prompt_tokens"] == 100
        assert data["metadata"]["elapsed"] == 1.0