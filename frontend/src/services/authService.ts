import axios from "axios";

import type {
  LoginData,
  LoginResponse,
} from "../types/auth";

const API = "http://127.0.0.1:8000";

// ======================================
// Login
// ======================================

export async function loginUser(
  data: LoginData
): Promise<LoginResponse> {

  const response = await axios.post<LoginResponse>(
    `${API}/auth/login`,
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
  const response = await axios.post(
    `${API}/auth/register`,
    data
  );

  return response.data;
}