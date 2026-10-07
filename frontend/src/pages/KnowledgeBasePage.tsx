import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { Search, BookOpen, FileText, ChevronLeft, ChevronRight } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../context/useAuth";
import { useReducedMotion } from "../hooks/useReducedMotion";
import { getKnowledgeArticles, getKnowledgeCategories } from "../services/knowledgeService";
import type { KnowledgeListParams, KnowledgeListResponse } from "../types/knowledge";

import Select from "../components/common/Select";
import Loader from "../components/common/Loader";
import EmptyState from "../components/analytics/EmptyState";
import ErrorState from "../components/analytics/ErrorState";

const ITEMS_PER_PAGE = 12;

const cardVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.3, ease: "easeOut" },
};

const containerVariants = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: { staggerChildren: 0.05, delayChildren: 0.1 } },
  exit: { opacity: 0 },
};

export default function KnowledgeBasePage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const reducedMotion = useReducedMotion();
  const isAdmin = user?.role === "Admin";

  const [articles, setArticles] = useState<KnowledgeListResponse["items"]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalPages, setTotalPages] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [categories, setCategories] = useState<{ value: string; label: string }[]>([]);

  const loadCategories = useCallback(async () => {
    try {
      const cats = await getKnowledgeCategories();
      setCategories(cats);
    } catch {
      // Categories failed to load - not critical
    }
  }, []);

  const loadArticles = useCallback(async (page: number = 1) => {
    setLoading(true);
    setError(null);
    try {
      const params: KnowledgeListParams = {
        page,
        page_size: ITEMS_PER_PAGE,
        search: search || undefined,
        category: selectedCategory || undefined,
        sort_by: "created_at",
        sort_order: "desc",
      };

      const response: KnowledgeListResponse = await getKnowledgeArticles(params);
      setArticles(response.items);
      setCurrentPage(response.page);
      setTotalPages(response.total_pages);
    } catch {
      setError("Failed to load articles. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [search, selectedCategory]);

  /* eslint-disable react-hooks/set-state-in-effect -- Initialization effect is a legitimate pattern */
  useEffect(() => {
    loadCategories();
  }, [loadCategories]);

  useEffect(() => {
    loadArticles(1);
  }, [loadArticles]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const handlePageChange = (page: number) => {
    if (page < 1 || page > totalPages) return;
    loadArticles(page);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadArticles(1);
  };

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category);
    loadArticles(1);
  };

  const handleSearchChange = (value: string) => {
    setSearch(value);
  };

  const handleClearFilters = () => {
    setSearch("");
    setSelectedCategory("");
    loadArticles(1);
  };

  const hasActiveFilters = search || selectedCategory;

  const statusColors: Record<string, string> = {
    PUBLISHED: "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400",
    DRAFT: "bg-yellow-100 text-yellow-700 dark:bg-yellow-500/20 dark:text-yellow-400",
    ARCHIVED: "bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300",
  };

  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return "";
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <motion.div
      className="flex-1 p-6 space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      {/* Header */}
      <motion.div
        className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div>
          <motion.h1
            className="text-2xl font-bold text-slate-900 dark:text-white"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            Knowledge Base
          </motion.h1>
          <motion.p
            className="mt-1 text-slate-500 dark:text-slate-400"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, delay: 0.05 }}
          >
            Search and browse help articles and documentation
          </motion.p>
        </div>

        {isAdmin && (
          <motion.button
            onClick={() => navigate("/knowledge-management")}
            className="flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-2.5 font-semibold text-white transition-all duration-300 hover:bg-blue-700 hover:shadow-lg"
            whileHover={reducedMotion ? {} : { scale: 1.02, boxShadow: "0 10px 25px -5px rgba(37, 99, 235, 0.4)" }}
            whileTap={reducedMotion ? {} : { scale: 0.98 }}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: 0.1 }}
          >
            <FileText size={18} />
            Manage Articles
          </motion.button>
        )}
      </motion.div>

      {/* Search & Filters */}
      <motion.div
        className="flex flex-col sm:flex-row gap-4"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
        <form onSubmit={handleSearch} className="flex-1 relative">
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
            <Search size={18} />
          </div>
          <motion.input
            type="text"
            placeholder="Search articles..."
            value={search}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="w-full rounded-xl border border-slate-300 bg-slate-50 py-2.5 pl-10 pr-4 text-slate-900 outline-none transition-all placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:placeholder:text-slate-400 dark:focus:ring-blue-500/20"
            whileFocus={reducedMotion ? {} : { scale: 1.01 }}
          />
        </form>

        <motion.div className="flex items-center gap-3">
          <Select
            value={selectedCategory}
            onValueChange={handleCategoryChange}
            placeholder="All Categories"
            options={[
              { value: "", label: "All Categories" },
              ...categories.map((cat) => ({ value: cat.value, label: cat.label })),
            ]}
            className="w-48"
            aria-label="Filter by category"
          />

          {hasActiveFilters && (
            <motion.button
              onClick={handleClearFilters}
              className="px-4 py-2 rounded-lg text-sm text-cyan-600 hover:text-cyan-700 dark:text-cyan-400 dark:hover:text-cyan-300 font-medium"
              whileHover={reducedMotion ? {} : { scale: 1.02 }}
            >
              Clear filters
            </motion.button>
          )}
        </motion.div>
      </motion.div>

      {/* Articles Grid */}
      <motion.div
        className="rounded-xl border border-slate-300 bg-white dark:border-slate-700 dark:bg-slate-900 overflow-hidden"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.2 }}
      >
        {loading && (
          <motion.div
            className="p-8 text-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            <Loader size="lg" text="Loading articles..." />
          </motion.div>
        )}

        {!loading && error && (
          <ErrorState
            message={error}
            onRetry={() => loadArticles(currentPage)}
          />
        )}

        {!loading && !error && articles.length === 0 && (
          <EmptyState
            icon={<BookOpen size={64} />}
            message={search || selectedCategory
              ? "Try adjusting your search or filters"
              : "No published articles available yet"}
          />
        )}

        {!loading && !error && articles.length > 0 && (
          <motion.div
            className="divide-y divide-slate-200 dark:divide-slate-700"
            variants={containerVariants}
            initial="initial"
            animate="animate"
            exit="exit"
          >
            {articles.map((article) => (
              <motion.article
                key={article.id}
                className="p-5 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer"
                onClick={() => navigate(`/knowledge/${article.slug}`)}
                variants={cardVariants}
                whileHover={reducedMotion ? {} : { x: 4 }}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <motion.div className="flex items-center gap-2 mb-2">
                      <motion.span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[article.status] || "bg-slate-100 text-slate-700"}`}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ type: "spring", stiffness: 400, damping: 25 }}
                      >
                        {article.status}
                      </motion.span>
                      <motion.span
                        className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400"
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ type: "spring", stiffness: 400, damping: 25, delay: 0.05 }}
                      >
                        {article.category}
                      </motion.span>
                    </motion.div>

                    <motion.h3
                      className="text-lg font-semibold text-slate-900 dark:text-white truncate mb-1"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.2, delay: 0.1 }}
                    >
                      {article.title}
                    </motion.h3>

                    <motion.p
                      className="text-slate-600 dark:text-slate-400 line-clamp-2 text-sm"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.2, delay: 0.15 }}
                    >
                      {article.summary}
                    </motion.p>

                    <motion.div
                      className="flex items-center gap-4 mt-3 text-xs text-slate-500 dark:text-slate-400"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.2, delay: 0.2 }}
                    >
                      <span className="flex items-center gap-1">
                        <FileText size={14} />
                        {article.author_name}
                      </span>
                      <span className="flex items-center gap-1">
                        <span>{formatDate(article.published_at)}</span>
                      </span>
                    </motion.div>
                  </div>

                  <motion.div
                    className="flex-shrink-0 text-slate-400"
                    initial={{ opacity: 0, x: 10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.2, delay: 0.25 }}
                  >
                    <BookOpen size={20} />
                  </motion.div>
                </div>
              </motion.article>
            ))}

            {/* Pagination */}
            {totalPages > 1 && (
              <motion.div
                key="pagination"
                className="flex items-center justify-center gap-2 px-4 py-4 border-t border-slate-200 dark:border-slate-700"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.2 }}
              >
                <motion.button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${currentPage === 1 ? "text-slate-400 cursor-not-allowed" : "text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"}`}
                  whileHover={reducedMotion || currentPage === 1 ? {} : { scale: 1.02 }}
                  whileTap={reducedMotion || currentPage === 1 ? {} : { scale: 0.98 }}
                >
                  <ChevronLeft size={16} />
                </motion.button>

                <motion.span
                  key={currentPage}
                  className="px-3 text-sm text-slate-600 dark:text-slate-400"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ type: "spring", stiffness: 400, damping: 25 }}
                >
                  Page {currentPage} of {totalPages}
                </motion.span>

                <motion.button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage >= totalPages}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${currentPage >= totalPages ? "text-slate-400 cursor-not-allowed" : "text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"}`}
                  whileHover={reducedMotion || currentPage >= totalPages ? {} : { scale: 1.02 }}
                  whileTap={reducedMotion || currentPage >= totalPages ? {} : { scale: 0.98 }}
                >
                  <ChevronRight size={16} />
                </motion.button>
              </motion.div>
            )}
          </motion.div>
        )}
      </motion.div>
    </motion.div>
  );
}