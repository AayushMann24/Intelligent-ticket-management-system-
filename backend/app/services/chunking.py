from typing import List
from dataclasses import dataclass

from app.config import settings


@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""
    content: str
    index: int
    start_char: int
    end_char: int


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> List[TextChunk]:
    """
    Split text into overlapping chunks.

    Args:
        text: The text to chunk
        chunk_size: Maximum size of each chunk in characters
        chunk_overlap: Number of characters to overlap between chunks

    Returns:
        List of TextChunk objects
    """
    if not text or not text.strip():
        return []

    chunk_size = chunk_size or settings.chunk_size
    chunk_overlap = chunk_overlap or settings.chunk_overlap

    # Ensure overlap is less than chunk size
    if chunk_overlap >= chunk_size:
        chunk_overlap = chunk_size // 4

    chunks = []
    start = 0
    index = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        # Try to break at a sentence boundary if possible
        if end < text_len:
            # Look for sentence ending punctuation within the last 100 chars
            search_start = max(start, end - 100)
            for i in range(end - 1, search_start - 1, -1):
                if text[i] in ".!?":
                    end = i + 1
                    break

        chunk_content = text[start:end].strip()
        if chunk_content:
            chunks.append(TextChunk(
                content=chunk_content,
                index=len(chunks),
                start_char=start,
                end_char=end,
            ))

        # Move start position with overlap
        if end >= text_len:
            break
        start = end - chunk_overlap
        if start <= 0:
            start = end

    return chunks


def prepare_article_text(article) -> str:
    """
    Prepare article text for chunking by combining title, summary, and content.

    Args:
        article: KnowledgeArticle model instance

    Returns:
        Combined text for embedding
    """
    parts = []

    if article.title:
        parts.append(f"Title: {article.title}")

    if article.category:
        parts.append(f"Category: {article.category.value if hasattr(article.category, 'value') else article.category}")

    if article.summary:
        parts.append(f"Summary: {article.summary}")

    if article.content:
        parts.append(f"Content: {article.content}")

    return "\n\n".join(parts)


def chunk_article(article) -> List[TextChunk]:
    """
    Chunk a knowledge article for embedding.

    Args:
        article: KnowledgeArticle model instance

    Returns:
        List of TextChunk objects
    """
    text = prepare_article_text(article)
    return chunk_text(text)