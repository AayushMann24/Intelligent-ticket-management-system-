import { useState } from "react";
import { Plus } from "lucide-react";

import MainLayout from "../layouts/MainLayout";

import useTickets from "../hooks/useTickets";

import TicketTable from "../components/tickets/TicketTable";
import TicketToolbar from "../components/tickets/TicketToolbar";

import TicketFormModal from "../components/tickets/TicketFormModal";
import TicketDetailsModal from "../components/tickets/TicketDetailsModal";
import DeleteConfirmModal from "../components/tickets/DeleteConfirmModal";

import type { Ticket } from "../types/ticket";

export default function TicketsPage() {
  const {
    tickets,
    loading,

    search,
    setSearch,

    status,
    setStatus,

    priority,
    setPriority,

    removeTicket,
    editTicket,
    addTicket,
  } = useTickets();

  const [selectedTicket, setSelectedTicket] =
    useState<Ticket | null>(null);

  const [isFormOpen, setIsFormOpen] =
    useState(false);

  const [isViewOpen, setIsViewOpen] =
    useState(false);

  const [isDeleteOpen, setIsDeleteOpen] =
    useState(false);

  if (loading) {
    return (
      <MainLayout>
        <div className="flex h-96 items-center justify-center">
          <h2 className="text-xl text-white">
            Loading Tickets...
          </h2>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>

      {/* Header */}

      <div className="mb-8 flex items-center justify-between">

        <h1 className="text-3xl font-bold text-white">
          Tickets
        </h1>

        <button
          onClick={() => {
            setSelectedTicket(null);
            setIsFormOpen(true);
          }}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          <Plus size={18} />
          New Ticket
        </button>

      </div>

      {/* Toolbar */}

      <TicketToolbar
        search={search}
        setSearch={setSearch}
        status={status}
        setStatus={setStatus}
        priority={priority}
        setPriority={setPriority}
      />

      {/* Table */}

      <TicketTable
        tickets={tickets}

        onView={(ticket) => {
          setSelectedTicket(ticket);
          setIsViewOpen(true);
        }}

        onEdit={(ticket) => {
          setSelectedTicket(ticket);
          setIsFormOpen(true);
        }}

        onDelete={(ticket) => {
          setSelectedTicket(ticket);
          setIsDeleteOpen(true);
        }}
      />

      {/* Create / Edit */}

      <TicketFormModal
        open={isFormOpen}
        ticket={selectedTicket}
        onClose={() => setIsFormOpen(false)}
        onSubmit={async (ticketData) => {

          if (selectedTicket) {

            await editTicket(
              selectedTicket.id,
              ticketData
            );

          } else {

            await addTicket({
              title: ticketData.title,
              description: ticketData.description,
              priority: ticketData.priority,
            });

          }

          setIsFormOpen(false);

        }}
      />

      {/* View */}

      <TicketDetailsModal
        open={isViewOpen}
        ticket={selectedTicket}
        onClose={() => setIsViewOpen(false)}
      />

      {/* Delete */}

      <DeleteConfirmModal
        open={isDeleteOpen}
        ticketTitle={selectedTicket?.title ?? ""}
        onClose={() => setIsDeleteOpen(false)}
        onConfirm={async () => {

          if (!selectedTicket) return;

          await removeTicket(selectedTicket.id);

          setIsDeleteOpen(false);

        }}
      />

    </MainLayout>
  );
}