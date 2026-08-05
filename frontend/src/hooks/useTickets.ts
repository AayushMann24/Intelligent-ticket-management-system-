import { useEffect, useState } from "react";

import { getAllTickets } from "../services/ticketService";

import type { Ticket } from "../types/ticket";

export default function useTickets() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);

  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [priority, setPriority] = useState("");

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

  useEffect(() => {
    loadTickets();
  }, []);

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

    search,
    setSearch,

    status,
    setStatus,

    priority,
    setPriority,
  };
}