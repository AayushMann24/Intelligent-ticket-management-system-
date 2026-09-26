import { useEffect, useMemo, useState } from "react";

import {
  getAllTickets,
  createTicket,
  updateTicket,
  deleteTicket,
  assignTicket,
  reassignTicket,
  unassignTicket,
  startWork,
  markPending,
  resolveTicket,
  reopenTicket,
  closeTicket,
  escalateTicket,
  getWorkflowActions,
  updateTicketStatus,
  type TicketPayload,
  type TicketUpdatePayload,
} from "../services/ticketService";

import type { Ticket, WorkflowActions } from "../types/ticket";

export default function useTickets() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);

  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [priority, setPriority] = useState("");
  const [ticketType, setTicketType] = useState("");

  // ===================================
  // Load Tickets
  // ===================================
  const loadTickets = async () => {
    try {
      setLoading(true);

      const data = await getAllTickets();

      console.log("========== API DATA ==========");
      console.log(data);
      console.log("==============================");

      setTickets(data.items || data);
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
  // Reassign Technician
  // ===================================
  const reassignTechnician = async (
    ticketId: number,
    technicianId: number
  ) => {
    try {
      await reassignTicket(
        ticketId,
        technicianId
      );

      await loadTickets();
    } catch (error) {
      console.error("Reassignment failed:", error);
    }
  };

  // ===================================
  // Unassign Ticket
  // ===================================
  const unassignTechnician = async (
    ticketId: number
  ) => {
    try {
      await unassignTicket(ticketId);
      await loadTickets();
    } catch (error) {
      console.error("Unassignment failed:", error);
    }
  };

  // ===================================
  // Start Work
  // ===================================
  const startWorkOnTicket = async (
    ticketId: number
  ) => {
    try {
      await startWork(ticketId);
      await loadTickets();
    } catch (error) {
      console.error("Start work failed:", error);
    }
  };

  // ===================================
  // Mark Pending
  // ===================================
  const markTicketPending = async (
    ticketId: number
  ) => {
    try {
      await markPending(ticketId);
      await loadTickets();
    } catch (error) {
      console.error("Mark pending failed:", error);
    }
  };

  // ===================================
  // Resolve Ticket
  // ===================================
  const resolveTicketAction = async (
    ticketId: number,
    resolutionSummary: string
  ) => {
    try {
      await resolveTicket(ticketId, resolutionSummary);
      await loadTickets();
    } catch (error) {
      console.error("Resolve failed:", error);
    }
  };

  // ===================================
  // Reopen Ticket
  // ===================================
  const reopenTicketAction = async (
    ticketId: number,
    reason?: string
  ) => {
    try {
      await reopenTicket(ticketId, reason);
      await loadTickets();
    } catch (error) {
      console.error("Reopen failed:", error);
    }
  };

  // ===================================
  // Close Ticket
  // ===================================
  const closeTicketAction = async (
    ticketId: number
  ) => {
    try {
      await closeTicket(ticketId);
      await loadTickets();
    } catch (error) {
      console.error("Close failed:", error);
    }
  };

  // ===================================
  // Escalate Ticket
  // ===================================
  const escalateTicketAction = async (
    ticketId: number,
    escalatedTo: number,
    escalationReason: string
  ) => {
    try {
      await escalateTicket(ticketId, escalatedTo, escalationReason);
      await loadTickets();
    } catch (error) {
      console.error("Escalate failed:", error);
    }
  };

  // ===================================
  // Get Workflow Actions
  // ===================================
  const fetchWorkflowActions = async (
    ticketId: number
  ): Promise<WorkflowActions> => {
    try {
      return await getWorkflowActions(ticketId);
    } catch (error) {
      console.error("Failed to fetch workflow actions:", error);
      return {
        can_assign: false,
        can_reassign: false,
        can_unassign: false,
        can_start_work: false,
        can_mark_pending: false,
        can_resolve: false,
        can_reopen: false,
        can_close: false,
        can_escalate: false,
        valid_status_transitions: [],
      };
    }
  };

  // ===================================
  // Update Status (Legacy)
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

      const matchesType =
        ticketType === "" ||
        ticket.ticket_type === ticketType;

      return (
        matchesSearch &&
        matchesStatus &&
        matchesPriority &&
        matchesType
      );
    });
  }, [
    tickets,
    search,
    status,
    priority,
    ticketType,
  ]);

  return {
    tickets: filteredTickets,
    loading,

    reloadTickets: loadTickets,

    addTicket,
    editTicket,
    removeTicket,

    assignTechnician,
    reassignTechnician,
    unassignTechnician,
    startWorkOnTicket,
    markTicketPending,
    resolveTicketAction,
    reopenTicketAction,
    closeTicketAction,
    escalateTicketAction,
    fetchWorkflowActions,
    changeStatus,

    search,
    setSearch,

    status,
    setStatus,

    priority,
    setPriority,

    ticketType,
    setTicketType,
  };
}