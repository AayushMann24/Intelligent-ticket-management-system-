import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Calendar, User, Tag, BookOpen } from "lucide-react";
import { useReducedMotion } from "../hooks/useReducedMotion";
import { getKnowledgeArticleBySlug } from "../services/knowledgeService";
import type { ArticleResponse } from "../types/knowledge";

import Loader from "../components/common/Loader";
import ErrorState from "../components/analytics/ErrorState";
import EmptyState from "../components/analytics/EmptyState";

export default function ArticleDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const reducedMotion = useReducedMotion();

  const [article, setArticle] = useState<ArticleResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug) return;

    const fetchArticle = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getKnowledgeArticleBySlug(slug);
        setArticle(data);
      } catch {
        setError("Article not found or you don't have permission to view it.");
      } finally {
        setLoading(false);
      }
    };

    fetchArticle();
  }, [slug]);

  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return "";
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  if (loading) {
    return (
      <motion.div
        className="flex-1 p-6 flex items-center justify-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <Loader size="lg" text="Loading article..." />
      </motion.div>
    );
  }

  if (error) {
    return (
      <motion.div
        className="flex-1 p-6 flex items-center justify-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <ErrorState
          message={error}
          onRetry={() => navigate("/knowledge")}
        />
      </motion.div>
    );
  }

  if (!article) {
    return (
      <motion.div
        className="flex-1 p-6 flex items-center justify-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <EmptyState
          icon={<BookOpen size={64} />}
          message="The article you're looking for doesn't exist or has been removed."
        />
      </motion.div>
    );
  }

  const statusColors: Record<string, string> = {
    PUBLISHED: "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400",
    DRAFT: "bg-yellow-100 text-yellow-700 dark:bg-yellow-500/20 dark:text-yellow-400",
    ARCHIVED: "bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300",
  };

  return (
    <motion.div
      className="flex-1 p-6 max-w-4xl mx-auto space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      {/* Back Button */}
      <motion.button
        onClick={() => navigate("/knowledge")}
        className="flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2 text-slate-700 transition-colors hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
        whileHover={reducedMotion ? {} : { x: -4 }}
        whileTap={reducedMotion ? {} : { scale: 0.98 }}
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.2 }}
      >
        <ArrowLeft size={18} />
        Back to Knowledge Base
      </motion.button>

      {/* Article Header */}
      <motion.div
        className="space-y-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
        <motion.div className="flex flex-wrap items-center gap-2">
          <motion.span
            className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${statusColors[article.status] || "bg-slate-100 text-slate-700"}`}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: "spring", stiffness: 400, damping: 25 }}
          >
            {article.status}
          </motion.span>
          <motion.span
            className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: "spring", stiffness: 400, damping: 25, delay: 0.05 }}
          >
            {article.category}
          </motion.span>
        </motion.div>

        <motion.h1
          className="text-3xl font-bold text-slate-900 dark:text-white"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.15 }}
        >
          {article.title}
        </motion.h1>

        <motion.div
          className="flex flex-wrap items-center gap-4 text-sm text-slate-500 dark:text-slate-400"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2, delay: 0.2 }}
        >
          <span className="flex items-center gap-1">
            <User size={14} />
            {article.author_name}
          </span>
          <span className="flex items-center gap-1">
            <Calendar size={14} />
            Published: {formatDate(article.published_at)}
          </span>
          {article.updated_at !== article.published_at && article.updated_at && (
            <span className="flex items-center gap-1">
              <Calendar size={14} />
              Updated: {formatDate(article.updated_at)}
            </span>
          )}
        </motion.div>
      </motion.div>

      {/* Article Summary */}
      <motion.div
        className="prose prose-slate dark:prose-invert max-w-none p-5 bg-slate-50 rounded-xl border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.25 }}
      >
        <p className="text-slate-700 dark:text-slate-300 leading-relaxed">{article.summary}</p>
      </motion.div>

      {/* Article Content */}
      <motion.div
        className="prose prose-slate dark:prose-invert max-w-none"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.3 }}
      >
        <div className="text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-wrap">
          {article.content}
        </div>
      </motion.div>

      {/* Meta Info */}
      <motion.div
        className="rounded-xl border border-slate-200 bg-slate-50 p-5 dark:border-slate-700 dark:bg-slate-800/50"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.35 }}
      >
        <h3 className="mb-4 font-semibold text-slate-900 dark:text-white flex items-center gap-2">
          <Tag size={20} />
          Article Information
        </h3>
        <dl className="grid gap-3 sm:grid-cols-2">
          <div>
            <dt className="text-sm text-slate-500 dark:text-slate-400">Article ID</dt>
            <dd className="font-mono text-slate-900 dark:text-white">#{article.id}</dd>
          </div>
          <div>
            <dt className="text-sm text-slate-500 dark:text-slate-400">Slug</dt>
            <dd className="font-mono text-slate-900 dark:text-white">{article.slug}</dd>
          </div>
          <div>
            <dt className="text-sm text-slate-500 dark:text-slate-400">Category</dt>
            <dd className="font-medium text-slate-900 dark:text-white">{article.category}</dd>
          </div>
          <div>
            <dt className="text-sm text-slate-500 dark:text-slate-400">Status</dt>
            <dd className="font-medium text-slate-900 dark:text-white capitalize">{article.status.toLowerCase()}</dd>
          </div>
          <div className="sm:col-span-2">
            <dt className="text-sm text-slate-500 dark:text-slate-400">Author</dt>
            <dd className="font-medium text-slate-900 dark:text-white">{article.author_name}</dd>
          </div>
          <div className="sm:col-span-2">
            <dt className="text-sm text-slate-500 dark:text-slate-400">Published</dt>
            <dd className="font-medium text-slate-900 dark:text-white">{formatDate(article.published_at)}</dd>
          </div>
        </dl>
      </motion.div>
    </motion.div>
  );
}