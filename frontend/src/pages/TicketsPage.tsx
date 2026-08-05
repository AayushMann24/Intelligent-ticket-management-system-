import { useState } from "react";

import MainLayout from "../layouts/MainLayout";

import useTickets from "../hooks/useTickets";

import TicketToolbar from "../components/tickets/TicketToolbar";
import TicketTable from "../components/tickets/TicketTable";

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

    addTicket,
    editTicket,
    removeTicket,
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

      <h1 className="mb-8 text-3xl font-bold text-white">
        Ticket Management
      </h1>

      <TicketToolbar
        search={search}
        setSearch={setSearch}
        status={status}
        setStatus={setStatus}
        priority={priority}
        setPriority={setPriority}
        onCreate={() => {
          setSelectedTicket(null);
          setIsFormOpen(true);
        }}
      />

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

      <TicketDetailsModal
        open={isViewOpen}
        ticket={selectedTicket}
        onClose={() => setIsViewOpen(false)}
      />

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