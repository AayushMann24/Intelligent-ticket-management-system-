import { useRef, useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  Download,
  FileText,
  Loader2,
  Paperclip,
  Trash2,
  Upload,
} from "lucide-react";

import useTicketAttachments from "../../hooks/useTicketAttachments";
import type { TicketAttachment } from "../../types/ticket";

// Mirrors the backend `max_upload_size_mb` default for immediate feedback.
const MAX_UPLOAD_SIZE_MB = 10;
const MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024;

const ACCEPTED_FILE_TYPES =
  ".pdf,.jpg,.jpeg,.png,.gif,.webp,.txt,.doc,.docx,.xls,.xlsx,.zip";

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

interface TicketAttachmentsPanelProps {
  ticketId: number;
}

export default function TicketAttachmentsPanel({
  ticketId,
}: TicketAttachmentsPanelProps) {
  const {
    attachments,
    loading,
    error,
    actionError,
    successMessage,
    uploading,
    uploadProgress,
    deletingId,
    reload,
    upload,
    remove,
    download,
  } = useTicketAttachments(ticketId);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [clientError, setClientError] = useState<string | null>(null);

  const handleFileChange = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    // Reset so selecting the same file again still triggers onChange.
    event.target.value = "";

    if (!file) return;

    setClientError(null);

    if (file.size === 0) {
      setClientError("The selected file is empty.");
      return;
    }

    if (file.size > MAX_UPLOAD_SIZE_BYTES) {
      setClientError(
        `File is too large. Maximum size is ${MAX_UPLOAD_SIZE_MB} MB.`
      );
      return;
    }

    await upload(file);
  };

  const banner = clientError ?? actionError;

  return (
    <div>
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-blue-600 p-2 text-white">
            <Paperclip size={20} />
          </div>
          <h3 className="text-xl font-semibold text-slate-900 dark:text-white">
            Attachments
          </h3>
          {attachments.length > 0 && (
            <span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-medium text-slate-700 dark:bg-slate-700 dark:text-slate-200">
              {attachments.length}
            </span>
          )}
        </div>

        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {uploading ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Upload size={16} />
          )}
          {uploading ? "Uploading..." : "Upload"}
        </button>

        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED_FILE_TYPES}
          className="hidden"
          onChange={handleFileChange}
          disabled={uploading}
          data-testid="attachment-file-input"
        />
      </div>

      {uploading && uploadProgress != null && (
        <div
          className="mb-4 h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700"
          role="progressbar"
          aria-valuenow={uploadProgress}
          aria-valuemin={0}
          aria-valuemax={100}
        >
          <div
            className="h-full bg-blue-600 transition-all"
            style={{ width: `${uploadProgress}%` }}
          />
        </div>
      )}

      {banner && (
        <div
          role="alert"
          className="mb-4 flex items-center gap-2 rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-300"
        >
          <AlertCircle size={16} className="flex-shrink-0" />
          {banner}
        </div>
      )}

      {successMessage && !banner && (
        <div
          role="status"
          className="mb-4 flex items-center gap-2 rounded-lg border border-emerald-300 bg-emerald-50 p-3 text-sm text-emerald-700 dark:border-emerald-800 dark:bg-emerald-900/20 dark:text-emerald-300"
        >
          <CheckCircle2 size={16} className="flex-shrink-0" />
          {successMessage}
        </div>
      )}

      {loading ? (
        <div
          role="status"
          className="flex items-center gap-3 text-slate-500 dark:text-slate-400"
        >
          <Loader2 size={18} className="animate-spin" />
          Loading attachments...
        </div>
      ) : error ? (
        <div className="rounded-xl border border-red-300 bg-red-50 p-4 text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-300">
          <p className="flex items-center gap-2 text-sm">
            <AlertCircle size={16} className="flex-shrink-0" />
            {error}
          </p>
          <button
            type="button"
            onClick={reload}
            className="mt-3 rounded-lg bg-red-600 px-4 py-2 text-sm text-white transition hover:bg-red-700"
          >
            Try again
          </button>
        </div>
      ) : attachments.length === 0 ? (
        <p className="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-6 text-center text-sm text-slate-500 dark:border-slate-700 dark:bg-slate-800/50 dark:text-slate-400">
          No attachments yet. Upload a file to add evidence to this ticket.
        </p>
      ) : (
        <ul className="space-y-3">
          {attachments.map((attachment: TicketAttachment) => (
            <li
              key={attachment.id}
              className="flex items-center justify-between gap-4 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="flex min-w-0 items-center gap-3">
                <FileText
                  size={18}
                  className="flex-shrink-0 text-slate-500 dark:text-slate-400"
                />
                <div className="min-w-0">
                  <p className="truncate font-medium text-slate-900 dark:text-white">
                    {attachment.original_filename}
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    {formatFileSize(attachment.file_size)}
                    {attachment.uploader_name
                      ? ` • ${attachment.uploader_name}`
                      : ""}
                    {` • ${new Date(attachment.created_at).toLocaleDateString()}`}
                  </p>
                </div>
              </div>

              <div className="flex flex-shrink-0 items-center gap-2">
                <button
                  type="button"
                  onClick={() => download(attachment)}
                  aria-label={`Download ${attachment.original_filename}`}
                  className="rounded-lg p-2 text-slate-600 transition hover:bg-slate-200 dark:text-slate-300 dark:hover:bg-slate-700"
                >
                  <Download size={16} />
                </button>
                <button
                  type="button"
                  onClick={() => remove(attachment.id)}
                  disabled={deletingId === attachment.id}
                  aria-label={`Delete ${attachment.original_filename}`}
                  className="rounded-lg p-2 text-red-600 transition hover:bg-red-100 disabled:cursor-not-allowed disabled:opacity-50 dark:hover:bg-red-500/20"
                >
                  {deletingId === attachment.id ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <Trash2 size={16} />
                  )}
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
