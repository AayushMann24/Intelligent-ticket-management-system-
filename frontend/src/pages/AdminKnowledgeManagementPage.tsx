import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Search, Plus, Edit, Trash2, Eye, Save, X, AlertTriangle, ChevronLeft, ChevronRight, BookOpen } from "lucide-react";
import { useAuth } from "../context/useAuth";
import { useReducedMotion } from "../hooks/useReducedMotion";
import { getKnowledgeArticles, getKnowledgeCategories, createKnowledgeArticle, updateKnowledgeArticle, publishKnowledgeArticle, archiveKnowledgeArticle, deleteKnowledgeArticle } from "../services/knowledgeService";
import type { KnowledgeListParams, KnowledgeListResponse, ArticleCreate, ArticleUpdate, ArticleCategoryValue } from "../types/knowledge";

import Button from "../components/common/Button";
import Input from "../components/common/Input";
import Select from "../components/common/Select";
import Modal from "../components/common/Modal";
import Loader from "../components/common/Loader";
import EmptyState from "../components/analytics/EmptyState";
import ErrorState from "../components/analytics/ErrorState";

const ITEMS_PER_PAGE = 10;

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

export default function AdminKnowledgeManagementPage() {
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
  const [selectedStatus, setSelectedStatus] = useState<string>("");
  const [categories, setCategories] = useState<{ value: string; label: string }[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingArticle, setEditingArticle] = useState<KnowledgeListResponse["items"][0] | null>(null);
  const [deletingArticle, setDeletingArticle] = useState<KnowledgeListResponse["items"][0] | null>(null);
  const [formData, setFormData] = useState<ArticleCreate>({
    title: "",
    summary: "",
    content: "",
    category: "Other",
  });
  const [formError, setFormError] = useState<string | null>(null);
  const [formLoading, setFormLoading] = useState(false);

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
        status: selectedStatus || undefined,
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
  }, [search, selectedCategory, selectedStatus]);

  // Initialize categories on mount
  /* eslint-disable react-hooks/set-state-in-effect -- Initialization effect is a legitimate pattern */
  useEffect(() => {
    loadCategories();
  }, [loadCategories]);

  // Load articles when dependencies change
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

  const handleStatusChange = (status: string) => {
    setSelectedStatus(status);
    loadArticles(1);
  };

  const handleSearchChange = (value: string) => {
    setSearch(value);
  };

  const handleClearFilters = () => {
    setSearch("");
    setSelectedCategory("");
    setSelectedStatus("");
    loadArticles(1);
  };

  const hasActiveFilters = search || selectedCategory || selectedStatus;

  const openCreateModal = () => {
    setFormData({
      title: "",
      summary: "",
      content: "",
      category: "Other",
    });
    setFormError(null);
    setShowCreateModal(true);
  };

  const openEditModal = (article: KnowledgeListResponse["items"][0]) => {
    setFormData({
      title: article.title,
      summary: article.summary,
      content: article.content,
      category: article.category as ArticleCategoryValue,
    });
    setEditingArticle(article);
    setFormError(null);
    setShowCreateModal(true);
  };

  const closeCreateModal = () => {
    setShowCreateModal(false);
    setEditingArticle(null);
    setFormData({
      title: "",
      summary: "",
      content: "",
      category: "Other",
    });
    setFormError(null);
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setFormLoading(true);

    try {
      if (editingArticle) {
        const updateData: ArticleUpdate = {
          title: formData.title,
          summary: formData.summary,
          content: formData.content,
          category: formData.category,
        };
        await updateKnowledgeArticle(editingArticle.id, updateData);
      } else {
        await createKnowledgeArticle(formData);
      }
      closeCreateModal();
      loadArticles(currentPage);
    } catch {
      setFormError("Failed to save article. Please try again.");
    } finally {
      setFormLoading(false);
    }
  };

  const handlePublish = async (article: KnowledgeListResponse["items"][0]) => {
    try {
      await publishKnowledgeArticle(article.id);
      loadArticles(currentPage);
    } catch {
      setError("Failed to publish article. Please try again.");
    }
  };

  const handleArchive = async (article: KnowledgeListResponse["items"][0]) => {
    try {
      await archiveKnowledgeArticle(article.id);
      loadArticles(currentPage);
    } catch {
      setError("Failed to archive article. Please try again.");
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deletingArticle) return;
    try {
      await deleteKnowledgeArticle(deletingArticle.id);
      setDeletingArticle(null);
      loadArticles(currentPage);
    } catch {
      setError("Failed to delete article. Please try again.");
      setDeletingArticle(null);
    }
  };

  const handleDelete = (article: KnowledgeListResponse["items"][0]) => {
    setDeletingArticle(article);
  };

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

  const truncate = (str: string, length: number) => {
    if (str.length <= length) return str;
    return str.slice(0, length) + "...";
  };

  if (!isAdmin) {
    return (
      <motion.div
        className="flex-1 p-6 flex items-center justify-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <ErrorState
          message="You don't have permission to access this page."
        />
      </motion.div>
    );
  }

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
            Knowledge Management
          </motion.h1>
          <motion.p
            className="mt-1 text-slate-500 dark:text-slate-400"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2, delay: 0.05 }}
          >
            Create, edit, and manage knowledge base articles
          </motion.p>
        </div>

        <motion.button
          onClick={openCreateModal}
          className="flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-2.5 font-semibold text-white transition-all duration-300 hover:bg-blue-700 hover:shadow-lg"
          whileHover={reducedMotion ? {} : { scale: 1.02, boxShadow: "0 10px 25px -5px rgba(37, 99, 235, 0.4)" }}
          whileTap={reducedMotion ? {} : { scale: 0.98 }}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          <Plus size={18} />
          New Article
        </motion.button>
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

          <Select
            value={selectedStatus}
            onValueChange={handleStatusChange}
            placeholder="All Status"
            options={[
              { value: "", label: "All Status" },
              { value: "DRAFT", label: "Draft" },
              { value: "PUBLISHED", label: "Published" },
              { value: "ARCHIVED", label: "Archived" },
            ]}
            className="w-40"
            aria-label="Filter by status"
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

      {/* Articles Table */}
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
            title="No Articles Found"
            icon={<BookOpen size={64} />}
            message={search || selectedCategory || selectedStatus
              ? "Try adjusting your search or filters"
              : "No articles yet. Create your first article!"}
            action={
              <Button onClick={openCreateModal} variant="primary">
                <Plus size={18} className="mr-2" />
                Create Article
              </Button>
            }
          />
        )}

        {!loading && !error && articles.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-100 dark:bg-slate-800">
                <tr className="text-left text-sm font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300">
                  <th className="px-6 py-4">Title</th>
                  <th className="px-6 py-4">Category</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Author</th>
                  <th className="px-6 py-4">Published</th>
                  <th className="px-6 py-4 text-center">Actions</th>
                </tr>
              </thead>
              <motion.tbody variants={containerVariants} initial="initial" animate="animate" exit="exit">
                {articles.map((article) => (
                  <motion.tr
                    key={article.id}
                    className="border-t border-slate-200 transition-colors hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800/40"
                    variants={cardVariants}
                  >
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-medium text-slate-900 dark:text-white truncate max-w-xs">
                          {article.title}
                        </p>
                        <p className="text-sm text-slate-500 dark:text-slate-400 truncate max-w-xs mt-1">
                          {truncate(article.summary, 80)}
                        </p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400">
                        {article.category}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${statusColors[article.status] || "bg-slate-100 text-slate-700"}`}>
                        {article.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-700 dark:text-slate-300">
                      {article.author_name}
                    </td>
                    <td className="px-6 py-4 text-slate-600 dark:text-slate-400">
                      {formatDate(article.published_at)}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-center gap-2">
                        <motion.button
                          onClick={() => navigate(`/knowledge/${article.slug}`)}
                          className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-blue-600 dark:hover:bg-slate-700 dark:hover:text-blue-400"
                          whileHover={reducedMotion ? {} : { scale: 1.1 }}
                          whileTap={reducedMotion ? {} : { scale: 0.9 }}
                          aria-label="View article"
                        >
                          <Eye size={18} />
                        </motion.button>

                        <motion.button
                          onClick={() => openEditModal(article)}
                          className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-green-600 dark:hover:bg-slate-700 dark:hover:text-green-400"
                          whileHover={reducedMotion ? {} : { scale: 1.1 }}
                          whileTap={reducedMotion ? {} : { scale: 0.9 }}
                          aria-label="Edit article"
                        >
                          <Edit size={18} />
                        </motion.button>

                        {article.status === "DRAFT" && (
                          <motion.button
                            onClick={() => handlePublish(article)}
                            className="rounded-lg p-2 text-green-600 transition-colors hover:bg-green-50 dark:hover:bg-green-500/10"
                            whileHover={reducedMotion ? {} : { scale: 1.1 }}
                            whileTap={reducedMotion ? {} : { scale: 0.9 }}
                            aria-label="Publish article"
                          >
                            <Save size={18} />
                          </motion.button>
                        )}

                        {article.status === "PUBLISHED" && (
                          <motion.button
                            onClick={() => handleArchive(article)}
                            className="rounded-lg p-2 text-yellow-600 transition-colors hover:bg-yellow-50 dark:hover:bg-yellow-500/10"
                            whileHover={reducedMotion ? {} : { scale: 1.1 }}
                            whileTap={reducedMotion ? {} : { scale: 0.9 }}
                            aria-label="Archive article"
                          >
                            <AlertTriangle size={18} />
                          </motion.button>
                        )}

                        <motion.button
                          onClick={() => handleDelete(article)}
                          className="rounded-lg p-2 text-red-600 transition-colors hover:bg-red-50 dark:hover:bg-red-500/10"
                          whileHover={reducedMotion ? {} : { scale: 1.1 }}
                          whileTap={reducedMotion ? {} : { scale: 0.9 }}
                          aria-label="Delete article"
                        >
                          <Trash2 size={18} />
                        </motion.button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </motion.tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <motion.div
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

      {/* Create/Edit Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <Modal
            isOpen={showCreateModal}
            onClose={closeCreateModal}
            title={editingArticle ? "Edit Article" : "Create Article"}
            description={editingArticle ? "Update the article details." : "Create a new knowledge base article."}
            size="lg"
          >
            <form onSubmit={handleFormSubmit}>
              <div className="space-y-6">
                <Input
                  label="Title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="Enter article title..."
                  required
                  error={formError || undefined}
                />

                <Input
                  label="Summary"
                  value={formData.summary}
                  onChange={(e) => setFormData({ ...formData, summary: e.target.value })}
                  placeholder="Brief summary of the article..."
                  required
                />

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
                    Content
                  </label>
                  <textarea
                    value={formData.content}
                    onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                    placeholder="Write your article content here (Markdown supported)..."
                    rows={10}
                    className="w-full rounded-xl border border-slate-300 bg-slate-50 p-3 text-slate-900 outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:focus:ring-blue-500/20"
                    required
                  />
                </div>

                <Select
                  label="Category"
                  value={formData.category}
                  onValueChange={(value: string) => setFormData({ ...formData, category: value as ArticleCategoryValue })}
                  placeholder="Select category"
                  options={categories.map((cat) => ({ value: cat.value, label: cat.label }))}
                />
              </div>

              <div className="mt-8 flex justify-end gap-4 border-t border-slate-200 pt-6 dark:border-slate-700">
                <Button
                  type="button"
                  onClick={closeCreateModal}
                  variant="outline"
                >
                  <X size={18} className="mr-2" />
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={formLoading}
                >
                  {formLoading ? "Saving..." : editingArticle ? "Update Article" : "Create Article"}
                </Button>
              </div>
            </form>
          </Modal>
        )}
      </AnimatePresence>

      {/* Delete Confirm Modal */}
      <AnimatePresence>
        {deletingArticle && (
          <Modal
            isOpen={true}
            onClose={() => setDeletingArticle(null)}
            title="Delete Article"
            description="This action cannot be undone."
            size="sm"
          >
            <div className="space-y-4">
              <p className="text-slate-700 dark:text-slate-300">
                Are you sure you want to permanently delete this article?
              </p>
              <div className="rounded-xl border border-red-200 bg-red-50 p-4 dark:border-red-900 dark:bg-red-500/10">
                <p className="text-sm text-slate-500 dark:text-slate-400">Article</p>
                <h3 className="mt-1 font-semibold text-slate-900 dark:text-white">{deletingArticle.title}</h3>
              </div>
              <p className="text-sm text-yellow-700 dark:text-yellow-300">
                ⚠ This article and all associated information will be permanently removed.
              </p>
            </div>
            <div className="flex justify-end gap-3 border-t border-slate-200 pt-5 dark:border-slate-800">
              <Button onClick={() => setDeletingArticle(null)} variant="outline">
                <X size={18} className="mr-2" />
                Cancel
              </Button>
              <Button onClick={handleDeleteConfirm} variant="primary" className="bg-red-600 hover:bg-red-700">
                <Trash2 size={18} className="mr-2" />
                Delete Article
              </Button>
            </div>
          </Modal>
        )}
      </AnimatePresence>
    </motion.div>
  );
}