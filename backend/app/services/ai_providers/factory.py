"""AI Provider Factory and Registry."""

from typing import Optional

from app.config import settings
from app.schemas.ai_gateway import AIProviderConfig
from app.services.ai_providers.base import AIProvider as AIProviderBase, AIProviderError
from app.services.ai_providers.gemini import GeminiProvider
from app.services.ai_providers.ollama import OllamaProvider


# Global provider instance cache
_provider_instance: Optional[AIProviderBase] = None
_current_provider_name: Optional[str] = None


def get_provider_config() -> AIProviderConfig:
    """Build provider configuration from settings."""
    provider_name = getattr(settings, "ai_provider", "ollama").lower()

    if provider_name == "gemini":
        model = getattr(settings, "gemini_model", "gemini-1.5-flash")
        api_key = getattr(settings, "gemini_api_key", None)
        if not api_key:
            raise AIProviderError(
                code="GEMINI_API_KEY_MISSING",
                message="GEMINI_API_KEY not configured in settings",
                provider="gemini",
                retryable=False,
            )
        return AIProviderConfig(
            provider="gemini",
            model=model,
            temperature=getattr(settings, "ai_temperature", 0.0),
            max_output_tokens=getattr(settings, "ai_max_output_tokens", 4096),
            timeout_seconds=getattr(settings, "ai_timeout_seconds", 30),
        )
    else:
        return AIProviderConfig(
            provider="ollama",
            model=getattr(settings, "ollama_model", "llama3.2"),
            temperature=getattr(settings, "ai_temperature", 0.0),
            max_output_tokens=getattr(settings, "ai_max_output_tokens", 4096),
            timeout_seconds=getattr(settings, "ai_timeout_seconds", 30),
        )


def create_provider(config: Optional[AIProviderConfig] = None) -> AIProviderBase:
    """Create a new provider instance based on configuration."""
    if config is None:
        config = get_provider_config()

    if config.provider == "gemini":
        return GeminiProvider(config)
    elif config.provider == "ollama":
        return OllamaProvider(config)
    else:
        raise AIProviderError(
            code="UNKNOWN_PROVIDER",
            message=f"Unknown AI provider: {config.provider}",
            provider=None,
            retryable=False,
        )


async def get_ai_provider(config: Optional[AIProviderConfig] = None) -> AIProviderBase:
    """Get or create the AI provider singleton."""
    global _provider_instance, _current_provider_name

    if config is None:
        config = get_provider_config()

    # Check if we need to recreate the provider
    if _provider_instance is None or _current_provider_name != config.provider:
        # Close existing provider if any
        if _provider_instance is not None:
            await _provider_instance.close()

        _provider_instance = create_provider(config)
        _current_provider_name = config.provider
        await _provider_instance.initialize()

    return _provider_instance


async def close_ai_provider() -> None:
    """Close the AI provider singleton."""
    global _provider_instance, _current_provider_name
    if _provider_instance is not None:
        await _provider_instance.close()
        _provider_instance = None
        _current_provider_name = None


def get_available_providers() -> list[str]:
    """Get list of available provider names."""
    return ["gemini", "ollama"]