"""Pydantic schemas for retrieval results and citations."""

from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


# Source type for retrieval results
RetrievalSource = Literal["semantic", "keyword", "hybrid"]


class RetrievalResult(BaseModel):
    """
    Structured retrieval result with citation metadata.

    This is the primary structure returned by search endpoints and used
    by downstream AI services for citation generation.
    """
    chunk_id: int = Field(..., description="Unique identifier of the knowledge chunk")
    article_id: int = Field(..., description="Identifier of the parent knowledge article")
    chunk_index: int = Field(..., description="Index of this chunk within the article")
    content: str = Field(..., description="The chunk text content")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0-1)")
    article_title: str = Field(..., description="Title of the parent article")
    article_slug: str = Field(..., description="URL-friendly slug of the parent article")
    article_category: str = Field(..., description="Category of the parent article")
    article_status: str = Field(..., description="Status of the parent article (PUBLISHED/DRAFT/ARCHIVED)")
    source: RetrievalSource = Field(..., description="How this result was retrieved")

    model_config = ConfigDict(from_attributes=True)


class CitationReference(BaseModel):
    """
    Stable citation representation for AI responses.

    Contains all information needed for a citation without requiring
    additional database lookups.
    """
    article_id: int
    article_title: str
    article_slug: str
    chunk_id: int
    chunk_index: int
    content: str
    score: float = Field(..., ge=0.0, le=1.0)
    source: RetrievalSource

    model_config = ConfigDict(from_attributes=True)


class RetrievalResponse(BaseModel):
    """Response wrapper for retrieval endpoints."""
    results: list[RetrievalResult]
    total_results: int
    query: str
    top_k: int


class HybridSearchParams(BaseModel):
    """Parameters for hybrid search."""
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=50)
    keyword_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    semantic_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    category: Optional[str] = Field(default=None, description="Optional category filter")


class SemanticSearchParams(BaseModel):
    """Parameters for semantic search."""
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=50)
    category: Optional[str] = Field(default=None, description="Optional category filter")


class RetrievalConfig(BaseModel):
    """Configuration for retrieval behavior."""
    max_top_k: int = 50
    default_top_k: int = 5
    default_semantic_weight: float = 0.5
    default_keyword_weight: float = 0.5
    max_context_chunks: int = 10
    max_context_chars: int = 8000


class ContextChunk(BaseModel):
    """A chunk selected for AI context with citation metadata."""
    chunk_id: int
    article_id: int
    article_title: str
    article_slug: str
    chunk_index: int
    content: str
    score: float
    source: RetrievalSource


class AIContext(BaseModel):
    """AI-ready context package with citations."""
    query: str
    chunks: list[ContextChunk]
    total_chunks: int
    total_chars: int
    citations: list[CitationReference]

    model_config = ConfigDict(from_attributes=True)