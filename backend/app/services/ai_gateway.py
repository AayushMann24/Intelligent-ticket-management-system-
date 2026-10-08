"""AI Gateway Service.

Single entry point for all AI operations in ITMS.
Handles provider selection, request validation, and normalized responses.
"""

import logging
from typing import Optional

from app.schemas.ai_gateway import (
    AIRequest,
    AIResponse,
    AIProviderConfig,
    AIProvider,
    AIError,
)
from app.services.ai_providers.factory import (
    get_ai_provider,
    get_provider_config,
    close_ai_provider,
)
from app.services.ai_providers.base import AIProviderError

logger = logging.getLogger(__name__)


class AIGatewayError(Exception):
    """AI Gateway error with normalized code."""

    def __init__(
        self,
        code: str,
        message: str,
        provider: Optional[str] = None,
        retryable: bool = False,
    ):
        self.code = code
        self.message = message
        self.provider = provider
        self.retryable = retryable
        super().__init__(f"[{code}] {message}")

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "provider": self.provider,
            "retryable": self.retryable,
        }


class AIGateway:
    """
    AI Gateway - Central service for all AI operations.

    Responsibilities:
    - Provider selection and lifecycle management
    - Request validation
    - Calling the selected provider
    - Normalized response handling
    - Error normalization
    - Logging (without secrets)
    """

    def __init__(self, config: Optional[AIProviderConfig] = None):
        self._config = config
        self._provider = None

    async def initialize(self) -> None:
        """Initialize the gateway and provider."""
        self._provider = await get_ai_provider(self._config)
        logger.info(
            "AI Gateway initialized",
            extra={"provider": self._provider.provider_name, "model": self._config.model if self._config else "default"},
        )

    async def close(self) -> None:
        """Close the gateway and provider."""
        await close_ai_provider()
        self._provider = None
        logger.info("AI Gateway closed")

    def _validate_request(self, request: AIRequest) -> None:
        """Validate the AI request."""
        if not request.messages:
            raise AIGatewayError(
                code="INVALID_REQUEST",
                message="At least one message is required",
                retryable=False,
            )

        # Ensure last message is from user (for chat)
        last_msg = request.messages[-1]
        if last_msg.role != "user":
            raise AIGatewayError(
                code="INVALID_REQUEST",
                message="Last message must be from user",
                retryable=False,
            )

        # Check for sensitive data patterns (basic)
        for msg in request.messages:
            if self._contains_sensitive_data(msg.content):
                logger.warning(
                    "Request may contain sensitive data",
                    extra={"message_role": msg.role, "content_length": len(msg.content)},
                )

    def _contains_sensitive_data(self, text: str) -> bool:
        """Basic check for potentially sensitive data in text."""
        import re
        # Check for patterns that might be sensitive
        patterns = [
            r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",  # Credit card
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
            r"\b(?:\d{1,3}\.){3}\d{1,3}\b",  # IP address
        ]
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False

    async def generate(self, request: AIRequest) -> AIResponse:
        """
        Generate an AI response.

        Args:
            request: Validated AI request with messages and optional RAG context

        Returns:
            Normalized AI response with citations

        Raises:
            AIGatewayError: On validation or provider errors
        """
        # Validate request
        self._validate_request(request)

        # Get provider
        if self._provider is None:
            await self.initialize()

        # Override provider if specified in request
        if request.provider and request.provider != self._provider.provider_name:
            # Create temporary provider for this request
            config = AIProviderConfig(
                provider=request.provider,
                model="gemini-1.5-flash" if request.provider == "gemini" else "llama3.2",
                temperature=request.temperature or 0.0,
                max_output_tokens=request.max_output_tokens or 4096,
            )
            temp_provider = await get_ai_provider(config)
            provider = temp_provider
        else:
            provider = self._provider

        # Log request (without sensitive content)
        logger.info(
            "AI Gateway generate request",
            extra={
                "provider": provider.provider_name,
                "model": provider.config.model,
                "message_count": len(request.messages),
                "has_rag_context": request.rag_context is not None,
                "rag_chunks": request.rag_context.total_chunks if request.rag_context else 0,
                "temperature": request.temperature,
                "max_tokens": request.max_output_tokens,
            },
        )

        try:
            # Call provider
            response = await provider.generate(request)

            logger.info(
                "AI Gateway generate success",
                extra={
                    "provider": response.provider,
                    "model": response.model,
                    "response_length": len(response.content),
                    "citation_count": len(response.citations),
                    "elapsed_seconds": response.metadata.get("elapsed_seconds", 0),
                },
            )

            return response

        except AIProviderError as e:
            logger.error(
                "AI Gateway provider error",
                extra={
                    "error_code": e.code,
                    "error_message": e.message,
                    "provider": e.provider,
                    "retryable": e.retryable,
                },
            )
            raise AIGatewayError(
                code=e.code,
                message=e.message,
                provider=e.provider,
                retryable=e.retryable,
            )
        except Exception as e:
            logger.exception(
                "AI Gateway unexpected error",
                extra={"error_type": type(e).__name__},
            )
            raise AIGatewayError(
                code="GATEWAY_INTERNAL_ERROR",
                message="An unexpected error occurred in the AI Gateway",
                provider=self._provider.provider_name if self._provider else None,
                retryable=False,
            )

    async def generate_simple(
        self,
        prompt: str,
        system_instructions: Optional[str] = None,
        rag_context: Optional = None,
        provider: Optional[AIProvider] = None,
    ) -> AIResponse:
        """
        Convenience method for simple generation.

        Args:
            prompt: User prompt
            system_instructions: Optional system instructions
            rag_context: Optional RAG context from retrieval
            provider: Optional provider override

        Returns:
            AI response
        """
        from app.schemas.ai_gateway import AIMessage

        request = AIRequest(
            messages=[AIMessage(role="user", content=prompt)],
            system_instructions=system_instructions,
            rag_context=rag_context,
            provider=provider,
        )
        return await self.generate(request)


# Global gateway instance
_gateway_instance: Optional[AIGateway] = None


async def get_ai_gateway(config: Optional[AIProviderConfig] = None) -> AIGateway:
    """Get or create the AI Gateway singleton."""
    global _gateway_instance
    if _gateway_instance is None:
        _gateway_instance = AIGateway(config)
        await _gateway_instance.initialize()
    return _gateway_instance


async def close_ai_gateway() -> None:
    """Close the AI Gateway singleton."""
    global _gateway_instance
    if _gateway_instance is not None:
        await _gateway_instance.close()
        _gateway_instance = None