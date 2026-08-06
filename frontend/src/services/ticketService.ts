import axios from "axios";

const API = "http://127.0.0.1:8000";

const getToken = () => localStorage.getItem("token");

// ======================================
// Axios Config
// ======================================
const authConfig = () => ({
  headers: {
    Authorization: `Bearer ${getToken()}`,
  },
});

// ======================================
// Types
// ======================================
export interface TicketPayload {
  title: string;
  description: string;
  priority: string;
}

export interface TicketUpdatePayload {
  title: string;
  description: string;
  priority: string;
  status: string;
  assigned_to: number | null;
}

// ======================================
// Get All Tickets
// ======================================
export async function getAllTickets() {

  console.log("Calling:", `${API}/tickets`);

  const response = await axios.get(
    `${API}/tickets`,
    authConfig()
  );

  console.log(response.data);

  return response.data;
}

// ======================================
// Create Ticket
// ======================================
export async function createTicket(
  ticket: TicketPayload
) {
  const response = await axios.post(
    `${API}/tickets`,
    ticket,
    authConfig()
  );

  return response.data;
}

// ======================================
// Update Ticket
// ======================================
export async function updateTicket(
  ticketId: number,
  ticket: TicketUpdatePayload
) {
  const response = await axios.put(
    `${API}/tickets/${ticketId}`,
    ticket,
    authConfig()
  );

  return response.data;
}

// ======================================
// Delete Ticket
// ======================================
export async function deleteTicket(
  ticketId: number
) {
  const response = await axios.delete(
    `${API}/tickets/${ticketId}`,
    authConfig()
  );

  return response.data;
}

// ======================================
// Assign Technician
// ======================================
export async function assignTicket(
  ticketId: number,
  assignedTo: number
) {
  const response = await axios.put(
    `${API}/tickets/${ticketId}/assign`,
    {
      assigned_to: assignedTo,
    },
    authConfig()
  );

  return response.data;
}

// ======================================
// Update Ticket Status
// ======================================
export async function updateTicketStatus(
  ticketId: number,
  status: string
) {
  const response = await axios.patch(
    `${API}/tickets/${ticketId}/status`,
    {
      status,
    },
    authConfig()
  );

  return response.data;
}