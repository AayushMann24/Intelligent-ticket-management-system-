from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class ArticleStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class ArticleCategory(str, Enum):
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    NETWORK = "Network"
    SECURITY = "Security"
    ACCOUNT = "Account"
    TROUBLESHOOTING = "Troubleshooting"
    PROCEDURES = "Procedures"
    OTHER = "Other"


# -----------------------------
# Create Article
# -----------------------------
class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    summary: str = Field(..., min_length=10, max_length=500)
    content: str = Field(..., min_length=20)
    category: ArticleCategory = ArticleCategory.OTHER


# -----------------------------
# Update Article (Partial)
# -----------------------------
class ArticleUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=255)
    summary: str | None = Field(None, min_length=10, max_length=500)
    content: str | None = Field(None, min_length=20)
    category: ArticleCategory | None = None


# -----------------------------
# Publish Article
# -----------------------------
class ArticlePublish(BaseModel):
    pass


# -----------------------------
# Archive Article
# -----------------------------
class ArticleArchive(BaseModel):
    pass


# -----------------------------
# Pagination
# -----------------------------
class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20

    class Config:
        validate_assignment = True


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


# -----------------------------
# Article Response
# -----------------------------
class ArticleResponse(BaseModel):
    id: int
    title: str
    slug: str
    summary: str
    content: str
    category: str
    status: str
    author_id: int
    author_name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    published_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# -----------------------------
# Article List Response (lighter)
# -----------------------------
class ArticleListResponse(BaseModel):
    id: int
    title: str
    slug: str
    summary: str
    category: str
    status: str
    author_id: int
    author_name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    published_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# -----------------------------
# Search/Filter Parameters
# -----------------------------
class ArticleFilterParams(BaseModel):
    search: str | None = None
    category: ArticleCategory | None = None
    status: ArticleStatus | None = None
    sort_by: str = "created_at"
    sort_order: str = "desc"