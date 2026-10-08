"""Ollama AI Provider Implementation."""

import asyncio
import time
from typing import Optional

from langchain_ollama import ChatOllama
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    AIMessage,
    BaseMessage,
)

from app.schemas.ai_gateway import (
    AIRequest,
    AIResponse,
    AIProviderConfig,
    AIUsage,
)
from app.services.ai_providers.base import AIProvider, AIProviderError


class OllamaProvider(AIProvider):
    """Ollama provider using langchain-ollama."""

    def __init__(self, config: AIProviderConfig):
        super().__init__(config)
        self._llm: Optional[ChatOllama] = None

    @property
    def provider_name(self) -> str:
        return "ollama"

    async def initialize(self) -> None:
        """Initialize the Ollama client."""
        try:
            self._llm = ChatOllama(
                model=self.config.model,
                temperature=self.config.temperature,
                num_predict=self.config.max_output_tokens,
                # Ollama-specific params can be added here
            )
            # Test connection
            await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._llm.invoke([HumanMessage(content="test")]),
                ),
                timeout=5.0,
            )
        except asyncio.TimeoutError:
            raise AIProviderError(
                code="OLLAMA_CONNECTION_TIMEOUT",
                message="Ollama server did not respond in time",
                provider="ollama",
                retryable=True,
            )
        except Exception as e:
            raise AIProviderError(
                code="OLLAMA_INIT_FAILED",
                message=f"Failed to initialize Ollama provider: {str(e)}",
                provider="ollama",
                retryable=False,
                original_exception=e,
            )

    async def close(self) -> None:
        """Clean up resources."""
        self._llm = None

    def _convert_messages(self, messages: list) -> list[BaseMessage]:
        """Convert AIMessage to langchain messages."""
        converted = []
        for msg in messages:
            if msg.role == "system":
                converted.append(SystemMessage(content=msg.content))
            elif msg.role == "user":
                converted.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                converted.append(AIMessage(content=msg.content))
            # Skip tool messages for now
        return converted

    async def generate(self, request: AIRequest) -> AIResponse:
        """Generate response using Ollama."""
        if not self._llm:
            await self.initialize()

        start_time = time.time()

        # Build messages
        system_prompt = self._build_system_prompt(request)
        messages = []

        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))

        # Add conversation messages
        lc_messages = self._convert_messages(request.messages)
        messages.extend(lc_messages)

        try:
            # Run in executor to avoid blocking
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._llm.invoke(messages),
                ),
                timeout=self.config.timeout_seconds,
            )

            elapsed = time.time() - start_time

            # Extract content
            content = response.content if hasattr(response, "content") else str(response)

            # Extract citations if RAG context provided
            citations = self._extract_citations_from_response(content, request.rag_context)

            # Build usage (Ollama doesn't provide token counts by default)
            usage = None
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                usage = AIUsage(
                    prompt_tokens=response.usage_metadata.get("input_tokens"),
                    completion_tokens=response.usage_metadata.get("output_tokens"),
                    total_tokens=response.usage_metadata.get("total_tokens"),
                )

            return AIResponse(
                content=content,
                citations=citations,
                provider="ollama",
                model=self.config.model,
                usage=usage,
                metadata={
                    "elapsed_seconds": elapsed,
                    "temperature": self.config.temperature,
                },
            )

        except asyncio.TimeoutError:
            raise AIProviderError(
                code="OLLAMA_TIMEOUT",
                message=f"Ollama request timed out after {self.config.timeout_seconds}s",
                provider="ollama",
                retryable=True,
            )
        except Exception as e:
            raise AIProviderError(
                code="OLLAMA_GENERATION_FAILED",
                message=f"Ollama generation failed: {str(e)}",
                provider="ollama",
                retryable=False,
                original_exception=e,
            )