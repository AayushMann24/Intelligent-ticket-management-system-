export const ArticleStatus = {
  DRAFT: "DRAFT",
  PUBLISHED: "PUBLISHED",
  ARCHIVED: "ARCHIVED",
} as const;

export type ArticleStatusValue = typeof ArticleStatus[keyof typeof ArticleStatus];

export const ArticleCategory = {
  HARDWARE: "Hardware",
  SOFTWARE: "Software",
  NETWORK: "Network",
  SECURITY: "Security",
  ACCOUNT: "Account",
  TROUBLESHOOTING: "Troubleshooting",
  PROCEDURES: "Procedures",
  OTHER: "Other",
} as const;

export type ArticleCategoryValue = typeof ArticleCategory[keyof typeof ArticleCategory];

export interface ArticleResponse {
  id: number;
  title: string;
  slug: string;
  summary: string;
  content: string;
  category: string;
  status: string;
  author_id: number;
  author_name: string | null;
  created_at: string | null;
  updated_at: string | null;
  published_at: string | null;
}

export interface ArticleListResponse {
  id: number;
  title: string;
  slug: string;
  summary: string;
  category: string;
  status: string;
  author_id: number;
  author_name: string | null;
  created_at: string | null;
  updated_at: string | null;
  published_at: string | null;
}

export interface ArticleCreate {
  title: string;
  summary: string;
  content: string;
  category: ArticleCategoryValue;
}

export interface ArticleUpdate {
  title?: string;
  summary?: string;
  content?: string;
  category?: ArticleCategoryValue;
}

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

export interface ArticleCategoryOption {
  value: string;
  label: string;
}