"""Gemini AI Provider Implementation using Google GenAI SDK."""

import asyncio
import os
import time
from typing import Optional

from google import genai
from google.genai import types

from app.schemas.ai_gateway import (
    AIRequest,
    AIResponse,
    AIProviderConfig,
    AIUsage,
)
from app.services.ai_providers.base import AIProvider, AIProviderError


class GeminiProvider(AIProvider):
    """Gemini provider using Google GenAI SDK."""

    def __init__(self, config: AIProviderConfig):
        super().__init__(config)
        self._client: Optional[genai.Client] = None

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def initialize(self) -> None:
        """Initialize the Gemini client."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise AIProviderError(
                code="GEMINI_API_KEY_MISSING",
                message="GEMINI_API_KEY environment variable is not set",
                provider="gemini",
                retryable=False,
            )

        try:
            self._client = genai.Client(api_key=api_key)
            # Test with a minimal request
            await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._client.models.generate_content(
                        model=self.config.model,
                        contents="test",
                        config=types.GenerateContentConfig(
                            max_output_tokens=10,
                            temperature=0,
                        ),
                    ),
                ),
                timeout=10.0,
            )
        except asyncio.TimeoutError:
            raise AIProviderError(
                code="GEMINI_CONNECTION_TIMEOUT",
                message="Gemini API did not respond in time",
                provider="gemini",
                retryable=True,
            )
        except Exception as e:
            # Check if it's an auth error
            error_msg = str(e).lower()
            if "api_key" in error_msg or "authentication" in error_msg or "unauthorized" in error_msg:
                raise AIProviderError(
                    code="GEMINI_AUTH_FAILED",
                    message="Invalid or missing Gemini API key",
                    provider="gemini",
                    retryable=False,
                    original_exception=e,
                )
            raise AIProviderError(
                code="GEMINI_INIT_FAILED",
                message=f"Failed to initialize Gemini provider: {str(e)}",
                provider="gemini",
                retryable=False,
                original_exception=e,
            )

    async def close(self) -> None:
        """Clean up resources."""
        self._client = None

    def _convert_messages(self, messages: list) -> list[types.Content]:
        """Convert AIMessage to Gemini Content format."""
        contents = []
        for msg in messages:
            role = "user" if msg.role in ("user", "system") else "model"
            # System messages go as user messages with a prefix
            content = msg.content
            if msg.role == "system":
                content = f"[System Instructions]\n{content}"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=content)],
                )
            )
        return contents

    async def generate(self, request: AIRequest) -> AIResponse:
        """Generate response using Gemini."""
        if not self._client:
            await self.initialize()

        start_time = time.time()

        # Build system prompt
        system_prompt = self._build_system_prompt(request)

        # Prepare contents
        contents = self._convert_messages(request.messages)

        # Add system prompt as first user message if present
        if system_prompt:
            # Prepend system to first user message or add as separate
            if contents and contents[0].role == "user":
                contents[0].parts[0].text = f"{system_prompt}\n\n{contents[0].parts[0].text}"
            else:
                contents.insert(0, types.Content(
                    role="user",
                    parts=[types.Part(text=system_prompt)],
                ))

        # Build generation config
        gen_config = types.GenerateContentConfig(
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_output_tokens,
        )

        try:
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._client.models.generate_content(
                        model=self.config.model,
                        contents=contents,
                        config=gen_config,
                    ),
                ),
                timeout=self.config.timeout_seconds,
            )

            elapsed = time.time() - start_time

            # Extract content
            content = response.text if response.text else ""

            # Extract citations if RAG context provided
            citations = self._extract_citations_from_response(content, request.rag_context)

            # Build usage
            usage = None
            if response.usage_metadata:
                usage = AIUsage(
                    prompt_tokens=response.usage_metadata.prompt_token_count,
                    completion_tokens=response.usage_metadata.candidates_token_count,
                    total_tokens=response.usage_metadata.total_token_count,
                )

            return AIResponse(
                content=content,
                citations=citations,
                provider="gemini",
                model=self.config.model,
                usage=usage,
                metadata={
                    "elapsed_seconds": elapsed,
                    "temperature": self.config.temperature,
                    "finish_reason": str(response.candidates[0].finish_reason) if response.candidates else None,
                },
            )

        except asyncio.TimeoutError:
            raise AIProviderError(
                code="GEMINI_TIMEOUT",
                message=f"Gemini request timed out after {self.config.timeout_seconds}s",
                provider="gemini",
                retryable=True,
            )
        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "rate limit" in error_msg or "429" in error_msg:
                raise AIProviderError(
                    code="GEMINI_RATE_LIMIT",
                    message=f"Gemini rate limit exceeded: {str(e)}",
                    provider="gemini",
                    retryable=True,
                    original_exception=e,
                )
            if "api_key" in error_msg or "authentication" in error_msg or "unauthorized" in error_msg:
                raise AIProviderError(
                    code="GEMINI_AUTH_FAILED",
                    message="Invalid or missing Gemini API key",
                    provider="gemini",
                    retryable=False,
                    original_exception=e,
                )
            raise AIProviderError(
                code="GEMINI_GENERATION_FAILED",
                message=f"Gemini generation failed: {str(e)}",
                provider="gemini",
                retryable=False,
                original_exception=e,
            )