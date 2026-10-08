from datetime import datetime, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeArticle, ArticleStatus
from app.models.knowledge_chunk import KnowledgeChunk
from app.services.embeddings import get_embedding_provider
from app.services.chunking import chunk_article, TextChunk


def get_article_chunks(db: Session, article_id: int) -> list[KnowledgeChunk]:
    """Get all chunks for an article."""
    return (
        db.query(KnowledgeChunk)
        .filter(KnowledgeChunk.article_id == article_id)
        .order_by(KnowledgeChunk.chunk_index)
        .all()
    )


def delete_article_chunks(db: Session, article_id: int) -> int:
    """Delete all chunks for an article. Returns number of deleted chunks."""
    count = (
        db.query(KnowledgeChunk)
        .filter(KnowledgeChunk.article_id == article_id)
        .delete()
    )
    return count


def ingest_article(db: Session, article: "KnowledgeArticle") -> dict:
    """
    Ingest a knowledge article into the vector store.

    Args:
        db: Database session
        article: KnowledgeArticle to ingest

    Returns:
        Dictionary with ingestion results
    """
    # Validate article is published
    if article.status != "PUBLISHED":
        return {
            "success": False,
            "error": f"Article must be published to ingest. Current status: {article.status}",
            "chunks_created": 0,
            "chunks_deleted": 0,
        }

    # Get embedding provider
    provider = get_embedding_provider()

    # Chunk the article
    chunks = chunk_article(article)
    if not chunks:
        return {
            "success": False,
            "error": "Article produced no valid chunks",
            "chunks_created": 0,
            "chunks_deleted": 0,
        }

    # Delete existing chunks for this article (idempotent)
    deleted_count = delete_article_chunks(db, article.id)

    # Generate embeddings for all chunks
    chunk_texts = [chunk.content for chunk in chunks]
    embeddings = provider.embed_documents(chunk_texts)

    # Store chunks with embeddings
    created_chunks = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        knowledge_chunk = KnowledgeChunk(
            article_id=article.id,
            chunk_index=chunk.index,
            content=chunk.content,
            embedding=embedding,
        )
        db.add(knowledge_chunk)
        created_chunks.append(knowledge_chunk)

    db.flush()

    return {
        "success": True,
        "chunks_created": len(created_chunks),
        "chunks_deleted": 0,  # We don't return the actual deleted count to avoid confusion
        "total_chunks": len(created_chunks),
    }


def reingest_article(db: Session, article: "KnowledgeArticle") -> dict:
    """
    Re-ingest an article (force full re-ingestion).

    This is useful when the article content has changed significantly
    or when the embedding model has changed.
    """
    # Delete all existing chunks first
    deleted_count = delete_article_chunks(db, article.id)
    db.flush()

    # Run full ingestion
    result = ingest_article(db, article)
    if result.get("success"):
        result["chunks_deleted"] = deleted_count
    return result


def is_article_ingested(db: Session, article_id: int) -> bool:
    """Check if an article has been ingested (has chunks)."""
    count = (
        db.query(KnowledgeChunk)
        .filter(KnowledgeChunk.article_id == article_id)
        .count()
    )
    return count > 0


def get_ingestion_status(db: Session, article_id: int) -> dict:
    """Get ingestion status for an article."""
    chunks = get_article_chunks(db, article_id)
    return {
        "ingested": len(chunks) > 0,
        "chunk_count": len(chunks),
        "last_updated": chunks[-1].updated_at if chunks else None,
    }