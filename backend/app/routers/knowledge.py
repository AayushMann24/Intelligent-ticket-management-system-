from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.schemas.knowledge import (
    ArticleCreate,
    ArticleUpdate,
    ArticleResponse,
    ArticleListResponse,
    PaginationParams,
)

from app.services.knowledge_service import (
    create_article,
    get_articles_for_user,
    get_article_by_id,
    update_article,
    publish_article,
    archive_article,
    delete_article,
    get_categories,
    get_article_by_slug,
    get_article_by_id as get_article_by_id_service,
)

from app.services.ingestion import ingest_article, reingest_article, get_ingestion_status
from app.services.retrieval import search_similar_chunks_pgvector, search_similar_chunks, hybrid_search

from app.dependencies.roles import (
    require_admin,
    require_technician,
    require_authenticated_user,
)
from app.dependencies.csrf import csrf_protect

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge Base"],
)


# ======================================================
# Get Categories
# ======================================================
@router.get("/categories", response_model=list[str])
def get_knowledge_categories(
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    return get_categories()


# ======================================================
# Create Article (Admin only)
# ======================================================
@router.post(
    "/",
    response_model=ArticleResponse,
    dependencies=[Depends(csrf_protect)],
)
def create_knowledge_article(
    article: ArticleCreate,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    return create_article(
        db=db,
        article_data=article,
        user_id=user["id"],
    )


# ======================================================
# Get Articles (with RBAC, pagination, search, filter)
# ======================================================
@router.get("/", response_model=dict)
def get_knowledge_articles(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, description="Search in title/summary/content/category"),
    category: str | None = Query(None, description="Filter by category"),
    status: str | None = Query(None, description="Filter by status (Admin only)"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    from app.models.knowledge import ArticleStatus, ArticleCategory

    # Parse category if provided
    category_enum = None
    if category:
        try:
            category_enum = ArticleCategory(category)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")

    # Parse status if provided (Admin only)
    status_enum = None
    if status:
        if user["role"] != "Admin":
            raise HTTPException(status_code=403, detail="Only Admin can filter by status")
        try:
            status_enum = ArticleStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    return get_articles_for_user(
        db=db,
        user_id=user["id"],
        role=user["role"],
        page=page,
        page_size=page_size,
        search=search,
        category=category_enum,
        status=status_enum,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# ======================================================
# Get Article By Slug (Public - for article detail page)
# ======================================================
@router.get(
    "/slug/{slug}",
    response_model=ArticleResponse,
)
def get_knowledge_article_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    return get_article_by_slug(
        db=db,
        slug=slug,
        user_role=user["role"],
    )


# ======================================================
# Get Article By ID
# ======================================================
@router.get(
    "/{article_id}",
    response_model=ArticleResponse,
)
def get_knowledge_article(
    article_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    return get_article_by_id(
        db=db,
        article_id=article_id,
        user_id=user["id"],
        user_role=user["role"],
    )


# ======================================================
# Update Article
# ======================================================
@router.put(
    "/{article_id}",
    response_model=ArticleResponse,
    dependencies=[Depends(csrf_protect)],
)
def update_knowledge_article(
    article_id: int,
    article: ArticleUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    return update_article(
        db=db,
        article_id=article_id,
        article_data=article,
        user_id=user["id"],
        user_role=user["role"],
    )


# ======================================================
# Publish Article (Admin only)
# ======================================================
@router.post(
    "/{article_id}/publish",
    response_model=ArticleResponse,
    dependencies=[Depends(csrf_protect)],
)
def publish_knowledge_article(
    article_id: int,
    _: dict,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    return publish_article(
        db=db,
        article_id=article_id,
        user_id=user["id"],
        user_role=user["role"],
    )


# ======================================================
# Archive Article (Admin only)
# ======================================================
@router.post(
    "/{article_id}/archive",
    response_model=ArticleResponse,
    dependencies=[Depends(csrf_protect)],
)
def archive_knowledge_article(
    article_id: int,
    _: dict,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    return archive_article(
        db=db,
        article_id=article_id,
        user_id=user["id"],
        user_role=user["role"],
    )


# ======================================================
# Delete Article (Admin only)
# ======================================================
@router.delete(
    "/{article_id}",
    dependencies=[Depends(csrf_protect)],
)
def delete_knowledge_article(
    article_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    return delete_article(
        db=db,
        article_id=article_id,
        user_id=user["id"],
        user_role=user["role"],
    )


# ======================================================
# Ingestion Endpoints (Admin only)
# ======================================================

@router.post(
    "/{article_id}/ingest",
    response_model=dict,
    dependencies=[Depends(csrf_protect)],
)
def ingest_knowledge_article(
    article_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    """Ingest a published article into the vector store."""
    article = get_article_by_id_service(db=db, article_id=article_id, user_id=user["id"], user_role=user["role"])
    return ingest_article(db=db, article=article)


@router.post(
    "/{article_id}/reingest",
    response_model=dict,
    dependencies=[Depends(csrf_protect)],
)
def reingest_knowledge_article(
    article_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    """Force re-ingestion of an article (replace all chunks)."""
    article = get_article_by_id_service(db=db, article_id=article_id, user_id=user["id"], user_role=user["role"])
    return reingest_article(db=db, article=article)


@router.get(
    "/{article_id}/ingestion-status",
    response_model=dict,
)
def get_knowledge_article_ingestion_status(
    article_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    """Get ingestion status for an article."""
    # Verify article exists and user has access
    get_article_by_id_service(db=db, article_id=article_id, user_id=user["id"], user_role=user["role"])
    return get_ingestion_status(db=db, article_id=article_id)


# ======================================================
# Semantic Search Endpoints
# ======================================================

@router.post(
    "/search/semantic",
    response_model=list[dict],
)
def semantic_search_knowledge(
    query: str,
    top_k: int = 5,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    """
    Perform semantic search on knowledge base articles.

    Args:
        query: Search query text
        top_k: Number of results to return (max 50)

    Returns:
        List of matching chunks with similarity scores and article metadata
    """
    if top_k > 50:
        top_k = 50

    try:
        results = search_similar_chunks_pgvector(
            db=db,
            query=query,
            top_k=top_k,
            user_role=user["role"],
        )
        return [
            {
                "chunk_id": r.chunk_id,
                "article_id": r.article_id,
                "chunk_index": r.chunk_index,
                "content": r.content,
                "similarity": r.similarity,
                "article_title": r.article_title,
                "article_category": r.article_category,
                "article_slug": r.article_slug,
                "article_status": r.article_status,
            }
            for r in results
        ]
    except Exception as e:
        # Fallback to in-memory similarity if pgvector fails
        results = search_similar_chunks(
            db=db,
            query=query,
            top_k=top_k,
            user_role=user["role"],
        )
        return [
            {
                "chunk_id": r.chunk_id,
                "article_id": r.article_id,
                "chunk_index": r.chunk_index,
                "content": r.content,
                "similarity": r.similarity,
                "article_title": r.article_title,
                "article_category": r.article_category,
                "article_slug": r.article_slug,
                "article_status": r.article_status,
            }
            for r in results
        ]


@router.post(
    "/search/hybrid",
    response_model=list[dict],
)
def hybrid_search_knowledge(
    query: str,
    top_k: int = 5,
    keyword_weight: float = 0.5,
    semantic_weight: float = 0.5,
    db: Session = Depends(get_db),
    user=Depends(require_authenticated_user),
):
    """
    Perform hybrid search combining keyword and semantic search.

    Args:
        query: Search query text
        top_k: Number of results to return (max 50)
        keyword_weight: Weight for keyword search (0-1)
        semantic_weight: Weight for semantic search (0-1)

    Returns:
        List of matching results with combined scores
    """
    if top_k > 50:
        top_k = 50

    # Normalize weights
    total_weight = keyword_weight + semantic_weight
    if total_weight == 0:
        keyword_weight = 0.5
        semantic_weight = 0.5
    else:
        keyword_weight = keyword_weight / total_weight
        semantic_weight = semantic_weight / total_weight

    try:
        results = hybrid_search(
            db=db,
            query=query,
            top_k=top_k,
            user_role=user["role"],
            keyword_weight=keyword_weight,
            semantic_weight=semantic_weight,
        )
        return [
            {
                "chunk_id": r.chunk_id,
                "article_id": r.article_id,
                "chunk_index": r.chunk_index,
                "content": r.content,
                "similarity": r.similarity,
                "article_title": r.article_title,
                "article_category": r.article_category,
                "article_slug": r.article_slug,
                "article_status": r.article_status,
            }
            for r in results
        ]
    except Exception:
        # Fallback to semantic only
        return semantic_search_knowledge(query=query, top_k=top_k, db=db, user=user)