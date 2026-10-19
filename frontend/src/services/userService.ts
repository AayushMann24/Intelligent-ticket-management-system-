import api from "./api";
import type {
  User,
  UpdateRoleRequest,
} from "../types/user";
import type {
  UserPreferences,
  PreferencesUpdate,
  ChangePasswordRequest,
  ChangePasswordResponse,
} from "../types/preferences";

export interface Technician {
  id: number;
  name: string;
  email: string;
  role: string;
  specialization?: string;
  workload?: number;
}

// =====================================
// Get Technicians/Admins (for assignment & escalation)
// =====================================
export async function getTechnicians(): Promise<Technician[]> {
  const response = await api.get<{ items: Technician[] }>("/users/technicians");
  return response.data.items;
}

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

// =====================================
// Current User Preferences
// =====================================
export async function getMyPreferences(): Promise<UserPreferences> {
  const response = await api.get<UserPreferences>("/users/me/preferences");
  return response.data;
}

export async function updateMyPreferences(
  updates: PreferencesUpdate
): Promise<UserPreferences> {
  const response = await api.put<UserPreferences>(
    "/users/me/preferences",
    updates
  );
  return response.data;
}

// =====================================
// Change Password
// =====================================
export async function changePassword(
  data: ChangePasswordRequest
): Promise<ChangePasswordResponse> {
  const response = await api.put<ChangePasswordResponse>(
    "/users/me/password",
    data
  );
  return response.data;
}