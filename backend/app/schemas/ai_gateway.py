"""AI Gateway schemas for provider-agnostic AI operations."""

from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


# AI Provider type
AIProvider = Literal["gemini", "ollama"]


class AIMessage(BaseModel):
    """A single message in the conversation."""
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    tool_calls: Optional[list] = None
    tool_call_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AIRequest(BaseModel):
    """Request to the AI Gateway."""
    messages: list[AIMessage] = Field(..., min_length=1, description="Conversation messages")
    system_instructions: Optional[str] = Field(default=None, description="Optional system prompt")
    rag_context: Optional["RAGContext"] = Field(default=None, description="Optional RAG context with citations")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0, description="Sampling temperature")
    max_output_tokens: Optional[int] = Field(default=None, ge=1, le=8192, description="Max tokens in response")
    provider: Optional[AIProvider] = Field(default=None, description="Override provider selection")

    model_config = ConfigDict(from_attributes=True)


class RAGContext(BaseModel):
    """RAG context package from retrieval service."""
    query: str
    chunks: list["ContextChunk"]
    total_chunks: int
    total_chars: int
    citations: list["CitationReference"]

    model_config = ConfigDict(from_attributes=True)


class ContextChunk(BaseModel):
    """A chunk selected for AI context."""
    chunk_id: int
    article_id: int
    article_title: str
    article_slug: str
    chunk_index: int
    content: str
    score: float
    source: str  # semantic | keyword | hybrid

    model_config = ConfigDict(from_attributes=True)


class CitationReference(BaseModel):
    """Stable citation reference for AI responses."""
    article_id: int
    article_title: str
    article_slug: str
    chunk_id: int
    chunk_index: int
    content: str
    score: float
    source: str

    model_config = ConfigDict(from_attributes=True)


class AIResponse(BaseModel):
    """Normalized AI response from any provider."""
    content: str = Field(..., description="The generated response text")
    citations: list[CitationReference] = Field(default_factory=list, description="Citations used in response")
    provider: AIProvider = Field(..., description="Provider that generated the response")
    model: str = Field(..., description="Model name used")
    usage: Optional["AIUsage"] = Field(default=None, description="Token usage if available")
    metadata: dict = Field(default_factory=dict, description="Provider-specific metadata")

    model_config = ConfigDict(from_attributes=True)


class AIUsage(BaseModel):
    """Token usage information."""
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class AIError(BaseModel):
    """Normalized AI error."""
    code: str
    message: str
    provider: Optional[AIProvider] = None
    retryable: bool = False


class AIProviderConfig(BaseModel):
    """Configuration for an AI provider."""
    provider: AIProvider
    model: str
    temperature: float = 0.0
    max_output_tokens: int = 4096
    timeout_seconds: int = 30
    extra_params: dict = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)