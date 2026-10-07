import api from "./api";
import type { ArticleResponse, ArticleCreate, ArticleUpdate, ArticleCategoryOption } from "../types/knowledge";

export interface KnowledgeListParams {
  page?: number;
  page_size?: number;
  search?: string;
  category?: string;
  status?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}

export interface KnowledgeListResponse {
  items: ArticleResponse[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ======================================
// Get Categories
// ======================================
export async function getKnowledgeCategories(): Promise<ArticleCategoryOption[]> {
  const response = await api.get<ArticleCategoryOption[]>("/knowledge/categories");
  return response.data;
}

// ======================================
// Create Article (Admin only)
// ======================================
export async function createKnowledgeArticle(
  data: ArticleCreate
): Promise<ArticleResponse> {
  const response = await api.post<ArticleResponse>("/knowledge/", data);
  return response.data;
}

// ======================================
// Get Articles (with pagination, search, filter)
// ======================================
export async function getKnowledgeArticles(
  params: KnowledgeListParams = {}
): Promise<KnowledgeListResponse> {
  const searchParams = new URLSearchParams();

  if (params.page) searchParams.append("page", params.page.toString());
  if (params.page_size) searchParams.append("page_size", params.page_size.toString());
  if (params.search) searchParams.append("search", params.search);
  if (params.category) searchParams.append("category", params.category);
  if (params.status) searchParams.append("status", params.status);
  if (params.sort_by) searchParams.append("sort_by", params.sort_by);
  if (params.sort_order) searchParams.append("sort_order", params.sort_order);

  const response = await api.get<KnowledgeListResponse>(`/knowledge/?${searchParams.toString()}`);
  return response.data;
}

// ======================================================
// Get Article By ID
// ======================================================
export async function getKnowledgeArticle(articleId: number): Promise<ArticleResponse> {
  const response = await api.get<ArticleResponse>(`/knowledge/${articleId}`);
  return response.data;
}

// ======================================================
// Get Article By Slug
// ======================================================
export async function getKnowledgeArticleBySlug(slug: string): Promise<ArticleResponse> {
  const response = await api.get<ArticleResponse>(`/knowledge/slug/${slug}`);
  return response.data;
}

// ======================================================
// Update Article
// ======================================================
export async function updateKnowledgeArticle(
  articleId: number,
  data: ArticleUpdate
): Promise<ArticleResponse> {
  const response = await api.put<ArticleResponse>(`/knowledge/${articleId}`, data);
  return response.data;
}

// ======================================================
// Publish Article (Admin only)
// ======================================================
export async function publishKnowledgeArticle(articleId: number): Promise<ArticleResponse> {
  const response = await api.post<ArticleResponse>(`/knowledge/${articleId}/publish`, {});
  return response.data;
}

// ======================================================
// Archive Article (Admin only)
// ======================================================
export async function archiveKnowledgeArticle(articleId: number): Promise<ArticleResponse> {
  const response = await api.post<ArticleResponse>(`/knowledge/${articleId}/archive`, {});
  return response.data;
}

// ======================================================
// Delete Article (Admin only)
// ======================================================
export async function deleteKnowledgeArticle(articleId: number): Promise<{ message: string }> {
  const response = await api.delete<{ message: string }>(`/knowledge/${articleId}`);
  return response.data;
}