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
)

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