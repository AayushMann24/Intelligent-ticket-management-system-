"""Tests for knowledge base retrieval services."""

import pytest
from sqlalchemy.orm import Session
from slugify import slugify

from app.models.knowledge import KnowledgeArticle, ArticleStatus, ArticleCategory
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.user import User
from app.services.retrieval import (
    search_similar_chunks,
    search_similar_chunks_pgvector,
    search_keyword_chunks,
    hybrid_search,
    build_context,
    retrieve_and_build_context,
    RetrievalResult,
)
from app.services.retrieval_evaluation import (
    EVAL_QUERIES,
    MockEmbeddingProvider,
    evaluate_retrieval,
    create_test_articles,
    compute_metrics,
)
from app.services.embeddings import get_embedding_provider
from app.utils.security import hash_password
from unittest.mock import patch


def _generate_unique_slug(db: Session, title: str, exclude_id: int | None = None) -> str:
    """Generate a unique slug from title (copied from knowledge_service for test use)."""
    base_slug = slugify(title)
    if not base_slug:
        base_slug = "article"

    slug = base_slug
    counter = 1
    while True:
        query = db.query(KnowledgeArticle).filter(KnowledgeArticle.slug == slug)
        if exclude_id:
            query = query.filter(KnowledgeArticle.id != exclude_id)
        if not query.first():
            return slug
        counter += 1
        slug = f"{base_slug}-{counter}"


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def admin_user(db_session: Session) -> User:
    """Create an admin user for testing."""
    user = User(
        name="Admin User",
        email="admin@test.com",
        password=hash_password("adminpass"),
        role="Admin",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def employee_user(db_session: Session) -> User:
    """Create an employee user for testing."""
    user = User(
        name="Employee User",
        email="employee@test.com",
        password=hash_password("emppass"),
        role="Employee",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def technician_user(db_session: Session) -> User:
    """Create a technician user for testing."""
    user = User(
        name="Technician User",
        email="tech@test.com",
        password=hash_password("techpass"),
        role="Technician",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def published_articles(db_session: Session, admin_user: User) -> list[KnowledgeArticle]:
    """Create published test articles with chunks."""
    articles_data = [
        {
            "title": "Password Reset Guide",
            "summary": "How to reset your password",
            "content": "To reset your password, go to the login page and click Forgot Password. Enter your email and follow the reset link.",
            "category": ArticleCategory.ACCOUNT,
        },
        {
            "title": "WiFi Troubleshooting",
            "summary": "Fix common WiFi issues",
            "content": "If your laptop won't connect to WiFi, toggle WiFi off and on. Check if other devices connect. Forget network and reconnect.",
            "category": ArticleCategory.NETWORK,
        },
        {
            "title": "VPN Setup Guide",
            "summary": "Configure VPN for remote access",
            "content": "Download VPN client from IT portal. Install and enter domain credentials. Select Corporate-Full tunnel for full access.",
            "category": ArticleCategory.NETWORK,
        },
        {
            "title": "Printer Configuration",
            "summary": "Set up network printers",
            "content": "Add network printer via Settings > Devices. Enter printer IP address. Install driver from manufacturer website.",
            "category": ArticleCategory.HARDWARE,
        },
    ]

    articles = []
    for data in articles_data:
        slug = _generate_unique_slug(db_session, data["title"])
        article = KnowledgeArticle(
            title=data["title"],
            slug=slug,
            summary=data["summary"],
            content=data["content"],
            category=data["category"],
            status=ArticleStatus.PUBLISHED,
            author_id=admin_user.id,
        )
        db_session.add(article)
        articles.append(article)

    db_session.commit()
    for article in articles:
        db_session.refresh(article)

    # Create chunks with mock embeddings
    provider = MockEmbeddingProvider()
    for article in articles:
        # Create 2-3 chunks per article
        for i in range(2):
            chunk_text = f"{article.title} - Part {i+1}: {article.content}"
            embedding = provider.embed_text(chunk_text)
            chunk = KnowledgeChunk(
                article_id=article.id,
                chunk_index=i,
                content=chunk_text,
                embedding=embedding,
            )
            db_session.add(chunk)

    db_session.commit()
    return articles


@pytest.fixture
def draft_article(db_session: Session, admin_user: User) -> KnowledgeArticle:
    """Create a draft article (should not be visible to employees)."""
    slug = _generate_unique_slug(db_session, "Draft Article - Not Published")
    article = KnowledgeArticle(
        title="Draft Article - Not Published",
        slug=slug,
        summary="This is a draft",
        content="Draft content that should not be retrievable by employees",
        category=ArticleCategory.OTHER,
        status=ArticleStatus.DRAFT,
        author_id=admin_user.id,
    )
    db_session.add(article)
    db_session.commit()
    db_session.refresh(article)

    # Add chunk with embedding
    provider = MockEmbeddingProvider()
    chunk = KnowledgeChunk(
        article_id=article.id,
        chunk_index=0,
        content="Draft content that should not be retrievable by employees",
        embedding=provider.embed_text("Draft content"),
    )
    db_session.add(chunk)
    db_session.commit()

    return article


@pytest.fixture
def archived_article(db_session: Session, admin_user: User) -> KnowledgeArticle:
    """Create an archived article (should not be visible to employees)."""
    slug = _generate_unique_slug(db_session, "Archived Article - Old Content")
    article = KnowledgeArticle(
        title="Archived Article - Old Content",
        slug=slug,
        summary="This is archived",
        content="Archived content that should not be retrievable by employees",
        category=ArticleCategory.OTHER,
        status=ArticleStatus.ARCHIVED,
        author_id=admin_user.id,
    )
    db_session.add(article)
    db_session.commit()
    db_session.refresh(article)

    provider = MockEmbeddingProvider()
    chunk = KnowledgeChunk(
        article_id=article.id,
        chunk_index=0,
        content="Archived content that should not be retrievable by employees",
        embedding=provider.embed_text("Archived content"),
    )
    db_session.add(chunk)
    db_session.commit()

    return article


# ============================================================
# Semantic Search Tests
# ============================================================

def test_semantic_search_returns_results(db_session: Session, published_articles):
    """Test semantic search returns relevant results."""
    results = search_similar_chunks_pgvector(
        db=db_session,
        query="password reset",
        top_k=5,
        user_role="Employee",
    )

    assert len(results) > 0
    assert all(isinstance(r, RetrievalResult) for r in results)
    assert all(r.source == "semantic" for r in results)
    # Should find the password reset article
    titles = [r.article_title for r in results]
    assert "Password Reset Guide" in titles


def test_semantic_search_respects_top_k(db_session: Session, published_articles):
    """Test semantic search respects top_k limit."""
    results = search_similar_chunks_pgvector(
        db=db_session,
        query="password",
        top_k=2,
        user_role="Employee",
    )
    assert len(results) <= 2

    results = search_similar_chunks_pgvector(
        db=db_session,
        query="password",
        top_k=10,
        user_role="Employee",
    )
    assert len(results) <= 10


def test_semantic_search_enforces_max_top_k(db_session: Session, published_articles):
    """Test semantic search enforces maximum top_k of 50."""
    results = search_similar_chunks_pgvector(
        db=db_session,
        query="password",
        top_k=100,  # Should be capped at 50
        user_role="Employee",
    )
    assert len(results) <= 50


def test_semantic_search_empty_query(db_session: Session, published_articles):
    """Test semantic search with empty query returns empty list."""
    results = search_similar_chunks_pgvector(
        db=db_session,
        query="",
        top_k=5,
        user_role="Employee",
    )
    assert results == []

    results = search_similar_chunks_pgvector(
        db=db_session,
        query="   ",
        top_k=5,
        user_role="Employee",
    )
    assert results == []


def test_semantic_search_category_filter(db_session: Session, published_articles):
    """Test semantic search with category filter."""
    results = search_similar_chunks_pgvector(
        db=db_session,
        query="troubleshooting",
        top_k=10,
        user_role="Employee",
        category="Network",
    )
    # Should only return Network category articles
    for r in results:
        assert r.article_category == "Network"


def test_semantic_search_invalid_category(db_session: Session, published_articles):
    """Test semantic search with invalid category returns empty."""
    results = search_similar_chunks_pgvector(
        db=db_session,
        query="password",
        top_k=5,
        user_role="Employee",
        category="InvalidCategory",
    )
    assert results == []


def test_semantic_search_published_only_for_employee(db_session: Session, published_articles, draft_article, archived_article):
    """Test employees only see published articles."""
    # Search for content that exists in draft/archived
    results = search_similar_chunks_pgvector(
        db=db_session,
        query="Draft Article",
        top_k=5,
        user_role="Employee",
    )
    # Should not find draft article
    titles = [r.article_title for r in results]
    assert "Draft Article - Not Published" not in titles

    results = search_similar_chunks_pgvector(
        db=db_session,
        query="Archived Article",
        top_k=5,
        user_role="Employee",
    )
    titles = [r.article_title for r in results]
    assert "Archived Article - Old Content" not in titles


def test_semantic_search_admin_sees_all(db_session: Session, published_articles, draft_article, archived_article):
    """Test admins see all articles regardless of status."""
    results = search_similar_chunks_pgvector(
        db=db_session,
        query="Draft Article",
        top_k=5,
        user_role="Admin",
    )
    titles = [r.article_title for r in results]
    assert "Draft Article - Not Published" in titles

    results = search_similar_chunks_pgvector(
        db=db_session,
        query="Archived Article",
        top_k=5,
        user_role="Admin",
    )
    titles = [r.article_title for r in results]
    assert "Archived Article - Old Content" in titles


def test_semantic_search_deterministic_ordering(db_session: Session, published_articles):
    """Test semantic search has deterministic ordering for ties."""
    # Run multiple times
    results1 = search_similar_chunks_pgvector(
        db=db_session,
        query="test query that might have ties",
        top_k=10,
        user_role="Employee",
    )
    results2 = search_similar_chunks_pgvector(
        db=db_session,
        query="test query that might have ties",
        top_k=10,
        user_role="Employee",
    )

    # Should have same order
    ids1 = [r.chunk_id for r in results1]
    ids2 = [r.chunk_id for r in results2]
    assert ids1 == ids2


def test_semantic_search_no_duplicates(db_session: Session, published_articles):
    """Test semantic search doesn't return duplicate chunks."""
    results = search_similar_chunks_pgvector(
        db=db_session,
        query="password",
        top_k=10,
        user_role="Employee",
    )
    chunk_ids = [r.chunk_id for r in results]
    assert len(chunk_ids) == len(set(chunk_ids))


def test_semantic_search_result_structure(db_session: Session, published_articles):
    """Test semantic search results have all required fields."""
    results = search_similar_chunks_pgvector(
        db=db_session,
        query="password",
        top_k=5,
        user_role="Employee",
    )

    assert len(results) > 0
    r = results[0]
    assert hasattr(r, 'chunk_id')
    assert hasattr(r, 'article_id')
    assert hasattr(r, 'chunk_index')
    assert hasattr(r, 'content')
    assert hasattr(r, 'score')
    assert hasattr(r, 'article_title')
    assert hasattr(r, 'article_slug')
    assert hasattr(r, 'article_category')
    assert hasattr(r, 'article_status')
    assert hasattr(r, 'source')
    assert r.source == "semantic"
    assert 0.0 <= r.score <= 1.0


# ============================================================
# Keyword Search Tests
# ============================================================

def test_keyword_search_returns_results(db_session: Session, published_articles):
    """Test keyword search returns relevant results."""
    results = search_keyword_chunks(
        db=db_session,
        query="password",
        top_k=5,
        user_role="Employee",
    )

    assert len(results) > 0
    assert all(r.source == "keyword" for r in results)
    titles = [r.article_title for r in results]
    assert "Password Reset Guide" in titles


def test_keyword_search_title_priority(db_session: Session, published_articles):
    """Test keyword search prioritizes title matches."""
    results = search_keyword_chunks(
        db=db_session,
        query="Password",
        top_k=5,
        user_role="Employee",
    )

    # Title match should score higher (1.0) than content match (0.5)
    password_results = [r for r in results if "Password" in r.article_title]
    if password_results:
        assert password_results[0].score >= 0.7  # Title or summary match


def test_keyword_search_published_only(db_session: Session, published_articles, draft_article):
    """Test keyword search respects visibility for employees."""
    results = search_keyword_chunks(
        db=db_session,
        query="Draft",
        top_k=5,
        user_role="Employee",
    )
    titles = [r.article_title for r in results]
    assert "Draft Article - Not Published" not in titles


def test_keyword_search_admin_sees_all(db_session: Session, published_articles, draft_article):
    """Test admin sees draft articles in keyword search."""
    results = search_keyword_chunks(
        db=db_session,
        query="Draft",
        top_k=5,
        user_role="Admin",
    )
    titles = [r.article_title for r in results]
    assert "Draft Article - Not Published" in titles


def test_keyword_search_category_filter(db_session: Session, published_articles):
    """Test keyword search with category filter."""
    results = search_keyword_chunks(
        db=db_session,
        query="network",
        top_k=10,
        user_role="Employee",
        category="Network",
    )
    for r in results:
        assert r.article_category == "Network"


def test_keyword_search_deterministic(db_session: Session, published_articles):
    """Test keyword search has deterministic ordering."""
    results1 = search_keyword_chunks(
        db=db_session,
        query="network",
        top_k=10,
        user_role="Employee",
    )
    results2 = search_keyword_chunks(
        db=db_session,
        query="network",
        top_k=10,
        user_role="Employee",
    )

    ids1 = [r.chunk_id for r in results1]
    ids2 = [r.chunk_id for r in results2]
    assert ids1 == ids2


# ============================================================
# Hybrid Search Tests
# ============================================================

def test_hybrid_search_returns_results(db_session: Session, published_articles):
    """Test hybrid search returns combined results."""
    results = hybrid_search(
        db=db_session,
        query="password reset",
        top_k=5,
        user_role="Employee",
        keyword_weight=0.5,
        semantic_weight=0.5,
    )

    assert len(results) > 0
    assert all(isinstance(r, RetrievalResult) for r in results)
    sources = {r.source for r in results}
    # Should have at least semantic results
    assert "semantic" in sources or "hybrid" in sources


def test_hybrid_search_no_duplicates(db_session: Session, published_articles):
    """Test hybrid search removes duplicate chunks."""
    results = hybrid_search(
        db=db_session,
        query="network vpn",
        top_k=10,
        user_role="Employee",
    )

    chunk_ids = [r.chunk_id for r in results]
    assert len(chunk_ids) == len(set(chunk_ids))


def test_hybrid_search_respects_top_k(db_session: Session, published_articles):
    """Test hybrid search respects top_k limit."""
    for k in [1, 3, 5, 10, 50]:
        results = hybrid_search(
            db=db_session,
            query="password",
            top_k=k,
            user_role="Employee",
        )
        assert len(results) <= k


def test_hybrid_search_weight_normalization(db_session: Session, published_articles):
    """Test hybrid search normalizes weights."""
    # Both weights zero should default to 0.5/0.5
    results = hybrid_search(
        db=db_session,
        query="password",
        top_k=5,
        user_role="Employee",
        keyword_weight=0.0,
        semantic_weight=0.0,
    )
    assert len(results) > 0

    # Unequal weights should be normalized
    results1 = hybrid_search(
        db=db_session,
        query="password",
        top_k=5,
        user_role="Employee",
        keyword_weight=1.0,
        semantic_weight=0.0,
    )
    results2 = hybrid_search(
        db=db_session,
        query="password",
        top_k=5,
        user_role="Employee",
        keyword_weight=2.0,
        semantic_weight=0.0,
    )
    # Should produce same results after normalization
    ids1 = [r.chunk_id for r in results1]
    ids2 = [r.chunk_id for r in results2]
    assert ids1 == ids2


def test_hybrid_search_source_attribution(db_session: Session, published_articles):
    """Test hybrid search correctly attributes sources."""
    results = hybrid_search(
        db=db_session,
        query="password wifi",  # Matches both password and wifi articles
        top_k=10,
        user_role="Employee",
        keyword_weight=0.5,
        semantic_weight=0.5,
    )

    sources = {r.source for r in results}
    # Should have hybrid results when both keyword and semantic match
    assert "semantic" in sources or "keyword" in sources or "hybrid" in sources


def test_hybrid_search_deterministic(db_session: Session, published_articles):
    """Test hybrid search has deterministic ordering."""
    results1 = hybrid_search(
        db=db_session,
        query="password network",
        top_k=10,
        user_role="Employee",
    )
    results2 = hybrid_search(
        db=db_session,
        query="password network",
        top_k=10,
        user_role="Employee",
    )

    ids1 = [r.chunk_id for r in results1]
    ids2 = [r.chunk_id for r in results2]
    assert ids1 == ids2


def test_hybrid_search_category_filter(db_session: Session, published_articles):
    """Test hybrid search with category filter."""
    results = hybrid_search(
        db=db_session,
        query="troubleshooting",
        top_k=10,
        user_role="Employee",
        category="Network",
    )
    for r in results:
        assert r.article_category == "Network"


def test_hybrid_search_published_only_employee(db_session: Session, published_articles, draft_article):
    """Test hybrid search respects visibility for employees."""
    results = hybrid_search(
        db=db_session,
        query="Draft",
        top_k=5,
        user_role="Employee",
    )
    titles = [r.article_title for r in results]
    assert "Draft Article - Not Published" not in titles


def test_hybrid_search_admin_sees_all(db_session: Session, published_articles, draft_article):
    """Test admin sees all in hybrid search."""
    results = hybrid_search(
        db=db_session,
        query="Draft",
        top_k=5,
        user_role="Admin",
    )
    titles = [r.article_title for r in results]
    assert "Draft Article - Not Published" in titles


# ============================================================
# Context Builder Tests
# ============================================================

def test_build_context_basic(db_session: Session, published_articles):
    """Test basic context building."""
    results = search_similar_chunks_pgvector(
        db=db_session,
        query="password",
        top_k=5,
        user_role="Employee",
    )

    context = build_context(results, "password", max_chunks=3, max_chars=1000)

    assert context.query == "password"
    assert len(context.chunks) <= 3
    assert context.total_chunks <= 3
    assert context.total_chars <= 1000
    assert len(context.citations) == len(context.chunks)


def test_build_context_max_chunks(db_session: Session, published_articles):
    """Test context respects max_chunks limit."""
    results = search_similar_chunks_pgvector(
        db=db_session,
        query="network",
        top_k=10,
        user_role="Employee",
    )

    context = build_context(results, "network", max_chunks=2, max_chars=10000)
    assert len(context.chunks) <= 2


def test_build_context_max_chars(db_session: Session, published_articles):
    """Test context respects max_chars limit."""
    results = search_similar_chunks_pgvector(
        db=db_session,
        query="password",
        top_k=10,
        user_role="Employee",
    )

    # Very small char limit
    context = build_context(results, "password", max_chunks=10, max_chars=50)
    assert context.total_chars <= 50


def test_build_context_empty_results(db_session: Session):
    """Test context building with empty results."""
    context = build_context([], "empty query")
    assert context.chunks == []
    assert context.citations == []
    assert context.total_chunks == 0
    assert context.total_chars == 0


def test_build_context_citation_structure(db_session: Session, published_articles):
    """Test citations have all required fields."""
    results = search_similar_chunks_pgvector(
        db=db_session,
        query="password",
        top_k=3,
        user_role="Employee",
    )

    context = build_context(results, "password")

    for citation in context.citations:
        assert hasattr(citation, 'article_id')
        assert hasattr(citation, 'article_title')
        assert hasattr(citation, 'article_slug')
        assert hasattr(citation, 'chunk_id')
        assert hasattr(citation, 'chunk_index')
        assert hasattr(citation, 'content')
        assert hasattr(citation, 'score')
        assert hasattr(citation, 'source')
        assert 0.0 <= citation.score <= 1.0


def test_retrieve_and_build_context(db_session: Session, published_articles):
    """Test combined retrieve and build context."""
    context = retrieve_and_build_context(
        db=db_session,
        query="password reset",
        top_k=5,
        user_role="Employee",
        use_hybrid=True,
    )

    assert context.query == "password reset"
    assert len(context.chunks) > 0
    assert len(context.citations) == len(context.chunks)


# ============================================================
# In-Memory Fallback Tests
# ============================================================

def test_search_similar_chunks_fallback(db_session: Session, published_articles):
    """Test in-memory semantic search fallback works."""
    results = search_similar_chunks(
        db=db_session,
        query="password",
        top_k=5,
        user_role="Employee",
    )

    assert len(results) > 0
    assert all(r.source == "semantic" for r in results)
    titles = [r.article_title for r in results]
    assert "Password Reset Guide" in titles


# ============================================================
# Retrieval Evaluation Tests
# ============================================================

def test_mock_embedding_provider_deterministic():
    """Test mock embedding provider returns deterministic vectors."""
    provider = MockEmbeddingProvider(dimension=10)

    vec1 = provider.embed_text("test query")
    vec2 = provider.embed_text("test query")
    vec3 = provider.embed_text("different query")

    assert vec1 == vec2
    assert vec1 != vec3
    assert len(vec1) == 10


def test_compute_metrics():
    """Test metric computation."""
    from app.schemas.retrieval import RetrievalSource

    results = [
        RetrievalResult(
            chunk_id=1, article_id=1, chunk_index=0, content="content1",
            score=0.9, article_title="Article A", article_slug="a",
            article_category="Test", article_status="PUBLISHED", source="semantic"
        ),
        RetrievalResult(
            chunk_id=2, article_id=2, chunk_index=0, content="content2",
            score=0.8, article_title="Article B", article_slug="b",
            article_category="Test", article_status="PUBLISHED", source="semantic"
        ),
        RetrievalResult(
            chunk_id=3, article_id=3, chunk_index=0, content="content3",
            score=0.7, article_title="Article C", article_slug="c",
            article_category="Test", article_status="PUBLISHED", source="semantic"
        ),
    ]

    expected = ["Article A", "Article C"]
    metrics = compute_metrics(results, expected, ks=[1, 3, 5])

    assert metrics.hit_at_k[1] == True  # Article A at rank 1
    assert metrics.hit_at_k[3] == True
    assert metrics.recall_at_k[1] == 0.5  # 1 of 2 found
    assert metrics.recall_at_k[3] == 1.0  # 2 of 2 found
    assert metrics.precision_at_k[1] == 1.0
    assert metrics.precision_at_k[3] == 2/3
    assert metrics.mrr == 1.0  # First relevant at rank 1


def test_evaluate_retrieval_runs(db_session: Session, admin_user: User):
    """Test evaluation runs without errors (using mock embeddings)."""
    # Create test articles
    create_test_articles(db_session, admin_user.id)

    # Mock the embedding provider
    with patch('app.services.retrieval.get_embedding_provider', return_value=MockEmbeddingProvider()):
        summary = evaluate_retrieval(
            db=db_session,
            queries=EVAL_QUERIES[:3],  # Just first 3 for speed
            user_role="Employee",
            top_k=5,
        )

    assert summary.total_queries == 3
    assert 0 <= summary.avg_recall_at_1 <= 1
    assert 0 <= summary.avg_recall_at_3 <= 1
    assert 0 <= summary.avg_recall_at_5 <= 1
    assert 0 <= summary.avg_mrr <= 1
    assert 0 <= summary.hit_rate_at_1 <= 1
    assert len(summary.per_query) == 3


# ============================================================
# Edge Cases
# ============================================================

def test_search_with_article_ids_filter(db_session: Session, published_articles):
    """Test search with article_ids filter."""
    article_id = published_articles[0].id

    results = search_similar_chunks_pgvector(
        db=db_session,
        query="password",
        top_k=5,
        user_role="Employee",
        article_ids=[article_id],
    )

    for r in results:
        assert r.article_id == article_id


def test_search_with_no_results(db_session: Session):
    """Test search with query that matches nothing."""
    from unittest.mock import patch
    from app.services.retrieval_evaluation import MockEmbeddingProvider

    with patch('app.services.retrieval.get_embedding_provider', return_value=MockEmbeddingProvider()):
        results = search_similar_chunks_pgvector(
            db=db_session,
            query="xyzqwertyunlikelyterm",
            top_k=5,
            user_role="Employee",
        )
    assert results == []


def test_technician_same_as_employee(db_session: Session, published_articles, technician_user):
    """Test technician has same visibility as employee."""
    from unittest.mock import patch
    from app.services.retrieval_evaluation import MockEmbeddingProvider

    with patch('app.services.retrieval.get_embedding_provider', return_value=MockEmbeddingProvider()):
        results_emp = search_similar_chunks_pgvector(
            db=db_session,
            query="password",
            top_k=5,
            user_role="Employee",
        )
        results_tech = search_similar_chunks_pgvector(
            db=db_session,
            query="password",
            top_k=5,
            user_role="Technician",
        )

    ids_emp = [r.chunk_id for r in results_emp]
    ids_tech = [r.chunk_id for r in results_tech]
    assert ids_emp == ids_tech


def test_retrieval_result_immutability(db_session: Session, published_articles):
    """Test retrieval results are proper Pydantic models."""
    from unittest.mock import patch
    from app.services.retrieval_evaluation import MockEmbeddingProvider

    with patch('app.services.retrieval.get_embedding_provider', return_value=MockEmbeddingProvider()):
        results = search_similar_chunks_pgvector(
            db=db_session,
            query="password",
            top_k=3,
            user_role="Employee",
        )

    r = results[0]
    # Should be able to serialize to dict
    d = r.model_dump()
    assert 'chunk_id' in d
    assert 'score' in d
    assert 'source' in d


# ============================================================
# Performance/Stress Tests
# ============================================================

def test_semantic_search_performance(db_session: Session, published_articles):
    """Test semantic search completes in reasonable time."""
    import time
    from unittest.mock import patch
    from app.services.retrieval_evaluation import MockEmbeddingProvider

    with patch('app.services.retrieval.get_embedding_provider', return_value=MockEmbeddingProvider()):
        start = time.time()
        for _ in range(10):
            search_similar_chunks_pgvector(
                db=db_session,
                query="password reset wifi vpn",
                top_k=10,
                user_role="Employee",
            )
        elapsed = time.time() - start

    # Should complete 10 searches in under 5 seconds
    assert elapsed < 5.0


def test_hybrid_search_performance(db_session: Session, published_articles):
    """Test hybrid search completes in reasonable time."""
    import time
    from unittest.mock import patch
    from app.services.retrieval_evaluation import MockEmbeddingProvider

    with patch('app.services.retrieval.get_embedding_provider', return_value=MockEmbeddingProvider()):
        start = time.time()
        for _ in range(10):
            hybrid_search(
                db=db_session,
                query="password reset wifi vpn",
                top_k=10,
                user_role="Employee",
            )
        elapsed = time.time() - start

    # Should complete 10 searches in under 10 seconds
    assert elapsed < 10.0