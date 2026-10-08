"""Knowledge base retrieval services.

Provides semantic search, keyword search, and hybrid retrieval
with citation-ready result structures.
"""

import math
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeArticle, ArticleStatus, ArticleCategory
from app.models.knowledge_chunk import KnowledgeChunk
from app.services.embeddings import get_embedding_provider
from app.schemas.retrieval import (
    RetrievalResult,
    RetrievalSource,
    CitationReference,
    ContextChunk,
    AIContext,
    RetrievalConfig,
)


# Configuration constants
DEFAULT_MAX_TOP_K = 50
DEFAULT_TOP_K = 5
DEFAULT_SEMANTIC_WEIGHT = 0.5
DEFAULT_KEYWORD_WEIGHT = 0.5
MAX_CONTEXT_CHUNKS = 10
MAX_CONTEXT_CHARS = 8000


@dataclass
class _ScoredChunk:
    """Internal structure for scored chunk during retrieval."""
    chunk: KnowledgeChunk
    article: KnowledgeArticle
    similarity: float
    source: RetrievalSource
    keyword_score: float = 0.0


def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not vec1 or not vec2:
        return 0.0
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def _build_visibility_filter(user_role: str) -> list:
    """Build SQLAlchemy filters for visibility based on user role."""
    filters = [
        KnowledgeArticle.is_deleted == False,
        KnowledgeChunk.embedding.isnot(None),
    ]
    if user_role != "Admin":
        filters.append(KnowledgeArticle.status == ArticleStatus.PUBLISHED)
    return filters


def _build_category_filter(category: Optional[str]) -> list:
    """Build SQLAlchemy filter for category if provided."""
    if category:
        try:
            cat_enum = ArticleCategory(category)
            return [KnowledgeArticle.category == cat_enum]
        except ValueError:
            return []
    return []


def _article_to_result(
    chunk: KnowledgeChunk,
    article: KnowledgeArticle,
    similarity: float,
    source: RetrievalSource,
) -> RetrievalResult:
    """Convert chunk/article pair to RetrievalResult."""
    return RetrievalResult(
        chunk_id=chunk.id,
        article_id=article.id,
        chunk_index=chunk.chunk_index,
        content=chunk.content,
        score=similarity,
        article_title=article.title,
        article_slug=article.slug,
        article_category=article.category.value if hasattr(article.category, 'value') else str(article.category),
        article_status=article.status.value if hasattr(article.status, 'value') else str(article.status),
        source=source,
    )


def search_similar_chunks(
    db: Session,
    query: str,
    top_k: int = DEFAULT_TOP_K,
    user_role: str = "Employee",
    article_ids: Optional[list[int]] = None,
    category: Optional[str] = None,
) -> list[RetrievalResult]:
    """
    Search for chunks similar to the query using vector similarity (in-memory fallback).

    Args:
        db: Database session
        query: Search query text
        top_k: Number of results to return (max 50)
        user_role: Role of the user (for visibility filtering)
        article_ids: Optional list of article IDs to restrict search to
        category: Optional category filter

    Returns:
        List of RetrievalResult objects with citation metadata
    """
    if not query or not query.strip():
        return []

    top_k = max(1, min(top_k, DEFAULT_MAX_TOP_K))

    # Get query embedding
    provider = get_embedding_provider()
    query_embedding = provider.embed_text(query)

    # Build the base query with joins for metadata
    base_query = (
        db.query(KnowledgeChunk, KnowledgeArticle)
        .join(KnowledgeArticle, KnowledgeChunk.article_id == KnowledgeArticle.id)
        .filter(*_build_visibility_filter(user_role))
        .filter(*_build_category_filter(category))
    )

    if article_ids:
        base_query = base_query.filter(KnowledgeArticle.id.in_(article_ids))

    chunks = base_query.all()

    if not chunks:
        return []

    # Compute cosine similarity for each chunk
    scored_chunks: list[_ScoredChunk] = []
    for chunk, article in chunks:
        similarity = _cosine_similarity(query_embedding, chunk.embedding)
        # Clamp to [0, 1] for citation schema validation
        similarity = max(0.0, min(1.0, similarity))
        scored_chunks.append(_ScoredChunk(
            chunk=chunk,
            article=article,
            similarity=similarity,
            source="semantic",
        ))

    # Sort by similarity descending, then by chunk_id for deterministic tie-breaking
    scored_chunks.sort(key=lambda x: (-x.similarity, x.chunk.id))

    # Take top_k
    top_chunks = scored_chunks[:top_k]

    # Convert to results
    return [_article_to_result(sc.chunk, sc.article, sc.similarity, sc.source) for sc in top_chunks]


def search_similar_chunks_pgvector(
    db: Session,
    query: str,
    top_k: int = DEFAULT_TOP_K,
    user_role: str = "Employee",
    article_ids: Optional[list[int]] = None,
    category: Optional[str] = None,
) -> list[RetrievalResult]:
    """
    Search for chunks using pgvector's native similarity search.

    More efficient than in-memory similarity for large datasets.
    Requires pgvector extension and HNSW/IVFFlat index on embedding column.

    Args:
        db: Database session
        query: Search query text
        top_k: Number of results to return (max 50)
        user_role: Role of the user (for visibility filtering)
        article_ids: Optional list of article IDs to restrict search to
        category: Optional category filter

    Returns:
        List of RetrievalResult objects with citation metadata
    """
    if not query or not query.strip():
        return []

    top_k = max(1, min(top_k, DEFAULT_MAX_TOP_K))

    provider = get_embedding_provider()
    query_embedding = provider.embed_text(query)

    # Convert embedding to pgvector format
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    # Build the query using pgvector's <=> operator (cosine distance)
    # 1 - cosine_distance/2 = cosine_similarity normalized to [0, 1]
    base_query = """
        SELECT
            kc.id,
            kc.article_id,
            kc.chunk_index,
            kc.content,
            ka.title,
            ka.category,
            ka.slug,
            ka.status,
            1 - (kc.embedding_vector <=> :query_embedding) / 2 as similarity
        FROM knowledge_chunks kc
        JOIN knowledge_articles ka ON kc.article_id = ka.id
        WHERE ka.is_deleted = false
        AND kc.embedding_vector IS NOT NULL
    """

    params = {"query_embedding": embedding_str, "top_k": top_k}

    # Apply visibility filter
    if user_role != "Admin":
        base_query += " AND ka.status = 'PUBLISHED'"

    # Apply category filter
    if category:
        base_query += " AND ka.category = :category"
        params["category"] = category

    # Apply article IDs filter
    if article_ids:
        placeholders = ",".join([f":id_{i}" for i in range(len(article_ids))])
        base_query += f" AND ka.id IN ({placeholders})"
        for i, aid in enumerate(article_ids):
            params[f"id_{i}"] = aid

    # Order by similarity (cosine distance) and limit
    # Add chunk.id as secondary sort for deterministic tie-breaking
    base_query += " ORDER BY kc.embedding_vector <=> :query_embedding, kc.id LIMIT :top_k"

    result = db.execute(text(base_query), params).fetchall()

    results = []
    for row in result:
        results.append(RetrievalResult(
            chunk_id=row.id,
            article_id=row.article_id,
            chunk_index=row.chunk_index,
            content=row.content,
            score=row.similarity,
            article_title=row.title,
            article_category=row.category,
            article_slug=row.slug,
            article_status=row.status,
            source="semantic",
        ))

    return results


def search_keyword_chunks(
    db: Session,
    query: str,
    top_k: int = DEFAULT_TOP_K,
    user_role: str = "Employee",
    article_ids: Optional[list[int]] = None,
    category: Optional[str] = None,
) -> list[RetrievalResult]:
    """
    Search for chunks using keyword (ILIKE) matching on article title/summary/content.

    Returns the first chunk of each matching article with a keyword-based score.

    Args:
        db: Database session
        query: Search query text
        top_k: Number of results to return
        user_role: Role of the user (for visibility filtering)
        article_ids: Optional list of article IDs to restrict search to
        category: Optional category filter

    Returns:
        List of RetrievalResult objects with citation metadata
    """
    if not query or not query.strip():
        return []

    top_k = max(1, min(top_k, DEFAULT_MAX_TOP_K))

    search_term = f"%{query}%"

    # Find matching articles first
    article_query = (
        db.query(KnowledgeArticle)
        .filter(KnowledgeArticle.is_deleted == False)
        .filter(*_build_visibility_filter(user_role))
        .filter(*_build_category_filter(category))
        .filter(
            or_(
                KnowledgeArticle.title.ilike(search_term),
                KnowledgeArticle.summary.ilike(search_term),
                KnowledgeArticle.content.ilike(search_term),
            )
        )
    )

    if article_ids:
        article_query = article_query.filter(KnowledgeArticle.id.in_(article_ids))

    # Order by title for deterministic results, then limit
    keyword_articles = article_query.order_by(KnowledgeArticle.title).limit(top_k).all()

    if not keyword_articles:
        return []

    # Get the first chunk for each matching article
    article_ids_matched = [a.id for a in keyword_articles]
    chunks = (
        db.query(KnowledgeChunk)
        .filter(KnowledgeChunk.article_id.in_(article_ids_matched))
        .order_by(KnowledgeChunk.article_id, KnowledgeChunk.chunk_index)
        .all()
    )

    # Group chunks by article and take the first (index 0) chunk
    chunks_by_article: dict[int, KnowledgeChunk] = {}
    for chunk in chunks:
        if chunk.article_id not in chunks_by_article:
            chunks_by_article[chunk.article_id] = chunk

    # Build results with keyword-based scoring
    # Score based on where the match occurs (title > summary > content)
    results = []
    for article in keyword_articles:
        chunk = chunks_by_article.get(article.id)
        if not chunk:
            continue

        # Calculate keyword relevance score
        score = 0.0
        query_lower = query.lower()
        if query_lower in article.title.lower():
            score = 1.0
        elif query_lower in article.summary.lower():
            score = 0.7
        elif query_lower in article.content.lower():
            score = 0.5

        results.append(_article_to_result(chunk, article, score, "keyword"))

    return results


def hybrid_search(
    db: Session,
    query: str,
    top_k: int = DEFAULT_TOP_K,
    user_role: str = "Employee",
    keyword_weight: float = DEFAULT_KEYWORD_WEIGHT,
    semantic_weight: float = DEFAULT_SEMANTIC_WEIGHT,
    article_ids: Optional[list[int]] = None,
    category: Optional[str] = None,
) -> list[RetrievalResult]:
    """
    Perform hybrid search combining keyword and semantic similarity.

    Uses Reciprocal Rank Fusion (RRF) for deterministic score fusion.
    Removes duplicate chunks, preserves source information.

    Args:
        db: Database session
        query: Search query text
        top_k: Number of results to return (max 50)
        user_role: User role for visibility filtering
        keyword_weight: Weight for keyword search (0-1)
        semantic_weight: Weight for semantic search (0-1)
        article_ids: Optional list of article IDs to restrict search to
        category: Optional category filter

    Returns:
        Combined and ranked RetrievalResult objects
    """
    if not query or not query.strip():
        return []

    top_k = max(1, min(top_k, DEFAULT_MAX_TOP_K))

    # Normalize weights
    total_weight = keyword_weight + semantic_weight
    if total_weight == 0:
        keyword_weight = DEFAULT_KEYWORD_WEIGHT
        semantic_weight = DEFAULT_SEMANTIC_WEIGHT
    else:
        keyword_weight = keyword_weight / total_weight
        semantic_weight = semantic_weight / total_weight

    # Retrieve from both sources with expanded pools for better fusion
    pool_size = min(top_k * 3, DEFAULT_MAX_TOP_K)

    keyword_results = search_keyword_chunks(
        db=db,
        query=query,
        top_k=pool_size,
        user_role=user_role,
        article_ids=article_ids,
        category=category,
    )

    semantic_results = search_similar_chunks_pgvector(
        db=db,
        query=query,
        top_k=pool_size,
        user_role=user_role,
        article_ids=article_ids,
        category=category,
    )

    # Reciprocal Rank Fusion (RRF) with k=60 (standard value)
    # RRF score = sum(weight / (k + rank))
    # This is deterministic and handles different score scales well
    RRF_K = 60

    # Track results by chunk_id to deduplicate
    chunk_scores: dict[int, dict] = {}

    # Process keyword results
    for rank, result in enumerate(keyword_results, 1):
        rrf_score = keyword_weight / (RRF_K + rank)
        chunk_scores[result.chunk_id] = {
            "result": result,
            "score": rrf_score,
            "sources": {"keyword": rank},
        }

    # Process semantic results
    for rank, result in enumerate(semantic_results, 1):
        rrf_score = semantic_weight / (RRF_K + rank)
        if result.chunk_id in chunk_scores:
            # Merge: add scores, track both sources
            chunk_scores[result.chunk_id]["score"] += rrf_score
            chunk_scores[result.chunk_id]["sources"]["semantic"] = rank
            # Keep the higher individual score for the result
            if result.score > chunk_scores[result.chunk_id]["result"].score:
                chunk_scores[result.chunk_id]["result"] = result
        else:
            chunk_scores[result.chunk_id] = {
                "result": result,
                "score": rrf_score,
                "sources": {"semantic": rank},
            }

    # Sort by combined RRF score descending, then by chunk_id for deterministic tie-breaking
    sorted_chunks = sorted(
        chunk_scores.values(),
        key=lambda x: (-x["score"], x["result"].chunk_id)
    )

    # Build final results with source attribution
    final_results = []
    for item in sorted_chunks[:top_k]:
        result = item["result"]
        sources = item["sources"]

        # Determine primary source
        if "keyword" in sources and "semantic" in sources:
            primary_source: RetrievalSource = "hybrid"
        elif "keyword" in sources:
            primary_source = "keyword"
        else:
            primary_source = "semantic"

        # Create new result with combined score and source
        final_results.append(RetrievalResult(
            chunk_id=result.chunk_id,
            article_id=result.article_id,
            chunk_index=result.chunk_index,
            content=result.content,
            score=item["score"],
            article_title=result.article_title,
            article_slug=result.article_slug,
            article_category=result.article_category,
            article_status=result.article_status,
            source=primary_source,
        ))

    return final_results


def build_context(
    results: list[RetrievalResult],
    query: str,
    max_chunks: int = MAX_CONTEXT_CHUNKS,
    max_chars: int = MAX_CONTEXT_CHARS,
) -> AIContext:
    """
    Build an AI-ready context package from retrieval results.

    Selects evidence chunks up to size limits, preserves citation metadata.

    Args:
        results: Ranked retrieval results
        query: Original query for context
        max_chunks: Maximum number of chunks to include
        max_chars: Maximum total characters in context

    Returns:
        AIContext with selected chunks and citation references
    """
    if not results:
        return AIContext(
            query=query,
            chunks=[],
            total_chunks=0,
            total_chars=0,
            citations=[],
        )

    selected_chunks: list[ContextChunk] = []
    total_chars = 0

    for result in results:
        if len(selected_chunks) >= max_chunks:
            break
        if total_chars + len(result.content) > max_chars:
            # Try to include a truncated version if we have room for at least some content
            remaining = max_chars - total_chars
            if remaining < 100:  # Not worth including a tiny fragment
                break
            # Could truncate here, but better to skip to avoid partial sentences
            break

        context_chunk = ContextChunk(
            chunk_id=result.chunk_id,
            article_id=result.article_id,
            article_title=result.article_title,
            article_slug=result.article_slug,
            chunk_index=result.chunk_index,
            content=result.content,
            score=result.score,
            source=result.source,
        )
        selected_chunks.append(context_chunk)
        total_chars += len(result.content)

    # Build citation references
    citations = [
        CitationReference(
            article_id=c.article_id,
            article_title=c.article_title,
            article_slug=c.article_slug,
            chunk_id=c.chunk_id,
            chunk_index=c.chunk_index,
            content=c.content,
            score=c.score,
            source=c.source,
        )
        for c in selected_chunks
    ]

    return AIContext(
        query=query,
        chunks=selected_chunks,
        total_chunks=len(selected_chunks),
        total_chars=total_chars,
        citations=citations,
    )


def retrieve_and_build_context(
    db: Session,
    query: str,
    top_k: int = DEFAULT_TOP_K,
    user_role: str = "Employee",
    keyword_weight: float = DEFAULT_KEYWORD_WEIGHT,
    semantic_weight: float = DEFAULT_SEMANTIC_WEIGHT,
    article_ids: Optional[list[int]] = None,
    category: Optional[str] = None,
    max_context_chunks: int = MAX_CONTEXT_CHUNKS,
    max_context_chars: int = MAX_CONTEXT_CHARS,
    use_hybrid: bool = True,
) -> AIContext:
    """
    Convenience function: retrieve and build context in one call.

    Args:
        db: Database session
        query: Search query
        top_k: Number of retrieval results
        user_role: User role for visibility
        keyword_weight: Keyword weight for hybrid
        semantic_weight: Semantic weight for hybrid
        article_ids: Optional article ID filter
        category: Optional category filter
        max_context_chunks: Max chunks in context
        max_context_chars: Max chars in context
        use_hybrid: Whether to use hybrid (True) or semantic-only (False)

    Returns:
        AIContext ready for downstream AI consumption
    """
    if use_hybrid:
        results = hybrid_search(
            db=db,
            query=query,
            top_k=top_k,
            user_role=user_role,
            keyword_weight=keyword_weight,
            semantic_weight=semantic_weight,
            article_ids=article_ids,
            category=category,
        )
    else:
        results = search_similar_chunks_pgvector(
            db=db,
            query=query,
            top_k=top_k,
            user_role=user_role,
            article_ids=article_ids,
            category=category,
        )

    return build_context(
        results=results,
        query=query,
        max_chunks=max_context_chunks,
        max_chars=max_context_chars,
    )