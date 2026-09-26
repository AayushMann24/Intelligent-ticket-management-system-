import api from "./api";
import type {
  LoginData,
  LoginResponse,
} from "../types/auth";

// Re-export types for consumers
export type {
  LoginData,
  LoginResponse,
};

// ======================================
// Login
// ======================================

export async function loginUser(
  data: LoginData
): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>(
    "/auth/login",
    data
  );
  return response.data;
}

// ======================================
// Register
// ======================================

export interface RegisterData {
  name: string;
  email: string;
  password: string;
  role: string;
}

export async function registerUser(
  data: RegisterData
) {
  const response = await api.post(
    "/auth/register",
    data
  );
  return response.data;
}

// ======================================
// Refresh Token
// ======================================

export interface RefreshTokenRequest {
  refresh_token: string;
}

export async function refreshAccessToken(
  data: RefreshTokenRequest
): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>(
    "/auth/refresh",
    data
  );
  return response.data;
}