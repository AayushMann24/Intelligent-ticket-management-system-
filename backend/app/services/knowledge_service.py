from datetime import datetime, timezone
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from slugify import slugify

from app.models.knowledge import KnowledgeArticle, ArticleStatus, ArticleCategory
from app.models.user import User
from app.schemas.knowledge import (
    ArticleCreate,
    ArticleUpdate,
    ArticleFilterParams,
    PaginationParams,
)
from app.dependencies.roles import require_admin


def _base_article_query(db: Session):
    """Base query that excludes soft-deleted articles."""
    return db.query(KnowledgeArticle).filter(KnowledgeArticle.is_deleted == False)


def _base_user_query(db: Session):
    """Base query that excludes soft-deleted users."""
    return db.query(User).filter(User.is_deleted == False)


def _generate_unique_slug(db: Session, title: str, exclude_id: int | None = None) -> str:
    """Generate a unique slug from title."""
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


def _serialize_article(article: KnowledgeArticle) -> dict:
    """Serialize article for API response."""
    return {
        "id": article.id,
        "title": article.title,
        "slug": article.slug,
        "summary": article.summary,
        "content": article.content,
        "category": article.category.value if hasattr(article.category, 'value') else article.category,
        "status": article.status.value if hasattr(article.status, 'value') else article.status,
        "author_id": article.author_id,
        "author_name": article.author.name if article.author else None,
        "created_at": article.created_at,
        "updated_at": article.updated_at,
        "published_at": article.published_at,
    }


def _can_view_article(user_role: str, article: KnowledgeArticle) -> bool:
    """Check if user can view an article based on role and article status."""
    # Admin can view all articles regardless of status
    if user_role == "Admin":
        return True
    # Published articles are visible to all authenticated users
    if article.status == ArticleStatus.PUBLISHED:
        return True
    # Draft and archived articles are only visible to Admin
    return False


def _can_modify_article(user_id: int, user_role: str, article: KnowledgeArticle) -> bool:
    """Check if user can modify an article."""
    # Admin can modify any article
    if user_role == "Admin":
        return True
    # Author can modify their own draft articles
    if article.author_id == user_id and article.status == ArticleStatus.DRAFT:
        return True
    return False


def _can_publish_article(user_role: str) -> bool:
    """Check if user can publish articles."""
    return user_role == "Admin"


def _can_archive_article(user_role: str) -> bool:
    """Check if user can archive articles."""
    return user_role == "Admin"


def _can_delete_article(user_role: str) -> bool:
    """Check if user can delete articles."""
    return user_role == "Admin"


# ==========================================
# Create Article
# ==========================================
def create_article(db: Session, article_data: ArticleCreate, user_id: int) -> KnowledgeArticle:
    slug = _generate_unique_slug(db, article_data.title)

    new_article = KnowledgeArticle(
        title=article_data.title,
        slug=slug,
        summary=article_data.summary,
        content=article_data.content,
        category=article_data.category,
        status=ArticleStatus.DRAFT,
        author_id=user_id,
    )

    db.add(new_article)
    db.commit()
    db.refresh(new_article)

    return new_article


# ==========================================
# Get Articles for User (with RBAC filtering)
# ==========================================
def get_articles_for_user(
    db: Session,
    user_id: int,
    user_role: str,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    category: ArticleCategory | None = None,
    status: ArticleStatus | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> dict:
    query = (
        _base_article_query(db)
        .options(joinedload(KnowledgeArticle.author))
    )

    # Apply RBAC filtering
    if user_role == "Admin":
        # Admin can see all statuses
        if status:
            query = query.filter(KnowledgeArticle.status == status)
    else:
        # Employee/Technician only see published articles
        query = query.filter(KnowledgeArticle.status == ArticleStatus.PUBLISHED)

    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                KnowledgeArticle.title.ilike(search_term),
                KnowledgeArticle.summary.ilike(search_term),
                KnowledgeArticle.content.ilike(search_term),
                KnowledgeArticle.category.ilike(search_term),
            )
        )

    if category:
        query = query.filter(KnowledgeArticle.category == category)

    # Get total count before pagination
    total = query.count()

    # Apply sorting
    sort_column = getattr(KnowledgeArticle, sort_by, KnowledgeArticle.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Apply pagination
    offset = (page - 1) * page_size
    articles = query.offset(offset).limit(page_size).all()

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": [_serialize_article(article) for article in articles],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# ==========================================
# Get Article By ID
# ==========================================
def get_article_by_id(
    db: Session,
    article_id: int,
    user_id: int,
    user_role: str,
) -> KnowledgeArticle:
    article = (
        _base_article_query(db)
        .options(joinedload(KnowledgeArticle.author))
        .filter(KnowledgeArticle.id == article_id)
        .first()
    )

    if not article:
        raise HTTPException(
            status_code=404,
            detail="Article not found",
        )

    # Check view permission
    if not _can_view_article(user_role, article):
        raise HTTPException(
            status_code=404,
            detail="Article not found",
        )

    return article


# ==========================================
# Update Article
# ==========================================
def update_article(
    db: Session,
    article_id: int,
    article_data: ArticleUpdate,
    user_id: int,
    user_role: str,
) -> KnowledgeArticle:

    article = get_article_by_id(db, article_id, user_id, user_role)

    # Check modify permission
    if not _can_modify_article(user_id, user_role, article):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to modify this article"
        )

    # Track changes for potential history
    if article_data.title is not None and article_data.title != article.title:
        article.slug = _generate_unique_slug(db, article_data.title, exclude_id=article.id)
        article.title = article_data.title

    if article_data.summary is not None and article_data.summary != article.summary:
        article.summary = article_data.summary

    if article_data.content is not None and article_data.content != article.content:
        article.content = article_data.content

    if article_data.category is not None and article_data.category != article.category:
        article.category = article_data.category

    db.commit()
    db.refresh(article)

    return article


# ==========================================
# Publish Article
# ==========================================
def publish_article(
    db: Session,
    article_id: int,
    user_id: int,
    user_role: str,
) -> KnowledgeArticle:

    article = get_article_by_id(db, article_id, user_id, user_role)

    if not _can_publish_article(user_role):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to publish articles"
        )

    if article.status == ArticleStatus.PUBLISHED:
        raise HTTPException(
            status_code=400,
            detail="Article is already published"
        )

    article.status = ArticleStatus.PUBLISHED
    article.published_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(article)

    return article


# ==========================================
# Archive Article
# ==========================================
def archive_article(
    db: Session,
    article_id: int,
    user_id: int,
    user_role: str,
) -> KnowledgeArticle:

    article = get_article_by_id(db, article_id, user_id, user_role)

    if not _can_archive_article(user_role):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to archive articles"
        )

    if article.status == ArticleStatus.ARCHIVED:
        raise HTTPException(
            status_code=400,
            detail="Article is already archived"
        )

    article.status = ArticleStatus.ARCHIVED

    db.commit()
    db.refresh(article)

    return article


# ==========================================
# Delete Article (Soft Delete)
# ==========================================
def delete_article(
    db: Session,
    article_id: int,
    user_id: int,
    user_role: str,
) -> dict:

    article = get_article_by_id(db, article_id, user_id, user_role)

    if not _can_delete_article(user_role):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete articles"
        )

    article.is_deleted = True
    article.updated_at = datetime.now(timezone.utc)

    db.commit()

    return {
        "message": "Article deleted successfully"
    }


# ==========================================
# Get Categories (for filter dropdown)
# ==========================================
def get_categories() -> list[str]:
    return [cat.value for cat in ArticleCategory]


# ==========================================
# Get Article by Slug (public endpoint)
# ==========================================
def get_article_by_slug(
    db: Session,
    slug: str,
    user_role: str,
) -> KnowledgeArticle:
    article = (
        _base_article_query(db)
        .options(joinedload(KnowledgeArticle.author))
        .filter(KnowledgeArticle.slug == slug)
        .first()
    )

    if not article:
        raise HTTPException(
            status_code=404,
            detail="Article not found",
        )

    if not _can_view_article(user_role, article):
        raise HTTPException(
            status_code=404,
            detail="Article not found",
        )

    return article