import { useEffect, useState } from "react";

import {
  getAllTickets,
  deleteTicket,
  updateTicket,
  createTicket,
} from "../services/ticketService";

import type { Ticket } from "../types/ticket";

export default function useTickets() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);

  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [priority, setPriority] = useState("");

  // ===============================
  // Load Tickets
  // ===============================
  const loadTickets = async () => {
    try {
      const data = await getAllTickets();
      setTickets(data);
    } catch (error) {
      console.error("Failed to load tickets:", error);
    } finally {
      setLoading(false);
    }
  };

  // ===============================
  // Delete Ticket
  // ===============================
  const removeTicket = async (ticketId: number) => {
    try {
      await deleteTicket(ticketId);
      await loadTickets();
    } catch (error) {
      console.error("Failed to delete ticket:", error);
    }
  };

  // ===============================
  // Edit Ticket
  // ===============================
  const editTicket = async (
    ticketId: number,
    updatedTicket: {
      title: string;
      description: string;
      priority: string;
      status: string;
      assigned_to: number | null;
    }
  ) => {
    try {
      await updateTicket(ticketId, updatedTicket);
      await loadTickets();
    } catch (error) {
      console.error("Failed to update ticket:", error);
    }
  };

  // ===============================
  // Create Ticket
  // ===============================
  const addTicket = async (ticket: {
    title: string;
    description: string;
    priority: string;
  }) => {
    try {
      await createTicket(ticket);
      await loadTickets();
    } catch (error) {
      console.error("Failed to create ticket:", error);
    }
  };

  useEffect(() => {
    loadTickets();
  }, []);

  // ===============================
  // Filters
  // ===============================
  const filteredTickets = tickets.filter((ticket) => {
    const matchesSearch = ticket.title
      .toLowerCase()
      .includes(search.toLowerCase());

    const matchesStatus =
      status === "" || ticket.status === status;

    const matchesPriority =
      priority === "" || ticket.priority === priority;

    return (
      matchesSearch &&
      matchesStatus &&
      matchesPriority
    );
  });

  return {
    tickets: filteredTickets,
    loading,

    reloadTickets: loadTickets,

    removeTicket,
    editTicket,
    addTicket,

    search,
    setSearch,

    status,
    setStatus,

    priority,
    setPriority,
  };
}