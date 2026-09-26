import api from "./api";
import type {
  User,
  UpdateRoleRequest,
} from "../types/user";

// =====================================
// Get All Users
// =====================================
export async function getUsers(): Promise<User[]> {
  const response = await api.get<User[]>("/users");
  return response.data;
}

// =====================================
// Get User By ID
// =====================================
export async function getUserById(
  userId: number
): Promise<User> {
  const response = await api.get<User>(`/users/${userId}`);
  return response.data;
}

// =====================================
// Update User Role
// =====================================
export async function updateUserRole(
  userId: number,
  role: UpdateRoleRequest
): Promise<User> {
  const response = await api.put<User>(`/users/${userId}/role`, role);
  return response.data;
}