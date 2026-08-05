import axios from "axios";

const API = "http://127.0.0.1:8000";

const getToken = () => localStorage.getItem("token");

// ===============================
// Get All Tickets
// ===============================
export async function getAllTickets() {
  const response = await axios.get(`${API}/tickets`, {
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
  });

  return response.data;
}

// ===============================
// Create Ticket
// ===============================
export async function createTicket(ticket: {
  title: string;
  description: string;
  priority: string;
}) {
  const response = await axios.post(
    `${API}/tickets`,
    ticket,
    {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    }
  );

  return response.data;
}

// ===============================
// Update Ticket
// ===============================
export async function updateTicket(
  ticketId: number,
  ticket: {
    title: string;
    description: string;
    priority: string;
    status: string;
    assigned_to: number | null;
  }
) {
  const response = await axios.put(
    `${API}/tickets/${ticketId}`,
    ticket,
    {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    }
  );

  return response.data;
}

// ===============================
// Delete Ticket
// ===============================
export async function deleteTicket(ticketId: number) {
  const response = await axios.delete(
    `${API}/tickets/${ticketId}`,
    {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    }
  );

  return response.data;
}