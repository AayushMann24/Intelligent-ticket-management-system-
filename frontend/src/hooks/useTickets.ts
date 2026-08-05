import { useEffect, useMemo, useState } from "react";

import {
  getAllTickets,
  createTicket,
  updateTicket,
  deleteTicket,
  assignTicket,
  updateTicketStatus,
  type TicketPayload,
  type TicketUpdatePayload,
} from "../services/ticketService";

import type { Ticket } from "../types/ticket";

export default function useTickets() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);

  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [priority, setPriority] = useState("");

  // ===================================
  // Load Tickets
  // ===================================
  const loadTickets = async () => {
    try {
      setLoading(true);

      const data = await getAllTickets();

      setTickets(data);
    } catch (error) {
      console.error("Failed to load tickets:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTickets();
  }, []);

  // ===================================
  // Create Ticket
  // ===================================
  const addTicket = async (
    ticket: TicketPayload
  ) => {
    try {
      await createTicket(ticket);
      await loadTickets();
    } catch (error) {
      console.error("Failed to create ticket:", error);
    }
  };

  // ===================================
  // Edit Ticket
  // ===================================
  const editTicket = async (
    ticketId: number,
    updatedTicket: TicketUpdatePayload
  ) => {
    try {
      await updateTicket(ticketId, updatedTicket);
      await loadTickets();
    } catch (error) {
      console.error("Failed to update ticket:", error);
    }
  };

  // ===================================
  // Delete Ticket
  // ===================================
  const removeTicket = async (
    ticketId: number
  ) => {
    try {
      await deleteTicket(ticketId);
      await loadTickets();
    } catch (error) {
      console.error("Failed to delete ticket:", error);
    }
  };

  // ===================================
  // Assign Technician
  // ===================================
  const assignTechnician = async (
    ticketId: number,
    technicianId: number
  ) => {
    try {
      await assignTicket(
        ticketId,
        technicianId
      );

      await loadTickets();
    } catch (error) {
      console.error("Assignment failed:", error);
    }
  };

  // ===================================
  // Update Status
  // ===================================
  const changeStatus = async (
    ticketId: number,
    newStatus: string
  ) => {
    try {
      await updateTicketStatus(
        ticketId,
        newStatus
      );

      await loadTickets();
    } catch (error) {
      console.error(
        "Status update failed:",
        error
      );
    }
  };

  // ===================================
  // Filter Tickets
  // ===================================
  const filteredTickets = useMemo(() => {
    return tickets.filter((ticket) => {

      const matchesSearch =
        ticket.title
          .toLowerCase()
          .includes(search.toLowerCase());

      const matchesStatus =
        status === "" ||
        ticket.status === status;

      const matchesPriority =
        priority === "" ||
        ticket.priority === priority;

      return (
        matchesSearch &&
        matchesStatus &&
        matchesPriority
      );
    });
  }, [
    tickets,
    search,
    status,
    priority,
  ]);

  return {
    tickets: filteredTickets,
    loading,

    reloadTickets: loadTickets,

    addTicket,
    editTicket,
    removeTicket,

    assignTechnician,
    changeStatus,

    search,
    setSearch,

    status,
    setStatus,

    priority,
    setPriority,
  };
}