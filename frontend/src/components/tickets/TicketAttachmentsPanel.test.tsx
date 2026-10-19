import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import { vi, describe, it, expect, beforeEach, beforeAll } from "vitest";

vi.mock("../../services/ticketService", () => ({
  getAttachments: vi.fn(),
  uploadAttachment: vi.fn(),
  downloadAttachment: vi.fn(),
  deleteAttachment: vi.fn(),
}));

import TicketAttachmentsPanel from "./TicketAttachmentsPanel";
import {
  getAttachments,
  uploadAttachment,
  downloadAttachment,
  deleteAttachment,
} from "../../services/ticketService";
import type {
  TicketAttachment,
  TicketAttachmentListResponse,
} from "../../types/ticket";

const attachment: TicketAttachment = {
  id: 1,
  ticket_id: 10,
  uploaded_by: 2,
  uploader_name: "Test User",
  original_filename: "evidence.pdf",
  content_type: "application/pdf",
  file_size: 2048,
  created_at: "2024-01-01T00:00:00Z",
};

const listOne: TicketAttachmentListResponse = {
  items: [attachment],
  total: 1,
  page: 1,
  page_size: 20,
  total_pages: 1,
};

const emptyList: TicketAttachmentListResponse = {
  items: [],
  total: 0,
  page: 1,
  page_size: 20,
  total_pages: 0,
};

beforeAll(() => {
  Object.defineProperty(URL, "createObjectURL", {
    writable: true,
    value: vi.fn(() => "blob:mock"),
  });
  Object.defineProperty(URL, "revokeObjectURL", {
    writable: true,
    value: vi.fn(),
  });
});

describe("TicketAttachmentsPanel", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    (getAttachments as vi.Mock).mockResolvedValue(listOne);
    (uploadAttachment as vi.Mock).mockResolvedValue({ ...attachment, id: 2 });
    (deleteAttachment as vi.Mock).mockResolvedValue({ message: "ok" });
    (downloadAttachment as vi.Mock).mockResolvedValue(new Blob(["data"]));
  });

  const renderPanel = () => render(<TicketAttachmentsPanel ticketId={10} />);

  it("loads and lists attachments for the ticket", async () => {
    renderPanel();

    expect(await screen.findByText("evidence.pdf")).toBeInTheDocument();
    expect(getAttachments).toHaveBeenCalledWith(10);
    expect(screen.getByText(/2.0 KB/)).toBeInTheDocument();
  });

  it("shows a loading state while fetching", async () => {
    let resolveLoad: ((value: TicketAttachmentListResponse) => void) | undefined;
    (getAttachments as vi.Mock).mockReturnValueOnce(
      new Promise((resolve) => {
        resolveLoad = resolve;
      })
    );

    renderPanel();

    expect(screen.getByText(/loading attachments/i)).toBeInTheDocument();
    expect(screen.queryByText("evidence.pdf")).not.toBeInTheDocument();

    await act(async () => {
      resolveLoad?.(listOne);
    });

    expect(await screen.findByText("evidence.pdf")).toBeInTheDocument();
  });

  it("shows an empty state when there are no attachments", async () => {
    (getAttachments as vi.Mock).mockResolvedValueOnce(emptyList);

    renderPanel();

    expect(
      await screen.findByText(/no attachments yet/i)
    ).toBeInTheDocument();
  });

  it("shows an error with retry when loading fails", async () => {
    (getAttachments as vi.Mock)
      .mockRejectedValueOnce(new Error("boom"))
      .mockResolvedValueOnce(listOne);

    renderPanel();

    expect(
      await screen.findByText(/unable to load attachments/i)
    ).toBeInTheDocument();

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /try again/i }));
    });

    expect(await screen.findByText("evidence.pdf")).toBeInTheDocument();
    expect(getAttachments).toHaveBeenCalledTimes(2);
  });

  it("uploads a file, refreshes the list, and reports success", async () => {
    (getAttachments as vi.Mock)
      .mockResolvedValueOnce(emptyList)
      .mockResolvedValueOnce(listOne);

    renderPanel();
    await screen.findByText(/no attachments yet/i);

    const file = new File(["hello"], "note.txt", { type: "text/plain" });

    await act(async () => {
      fireEvent.change(screen.getByTestId("attachment-file-input"), {
        target: { files: [file] },
      });
    });

    expect(uploadAttachment).toHaveBeenCalledWith(10, file, expect.any(Function));
    expect(await screen.findByText("evidence.pdf")).toBeInTheDocument();
    expect(screen.getByText(/attachment uploaded/i)).toBeInTheDocument();
  });

  it("prevents duplicate uploads while one is in flight", async () => {
    let resolveUpload: ((value: TicketAttachment) => void) | undefined;
    (uploadAttachment as vi.Mock).mockReturnValueOnce(
      new Promise((resolve) => {
        resolveUpload = resolve;
      })
    );

    renderPanel();
    await screen.findByText("evidence.pdf");

    const file = new File(["hello"], "note.txt", { type: "text/plain" });
    const input = screen.getByTestId("attachment-file-input");

    fireEvent.change(input, { target: { files: [file] } });
    fireEvent.change(input, { target: { files: [file] } });

    expect(uploadAttachment).toHaveBeenCalledTimes(1);
    expect(input).toBeDisabled();

    await act(async () => {
      resolveUpload?.({ ...attachment, id: 2 });
    });
  });

  it("rejects an empty file before calling the API", async () => {
    renderPanel();
    await screen.findByText("evidence.pdf");

    const emptyFile = new File([], "empty.txt", { type: "text/plain" });

    fireEvent.change(screen.getByTestId("attachment-file-input"), {
      target: { files: [emptyFile] },
    });

    expect(await screen.findByText(/file is empty/i)).toBeInTheDocument();
    expect(uploadAttachment).not.toHaveBeenCalled();
  });

  it("deletes an attachment and refreshes the list", async () => {
    renderPanel();
    await screen.findByText("evidence.pdf");

    await act(async () => {
      fireEvent.click(
        screen.getByRole("button", { name: /delete evidence.pdf/i })
      );
    });

    expect(deleteAttachment).toHaveBeenCalledWith(10, 1);
    expect(screen.getByText(/attachment deleted/i)).toBeInTheDocument();
  });

  it("handles a forbidden deletion gracefully", async () => {
    (deleteAttachment as vi.Mock).mockRejectedValueOnce({
      response: { status: 403 },
    });

    renderPanel();
    await screen.findByText("evidence.pdf");

    await act(async () => {
      fireEvent.click(
        screen.getByRole("button", { name: /delete evidence.pdf/i })
      );
    });

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent(/not allowed/i);
    // The attachment is still listed after a failed delete.
    expect(screen.getByText("evidence.pdf")).toBeInTheDocument();
  });

  it("downloads an attachment through a blob link", async () => {
    renderPanel();
    await screen.findByText("evidence.pdf");

    await act(async () => {
      fireEvent.click(
        screen.getByRole("button", { name: /download evidence.pdf/i })
      );
    });

    expect(downloadAttachment).toHaveBeenCalledWith(10, 1);
    expect(URL.createObjectURL).toHaveBeenCalled();
    expect(URL.revokeObjectURL).toHaveBeenCalled();
  });

  it("surfaces download failures", async () => {
    (downloadAttachment as vi.Mock).mockRejectedValueOnce(new Error("nope"));

    renderPanel();
    await screen.findByText("evidence.pdf");

    await act(async () => {
      fireEvent.click(
        screen.getByRole("button", { name: /download evidence.pdf/i })
      );
    });

    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent(/download failed/i)
    );
  });
});
