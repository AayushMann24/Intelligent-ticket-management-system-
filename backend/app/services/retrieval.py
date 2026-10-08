from typing import List, Optional
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge import KnowledgeArticle, ArticleStatus
from app.services.embeddings import get_embedding_provider


@dataclass
class RetrievalResult:
    """Represents a retrieval result with metadata."""
    chunk_id: int
    article_id: int
    chunk_index: int
    content: str
    similarity: float
    article_title: str
    article_category: str
    article_slug: str
    article_status: str


def search_similar_chunks(
    db: Session,
    query: str,
    top_k: int = 5,
    user_role: str = "Employee",
    article_ids: Optional[List[int]] = None,
) -> List[RetrievalResult]:
    """
    Search for chunks similar to the query using vector similarity.

    Args:
        db: Database session
        query: Search query text
        top_k: Number of results to return
        user_role: Role of the user (for visibility filtering)
        article_ids: Optional list of article IDs to restrict search to

    Returns:
        List of RetrievalResult objects
    """
    if not query or not query.strip():
        return []

    if top_k <= 0:
        top_k = 5
    if top_k > 50:
        top_k = 50

    # Get query embedding
    provider = get_embedding_provider()
    query_embedding = provider.embed_text(query)

    # Build the base query
    # We need to join with KnowledgeArticle to filter by status and get metadata
    base_query = (
        db.query(
            KnowledgeChunk.id,
            KnowledgeChunk.article_id,
            KnowledgeChunk.chunk_index,
            KnowledgeChunk.content,
            KnowledgeChunk.embedding,
            KnowledgeArticle.title,
            KnowledgeArticle.category,
            KnowledgeArticle.slug,
            KnowledgeArticle.status,
        )
        .join(KnowledgeArticle, KnowledgeChunk.article_id == KnowledgeArticle.id)
        .filter(KnowledgeArticle.is_deleted == False)
        .filter(KnowledgeChunk.embedding.isnot(None))
    )

    # Apply visibility filtering based on user role
    if user_role == "Admin":
        # Admin can see all articles including drafts
        pass
    else:
        # Employee/Technician only see published articles
        base_query = base_query.filter(KnowledgeArticle.status == ArticleStatus.PUBLISHED)

    # Apply article ID filter if provided
    if article_ids:
        base_query = base_query.filter(KnowledgeArticle.id.in_(article_ids))

    # Get all matching chunks (we'll do similarity scoring in Python)
    # For large datasets, this should be done with pgvector's built-in similarity
    # but for now we do it in Python for correctness
    chunks = base_query.all()

    if not chunks:
        return []

    # Compute cosine similarity for each chunk
    query_vec = query_embedding

    def cosine_similarity(vec1, vec2):
        """Compute cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0
        import math
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    # Score all chunks
    scored_chunks = []
    for chunk in chunks:
        similarity = cosine_similarity(query_vec, chunk.embedding)
        scored_chunks.append((similarity, chunk))

    # Sort by similarity descending
    scored_chunks.sort(key=lambda x: x[0], reverse=True)

    # Take top_k
    top_chunks = scored_chunks[:top_k]

    # Convert to results
    results = []
    for similarity, chunk in top_chunks:
        results.append(RetrievalResult(
            chunk_id=chunk.id,
            article_id=chunk.article_id,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            similarity=similarity,
            article_title=chunk.title,
            article_category=chunk.category.value if hasattr(chunk.category, 'value') else chunk.category,
            article_slug=chunk.slug,
            article_status=chunk.status,
        ))

    return results


def search_similar_chunks_pgvector(
    db: Session,
    query: str,
    top_k: int = 5,
    user_role: str = "Employee",
    article_ids: Optional[List[int]] = None,
) -> List[RetrievalResult]:
    """
    Search for chunks using pgvector's native similarity search.
    This is more efficient than in-memory similarity for large datasets.

    Requires pgvector extension and an IVFFlat or HNSW index on the embedding column.
    """
    if not query or not query.strip():
        return []

    if top_k <= 0:
        top_k = 5
    if top_k > 50:
        top_k = 50

    provider = get_embedding_provider()
    query_embedding = provider.embed_text(query)

    # Convert embedding to pgvector format (array of floats)
    # pgvector expects a string like '[0.1, 0.2, ...]'
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    # Build the query using pgvector's <=> operator (cosine distance)
    # 1 - cosine_distance = cosine_similarity
    from sqlalchemy import text

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
            1 - (kc.embedding <=> :query_embedding) as similarity
        FROM knowledge_chunks kc
        JOIN knowledge_articles ka ON kc.article_id = ka.id
        WHERE ka.is_deleted = false
        AND kc.embedding IS NOT NULL
    """

    params = {"query_embedding": embedding_str, "top_k": top_k}

    if user_role != "Admin":
        base_query += " AND ka.status = 'PUBLISHED'"

    if article_ids:
        placeholders = ",".join([f":id_{i}" for i in range(len(article_ids))])
        base_query += f" AND ka.id IN ({placeholders})"
        for i, aid in enumerate(article_ids):
            params[f"id_{i}"] = aid

    base_query += " ORDER BY kc.embedding <=> :query_embedding LIMIT :top_k"

    result = db.execute(text(base_query), params).fetchall()

    results = []
    for row in result:
        results.append(RetrievalResult(
            chunk_id=row.id,
            article_id=row.article_id,
            chunk_index=row.chunk_index,
            content=row.content,
            similarity=row.similarity,
            article_title=row.title,
            article_category=row.category,
            article_slug=row.slug,
            article_status=row.status,
        ))

    return results


def hybrid_search(
    db: Session,
    query: str,
    top_k: int = 5,
    user_role: str = "Employee",
    keyword_weight: float = 0.5,
    semantic_weight: float = 0.5,
) -> List[RetrievalResult]:
    """
    Perform hybrid search combining keyword (ILIKE) and semantic similarity.

    Args:
        db: Database session
        query: Search query
        top_k: Number of results
        user_role: User role for visibility
        keyword_weight: Weight for keyword search results
        semantic_weight: Weight for semantic search results

    Returns:
        Combined and ranked results
    """
    # Get keyword search results
    from sqlalchemy import or_
    from app.models.knowledge import KnowledgeArticle

    keyword_query = (
        db.query(KnowledgeArticle)
        .filter(KnowledgeArticle.is_deleted == False)
    )

    if user_role != "Admin":
        keyword_query = keyword_query.filter(KnowledgeArticle.status == ArticleStatus.PUBLISHED)

    keyword_query = keyword_query.filter(
        or_(
            KnowledgeArticle.title.ilike(f"%{query}%"),
            KnowledgeArticle.summary.ilike(f"%{query}%"),
            KnowledgeArticle.content.ilike(f"%{query}%"),
        )
    )

    keyword_articles = keyword_query.limit(top_k).all()

    # Get semantic search results
    semantic_results = search_similar_chunks_pgvector(db, query, top_k, user_role)

    # Combine results with weighted scoring
    # This is a simplified hybrid - in production you'd want more sophisticated fusion
    article_scores = {}

    # Add keyword results
    for article in keyword_articles:
        article_scores[article.id] = keyword_weight * 1.0  # Max score for exact keyword match

    # Add semantic results
    for result in semantic_results:
        current = article_scores.get(result.article_id, 0)
        article_scores[result.article_id] = max(current, semantic_weight * result.similarity)

    # Sort by combined score
    sorted_articles = sorted(article_scores.items(), key=lambda x: x[1], reverse=True)

    # Get top chunks for the top articles
    top_article_ids = [aid for aid, _ in sorted_articles[:top_k]]
    if not top_article_ids:
        return []

    # Get the best chunk for each article
    combined_results = []
    for article_id in top_article_ids:
        article_chunks = [
            r for r in semantic_results if r.article_id == article_id
        ]
        if article_chunks:
            best_chunk = max(article_chunks, key=lambda c: c.similarity)
            combined_results.append(best_chunk)

    return combined_results[:top_k]