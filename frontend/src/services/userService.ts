import api from "./api";
import type {
  User,
  UpdateRoleRequest,
} from "../types/user";

const API = "http://127.0.0.1:8000";

const getToken = () => localStorage.getItem("token");

const authHeaders = () => ({
  headers: {
    Authorization: `Bearer ${getToken()}`,
  },
});

// =====================================
// Get All Users
// =====================================
export async function getUsers(): Promise<User[]> {
  const response = await api.get<User[]>(
    `${API}/users`,
    authHeaders()
  );

  return response.data;
}

// =====================================
// Get User By ID
// =====================================
export async function getUserById(
  userId: number
): Promise<User> {
  const response = await api.get<User>(
    `${API}/users/${userId}`,
    authHeaders()
  );

  return response.data;
}

// =====================================
// Update User Role
// =====================================
export async function updateUserRole(
  userId: number,
  role: UpdateRoleRequest
): Promise<User> {
  const response = await api.put<User>(
    `${API}/users/${userId}/role`,
    role,
    authHeaders()
  );

  return response.data;
}