import { useCallback, useEffect, useRef, useState } from "react";

import {
  getAttachments,
  uploadAttachment,
  downloadAttachment,
  deleteAttachment,
} from "../services/ticketService";
import type { TicketAttachment } from "../types/ticket";

interface ApiErrorLike {
  response?: {
    status?: number;
    data?: { detail?: unknown };
  };
}

function getErrorMessage(error: unknown, fallback: string): string {
  const response = (error as ApiErrorLike)?.response;
  const status = response?.status;
  const detail = response?.data?.detail;

  // Backend messages for attachment actions are safe to surface.
  if (typeof detail === "string" && detail.length > 0) {
    return detail;
  }

  switch (status) {
    case 403:
      return "You are not allowed to perform this action.";
    case 404:
      return "The attachment could not be found.";
    case 413:
      return "The file is too large.";
    case 415:
      return "That file type is not supported.";
    default:
      return fallback;
  }
}

export interface UseTicketAttachmentsResult {
  attachments: TicketAttachment[];
  loading: boolean;
  error: string | null;
  actionError: string | null;
  successMessage: string | null;
  uploading: boolean;
  uploadProgress: number | null;
  deletingId: number | null;
  reload: () => Promise<void>;
  upload: (file: File) => Promise<boolean>;
  remove: (attachmentId: number) => Promise<boolean>;
  download: (attachment: TicketAttachment) => Promise<void>;
}

export default function useTicketAttachments(
  ticketId: number
): UseTicketAttachmentsResult {
  const [attachments, setAttachments] = useState<TicketAttachment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  // Guards prevent accidental duplicate requests even before React re-renders.
  const uploadingRef = useRef(false);
  const deletingRef = useRef(false);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await getAttachments(ticketId);
      setAttachments(data.items);
    } catch (err) {
      setError(
        getErrorMessage(err, "Unable to load attachments. Please try again.")
      );
    } finally {
      setLoading(false);
    }
  }, [ticketId]);

  useEffect(() => {
    reload();
  }, [reload]);

  const upload = useCallback(
    async (file: File): Promise<boolean> => {
      if (uploadingRef.current) return false;

      uploadingRef.current = true;
      setUploading(true);
      setUploadProgress(0);
      setActionError(null);
      setSuccessMessage(null);

      try {
        await uploadAttachment(ticketId, file, setUploadProgress);
        await reload();
        setSuccessMessage("Attachment uploaded.");
        return true;
      } catch (err) {
        setActionError(
          getErrorMessage(err, "Upload failed. Please try again.")
        );
        return false;
      } finally {
        uploadingRef.current = false;
        setUploading(false);
        setUploadProgress(null);
      }
    },
    [ticketId, reload]
  );

  const remove = useCallback(
    async (attachmentId: number): Promise<boolean> => {
      if (deletingRef.current) return false;

      deletingRef.current = true;
      setDeletingId(attachmentId);
      setActionError(null);
      setSuccessMessage(null);

      try {
        await deleteAttachment(ticketId, attachmentId);
        await reload();
        setSuccessMessage("Attachment deleted.");
        return true;
      } catch (err) {
        setActionError(
          getErrorMessage(err, "Could not delete the attachment. Please try again.")
        );
        return false;
      } finally {
        deletingRef.current = false;
        setDeletingId(null);
      }
    },
    [ticketId, reload]
  );

  const download = useCallback(
    async (attachment: TicketAttachment): Promise<void> => {
      setActionError(null);

      try {
        const blob = await downloadAttachment(ticketId, attachment.id);
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = attachment.original_filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      } catch (err) {
        setActionError(
          getErrorMessage(err, "Download failed. Please try again.")
        );
      }
    },
    [ticketId]
  );

  return {
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
  };
}
