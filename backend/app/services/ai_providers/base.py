"""AI Provider Abstraction.

Defines the interface that all AI providers must implement.
"""

from abc import ABC, abstractmethod
from typing import Optional

from app.schemas.ai_gateway import (
    AIRequest,
    AIResponse,
    AIProviderConfig,
    AIError,
    AIUsage,
)


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, config: AIProviderConfig):
        self.config = config
        self._client = None

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider identifier."""
        pass

    @abstractmethod
    async def generate(self, request: AIRequest) -> AIResponse:
        """
        Generate a response from the AI provider.

        Args:
            request: The AI request with messages and optional RAG context

        Returns:
            Normalized AI response

        Raises:
            AIProviderError: On provider-specific errors
        """
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider (e.g., create client, validate config)."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Clean up resources (e.g., close connections)."""
        pass

    def _build_system_prompt(self, request: AIRequest) -> str:
        """Build the system prompt from request."""
        parts = []

        if request.system_instructions:
            parts.append(request.system_instructions)

        if request.rag_context:
            parts.append(self._format_rag_context(request.rag_context))

        return "\n\n".join(parts) if parts else ""

    def _format_rag_context(self, rag_context) -> str:
        """Format RAG context for the LLM."""
        if not rag_context or not rag_context.chunks:
            return ""

        parts = ["=== RETRIEVED KNOWLEDGE BASE EVIDENCE ==="]
        parts.append(f"Query: {rag_context.query}")
        parts.append(f"Total evidence chunks: {rag_context.total_chunks}")
        parts.append("")

        for i, chunk in enumerate(rag_context.chunks, 1):
            parts.append(f"--- Evidence {i} ---")
            parts.append(f"Article: {chunk.article_title} ({chunk.article_slug})")
            parts.append(f"Chunk #{chunk.chunk_index}, Score: {chunk.score:.3f}, Source: {chunk.source}")
            parts.append(f"Content: {chunk.content}")
            parts.append("")

        parts.append("=== INSTRUCTIONS ===")
        parts.append("Ground your answer in the evidence above. Cite sources using [Evidence N] format.")
        parts.append("If evidence is insufficient, say so explicitly.")
        parts.append("Do not fabricate information not present in the evidence.")

        return "\n".join(parts)

    def _extract_citations_from_response(
        self,
        response_text: str,
        rag_context
    ) -> list:
        """Extract citations from response text based on [Evidence N] references."""
        if not rag_context or not rag_context.citations:
            return []

        import re
        # Find all [Evidence N] references
        pattern = r"\[Evidence\s+(\d+)\]"
        matches = re.findall(pattern, response_text)

        citations = []
        for match in matches:
            try:
                idx = int(match) - 1
                if 0 <= idx < len(rag_context.citations):
                    citations.append(rag_context.citations[idx])
            except (ValueError, IndexError):
                continue

        # Deduplicate by chunk_id
        seen = set()
        unique_citations = []
        for c in citations:
            if c.chunk_id not in seen:
                seen.add(c.chunk_id)
                unique_citations.append(c)

        return unique_citations


class AIProviderError(Exception):
    """Normalized AI provider error."""

    def __init__(
        self,
        code: str,
        message: str,
        provider: Optional[str] = None,
        retryable: bool = False,
        original_exception: Optional[Exception] = None,
    ):
        self.code = code
        self.message = message
        self.provider = provider
        self.retryable = retryable
        self.original_exception = original_exception
        super().__init__(f"[{code}] {message}")

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "provider": self.provider,
            "retryable": self.retryable,
        }