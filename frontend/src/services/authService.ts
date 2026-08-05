import axios from "axios";

import type {
  LoginData,
  LoginResponse,
} from "../types/auth";

const API = "http://127.0.0.1:8000";

export async function loginUser(
  data: LoginData
): Promise<LoginResponse> {

  const response = await axios.post<LoginResponse>(
    `${API}/auth/login`,
    data
  );

  return response.data;
}